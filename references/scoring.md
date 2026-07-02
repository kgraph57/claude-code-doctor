# Scoring model — how the checkup grades are computed

The checkup decomposes a Claude Code setup into **10 body systems**, scores each
0-100, converts scores to the five checkup grades (A-E), and lets **red flags**
override everything. This file is the single source of truth for that model.

## 1. Decomposition: domain → organ → checkpoints

| # | Domain | Organ (metaphor) | What it stands for |
|---|--------|------------------|--------------------|
| 1 | Directory structure | Skeleton | the frame everything hangs on |
| 2 | Dev repositories | Spine | posture: where code lives and how straight |
| 3 | CLAUDE.md hierarchy | Brain | standing knowledge and instructions |
| 4 | Settings & permissions | Heart | pumps on every beat (session); guards the valves |
| 5 | Skills | Hands | what it can actually do |
| 6 | Commands | Mouth | how you call for things |
| 7 | Subagents | Muscles | delegated workforce |
| 8 | MCP & plugins | Blood vessels | external supply lines |
| 9 | Automations & git | Autonomic nerves | things that fire without thinking |
| 10 | Usage & disk | Body fat | accumulated mass that slows movement |

Each domain's concrete checkpoints live in [`domains.md`](domains.md). Every
checkpoint produces zero or more findings with `severity` (high / medium / low)
and optionally `"critical": true`.

## 2. Per-domain score (0-100)

```text
burden = 3 x (# high) + 1 x (# medium) + 0.25 x (# low)
score  = max(5, 100 - 5 x burden)
```

Interpretation: one high finding costs 15 points; a domain with three highs and
a handful of mediums is already down at ~30.

## 3. Score → grade

| Grade | Score | Checkup label (en / ja) | Meaning |
|-------|-------|--------------------------|---------|
| A | 95-100 | Healthy / 異常なし | nothing to do |
| B | 80-94 | Minor findings / 軽度所見 | tidy when passing by |
| C | 55-79 | Watch / 要経過観察 | schedule a cleanup |
| D | 25-54 | Needs work / 要精密検査 | plan concrete fixes |
| E | 0-24 | Treat now / 要治療 | fix before it bites |

## 4. Red flags (override the arithmetic)

Some findings are dangerous regardless of how few points they cost. Mark them
`"critical": true` in the findings JSON; any critical finding forces the domain
grade to **E**, and the overall grade can never be A/B while any system is at E.

Standing red-flag list (extend as needed):

- Plaintext credentials / API keys / account IDs inside config files
- Private or patient-adjacent files tracked by git (one commit from public)
- Permission rules granting access into user-designated no-go paths
- A guardrail (deny list / destructive-command hook) that is entirely absent
- Automations executing scripts from untrusted or world-writable locations

## 5. Overall

```text
overall_score = mean(domain scores)   # rounded
overall_grade = grade(overall_score), capped at C if any system is E
```

The dashboard shows: overall grade + score, a 10-axis radar chart of the domain
scores, the body map with per-organ grade badges, and a RED FLAGS box listing
critical findings verbatim.

## 6. Honesty rules

- Scores are computed from findings actually verified with evidence — never
  from vibes. If a domain wasn't scanned, it gets no score (not a default A).
- The model is deliberately strict: a two-year-old heavy setup scoring D overall
  is expected, not embarrassing. The point is the delta at the next checkup.
- Record the scoring-model version in the report so future diffs stay comparable.
