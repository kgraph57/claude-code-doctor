# Examples

Claude Code Doctor examples are meant to be public, inspectable, and safe to
run. The example manifest makes that promise testable.

## Validate The Manifest

```bash
python3 scripts/validate_examples_manifest.py docs/examples-manifest.json
```

The manifest uses `claude-code-doctor-example-manifest-v1` and records:

- the repo-relative example path
- the example kind
- whether the example is fictional
- the validator or renderer command that proves it still works
- short notes for humans reviewing the file

The validator rejects missing files, non-fictional examples, unsupported
validator commands, raw user paths, emails, API-key shapes, bearer tokens, and
other secret-shaped text.

## Why This Exists

Public examples are a trust surface. If they drift, users lose confidence. If
they contain real local paths or private data, the project teaches the wrong
habit. The manifest keeps examples useful while preserving the core rule:
diagnose first, treat only after consent, and publish only fictional or
sanitized fixtures.
