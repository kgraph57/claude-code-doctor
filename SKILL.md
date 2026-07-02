---
name: claude-code-doctor
description: >
  Use when the user asks to audit, diagnose, or health-check their Claude Code setup,
  wonders where their context/tokens go, or invokes /doctor. Runs a read-only audit
  across 10 domains (directory structure, dev repos, CLAUDE.md hierarchy,
  settings & permissions, skills, commands, subagents, MCP & plugins,
  automations & git, usage & disk) with parallel subagents, triages findings on an
  impact-x-effort matrix, and renders an HTML dashboard with A-E grades, red flags
  and a paste-ready action plan. Zero changes until the user approves each fix.
  Triggers: '/doctor', 'audit my claude code setup', 'setup audit', 'health check my setup',
  'claude code doctor', '環境監査', 'セットアップ監査', 'Claude Code健康診断', '設定を診断して'
---

# claude-code-doctor

A health checkup for Claude Code. The core idea: **diagnosis (read-only) and treatment
(after approval) are strictly separated.**

Write the report, dashboard and all conversation output in the user's language.

## Iron rules (override everything else)

0. **Be honest about what "read-only" is**: a prompt-level contract, not an OS
   sandbox. Tell the user so if asked, and recommend pairing with Claude Code
   permission deny rules for hard guarantees.
1. **The diagnosis phase is strictly read-only.** Never use Write / Edit / mkdir / mv /
   rm / any git-mutating command. Allowed: ls / find / du / wc / head / grep / cat /
   stat / plutil -p / git status / git log / git ls-files, plus Linux read-only
   probes such as `crontab -l`, `systemctl --user list-timers --all --no-pager`,
   `systemctl --user list-unit-files --type=timer --no-pager`, and `ss -ltnp`;
   plus the Read / Grep / Glob tools.
   On Linux, never run `rm`, `mv`, `mkdir`, `touch`, `chmod`, `chown`, `sed -i`,
   package-manager commands, `systemctl start` / `stop` / `enable` / `disable`,
   or `crontab -e`.
   On Windows, use read-only PowerShell probes such as `Get-ChildItem`,
   `Get-Content -TotalCount`, `Get-ScheduledTask`, `schtasks /Query`, and
   `git status`; never run `Set-Item`, `Remove-Item`, `New-Item`, `Move-Item`,
   `Copy-Item`, registry writes, or `schtasks /Change` / `/Delete`.
2. **The user decides.** Findings are "evidence + proposal". Fixes wait for an explicit GO.
   "Probably fine" or "might be OK" is not approval.
3. **Confirm no-go paths first.** User-designated excluded paths (personal, patient,
   secret areas) must not be read at all. Every find command carries the exclusion.
4. **Never quote secrets.** If something looks like an API key or token, report the
   path and existence only, never the value.

## Step 0: Scope confirmation

Before scanning, confirm with the user (use AskUserQuestion if available):

- Scan root: entire `~/`, or only `~/.claude` + development directories?
- No-go paths: directories that must not be touched (suggest defaults: personal
  documents, keys, patient data)
- Report destination: get write permission for exactly one output location
  (everything else stays read-only)

## Step 1: Recon (main loop, 1-2 minutes)

Grasp the size of the estate before fanning out:

```bash
ls -la ~/.claude/ && ls ~/.claude/skills | wc -l && ls ~/.claude/agents | wc -l
wc -c ~/.claude/settings.json ~/.claude/CLAUDE.md 2>/dev/null
ls ~/Library/LaunchAgents/ 2>/dev/null | head -30   # macOS only
crontab -l 2>/dev/null | head -10
```

Windows coverage is beta. If the scan is on Windows, generate a reviewable
PowerShell probe plan first:

```bash
python3 scripts/build_windows_probe_plan.py windows-probe-plan.md
```

Then ask the user to approve the no-go paths and output location before running
any PowerShell command from that plan.

Linux coverage is beta. If the scan is on Linux or WSL, generate a reviewable
shell probe plan first:

```bash
python3 scripts/build_linux_probe_plan.py linux-probe-plan.md
```

Then ask the user to approve the no-go paths and output location before running
any shell command from that plan.

Embed the counts and sizes you find into each domain prompt (agents wander less
when given concrete targets).

## Step 2: Parallel fan-out (10 domains)

Use the domain definitions in `references/domains.md` and launch read-only subagents
in parallel. Use the Workflow tool's `parallel()` if available; otherwise launch
multiple Agent tool calls in a single message.

- Prepend the **common prohibition block** (top of domains.md) to every agent
- Force structured output (the findings schema in `references/report-format.md`)
- Model routing: pin scanners to cheaper models (e.g. haiku/sonnet) explicitly.
  Synthesis and judgment stay on the main loop's stronger model. Do not let every
  subagent inherit the top-tier default — that cost leak is itself one of the most
  common findings this audit produces.

## Step 3: Synthesis (main loop)

With all agent results in hand:

1. **Verify the load-bearing claims**: re-check 2-3 pivotal findings yourself
   (ones confirmable with a single command)
2. **Impact x Effort matrix**: A = high impact x low effort (do now) / B = high x mid /
   C = high x high / D = low x low (while passing by) / E = not worth it (say so explicitly)
3. **Top 10** findings by effect on daily efficiency, safety and cost
4. **Extract decisions**: 3-5 choices only the user can make, presented as OPTION A/B
5. **Phased plan**: Phase 0 (backup, non-destructive) → 1 (stop the bleeding) →
   2 (context diet) → 3 (grooming) → 4 (heavy lifting). For destructive steps, always
   spell out the order: backup → quarantine → verify → delete later

## Step 4: Outputs

1. **Markdown report** written to the single approved location
   (state map → matrix → ideal layout → phased plan)
2. **Prescriptions (action plan)**: for every matrix-A/B item, write an `actions[]`
   entry whose `prompt` is a ready-to-paste Claude Code instruction that executes
   that one fix safely (backup → quarantine → verify baked in, ends with a report
   step). A diagnosis without an executable action plan is not a deliverable.
3. **HTML dashboard**: assemble the findings JSON and run
   `python3 scripts/build_dashboard.py findings.json out.html`
   (set `meta.lang` to `en` or `ja`), then open it in the browser
4. **Share cards (only on request)**: assemble a sanitized summary JSON and run
   `python3 scripts/build_share_cards.py cards.json outdir/` for four 16:9 PNGs

Always **verify rendering with a headless browser screenshot** before calling any
generated HTML finished.

### Sanitization rules for share cards (mandatory)

Public-facing cards may contain aggregates and generalized lessons only:

- Allowed: finding counts / always-on token totals / permission-list sizes /
  MCP tool counts / lessons learned
- Never: real paths (generic ones like `~/.claude` are fine) / personal or patient
  folder names / actual spend figures / exact locations of security gaps /
  whereabouts of account IDs or keys

## Step 5: Treatment (after approval only)

After an explicit GO ("do it", "run phase 1"), execute matrix-A items **one at a time**:

1. Back up before touching anything (settings.json / crontab / target files)
2. Execute → verify on the spot (counts, JSON validity, launchctl list, etc.) →
   report in one line
3. Never delete. Move to a quarantine folder with a MANIFEST.tsv
   (original path, reason, date) and delete weeks later

If a permission guard blocks you mid-treatment, stop and report to the user.
Do not route around it — the guard firing is evidence the setup is healthy.

## Fallback without subagents

Walk the 10 domains sequentially in the main loop (finalize each domain's findings
before moving on). Slower, but converges to the same schema and outputs.
