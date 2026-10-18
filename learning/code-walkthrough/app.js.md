# ソース全文・逐次解説｜`public/app.js`

> 元ファイルと全文一致するソーススナップショットです。変更した場合はこの教材も再生成してください。

## 1. ファイルの役割

- **役割**：ブラウザ側の制御中枢。編集イベント・HTTP非同期通信・競合対策・DOM反映・HTMLのダウンロード・Monaco導入を担当する。
- **依存関係**：public/index.htmlの各id要素、src/converter.pyが生成しserver.pyが返すJSON、ブラウザのfetch/Blob/DOM API。
- **入力・出力**：入力：Markdown文字列とクリック/ファイル選択。出力：iframeのsrcdoc、HTMLソース表示、ダウンロード用Blob。
- **前提知識**：`learning/02_KEY_CONCEPTS.md` の関連節。

## 2. 元のソースコード全文

```javascript
'use strict';

// The original <textarea> is fully functional on its own. Monaco is optional
// progressive enhancement loaded from a CDN (online only).
const SAMPLE_MARKDOWN = `# Markdown Studio

Markdownを書いて、**右側でHTMLを確認**できます。

## できること

- **リアルタイム**でプレビュー
- HTMLソースの表示とコピー
- HTMLファイルをダウンロード

> 💡 Ctrl + S でも保存できます。

### コード

\`\`\`javascript
const message = 'Hello, Markdown!';
console.log(message);
\`\`\`

### 表

| 記法 | 表示 |
| --- | --- |
| \`**太字**\` | **太字** |
| \`*斜体*\` | *斜体* |

[Markdownの仕様](https://commonmark.org/) を確認する。
`;

const textarea = document.getElementById('markdown-input');
const editorFrame = document.getElementById('editor-frame');
const monacoContainer = document.getElementById('monaco-container');
const editorMode = document.getElementById('editor-mode');
const previewFrame = document.getElementById('preview-frame');
const htmlPanel = document.getElementById('html-panel');
const htmlSource = document.getElementById('html-source');
const status = document.getElementById('render-status');
const charCount = document.getElementById('character-count');
const lineCount = document.getElementById('line-count');
const unsavedDot = document.getElementById('unsaved-dot');
const downloadButton = document.getElementById('download-button');
const previewTab = document.getElementById('preview-tab');
const htmlTab = document.getElementById('html-tab');
const fileInput = document.getElementById('file-input');

let monacoEditor = null;
let currentMarkdown = SAMPLE_MARKDOWN;
let currentDocument = '';
let renderTimer = null;
let activeRequest = null;
let renderSequence = 0;
let completedSequence = -1;
let currentFileName = 'untitled.md';
const SIZE_LIMIT = 200_000;

function setStatus(message, isError = false) {
  status.textContent = message;
  status.style.color = isError ? '#bd5151' : '';
}
function refreshCounts(value) {
  charCount.textContent = `${value.length.toLocaleString('ja-JP')} 文字`;
  lineCount.textContent = `${value.length === 0 ? 0 : value.split('\n').length} 行`;
}
function editorChanged(value) {
  currentMarkdown = value;
  unsavedDot.hidden = false;
  refreshCounts(value);
  renderSequence += 1;
  completedSequence = -1;
  currentDocument = '';
  downloadButton.disabled = true;
  if (renderTimer !== null) clearTimeout(renderTimer);
  if (activeRequest) activeRequest.abort();
  if (value.length > SIZE_LIMIT) {
    setStatus(`入力は最大${SIZE_LIMIT.toLocaleString()}文字です`, true);
    return;
  }
  setStatus('変換中...');
  const sequence = renderSequence;
  renderTimer = setTimeout(() => void renderMarkdown(value, sequence), 180);
}
async function renderMarkdown(markdown, sequence) {
  const controller = new AbortController();
  activeRequest = controller;
  try {
    const response = await fetch('/api/convert', {
      method: 'POST',
      headers: {'Content-Type': 'application/json'},
      body: JSON.stringify({markdown}),
      signal: controller.signal,
    });
    const payload = await response.json();
    if (sequence !== renderSequence) return;
    if (!response.ok) throw new Error(payload.error || `HTTP ${response.status}`);
    currentDocument = payload.document;
    completedSequence = sequence;
    htmlSource.textContent = payload.document;
    previewFrame.srcdoc = payload.document;
    downloadButton.disabled = false;
    setStatus('変換完了 · 最新の内容');
  } catch (error) {
    if (error.name === 'AbortError' || sequence !== renderSequence) return;
    completedSequence = -1;
    currentDocument = '';
    downloadButton.disabled = true;
    setStatus(`変換エラー: ${error.message}`, true);
  } finally {
    if (activeRequest === controller) activeRequest = null;
  }
}
function replaceMarkdown(text, fileName = 'untitled.md') {
  currentFileName = fileName;
  document.querySelector('.file-name').textContent = fileName;
  if (monacoEditor) monacoEditor.setValue(text);
  else { textarea.value = text; editorChanged(text); }
  // setValue fires an onDidChangeModelContent event when Monaco is active.
  if (monacoEditor && currentMarkdown !== text) editorChanged(text);
}
function selectView(sourceView) {
  previewTab.classList.toggle('active', !sourceView);
  htmlTab.classList.toggle('active', sourceView);
  previewTab.setAttribute('aria-pressed', String(!sourceView));
  htmlTab.setAttribute('aria-pressed', String(sourceView));
  previewFrame.hidden = sourceView;
  htmlPanel.hidden = !sourceView;
}

