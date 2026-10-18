# ソース全文・逐次解説｜`server.py`

> 元ファイルと全文一致するソーススナップショットです。変更した場合はこの教材も再生成してください。

## 1. ファイルの役割

- **役割**：Python標準HTTPサーバー。静的ファイル配信とMarkdown変換APIのHTTP境界を実装する。
- **依存関係**：src/converter.py、Python標準ライブラリ http.server/json/pathlib/os。
- **入力・出力**：入力：ブラウザのGET/HEAD/POSTリクエスト。出力：HTTPステータス、ヘッダー、HTML/JS/CSS/JSON本文。
- **前提知識**：`learning/02_KEY_CONCEPTS.md` の関連節。

## 2. 元のソースコード全文

```python
"""Dependency-light local HTTP server for the Markdown-to-HTML web app."""
from __future__ import annotations

from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
import json
import os
from pathlib import Path
from urllib.parse import urlsplit

from src.converter import MAX_MARKDOWN_CHARS, convert_markdown, make_html_document

ROOT = Path(__file__).resolve().parent
PUBLIC = ROOT / 'public'
MAX_REQUEST_BYTES = 800_000  # handles escaped / multibyte JSON without large uploads

STATIC_FILES = {
    '/': ('index.html', 'text/html; charset=utf-8'),
    '/index.html': ('index.html', 'text/html; charset=utf-8'),
    '/styles.css': ('styles.css', 'text/css; charset=utf-8'),
    '/app.js': ('app.js', 'application/javascript; charset=utf-8'),
}


class AppHandler(BaseHTTPRequestHandler):
    server_version = 'MarkdownToHTML/1.0'

    def _security_headers(self):
        self.send_header('X-Content-Type-Options', 'nosniff')
        self.send_header('Referrer-Policy', 'no-referrer')
        self.send_header('X-Frame-Options', 'DENY')
        self.send_header('Cache-Control', 'no-store')
        # Monaco loads only if CDN can be reached; plain textarea always works.
        self.send_header('Content-Security-Policy',
            "default-src 'self'; script-src 'self' https://cdn.jsdelivr.net 'unsafe-eval'; "
            "worker-src 'self' blob:; style-src 'self' 'unsafe-inline' https://cdn.jsdelivr.net; "
            "img-src 'self' data: https: http:; connect-src 'self'; frame-src 'self' blob:; "
            "font-src 'self' data: https://cdn.jsdelivr.net; object-src 'none'; "
            "base-uri 'none'; form-action 'self'; frame-ancestors 'none'")

    def _reply(self, status: int, body: bytes, content_type: str = 'application/json; charset=utf-8', head_only=False):
        self.send_response(status)
        self.send_header('Content-Type', content_type)
        self.send_header('Content-Length', str(len(body)))
        self._security_headers()
        self.end_headers()
        if not head_only:
            self.wfile.write(body)

    def _json(self, status: int, data: dict):
        payload = json.dumps(data, ensure_ascii=False).encode('utf-8')
        self._reply(status, payload)

    def do_HEAD(self):
        self._serve_get(head_only=True)

    def do_GET(self):
        self._serve_get(head_only=False)

    def _serve_get(self, head_only=False):
        path = urlsplit(self.path).path
        if path == '/api/health':
            payload = b'{"status":"ok"}'
            self._reply(200, payload, head_only=head_only)
            return
        resource = STATIC_FILES.get(path)
        if resource is None:
            self._reply(404, b'{"error":"Not found"}', head_only=head_only)
            return
        filename, content_type = resource
        self._reply(200, (PUBLIC / filename).read_bytes(), content_type, head_only=head_only)

    def do_POST(self):
        if urlsplit(self.path).path != '/api/convert':
            self._json(404, {'error': 'Not found'})
            return
        if self.headers.get('Content-Type', '').split(';', 1)[0].strip().lower() != 'application/json':
            self._json(415, {'error': 'Content-Type must be application/json'})
            return
        size = self.headers.get('Content-Length')
        if size is None or not size.isdecimal():
            self._json(411, {'error': 'Content-Length is required'})
            return
        length = int(size)
        if length > MAX_REQUEST_BYTES:
            self._json(413, {'error': 'Request exceeds maximum size'})
            return
        try:
            data = json.loads(self.rfile.read(length).decode('utf-8'))
        except (UnicodeDecodeError, json.JSONDecodeError):
            self._json(400, {'error': 'Invalid JSON'})
            return
        if not isinstance(data, dict) or not isinstance(data.get('markdown'), str):
            self._json(422, {'error': 'markdown must be a string'})
            return
        if len(data['markdown']) > MAX_MARKDOWN_CHARS:
            self._json(413, {'error': f'Markdown is limited to {MAX_MARKDOWN_CHARS} characters'})
            return
        try:
            fragment = convert_markdown(data['markdown'])
        except (TypeError, ValueError) as error:
            self._json(422, {'error': str(error)})
            return
        self._json(200, {
            'html': fragment,
            'document': make_html_document(fragment),
        })


def main():
    host = os.environ.get('HOST', '127.0.0.1')
    port = int(os.environ.get('PORT', '8000'))
    if not (1 <= port <= 65535):
        raise ValueError('PORT must be 1..65535')
    server = ThreadingHTTPServer((host, port), AppHandler)
    print(f'Markdown to HTML running at http://{host}:{port}/', flush=True)
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print('\nStopping server...', flush=True)
    finally:
        server.server_close()


if __name__ == '__main__':
    main()
```

