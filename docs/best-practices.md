# Best practices for putting a frontier model to work

Principles baked into this skill's design. The setup audit is one application;
the principles carry over to research, review, and large refactors driven by
frontier-class models (Claude Fable 5 / Opus) inside Claude Code.

For the broader "why this is a checkup, not a cleanup script" frame, see
[`ai-checkup-philosophy.md`](ai-checkup-philosophy.md).

## 1. Decide the shape of the work before you fire the model

Don't open with "audit everything". Decide first:

- **Scope** — what gets scanned, what must never be touched
- **Output shape** — the findings schema, the matrix, the phased plan
- **The permission line** — read-only or not, and where writing is allowed

Once the shape is fixed, parallelization, aggregation and visualization all become
mechanical. Fire a strong model at a vague shape and you get eloquent,
unstructurable prose.

## 2. Read-only parallel fan-out, top-tier synthesis

- Coverage comes from **cheap models in parallel**: scanning ten domains is labor,
  not judgment. Pin subagent models explicitly — letting them inherit the top-tier
  default is the silent cost leak this audit keeps finding in the wild.
- Judgment comes from **one strong pass**: the matrix, the extracted decisions, and
  the re-verification of pivotal claims stay on the main loop. Re-verify only the
  2-3 load-bearing findings that a single command can confirm.

## 3. Force structured output

Free-form answers make synthesis manual labor. Receiving everything as
title / severity / effort / detail / recommendation means:

- Aggregation (counts, per-domain distribution) is mechanical
- The dashboard is one script away
- Evidence and proposal stay separated, which keeps the fix decision clean

## 4. Separate diagnosis from treatment (user sovereignty)

- The diagnosis phase is **strictly read-only** — no matter how confident the model is
- Decisions go to the user as **OPTION A/B** items they can answer by number
- "Probably fine" is not approval. When wording is ambiguous, stop and ask
- Treatment is one item at a time: backup → execute → verify on the spot → one-line report
- Nothing gets deleted. Quarantine with a MANIFEST (original path, reason, date),
  delete weeks later

If a permission guard blocks a step, don't route around it — report it.
The guard firing is evidence the setup is healthy.

## 5. Carry deliverables to "showable"

- Don't stop at a long Markdown report: render an **HTML dashboard**
  (stat band → decisions → matrix → collapsible findings)
- **Verify rendering with a headless-browser screenshot** before calling HTML done —
  CSS bugs only reveal themselves to eyes
- For public sharing, generate **sanitized cards** separately. Internal reports contain
  real paths, security gaps and spend figures that must never leave the machine

## 6. Always-on context is rent

- CLAUDE.md, rules, memory and MCP tool lists are paid for at the start of every session
- Write skills with progressive disclosure: a thin SKILL.md skeleton, details split
  into references/ loaded on demand
- The audit always reports **total always-on tokens as a number** — you can't cut
  what you don't measure
