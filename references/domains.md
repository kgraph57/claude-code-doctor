# The 10 audit domains — what exactly gets checked

Each subagent prompt = common prohibition block + one domain definition below.
Findings must follow the schema in `report-format.md`.
Every domain lists its concrete checks so users can review (and veto) them upfront.

## Common prohibition block (prepend to every agent)

```text
You are one auditor on a Claude Code setup-audit team. Operate strictly READ-ONLY.

【Absolutely forbidden】
- Any mutating operation: Write/Edit/mkdir/mv/rm/touch/git commit etc.
  Allowed: read-only commands (ls/find/du/wc/head/grep/cat/stat/plutil -p/
  git status/log/ls-files) and the Read/Grep/Glob tools.
- User-designated no-go paths: {EXCLUDED_PATHS}. Never enter, read, or traverse
  them with find.
- Do not open personal documents or content files. File contents may be read ONLY
  for Claude Code configuration files (CLAUDE.md/SKILL.md/rules/settings/hooks/
  plist/scripts).
- If you find anything that looks like a secret, report path and existence only.
  Never quote the value.

【Output】Findings need concrete paths and evidence. Report only verified facts,
never guesses. Proposals are proposals — do not execute them.
```

## Domain 1: Directory structure (home)

Checks:
- Files parked directly in `~/` (and how long they have sat there)
- Unknown-purpose folders: one-level `ls` to identify them by name only
- Naming inconsistencies (language mix, numbering schemes, depth extremes)
- Desktop / Downloads / Documents backlog, classified by age and type
- Dead hidden dot-folders (alive or abandoned, judged by mtime)
- Size measurements (`du`, skipping cloud mounts)

## Domain 2: Development repositories

Checks:
- Every git repo: current branch / dirty count / `.git` size
  (`git count-objects -vH`) / last commit date
- Repos living outside the canonical code directory (strays)
- Nested repos and circular mirror clones
- Per-repo presence of `.github/workflows`, pre-commit hooks, project `.claude/`

## Domain 3: CLAUDE.md hierarchy

Checks:
- Inventory of every CLAUDE.md (bytes, estimated tokens, mtime); copies inside
  build artifacts are flagged as "proliferation"
- Close reading of user-global and project files: does content deserve always-on
  loading / are procedures (skill material) mixed in / duplication across levels /
  staleness of dated notes / contradictions between files
- **Total always-on token tax, as a number** (for Japanese, bytes ÷ 1.8 as a rough guide)

## Domain 4: rules / settings / permissions / hooks

Checks:
- settings.json: model and effort values vs. the user's own written policy
- permissions allow/deny/ask: counts, dead entries pointing at paths that no longer
  exist, corrupted entries, plaintext credentials, over-broad grants
- Full hook inventory (which event calls which script; do the scripts exist)
- Guardrail gaps: destructive-command blocking, secret blocking, formatters
- rules/ scoping: which rules load always vs. path-scoped, and whether that's right
- Backup-file sediment inside the config directory
- Project-level settings relying entirely on global deny lists

## Domain 5: Skills

Checks:
- Every SKILL.md description: too vague to fire / too broad (misfires) /
  trigger words colliding with other skills (build synonym clusters and cross-check)
- Body granularity: oversized single files, progressive-disclosure violations
- Broken layouts: ZIP files, loose .md files, directories missing SKILL.md
- Archive hygiene and consistency

## Domain 6: Commands (duplication with skills)

Checks:
- Full command list crossed against skill names: (a) stubs left after migration
  (b) live command-only entries (c) both-exist-but-diverged — most dangerous,
  especially same name with different behavior across scopes
- References to retired project names or nonexistent output paths
- If a sync script maintains duplicates, identify sync direction and state
  which side is safe to edit

## Domain 7: Subagents

Checks:
- Every agent definition's frontmatter: is `model` pinned? (unpinned = inherits the
  top-tier default = silent cost leak)
- Tool discipline: do reviewer/critic roles carry Write/Edit they don't need?
- Role duplication, superseded legacy teams
- Dormant agents referenced by no skill, command, or script
- Mechanical-work agents pinned to premium models

## Domain 8: MCP servers and plugins

Checks:
- Total tool count injected every session (context tax) per always-on server
- Functionally overlapping servers
- Dead configs: servers that fail to connect every session (e.g. localhost ports
  nothing listens on)
- Ghost project entries pointing at paths that no longer exist
- Plugins with zero recorded usage; integrations stuck in needs-auth for weeks

## Domain 9: Automations and git hygiene

Checks:
- launchd/cron/scheduler inventory: does every referenced script exist / zombies
  pointing at vanished paths (failing silently every day) / backup plists that could
  be accidentally re-enabled / logs growing without rotation
- Orphan scripts called by nothing
- Git: commit-convention adherence in recent history / unmerged and stale branches /
  presence of a CI net (types, lint, tests)

## Domain 10: Usage reality and disk hygiene

Checks:
- Size breakdown of the config directory (`~/.claude` etc.): transcript remains from
  old project paths / node_modules・virtualenvs・build output inside skills /
  oversized single sessions / quantified cleanup candidates

**Hard rule: never read transcript or conversation contents. du/ls/wc/dates only.**
