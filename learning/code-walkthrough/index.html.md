# ソース全文・逐次解説｜`public/index.html`

> 元ファイルと全文一致するソーススナップショットです。変更した場合はこの教材も再生成してください。

## 1. ファイルの役割

- **役割**：ブラウザの構造と操作要素。スタイルとJavaScriptを読み込み、DOMのidを通じてJSと接続する。
- **依存関係**：public/styles.css、public/app.js、ブラウザ標準のHTML/DOM。
- **入力・出力**：入力：文字入力、ファイル選択、各種クリック。出力：画面のレイアウトとJSが更新する表示領域。
- **前提知識**：`learning/02_KEY_CONCEPTS.md` の関連節。

## 2. 元のソースコード全文

```html
<!doctype html>
<html lang="ja">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <meta name="description" content="Markdownを書きながらHTMLをプレビューして、完成したHTMLファイルをダウンロードできます。">
  <title>Markdown to HTML — Studio</title>
  <link rel="stylesheet" href="/styles.css">
  <script src="/app.js" defer></script>
</head>
<body>
  <div class="app-shell">
    <header class="site-header">
      <a class="logo" href="/" aria-label="Markdown to HTML ホーム">
        <span class="brand-icon" aria-hidden="true">M<span>↗</span></span>
        <span>markdown<span class="brand-faint">/</span>html</span>
      </a>
      <span class="header-mark">WEB CONVERTER <span class="mark-dot">●</span> V1.0</span>
      <span class="github-hint">LOCAL-FIRST <span aria-hidden="true">✦</span></span>
    </header>

    <main class="workspace" id="main">
      <div class="hero">
        <div class="hero-content">
          <p class="eyebrow"><span class="eyebrow-line"></span> THE MARKDOWN WORKSPACE</p>
          <h1>Write in Markdown.<br><span>See it in HTML.</span></h1>
          <p class="hero-subtitle">MarkdownをHTMLに変換。書いた内容をすぐに確認し、<br class="desktop-break">そのままHTMLファイルとして保存できます。</p>
        </div>
        <div class="hero-symbol" aria-hidden="true"><span>md</span><span class="hero-arrow">→</span><span>html</span></div>
      </div>

      <section class="work-card" aria-label="Markdownエディタとプレビュー">
        <div class="work-toolbar">
          <div class="file-ident">
            <span class="file-icon" aria-hidden="true">M↓</span>
            <span class="file-name">untitled.md</span>
            <span class="unsaved-dot" id="unsaved-dot" title="編集済み" hidden></span>
          </div>
          <div class="toolbar-actions">
            <button class="tool-button" type="button" id="upload-button" title=".mdファイルを読み込む"><span aria-hidden="true">↥</span> 読み込む</button>
            <input type="file" id="file-input" accept=".md,.markdown,.txt,text/markdown,text/plain" hidden>
            <button class="tool-button" type="button" id="sample-button">サンプル</button>
            <button class="tool-button" type="button" id="clear-button">クリア</button>
            <span class="action-divider" aria-hidden="true"></span>
            <button class="primary-button" type="button" id="download-button"><span aria-hidden="true">↓</span> HTMLをダウンロード</button>
          </div>
        </div>

        <div class="editor-grid">
          <section class="pane editor-pane" aria-labelledby="editor-label">
            <div class="pane-heading">
              <div class="pane-title"><span class="green-dot"></span><h2 id="editor-label">MARKDOWN EDITOR</h2></div>
              <span class="heading-note" id="editor-mode">テキストエディタ</span>
            </div>
            <div class="code-surface" id="editor-frame">
              <div id="monaco-container" aria-label="Monaco Markdownエディタ"></div>
              <label for="markdown-input" class="sr-only">Markdownを入力してください</label>
              <textarea id="markdown-input" spellcheck="false" aria-label="Markdownを入力してください" autocomplete="off" autocapitalize="off"></textarea>
            </div>
            <div class="pane-footer"><span id="character-count">0 文字</span><span id="line-count">0 行</span></div>
          </section>

          <section class="pane preview-pane" aria-labelledby="preview-label">
            <div class="pane-heading preview-heading">
              <div class="pane-title"><span class="blue-dot"></span><h2 id="preview-label">LIVE PREVIEW</h2></div>
              <div class="view-toggle" role="group" aria-label="表示形式を選択">
                <button type="button" class="view-button active" id="preview-tab" aria-pressed="true">Preview</button>
                <button type="button" class="view-button" id="html-tab" aria-pressed="false">HTML</button>
              </div>
            </div>
            <div class="output-surface">
              <iframe id="preview-frame" title="変換結果のプレビュー" sandbox="" referrerpolicy="no-referrer"></iframe>
              <div id="html-panel" hidden>
                <button type="button" id="copy-button" class="copy-button">HTMLをコピー</button>
                <pre><code id="html-source"></code></pre>
              </div>
            </div>
            <div class="pane-footer"><span id="render-status" role="status" aria-live="polite">準備中...</span><span class="status-right">HTML5</span></div>
          </section>
        </div>
      </section>

      <div class="info-row">
        <div class="info-intro"><span class="spark" aria-hidden="true">✳</span> WRITE. PREVIEW. EXPORT.<p>Markdownの編集からHTMLファイルの保存まで、この画面で完結します。</p></div>
        <div class="shortcuts"><kbd>Ctrl</kbd><span>+</span><kbd>S</kbd><span>保存</span></div>
      </div>
      <p class="privacy-note">Markdownは変換のためローカルサーバーに送信されます。変換内容をサーバーに保存する機能はありません。Monacoエディタの読み込みにはインターネット接続が必要です。</p>
    </main>
    <footer class="site-footer"><span>MARKDOWN TO HTML</span><span>Built for a better writing workflow.</span></footer>
  </div>
</body>
</html>
```

