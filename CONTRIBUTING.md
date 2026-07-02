# Contributing

Issues and PRs are welcome, in English or Japanese. 日本語でどうぞ。

## The fastest ways to help

1. **Run the checkup and report your overall grade** in an issue — real-world
   grades calibrate the scoring model (`references/scoring.md`).
2. **Add or sharpen a check.** The audit's checks live in
   [`references/domains.md`](references/domains.md) as plain-language
   checklists — no code needed for most contributions. Propose new checks as a
   PR that edits the relevant domain section.
3. **Port a domain to another OS.** Domain 9 (automations) is the most
   macOS-flavored; Linux equivalents (systemd timers) and Windows (Task
   Scheduler) checks are wanted.

## Ground rules for changes

- **Diagnosis stays read-only.** Any proposed check must be executable with
  read-only commands. Checks that mutate state will not be merged.
- **Honesty over polish.** Scores are computed indicators, not measurements —
  changes to weights or thresholds need a written rationale in `scoring.md`.
- **No new runtime dependencies** for the dashboard (`build_dashboard.py` is
  Python standard library only, on purpose). Share-card dependencies stay
  optional.
- Sanitizer changes must keep the **fail-closed** property: when in doubt,
  refuse to render rather than risk leaking.

## Developing

```bash
# render a dashboard from a sample
python3 scripts/build_dashboard.py your-findings.json out.html

# render share cards (needs Chrome/Chromium + Pillow)
python3 scripts/build_share_cards.py your-cards.json out/
```

Input schemas: [`references/report-format.md`](references/report-format.md).
Before a PR, run both scripts against your sample and eyeball the rendered
HTML in a browser (CSS bugs only reveal themselves to eyes).
