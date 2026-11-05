"""WebView2 ウィンドウでファイルを表示する。
  .dwg/.dxf -> CADXChange のブラウザ版ビューアに読み込ませる (図面はブラウザ内で処理される)
  .html/.htm/.svg/.md 等 -> そのまま表示 (JavaScript アプリも実行可)
  http(s):// -> そのページを開く
使い方: python runner.py <path-or-url> <scale> <dwg_url> <cad_exts(カンマ区切り)> <storage_dir>
"""
import base64
import json
import sys
from pathlib import Path

import webview

DWG_URL = "https://cadxchange.net/ja/dwg-viewer"
CAD_EXTS = {".dwg", ".dxf"}
SCALE = 0.8
STORAGE = Path.home() / ".xefm" / "state" / "webview-viewer"

# <input type=file> に File を設定して change を発火させる
_INJECT = """
void (async () => {
  const name = %s, b64 = %s;
  for (let i = 0; i < 300 && !document.querySelector('input[type=file]'); i++)
    await new Promise(r => setTimeout(r, 200));
  const input = document.querySelector('input[type=file]');
  if (!input) return;
  const bin = Uint8Array.from(atob(b64), c => c.charCodeAt(0));
  const dt = new DataTransfer();
  dt.items.add(new File([bin], name));
  input.files = dt.files;
  input.dispatchEvent(new Event('change', {bubbles: true}));
})();
"""


_CLOSE_KEYS = """
if (!window.__closeKeys) {
  window.__closeKeys = true;
  addEventListener('keydown', e => {
    const t = e.target, typing = t && (t.isContentEditable || /^(INPUT|TEXTAREA|SELECT)$/.test(t.tagName));
    if (typing || e.ctrlKey || e.altKey || e.metaKey) return;
    if (e.key === 'Escape' || e.key === 'q' || e.key === 'Q') pywebview.api.close();
  }, true);
}
"""

class Api:
    def close(self):
        webview.windows[0].destroy()


def _open(title, url):
    scr = webview.screens[0]
    w, h = int(scr.width * SCALE), int(scr.height * SCALE)
    x, y = scr.x + (scr.width - w) // 2, scr.y + (scr.height - h) // 2
    window = webview.create_window(title, url, width=w, height=h, x=x, y=y, js_api=Api())
    window.events.loaded += lambda: window.evaluate_js(_CLOSE_KEYS)
    return window


def _watch_close_keys():
    """PDF ビューアはキー入力をページの JS に渡さないため、OS 側で Esc/Q を監視して閉じる。"""
    import ctypes
    import os
    import threading
    import time

    u = ctypes.windll.user32

    def loop():
        for k in (0x1B, 0x51):
            u.GetAsyncKeyState(k)      # 起動前の打鍵で即終了しないよう履歴を消す
        while True:
            time.sleep(0.02)
            hwnd = u.GetForegroundWindow()
            pid = ctypes.c_ulong()
            u.GetWindowThreadProcessId(hwnd, ctypes.byref(pid))
            mine = pid.value == os.getpid()
            # 0x8000: 押下中 / 0x0001: 前回の呼び出し以降に押された (短い打鍵の取りこぼし防止)
            hit = any(u.GetAsyncKeyState(k) & 0x8001 for k in (0x1B, 0x51))
            mod = u.GetAsyncKeyState(0x11) & 0x8000 or u.GetAsyncKeyState(0x12) & 0x8000
            if mine and hit and not mod and webview.windows:
                webview.windows[0].destroy()
                return

    threading.Thread(target=loop, daemon=True).start()


def main(target):
    if target.startswith(("http://", "https://")):
        _open(target, target)
    else:
        path = Path(target)
        if path.suffix.lower() in CAD_EXTS:
            window = _open(path.name, DWG_URL)
            data = base64.b64encode(path.read_bytes()).decode("ascii")
            script = _INJECT % (json.dumps(path.name), json.dumps(data))
            window.events.loaded += lambda: window.evaluate_js(script)
        else:
            _open(path.name, path.resolve().as_uri())
            if path.suffix.lower() == ".pdf":
                _watch_close_keys()
    webview.start(private_mode=False, storage_path=str(_storage()))


def _storage():
    STORAGE.mkdir(parents=True, exist_ok=True)
    return STORAGE


if __name__ == "__main__":
    if len(sys.argv) >= 6:
        SCALE = float(sys.argv[2])
        DWG_URL = sys.argv[3]
        CAD_EXTS = {x.strip().lower() for x in sys.argv[4].split(",") if x.strip()}
        STORAGE = Path(sys.argv[5])
    main(sys.argv[1])
