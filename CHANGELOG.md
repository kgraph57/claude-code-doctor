# Changelog

## v0.13.0 - 2026-07-02

This release ships example-manifest validation: a safety and reproducibility
index for the public sample files and generated demo artifacts.

### Added

- `scripts/validate_examples_manifest.py` for validating the public examples
  index.
- `docs/examples-manifest.json` listing fictional examples and their proof
  commands.
- `docs/examples.md` explaining the example safety contract.
- CI coverage for the example manifest.

### Changed

- README and README.ja now include an Example Manifest quick command.
- Roadmap now marks better safe examples as shipped.

## v0.12.0 - 2026-07-02

This release ships renderer-bug validation: a safe minimal reproduction format
for dashboard and share-card rendering issues.

### Added

- `scripts/validate_renderer_bug.py` for validating sanitized renderer bug
  fixtures.
- `samples/renderer-bug-dashboard.json` as a fictional valid dashboard repro.
- `docs/renderer-bug-reports.md` with the public-safe bug report schema.
- CI coverage for the renderer-bug validator.

### Changed

- README and README.ja now include a renderer-bug quick command.
- The bug-report issue template now points contributors to the renderer-bug
  validator.
- Roadmap now marks renderer-bug validation as shipped.

## v0.11.0 - 2026-07-02

This release ships contributed-report validation: a safe intake format for
people who want to share real overall grades without posting raw local reports.

### Added

- `scripts/validate_contributed_report.py` for validating sanitized community
  grade reports.
- `samples/contributed-report.json` as a fictional valid fixture.
- `docs/contributed-reports.md` with the public-safe report schema.
- CI coverage for the contributed-report validator.

### Changed

- README and README.ja now include a contributed-report quick command.
- The checkup-grade issue template now points contributors to the validator.
- Roadmap now marks contributed-report validation as shipped.

## v0.10.0 - 2026-07-02

This release ships Linux beta coverage: a read-only shell probe plan for Linux
and WSL setup checkups.

### Added

- `scripts/build_linux_probe_plan.py` for generating a Linux read-only probe
  plan.
- `docs/linux.md` generated from the probe-plan builder.
- Linux-safe read-only command guidance in `SKILL.md` and
  `references/domains.md`.
- CI coverage for the Linux probe-plan generator.

### Changed

- README and README.ja now include a Linux beta quick command.
- Roadmap now marks Linux beta coverage as shipped.

## v0.9.0 - 2026-07-02

This release ships a 60-second walkthrough generator: a repeatable Markdown
script and self-contained HTML capture surface for demos, GIFs, or short video
walkthroughs.

### Added

- `scripts/build_walkthrough.py` for generating `demo-walkthrough.md` and
  `demo-walkthrough.html`.
- `docs/walkthrough.md` as the canonical narration script.
- `docs/generated-demo/` generated demo artifacts.
- CI coverage for the walkthrough generator.

### Changed

- README and README.ja now include a 60-second walkthrough quick command.
- Roadmap now marks the 60-second walkthrough generator as shipped.

## v0.8.0 - 2026-07-02

This release ships Windows beta coverage: a read-only PowerShell probe plan that
maps all ten audit domains to reviewable Windows-safe commands.

### Added

- `scripts/build_windows_probe_plan.py` for generating a Windows read-only
  probe plan.
- `docs/windows.md` generated from the probe-plan builder.
- Windows-safe read-only command guidance in `SKILL.md` and
  `references/domains.md`.
- CI coverage for the Windows probe-plan generator.

### Changed

- README and README.ja now describe Windows beta coverage instead of marking
  Windows as untuned.

## v0.7.0 - 2026-07-02

This release ships Cross-Harness Checkups: adapter notes for applying the same
diagnostic protocol beyond Claude Code.

### Added

- `scripts/validate_adapter_notes.py` for validating cross-harness adapter
  notes.
- `docs/cross-harness.md` with shared vocabulary and adapter rules.
- Adapter notes for:
  - Claude Code
  - Codex
  - Cursor
  - OpenCode-style workbenches
