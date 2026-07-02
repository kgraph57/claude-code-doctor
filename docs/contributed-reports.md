# Contributed Reports

Real checkups make the scoring model better, but raw reports are too sensitive
for public GitHub issues. Use the contributed-report format when you want to
share a grade without sharing paths, secrets, customer data, or full local
findings.

## Validate Before Posting

```bash
python3 scripts/validate_contributed_report.py samples/contributed-report.json
```

The validator accepts only aggregate fields and fails closed when it sees raw
user paths, emails, API-key shapes, bearer tokens, or other secret-shaped text.

## Schema

This is an abridged example. See
[`samples/contributed-report.json`](../samples/contributed-report.json) for a
complete valid file with all 10 domain summaries.

```json
{
  "schema": "claude-code-doctor-contributed-report-v1",
  "environment": {
    "os": "macOS",
    "harness": "Claude Code",
    "doctor_version": "v0.11.0",
    "audit_date": "2026-07-02"
  },
  "overall": {"grade": "B", "score": 72},
  "metrics": {
    "always_on_tokens": 18400,
    "permissions": 220,
    "mcp_tools": 31,
    "critical_findings": 0,
    "total_findings": 42
  },
  "domains": [
    {"name": "Directory structure", "grade": "B", "score": 74, "finding_count": 4, "red_flag_count": 0}
  ],
  "feedback": {
    "grade_felt": "about_right",
    "notes": "Aggregate feedback only."
  }
}
```

Rules:

- Include exactly 10 domain summaries.
- Use grades `A` through `E` and scores from `0` to `100`.
- Use non-negative integer counts for all metrics.
- Keep notes general: no raw paths, emails, secrets, patient data, customer
  data, or full report excerpts.

## Good Contribution

- Overall grade and score.
- OS family and harness.
- Aggregate metrics: token load, permission count, MCP tool count, critical
  finding count, total finding count.
- Per-domain grade, score, finding count, and red-flag count.
- A short note about whether the grade felt too harsh, too soft, or about right.

## Not For Public Issues

- Full local reports.
- `tree` output with real directories.
- Raw action prompts containing local paths.
- Secret-looking strings, emails, tokens, account IDs, patient data, or customer
  data.
