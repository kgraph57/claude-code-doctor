# 60-Second Walkthrough

A concise demo script for Claude Code Doctor. Use it as narration for a GIF,
screen recording, or live walkthrough.

## 0-10s - The Hidden Layer

Claude Code Doctor audits the AI-workspace layer before the agent writes code.

Visual cue: Show the 104-finding proof: context tax, dead permissions, MCP
bloat, and zombie automations.

## 10-20s - Safe First Run

Paste the read-only prompt and confirm scan scope, no-go paths, and one report
destination.

Visual cue: Diagnose first. Treat only after consent.

## 20-30s - Dashboard

Render the fictional fixture to preview the local dashboard without scanning a
real machine.

Visual cue: No uploads. No telemetry. Local HTML only.

## 30-40s - Diff Mode

Compare before and after checkups to prove what improved and what regressed.

Visual cue: The second checkup is the point of the first one.

## 40-50s - CI Budget Gate

Fail a pull request when context, permissions, tools, or critical findings cross
a budget.

Visual cue: Useful teams make drift visible before it becomes normal.

## 50-60s - Extend Safely

Validate community domain packs and adapter notes before expanding the checkup.

Visual cue: Same protocol across Claude Code, Codex, Cursor, and Windows beta
probes.

## Demo Commands

```bash
python3 scripts/build_dashboard.py samples/dashboard.json /tmp/claude-code-doctor-dashboard.html
python3 scripts/compare_reports.py samples/diff-before.json samples/diff-after.json /tmp/claude-code-doctor-diff.md
python3 scripts/check_budgets.py samples/diff-before.json samples/budgets.json /tmp/claude-code-doctor-budget.md
python3 scripts/validate_domain_pack.py domain-packs/*.md
python3 scripts/validate_adapter_notes.py docs/adapters/*.md
python3 scripts/build_windows_probe_plan.py /tmp/claude-code-doctor-windows.md
```
