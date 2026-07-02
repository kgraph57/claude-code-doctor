# Cross-Harness Checkups

Claude Code Doctor starts with Claude Code, but the checkup protocol is meant
for agentic coding workbenches in general. Adapter notes define how each
harness maps its local reality into the shared dashboard schema.

## Validate Adapter Notes

```bash
python3 scripts/validate_adapter_notes.py docs/adapters/*.md
```

Each adapter note must define:

- `harness`
- `status`
- `report_schema`
- `Scope`
- `No-Go Paths`
- `Permission Boundary`
- `Evidence Export`
- `Known Gaps`

The validator requires the permission boundary to explicitly forbid routing
around guards. A blocked probe is evidence, not an obstacle.

## Shared Vocabulary

- `context tax`: always-loaded instructions, memories, rules, or transcripts.
- `permission drift`: permissions that are stale, broad, dead, or unclear.
- `tool tax`: tools injected into a session whether or not the task needs them.
- `automation drift`: scheduled or background work that silently fails or points
  at vanished paths.
- `red flag`: a critical finding such as secret exposure, tracked private data,
  or absent safety boundaries.
- `prescription`: a user-approved fix prompt that preserves diagnosis/treatment
  separation.

## Included Adapters

- `docs/adapters/claude-code.md`: supported baseline adapter.
- `docs/adapters/codex.md`: draft adapter for Codex workspace instructions,
  tools, sandbox boundaries, and connector surfaces.
- `docs/adapters/cursor.md`: draft adapter for Cursor rules, agent settings,
  and workspace access rules.
- `docs/adapters/opencode.md`: schema sketch for OpenCode-style workbenches.
