# 00｜最初に読む — Markdown to HTML

> この資料は実装済みの `Markdown-to-HTML` プロジェクトを理解するための学習ガイドです。最短15分でも構造を把握でき、時間をかければ全行まで追えるよう構成しています。

## 1. 3分で把握する完成品

このWebアプリは「ブラウザにMarkdownを書く → ブラウザがPythonサーバーへ文字列を送る → サーバーがHTMLへ変換して返す → ブラウザに表示し、必要ならHTMLファイルとして保存する」という仕組みです。

```text
利用者のキーボード
    ↓（inputイベント）
Monaco Editor / textarea                 public/app.js
    ↓（180msのデバウンス）
fetch('/api/convert', POST JSON)
    ↓ HTTP（ブラウザ → Pythonサーバー）
AppHandler.do_POST()                      server.py
    ↓ 入力・サイズ・型を検証
convert_markdown()                        src/converter.py
    ↓ MarkdownItによる変換 → bleachによる安全化
make_html_document()                      src/converter.py
    ↓ 完成HTML文書をJSONにして返送
renderMarkdown()                          public/app.js
    ├─ iframe.srcdoc：表示（隔離されたプレビュー）
    └─ Blob → a.download：HTMLファイルの保存
```

**核心は `fetch` と `do_POST` のつながり**です。見た目を変更するCSSより、まずこの往復を理解してください。

## 2. 最重要の5ファイル

| 順番 | ファイル | 役割 | 優先度 |
|---|---|---|---|
| 1 | `public/app.js` | 編集イベント、非同期通信、プレビュー更新、ダウンロード | **必須** |
| 2 | `server.py` | HTTP受付、入力検証、API応答、静的ファイル配信 | **必須** |
| 3 | `src/converter.py` | MarkdownからHTMLへの変換と安全化 | **必須** |
| 4 | `public/index.html` | 入力欄、プレビュー、各ボタンの配置 | 重要 |
| 5 | `public/styles.css` | レイアウト、色、レスポンシブ調整 | 参考 |

## 3. 特に重要な関数

1. `editorChanged(value)` — 新しい入力を受け、前の通信を中断し、最新の変換だけを予約。
2. `renderMarkdown(markdown, sequence)` — `fetch` でPOST、JSONを受け、画面とダウンロード用HTMLを更新。
3. `AppHandler.do_POST(self)` — APIへのPOSTが妥当か確認し、Python変換関数を呼ぶ。
4. `convert_markdown(markdown)` — Markdown → HTML断片、危険なタグや属性を除去。
5. `make_html_document(fragment)` — HTML断片を完全なHTML5文書として包み、CSSを埋め込む。
6. `downloadHTML()` — `Blob` と `URL.createObjectURL` を使いクライアントでダウンロード開始。
7. `tryLoadMonaco()` — CDNエディタを読み込み、オフラインではtextareaのまま操作可能にする。

## 4. どこまで覚えるべき？

**まず理解すべき**：ブラウザとサーバーの役割分担、GETとPOST、JSON、イベント、非同期、状態の更新、HTMLエスケープ、サニタイズ、ダウンロード。

**後回しでよい**：Monacoの細かなオプション、すべてのCSSプロパティ、CSPの詳細なディレクティブ、各種HTTPステータス番号の暗記、Dockerfileの細部。

暗記より「ユーザーが入力したデータが、どのファイルのどの関数を経由して、画面に出てくるか」を説明できることを重視します。

## 5. 学習時間別コース

### 15分

- このガイド（3分）。
- `learning/01_ARCHITECTURE.md` のシーケンス（3分）。
- `learning/03_EXECUTION_FLOW.md` の具体例（5分）。
- `public/app.js` の `renderMarkdown()` と `server.py` の `do_POST()` に目を通す（4分）。

到達目標：「画面が更新されるまで」を図なしで説明できる。

### 30分

上の15分に加え、`learning/02_KEY_CONCEPTS.md` の HTTP/JSON/async/await/サニタイズ/Blob を読み、`learning/05_REVIEW.md` の最初の5問を解く。

到達目標：「なぜ単なるHTMLファイルだけではこのバックエンド構成にならないのか」「古いレスポンスを捨てる理由」を説明できる。

### 60分

上の30分に加え、`code-walkthrough/app.js.md`、`code-walkthrough/server.py.md`、`code-walkthrough/converter.py.md` を実行順に読みながら、入力例を自分で変更して動作を比較する。

到達目標：課題要件を満たす別バージョンを自力で設計できる。

## 6. 技術分野ごとの重要度

| 技術分野 | 特に重要な学習要素 | 重要度 |
|---|---|---|
| ソフトウェア開発 | モジュール境界、入力検証、責務分割、テスト、デプロイ | **非常に高い** |
| Web/フロントエンド | DOM、イベント、非同期fetch、UI状態、アクセシビリティ | **非常に高い** |
| AI/MLアプリケーション | テキスト入力→サーバー処理→結果返却という推論APIと同形の処理、入出力検証 | **高い** |

## 7. 最短の動作確認

```bash
python3 -m venv .venv
source .venv/bin/activate
python -m pip install -r requirements.txt
python server.py
```

ブラウザで `http://127.0.0.1:8000/` を開く。Markdownを変更 → Preview → HTML → Downloadを試す。終了 `Ctrl+C`。

テスト：`python -m unittest discover -s tests -p 'test_*.py' -v`。

## 8. 読み進める順序

`00_START_HERE` → `01_ARCHITECTURE` → `03_EXECUTION_FLOW` → `02_KEY_CONCEPTS` → `code-walkthrough/app.js` → `code-walkthrough/server.py` → `code-walkthrough/converter.py` → `04_DEBUGGING` → `05_REVIEW`。 HTML/CSSに深く取り組むときだけ、それぞれの全文解説に進んでください。
