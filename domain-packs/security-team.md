# Security Team Pack

id: security-team
version: 1
languages: en, ja
compatible_reports: dashboard-json-v1

## Check: Plaintext secret shapes

Evidence: Search settings, commands, skills, agents, and sample fixtures for secret-shaped strings without printing the matched value.
Fails when: A secret-shaped string appears outside an explicitly documented sanitizer test fixture.
Safety: Read-only search only; redact values and report path plus category.

## Check: Private files tracked by git

Evidence: Inspect git status and tracked file names for personal, credential, patient, or customer-data patterns without opening sensitive files.
Fails when: A private or regulated-data path is tracked or staged.
Safety: Read-only git inspection only; report path category and do not print file contents.
