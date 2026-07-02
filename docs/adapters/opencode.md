# OpenCode Adapter

harness: opencode
status: sketch
report_schema: dashboard-json-v1

## Scope

Use OpenCode-style project instructions, tool configuration, model routing, workspace roots, git state, and local automation evidence.

## No-Go Paths

Confirm workspace root and no-go paths before scanning. Avoid assumptions from Claude Code or Codex path conventions.

## Permission Boundary

Treat unsupported tools, blocked probes, and absent configuration access as findings. Do not route around a deny rule.

## Evidence Export

Export dashboard JSON using the shared vocabulary for context tax, permission drift, tool tax, automation drift, red flags, and prescriptions.

## Known Gaps

OpenCode ecosystems vary; this adapter is a schema sketch until real fixture reports are contributed.
