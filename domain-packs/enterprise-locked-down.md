# Enterprise Locked-Down Pack

id: enterprise-locked-down
version: 1
languages: en, ja
compatible_reports: dashboard-json-v1

## Check: Permission guard visibility

Evidence: Inspect report findings for permission-denied probes and confirm they are recorded as findings.
Fails when: Blocked probes are missing from the report or described as successful coverage.
Safety: Read-only report review only; never route around permission guards.

## Check: Local-only evidence boundary

Evidence: Confirm report generation, renderer commands, and budget checks use local files only.
Fails when: A workflow uploads raw reports, private paths, secrets, or machine inventories to a third-party service.
Safety: Read-only workflow and documentation review only; do not execute uploads.
