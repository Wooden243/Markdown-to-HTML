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
