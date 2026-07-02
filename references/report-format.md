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
      "recommendation": "concrete fix proposal (not executed)",
      "critical": false
    }
  ]
}
```

- `critical: true` marks red-flag findings (plaintext secrets, private data one
  commit from public, absent guardrails). Any critical finding forces the
  domain's checkup grade to E regardless of score — so auditors MUST set it
  when the evidence warrants.

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
  "metrics": {
    "always_on_tokens": 45000,
    "permissions": 804,
    "mcp_tools": 63
  },
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
    "D": {"title": "low impact x low effort / not worth it",
          "when": "while passing by", "items": ["..."], "skip": true}
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
- `metrics`: optional machine-readable counters used by Diff Mode. The renderer
  ignores this object, but `compare_reports.py` uses it before falling back to
  heuristics from `stats[]` labels.
- All sections except `meta` are optional; omitted sections don't render.

## Diff input (before/after comparison)

```bash
python3 scripts/compare_reports.py before.json after.json diff.md
```

Diff Mode accepts the same dashboard JSON export. For best results, include:

- `metrics.always_on_tokens`: number of always-loaded tokens.
- `metrics.permissions`: number of permission/allow-list entries.
- `metrics.mcp_tools`: number of MCP/plugin tools injected into the session.
- `checkup.systems[].domain`, `grade`, and `score`.
- `checkup.red_flags[]`.
- `domains[].findings[].title`.
- `actions[].id`, `title`, and optional `done: true` or
  `status: "completed"` for prescription progress.

## CI budget input

```bash
python3 scripts/check_budgets.py report.json budgets.json budget-summary.md
```

Budget files use maximum values:

```json
{
  "max": {
    "always_on_tokens": 30000,
    "permissions": 500,
    "mcp_tools": 40,
    "critical_findings": 0
  }
}
```

The budget gate never scans a machine. It only reads an exported report and a
budget file. Missing metrics are reported as missing and do not fail the gate;
present metrics fail when they exceed the configured maximum.

## Domain pack input

```bash
python3 scripts/validate_domain_pack.py domain-packs/*.md
```

Community domain packs are Markdown files with required metadata:

- `id`
- `version`
- `languages`
- `compatible_reports`

Each `## Check:` section must include `Evidence`, `Fails when`, and `Safety`.
The validator requires `Safety` to explicitly say `read-only`, so community
packs cannot silently turn the checkup into a mutation workflow.

## Adapter note input

```bash
python3 scripts/validate_adapter_notes.py docs/adapters/*.md
```

Adapter notes map a non-Claude-Code workbench into the same dashboard schema.
Each note must include `harness`, `status`, `report_schema`, and the sections
`Scope`, `No-Go Paths`, `Permission Boundary`, `Evidence Export`, and
`Known Gaps`. The permission boundary must explicitly forbid routing around
guards.

## Windows probe-plan input

```bash
python3 scripts/build_windows_probe_plan.py windows-probe-plan.md
```

The generated plan is documentation, not a scanner. It maps the ten domains to
read-only PowerShell commands and names forbidden mutations such as `Set-Item`,
`Remove-Item`, registry writes, and `schtasks /Change` or `/Delete`.

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
      {"organ": "Brain (optional)", "short": "CLAUDE.md",
       "domain": "CLAUDE.md hierarchy",
       "grade": "D", "score": 18, "note": "optional one-liner"}
    ]
  }
}
```

- `systems[]`: first half renders left, second half right. `short` labels the
  radar axis when `organ` is omitted. `grade`/`score` are optional — computed
  from the matching `domains[]` entry (matched by name; index fallback only
  when counts are equal) per `scoring.md`.
- A system with no matching domain renders as **not measured** (no score, no
  grade) and is excluded from the radar and the overall mean — never a default
  passing grade.
- Findings may carry `"critical": true` — any critical finding forces that
  domain's grade to E (red-flag override).
- `red_flags[]`: strings shown in the RED FLAGS box.
- Scoring model and organ mapping: see `scoring.md`.

## Action plan input (prescriptions)

```json
{
  "actions": [
    {"id": "RX-01", "phase": "Phase 2", "phase_when": "shown once per phase header",
     "title": "what to do", "effect": "expected effect (e.g. -10,000tk/session)",
     "effort": "30 min", "risk": "safe | careful | surgery",
     "steps": ["1-3 bullet steps"],
     "prompt": "ready-to-paste prompt for Claude Code that executes this one fix safely"}
  ]
}
```

- Rendered as checkable cards grouped by phase; checkbox state persists in the
  browser (localStorage). Each card carries a copy button for its prompt.
- Prompts must bake in the safety order (backup → quarantine → verify) and end
  with a reporting instruction, so pasting one is always safe.
- risk: `safe` (reversible) / `careful` (shared state) / `surgery` (do it with
  the user present).
