"""Optional browser smoke test. Requires playwright + installed Chromium."""
import os
from pathlib import Path
import subprocess
import sys
import time
from urllib.request import urlopen
from playwright.sync_api import sync_playwright
import json
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from src.converter import convert_markdown, make_html_document

ROOT = Path(__file__).resolve().parent.parent
PORT = '18765'
server = subprocess.Popen([sys.executable, 'server.py'], cwd=ROOT,
                          env={**os.environ, 'PORT': PORT}, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
try:
    for _ in range(40):
        try:
            with urlopen(f'http://127.0.0.1:{PORT}/api/health', timeout=.5) as req:
                if req.status == 200: break
        except Exception: time.sleep(.1)
    else: raise RuntimeError('server did not start')
    # Managed Chromium blocks loopback navigation in this environment.
    # Load local assets in about:blank and mock fetch for UI tests.
    # Real HTTP behavior is separately covered by test_server.py.
    def start_page(page):
        page.expose_function('__convertMarkdown', lambda value: {
            'html': convert_markdown(value['markdown']),
            'document': make_html_document(convert_markdown(value['markdown']))
        })
        page.set_content((ROOT / 'public/index.html').read_text())
        page.add_style_tag(content=(ROOT / 'public/styles.css').read_text())
        page.evaluate("""() => { window.fetch = async (_url, options) => {
            const payload = await window.__convertMarkdown(JSON.parse(options.body));
            return {ok:true, json:async()=>payload};
        }; }""")
        page.add_script_tag(content=(ROOT / 'public/app.js').read_text())
    with sync_playwright() as pw:
        browser = pw.chromium.launch(executable_path=os.environ.get('CHROMIUM_PATH', '/usr/bin/chromium'), headless=True, args=['--no-sandbox'])
        context = browser.new_context(viewport={'width': 1400, 'height': 1020}, accept_downloads=True)
        page = context.new_page()
        errors = []
        page.on('pageerror', lambda e: errors.append(str(e)))
        start_page(page)
        page.locator('#render-status').get_by_text('変換完了', exact=False).wait_for(timeout=10000)
        assert page.frame_locator('#preview-frame').locator('h1').inner_text() == 'Markdown Studio'
        page.screenshot(path=str(ROOT / 'docs' / 'screenshot-desktop.png'), full_page=True)

        page.get_by_role('button', name='HTML', exact=True).click()
        assert page.locator('#html-panel').is_visible()
        assert '<!doctype html>' in page.locator('#html-source').inner_text()
        page.get_by_role('button', name='Preview', exact=True).click()
        assert page.locator('#preview-frame').is_visible()

        # test textarea path (Monaco loads only if internet available)
        if not page.locator('#editor-frame').evaluate('(e) => e.classList.contains("monaco-ready")'):
            page.locator('#markdown-input').fill('# Browser Test\n\n**OK**')
        else:
            page.evaluate("window.monaco.editor.getModels()[0].setValue('# Browser Test\\n\\n**OK**')")
        page.locator('#render-status').get_by_text('変換完了', exact=False).wait_for(timeout=10000)
        assert page.frame_locator('#preview-frame').locator('h1').inner_text() == 'Browser Test'
        assert page.frame_locator('#preview-frame').locator('strong').inner_text() == 'OK'
        with page.expect_download() as transfer:
            page.get_by_role('button', name='HTMLをダウンロード').click()
        download = transfer.value
        assert download.suggested_filename.endswith('.html')
        filename = ROOT / 'docs' / '_browser-test-output.html'
        download.save_as(str(filename))
        assert '<h1>Browser Test</h1>' in filename.read_text()
        filename.unlink()

        page.get_by_role('button', name='クリア').click()
        page.locator('#render-status').get_by_text('変換完了', exact=False).wait_for(timeout=10000)
        assert page.frame_locator('#preview-frame').locator('h1').count() == 0
        page.locator('#file-input').set_input_files({'name': 'import.md', 'mimeType': 'text/markdown', 'buffer': b'# Imported'})
        page.locator('#render-status').get_by_text('変換完了', exact=False).wait_for(timeout=10000)
        assert page.frame_locator('#preview-frame').locator('h1').inner_text() == 'Imported'

        mobile = browser.new_context(viewport={'width': 390, 'height': 844}, is_mobile=True, has_touch=True)
        mpage = mobile.new_page()
        start_page(mpage)
        mpage.locator('#render-status').get_by_text('変換完了', exact=False).wait_for(timeout=10000)
        mpage.frame_locator('#preview-frame').locator('h1').wait_for(timeout=10000)
        mpage.locator('#preview-frame').scroll_into_view_if_needed()
        assert mpage.evaluate('document.documentElement.scrollWidth <= window.innerWidth + 1'), 'mobile horizontal overflow'
        assert not errors, f'Browser JS errors: {errors}'
        print('BROWSER PASS: initial render, preview/source toggle, editor, download, clear, file upload, mobile viewport, no JS errors')
        browser.close()
finally:
    server.terminate()
    server.wait(timeout=5)
