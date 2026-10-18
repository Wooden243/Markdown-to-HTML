# ソース全文・逐次解説｜`src/converter.py`

> 元ファイルと全文一致するソーススナップショットです。変更した場合はこの教材も再生成してください。

## 1. ファイルの役割

- **役割**：MarkdownをHTML断片へ変換・安全化し、自己完結するHTML5ファイルの文字列を作る。
- **依存関係**：markdown_it.MarkdownIt、bleach、html.escape。HTTP層には依存しない。
- **入力・出力**：入力：Python str のMarkdown。出力：サニタイズ済みHTML断片またはCSS付きHTML文書（str）。
- **前提知識**：`learning/02_KEY_CONCEPTS.md` の関連節。

## 2. 元のソースコード全文

```python
"""Markdown conversion and safe standalone HTML export.

Markdown is rendered server-side and sanitized before being embedded in a
sandboxed preview or downloaded as a standalone HTML document.
"""
from __future__ import annotations

from html import escape

import bleach
from markdown_it import MarkdownIt

MAX_MARKDOWN_CHARS = 200_000

# In MarkdownIt, HTML is deliberately disabled so raw tags are text, not HTML.
PARSER = MarkdownIt('commonmark', {'html': False, 'linkify': False})
PARSER.enable(['table', 'strikethrough'])

ALLOWED_TAGS = frozenset({
    'a', 'blockquote', 'br', 'code', 'del', 'em', 'h1', 'h2', 'h3', 'h4',
    'h5', 'h6', 'hr', 'img', 'li', 'ol', 'p', 'pre', 's', 'strong',
    'table', 'tbody', 'td', 'th', 'thead', 'tr', 'ul',
})
ALLOWED_ATTRIBUTES = {
    'a': ['href', 'title'],
    'img': ['alt', 'src', 'title'],
    'code': ['class'],
}
# bleach constrains href/src URL schemes (data:, javascript:, etc. rejected).
ALLOWED_PROTOCOLS = ['https', 'http', 'mailto']

# Renderer stylesheet shared by preview and downloaded document. Keeping the
# CSS inline makes the export work without a running server or any CDNs.
DOCUMENT_CSS = """
:root { color-scheme: light; font-family: system-ui, -apple-system, 'Segoe UI', sans-serif; }
body { box-sizing: border-box; max-width: 820px; margin: 0 auto; padding: 28px 32px 80px;
       color: #263247; background: #fff; line-height: 1.75; overflow-wrap: anywhere; }
h1, h2, h3, h4 { margin-top: 1.55em; margin-bottom: .6em; line-height: 1.28; color: #192844; }
h1 { font-size: 2rem; padding-bottom: .4em; border-bottom: 1px solid #e2e7ef; }
h2 { font-size: 1.5rem; padding-bottom: .25em; border-bottom: 1px solid #e9edf3; }
p, li { margin: .65em 0; } a { color: #266cc5; } a:hover { text-decoration-thickness: 2px; }
pre { padding: 18px 20px; overflow: auto; color: #e6edf7; background: #1d283a;
      border-radius: 10px; font-size: .9em; line-height: 1.55; }
code { font-family: ui-monospace, SFMono-Regular, Consolas, monospace; }
:not(pre) > code { background: #f1f4f8; color: #a43f63; border-radius: 4px;
                     padding: 2px 5px; font-size: .9em; }
blockquote { margin: 1em 0; padding: 2px 18px; border-left: 4px solid #9bbcf2;
             background: #f4f8ff; color: #45546b; }
table { border-collapse: collapse; width: 100%; margin: 1.1em 0; display: block;
        overflow-x: auto; } th, td { border: 1px solid #d7deea; padding: 8px 12px; text-align: left; }
th { background: #f3f6fb; } tr:nth-child(even) { background: #fafbfe; }
img { max-width: 100%; height: auto; } hr { border: none; border-top: 1px solid #e3e8f0; }
@media (max-width: 600px) { body { padding: 18px; } h1 { font-size: 1.65rem; } }
""".strip()


def convert_markdown(markdown: str) -> str:
    """Convert Markdown to an allowlisted HTML fragment.

    Raises TypeError/ValueError for missing/wrong/oversized input.
    """
    if not isinstance(markdown, str):
        raise TypeError('markdown must be a string')
    if len(markdown) > MAX_MARKDOWN_CHARS:
        raise ValueError(f'markdown exceeds {MAX_MARKDOWN_CHARS} characters')
    rendered = PARSER.render(markdown)
    return bleach.clean(
        rendered,
        tags=ALLOWED_TAGS,
        attributes=ALLOWED_ATTRIBUTES,
        protocols=ALLOWED_PROTOCOLS,
        strip=True,
    )


def make_html_document(fragment: str, title: str = 'Converted Markdown') -> str:
    """Wrap a sanitized fragment as a self-contained, downloadable HTML file.

    Only call this with convert_markdown() output: the fragment is already
    sanitized. title is escaped even if supplied by an untrusted caller.
    """
    if not isinstance(fragment, str):
        raise TypeError('fragment must be a string')
    clean_title = escape(title, quote=True)
    return (
        '<!doctype html>\n'
        '<html lang="ja">\n<head>\n'
        '<meta charset="utf-8">\n'
        '<meta name="viewport" content="width=device-width, initial-scale=1">\n'
        f'<title>{clean_title}</title>\n'
        f'<style>\n{DOCUMENT_CSS}\n</style>\n'
        '</head>\n<body>\n'
        f'{fragment}\n'
        '</body>\n</html>\n'
    )
```