コード行数：92行。SHA-256：`29f854039571ad9a58a497c982bc372afd84cceefbb1e2b6dd3b5f457ed3b5df`

## 3. 上から順に読む詳細解説

以下は上記ソースの先頭から末尾までを、意味がまとまる範囲で逐次説明したものです。

### 1. HTML文書の宣言とhead（1〜11行）

**該当箇所の冒頭**：`<!doctype html>`

`<!doctype html>` はHTML5として解釈させる宣言。`lang=ja`は文書言語。`meta charset=utf-8` で日本語を正しく表示。`viewport` はモバイル表示の幅制御。`link rel=stylesheet` がCSSを読み込み、`script src=/app.js defer` がHTML解析後にJavaScriptを実行する。`defer`を消すとDOMがまだ存在しない時点でJSが実行される場合がある。

### 2. ページ全体とヘッダー（12〜21行）

**該当箇所の冒頭**：`<div class="app-shell">`

`.app-shell` は全体の縦レイアウト用。`header` にはロゴ、ステータス表示を配置する。`aria-label` はリンクの意味をスクリーンリーダーへ伝える。視覚装飾には `aria-hidden=true` を指定し、読み上げの冗長さを減らす。

### 3. ヒーロー領域（22〜31行）

**該当箇所の冒頭**：`<main class="workspace" id="main">`

`main` は主コンテンツを示すセマンティックなHTML要素。`hero` はタイトルと説明文を配置する。`h1` はページの第一見出し、`span` と `br` でスタイル上の強調を付ける。見た目の調整はCSSで行い、重要な操作ロジックは含まない。

### 4. ワークスペースのツールバー（32〜48行）

**該当箇所の冒頭**：`<section class="work-card" aria-label="Markdownエディタとプレビュー">`

`section` はまとまった機能領域。`#upload-button` のイベントで `#file-input` をクリックしてファイル選択を開く。`input type=file` はOSのファイル選択を利用し、`accept` は選択候補の形式を提示する。`#sample-button`、`#clear-button`、`#download-button` はそれぞれJSのイベントに結び付く。`type=button` は意図しないフォーム送信を防ぐ。

### 5. 2ペインの配置と入力欄（49〜62行）

**該当箇所の冒頭**：`<div class="editor-grid">`

`.editor-grid` は左右のエディタとプレビューをCSS Gridで並べる。`#monaco-container` は後から作られるMonacoの描画先。`#markdown-input` はネット接続に依存しないtextarea。`label` の `for` とidの対応はアクセシビリティを高める。`#character-count` と `#line-count` はJSで変更されるテキスト。

### 6. プレビュー・HTMLソース・ステータス（63〜82行）

**該当箇所の冒頭**：`<section class="pane preview-pane" aria-labelledby="preview-label">`

Preview/HTMLボタンには `aria-pressed` で選択状態を与える。`#preview-frame` は `sandbox=""` を持つiframeで、変換HTMLを隔離。`#html-source` はコード文字列を表示する領域、`#copy-button` はクリップボード操作。`#render-status` は `role=status` と `aria-live=polite` で状態変化を知らせる。`hidden` 属性の有無で2つの表示を切り替える。

### 7. 補助説明とフッター（83〜92行）

**該当箇所の冒頭**：`<div class="info-row">`

ショートカットの `<kbd>` はキーボード入力を示す意味的なタグ。プライバシーに関する説明は、Markdownがローカルサーバーで処理されることとMonacoのCDN依存を知らせる。`footer` はサイト全体の補助情報。ブラウザとサーバーは入力文書を長期保存する仕組みを備えていない。

## 4. 実行トレース

初回ロードで `styles.css` と `app.js` が取得され、`#markdown-input` にサンプルが入力される。利用者が `#download-button` を押すと `app.js` の登録済みイベントから保存処理へ進む。`#preview-frame` には別のHTML文書が srcdoc として読み込まれる。

## 5. 最重要ポイント

1. HTMLは構造、CSSは見た目、JSは振る舞い。
2. idはJavaScriptとの接点。
3. script deferはDOMのパース後にJSを実行。
4. button type=buttonはフォーム送信を意図しない操作。
5. textareaはMonacoがなくても動く。
6. iframe sandboxはプレビューを隔離する。
7. aria属性は支援技術のために用いる。

## 6. 自分で検証するには

詳細な起動手順は `README.md`、具体的な変数の流れは `learning/03_EXECUTION_FLOW.md`、デバッグは `learning/04_DEBUGGING.md` を参照。

**この教材のコード全文は、上記SHA-256値で元ソースとの一致を確認できます。**
