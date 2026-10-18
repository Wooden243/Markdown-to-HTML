# ソース全文・逐次解説｜`public/styles.css`

> 元ファイルと全文一致するソーススナップショットです。変更した場合はこの教材も再生成してください。

## 1. ファイルの役割

- **役割**：アプリの外側の見た目とレスポンシブレイアウト。生成されたHTMLの見た目は別のCSSを使う。
- **依存関係**：public/index.htmlのclass名・id、public/app.jsが付ける .monaco-ready / .active クラス。
- **入力・出力**：入力：ブラウザの画面幅、DOMのclass/hidden状態。出力：配置・サイズ・色・可視性。
- **前提知識**：`learning/02_KEY_CONCEPTS.md` の関連節。

## 2. 元のソースコード全文

```css
:root{color-scheme:light;font-family:'DM Sans',system-ui,-apple-system,BlinkMacSystemFont,'Segoe UI',sans-serif;color:#17263e;background:#f5f6f9;font-synthesis:none}
*{box-sizing:border-box}html{min-height:100%;scroll-behavior:smooth}body{margin:0;min-height:100vh}
button,input,textarea{font:inherit}button{cursor:pointer}button:focus-visible,a:focus-visible,textarea:focus-visible{outline:3px solid #8eb8fd;outline-offset:2px}a{color:inherit;text-decoration:none}[hidden]{display:none!important}
.app-shell{min-height:100vh;display:flex;flex-direction:column}
.site-header{height:70px;flex-shrink:0;background:#fff;border-bottom:1px solid #e6e9f0;display:flex;align-items:center;justify-content:space-between;padding:0 clamp(18px,4.6vw,76px);gap:24px}
.logo{display:inline-flex;align-items:center;gap:12px;font-family:'Space Grotesk',sans-serif;font-size:20px;font-weight:700;letter-spacing:-.065em;color:#1c2c46;white-space:nowrap}
.brand-icon{display:flex;width:34px;height:34px;align-items:center;justify-content:center;border-radius:9px;color:#fff;background:#26467d;font-size:17px;letter-spacing:-3px;padding-right:4px}.brand-icon span{font-size:12px;margin-left:1px;color:#99d9ef}.brand-faint{color:#a3b0c5;padding:0 2px}
.header-mark{font-family:'Space Grotesk',sans-serif;font-size:10px;letter-spacing:.16em;color:#8190a6;font-weight:600}.mark-dot{font-size:7px;color:#33b98b;vertical-align:2px;margin:0 5px}
.github-hint{font-size:12px;font-weight:700;color:#6d7a90}.github-hint span{margin-left:7px}
.workspace{width:min(1392px,calc(100% - 80px));margin:0 auto;flex:1}
.hero{display:flex;align-items:center;justify-content:space-between;gap:32px;padding:61px 7px 49px}.eyebrow{display:flex;align-items:center;gap:11px;font-family:'Space Grotesk',sans-serif;font-size:11px;font-weight:700;letter-spacing:.19em;color:#527caa;margin:0 0 16px}.eyebrow-line{width:27px;height:2px;background:#4b85ce}.hero h1{font-family:'Space Grotesk',sans-serif;font-size:clamp(34px,4.1vw,62px);letter-spacing:-.069em;line-height:1.075;font-weight:700;margin:0 0 19px}.hero h1 span{color:#7e93b4}.hero-subtitle{line-height:1.8;color:#728096;font-size:14px;margin:0}.hero-symbol{flex-shrink:0;display:flex;align-items:center;gap:18px;color:#acb9cc;font-family:'Space Grotesk',sans-serif;font-size:43px;font-weight:700;letter-spacing:-.07em;user-select:none;padding-right:28px}.hero-symbol span:first-child{color:#426c9d}.hero-symbol .hero-arrow{font-size:30px;color:#adc0d4}.hero-symbol span:last-child{color:#90a2b9}
.work-card{background:#fff;border:1px solid #e0e6f0;border-radius:14px;overflow:hidden;box-shadow:0 16px 48px rgba(34,51,78,.055)}
.work-toolbar{height:68px;display:flex;align-items:center;justify-content:space-between;gap:16px;padding:0 20px 0 22px;border-bottom:1px solid #e7ebf1}
.file-ident,.toolbar-actions{display:flex;align-items:center}.file-ident{gap:10px}.file-icon{display:flex;align-items:center;justify-content:center;background:#e7effa;color:#3970a8;border-radius:6px;width:29px;height:29px;font-size:13px;font-weight:800}.file-name{font-size:13px;font-weight:700;color:#34445e}.unsaved-dot{width:6px;height:6px;border-radius:100%;background:#eba657}.toolbar-actions{gap:8px}.tool-button{border:1px solid transparent;background:transparent;color:#687892;font-size:12px;padding:9px 11px;border-radius:7px;font-weight:600}.tool-button:hover{background:#f0f4f9;color:#354e73}.action-divider{height:25px;width:1px;background:#e3e8f1;margin:0 6px}.primary-button{display:flex;align-items:center;gap:9px;background:#2a548e;color:white;border:1px solid #2a548e;border-radius:8px;padding:11px 16px;font-size:12px;font-weight:700;white-space:nowrap;box-shadow:0 4px 8px rgba(41,81,140,.1)}.primary-button:hover{background:#1c416f}.primary-button:disabled{opacity:.55;cursor:wait}
.editor-grid{display:grid;grid-template-columns:minmax(0,1fr) minmax(0,1fr);min-height:540px}.pane{min-width:0;display:flex;flex-direction:column}.editor-pane{border-right:1px solid #e6eaf1}.pane-heading{height:51px;flex-shrink:0;background:#fbfcfe;border-bottom:1px solid #e6eaf1;display:flex;align-items:center;justify-content:space-between;padding:0 19px;gap:12px}.pane-title{display:flex;gap:9px;align-items:center}.pane-title h2{font-family:'Space Grotesk',sans-serif;letter-spacing:.115em;font-weight:700;color:#58677d;font-size:10px;margin:0}.green-dot,.blue-dot{width:7px;height:7px;border-radius:50%;background:#26b58c}.blue-dot{background:#5b91e1}.heading-note{font-size:11px;color:#a0acbd}.code-surface{height:480px;position:relative;overflow:hidden;background:#1c2637}.code-surface textarea{width:100%;height:100%;resize:none;border:0;outline:none;background:#1c2637;color:#dbe6f4;padding:22px 24px;font-family:ui-monospace,Consolas,'Courier New',monospace;font-size:13px;line-height:1.73;tab-size:2}.code-surface textarea::selection{background:#466c9c}.code-surface #monaco-container{display:none;position:absolute;inset:0;z-index:2}.code-surface.monaco-ready #monaco-container{display:block}.code-surface.monaco-ready textarea{visibility:hidden}.pane-footer{background:#fcfdff;color:#8694a9;font-size:10px;letter-spacing:.03em;font-weight:600;height:35px;flex-shrink:0;display:flex;justify-content:space-between;align-items:center;padding:0 19px;border-top:1px solid #e6eaf1}
.preview-heading{padding-right:15px}.view-toggle{display:flex;padding:3px;background:#eaf0f7;border-radius:7px;gap:1px}.view-button{border:0;background:transparent;color:#7a8aa1;font-size:10px;padding:6px 10px;border-radius:5px;font-weight:700}.view-button.active{background:#fff;color:#3266a0;box-shadow:0 1px 4px rgba(18,40,73,.13)}
.output-surface{height:480px;min-height:0;overflow:hidden;background:#fff;position:relative}.output-surface iframe{border:0;width:100%;height:100%;background:white}.output-surface #html-panel{height:100%;position:relative;background:#f7f9fc;overflow:auto}.output-surface pre{padding:54px 22px 22px;margin:0;font-size:12px;line-height:1.7;color:#354a67;font-family:ui-monospace,Consolas,monospace;white-space:pre-wrap;overflow-wrap:anywhere}.copy-button{position:sticky;left:calc(100% - 125px);top:12px;margin:12px 15px -44px auto;display:block;z-index:1;padding:8px 12px;background:#fff;border:1px solid #dce5f1;border-radius:6px;color:#476a9b;font-weight:700;font-size:10px}.copy-button:hover{background:#eaf2ff}.status-right{font-family:'Space Grotesk',sans-serif}
.info-row{padding:25px 4px 0;display:flex;align-items:center;justify-content:space-between;gap:16px}.info-intro{font-family:'Space Grotesk',sans-serif;font-size:11px;font-weight:700;color:#657791;letter-spacing:.12em}.spark{font-size:17px;margin-right:7px;color:#4c7eb7}.info-intro p{font-family:'DM Sans',sans-serif;font-size:12px;font-weight:400;letter-spacing:0;color:#9ba6b7;margin:8px 0 0}.shortcuts{display:flex;align-items:center;gap:7px;color:#95a4b8;font-size:11px}.shortcuts kbd{font-family:inherit;padding:4px 8px;border:1px solid #dce3ef;background:#fff;border-radius:5px;font-weight:700;color:#718198}.shortcuts span:last-child{margin-left:6px}.privacy-note{margin:23px 4px 44px;color:#a3adbc;font-size:11px;line-height:1.7}.site-footer{border-top:1px solid #e5eaf1;display:flex;align-items:center;justify-content:space-between;padding:22px max(40px,calc((100% - 1392px)/2));font-size:10px;font-weight:700;letter-spacing:.13em;color:#9ba9bd}.site-footer span:last-child{letter-spacing:0;font-weight:500}
.sr-only{position:absolute;width:1px;height:1px;clip:rect(0,0,0,0);white-space:nowrap;overflow:hidden}
@media(max-width:1050px){.workspace{width:min(100% - 36px,1392px)}.hero{padding:43px 4px 36px}.hero-symbol{font-size:28px}.toolbar-actions{gap:1px}}
@media(max-width:760px){.site-header{height:58px;padding:0 18px}.header-mark{display:none}.hero{padding:38px 2px 32px}.hero-symbol{display:none}.hero h1{font-size:36px}.desktop-break{display:none}.work-toolbar{padding:12px 14px;min-height:60px;height:auto;align-items:flex-start;flex-wrap:wrap}.toolbar-actions{flex-wrap:wrap}.tool-button{padding:9px 8px}.action-divider{display:none}.primary-button{padding:9px 12px}.editor-grid{display:block}.editor-pane{border-right:0;border-bottom:1px solid #e6eaf1}.code-surface{height:340px}.output-surface{height:340px}.pane-heading{height:47px}.info-row{align-items:flex-start;flex-direction:column}.shortcuts{display:none}.site-footer{padding:18px;gap:12px}.site-footer span:last-child{display:none}}
@media(max-width:420px){.logo{font-size:17px}.hero h1{font-size:31px}.hero-subtitle{font-size:12px}.file-name{font-size:12px}.work-toolbar{gap:5px}.tool-button{font-size:11px}.primary-button{font-size:11px}.toolbar-actions{width:100%}.workspace{width:calc(100% - 20px)}.pane-heading{padding:0 12px}}
```

