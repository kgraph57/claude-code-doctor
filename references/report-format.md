# Output formats

## findings schema (force this structured output on every subagent)

```json
{
  "summary": "3-6 sentence overview of the domain",
  "inventory": "factual map: what exists where, counts and sizes (tree fragments OK)",
  "findings": [
    {
      "title": "one-line finding",
      "severity": "high | medium | low",
      "effort": "low | medium | high",
      "detail": "evidence: paths, sizes, counts, quotes",
      "recommendation": "concrete fix proposal (not executed)"
    }
  ]
}
```

- severity = impact on daily efficiency, safety, and cost
- effort = cost of fixing
- `detail` contains verified facts only, never guesses

## Dashboard input (build_dashboard.py)

```json
{
  "meta": {
    "lang": "en",
    "title": "Claude Code Setup Audit",
    "date": "YYYY-MM-DD",
    "method": "read-only parallel audit (10 domains)",
    "note": "diagnosis only, nothing changed",
    "lede": "intro sentence",
    "kicker": "CLAUDE CODE DOCTOR",
    "footer": "left footer text"
  },
  "stats": [
    {"n": "104", "unit": "", "label": "total findings", "tone": "alert"},
    {"n": "45,000", "unit": "tk", "label": "always-on load", "tone": "alert"}
  ],
  "decisions": [
    {"q": "decision headline", "why": "1-2 sentence background",
     "options": [{"tag": "OPTION A", "body": "..."}, {"tag": "OPTION B", "body": "..."}]}
  ],
  "top": [{"title": "headline", "tag": "cost hit (optional)", "body": "text"}],
  "matrix": {
    "A": {"title": "high impact x low effort", "when": "do now",
          "items": ["..."], "prime": true},
    "B": {"title": "high impact x mid effort", "when": "this week", "items": ["..."]},
    "C": {"title": "high impact x high effort", "when": "plan it", "items": ["..."]},
    "D": {"title": "low impact / not worth it", "when": "while passing by",
          "items": ["..."], "skip": true}
  },
  "phases": [{"name": "Phase 1", "when": "30 min, stop the bleeding",
              "steps": ["..."], "note": "optional"}],
  "trees": [{"title": "state map", "body": "text rendered in a <pre> block"}],
  "domains": [
    {"name": "domain name", "sub": "one-line scope", "summary": "...",
     "findings": [/* findings-schema array */]}
  ]
}
```

- `meta.lang`: `"en"` (default) or `"ja"` — switches all chrome labels
- `stats[].tone`: `alert` (orange, problems) / `key` (teal, scale)
- All sections except `meta` are optional; omitted sections don't render.

## How to assign the matrix

| Cell | Meaning | When to act |
|---|---|---|
| A | high impact x low effort | now (aim: under one hour total) |
| B | high impact x mid effort | this week (2-4 hours) |
| C | high impact x high effort | planned, with the user present |
| D | low impact x low effort | while passing by |
| E | effort exceeds payoff | explicitly say "not doing this" (important) |

## Phased-plan template

- Phase 0: backups and checks (non-destructive)
- Phase 1: stop the bleeding (high-impact x low-effort safety and cost items)
- Phase 2: context diet (always-on load)
- Phase 3: grooming (skills, agents, triggers)
- Phase 4: heavy lifting (disk, git history, structural moves)

Destructive operations always follow: backup → quarantine (with MANIFEST) →
verify → delete later.

## Checkup input (body map + radar + grades)

```json
{
  "checkup": {
    "comment": "doctor's one-paragraph comment",
    "overall": "D",            
    "overall_score": 35,       
    "red_flags": ["critical finding 1", "critical finding 2"],
    "systems": [
      {"organ": "Brain", "domain": "CLAUDE.md hierarchy",
       "grade": "D", "score": 18, "note": "optional one-liner"}
    ]
  }
}
```

- `systems[]`: first half renders left of the figure, second half right.
  `grade`/`score` are optional — computed from the matching `domains[]` entry
  (by name, falling back to index) per `scoring.md`.
- Findings may carry `"critical": true` — any critical finding forces that
  domain's grade to E (red-flag override).
- `red_flags[]`: strings shown in the RED FLAGS box.
- Scoring model and organ mapping: see `scoring.md`.
