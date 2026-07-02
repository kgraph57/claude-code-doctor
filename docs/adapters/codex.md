# Codex Adapter

harness: codex
status: draft
report_schema: dashboard-json-v1

## Scope

Use Codex workspace instructions, AGENTS.md hierarchy, local tool availability, git state, test commands, sandbox settings, and connector/plugin surfaces.

## No-Go Paths

Confirm workspace roots and forbidden paths before reading. Respect project instructions that forbid private folders, credentials, or regulated records.

## Permission Boundary

Treat sandbox denial, connector denial, or permission-denied probes as findings. Do not route around a deny rule.

## Evidence Export

Export the same dashboard JSON counters where possible: always-on context, permission/tool surface, red flags, domain findings, and safe action prompts.

## Known Gaps

Codex session state and connector availability differ by desktop/API context, so adapter evidence should name the runtime that was inspected.