コード行数：125行。SHA-256：`7c11d5089df265ca5f02021574aed6ca308486e3662ee6e9df9ff3f7fb146e98`

## 3. 上から順に読む詳細解説

以下は上記ソースの先頭から末尾までを、意味がまとまる範囲で逐次説明したものです。

### 1. ファイルの目的と標準ライブラリ（1〜11行）

**該当箇所の冒頭**：`"""Dependency-light local HTTP server for the Markdown-to-HTML web app."""`

ドキュメント文字列は役割を示す。`from __future__ import annotations` は型注釈の評価を遅らせ、`BaseHTTPRequestHandler`/`ThreadingHTTPServer` は標準HTTP機構。`json` はJSONとPython値の相互変換、`Path` はファイルパス操作、`urlsplit` はURLのクエリを分離する。外部ライブラリは変換モジュールだけが直接使う構成。

### 2. 公開ディレクトリとHTTPルートの定義（12〜23行）

**該当箇所の冒頭**：`ROOT = Path(__file__).resolve().parent`

`Path(__file__).resolve().parent` はこのファイルが存在するディレクトリを求める。作業ディレクトリが違っても静的ファイルを正しく参照できる。`PUBLIC` は配信対象、`MAX_REQUEST_BYTES` はメモリ占有抑制の上限、`STATIC_FILES` はURLからファイル名・Content-Typeへの固定表。任意パスを連結してファイルを配信しないため、ディレクトリトラバーサルを防ぎやすい。

### 3. HTTPハンドラーのクラス（24〜26行）

**該当箇所の冒頭**：`class AppHandler(BaseHTTPRequestHandler):`

`class AppHandler(BaseHTTPRequestHandler)` は継承。親クラスが受信したHTTPメソッドから`do_GET`や`do_POST`を呼び、子クラスでアプリ固有の処理を追加する。`server_version` はServerヘッダーに使われる。`self` はリクエストごとのハンドラーインスタンスを指す。

### 4. セキュリティに関連するレスポンスヘッダー（27〜39行）

**該当箇所の冒頭**：`def _security_headers(self):`

`self.send_header(name,value)` でHTTPヘッダーを構成する。`nosniff` はブラウザのMIME推測を抑え、`Referrer-Policy` は遷移先にURL情報を渡す範囲を狭める。CSPは実行を許すスクリプトやワーカーの配布元を制限する。MonacoのCDN互換性で `'unsafe-eval'` を例外的に許しており、本番では自己ホスト等の検討余地がある。`Cache-Control:no-store` は入力レスポンスのキャッシュ保存を抑える。

### 5. HTTPレスポンス共通の送信処理（40〜48行）

**該当箇所の冒頭**：`def _reply(self, status: int, body: bytes, content_type: str = 'application/json; charset=utf-8', he`

