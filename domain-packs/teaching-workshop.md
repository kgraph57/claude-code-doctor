# Teaching Workshop Pack

id: teaching-workshop
version: 1
languages: en, ja
compatible_reports: dashboard-json-v1

## Check: Workshop reproducibility

Evidence: Confirm setup instructions, demo fixtures, and local render commands exist for a fresh participant machine.
Fails when: A demo requires private local paths, hidden credentials, or undocumented manual steps.
Safety: Read-only documentation and fixture inspection only; do not create accounts or change settings.

## Check: Student-safe no-go paths

Evidence: Inspect audit prompts and examples for explicit no-go path confirmation before scanning.
Fails when: A workshop prompt encourages broad scanning without no-go path confirmation.
Safety: Read-only prompt review only; do not run scans on participant machines.
