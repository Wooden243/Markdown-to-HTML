# 03｜実行フロー — 具体的な値で追跡する

## 1. サーバー起動からブラウザ表示まで

ターミナルで `python server.py` を実行すると、Pythonは `main()` を呼びます。

1. `os.environ.get('HOST', '127.0.0.1')` と `os.environ.get('PORT', '8000')` で接続先を決める。
2. `ThreadingHTTPServer((host, port), AppHandler)` を作り、HTTPリクエストを待ち受ける。
3. ブラウザで `http://127.0.0.1:8000/` を開くと `GET /` を送信する。
4. `AppHandler.do_GET()` が `_serve_get()` を実行。`STATIC_FILES['/']` を参照して `public/index.html` を返す。
5. ブラウザは `styles.css` と `app.js` を追加でGETする。
6. JSの最後で `editorChanged(SAMPLE_MARKDOWN)` を実行し、最初のプレビュー生成を予約する。
7. `tryLoadMonaco()` がCDNのloader.jsを非同期読み込みし、成功すればエディタを高度化。失敗してもtextareaは維持される。

## 2. 最初の入力例

利用者がテキストを次に変更したとします。

```markdown
# 今日の予定

- **勉強**
- 散歩
```

### T0：inputイベント

`textarea.addEventListener('input', ...)` から `editorChanged(textarea.value)` が呼ばれます。Monaco読み込み成功時は `monacoEditor.onDidChangeModelContent(...)` が同じ役割を持ちます。

この時点での代表的な状態：

```js
currentMarkdown = '# 今日の予定\n\n- **勉強**\n- 散歩';
renderSequence = 5; // 以前の編集で4まで増えていた例
completedSequence = -1;
currentDocument = '';
// ダウンロードボタンは disabled = true
```

`refreshCounts(value)` により文字数・行数を更新し、既存タイマーは消去されます。

### T1：180ms経過

次のような処理が呼ばれます。

```js
renderMarkdown('# 今日の予定\n\n- **勉強**\n- 散歩', 5)
```

`AbortController` が作られ、`fetch` で次のリクエストを送信します。

```http
POST /api/convert HTTP/1.1
Content-Type: application/json

{"markdown":"# 今日の予定\n\n- **勉強**\n- 散歩"}
```

### T2：Pythonサーバーへ到着

`AppHandler.do_POST()` の処理順：

```text
URL /api/convert？ → YES
Content-Type application/json？ → YES
Content-Lengthあり？ → YES
本文80万バイト以下？ → YES
JSONとして読める？ → YES
markdownはstring？ → YES
20万文字以下？ → YES
```

ここで `data['markdown']` はPythonの `str` です。

### T3：HTML変換

`src/converter.py` の `PARSER.render()` がMarkdown構文をHTMLへ変換します。概ね次の断片が得られます。

```html
<h1>今日の予定</h1>
<ul>
<li><strong>勉強</strong></li>
<li>散歩</li>
</ul>
```

次に `bleach.clean()` でHTMLの許可タグやURLを検査します。上の見出し・リスト・strongは許可されるので残ります。

`make_html_document(fragment)` によりHTML5文書を構築。`<head>` にはUTF-8指定、表示領域のCSS、文書タイトルが入ります。これによりブラウザで単独表示できるHTMLになります。

### T4：レスポンスの返却

サーバーは次の構造のJSONを返します。

```json
{
  "html": "<h1>今日の予定</h1>\n<ul>...",
  "document": "<!doctype html>\n<html lang=..."
}
```

- `html`：HTML断片。主にAPIの確認・再利用用。
- `document`：CSSを含む単独HTMLファイル用。プレビューにも同じ文字列を使用します。

### T5：画面更新

`response.json()` でオブジェクトへ変換したあと、`sequence === renderSequence` を確認します。

```js
currentDocument = payload.document;
completedSequence = sequence;
htmlSource.textContent = payload.document;
previewFrame.srcdoc = payload.document;
downloadButton.disabled = false;
```

`iframe.srcdoc` がHTMLをフレーム内でレンダリングし、見出しと箇条書きを表示します。

## 3. ダウンロードボタンを押した場合

ユーザーがHTMLダウンロードを押すと `downloadHTML()` を実行します。

1. `currentDocument` が空でないか、`completedSequence` が最新かを確認。
2. `new Blob([currentDocument], {type:'text/html;charset=utf-8'})` を生成。
3. `URL.createObjectURL(file)` でBlob用の一時URLを生成。
4. `<a>` 要素を一時的に作成し、その `download` 属性に `.html` の名前を設定。
5. `.click()` を呼びブラウザへ保存を要求。
6. 1秒後に `URL.revokeObjectURL(objectURL)` で一時URLを解放。

ここでは**2回目のサーバー変換は行われません**。すでに受信済みの文書文字列を保存しています。したがってプレビューとダウンロード内容が一致しやすい設計です。

## 4. 連続入力（競合状態）

次のようなタイミングを考えます。

```text
0 ms: "# A"  入力 → sequence=1
180ms: AのPOST開始
240ms: "# AB" 入力 → sequence=2、Aの通信をabort
420ms: BのPOST開始
500ms: BのPOST応答 → sequence=2 と一致 → 採用
600ms: 仮にAの応答が遅れて届いても sequence=1 ≠ 2 → 破棄
```

**実際には通信の中断が成功すればAの応答は処理されません**。ただし中断タイミングに依存しないよう番号でも比較しています。

### 状態遷移表

| 状況 | `currentDocument` | `downloadButton.disabled` | status |
|---|---|---|---|
| 初期 | 空 | true | 変換中 |
| 変換成功 | 完成HTML | false | 変換完了 |
| 新しく入力 | 空へリセット | true | 変換中 |
| エラー | 空 | true | 変換エラー |
| ダウンロード | 変更なし | false | ダウンロード開始 |

## 5. 異常系例：Markdownが文字列でない

次をPOSTした場合：

```json
{"markdown": 123}
```

`isinstance(data.get('markdown'), str)` が false なので、HTTP 422 と `{"error":"markdown must be a string"}` を返します。変換関数には到達しません。UIから通常この型エラーは出ませんが、APIを直接使う利用者や誤った外部プログラムに対する防御となります。

## 6. 異常系例：危険なHTML

入力：

```markdown
<script>alert(1)</script>
```

この文字列はMarkdownItの `html=False` により通常のテキストとしてエスケープされます。

```html
<p>&lt;script&gt;alert(1)&lt;/script&gt;</p>
```

したがってプレビューでJavaScriptは実行されません。万が一変換ライブラリから想定外のHTMLが出ても、`bleach`による許可リストと `iframe` のsandboxが追加の対策となります。

## 7. DevToolsで実際に見る

1. ブラウザの開発者ツール `F12` を開く。
2. **Network** タブで `Fetch/XHR` に絞る。
3. Markdownを変更して `/api/convert` をクリック。
4. Headersで `Request Method: POST` と `Content-Type: application/json` を確認。
5. Payloadで `markdown` の文字列を見る。
6. Responseで `html` と `document` を確認。
7. **Elements** でiframeと `srcdoc` の変化を見る。

この一連を追えれば、「ブラウザが自動的に変換する」ではなく、**どこで何が実行されるか**を説明できます。
