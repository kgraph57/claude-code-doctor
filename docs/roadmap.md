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

Shipped in this release. The real point of a checkup is the next checkup.

- Compare `before.json` and `after.json` reports with `scripts/compare_reports.py`.
- Show grade deltas, token-tax deltas, permission drift, and tool-count drift.
- Separate "improved", "unchanged", "regressed", "new red flag", and
  "resolved red flag".
- Generate a progress prescription for the next cleanup session.

## v0.5.0 - CI Budget Gate

Shipped in this release. Make AI-workspace drift visible in team repositories.

- Budget gate script that validates exported checkup JSON.
- Optional budgets for always-on context, permission count, MCP tool count, and
  critical findings.
- No secrets, no uploads, no machine scan inside CI unless a user explicitly
  supplies sanitized fixture data.
- Markdown summary comment for pull requests.

## v0.6.0 - Community Domain Packs

Shipped in this release. Let teams extend the checkup without forking the skill.

- Domain-pack format in Markdown.
- Validation script and example packs.
- Security-team pack, solo-founder pack, teaching/workshop pack, and enterprise
  locked-down pack.
- Clear compatibility rules for English and Japanese reports.

## v0.7.0 - Cross-Harness Checkups

Shipped in this release. Claude Code is the first target, not the only target.

- Adapter notes for Claude Code, Codex, Cursor, and OpenCode-style workbenches.
- Shared scoring vocabulary for context tax, permission drift, tool tax, and
  automation drift.
- Harness-specific no-go path and permission guidance.

## v0.8.0 - Windows Beta Coverage

Shipped in this release. Windows support starts with a reviewable read-only
PowerShell probe plan, not an opaque script.

- Generate `docs/windows.md` with `scripts/build_windows_probe_plan.py`.
- Map all ten audit domains to Windows-safe probes.
- Explicitly forbid mutating PowerShell commands, registry writes, and Task
  Scheduler changes.
- Keep Windows marked beta until a real Windows checkup report is contributed.

## v0.9.0 - 60-Second Walkthrough

Shipped in this release. The demo is a reproducible script plus a self-contained
HTML capture page, so a GIF or short video can be recorded without improvising.

- Generate `demo-walkthrough.md` and `demo-walkthrough.html` with
  `scripts/build_walkthrough.py`.
- Cover the story in six 10-second beats.
- Include the exact local demo commands for dashboard, diff, budget, domain
  packs, adapters, and Windows beta probes.
- Keep the demo fixture-based and fictional-data-only.

## v0.10.0 - Linux Beta Coverage

Shipped in this release. Linux and WSL support now starts with the same
reviewable-plan pattern as Windows: safe shell probes first, explicit no-go
paths before execution, and no mutating commands.

- Generate `docs/linux.md` with `scripts/build_linux_probe_plan.py`.
- Map all ten audit domains to Linux-safe probes.
- Cover cron, user systemd timers, listener inventory, config sizes, and
  `.claude` metadata without reading transcript contents.
- Explicitly forbid destructive shell commands, package-manager changes,
  `systemctl start/stop/enable/disable`, and `crontab -e`.
- Keep Linux marked beta until a real Linux checkup report is contributed.

## v0.11.0 - Contributed Report Intake

Shipped in this release. The project can now accept public calibration data
without asking people to paste raw local reports.

- Validate `claude-code-doctor-contributed-report-v1` JSON with
  `scripts/validate_contributed_report.py`.
- Require aggregate metrics, overall grade/score, and exactly 10 domain
  summaries.
- Reject raw user paths, emails, API-key shapes, bearer tokens, and other
  secret-shaped strings before public posting.
- Provide a fictional valid fixture in `samples/contributed-report.json`.
- Connect the checkup-grade issue template to the validator.

## v0.12.0 - Renderer Bug Repro Intake

Shipped in this release. Dashboard and share-card bugs can now be reported as
small fictional fixtures instead of screenshots or raw local reports.

- Validate `claude-code-doctor-renderer-bug-v1` JSON with
  `scripts/validate_renderer_bug.py`.
- Support dashboard and share-card renderer repros with command/expected/actual
  fields.
- Reject raw user paths, emails, API-key shapes, bearer tokens, and other
  secret-shaped strings.
- Provide a fictional dashboard repro in `samples/renderer-bug-dashboard.json`.
- Connect the bug-report issue template to the validator.

## v0.13.0 - Example Manifest

Shipped in this release. Public examples are now indexed and validated so they
remain fictional, reproducible, and safe to share.

- Validate `claude-code-doctor-example-manifest-v1` JSON with
  `scripts/validate_examples_manifest.py`.
- List sample reports, share-card fixtures, diff fixtures, budget fixtures,
  contributed-report examples, renderer bug repros, and generated walkthroughs.
- Require every example to be marked fictional and to name a proof command.
- Reject raw user paths, emails, API-key shapes, bearer tokens, and other
  secret-shaped strings in the manifest.
- Keep "better examples" tied to the core safety rule instead of becoming
  decoration.

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
  only after consent. Shipped via the example manifest; new examples should be
  added there with a proof command.
