# ソースコード全文・逐次解説

このフォルダーは実際のソースファイルと1対1に対応し、各ファイルの **①役割／依存関係・②コード全文・③上から順の詳細な解説・④実行トレース・⑤最重要ポイント** を提供します。

| 学習順 | 解説 | 元のファイル | 主題 |
|---|---|---|---|
| 1 | [app.js.md](app.js.md) | `public/app.js` | イベント、fetch、非同期、表示更新、Blob |
| 2 | [server.py.md](server.py.md) | `server.py` | HTTP、バリデーション、JSON |
| 3 | [converter.py.md](converter.py.md) | `src/converter.py` | Markdownパーサー、サニタイズ、HTML文書 |
| 4 | [index.html.md](index.html.md) | `public/index.html` | DOM、フォーム、iframe、アクセシビリティ |
| 5 | [styles.css.md](styles.css.md) | `public/styles.css` | CSS Grid、レスポンシブ、Monaco表示切替 |

各解説には元ソースの全文を省略せず収録しています。元のファイルを変更すると解説内のコードと一致しなくなるため、変更後に教材側も更新してください。実装を読むときは**逐次解説の部分に沿って、IDEで元のファイルを確認する**のが効果的です。
