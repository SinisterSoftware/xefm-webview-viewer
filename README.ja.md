# WebView Viewer

XeFM のカーソル位置にあるファイルを、別ウィンドウの WebView2 で開く拡張機能です。DWG/DXF は CADXChange の Web ビューアで開き、HTML・SVG・PDF などはローカルファイルをそのまま表示します。

## 動作要件

- Windows
- XeFM 1.11.0 以降
- 拡張機能の Python 依存パッケージ `pywebview`（インストール時に同期するか、後から `xefm deps sync` を実行）
- DWG/DXF を開く場合は CADXChange の Web ビューアに接続できるインターネット環境

## インストール

XeFM で次を実行します。

```text
xefm ext install github:SinisterSoftware/xefm-webview-viewer
```

インストール時に表示される確認に従ってください。依存パッケージの同期を後回しにした場合は、ターミナルで次を実行します。

```text
xefm deps sync
```

その後、XeFM の **Tools ▸ Reload Configuration** を実行するか、XeFM を再起動します。インストール済みかどうかは `xefm ext list` で確認できます。

## 開き方

1. XeFM のファイル一覧で、開きたいファイルにカーソルを合わせます。
2. **File** メニューまたはファイルのコンテキストメニューから **Open in WebView** を選びます。アクションはコマンドパレットからも呼び出せます。
3. 画面中央に WebView ウィンドウが開きます。既定のサイズは画面幅・高さのそれぞれ 80% です。

アクションのキー候補は `Alt-Shift-W` です。XeFM が候補キーを割り当てられなかった場合や、別のキーに変更したい場合は、`~/.xefm/config.py` の `KEY_BINDINGS` に `webview.open` を追加してください。Windows では通常、設定ファイルは `C:\Users\<ユーザー名>\.xefm\config.py` にあります。次は設定例です。既存の `KEY_BINDINGS` がある場合は、テーブルを置き換えず、その中にエントリーだけを追加します。

```python
class Config:
    KEY_BINDINGS = {
        'webview.open': ['Alt-Shift-W'],
    }
```

設定変更後は **Tools ▸ Reload Configuration** を実行するか、XeFM を再起動してください。

## 対応ファイルと表示方法

| 拡張子 | 表示方法 |
| --- | --- |
| `.dwg`, `.dxf` | CADXChange の Web ビューアを開き、選択した図面を読み込ませます。 |
| `.html`, `.htm`, `.xhtml`, `.mht`, `.mhtml` | ローカルファイルを WebView で直接表示します。 |
| `.svg` | ローカルファイルを WebView で直接表示します。 |
| `.pdf` | ローカルファイルを WebView で直接表示します。 |

上記の一覧は既定値です。対象外のファイルを選ぶと、対応する拡張子の一覧を XeFM のメッセージに表示して開きません。フォルダーや、カーソル位置にファイルがない状態では実行できません。

### DWG/DXF を開くときの注意

DWG/DXF はローカルで完結する表示ではありません。拡張機能が図面を読み込み、CADXChange の Web ページに渡して表示します。図面の取り扱い、アップロードやプライバシーは CADXChange のサービスに従います。機密情報を含む図面は、同サービスへ渡してよいことを確認してから開いてください。また、サービスへの接続やサービス側の変更により、表示できない場合があります。

拡張機能は図面ファイル全体を読み込んでからビューアに渡します。そのため、大きなファイルでは相応のメモリを使用します。

### HTML などのローカルファイルを開くときの注意

HTML や SVG などは WebView 内で通常のページとして表示されます。HTML に含まれるスクリプトも実行されるため、信頼できるファイルだけを開いてください。ページが参照する外部リソースには、ネットワーク接続が必要な場合があります。

## 終了方法

WebView ウィンドウが前面にあるときに `Esc` または `Q` を押すと閉じます。PDF ビューアのようにページがキー入力を処理する場合にも閉じられるよう、Windows 側でもキーを監視します。`Ctrl` または `Alt` と同時に押した場合は閉じません。

## 設定

既定値は拡張機能の設定として定義されています。`xefm ext settings webview-viewer` を実行すると、現在の XeFM で使う設定クラス名と貼り付け用の設定例を確認できます。必要な属性だけを `~/.xefm/config.py` の対応する設定クラスに追加してください。

| 設定 | 既定値 | 説明 |
| --- | --- | --- |
| `WEB_EXTS` | `[".dwg", ".dxf", ".pdf", ".html", ".htm", ".svg", ".xhtml", ".mht", ".mhtml"]` | アクションで受け付ける拡張子。小文字・先頭にドットを付けて指定します。 |
| `CAD_EXTS` | `[".dwg", ".dxf"]` | CADXChange ビューアに渡す拡張子。 |
| `DWG_VIEWER_URL` | `https://cadxchange.net/ja/dwg-viewer` | DWG/DXF の表示に使う Web ビューアの URL。 |
| `WINDOW_SCALE` | `0.8` | 画面に対するウィンドウの幅・高さの比率。たとえば `0.6` は各寸法の 60% です。 |

`WEB_EXTS` に拡張子を追加すると、そのファイルは WebView で直接開かれます。CADXChange に渡す場合は `CAD_EXTS` にも含めますが、DWG/DXF 以外の形式がビューアで動作する保証はありません。拡張子を削除すればアクションの対象外になります。設定は **Tools ▸ Reload Configuration** を実行するか、XeFM を再起動して反映します。

## 保存されるデータ

WebView のブラウザーデータは、ユーザーごとの XeFM 状態フォルダー `~/.xefm/state/webview-viewer` に保存されます。Windows では通常 `C:\Users\<ユーザー名>\.xefm\state\webview-viewer` です。ログイン状態や Cookie などが残ることがあるため、共有環境ではご注意ください。

## トラブルシューティング

- **「pywebview が未導入です」と表示される**: `xefm deps sync` を実行し、同期が完了したら **Tools ▸ Reload Configuration** を実行するか XeFM を再起動してください。
- **「ファイルにカーソルを合わせてください」と表示される**: ファイル一覧で通常のファイルにカーソルを合わせてから実行してください。
- **「WebView 対象外」と表示される**: 表示された拡張子一覧を確認してください。必要なら `WEB_EXTS` を設定します。
- **DWG/DXF が表示されない**: インターネット接続と CADXChange の稼働状況を確認してください。ビューア側が対象ファイルを受け付けない場合もあります。
- **メニュー項目が見つからない**: 拡張機能が有効か `xefm ext list` で確認し、設定を再読み込みするか XeFM を再起動してください。コマンドパレットから `webview.open` を探すこともできます。
- **キーが反応しない**: XeFM のキー設定で `webview.open` に割り当てたキーが、他のアクションや OS に使われていないか確認してください。キー候補が適用されなかった場合は `KEY_BINDINGS` で明示的に設定してください。

## 開発者向け

リポジトリのルートで拡張機能のマニフェストとコードを確認するには、次を実行します。

```text
xefm ext check .
```
