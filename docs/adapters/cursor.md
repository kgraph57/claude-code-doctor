# Cursor Adapter

harness: cursor
status: draft
report_schema: dashboard-json-v1

## Scope

Use Cursor rules, project instructions, agent settings, extension/tool surfaces, repo state, test commands, and workspace-level automation evidence.

## No-Go Paths

Confirm excluded folders, private project files, and regulated data folders before scanning. Respect `.cursorignore` and project-level access rules.

## Permission Boundary

Treat blocked reads, disabled tools, or unavailable extensions as findings. Do not route around a deny rule.

## Evidence Export

Export dashboard JSON with adapter notes that distinguish Cursor-only rules from repository-owned rules.

## Known Gaps

Cursor UI and cloud-agent state may not be fully inspectable from a local repository checkout.
