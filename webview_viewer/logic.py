import importlib.util
import os
import subprocess
from pathlib import Path
from typing import Any, Dict

from xefm.user_api import extension, xefm_python

_DEFAULTS: Dict[str, Any] = {
    "WEB_EXTS": [".dwg", ".dxf", ".pdf", ".html", ".htm", ".svg", ".xhtml", ".mht", ".mhtml"],
    "CAD_EXTS": [".dwg", ".dxf"],
    "DWG_VIEWER_URL": "https://cadxchange.net/ja/dwg-viewer",
    "WINDOW_SCALE": 0.8,
}
OVERRIDES: Dict[str, Any] = {}

RUNNER = Path(__file__).with_name("runner.py")


def cfg(name: str) -> Any:
    if name in OVERRIDES:
        return OVERRIDES[name]
    ext = extension(__name__)
    if ext is not None:
        return getattr(ext.settings, name, _DEFAULTS[name])
    return _DEFAULTS[name]


def storage_dir() -> Path:
    return Path.home() / ".xefm" / "state" / "webview-viewer"


def build_command(path: str) -> list:
    return [str(xefm_python), str(RUNNER), path,
            str(cfg("WINDOW_SCALE")), cfg("DWG_VIEWER_URL"),
            ",".join(cfg("CAD_EXTS")), str(storage_dir())]


def open_file(ctx) -> None:
    e = ctx.pane.focused
    if e is None or not e.is_file:
        ctx.message("ファイルにカーソルを合わせてください")
        return
    exts = {x.lower() for x in cfg("WEB_EXTS")}
    if e.suffix.lower() not in exts:
        ctx.message("WebView 対象外: " + ", ".join(sorted(exts)))
        return
    # サブプロセスにも同期済み python_packages の場所を渡す (pywebview と依存は同じ site-packages にある)
    spec = importlib.util.find_spec("webview")
    if spec is None or not spec.origin:
        ctx.message("pywebview が未導入です: xefm deps sync を実行してください")
        return
    site = str(Path(spec.origin).parent.parent)
    env = {**os.environ, "PYTHONPATH": site}
    subprocess.Popen(build_command(os.path.normpath(str(e.path))), env=env, creationflags=0x08000000)
    ctx.message("WebView で開いています…")
