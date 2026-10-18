# 04｜デバッグ — 症状から原因を切り分ける

## 1. 画面が開かない / 接続が拒否される

### 確認

```bash
python server.py
curl -i http://127.0.0.1:8000/api/health
```

`{"status":"ok"}` が返ればHTTPサーバー自体は稼働中です。

### 主な原因

- サーバープロセスを起動していない。
- ポート8000が他のプログラムに使用されている。
- WSL環境で Windows 側ブラウザと通信するポートが異なる。
- `HOST`、`PORT` を変更したのに古いURLを開いている。

### 解決

`PORT=9000 python server.py` で別ポートを使い、`http://127.0.0.1:9000/` を開く。`curl -i` が成功すれば次はブラウザの開発者ツールを見る。

## 2. `ModuleNotFoundError: markdown_it` または `bleach`

仮想環境が有効かを確認：

```bash
which python
python -m pip show markdown-it-py bleach
```

失敗なら、プロジェクト内で：

```bash
python3 -m venv .venv
source .venv/bin/activate
python -m pip install -r requirements.txt
```

注意：pipに `markdown-it-py` と記載し、Pythonコードでは `from markdown_it import MarkdownIt` と読み込む。**配布パッケージ名とimport名が違うことがある**。

## 3. Monaco Editorにならずtextareaのまま

Monacoは外部CDNから読み込みます。回線不調、会社・大学ネットワークのフィルタ、CSP、ブラウザ拡張の影響で失敗することがあります。

1. `F12 → Network` で `loader.js` の通信が成功しているか確認。
2. `F12 → Console` でエラーを確認。
3. CDNを開けないネットワークなら通常textareaのまま操作できることを確認。
4. セキュリティ設定を無理に緩めず、Monaco自己ホストを検討。

**フォールバックの存在は不具合ではありません**。基本的なMarkdown変換はMonacoが使えなくても動きます。

## 4. プレビューが更新されない

調査順序：

1. ブラウザ下部のステータスが「変換中」「変換エラー」のどちらかを確認。
2. Networkの `/api/convert` が発行されているか確認。発行されていなければブラウザのイベント側。
3. 返ってきたHTTPステータスが200か確認。4xxならJSON本文の `error` を読む。
4. 200でもプレビューが違えば `renderMarkdown` の `sequence` と `currentDocument` を追う。
5. `iframe` の `srcdoc` を開発者ツールで確認。
6. `HTML` タブのソースも古い場合はAPI〜JS側。ソースは新しいがプレビューだけ違う場合はiframe/CSS側。

## 5. ダウンロードボタンが押せない

入力変更直後の「変換中」は、古いHTMLをダウンロードしないため意図的に無効化しています。

```js
currentDocument = '';
downloadButton.disabled = true;
```

`変換完了` まで待つ。エラー時には再試行としてテキストを編集。ダウンロード時にブラウザがポップアップや保存をブロックしていないかも確認する。

## 6. ファイルが読めない

- `.md`/`.txt` のテキストファイルか確認する。
- 上限20万文字を超えていないか確認する。
- `file.text()` はUTF-8等のテキストを読み込む想定。バイナリや文字コードが異なるファイルは文字化けする場合がある。
- ファイルをサーバーにアップロードしているのではなく、ブラウザ側で読み込んで編集欄へ表示している。

## 7. API 400/411/413/415/422

`curl` を使ってPOSTの正しい例を試す：

```bash
curl -i -X POST http://127.0.0.1:8000/api/convert \
  -H 'Content-Type: application/json' \
  -d '{"markdown":"# Hello"}'
```

- **400**：JSONの括弧・引用符が壊れていないか。
- **411**：Content-Lengthがあるか（通常curlが付ける）。
- **413**：サイズ上限を超えていないか。
- **415**：`Content-Type: application/json` か。
- **422**：`markdown` キーの値が文字列か。

## 8. Markdownの見た目が期待と違う

Markdown方言の違いが考えられます。例えばGitHub Flavored Markdownのすべてを再現するアプリではありません。テーブルと取り消し線には対応しますが、生HTML・数式・Mermaidは必須範囲から除外しました。必要な拡張を決めてからパーサー設定とテストを同時に変更します。

### HTML/CSSを調べる

- CSSが読めているか：Networkの`/styles.css`を確認。
- モバイルの縦並び：`@media(max-width:760px)`で`.editor-grid{display:block}`に切り替わる。
- Preview内の見た目：`src/converter.py:DOCUMENT_CSS` が埋め込まれるため、**アプリ本体のCSSとは別**。

## 9. テストで確認する

```bash
python -m unittest discover -s tests -p 'test_*.py' -v
python -m py_compile server.py src/converter.py
```

コードを変更したら、ブラウザ手動確認だけでなく必ずテストも再実行する。

## 10. 最小の調査手順（覚えるべき順）

1. **再現**：どんな操作で起きるか入力と手順を固定。
2. **観察**：Console、Network、エラー文、HTTPステータスを記録。
3. **切り分け**：ブラウザ側・HTTP通信・Python変換のどこか判断。
4. **仮説**：原因を1つ想定し、関連するコードを見つける。
5. **小さく修正**：無関係な機能まで変更しない。
6. **再テスト**：元のエラーが消え、既存テストも失敗しないか確認。

このサイクルを反復することがデバッグの基本です。
