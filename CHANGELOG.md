# Changelog

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