コード行数：22行。SHA-256：`ed7531a2fb34cfca2d3e836e700dfbe9e3af1d4983092ebfc0fb7f2150853a5d`

## 3. 上から順に読む詳細解説

以下は上記ソースの先頭から末尾までを、意味がまとまる範囲で逐次説明したものです。

### 1. ルート変数・全体の初期設定（1〜3行）

**該当箇所の冒頭**：`:root{color-scheme:light;font-family:'DM Sans',system-ui,-apple-system,BlinkMacSystemFont,'Segoe UI'`

`:root` は文書全体にかかるセレクター。`color-scheme:light` はブラウザの配色前提を指定し、`font-family` はOS標準のフォントを代替順で設定。`*{box-sizing:border-box}` はpaddingやborderを要素の指定幅に含める。`body{margin:0}` でブラウザの既定余白を除く。

### 2. ヘッダーと全体の縦配置（4〜9行）

**該当箇所の冒頭**：`.app-shell{min-height:100vh;display:flex;flex-direction:column}`

`display:flex` と `flex-direction:column` でヘッダー、main、footerを縦方向に並べる。`.site-header` は横並びかつ両端寄せ、`.logo` にはサイズと文字間隔を設定。`gap` は子要素の間隔、`padding` は要素内の余白。CSSはレイアウトを示すだけでクリックイベントは担当しない。