引数`status:int`はHTTPステータス、`body:bytes`は送るバイト列、`content_type`はMIME、`head_only` はHEAD時に本文を送らないためのフラグ。`send_response`→`send_header`→`end_headers`→`wfile.write` の順でHTTPメッセージを組み立てる。`Content-Length` はUTF-8変換後の `len(body)` を数えるのが正しい。戻り値はなし。

### 6. Python辞書をJSONレスポンスへ変換（49〜52行）

**該当箇所の冒頭**：`def _json(self, status: int, data: dict):`

`json.dumps(...,ensure_ascii=False)` は日本語をそのままJSON文字列として表し、`.encode('utf-8')` でバイト列にする。`self._reply` はHTTPと本文を送る共通関数なので、JSON送信の重複コードを避けられる。JSONが文字列であることとHTTP本文がbytesであることを区別する。

### 7. GETとHEADのルーティング（53〜58行）

**該当箇所の冒頭**：`def do_HEAD(self):`

HTTPメソッドと同じ名前のメソッドを定義する。`do_HEAD` はGET相当のヘッダーだけ、`do_GET` は本文も送る。両者は `_serve_get(head_only=...)` を共有することで誤差を防ぐ。HEADで本文を送るとプロトコルの期待と異なるため、フラグが必要。

### 8. 静的ファイルとヘルスチェック（59〜71行）

**該当箇所の冒頭**：`def _serve_get(self, head_only=False):`

`urlsplit(self.path).path` はクエリ文字列を除いたURLのパス。`/api/health` は運用時の稼働確認用。`STATIC_FILES.get(path)` にないURLは404にする。存在すれば対象の `public/` 内のファイルを `read_bytes()` で読み、定義したContent-Typeで返す。ユーザーが入力したファイルパスをそのまま読むことはない。

### 9. JSON入力の検証と変換API（72〜108行）

**該当箇所の冒頭**：`def do_POST(self):`

まずURLとContent-Typeを確認し、対象外やJSON以外は拒否する。`Content-Length` が数値か判定して最大80万バイトを超える場合は**読む前に**413。`self.rfile.read(length)` は指定バイト分だけリクエストボディを読む。UTF-8に変換して `json.loads` で辞書に戻し、型と文字数を確認。`convert_markdown` がHTML断片を返し、`make_html_document` が単体HTML文書を生成する。最後に `_json(200,{'html':..., 'document':...})` を返す。エラー処理は種類に応じ400/411/413/415/422を返す。

### 10. サーバー起動・環境変数・停止処理（109〜125行）

**該当箇所の冒頭**：`def main():`

`os.environ.get` で `HOST` と `PORT` を取得する。環境変数は起動時に設定する構成値で、APIキーなどの秘密をソースに埋めることを避ける際にも使われる。`int` はポート文字列を整数へ変換し、1〜65535で検証。`ThreadingHTTPServer` は複数接続をスレッドで扱う。`serve_forever()` は待受ループ、`KeyboardInterrupt` はCtrl+C、`finally` の `server_close()` はソケットの後片付け。`if __name__=='__main__'` により直接実行時だけ起動する。

## 4. 実行トレース

`POST /api/convert` に `{"markdown":"# Hello"}` が到着すると：`do_POST` → Content-Type確認 → Content-Length確認 → JSON解析 → 文字列検証 → `convert_markdown` → `make_html_document` → `_json(200,...)` → `_reply` → `self.wfile.write`。戻ると通信は終了し、ブラウザが本文を受け取る。

## 5. 最重要ポイント

1. GETは静的ページ取得、POSTはMarkdown変換。
2. 静的ファイルは公開を許可した4パスだけ配信。
3. HTTPリクエスト本文にはContent-Lengthとサイズの検証が必要。
4. json.loadsはJSONテキストをPythonの値へ変える。
5. HTTP statusを正しく区別すると不具合の切り分けが容易。
6. HTTP処理と変換処理を別モジュールにしてテストを分ける。
7. バインド先127.0.0.1はローカル限定、0.0.0.0は外部接続用。

## 6. 自分で検証するには

詳細な起動手順は `README.md`、具体的な変数の流れは `learning/03_EXECUTION_FLOW.md`、デバッグは `learning/04_DEBUGGING.md` を参照。

**この教材のコード全文は、上記SHA-256値で元ソースとの一致を確認できます。**
