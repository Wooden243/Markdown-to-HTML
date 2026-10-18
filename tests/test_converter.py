"""Unit tests for Markdown parser, sanitizer, HTML generation."""
import unittest

from src.converter import (
    MAX_MARKDOWN_CHARS,
    convert_markdown,
    make_html_document,
)


class ConverterTests(unittest.TestCase):
    def test_header_and_paragraph(self):
        self.assertIn('<h1>Title</h1>', convert_markdown('# Title'))
        self.assertIn('<p>hello</p>', convert_markdown('hello'))

    def test_bold_and_italic(self):
        result = convert_markdown('**bold** and *italic*')
        self.assertIn('<strong>bold</strong>', result)
        self.assertIn('<em>italic</em>', result)

    def test_list(self):
        result = convert_markdown('- one\n- two')
        self.assertIn('<ul>', result)
        self.assertEqual(result.count('<li>'), 2)

    def test_table(self):
        result = convert_markdown('|a|b|\n|-|-|\n|1|2|')
        self.assertIn('<table>', result)
        self.assertIn('<td>2</td>', result)

    def test_blockquote(self):
        self.assertIn('<blockquote>', convert_markdown('> Quote'))

    def test_fenced_code(self):
        result = convert_markdown('```python\nprint(1)\n```')
        self.assertIn('<pre><code', result)
        self.assertIn('print(1)', result)

    def test_link(self):
        self.assertIn('href="https://example.com"', convert_markdown('[site](https://example.com)'))

    def test_markdown_image(self):
        self.assertIn('src="https://example.com/x.png"', convert_markdown('![x](https://example.com/x.png)'))

    def test_strikethrough(self):
        self.assertIn('<s>old</s>', convert_markdown('~~old~~'))

    def test_empty(self):
        self.assertEqual(convert_markdown(''), '')

    def test_utf8_japanese(self):
        self.assertIn('日本語', convert_markdown('# 日本語'))

    def test_raw_html_escaped(self):
        fragment = convert_markdown('<script>alert(1)</script>')
        self.assertNotIn('<script>', fragment)
        self.assertIn('&lt;script&gt;', fragment)

    def test_javascript_protocol_blocked(self):
        result = convert_markdown('[click](javascript:alert(1))')
        self.assertNotIn('href="javascript:', result)

    def test_data_protocol_blocked(self):
        result = convert_markdown('![unsafe](data:text/html,hello)')
        self.assertNotIn('src="data:', result)

    def test_html_event_handlers_blocked(self):
        result = convert_markdown('<img src="x" onerror="alert(1)">')
        self.assertNotIn('<img', result)
        self.assertIn('&lt;img', result)

    def test_url_encoded_script_blocked(self):
        result = convert_markdown('[x](javascript%3Aalert%281%29)')
        self.assertNotIn('href="javascript:', result)

    def test_wrong_type(self):
        with self.assertRaises(TypeError):
            convert_markdown(None)

    def test_limit(self):
        self.assertEqual(convert_markdown('a' * MAX_MARKDOWN_CHARS).count('a'), MAX_MARKDOWN_CHARS)
        with self.assertRaises(ValueError):
            convert_markdown('a' * (MAX_MARKDOWN_CHARS + 1))

    def test_full_document(self):
        html = make_html_document(convert_markdown('# Example'))
        for token in ('<!doctype html>', '<html lang="ja">', '<meta charset="utf-8">', '<style>', '<h1>Example</h1>', '</html>'):
            with self.subTest(token=token):
                self.assertIn(token, html)

    def test_title_escaped(self):
        doc = make_html_document('', '<script>')
        self.assertIn('&lt;script&gt;', doc)
        self.assertNotIn('<title><script>', doc)

    def test_html_is_standalone(self):
        doc = make_html_document('<h1>Test</h1>')
        self.assertNotIn('<link rel=', doc)
        self.assertNotIn('<script ', doc)


if __name__ == '__main__':
    unittest.main()