- CI coverage for all bundled adapter notes.

### Changed

- README and README.ja now include a Cross-Harness Checkups quick command.
- Roadmap now marks v0.7.0 Cross-Harness Checkups as shipped.

## v0.6.0 - 2026-07-02

This release ships Community Domain Packs: read-only Markdown check packs that
teams can validate before using or contributing.

### Added

- `scripts/validate_domain_pack.py` for validating community pack metadata and
  per-check safety fields.
- `docs/domain-packs.md` with pack format and compatibility rules.
- Four example packs in `domain-packs/`:
  - `security-team.md`
  - `solo-founder.md`
  - `teaching-workshop.md`
  - `enterprise-locked-down.md`
- CI coverage for all bundled domain packs.

### Changed

- README and README.ja now include a Community Domain Packs quick command.
- Roadmap now marks v0.6.0 Community Domain Packs as shipped.

## v0.5.0 - 2026-07-02

This release ships CI Budget Gate: teams can fail a PR when a sanitized report
exceeds agreed AI-workspace budgets.

### Added

- `scripts/check_budgets.py` for budget enforcement in CI.
- `samples/budgets.json` as a copyable budget fixture.
- `docs/ci-budget-gate.md` with command usage, exit codes, budget schema, and
  a GitHub Actions example.
- CI coverage for the budget gate fixture.

### Changed

- README and README.ja now include a CI Budget Gate quick command.
- Roadmap now marks v0.5.0 CI Budget Gate as shipped.

## v0.4.0 - 2026-07-02

This release ships Diff Mode: the second checkup can now prove what improved,
what regressed, and what still needs attention.

### Added

- `scripts/compare_reports.py` for comparing two dashboard JSON exports.
- Fictional before/after fixtures:
  - `samples/diff-before.json`
  - `samples/diff-after.json`
- Markdown diff output covering metric deltas, domain grade/score deltas, red
  flags, findings, prescription progress, and the next progress prescription.
- CI coverage for the diff fixtures and compare script.

### Changed

- README and README.ja now include a Diff Mode quick command.
- Roadmap now marks v0.4.0 Diff Mode as shipped.

## v0.3.0 - 2026-07-02

This release sharpens the public GitHub surface: a visitor can understand the
promise, paste a safe prompt into Claude Code, run a local demo, and see where
the project is going.

### Added

- LLM Quickstart / paste-ready audit prompt in English and Japanese.
- 10-second demo commands for the dashboard and share-card renderers.
- GitHub Actions test workflow for renderer and fixture validation.
- Issue templates for checkup-grade reports, domain-pack proposals, and bugs.
- Public roadmap in `docs/roadmap.md`.

### Changed

- README top section now leads with the 104-finding proof, safe first-run
  prompt, local demo, and "Why Star This Repo?" instead of burying those lower
  in the page.
- Japanese README now mirrors the English star-conversion surface.

## v0.2.0 - 2026-07-02

This release turns Claude Code Doctor from a clever audit skill into a more
complete AI workspace checkup package.

### Added

- AI workspace checkup philosophy docs in English and Japanese:
  - `docs/ai-checkup-philosophy.md`
  - `docs/ai-checkup-philosophy.ja.md`
- Sample dashboard and share-card JSON fixtures in `samples/`.
- Standard-library regression tests in `tests/`.
- README links to the philosophy docs and renderer preview command.

### Hardened

- `build_dashboard.py` now reports invalid JSON without a Python traceback.
- Dashboard rendering now tolerates malformed optional sections from LLM output.
- High-severity findings cap a domain at C; critical findings force E.
- User-supplied dashboard text is covered by explicit HTML escaping tests.
- `build_share_cards.py` sanitizes all visible fields, including numeric fields.
- Share-card rendering fails closed when secret-shaped strings survive masking.

### Removed

- Deleted the stray invalid `bad.json` fixture from the repository root.