### 3. 本文の最大幅とヒーロー（10〜11行）

**該当箇所の冒頭**：`.workspace{width:min(1392px,calc(100% - 80px));margin:0 auto;flex:1}`

`width:min(1392px,calc(100% - 80px))` は大画面で幅を制限し、狭い画面では余白を残す。`.hero` はタイトル領域、`.eyebrow`は小見出し、`clamp`で文字サイズや余白を画面幅に応じて調整する。ここは見た目なので機能要件ではないが読みやすさに影響。

### 4. 作業領域とツールバー（12〜14行）

**該当箇所の冒頭**：`.work-card{background:#fff;border:1px solid #e0e6f0;border-radius:14px;overflow:hidden;box-shadow:0 `

`.work-card` は白いカード型の背景・境界・影を担当する。`.work-toolbar` はファイル名とボタン群の横並び。`.primary-button` は主操作のダウンロードボタン。`:hover` はマウスを乗せたときの見た目、`:disabled` は変換中の無効状態を示す。JS側でもdisabledを設定しないと実際の制御はできない。

### 5. 編集・プレビューの2カラムとMonacoの重ね合わせ（15〜15行）

**該当箇所の冒頭**：`.editor-grid{display:grid;grid-template-columns:minmax(0,1fr) minmax(0,1fr);min-height:540px}.pane{m`