textarea.value = currentMarkdown;
textarea.addEventListener('input', () => editorChanged(textarea.value));
textarea.addEventListener('keydown', (event) => {
  if (event.key === 'Tab') {
    event.preventDefault();
    const start = textarea.selectionStart;
    const end = textarea.selectionEnd;
    textarea.setRangeText('  ', start, end, 'end');
    editorChanged(textarea.value);
  }
});
document.getElementById('sample-button').addEventListener('click', () => replaceMarkdown(SAMPLE_MARKDOWN));
document.getElementById('clear-button').addEventListener('click', () => replaceMarkdown(''));
document.getElementById('upload-button').addEventListener('click', () => fileInput.click());
fileInput.addEventListener('change', async () => {
  const file = fileInput.files?.[0];
  if (!file) return;
  if (file.size > SIZE_LIMIT * 4) { setStatus('ファイルが大きすぎます', true); fileInput.value = ''; return; }
  try {
    const text = await file.text();
    if (text.length > SIZE_LIMIT) throw new Error('文字数の上限を超えています');
    replaceMarkdown(text, file.name);
  } catch (error) { setStatus(`読み込み失敗: ${error.message}`, true); }
  finally { fileInput.value = ''; }
});
previewTab.addEventListener('click', () => selectView(false));
htmlTab.addEventListener('click', () => selectView(true));
document.getElementById('copy-button').addEventListener('click', async () => {
  if (!currentDocument) return;
  try {
    await navigator.clipboard.writeText(currentDocument);
    setStatus('HTMLをコピーしました');
  } catch {
    setStatus('コピーできませんでした。HTTPSまたはlocalhostでお試しください。', true);
  }
});
function downloadHTML() {
  if (!currentDocument || completedSequence !== renderSequence) return;
  const file = new Blob([currentDocument], {type: 'text/html;charset=utf-8'});
  const objectURL = URL.createObjectURL(file);
  const anchor = document.createElement('a');
  anchor.href = objectURL;
  const safeBase = currentFileName.replace(/\.(md|markdown|txt)$/i, '').replace(/[^a-zA-Z0-9ぁ-んァ-ヶ一-龠_-]/g, '-').slice(0, 70) || 'converted';
  anchor.download = `${safeBase}.html`;
  document.body.append(anchor);
  anchor.click();
  anchor.remove();
  setTimeout(() => URL.revokeObjectURL(objectURL), 1000);
  setStatus('HTMLのダウンロードを開始しました');
}
downloadButton.addEventListener('click', downloadHTML);
window.addEventListener('keydown', (event) => {
  if ((event.ctrlKey || event.metaKey) && event.key.toLowerCase() === 's') {
    event.preventDefault();
    downloadHTML();
  }
});

