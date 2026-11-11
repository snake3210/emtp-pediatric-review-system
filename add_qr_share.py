# -*- coding: utf-8 -*-
"""Generates offline vector SVG QR code, updates spa_template.html and subject_config.json, and rebuilds SPA."""

import io
import json
import os
import re
import segno

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
CFG_PATH = os.path.join(BASE_DIR, "subject_config.json")
TEMPLATE_PATH = r"C:\Users\firem\.gemini\config\skills\universal-exam-review-builder\resources\spa_template.html"
SHARE_URL = "https://snake3210.github.io/emtp-pediatric-review-system/"


def main():
    # 1. Generate responsive SVG QR Code
    qr = segno.make(SHARE_URL, error="m")
    buff = io.BytesIO()
    qr.save(buff, kind="svg", xmldecl=False, svgns=True, border=2, dark="#0f172a", light="#ffffff")
    svg_str = buff.getvalue().decode("utf-8").strip()
    svg_str = re.sub(
        r'width="(\d+)"\s+height="(\d+)"',
        r'viewBox="0 0 \1 \2" class="w-full h-full"',
        svg_str,
    )

    with open(CFG_PATH, "r", encoding="utf-8") as f:
        cfg = json.load(f)
    cfg["shareUrl"] = SHARE_URL
    cfg["qrCodeSvg"] = svg_str
    with open(CFG_PATH, "w", encoding="utf-8") as f:
        json.dump(cfg, f, ensure_ascii=False, indent=2)
    print(f"Updated {CFG_PATH} with shareUrl and qrCodeSvg ({len(svg_str)} chars)")

    # 2. Update spa_template.html
    with open(TEMPLATE_PATH, "r", encoding="utf-8") as f:
        html = f.read()

    # Normalize line endings to \n for clean replacement
    html = html.replace("\r\n", "\n")

    # (a) Navbar button
    if 'id="nav-share-qr-btn"' not in html:
        target_nav = """        <!-- 題號矩陣總覽按鈕 -->
        <button onclick="openQuestionMatrixModal()" class="flex items-center gap-1.5 px-3 py-2 rounded-xl font-semibold text-xs sm:text-sm bg-slate-800/90 hover:bg-slate-700 text-slate-200 border border-slate-700 transition">
          <span>🔢 題號總覽</span>
        </button>"""
        replacement_nav = target_nav + """

        <!-- 📱 QR Code 分享按鈕 -->
        <button onclick="openShareQrModal()" id="nav-share-qr-btn" class="flex items-center gap-1.5 px-3 py-2 rounded-xl font-bold text-xs sm:text-sm bg-cyan-500/15 hover:bg-cyan-500/25 text-cyan-300 border border-cyan-500/40 transition" title="顯示網址 QR Code 分享給朋友">
          <span>📱</span>
          <span>分享 QR</span>
        </button>"""
        assert target_nav in html, "target_nav not found"
        html = html.replace(target_nav, replacement_nav, 1)

    # (b) Footer share banner inside <main>
    if 'id="footer-share-banner"' not in html:
        target_main_end = """            <ul id="guideline-check-list" class="space-y-2.5 text-xs sm:text-sm text-slate-200 leading-relaxed"></ul>
          </div>
        </div>
      </aside>
    </div>
  </main>"""
        replacement_main_end = """            <ul id="guideline-check-list" class="space-y-2.5 text-xs sm:text-sm text-slate-200 leading-relaxed"></ul>
          </div>
        </div>
      </aside>
    </div>

    <!-- 底部常駐 QR Code 分享橫幅卡片 -->
    <section id="footer-share-banner" class="bg-[#0b1323]/90 border border-cyan-500/30 rounded-2xl p-4 sm:p-5 shadow-xl flex flex-col sm:flex-row items-center justify-between gap-4">
      <div class="space-y-2 text-center sm:text-left">
        <div class="inline-flex items-center gap-2 px-2.5 py-1 rounded-lg bg-cyan-500/15 border border-cyan-500/30 text-cyan-300 text-xs font-bold">
          <span>📱 戰情室好康分享</span>
          <span>‧</span>
          <span>手機掃描立即開刷</span>
        </div>
        <h3 class="text-sm sm:text-base font-black text-white">覺得這套視覺化複習系統有幫助嗎？分享給一起備考的夥伴！</h3>
        <p id="footer-share-url-text" class="text-xs font-mono text-slate-400 break-all"></p>
        <div class="flex flex-wrap items-center justify-center sm:justify-start gap-2 pt-1">
          <button onclick="copyShareUrl('footer-copy-btn-text')" class="px-3.5 py-2 rounded-xl bg-cyan-500 hover:bg-cyan-400 text-slate-950 font-bold text-xs shadow-md transition flex items-center gap-1.5">
            <span>📋</span>
            <span id="footer-copy-btn-text">複製刷題網址</span>
          </button>
          <button onclick="openShareQrModal()" class="px-3.5 py-2 rounded-xl bg-slate-800 hover:bg-slate-700 text-slate-200 border border-slate-700 font-bold text-xs transition flex items-center gap-1.5">
            <span>🔍</span>
            <span>放大顯示 QR Code</span>
          </button>
          <button onclick="triggerNativeShare()" class="px-3.5 py-2 rounded-xl bg-emerald-500/20 hover:bg-emerald-500/30 text-emerald-300 border border-emerald-500/40 font-bold text-xs transition flex items-center gap-1.5">
            <span>📤</span>
            <span>轉傳 LINE / 分享</span>
          </button>
        </div>
      </div>
      <div onclick="openShareQrModal()" class="cursor-pointer group flex flex-col items-center gap-1.5 shrink-0" title="點擊放大 QR Code">
        <div id="footer-qr-box" class="w-28 h-28 sm:w-32 sm:h-32 bg-white p-2 rounded-2xl shadow-lg border-2 border-cyan-400/50 group-hover:scale-105 transition-transform flex items-center justify-center overflow-hidden"></div>
        <span class="text-[11px] text-cyan-300 font-semibold group-hover:underline">👆 點擊放大掃描</span>
      </div>
    </section>
  </main>"""
        assert target_main_end in html, "target_main_end not found"
        html = html.replace(target_main_end, replacement_main_end, 1)

    # (c) Share QR Modal
    if 'id="share-qr-modal"' not in html:
        target_modal = """      <div id="matrix-grid-container" class="p-5 overflow-y-auto grid grid-cols-4 sm:grid-cols-6 md:grid-cols-8 gap-2"></div>
    </div>
  </div>"""
        replacement_modal = target_modal + """

  <!-- 📱 QR Code 分享專屬彈窗 -->
  <div id="share-qr-modal" onclick="closeShareQrModal()" class="hidden fixed inset-0 z-50 bg-slate-950/85 backdrop-blur-md flex items-center justify-center p-4">
    <div onclick="event.stopPropagation()" class="bg-[#0b1323] border border-cyan-500/40 rounded-2xl max-w-md w-full p-6 shadow-2xl flex flex-col items-center text-center space-y-4">
      <div class="w-full flex items-center justify-between border-b border-slate-800 pb-3">
        <div class="flex items-center gap-2 text-left">
          <span class="w-8 h-8 rounded-xl bg-cyan-500/20 border border-cyan-500/40 flex items-center justify-center text-lg">📱</span>
          <div>
            <h3 class="text-base font-black text-white">掃描 QR Code 立即刷題</h3>
            <p class="text-xs text-slate-400">支援手機、平板、電腦跨裝置免安裝使用</p>
          </div>
        </div>
        <button onclick="closeShareQrModal()" class="px-3 py-1.5 rounded-xl bg-slate-800 hover:bg-rose-600 text-slate-300 hover:text-white text-xs font-bold transition">✕ 關閉</button>
      </div>

      <div id="modal-qr-box" class="w-56 h-56 sm:w-64 sm:h-64 bg-white p-3 rounded-2xl shadow-2xl border-4 border-cyan-400/60 flex items-center justify-center overflow-hidden"></div>

      <div class="space-y-1 w-full">
        <p id="modal-share-title" class="text-sm font-bold text-slate-100"></p>
        <p id="modal-share-url" class="text-xs font-mono text-cyan-300 bg-slate-900/90 border border-slate-800 px-3 py-2 rounded-xl break-all select-all"></p>
      </div>

      <div class="grid grid-cols-2 gap-2.5 w-full pt-1">
        <button onclick="copyShareUrl('modal-copy-btn-text')" class="py-2.5 px-4 rounded-xl bg-cyan-500 hover:bg-cyan-400 text-slate-950 font-black text-xs sm:text-sm shadow-lg shadow-cyan-500/20 transition flex items-center justify-center gap-1.5">
          <span>📋</span>
          <span id="modal-copy-btn-text">複製網址</span>
        </button>
        <button onclick="triggerNativeShare()" class="py-2.5 px-4 rounded-xl bg-emerald-500/20 hover:bg-emerald-500/30 text-emerald-300 border border-emerald-500/40 font-black text-xs sm:text-sm transition flex items-center justify-center gap-1.5">
          <span>📤</span>
          <span>直接轉傳分享</span>
        </button>
      </div>
    </div>
  </div>"""
        assert target_modal in html, "target_modal not found"
        html = html.replace(target_modal, replacement_modal, 1)

    # (d) JS initSubjectMetadata QR setup
    if "document.getElementById('footer-qr-box')" not in html:
        target_init = """      } else {
        tabHeader.innerHTML = '';
        tabBody.innerHTML = '<p class="text-slate-400">尚未設定速查表內容。</p>';
      }
    }"""
        replacement_init = """      } else {
        tabHeader.innerHTML = '';
        tabBody.innerHTML = '<p class="text-slate-400">尚未設定速查表內容。</p>';
      }

      // 初始化分享網址與 QR Code
      const shareUrl = SUBJECT_CONFIG.shareUrl || window.location.href;
      document.getElementById('footer-share-url-text').textContent = shareUrl;
      document.getElementById('modal-share-url').textContent = shareUrl;
      document.getElementById('modal-share-title').textContent = SUBJECT_CONFIG.title || '';

      if (SUBJECT_CONFIG.qrCodeSvg) {
        document.getElementById('footer-qr-box').innerHTML = SUBJECT_CONFIG.qrCodeSvg;
        document.getElementById('modal-qr-box').innerHTML = SUBJECT_CONFIG.qrCodeSvg;
      } else {
        const fallbackImg = `<img src="https://api.qrserver.com/v1/create-qr-code/?size=256x256&margin=8&data=${encodeURIComponent(shareUrl)}" alt="QR Code" class="w-full h-full object-contain" />`;
        document.getElementById('footer-qr-box').innerHTML = fallbackImg;
        document.getElementById('modal-qr-box').innerHTML = fallbackImg;
      }
    }"""
        assert target_init in html, "target_init not found"
        html = html.replace(target_init, replacement_init, 1)

    # (e) JS helper functions
    if "function openShareQrModal()" not in html:
        target_funcs = """    function closeQuestionMatrixModal() { document.getElementById('matrix-modal').classList.add('hidden'); }
    function jumpToQuestionIndex(idx) { currentIndex = idx; closeQuestionMatrixModal(); renderCurrentQuestion(); }
    function toggleDataMenu() { document.getElementById('data-menu-dropdown').classList.toggle('hidden'); }"""
        replacement_funcs = target_funcs + """

    function openShareQrModal() {
      document.getElementById('share-qr-modal').classList.remove('hidden');
    }
    function closeShareQrModal() {
      document.getElementById('share-qr-modal').classList.add('hidden');
    }
    function copyShareUrl(labelId) {
      const shareUrl = SUBJECT_CONFIG.shareUrl || window.location.href;
      navigator.clipboard.writeText(shareUrl).then(() => {
        const el = document.getElementById(labelId);
        if (el) {
          const orig = el.textContent;
          el.textContent = '✓ 已複製網址！';
          setTimeout(() => { el.textContent = orig; }, 2000);
        }
      }).catch(() => {
        prompt('請複製以下網址分享給朋友：', shareUrl);
      });
    }
    function triggerNativeShare() {
      const shareUrl = SUBJECT_CONFIG.shareUrl || window.location.href;
      if (navigator.share) {
        navigator.share({
          title: SUBJECT_CONFIG.title,
          text: `${SUBJECT_CONFIG.title} — 互動式考古題四維度拆解與戰情複習系統`,
          url: shareUrl
        }).catch(() => {});
      } else {
        copyShareUrl('modal-copy-btn-text');
      }
    }"""
        assert target_funcs in html, "target_funcs not found"
        html = html.replace(target_funcs, replacement_funcs, 1)

    with open(TEMPLATE_PATH, "w", encoding="utf-8") as f:
        f.write(html)
    print(f"Successfully updated {TEMPLATE_PATH}")


if __name__ == "__main__":
    main()
