# 02｜重要概念 — 使い方・理由・落とし穴

この章は**必須 → 重要 → 参考**の順に並べています。関数・構文は実際の実装ファイルに対応します。

## 1. HTTP・GETとPOST【必須】

**意味**：HTTPはブラウザ（クライアント）とWebサーバーがリクエストとレスポンスを交換する通信規約。GETは情報取得、POSTはサーバーへのデータ送信に一般的に使います。

**なぜ必要**：`GET /` は画面を表示し、`POST /api/convert` は入力Markdownを変換して返します。

```text
GET / HTTP/1.1
Host: 127.0.0.1:8000

HTTP/1.0 200 OK
Content-Type: text/html; charset=utf-8

<!doctype html>...
```

```text
POST /api/convert HTTP/1.1
Content-Type: application/json

{"markdown":"# Hello"}
```

**よくある間違い**：POSTすると必ずDBに保存される、という理解は誤り。今回はサーバーがデータを受け取ってその場でHTMLに変換するだけ。実務では推論API、検索API、画像変換APIにも同じ構造を使います。

## 2. JSONとシリアライズ【必須】

JSONはJavaScriptのオブジェクトに似たテキスト形式で、異なる言語間のデータ交換に使えます。

```js
JSON.stringify({markdown: '# Test'})  // '{"markdown":"# Test"}'
```

```python
json.loads('{"markdown":"# Test"}')  # {'markdown': '# Test'}
```

**使う場所**：ブラウザの `fetch` と、Python `AppHandler.do_POST()`。**よくある間違い**：文字列 `'{'` をPythonの辞書としてそのまま操作すること。`json.loads()` が必要です。逆方向は `json.dumps()`。

## 3. イベントとDOM【必須】

DOMはHTML要素をJavaScriptから操作するためのオブジェクトツリー。`addEventListener` はユーザーの操作をきっかけに関数を実行します。

```js
textarea.addEventListener('input', () => editorChanged(textarea.value));
```

**なぜ必要**：キー入力のたびにプレビューを再計算するため。`click` はボタン、`change` はファイル入力に使用。**よくある間違い**：`editorChanged()` を渡すのではなく読み込み時に実行してしまう、イベント引数と文字列を混同する、DOMのIDを誤ること。

## 4. `fetch` と `async`/`await`【必須】

```js
const response = await fetch('/api/convert', {
  method: 'POST',
  headers: {'Content-Type': 'application/json'},
  body: JSON.stringify({markdown}),
});
const payload = await response.json();
```

**意味**：`fetch` はHTTPリクエストを非同期に行うAPI。`await` はPromiseの完了を待って解決値を取り出す。`await` を使う関数には `async` を付ける。

**なぜ必要**：通信中もブラウザで文字入力ができるようにするため。**よくある間違い**：`fetch` の戻り値がいきなりJSONのオブジェクトだと思うこと、`response.ok` を確認せずHTTP 400/500を成功扱いすること。実務ではREST APIやLLM推論APIの呼び出しで頻繁に利用。

## 5. デバウンス（debounce）【必須】

キー入力が非常に速いと毎打鍵でPOSTし、不要な通信が増えます。最後の入力から180msだけ待って送信します。

```js
if (renderTimer !== null) clearTimeout(renderTimer);
renderTimer = setTimeout(() => renderMarkdown(value, sequence), 180);
```

**よくある間違い**：デバウンスだけで古いレスポンス対策も済むと考えること。すでに送られた前回のリクエストはまだ返ってくる可能性があります。`AbortController` とシーケンス番号も必要です。実務例は検索候補の表示、入力バリデーション、オートコンプリート。

## 6. HTMLのサニタイズとエスケープ【必須】

Markdown内にユーザーが `<script>` を書いた場合、そのままHTMLページへ埋め込むと悪意あるJavaScriptが実行される危険があります。

この課題は `MarkdownIt(html=False)` で生HTMLをテキスト化し、さらに `bleach.clean(..., strip=True)` で許可タグ・属性・URLに制限します。HTMLを表示するiframeには `sandbox=""` を付けます。

- エスケープ：`<` を `&lt;` のような文字参照として表示する。
- サニタイズ：許可されないタグ、属性、URLスキームを除去する。
- `textContent`：HTMLコードを文字列として表示する。
- `innerHTML`：HTMLを解析してDOMとして挿入する。信頼できない文字列を直接設定するのは危険。

**よくある間違い**：「HTMLを書き出せれば何でもよい」「`iframe`だけで安全」と考えること。ダウンロード後のHTMLを直接開く場合にはiframeの制約がないため、出力自体の安全化も必要です。

## 7. `Blob`、Object URL、download属性【必須】

```js
const blob = new Blob([currentDocument], {type: 'text/html;charset=utf-8'});
const url = URL.createObjectURL(blob);
const anchor = document.createElement('a');
anchor.href = url;
anchor.download = 'converted.html';
anchor.click();
URL.revokeObjectURL(url);
```

