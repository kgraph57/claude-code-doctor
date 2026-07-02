> 🌐 **English README** → [README.md](README.md)

<div align="center">

<img src="docs/assets/banner.png" alt="Claude Code Doctor — Claude Code環境の健康診断" width="100%">

[English](README.md) | **日本語**

[![License: MIT](https://img.shields.io/badge/License-MIT-0B7DA3.svg)](LICENSE)
[![PRs Welcome](https://img.shields.io/badge/PRs-welcome-0B7DA3.svg)](https://github.com/kgraph57/claude-code-doctor/pulls)
[![Tests](https://github.com/kgraph57/claude-code-doctor/actions/workflows/test.yml/badge.svg)](https://github.com/kgraph57/claude-code-doctor/actions/workflows/test.yml)
[![Made with Claude Code](https://img.shields.io/badge/made%20with-Claude%20Code-E8801A.svg)](https://claude.com/claude-code)

<h3>2年使い込んだClaude Code環境を、Claude自身に監査させた。<br>返ってきた指摘は104件。</h3>

*Claude Code環境に潜む文脈税、死に権限、MCP肥大、ゾンビ自動化を見つける。*

現在のリリース: **v0.10.0** — Linux beta probe plan、60秒ウォークスルー生成、Windows beta probe plan、ハーネス横断チェックアップ、コミュニティ領域パック、CI予算ゲート、差分モードを含みます。詳細は [CHANGELOG.md](CHANGELOG.md)。

</div>

---

## 104件の健康診断

Claude Code Doctorは、AIワークスペース層のread-only健康診断です。コードそのものではなく、AIが1行目を書く前に読んでいる文脈、permissions、tools、skills、自動化、証拠記録を診ます。最初の患者は、2年使い込んだ自分のClaude Code環境でした。

| 項目 | 実測 |
|------|------|
| **毎セッション**最初に読み込まれる常時ロード | **45,000トークン**（コンテキストの22.5%が仕事の前に消える） |
| permissions許可リスト | **804件**、うち77件はもう存在しないパスへの「死に許可」 |
| 毎セッション注入されるMCPツール | **63個**、機能が丸ごと重複するサーバー込み |
| 毎朝空振りし続けていたゾンビ自動化 | **12本** |
| トリガー語が衝突するスキル | **70本**の中に複数クラスタ |
| ついでに見つかったディスク回収余地 | **約200GB** |

あなたの環境は違う数字のはずです。それこそがポイントで、見てみるまで分かりません。コードを診るツールはあります。このリポは、AIにとっての「普通」を作っている環境そのものを診ます。

## Claude Codeに貼る

初回はこのまま貼るのが安全です。

```text
Claude Code Doctorをread-onlyの環境監査として実行したいです。
先にスキャン範囲、立入禁止パス、レポート出力先を1つ確認してください。
私が承認するまで、ファイル、settings、git状態、自動化、permissions、秘密情報を変更しないでください。
その後、10領域の監査、Markdownレポート、HTMLダッシュボード、matrix-A/B形式の処方箋まで出してください。
```

短く言うなら:

```text
read-onlyで私のClaude Code環境を監査して。承認前に変更禁止。
```

または `/doctor`。

## 10秒デモ

自分の環境をスキャンせず、レンダラーだけ試せます。

```bash
python3 scripts/build_dashboard.py samples/dashboard.json /tmp/claude-code-doctor-dashboard.html
open /tmp/claude-code-doctor-dashboard.html
```

架空データからサニタイズ済み共有カードPNGも作れます。

```bash
python3 scripts/build_share_cards.py samples/share-cards.json /tmp/claude-code-doctor-cards/
open /tmp/claude-code-doctor-cards/
```

サンプルデータはすべて架空です。実レポートはローカルで生成され、外には出ません。

## 60秒ウォークスルー

短いナレーション台本とHTMLキャプチャ面を生成できます。

```bash
python3 scripts/build_walkthrough.py docs/generated-demo
open docs/generated-demo/demo-walkthrough.html
```

台本は [docs/walkthrough.md](docs/walkthrough.md) にもあります。

## 差分モード

健診の本命は、次の健診です。2つのエクスポート済みレポートを比較できます。

```bash
python3 scripts/compare_reports.py samples/diff-before.json samples/diff-after.json /tmp/claude-code-doctor-diff.md
open /tmp/claude-code-doctor-diff.md
```

差分レポートには、スコア差分、常時ロードtokenの増減、permission drift、MCP tool drift、解決/新規red flag、findingの移動、処方箋の進捗が出ます。

## CI予算ゲート

サニタイズ済みレポートがチーム予算を超えたらCIを落とせます。

```bash
python3 scripts/check_budgets.py samples/diff-before.json samples/budgets.json /tmp/claude-code-doctor-budget.md
open /tmp/claude-code-doctor-budget.md
```

常時ロードtoken、permission数、MCP tool数、critical finding数に上限を設定できます。詳細は [docs/ci-budget-gate.md](docs/ci-budget-gate.md)。

## コミュニティ領域パック

任意のread-onlyチェックパックを、使う前・PRする前に検証できます。

```bash
python3 scripts/validate_domain_pack.py domain-packs/security-team.md
python3 scripts/validate_domain_pack.py domain-packs/*.md
```

同梱パックはsecurity team、solo founder、teaching workshop、locked-down enterprise向けです。詳細は [docs/domain-packs.md](docs/domain-packs.md)。

## ハーネス横断チェックアップ

Claude Code、Codex、Cursor、OpenCode系workbench向けのadapter notesを検証できます。

```bash
python3 scripts/validate_adapter_notes.py docs/adapters/*.md
```

adapterは、context tax、permission drift、tool tax、automation drift、red flag、prescriptionという共通語彙で揃えます。詳細は [docs/cross-harness.md](docs/cross-harness.md)。

## Linux beta

Linux/WSLをスキャンする前に、review可能なread-only shell planを生成できます。

```bash
python3 scripts/build_linux_probe_plan.py /tmp/claude-code-doctor-linux.md
open /tmp/claude-code-doctor-linux.md
```

10領域を `find`、`du`、`crontab -l`、`systemctl --user list-timers`、`ss -ltnp` などの安全な読取probeへ対応させます。詳細は [docs/linux.md](docs/linux.md)。

## Windows beta

Windowsをスキャンする前に、review可能なread-only PowerShell planを生成できます。

```bash
python3 scripts/build_windows_probe_plan.py /tmp/claude-code-doctor-windows.md
open /tmp/claude-code-doctor-windows.md
```

10領域を `Get-ChildItem`、`Get-ScheduledTask`、`schtasks /Query` などの安全な読取probeへ対応させます。詳細は [docs/windows.md](docs/windows.md)。

## クイックスタート

```bash
git clone https://github.com/kgraph57/claude-code-doctor.git ~/.claude/skills/claude-code-doctor
```

この1行がやることは3つだけです: ①GitHubからこのツール一式をダウンロードし ②Claude Codeがスキルを探す決まったフォルダ（`~/.claude/skills/`）に置き ③以後、Claude Codeが自動で見つけて使えるようにします。あなたのファイルには何も起きません。

> 必要環境: 監査とMarkdownレポートは追加依存なし。HTMLダッシュボードはPython標準ライブラリのみ。共有カードPNG（任意機能）だけheadless Chrome/ChromiumとPillowが必要。
>
> **Linux**: beta coverageとしてread-only shell probe planを用意しています。詳細は [docs/linux.md](docs/linux.md)。領域9はlaunchdの代わりにcron/systemdタイマーを確認し、plutil系はmacOS限定です。**Windows**: beta coverageとしてread-only PowerShell probe planを用意しています。詳細は [docs/windows.md](docs/windows.md)。

## なぜスターするか

このリポを、agentic coding環境の標準安全レイヤーに育てたい人はスターしてください。

- **月次健康診断**: AIワークスペースを人間ドックのように繰り返し測る
- **差分モード**: 前回の健診と比べ、掃除の効果を数字で見る（v0.4.0で実装済み）
- **CI予算ゲート**: 常時ロード、permissions、tool taxが予算を超えたらPRを止める（v0.5.0で実装済み）
- **コミュニティ領域パック**: チーム、フレームワーク、OS、セキュリティ方針ごとのチェックを追加する（v0.6.0で実装済み）
- **横断チェックアップ**: Claude Code、Codex、Cursor、その他agent workbenchへ同じ診断思想を広げる（v0.7.0で実装済み）

今後の実装順は [docs/roadmap.md](docs/roadmap.md) にまとめています。

## なぜ作ったか

Claude Codeの環境は庭のように育ちます。足したスキル、承認した許可、試したMCPサーバーはすべて残り続け、誰も振り返りません。不健康な環境は、不健康なAIを育てます。設定で肥大化したAIは毎セッション重い体を引きずって起動し、動きが鈍り、変な行動をし始めます。あなたが今育てているのは未来の相棒です。太らせたままにしないでください。

<p align="center">
<img src="docs/assets/bloated-vs-fit.png" alt="設定のガラクタで肥満化して鈍くなったAIロボットと、健診を経て引き締まった同じロボット" width="82%">
</p>

## 仕組み

<img src="docs/assets/how-it-works.png" alt="診断が先、治療はGOの後。5ステップ: スコープ確認、read-only監査10体のファンアウト、構造化findings、影響度×工数トリアージ、承認ゲート" width="100%">

核心はひとつの分離です。**診断は完全read-only、治療はあなたが1個ずつ承認してから。** 網羅は安いモデルの並列で、判断は上位モデルの1本で、決定はあなたの手元に残ります。

## 何が得られるか

以下のスクリーンショットはすべて**架空のサンプルデータ**です。あなたのレポートはあなたのマシン上でローカル生成され、外には出ません。

**人間ドックのような健診結果表。** 領域ごとに0〜100点のスコアとA〜E判定（A=異常なし〜E=要治療）、10軸のレーダーチャート。共有向けには任意で人体マップモード（CLAUDE.md=脳、settings=心臓の臓器比喩）も使えますが、既定は素の領域名です。平文の鍵や個人ファイルのgit追跡のような危険な所見は、点数に関係なく判定を強制的に落とす**レッドフラグ**として明示されます。採点モデルは [`references/scoring.md`](references/scoring.md) に全文書化:

<img src="docs/examples/checkup.png" alt="サンプル健診結果: 総合判定C 55/100、10領域のレーダーチャート、レッドフラグ、領域別判定カード" width="100%">

**診断だけでなく、処方箋。** すべての修正はアクションカードになっています: リスク3段階（安全/要注意/手術）・所要時間・期待効果、そして**コピーしてClaude Codeに貼るだけの実行プロンプト**。バックアップと隔離の手順が焼き込まれているので、貼ればその1件だけが安全に実行されます。チェックはブラウザに保存され、レポートがそのまま進捗表になります:

<img src="docs/examples/prescriptions.png" alt="サンプル処方箋: フェーズ別のRXカード。1枚が開いておりコピー可能なプロンプトとリスク表示が見える" width="100%">

**1枚のHTMLダッシュボード**。数字サマリ、あなたにしか決められない決定事項（OPTION A/B形式）、影響度×工数マトリクス、段階的修復プラン、全指摘の折りたたみ表示（事実＋提案のペア）:

<img src="docs/examples/dashboard.png" alt="サンプルダッシュボード: 数字サマリと健診セクションの冒頭" width="100%">

**サニタイズ済み共有カード**（任意）。パスを漏らさずに診断結果を自慢できます。実パスの自動マスク付き:

<p align="center">
<img src="docs/examples/ja/card2-numbers.png" width="49%" alt="共有カード: 数字で見る設定の家賃">
<img src="docs/examples/ja/card3-lessons.png" width="49%" alt="共有カード: わかったこと">
</p>

## 何をチェックするか

10領域それぞれに明示的なチェックリストがあり、スキャン前に確認（拒否）できます。完全な定義は [`references/domains.md`](references/domains.md):

| # | 領域 | 見つけるものの例 |
|---|------|------------------|
| 1 | ディレクトリ構造 | ホーム直下に何年も置かれたファイル、死んだ隠しフォルダ、Desktop/Downloadsの滞留 |
| 2 | 開発リポジトリ | 野良リポ、肥大した.git、ネスト/循環クローン、CI不在 |
| 3 | CLAUDE.md階層 | 常時ロードのトークン税（数値で）、重複、日付付き記述の陳腐化 |
| 4 | settings・permissions | 死に許可、平文の資格情報、ガードレールの空白、スコープなしルール |
| 5 | スキル | トリガー語の衝突、誤発火しやすいdescription、肥大した単一ファイル |
| 6 | コマンド | スキルと分岐した二重管理、同名別機能 |
| 7 | サブエージェント | model未指定（静かなコスト漏れ）、レビュー役のWrite保持、休眠チーム |
| 8 | MCP・プラグイン | セッション毎のツール税、重複サーバー、ゴースト設定、死にポート |
| 9 | 自動化・Git | 消滅パスを参照するcron/launchdゾンビ、ローテなしログ、staleブランチ |
| 10 | 利用実態・ディスク | 旧パスのトランスクリプト遺物、スキル内のnode_modules、肥大セッション |

## 安全設計

- **プロンプト契約でread-only** ── 変更禁止を全サブエージェントに焼き込み。正直に言うと、これは指示レベルの契約であってOSのサンドボックスではありません。固い保証が要る場合はClaude Codeのpermission deny設定と併用してください。ガードが発火したら、このスキルは迂回せず停止します
- **立入禁止パス** ── 指定フォルダは読み取りもfind走査もしない
- **秘密情報は引用しない** ── パスと存在の指摘のみ
- **削除はしない** ── 修復はMANIFEST付き隔離。削除は後日
- **データは外に出ない** ── テレメトリなし・アップロードなし。共有カードはオプトインで、メール・APIキー形状・トークン・UUID・ユーザーパスを自動マスクし、**秘密らしき文字列が残った場合は生成自体を拒否**（フェイルクローズド）。それでもマスクはシートベルトであって保証ではないので、投稿前に一目確認を
- 修復中に権限ガードにブロックされたら、迂回せず停止して報告

## この健康診断の哲学

AIワークスペース健康診断は、掃除スクリプトではありません。安心してAIに任せるための臨床プロトコルです。AIが動く前に、隠れた文脈、permissions、tools、自動化、証拠記録を測ります。短く言えば、**先に診断し、同意の後にだけ治療し、すべてのfindingを点検可能にする**という考え方です。詳しくは [docs/ai-checkup-philosophy.ja.md](docs/ai-checkup-philosophy.ja.md)（[English](docs/ai-checkup-philosophy.md)）を参照してください。

## 焼き込まれた設計原則

このリポ自体が、Claude Codeでフロンティアモデルを使い倒すベストプラクティスの実装例です。**Claude Fable 5** と **Opus 4.8** で開発・実戦検証済みで、「Fable 5を使い始めたけどコンテキストがどこに消えているか分からない」人が最初に回すと効きます。詳細は [docs/best-practices.ja.md](docs/best-practices.ja.md)（[English](docs/best-practices.md)）:

1. 仕事の形を決めてからモデルを撃つ
2. read-only並列ファンアウト＋上位モデルでの統合
3. 構造化出力の強制
4. 診断と治療の分離（決めるのはユーザー）
5. 成果物は「見せられる形」まで。レンダリング検証してから完成と言う
6. 常時ロードは家賃。測ってから削る

## FAQ

<details>
<summary><b>マシンに変更を加えますか？</b></summary>
診断中は加えません。監査が書くのは、事前に承認された場所へのレポート1ファイルだけです。修復は1件ずつ明示承認の後、バックアップと隔離（削除ではなく）で進みます。
</details>

<details>
<summary><b>データはどこかに送られますか？</b></summary>
いいえ。すべてあなたのClaude Codeセッション内でローカルに動きます。共有カードはオプトイン機能で、集計値だけをサニタイズして出します。
</details>

<details>
<summary><b>監査自体のコストは？</b></summary>
最初の患者（2年物のヘビー環境・並列サブエージェント10体）で合計およそ100万トークンでした。API従量なら数ドル、サブスクリプションならセッション枠をそれなりに使います。コスト漏れを指摘するツールなので、自分の値札も開示しておきます。
</details>

<details>
<summary><b>会社の厳しい権限環境でも動きますか？</b></summary>
すべてローカルのClaude Codeセッション内で動き、このスキル自身は通信もテレメトリも追加しません。permission設定は尊重され、denyに阻まれた場合は迂回せず「そこにガードがある」ことを所見として報告します。
</details>

<details>
<summary><b>どれくらい時間がかかりますか？</b></summary>
最初の患者（2年物のヘビーな環境）は並列サブエージェント10体で約12分でした。逐次フォールバックはもう少しかかります。
</details>

## ロードマップ

- [x] 健康スコア（0〜100点）・A〜E判定・レーダーチャート・レッドフラグ ── 実装済み
- [x] 60秒ウォークスルー生成とcapture page ── 実装済み
- [x] 差分モード: 前回の健診との比較（健診の本命）── 実装済み
- [x] Linux path coverage beta: read-only shell probe plan ── 実装済み
- [x] Windows path coverage beta: read-only PowerShell probe plan ── 実装済み
- [x] CIモード: 常時ロード税が予算を超えたらPRを落とす ── 実装済み
- [x] コミュニティ製チェック項目パック（validated Markdown pack）── 実装済み

IssueもPRも歓迎です（日本語・英語どちらでも）。[CONTRIBUTING.md](CONTRIBUTING.md) 参照。

## 役に立ったら

トークンとお金と週末の掃除時間が浮いたら、⭐で次の人に教えてあげてください。総合判定を添えたissueは採点モデルの調整に役立ちます。

## ライセンス

[MIT](LICENSE) ── © 2026 [Ken Okamoto](https://github.com/kgraph57)（小児科医 × AI、東京）
