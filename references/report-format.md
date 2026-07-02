# 出力フォーマット定義

## findings スキーマ（各サブエージェントに強制する構造化出力）

```json
{
  "summary": "3〜6文の領域概観",
  "inventory": "何がどこに何件・何バイトあるかの事実マップ（ツリー断片可）",
  "findings": [
    {
      "title": "指摘の1行タイトル",
      "severity": "high | medium | low",
      "effort": "low | medium | high",
      "detail": "エビデンス: パス・サイズ・件数・引用",
      "recommendation": "具体的な修正提案（実行はしない）"
    }
  ]
}
```

- severity = 日々の効率・安全・コストへの影響度
- effort = 修正の工数
- detailは「確認した事実」のみ。推測は書かない

## ダッシュボード入力（build_dashboard.py）

```json
{
  "meta": {
    "title": "Claude Code 環境監査",
    "date": "YYYY-MM-DD",
    "method": "read-only 並列監査（10領域）",
    "note": "診断のみ・未変更"
  },
  "stats": [
    {"n": "104", "unit": "件", "label": "総指摘数", "tone": "alert"},
    {"n": "45,000", "unit": "tk", "label": "常時ロード", "tone": "alert"}
  ],
  "decisions": [
    {"q": "決定の見出し", "why": "背景1〜2文",
     "options": [{"tag": "OPTION A", "body": "..."}, {"tag": "OPTION B", "body": "..."}]}
  ],
  "top": [{"title": "見出し", "tag": "コスト直撃(任意)", "body": "本文"}],
  "matrix": {
    "A": {"title": "高影響 × 低工数", "when": "即実行", "items": ["..."], "prime": true},
    "B": {"title": "高影響 × 中工数", "when": "今週中", "items": ["..."]},
    "C": {"title": "高影響 × 高工数", "when": "計画して実行", "items": ["..."]},
    "D": {"title": "低影響 × 低工数 / やらない", "when": "ついで", "items": ["..."], "skip": true}
  },
  "phases": [{"name": "Phase 1", "when": "30分・止血", "steps": ["..."], "note": "任意"}],
  "trees": [{"title": "現状マップ", "body": "preで表示するテキスト"}],
  "domains": [
    {"name": "領域名", "sub": "説明", "summary": "...",
     "findings": [/* findingsスキーマの配列 */]}
  ]
}
```

statsのtone: `alert`（オレンジ・問題系）/ `key`（ティール・规模系）。

## マトリクスの振り方

| 区分 | 意味 | 着手 |
|---|---|---|
| A | 高影響 × 低工数 | 即実行候補（合計1時間以内を目安） |
| B | 高影響 × 中工数 | 今週中（2〜4時間） |
| C | 高影響 × 高工数 | 計画して実行・本人立ち会い |
| D | 低影響 × 低工数 | 他作業のついでに |
| E | 効果が工数に見合わない | やらないと明記する（重要） |

## 段階的実行プランの雛形

- Phase 0: バックアップと確認（非破壊）
- Phase 1: 止血（安全・コストの高影響×低工数）
- Phase 2: 減量（常時ロード・コンテキスト税）
- Phase 3: 整備（スキル・エージェント・トリガー）
- Phase 4: 大物（ディスク・git履歴・構造統合）

破壊的操作は常に「バックアップ → 隔離（MANIFEST付き）→ 動作確認 → 後日削除」。
