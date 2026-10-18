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
