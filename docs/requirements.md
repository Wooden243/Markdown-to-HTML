# 要件定義とトレーサビリティ

## 原資料

ユーザー提示の Recursion「Markdown to HTML」課題画面（2026-10-18）を一次情報とする。画面の要点：

- 前回のバックエンド課題に続き、MarkdownファイルをHTMLファイルに変換するプログラムを、**ブラウザから使えるWeb版**として実装する。
- 入力欄は **Monaco コードエディタ**とし、Markdownの入力・編集ができるようにする。
- **Webフォーム**を用意し、入力されたMarkdownをサーバーへ送信してHTMLへ変換する。
- サーバーは既存Markdownコンバータを使用してよい。言語は例示として PHP、Python、Node.js 等。
- 変換されたHTMLを**画面に表示するか、HTMLファイルとしてダウンロード**できる。
- ブラウザでアクセスできるように **Webアプリケーションをリリース**。課題画面にはホスト名の例として `mdtohtml` が登場する。
- オプションとしてコードハイライト、使いやすさを高める補助機能を付けてよい。
- 画像の注意書きにはネットワーク/APIエラーへの対処と、送信処理のエラー時のチェックポイントがある。

## 仕様化した画面動作

1. 初回起動でサンプルMarkdownを入力状態で表示し、右側に生成HTMLの表示を行う。
2. MonacoはCDNから非同期で読み込む（初期操作を妨げない）。読込に失敗した場合はtextareaで編集を継続できる。
3. ユーザーの入力イベントから180ms待って、`POST /api/convert` にJSONを送信する。
4. PythonサーバーがMarkdownをHTMLに変換し、安全化したHTML断片と完成HTML文書を返す。
5. 右側のプレビュー領域にサンドボックスiframeでHTML文書を表示する。
6. HTMLタブでは完成HTML全文を文字列として表示する。
7. HTMLダウンロードを押すと `Blob` から `.html` を生成して保存を開始する。
8. エラー時はメッセージを表示し、古いHTMLを誤ってダウンロードしないようボタンを無効にする。

## 要件対応表

| ID | 課題要件 | 実装箇所 | テスト・確認方法 | 現状 |
|---|---|---|---|---|
| R01 | Markdownを編集できる Monaco エディタ | `public/app.js:tryLoadMonaco()`, `public/index.html:#monaco-container` | 実装・URL・初期化コードを確認。CDNの実接続は未確認 | **実装、実機CDN読込未検証** |
| R02 | Markdown入力フォーム | `public/index.html`, `public/app.js:editorChanged()` | ブラウザUIテストでtextarea入力 | 成功 |
| R03 | Markdown→HTML変換 | `src/converter.py:convert_markdown` | unit tests: 見出し、表、コード、リンクなど | 成功 |
| R04 | サーバーへの送信とレスポンス | `server.py:AppHandler.do_POST`, `public/app.js:renderMarkdown` | HTTP test とブラウザモックUIテスト | 成功 |
| R05 | 変換されたHTMLのプレビュー | `public/app.js:renderMarkdown`, `public/index.html:#preview-frame` | Chromium UIテスト・デスクトップの記録 | 成功 |
| R06 | 変換したHTMLの表示切替 | `public/app.js:selectView` | Chromium UIテスト | 成功 |
| R07 | HTMLファイルのダウンロード | `public/app.js:downloadHTML`, `src/converter.py:make_html_document` | ChromiumダウンロードのHTMLファイル内容テスト | 成功 |
| R08 | ブラウザ経由で使用できるサーバー | `server.py`, `Dockerfile` | 実HTTP GET/POST試験 | 成功（ローカル） |
| R09 | インターネット公開 | `docs/deployment.md` | 実ホスティング／ドメインは外部アカウントを要する | **未実施** |
| R10 | API・異常入力の扱い | `server.py`, `src/converter.py` | 4xx応答、XSS検査 | 成功 |
| R11 | 課題に沿った学習教材・実行手順 | `learning/`, `README.md` | コードと教材の全文一致を自動照合 | 検査済 |
| O01 | ファイル読込、サンプル、クリア | `public/index.html`, `public/app.js` | Chromium UIテスト | 成功（追加機能） |
| O02 | Ctrl/Cmd+S、文字/行数表示 | `public/app.js` | コード検査 | 実装（追加機能） |
| O03 | モバイル対応 | `public/styles.css` | Chromiumの画面サイズとオーバーフロー検査 | 成功（追加機能） |

## 不明点と採用した解釈

- **どのMarkdown拡張まで必要か**：課題はライブラリ選択自由で具体的な方言の指定がないため、CommonMarkと表、取り消し線に対応する。生HTML、LaTeX数式、Mermaidのレンダリングは必須要件とみなさない。
- **変換結果を直接ページに描画するか**：iframe内に安全化したHTMLを表示する。これはプレビューを隔離し、ページのボタンや編集UIにMarkdownが影響しないため。
- **HTMLの表示とダウンロードの選択**：Preview・HTMLタブを切替え、ダウンロードを別ボタンにする。
- **Monacoの提供方法**：CDN読み込み。完全オフラインではtextareaへフォールバック。Monaco実ロードテストには外部ネットワークが必要。
- **本番公開のサービス名・ドメイン**：公開に必要なアカウント・権限は与えられていないため、実際のリリースは行わず、Dockerとデプロイ手順を用意。
- **バックエンド言語**：Pythonを採用。課題資料に複数言語の実装可能性が記載されており、特定言語への強制指定がない。
- **セキュリティ**：入力を変換後サニタイズし、HTML埋め込み、スクリプト実行、危険なリンク等を防ぐ。Markdown表示からHTMLコードへの切替時も `.textContent` で表示。