// Progressive enhancement: CDN failure leaves the textarea visible and usable.
function tryLoadMonaco() {
  const script = document.createElement('script');
  const baseURL = 'https://cdn.jsdelivr.net/npm/monaco-editor@0.52.2/min/';
  script.src = `${baseURL}vs/loader.js`;
  script.async = true;
  script.onerror = () => { editorMode.textContent = 'テキストエディタ（オフライン）'; };
  script.onload = () => {
    if (typeof window.require !== 'function') return;
    const timeout = setTimeout(() => { editorMode.textContent = 'テキストエディタ（オフライン）'; }, 8000);
    try {
      window.MonacoEnvironment = {
        getWorkerUrl: () => {
          const proxy = `self.MonacoEnvironment={baseUrl:'${baseURL}'};importScripts('${baseURL}vs/base/worker/workerMain.js');`;
          return URL.createObjectURL(new Blob([proxy], {type:'text/javascript'}));
        },
      };
      window.require.config({paths: {vs: `${baseURL}vs`}});
      window.require(['vs/editor/editor.main'], () => {
        clearTimeout(timeout);
        if (monacoEditor) return;
        monacoEditor = window.monaco.editor.create(monacoContainer, {
          value: currentMarkdown,
          language: 'markdown',
          theme: 'vs-dark',
          minimap: {enabled: false},
          fontSize: 13,
          lineHeight: 22,
          wordWrap: 'on',
          automaticLayout: true,
          scrollBeyondLastLine: false,
          padding: {top: 18},
          ariaLabel: 'Markdownの編集',
        });
        monacoEditor.onDidChangeModelContent(() => editorChanged(monacoEditor.getValue()));
        editorFrame.classList.add('monaco-ready');
        editorMode.textContent = 'Monaco Editor';
      }, () => {
        clearTimeout(timeout);
        editorMode.textContent = 'テキストエディタ（オフライン）';
      });
    } catch {
      clearTimeout(timeout);
      editorMode.textContent = 'テキストエディタ（オフライン）';
    }
  };
  document.head.append(script);
}

