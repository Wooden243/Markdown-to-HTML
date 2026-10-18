# 05｜理解度チェック — 問題と詳しい模範解答

## 問題

**Q1｜全体像**　Markdownがユーザーの入力からHTMLとしてプレビューされるまで、最低5段階で説明してください。

**Q2｜HTTP**　`GET /` と `POST /api/convert` の役割の違いは何ですか。

**Q3｜JSON**　`JSON.stringify({markdown: '# Test'})` は何を返しますか。Python側ではどの関数で辞書に戻しますか。

**Q4｜非同期**　`await fetch(...)` と `await response.json()` はそれぞれ何を待っていますか。

**Q5｜Markdown**　次を変換するとどのようなHTML要素が現れますか。

```markdown
# Title

- **A**
- B
```

**Q6｜セキュリティ**　`<script>alert(1)</script>` をそのまま `innerHTML` に設定してはいけないのはなぜですか。今回どの3層の対策を取っていますか。

**Q7｜競合**　古い変換結果が新しい入力の画面を上書きする問題を、`renderSequence` と `AbortController` の役割に分けて説明してください。

**Q8｜ダウンロード**　`Blob`、`URL.createObjectURL`、`a.download`、`URL.revokeObjectURL` はそれぞれ何をしていますか。

**Q9｜Monaco**　CDN接続がないときもMarkdownを入力できるのはなぜですか。

**Q10｜設計**　`src/converter.py` にHTTPヘッダーを書かず、`server.py` にMarkdownのHTMLルールを書かない理由を説明してください。

**Q11｜小規模改修**　プレビュー更新を180msではなく300msにしたい場合、どこを変更しますか。副作用はありますか。

**Q12｜小規模改修**　完成HTMLのタイトルを `My Document` に変更するにはどの関数のどの値を変更しますか。

**Q13｜デバッグ**　テキストを入力したのに Preview が変わらない場合、調査の優先順位を3ステップ書いてください。

**Q14｜HTTP入力検証**　`{"markdown": 5}` を送ると何番のステータスになり、何が理由ですか。

**Q15｜レスポンシブ**　CSSの`@media(max-width:760px)`は何を変えますか。

---

## 模範解答と解説

### A1

1. エディタのinputイベントが発生。
2. `editorChanged` が文字列を取得し、タイマーを予約。
3. `renderMarkdown` がJSONとして `POST /api/convert` を送信。
4. Pythonの `AppHandler.do_POST` がバリデーション後 `convert_markdown()` を実行。
5. `markdown-it-py` と `bleach` により安全なHTML断片を生成。
6. `make_html_document` がCSS付きHTML全文を生成し、JSONを返す。
7. ブラウザが `iframe.srcdoc` にHTML文書を設定する。

必要なのは**クライアントとサーバーの責務**を理解することです。

### A2

`GET /` は静的HTMLページを取得するためのリクエスト。`POST /api/convert` は入力Markdownをサーバーに渡して変換結果を受け取るためのリクエストです。どちらもHTTPを利用しますが、目的と処理内容が異なります。POSTだから必ず保存処理があるとは限りません。

### A3

JSON形式の**文字列** `'{"markdown":"# Test"}'` になります。Python側では `json.loads()` で辞書 `{'markdown': '# Test'}` に戻します。JavaScriptのオブジェクトとJSON文字列は別の型です。

### A4

`await fetch()` はリクエストが送信されレスポンスが得られるまでを待ちます。`await response.json()` はレスポンス本文を読み、JSONを解析してJavaScriptの値にするまで待ちます。ブラウザがフリーズするわけではなく、待ち時間中もイベント処理を進められます。

### A5

`h1`、`ul`、2つの`li`、1つの`strong` が主に現れます。マークアップ例：

```html
<h1>Title</h1>
<ul>
<li><strong>A</strong></li>
<li>B</li>
</ul>
```

Markdownの `#` は見出し、`-` は箇条書き、`**` は太字です。

### A6

`innerHTML` は文字列をHTMLとして解析するため、信頼できないスクリプトや属性が実行されるリスクがあります。今回の対策は (1) MarkdownIt `html=False`、(2) Bleachの許可リスト、(3) `iframe sandbox=""` です。HTMLソースタブは `textContent` を使います。ダウンロード版ではiframeの制約がないため、出力そのものを無害化することが特に重要です。

### A7

`AbortController` は通信中の古いリクエストを中止しようとします。`renderSequence` は入力が変わるたび増え、レスポンス時に一致するものだけを採用します。中断タイミングの競合があり得るため、**両方が必要**です。

### A8

`Blob` はHTML文字列をファイル相当のデータにし、`createObjectURL` はブラウザ内の一時URLを発行し、`a.download` は保存時の名前を指定し、`revokeObjectURL` は使い終えた一時URLを解放します。 `a.click()` で保存操作を開始します。

### A9

アプリは最初から普通のHTML `textarea` を持っており、入力イベントを登録しています。MonacoのCDN読込成功時だけ、その編集領域へ切り替えます。そのためネットワークがなくても主要機能が失われません。

### A10

責務分離のためです。`server.py` はHTTP層、`converter.py` は変換層です。変更が影響する範囲を小さくし、変換関数だけを単体テストでき、他のアプリやCLIからも再利用しやすくなります。

### A11

`public/app.js` 内の `setTimeout(() => renderMarkdown(value, sequence), 180)` を300に変更します。リクエスト数が減る可能性がありますが、プレビューが更新されるまでの待ち時間は長くなります。修正後にブラウザUIテストを実行してください。

### A12

`src/converter.py` の `make_html_document(fragment, title='Converted Markdown')` の既定引数を `'My Document'` に変更するか、`server.py` の呼び出し `make_html_document(fragment, title='My Document')` とします。UI側の見出しを変えてもダウンロード文書の `<title>` は変わりません。

### A13

(1) Networkで `/api/convert` が送られたか確認。(2) レスポンスHTTPステータスとJSONを確認。(3) 成功レスポンスがあるならブラウザ側の `renderSequence`、`currentDocument`、`iframe.srcdoc` を確認。前から順に追えば調査が速くなります。

### A14

HTTP 422 になります。JSON自体は正しくても `markdown` が文字列でなく数値なので、サーバーの型検証に失敗します。400はJSONそのものが壊れている場合です。

### A15

主に編集領域とプレビュー領域を横並びから縦並びへ切り替え、画面幅が狭くても操作できるようにします。同時にエディタの高さやツールバーの並びも調整します。CSSメディアクエリは画面サイズに合わせてスタイルを切り替える仕組みです。

## 追加演習（答えは直上の概念を応用）

1. `Ctrl + Enter` で手動変換するボタンを追加してみる。`editorChanged` 内の送信予約をどこまで再利用できるか設計。
2. フォントサイズ変更ボタンを追加する。`textarea` と `MonacoEditor.updateOptions` の違いを確認。
3. Markdownに画像リンクを含めたとき、プレビューとダウンロード版で画像の扱いがどう違うか検証。
4. `MAX_MARKDOWN_CHARS` を下げたとき、サーバーとクライアント双方の設定を揃える必要がある理由を考察。
5. `.md` の内容をブラウザ再読み込み後も復元したい場合、LocalStorage等の設計に何が必要か考える（この課題では未実装）。
