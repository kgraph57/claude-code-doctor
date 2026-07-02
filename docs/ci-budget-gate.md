# CI Budget Gate

Use `check_budgets.py` when you want a sanitized Claude Code Doctor report to
act like a CI guardrail. It does not scan a machine in CI. It only reads a JSON
report that you explicitly provide.

## Command

```bash
python3 scripts/check_budgets.py report.json budgets.json budget-summary.md
```

Exit codes:

- `0`: all present metrics are within budget.
- `1`: at least one present metric exceeds budget.
- `2`: invalid CLI arguments or invalid JSON input.

## Budget File

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

Missing metrics are reported as missing, not failed. This keeps the gate usable
while teams roll out the full report schema gradually.

## GitHub Actions Example

```yaml
name: claude-code-doctor-budget

on:
  pull_request:

jobs:
  budget:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-python@v5
        with:
          python-version: "3.11"
      - run: |
          python scripts/check_budgets.py \
            reports/claude-code-doctor.json \
            .github/claude-code-doctor-budgets.json \
            /tmp/claude-code-doctor-budget.md
```

The default recommendation for real teams is `critical_findings: 0`. The sample
fixture in `samples/budgets.json` is intentionally lenient because
`samples/diff-before.json` contains a fictional red flag for demo purposes.