refreshCounts(currentMarkdown);
editorChanged(currentMarkdown);
unsavedDot.hidden = true;
selectView(false);
tryLoadMonaco();
```

コード行数：243行。SHA-256：`32ccc8a0d647ad7218c1bc55ef528b9f88276b9de8d794b67694f96ff5761788`

## 3. 上から順に読む詳細解説

以下は上記ソースの先頭から末尾までを、意味がまとまる範囲で逐次説明したものです。

### 1. スクリプト先頭・サンプル定義（1〜33行）

**該当箇所の冒頭**：`'use strict';`

`'use strict'` は厳格モードを有効化して曖昧なJavaScript動作を抑制する。`SAMPLE_MARKDOWN` はテンプレートリテラル（バッククォート）なので、改行を含むMarkdownをそのまま記述できる。入力画面を初期表示するための定数で、利用者が書き換える可変状態ではない。`const`を削除するとサンプルボタン・初回表示が参照する値がなくなる。実務ではデモデータを別ファイル化する代替もあるが、この規模では一つの定数で十分。

### 2. DOM要素の取得と共有（34〜49行）

**該当箇所の冒頭**：`const textarea = document.getElementById('markdown-input');`

`document.getElementById('markdown-input')` はHTMLのidから1要素を参照する。ここで取得するボタンやiframeはイベント処理内で繰り返し使うため `const` へ保持する。`document` はブラウザが提供するオブジェクト、戻り値はDOM要素（存在しないidならnull）。`index.html` のid変更時にJSも更新しなければ `null.addEventListener` 等のエラーとなる。HTMLとJSのインターフェースとしてIDを扱うのが重要。

### 3. アプリの状態変数（50〜59行）

**該当箇所の冒頭**：`let monacoEditor = null;`

`let` は後から再代入する変数。`monacoEditor=null` はまだMonacoを起動していない意味、`currentMarkdown` は最新入力、`currentDocument` は最後に確定したHTML、`activeRequest` は中断可能な通信、`renderSequence` は入力世代、`completedSequence` は成功済み世代。`SIZE_LIMIT` はクライアント側の文字数上限。状態が複数あるのは「編集中の入力」と「正しく変換済みの出力」を区別するため。全てを1変数で表すと旧データのダウンロードや古い表示が起こる。

### 4. ステータスメッセージの反映（60〜63行）

**該当箇所の冒頭**：`function setStatus(message, isError = false) {`

`setStatus(message, isError=false)` は画面下の文章とエラー用色を変更するヘルパー。`status.textContent=message` は引数をHTMLとして解析せず文字列で表示するため、安全にエラー文字列を示せる。戻り値は明示しないので `undefined`。第二引数は省略するとfalse。`innerHTML` へ変更すると、エラー文にタグが混入したとき危険。

### 5. 文字数と行数の計算（64〜67行）

**該当箇所の冒頭**：`function refreshCounts(value) {`

`value.length` はJavaScript文字列のUTF-16コード単位数で、サーバーPythonのUnicode文字数とは絵文字などで一致しない場合がある。`split('\n').length` は改行を境に行を数える。空文字列だけ0行扱いとしている。`toLocaleString('ja-JP')` は桁区切りの見た目を調整。カウントは表示補助で、厳密な上限判定はサーバー側でも別途行われる。

### 6. 入力変更・デバウンス・古い通信の停止（68〜85行）

**該当箇所の冒頭**：`function editorChanged(value) {`

引数 `value` は新しいMarkdown文字列。`renderSequence+=1` によって新しい入力世代を発行し、`completedSequence=-1` で以前の成功状態を解除する。`currentDocument=''` と `downloadButton.disabled=true` は古いHTMLの誤保存を防ぐ。`clearTimeout` は以前予約した未実行の変換をキャンセルする。`activeRequest.abort()` は通信中断を試みる。長さ超過なら再通信しない。最後の `setTimeout(...,180)` は180msのデバウンス。戻り値はない（副作用として画面状態とタイマーを変更する）。このブロックを消すと文字入力でプレビューが更新されなくなる。

### 7. API送信・レスポンス・成功と失敗の処理（86〜114行）

**該当箇所の冒頭**：`async function renderMarkdown(markdown, sequence) {`

`async` は関数内で `await` を使えるようにし、関数の戻り値はPromiseになる。`fetch` の `method:'POST'`、`Content-Type:'application/json'`、`JSON.stringify({markdown})` によりPythonが読める形式で送る。`AbortController.signal` は中止要求を通信に渡す。`response.json()` はレスポンス本文を解析する非同期処理。`sequence!==renderSequence` の場合は結果を無視する。HTTP 4xxは`fetch`自体の例外とは限らないため`response.ok`も確認する。成功時 `currentDocument`、`htmlSource.textContent`、`previewFrame.srcdoc` を同時に更新。例外時は古いデータを無効化し、`finally` で当該コントローラだけ掃除する。`return` は条件に応じて処理を終える。主な引数はMarkdown文字列と世代番号、直接の返却値ではなくUI更新が目的。

### 8. サンプル・クリア・読み込みの共通処理（115〜122行）

**該当箇所の冒頭**：`function replaceMarkdown(text, fileName = 'untitled.md') {`

`text` は上書きするMarkdown、`fileName='untitled.md'` は省略可能なファイル名。ファイル名を `.textContent` で表示するのでHTMLファイル名が表示上のタグにならない。Monacoがある場合は `setValue` により変更イベントが発生する。ない場合はtextareaに値を入れて `editorChanged` を明示的に呼ぶ。入力ソースごとに別の処理を作らず、この関数を再利用している。

### 9. PreviewとHTMLソースの切り替え（123〜131行）

**該当箇所の冒頭**：`function selectView(sourceView) {`

引数 `sourceView` は真偽値。trueならHTMLのソース、falseならプレビュー。`classList.toggle('active',bool)` はクラスを追加/削除し、`aria-pressed` は支援技術向けにボタンの状態を知らせる。`hidden` プロパティは対象要素を非表示にする。ここではサーバー通信は行わず、既存のDOM表示を切り替えるだけ。戻り値なし。

### 10. textareaと各ボタンへのイベント登録（132〜167行）

**該当箇所の冒頭**：`textarea.value = currentMarkdown;`

読み込み直後にtextareaへサンプルを設定し、`input` で `editorChanged` を呼ぶ。`keydown` はTabを2スペースへ変えるため `preventDefault()` で既定動作を抑止し、選択範囲を `setRangeText` で置換。サンプル/クリアは `replaceMarkdown` を呼び出す。アップロードは `file.text()` でブラウザ内のファイル内容を読み、20万文字以内であればセットする。`fileInput.value=''` は同じファイルを再度選択できるようにする。`change`、`click`、`keydown` のイベントの違いを意識する。

### 11. 完成したHTMLからファイルを保存（168〜190行）

**該当箇所の冒頭**：`function downloadHTML() {`

`completedSequence !== renderSequence` のときは未確定なので保存を拒否する。`new Blob([currentDocument], {type:'text/html;charset=utf-8'})` はHTML文字列のバイナリ表現を作り、`URL.createObjectURL` は一時URLを返す。`document.createElement('a')` に `download` 属性を付け、プログラムで `.click()` を実行して保存開始を要求する。ファイル名は置換と文字種制限を入れている。最後の `URL.revokeObjectURL` はリソース解放だが、ダウンロードが始まる前に解放しないよう1秒待つ。ファイルが確実に保存されたことまでは検出していない。`Ctrl/Cmd+S` は既定のブラウザ保存を抑止して同関数を呼ぶ。

### 12. Monaco Editorの遅延初期化とフォールバック（191〜238行）

**該当箇所の冒頭**：`function tryLoadMonaco() {`

ブラウザの `script` 要素を動的生成し、jsDelivrのMonaco loaderを非同期で取得する。`script.onerror` は読み込み失敗時にtextareaを残す。`window.require.config` に Monacoのモジュールパスを指定、`require(['vs/editor/editor.main'], success, failure)` でメインモジュールを読み込む。`MonacoEnvironment.getWorkerUrl` はWorkerスクリプトのURLを生成する。`monaco.editor.create` はエディタインスタンスを返し、`language:'markdown'` や `theme:'vs-dark'` 等で設定する。`onDidChangeModelContent` に変更イベントを接続してから `.monaco-ready` を追加しtextareaを隠す。CDNが使えない状態を正常なフォールバックとみなす。

### 13. 初期化の実行順序（239〜243行）

**該当箇所の冒頭**：`refreshCounts(currentMarkdown);`

最後に文字数表示を更新し、初回変換を予約、編集済みの印は隠し、Previewタブを選び、Monaco読込を開始する。この順序で初回表示直後も動作する。`tryLoadMonaco()` を他処理より先にすると、外部ネット接続状況によって初回表示に影響しやすくなる。各処理はDOMContentLoaded後に `defer` で実行されることが前提。

## 4. 実行トレース

### 例：`# Memo` を入力した場合
1. `textarea.value = "# Memo"` → `editorChanged('# Memo')` が呼ばれる。
2. `renderSequence` が1増える。`currentDocument=''` にして保存を一時無効化。
3. 180ms後、`renderMarkdown('# Memo', sequence)` が実行される。
4. `fetch` が `{markdown:'# Memo'}` をJSONで送る。受信時に `sequence` が最新か確認。
5. `currentDocument` に完成HTML文字列が入り、`previewFrame.srcdoc` に代入される。
6. 保存ボタン押下でBlobを作成、`untitled.html` という名前でダウンロードが始まる。

### 頻繁な編集の例
`# A` の応答待ちに `# AB` が入力された場合、前のAbortControllerで通信を中断し、さらに `renderSequence` で古い応答を排除する。古いHTMLを保存できないよう `completedSequence=-1` を代入する。

## 5. 最重要ポイント

1. ブラウザは文字列を変換しない。変換APIを呼び出す。
2. inputイベントがすべての更新の入口。
3. 非同期のfetchとPromiseを理解する。
4. デバウンス・中断・世代番号は別の役割。
5. srcdocはHTMLを表示し、textContentはソースを文字列として示す。
6. ダウンロードはBlobで実施し再通信しない。
7. Monacoは必須でなく機能拡張として扱う。
8. 変換失敗中には古い文書をダウンロードしない。

## 6. 自分で検証するには

詳細な起動手順は `README.md`、具体的な変数の流れは `learning/03_EXECUTION_FLOW.md`、デバッグは `learning/04_DEBUGGING.md` を参照。

**この教材のコード全文は、上記SHA-256値で元ソースとの一致を確認できます。**
