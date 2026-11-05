class Settings:
    # 開く対象の拡張子 (小文字、ドット付き)
    WEB_EXTS = [".dwg", ".dxf", ".pdf", ".html", ".htm", ".svg", ".xhtml", ".mht", ".mhtml"]
    # このうち DWG ビューアに読み込ませる拡張子
    CAD_EXTS = [".dwg", ".dxf"]
    DWG_VIEWER_URL = "https://cadxchange.net/ja/dwg-viewer"
    # ウィンドウ寸法 = 画面の何割か (中央に表示)
    WINDOW_SCALE = 0.8