コード行数：95行。SHA-256：`11a125f60c6b6abe6e209921a471448db37f5d96d3da2ea1cfe66daa3d8f38ca`

## 3. 上から順に読む詳細解説

以下は上記ソースの先頭から末尾までを、意味がまとまる範囲で逐次説明したものです。

### 1. 役割・import・上限（1〜15行）

**該当箇所の冒頭**：`"""Markdown conversion and safe standalone HTML export.`

モジュールdocstringにセキュリティ方針を示す。`from __future__ import annotations` は型注釈の扱いを改善。`html.escape` はHTMLの特殊文字をエスケープ、`bleach` はHTMLサニタイズ、`MarkdownIt` はMarkdown構文解析。`MAX_MARKDOWN_CHARS` は20万文字を超える入力を拒否するための定数。

### 2. Markdownパーサー設定（16〜18行）

**該当箇所の冒頭**：`PARSER = MarkdownIt('commonmark', {'html': False, 'linkify': False})`

`MarkdownIt('commonmark',{'html':False,'linkify':False})` はCommonMarkを基礎として、生HTMLを無効化し、自動リンクの追加は行わない。`PARSER.enable(['table','strikethrough'])` は表・取り消し線を有効化。`MarkdownIt` はオブジェクトを返し、`.render(markdown)` でHTMLに変換する。CommonMark以外のGitHub独自拡張はすべて対応するわけではない。

### 3. 許可するタグ・属性・プロトコル（19〜33行）

**該当箇所の冒頭**：`ALLOWED_TAGS = frozenset({`

`frozenset` は変更しないタグ集合を表す。h1〜h6、p、blockquote、table、pre、code、aなどの表示に必要なタグのみを許す。`ALLOWED_ATTRIBUTES` でリンクのhref/title、画像のsrc/alt/title、コードのclassを許す。`ALLOWED_PROTOCOLS` はhttp/https/mailtoで、javascript:やdata:などを拒否する。リストを過度に緩めると危険な属性が出力に混入する。

### 4. HTMLファイルに埋め込むCSS（34〜56行）

**該当箇所の冒頭**：`DOCUMENT_CSS = """`

三重引用符で複数行CSSを1つのPython文字列定数として保持する。見出し、コードブロック、テーブル、画像、狭い画面用`@media`等を整える。これはプレビューとダウンロードしたHTMLで**同じ見た目**を再現するためのCSSで、アプリ外側の `public/styles.css` とは役割が異なる。`.strip()` で不要な前後改行を取り除く。

### 5. 入力検証→変換→サニタイズ（57〜75行）

**該当箇所の冒頭**：`def convert_markdown(markdown: str) -> str:`

`markdown: str` は文字列の型注釈、`-> str` は戻り値が文字列である宣言。`isinstance` で非文字列にTypeErrorを出す。`len` で文字数を確認し上限超過でValueError。`PARSER.render` がHTML断片を生成した後、`bleach.clean` で許可タグ・属性・プロトコルだけを通す。`strip=True` は許可外タグを取り除く指定。戻り値は安全化したHTML断片。入力が空なら空文字列を返す。

### 6. 独立HTMLファイルを生成（76〜95行）

**該当箇所の冒頭**：`def make_html_document(fragment: str, title: str = 'Converted Markdown') -> str:`

引数 `fragment` は**convert_markdown後の安全な断片**、`title` は既定では `Converted Markdown`。型検証後、`escape(title,quote=True)` でタイトルをエスケープする。`f-string` でHTMLの各パーツを連結し、doctype、lang、charset、viewport、title、style、bodyを含む全文を返す。`fragment` はすでに安全化済みであることが前提。生のユーザー入力を直接渡すと危険なので、呼び出し側は必ず `convert_markdown()` を通す。

## 4. 実行トレース

`convert_markdown('# Example')` → MarkdownItが `<h1>Example</h1>` へ変換 → Bleachが許可タグh1を検査しそのまま返す → `make_html_document('<h1>Example</h1>')` → `<!doctype html>`から始まるHTML5文書を返す。`<script>`を入力した場合はエスケープして文章として表示する。

## 5. 最重要ポイント

1. 変換とHTTPは別責務。
2. Markdown構文を自前の置換で再実装しない。
3. html=Falseにより生HTMLを無効にする。
4. タグと属性とURLスキームの許可リストを使う。
5. HTML断片とHTML文書は別のもの。
6. CSSを文書内に埋め込むと単独で開ける。
7. titleにはescapeが必要。

## 6. 自分で検証するには

詳細な起動手順は `README.md`、具体的な変数の流れは `learning/03_EXECUTION_FLOW.md`、デバッグは `learning/04_DEBUGGING.md` を参照。

**この教材のコード全文は、上記SHA-256値で元ソースとの一致を確認できます。**
