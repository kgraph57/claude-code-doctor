# Solo Founder Pack

id: solo-founder
version: 1
languages: en, ja
compatible_reports: dashboard-json-v1

## Check: Always-on context rent

Evidence: Count always-loaded instruction files and estimate token load by source.
Fails when: Rare workflows or dated notes are loaded into every session.
Safety: Read-only file size and token estimation only; do not rewrite context files.

## Check: Dormant automation drag

Evidence: Inspect configured cron, launchd, or systemd timers for missing paths and repeated failures.
Fails when: A scheduled task points at a missing path or stale log target.
Safety: Read-only automation inventory only; do not disable timers.
