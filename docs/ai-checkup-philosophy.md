# The philosophy of an AI workspace checkup

This explanation is for people who already use Claude Code, Codex, Cursor, MCP
servers, skills, commands, subagents, and local automations. It explains why an
AI workspace needs a checkup, not just a cleanup script.

The goal is simple: after reading this document, you should understand what this
tool treats as "health" and why diagnosis stays separate from treatment.

## Health means trustworthy delegation

An AI workspace is healthy when a human can delegate work without wondering what
hidden context, stale permission, forgotten automation, or oversized tool list is
tilting the result.

That definition is deliberately practical. It does not ask whether the model is
smart in the abstract. It asks whether the whole working environment lets the
model act with the right context, the right permissions, the right tools, and the
right evidence trail.

## The workspace is the system

The model is only one organ. The rest of the body is made of instructions, memory,
skills, commands, subagents, MCP servers, permissions, hooks, automations,
transcripts, caches, and local repositories. These pieces interact.

That is why this project checks ten domains instead of one file. A bloated
`CLAUDE.md` can waste context. A stale allow-list can widen access. A zombie
automation can fail every morning. A duplicate MCP server can inject tools that
the current task never needs. The system becomes unhealthy through accumulation,
not one dramatic mistake.

The scoring model is a triage device, not a moral grade. The most useful number
is often the delta between checkups.

## Diagnosis is not treatment

The central rule is clinical: diagnose first, treat only after consent.

During diagnosis, the auditor gathers evidence and writes proposals. It does not
move files, edit settings, delete caches, rewrite commands, or "just fix" an
obvious problem. That restraint is the product.

Treatment starts only after explicit approval. Each fix should be small enough to
review, reversible enough to trust, and specific enough to verify. The safest
order is backup, quarantine, verify, report. Deletion can wait.

## Read-only is a contract, not a force field

This project is honest about the phrase "read-only". In a prompt-driven agent,
read-only is an instruction-level contract. It is not an operating-system
sandbox.

Hard guarantees require permission deny rules, filesystem controls, or a
separate execution environment. The checkup should respect those controls. If a
guard blocks a probe or a fix, the auditor should stop and report the guard. A
working guard is a finding in favor of the setup.

## Context is rent

Always-on context is paid at the start of every session. The rent may be worth
paying, but it should be visible.

This is why the checkup measures persistent instructions, inherited rules, memory
loads, and injected tool lists. You cannot reduce a context tax that you never
count. Progressive disclosure is the healthy alternative: keep the always-on
entry point thin, then load detailed references only when a task needs them.

## Permissions are immune function

Permissions should be specific, current, and boring. A permission system is
healthy when it allows routine work and blocks surprising work.

Dead allow-list entries, broad write access, unscoped commands, and access into
no-go paths are not merely clutter. They are immune-system defects. The checkup
therefore treats permission drift as a first-class medical sign.

## No-go paths express human sovereignty

Some areas should not be read at all. Personal documents, patient data, recovery
codes, private keys, and sensitive business files belong outside the scan unless
the human explicitly chooses otherwise.

This boundary matters because a helpful AI can still be too curious. A good
checkup narrows the world before it starts looking.

## Evidence beats vibes

Every finding should pair evidence with a proposal. The evidence side records
paths, counts, sizes, timestamps, and observed behavior. The proposal side says
what to do next.

Keeping those fields separate protects the human decision. It also makes the
report testable: another agent, or the same agent next month, can inspect whether
the evidence changed.

## A checkup must be showable

A long Markdown report is useful, but it is not enough. The result should be easy
to inspect as a dashboard, easy to revisit as a progress tracker, and safe to
summarize publicly without leaking real paths or secret-shaped strings.

This is why the project renders an HTML dashboard, persists prescription
checkboxes locally, and generates share cards only from sanitized aggregate data.
Showability is not decoration. It is how a human catches mistakes.

## The public reference points

This philosophy borrows from several public AI safety and operations frames:

- xAI's mission emphasizes first-principles reasoning and AI as a tool for
  scientific discovery: https://x.ai/company
- Anthropic's Responsible Scaling Policy frames AI governance as proportional,
  iterative, and exportable, and Claude's Constitution frames helpfulness,
  honesty, harmlessness, and human oversight as core design concerns:
  https://www.anthropic.com/responsible-scaling-policy and
  https://www.anthropic.com/constitution
- OpenAI's Preparedness Framework emphasizes measuring risks, defining thresholds,
  and publishing safeguards as capabilities change:
  https://openai.com/index/updating-our-preparedness-framework/
- Palantir's AIP and Ontology docs emphasize grounding AI in operational truth,
  permissions, workflows, and action logs:
  https://palantir.com/docs/foundry/aip/overview/ and
  https://palantir.com/docs/foundry/ontology/overview/
- The 2024 Nobel Prizes in Physics and Chemistry recognized work that underpins
  modern neural networks and AI-enabled scientific discovery:
  https://www.nobelprize.org/prizes/physics/2024/press-release/ and
  https://www.nobelprize.org/prizes/chemistry/2024/press-release/
- Stanford HAI and Fei-Fei Li's public profile keep the human-centered frame in
  view: https://hai.stanford.edu/people/fei-fei-li

These sources do not endorse this project. They provide lenses for thinking
about what an AI workspace checkup should measure.