`display:grid`、`grid-template-columns:minmax(0,1fr) minmax(0,1fr)` により左右を等幅にする。`.code-surface` は相対配置で、Monaco領域を絶対配置してtextareaと同じ範囲に重ねる。初期はMonacoを `display:none`、読み込み成功後は `.monaco-ready` で表示しtextareaを隠す。エディタの高さは480px、スクロールは内部で処理。

### 6. 表示切替とHTMLソース表示（16〜17行）

**該当箇所の冒頭**：`.preview-heading{padding-right:15px}.view-toggle{display:flex;padding:3px;background:#eaf0f7;border-`

`.view-toggle` はPreview/HTML切替ボタンの入れ物、`.view-button.active` が選択状態。`.output-surface iframe` はプレビュー面全体を使う。`pre` は空白や改行を保ってHTML全文を表示し、`white-space:pre-wrap` で横幅に合わせて折り返す。コピー操作ボタンはstickyでスクロール時も押しやすくする。

### 7. 画面下部の説明・補足（18〜19行）

**該当箇所の冒頭**：`.info-row{padding:25px 4px 0;display:flex;align-items:center;justify-content:space-between;gap:16px}`

`.info-row` は機能概要とショートカットの並び。`kbd` 風の要素はCSSでキーらしく装飾する。`.privacy-note` は小さな補足テキスト、`.site-footer` はフッター。`.sr-only` は視覚的には隠しながらスクリーンリーダー用にテキストを保持するアクセシビリティ用クラス。

### 8. 画面幅別レイアウトの切替（20〜22行）

**該当箇所の冒頭**：`@media(max-width:1050px){.workspace{width:min(100% - 36px,1392px)}.hero{padding:43px 4px 36px}.hero-`

`@media` は画面幅などの条件に応じてCSSを適用する。1050px以下で余白や文字サイズを縮小、760px以下では`.editor-grid{display:block}`で縦並びにする。420px以下ではツールバーの幅や文字サイズをさらに調整。`@media`がないとスマホで2つの狭いペインになり操作しにくい。

## 4. 実行トレース

デスクトップ幅1400pxでは `.editor-grid` が2列に分割される。幅390pxでは `@media(max-width:760px)` が発火し、エディタ→プレビューの縦並びになる。Monaco読込成功でJSが `.monaco-ready` を付けると、Monaco領域がdisplay:block、textareaがvisibility:hiddenになる。

## 5. 最重要ポイント

1. セレクターがHTMLのclass名に一致して初めてスタイルが効く。
2. box-sizing:border-boxで幅計算を分かりやすくする。
3. CSS Gridは編集とプレビューの2列配置に使用。
4. overflowはコードが画面外へはみ出さないため。
5. hidden属性と.activeクラスが状態に応じた見た目を決める。
6. @mediaはモバイルの並びを変える。
7. Preview中のHTMLは別CSS（DOCUMENT_CSS）で整形。

## 6. 自分で検証するには

詳細な起動手順は `README.md`、具体的な変数の流れは `learning/03_EXECUTION_FLOW.md`、デバッグは `learning/04_DEBUGGING.md` を参照。

**この教材のコード全文は、上記SHA-256値で元ソースとの一致を確認できます。**