**意味**：Blobはブラウザ内でファイル相当のバイト列を表す。Object URLはそのBlobを指す一時URL。`download`は保存ファイル名を指定するHTML属性です。

**使う場所**：`public/app.js:downloadHTML`。**なぜ必要**：サーバーへ再度「ファイルを送れ」と要求せず、すでに受け取ったHTML文字列をブラウザ側で保存できる。**落とし穴**：`revokeObjectURL` をクリック前に呼ぶと保存できない場合があるので遅延実行する。

## 8. Markdownパーサー【重要】

Markdownは単なる置換ではなく、見出し、リスト、表、コードブロック、リンクなど階層構造と例外を持つ文法です。`
# Title` を `<h1>Title</h1>` にするだけなら簡単ですが、入れ子やコードブロック、エスケープ処理まで正しく作るのは難しいため、既存の `markdown-it-py` を使用しています。

Pythonファイル `src/converter.py` で `PARSER.render(markdown)` を実行。表は `table` を有効化、取り消し線は `strikethrough` を有効化します。**実務**でもよく使われる「実績あるパーサーに任せる」設計です。

## 9. iframeとsandbox【重要】

```html
<iframe id="preview-frame" sandbox="" title="変換結果のプレビュー"></iframe>
```

`srcdoc` はHTML文字列をフレーム内文書として表示します。`sandbox=""` はスクリプトの実行などを制約する設定です。出力結果が親ページのナビゲーションやDOMを勝手に変更しないよう分離します。

**よくある間違い**：`iframe.src = 'HTML全文'` とすること。URLではなくHTMLの文字列は `iframe.srcdoc` に渡します。

## 10. Monaco Editor とプログレッシブエンハンスメント【重要】

MonacoはVisual Studio Codeのエディタ基盤と関係のあるリッチテキストエディタです。CDNから読み込む場合、ネットワーク不調で読み込めないことがあります。そこで、初めから普通の `textarea` を使えるようにしておき、Monaco読み込みに成功したら見た目と編集機能を置き換えます。

**使う場所**：`tryLoadMonaco()` と CSS `.monaco-ready`。実務では「高度な機能が使えなくても中核機能は落とさない」設計をプログレッシブエンハンスメントと呼びます。

## 11. PythonのHTTPハンドラ【重要】

`BaseHTTPRequestHandler` はHTTPリクエストを受け、メソッドに応じて `do_GET()`・`do_POST()` 等を呼び分けます。`self.headers` でヘッダーを読み、`self.rfile.read(length)` でボディを読む。`self.wfile.write()` でレスポンスを返します。

**よくある間違い**：標準HTTPサーバーは本番負荷試験済みのフレームワークと同じだと考えること。今回の用途は学習用・小規模デモ用。実務ではReverse Proxy、WSGI/ASGI、レート制限なども検討します。

## 12. 入力検証とHTTPエラー【重要】

- 400：JSONの構文が正しくない。
- 411：本文の長さ（Content-Length）が送られていない。
- 413：リクエストまたはMarkdownが規定サイズを超えた。
- 415：Content-Typeが`application/json`でない。
- 422：JSONではあるが `markdown` の値が文字列でない。
- 404：存在しないURL。

**実務での意味**：何が間違っているかをHTTPステータスとレスポンス本文の両方で説明することで、利用者も開発者も問題を特定しやすくなります。

## 13. 仮想環境（venv）とrequirements.txt【重要】

`python3 -m venv .venv` でプロジェクト専用のライブラリ環境を作成し、`pip install -r requirements.txt` で再現します。LinuxやWSLのグローバルPythonへ直接ライブラリを大量に追加せずに済むのが利点。`.venv/` は巨大で環境依存するのでGitやZIPに入れません。

## 14. 単体・結合・ブラウザテスト【重要】

- 単体：`convert_markdown` を直接呼び、見出しや禁止プロトコル等の出力を確認。
- 結合：実際にローカルHTTPサーバーを立て、POSTして200/400/413等を確認。
- ブラウザ：キーボード編集→プレビュー→ダウンロードをUIから操作して検証。

3種類を組み合わせることで「変換関数だけ動くがフォームは動かない」といった見落としを減らします。

## 15. CSPとHTTPレスポンスヘッダー【参考】

`Content-Security-Policy` はブラウザが読み込めるスクリプトなどの出所を制限するHTTPヘッダーです。MonacoのCDN版との互換性のためscript-srcにCDNと `unsafe-eval` を許していますが、一般に `unsafe-eval` を許可しない方が攻撃面が小さくなります。本番ではCDNの自己ホスト等を検討できます。`X-Content-Type-Options: nosniff`、`Referrer-Policy: no-referrer` も付与しています。

## 16. 実務との接続【参考】

この構成をMarkdownから別の変換に置き換えると、CSVデータを分析してグラフを表示するアプリ、文章要約API、機械学習推論結果の表示などにも転用できます。入力→検証→変換→出力の境界が保たれているため、API処理の中身を交換しやすいのです。
