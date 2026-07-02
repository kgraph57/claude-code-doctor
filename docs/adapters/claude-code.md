# Claude Code Adapter

harness: claude-code
status: supported
report_schema: dashboard-json-v1

## Scope

Use Claude Code skills, commands, settings, MCP tools, subagents, transcripts, local repos, and local automation evidence.

## No-Go Paths

Confirm personal, credential, patient, and customer-data exclusions before scanning. The scan should not traverse no-go paths even for counts.

## Permission Boundary

Treat permission-denied probes as findings. Do not route around a deny rule.

## Evidence Export

Export dashboard JSON with `metrics`, `checkup.systems`, `checkup.red_flags`, `domains[].findings`, and `actions`.

## Known Gaps

Windows-specific checks and non-Claude Code transcript formats need separate coverage.
