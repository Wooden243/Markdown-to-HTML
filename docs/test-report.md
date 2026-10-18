# 実行・テスト報告書

## テスト対象

プロジェクト名：Markdown to HTML。対象機能：Markdown編集、HTTPによる変換、HTMLプレビュー、HTMLコード表示とダウンロード、安全化、モバイル用レイアウト、READMEの再現性。

## 検証環境

- Python：3.13系列（コンテナ実行環境）
- Node.js：JavaScript構文検査のみ（サーバー実行には不要）
- Chromium：144系（PlaywrightのUI検証）
- OS：Linux（Windows＋WSL2での直接実行は未検証）
- Pythonライブラリ：`markdown-it-py`・`bleach`（ローカル環境に導入済みのパッケージ）

## 実施済み

| テスト | 実施方法 | 結果 |
|---|---|---|
| Markdownの見出し・太字・斜体・リスト・表・引用・コード・画像・リンク | `tests/test_converter.py` | PASS |
| XSSにつながる生HTML・JavaScriptリンク・data URLの無効化 | `tests/test_converter.py` | PASS |
| 日本語UTF-8・空入力・20万文字境界・型不一致 | `tests/test_converter.py` | PASS |
| 単独HTML（doctype / title / CSS埋込） | `tests/test_converter.py` | PASS |
| GET・HEAD・ヘルスチェック・静的ファイル配信・404 | `tests/test_server.py`（実HTTP通信） | PASS |
| JSON POST・Content-Type・サイズ上限・不正JSON・404/411/413/415/422 | `tests/test_server.py`（実HTTP通信） | PASS |
| HTTPヘッダー（CSP / nosniff / X-Frame-Options 等） | `tests/test_server.py` | PASS |
| 初期プレビューと編集後の見出し・太字表示 | `tests/browser_check.py`（Chromium、UI） | PASS |
| Preview / HTMLソース切替 | `tests/browser_check.py`（Chromium、UI） | PASS |
| ダウンロードされたHTMLの内容 | `tests/browser_check.py`（Chromium、UI） | PASS |
| クリア・サンプル・`.md` ファイル読込 | `tests/browser_check.py`（Chromium、UI） | PASS（サンプル動作は初期描画で確認） |
| モバイル幅のDOMと水平方向オーバーフロー検査 | `tests/browser_check.py`（Chromium、UI） | PASS |
| Python構文検証 | `python -m py_compile server.py src/converter.py` | PASS |
| JavaScript構文検証 | `node --check public/app.js` | PASS |

### 自動テスト件数

- `unittest`：**40件実施・40件成功**（`python -m unittest discover -s tests -p 'test_*.py' -q`）。
- 追加ブラウザUIスモークテスト：**1シナリオ実施・成功**。初期描画、編集、プレビュー/HTML切替、ダウンロード、クリア、ファイル読込、モバイル幅、JavaScriptエラーなしを確認。
- 詳細なコンソール出力はテストの再実行で再現可能。

## 重要な検証上の制約

1. **Playwrightブラウザ環境では、管理ポリシーにより localhost へのブラウザ直アクセスが制限**された。このためブラウザUIテストはローカルのHTML/CSS/JSをブラウザへ直接渡し、`fetch` をローカル関数のモックレスポンスに置換して実施した。**実HTTP通信は別途 `tests/test_server.py` で本物のHTTPサーバーに対して検証済み**。この2つを同一テストの成功としては扱わない。
2. **Monacoの外部CDNからのロード成功は未確認**。本実行環境は外部ネットワーク利用制限がある。テキストエリアのフォールバックで主要操作を検証した。
3. モバイルのDOMと画面横幅は確認したが、Chromeのこの環境では画面外のiframeプレビュー画像を正しく撮影できなかったため、**モバイルの視覚的な完成確認は未実施**。
4. ユーザーのWindows＋WSL2 Ubuntu環境でのインストールと起動、Dockerの実ビルド、外部Webホストでのデプロイ、独自サブドメインDNS、Recursionの採点は未検証。
5. ブラウザがダウンロードを開始し、生成ファイルの内容を確認した。各OSの保存ダイアログ表示などまでは保証しない。

## 再実行コマンド

```bash
python -m unittest discover -s tests -p 'test_*.py' -v
python -m py_compile server.py src/converter.py
node --check public/app.js
python tests/browser_check.py  # 任意、Playwright + Chromiumが必要
```

## ZIPと学習教材の整合性

- 配布用ZIPには `.venv/`、`__pycache__/`、秘密情報等を含めない。
- 逐次解説5ファイルは元ソースの全文を保存し、SHA-256で照合する。
- **ZIP展開後の再検証を実施し、40件の単体・HTTPテスト、Python/JavaScript構文検証がすべて成功**。逐次解説5ファイルのコード全文も元ソースとSHA-256で照合した。

**成功と記載しているのは実行した検証だけです。**
