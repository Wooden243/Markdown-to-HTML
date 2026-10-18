"""End-to-end HTTP tests against a real, ephemeral local HTTP server."""
from http.server import ThreadingHTTPServer
import http.client
import json
import threading
import unittest

from server import AppHandler, MAX_REQUEST_BYTES


class HttpServerTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.server = ThreadingHTTPServer(('127.0.0.1', 0), AppHandler)
        cls.thread = threading.Thread(target=cls.server.serve_forever, daemon=True)
        cls.thread.start()
        cls.port = cls.server.server_address[1]

    @classmethod
    def tearDownClass(cls):
        cls.server.shutdown()
        cls.server.server_close()
        cls.thread.join(timeout=3)

    def request(self, method, path, body=None, headers=None):
        connection = http.client.HTTPConnection('127.0.0.1', self.port, timeout=5)
        connection.request(method, path, body=body, headers=headers or {})
        response = connection.getresponse()
        data = response.read()
        result = (response.status, dict(response.getheaders()), data)
        connection.close()
        return result

    def convert(self, value, headers=None):
        return self.request('POST', '/api/convert', body=json.dumps(value, ensure_ascii=False).encode('utf-8'),
                            headers=headers or {'Content-Type': 'application/json'})

    def test_root_html(self):
        status, headers, body = self.request('GET', '/')
        self.assertEqual(status, 200)
        self.assertIn(b'Markdown to HTML', body)
        self.assertIn('text/html', headers['Content-Type'])

    def test_assets(self):
        for file in ('/styles.css', '/app.js', '/index.html'):
            with self.subTest(file=file):
                status, _, body = self.request('GET', file)
                self.assertEqual(status, 200)
                self.assertTrue(body)

    def test_health(self):
        status, _, body = self.request('GET', '/api/health')
        self.assertEqual(status, 200)
        self.assertEqual(json.loads(body), {'status': 'ok'})

    def test_head_request(self):
        status, headers, body = self.request('HEAD', '/')
        self.assertEqual(status, 200)
        self.assertFalse(body)
        self.assertGreater(int(headers['Content-Length']), 0)

    def test_not_found(self):
        status, _, _ = self.request('GET', '/nonexistent')
        self.assertEqual(status, 404)

    def test_path_traversal(self):
        status, _, body = self.request('GET', '/../../server.py')
        self.assertEqual(status, 404)
        self.assertNotIn(b'ThreadingHTTPServer', body)

    def test_conversion(self):
        status, headers, body = self.convert({'markdown': '# Hi\n\n**Bold**'})
        data = json.loads(body)
        self.assertEqual(status, 200)
        self.assertIn('<h1>Hi</h1>', data['html'])
        self.assertIn('<strong>Bold</strong>', data['html'])
        self.assertIn('<!doctype html>', data['document'])
        self.assertIn('nosniff', headers['X-Content-Type-Options'])

    def test_empty_markdown(self):
        status, _, body = self.convert({'markdown': ''})
        self.assertEqual(status, 200)
        self.assertEqual(json.loads(body)['html'], '')

    def test_unicode(self):
        status, _, body = self.convert({'markdown': '# 日本語'})
        self.assertEqual(status, 200)
        self.assertIn('日本語', json.loads(body)['document'])

    def test_no_raw_script(self):
        status, _, body = self.convert({'markdown': '<script>alert(1)</script>'})
        self.assertEqual(status, 200)
        self.assertNotIn('<script>', json.loads(body)['html'])

    def test_missing_markdown(self):
        status, _, body = self.convert({'text': 'no'})
        self.assertEqual(status, 422)
        self.assertIn('error', json.loads(body))

    def test_non_string(self):
        for bad in (False, None, 23, [], {}):
            with self.subTest(value=bad):
                status, _, _ = self.convert({'markdown': bad})
                self.assertEqual(status, 422)

    def test_bad_json(self):
        status, _, _ = self.request('POST', '/api/convert', b'{bad', {'Content-Type': 'application/json'})
        self.assertEqual(status, 400)

    def test_wrong_content_type(self):
        status, _, _ = self.request('POST', '/api/convert', b'hello', {'Content-Type': 'text/plain'})
        self.assertEqual(status, 415)

    def test_oversize_request(self):
        # Send only headers: the server must reject before reading the body.
        connection = http.client.HTTPConnection('127.0.0.1', self.port, timeout=5)
        connection.putrequest('POST', '/api/convert')
        connection.putheader('Content-Type', 'application/json')
        connection.putheader('Content-Length', str(MAX_REQUEST_BYTES + 1))
        connection.endheaders()
        response = connection.getresponse()
        self.assertEqual(response.status, 413)
        response.read()
        connection.close()

    def test_oversize_markdown(self):
        status, _, _ = self.convert({'markdown': 'a' * 200001})
        self.assertEqual(status, 413)

    def test_unknown_post_path(self):
        status, _, _ = self.request('POST', '/wrong', b'{}', {'Content-Type': 'application/json'})
        self.assertEqual(status, 404)

    def test_missing_content_length(self):
        connection = http.client.HTTPConnection('127.0.0.1', self.port, timeout=5)
        connection.putrequest('POST', '/api/convert')
        connection.putheader('Content-Type', 'application/json')
        connection.endheaders()
        resp = connection.getresponse()
        self.assertEqual(resp.status, 411)
        resp.read()
        connection.close()

    def test_csp_and_other_headers(self):
        status, headers, _ = self.request('GET', '/')
        self.assertEqual(status, 200)
        self.assertIn('Content-Security-Policy', headers)
        self.assertEqual(headers['X-Frame-Options'], 'DENY')
        self.assertEqual(headers['Cache-Control'], 'no-store')


if __name__ == '__main__':
    unittest.main()
