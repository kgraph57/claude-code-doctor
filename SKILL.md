---
name: claude-code-doctor
description: >
  Claude Code環境の健康診断（セットアップ監査）。read-onlyの並列サブエージェントで
  CLAUDE.md / rules / skills / agents / hooks / permissions / MCP / 自動化 / Git を全数診断し、
  影響度×工数マトリクス付きレポートとHTMLダッシュボード、共有用サニタイズカードを生成する。
  診断中は一切変更せず、ユーザーの明示承認を得てから修復に入る。
  トリガー: '/doctor', '環境監査', 'セットアップ監査', 'Claude Code健康診断', '設定を診断して',
  'audit my claude code setup', 'setup audit', 'claude code doctor', 'health check my setup'
---

# claude-code-doctor

Claude Code環境の健康診断。診断（read-only）と治療（承認後）を分離するのが本体思想。

## 鉄則（すべてに優先する）

1. **診断フェーズは完全read-only**。Write / Edit / mkdir / mv / rm / git変更系を使わない。
   使ってよいのは ls / find / du / wc / head / grep / cat / stat / plutil -p /
   git status / git log / git ls-files などの読み取りと、Read / Grep / Glob ツールのみ。
2. **決めるのはユーザー**。診断結果は「事実＋提案」で出し、修復は明示的なGOを待つ。
   「たぶん良い」「かもしれない」は承認ではない。
3. **立入禁止パスを最初に確認する**。ユーザーが指定した除外パス（個人情報・患者情報・
   秘密領域）は読み取りも含めて触れない。findには必ず除外を入れる。
4. **秘密情報は引用しない**。APIキーやトークンらしき文字列を見つけても、
   パスと存在の指摘のみで値は書かない。

## Step 0: スコープ確認

診断開始前にユーザーへ確認する（AskUserQuestionがあれば使う）:

- スキャン範囲: `~/` 全体か、`~/.claude` ＋ 開発ディレクトリのみか
- 除外パス: 触れてはいけないディレクトリ（デフォルト提案: 個人情報・鍵・患者データ系）
- レポート出力先: 1ファイルだけ書き込み許可をもらう（それ以外は変更禁止のまま）

## Step 1: 偵察（メインループ・1〜2分）

ファンアウト前に全体サイズを掴む:

```bash
ls -la ~/.claude/ && ls ~/.claude/skills | wc -l && ls ~/.claude/agents | wc -l
wc -c ~/.claude/settings.json ~/.claude/CLAUDE.md 2>/dev/null
ls ~/Library/LaunchAgents/ 2>/dev/null | head -30   # macOSのみ
crontab -l 2>/dev/null | head -10
```

ここで得た件数・サイズを各領域プロンプトに埋め込む（エージェントの迷いが減る）。

## Step 2: 並列ファンアウト（10領域）

`references/domains.md` の領域定義を使い、read-onlyサブエージェントを並列起動する。
Workflowツールがあれば `parallel()` で、なければAgentツールを1メッセージ内で複数起動。

- 各エージェントに **共通禁止事項ブロック**（domains.md冒頭）を必ず前置する
- 構造化出力（`references/report-format.md` のfindingsスキーマ）を強制する
- モデル振り分け: スキャン系は下位モデル（例: haiku/sonnet）を明示指定。
  統合・判断はメインループ（上位モデル）が担う。デフォルト継承で全部
  最上位モデルにしない（それ自体がこの監査の頻出指摘）

## Step 3: 統合（メインループ）

全エージェントの結果を受けて:

1. **裏取り**: 判断の要となる指摘2〜3件は自分の目で再確認する（1コマンドで済むもの）
2. **影響度×工数マトリクス**: A=高影響×低工数（即実行）/ B=高×中 / C=高×高 /
   D=低×低（ついで）/ E=やらない（工数対効果が合わない）に振る
3. **Top 10**: 日々の効率・安全・コストへの影響順
4. **決定事項の抽出**: ユーザーにしか決められない選択肢をOPTION A/B形式で3〜5点
5. **段階的実行プラン**: Phase 0（バックアップ・非破壊）→ 1（止血）→ 2（減量）→
   3（整備）→ 4（大物）。破壊的操作は「バックアップ→隔離→動作確認→後日削除」の順序を明記

## Step 4: 出力

1. **Markdownレポート**: 承認済みの出力先に1本（現状マップ→マトリクス→理想構成→プラン）
2. **HTMLダッシュボード**: findings JSONを組み立てて
   `python3 scripts/build_dashboard.py findings.json out.html` で生成し、ブラウザで開く
3. **共有カード（希望時のみ）**: サニタイズ済みsummary JSONを組み立てて
   `python3 scripts/build_share_cards.py cards.json outdir/` で16:9 PNG 4枚を生成

生成したHTMLは必ずheadlessブラウザ等で**レンダリング検証**してから完成と言う。

### 共有カードのサニタイズ規則（必須）

公開向けカードに含めてよいのは集計値と一般化した教訓のみ:

- 含めてよい: 指摘件数 / 常時ロードトークン / 許可リスト件数 / MCPツール数 / 教訓
- 含めない: 実パス（`~/.claude` などの一般名は可）/ 個人・患者フォルダ名 /
  コスト実額 / セキュリティの穴の具体的な位置 / アカウントID・キーの存在箇所

## Step 5: 治療（承認後のみ）

ユーザーの明示GO（「実行して」等）を受けてから、マトリクスAの項目を**1個ずつ**:

1. 変更前バックアップ（settings.json / crontab / 対象ファイル）
2. 実行 → その場で検証（件数・JSON validity・launchctl list等）→ 1行報告
3. 削除はしない。隔離フォルダ＋MANIFEST.tsv（元パス・理由・日付）で退避し、後日削除

途中で権限ガードにブロックされたら、迂回せず止まってユーザーに報告する。

## サブエージェントが使えない環境でのフォールバック

10領域を1つずつ順番にメインループで診断する（1領域ごとに findings を確定させてから次へ）。
時間はかかるが同じスキーマ・同じ出力に収束させる。
