# Renderer Bug Reports

Renderer bugs are easier to fix when they arrive as tiny fictional fixtures
instead of screenshots of private reports. Use the renderer-bug format for
dashboard and share-card rendering issues.

## Validate Before Posting

```bash
python3 scripts/validate_renderer_bug.py samples/renderer-bug-dashboard.json
```

The validator accepts minimal fictional input for supported renderers and fails
closed when it sees raw user paths, emails, API-key shapes, bearer tokens, or
other secret-shaped text.

The renderer consumes the nested `input` object. Save that object to the JSON
path named in `reproduction.command` when you reproduce the bug locally.

## Schema

```json
{
  "schema": "claude-code-doctor-renderer-bug-v1",
  "renderer": "dashboard",
  "doctor_version": "v0.12.0",
  "input": {
    "meta": {"lang": "en", "title": "Minimal fictional renderer bug fixture"}
  },
  "reproduction": {
    "command": "python3 scripts/build_dashboard.py /tmp/ccd-bug.json /tmp/ccd-bug.html",
    "expected": "The stat card renders inside the viewport.",
    "actual": "The stat card overflows the fixture viewport.",
    "environment": "macOS, Python 3.13, Chrome 126"
  },
  "safety": {
    "fictional_data": true,
    "no_private_paths": true,
    "no_secrets": true
  }
}
```

Rules:

- Use `renderer: "dashboard"` for `scripts/build_dashboard.py`.
- Use `renderer: "share_cards"` for `scripts/build_share_cards.py`.
- Keep `input` minimal and fictional.
- Set all safety flags to `true`.
- Do not include raw report exports, real paths, emails, secrets, account IDs,
  patient data, customer data, or screenshots containing private content.

Good bug reports include:

- The validated JSON fixture.
- The command used to reproduce the issue.
- Expected vs. actual rendering behavior.
- OS, Python version, and Chrome/Chromium version when browser rendering is
  involved.
