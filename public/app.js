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
