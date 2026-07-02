# Community Domain Packs

Domain packs are optional Markdown checklists that extend Claude Code Doctor
without forking the core skill. They are meant for teams with different risk
profiles: security review, solo-founder hygiene, workshops, or locked-down
enterprise environments.

## Validate A Pack

```bash
python3 scripts/validate_domain_pack.py domain-packs/security-team.md
python3 scripts/validate_domain_pack.py domain-packs/*.md
```

## Format

```markdown
# Pack Title

id: security-team
version: 1
languages: en, ja
compatible_reports: dashboard-json-v1

## Check: Plaintext secret shapes

Evidence: Search settings and skill files for secret-shaped strings without printing the matched value.
Fails when: A secret-shaped string appears outside a documented test fixture.
Safety: Read-only search only; redact values and report path plus category.
```

Required metadata:

- `id`
- `version`
- `languages`
- `compatible_reports`

Each `## Check:` must include:

- `Evidence`: what the auditor should inspect
- `Fails when`: the measurable failure condition
- `Safety`: the read-only boundary and redaction rule

## Compatibility Rules

- `languages: en, ja` means the pack can be reported in English or Japanese.
- `compatible_reports: dashboard-json-v1` means findings can be represented in
  the dashboard schema documented in `references/report-format.md`.
- Packs must be read-only. They may ask the auditor to inspect evidence, but
  they must not ask it to edit, delete, upload, disable, rotate, or bypass
  anything.

## Included Packs

- `security-team.md`: secrets, tracked private files, and reportable evidence
  boundaries.
- `solo-founder.md`: always-on context rent and dormant automation drag.
- `teaching-workshop.md`: reproducible demos and student-safe no-go paths.
- `enterprise-locked-down.md`: permission guard visibility and local-only
  evidence boundaries.
