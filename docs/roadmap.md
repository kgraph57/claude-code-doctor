# Roadmap

Claude Code Doctor should grow from a clever one-shot audit into a recurring
diagnostic system for agentic coding workbenches. The north star is simple:
make the invisible AI-workspace layer measurable, reviewable, and safe to
improve.

## v0.3.0 - Show, Don't Tell

Shipped in this release.

- LLM Quickstart: paste-ready prompt for a safe first run.
- 10-second demo: render the dashboard and share cards from fictional fixtures.
- README proof strip: the 104-finding patient-zero result stays above the fold.
- GitHub surface: CI badge, issue templates, changelog, and this roadmap.

## v0.4.0 - Diff Mode

The real point of a checkup is the next checkup.

- Compare `before.json` and `after.json` reports.
- Show grade deltas, token-tax deltas, permission drift, and tool-count drift.
- Separate "improved", "unchanged", "regressed", and "new red flag".
- Generate a progress prescription for the next cleanup session.

## v0.5.0 - CI Budget Gate

Make AI-workspace drift visible in team repositories.

- GitHub Action that validates exported checkup JSON.
- Optional budgets for always-on context, permission count, MCP tool count, and
  critical findings.
- No secrets, no uploads, no machine scan inside CI unless a user explicitly
  supplies sanitized fixture data.
- Markdown summary comment for pull requests.

## v0.6.0 - Community Domain Packs

Let teams extend the checkup without forking the skill.

- Domain-pack format in YAML or Markdown.
- Validation script and example packs.
- Security-team pack, solo-founder pack, teaching/workshop pack, and enterprise
  locked-down pack.
- Clear compatibility rules for English and Japanese reports.

## v0.7.0 - Cross-Harness Checkups

Claude Code is the first target, not the only target.

- Adapter notes for Claude Code, Codex, Cursor, and OpenCode-style workbenches.
- Shared scoring vocabulary for context tax, permission drift, tool tax, and
  automation drift.
- Harness-specific no-go path and permission guidance.

## What We Will Not Build

- No default auto-fix mode. Diagnosis and treatment stay separate.
- No secret uploads, telemetry, or hosted report ingestion.
- No destructive cleanup commands.
- No fake celebrity endorsements or unverifiable claims.
- No bypassing permission guards. A blocked probe is a finding, not an obstacle
  to route around.

## How To Contribute

Good contributions make the checkup more measurable or safer:

- Sanitized overall-grade reports from real setups.
- Reproducible renderer bugs.
- Domain-pack proposals with explicit checks and expected evidence.
- OS-specific coverage notes for Linux and Windows.
- Better examples that preserve the core safety rule: diagnose first, treat
  only after consent.
