# claude-code-doctor

**Claude Code環境の健康診断スキル。** read-onlyの並列サブエージェントで設定・スキル・権限・自動化を全数診断し、影響度×工数マトリクス付きのレポートとHTMLダッシュボード、共有用カードを生成します。診断中は一切変更せず、修復はあなたの承認後に1個ずつ。

> A health checkup for your Claude Code setup, made by an actual doctor.
> Read-only parallel audit, impact-x-effort triage, one-page HTML dashboard, shareable cards. English docs below.

## なぜ作ったか

2年使い込んだ自分のClaude Code環境をClaude自身に監査させたら、**104件の指摘**が返ってきました。

- 常時ロード **45,000トークン**。毎セッション、仕事を始める前にコンテキストの22.5%が設定の読み込みで消えていた
- permissions許可リスト**804件**。うち77件はもう存在しないパスへの「死に許可」
- 常時注入されるMCPツール**63個**。機能が丸ごと重複するサーバーも
- 毎朝空振りし続けるcronと常駐監視が**12本**。誰も気づいていなかった

設定は資産のつもりで、半分は家賃でした。この監査の手順をそのままスキル化したのが本リポジトリです。

<p>
<img src="docs/examples/card2-numbers.png" width="49%" />
<img src="docs/examples/card3-lessons.png" width="49%" />
</p>

## 何をするか

| フェーズ | 内容 | 書き込み |
|---|---|---|
| 診断 | 10領域をread-only並列サブエージェントで全数スキャン | なし（レポート1本のみ許可制） |
| 統合 | 指摘を影響度×工数でマトリクス化・決定事項をOPTION形式で提示 | なし |
| 出力 | Markdownレポート＋HTMLダッシュボード＋共有カード（希望時） | 承認した場所のみ |
| 治療 | あなたの明示GO後に、止血項目を1個ずつ（バックアップ→実行→検証→報告） | 承認後のみ |

診断する10領域: ディレクトリ構造 / 開発リポ / CLAUDE.md階層 / rules・settings・permissions・hooks / スキル / コマンド / サブエージェント / MCP・プラグイン / 自動化・Git / 利用実態・ディスク。

## インストール

```bash
git clone https://github.com/kgraph57/claude-code-doctor.git
ln -s "$(pwd)/claude-code-doctor" ~/.claude/skills/claude-code-doctor
```

依存: HTMLダッシュボードは標準ライブラリのみ。共有カード生成のみ headless Chrome と Pillow が必要（任意機能）。

## 使い方

Claude Codeで:

```
read-onlyで私のClaude Code環境を監査して。承認前に変更禁止。
```

または `/doctor`。スキルが範囲と除外パス（個人情報など触ってほしくない場所）を先に確認してから走ります。

## 設計原則（Fable 5クラスのモデルを有効活用するために）

このスキル自体が、フロンティアモデル×マルチエージェントのベストプラクティス実装例になるよう書かれています。詳細は [docs/best-practices-fable5.md](docs/best-practices-fable5.md)。

1. **診断と治療を分離する** ── AIは提案まで、決めるのは人間。承認の言葉が曖昧なら止まる
2. **read-only並列ファンアウト** ── 網羅は安いモデルの並列で、判断は上位モデルの1本で
3. **構造化出力を強制する** ── findingsスキーマで受けるから、集計も可視化も機械的にできる
4. **成果物は「見せられる形」まで** ── レポートで終わらせず、検証済みダッシュボードとサニタイズ済み共有カードまで
5. **常時ロードは家賃** ── このスキル自身もprogressive disclosure（本文は薄く、詳細はreferences/）

## 安全性

- 診断フェーズは完全read-only（変更系コマンド禁止をプロンプトに焼き込み）
- ユーザー定義の立入禁止パス（読み取りも禁止）
- 秘密情報らしき値は引用せず、存在の指摘のみ
- 共有カードは実パス・実額・セキュリティ詳細を落とすサニタイズ規則＋自動パスマスク

## English

`claude-code-doctor` audits your Claude Code setup with read-only parallel subagents across 10 domains (CLAUDE.md token tax, dead permission entries, MCP tool overload, skill trigger collisions, subagent model leaks, zombie automations, and more). Findings are triaged on an impact-x-effort matrix, rendered as a one-page HTML dashboard, and optionally exported as sanitized share cards. No changes are made until you explicitly approve each fix.

Install: clone and symlink into `~/.claude/skills/`, then ask Claude Code to "audit my claude code setup, read-only". 

## License

MIT
