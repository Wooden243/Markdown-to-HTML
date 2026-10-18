# 公開（デプロイ）手順

## 「GitHubにpush」と「Webで公開する」は違う

- GitHubはソースコードを保存・共有するサービス。ソースをpushしただけではサーバープログラムは実行されない。
- 今回のWebアプリは Python プロセスを起動し、HTTPを受け付ける必要がある。そのため、Render/Railway/Fly.io/自分のVPS/Dockerを動かせるホスト等が必要。
- Reactや純静的HTMLだけのサイトと異なり、`POST /api/convert` を処理するバックエンドが必要。GitHub Pages単体への配置では動作しない。

## 方法A：Dockerを動かせるホスト（推奨）

ビルドとローカル確認：

```bash
docker build -t markdown-to-html .
docker run --rm -p 8000:8000 markdown-to-html
```

`http://127.0.0.1:8000/` を開き、フォームを操作する。Dockerfileでは `HOST=0.0.0.0` に設定されるため、コンテナ外からアクセスできる。

Dockerイメージをホスティングサービスにデプロイする場合は、ホスト側のドキュメントに従い、`PORT` を使用するように構成する。サービスが割り当てた環境変数 `PORT` を `server.py` が読み取る。

### 本番のための追加対応

- サーバー前段でTLS（HTTPS）とリバースプロキシを構成する。
- 不特定多数へ公開する場合はレート制限、同時実行数の上限、プロセス監視、ヘルスチェック、エラーログの収集が必要。
- CDN依存の Monaco Editor がブロックされても入力できるが、本番ではMonacoのファイルを自己ホストしてもよい（ライセンスを遵守）。
- 入力はサーバーメモリ上でのみ処理し、ファイルに保存しない。WebホストのHTTPアクセスログにも本文を含めない設計とする。
- `HTTPServer` はシンプルな開発・デモ用。大量アクセス対応や運用保守要件がある場合はWSGI/ASGIサービスへの移行を検討する。

## 方法B：Python実行対応PaaS

1. GitHubへこのリポジトリをpushする。
2. PythonまたはDockerのデプロイに対応したWebホスティングサービスで新しいWebサービスを作成する。
3. Python方式の場合はビルドコマンドに `pip install -r requirements.txt`、起動コマンドに `HOST=0.0.0.0 python server.py` を設定する。
4. ヘルスチェックを `/api/health` に設定し、応答 `{"status":"ok"}` を確認する。
5. ホストが発行した HTTPS URL にアクセスし、変換・プレビュー・ダウンロードまで動作確認する。

## `mdtohtml` のようなサブドメイン

Recursionの課題画面にある名称はホストの例であり、**本プロジェクトが勝手に取得・設定できるものではない**。独自ドメインを持っている場合、Webサービスの管理画面でサブドメインを追加し、DNSのCNAMEレコード等を設定する。ホスト指定のDNSターゲットとHTTPS証明書の発行を確認する。

## デプロイ確認リスト

- アプリが `GET /` でHTMLを返す
- `GET /api/health` が200を返す
- `POST /api/convert` が200でHTMLを返す
- Markdownの編集からプレビューが更新される
- `script` や `javascript:` リンクを含むMarkdownでコードが実行されない
- ダウンロードしたHTMLを単独のローカルファイルとして開ける
- HTTPSで動作し、ブラウザのConsoleに重大エラーがない
- 公開先URLとGitHubリポジトリURLを別々に控える

**納品時点ではクラウドへのデプロイ、DNS設定、TLS設定は行っていない。**
