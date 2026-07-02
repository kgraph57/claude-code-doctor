#!/usr/bin/env python3
"""Generate a Linux read-only probe plan for Claude Code Doctor.

Usage:
    python3 scripts/build_linux_probe_plan.py out.md

This does not scan a machine. It writes a checklist of read-only shell commands
that an auditor can review before running a Linux or WSL setup checkup.
"""
import sys
from pathlib import Path


DOMAINS = [
    (
        "Domain 1: Directory structure",
        [
            'ls -la "$HOME"',
            'find "$HOME/Desktop" "$HOME/Downloads" -maxdepth 2 -type f -printf "%TY-%Tm-%Td\\t%s\\t%p\\n" 2>/dev/null | head -200',
        ],
    ),
    (
        "Domain 2: Development repositories",
        [
            'find "$HOME/dev" "$HOME/Developer" "$HOME/src" -name .git -type d -prune -print 2>/dev/null',
            "git status --short --branch",
        ],
    ),
    (
        "Domain 3: CLAUDE.md hierarchy",
        [
            'find "$HOME" -path "$HOME/.cache" -prune -o -name CLAUDE.md -type f -printf "%s\\t%TY-%Tm-%Td\\t%p\\n" 2>/dev/null',
        ],
    ),
    (
        "Domain 4: Settings and permissions",
        [
            'ls -la "$HOME/.claude" "$HOME/.config" 2>/dev/null',
            'head -80 "$HOME/.claude/settings.json" 2>/dev/null',
        ],
    ),
    (
        "Domain 5: Skills",
        [
            'find "$HOME/.claude/skills" -name SKILL.md -type f -printf "%s\\t%TY-%Tm-%Td\\t%p\\n" 2>/dev/null',
        ],
    ),
    (
        "Domain 6: Commands",
        [
            'find "$HOME/.claude/commands" -type f -printf "%s\\t%TY-%Tm-%Td\\t%p\\n" 2>/dev/null',
        ],
    ),
    (
        "Domain 7: Subagents",
        [
            'find "$HOME/.claude/agents" -type f -printf "%s\\t%TY-%Tm-%Td\\t%p\\n" 2>/dev/null',
        ],
    ),
    (
        "Domain 8: MCP and plugins",
        [
            'find "$HOME/.claude" "$HOME/.config" \\( -iname "*mcp*" -o -iname "*plugin*" \\) -printf "%s\\t%TY-%Tm-%Td\\t%p\\n" 2>/dev/null',
            "ss -ltnp 2>/dev/null | head -100",
        ],
    ),
    (
        "Domain 9: Automations and git hygiene",
        [
            "crontab -l 2>/dev/null",
            "systemctl --user list-timers --all --no-pager 2>/dev/null",
            "systemctl --user list-unit-files --type=timer --no-pager 2>/dev/null",
            'ls -la "$HOME/.config/systemd/user" 2>/dev/null',
        ],
    ),
    (
        "Domain 10: Usage reality and disk hygiene",
        [
            'du -sh "$HOME/.claude" "$HOME/.config/claude-code" 2>/dev/null',
            'find "$HOME/.claude" -type f -printf "%s\\t%TY-%Tm-%Td\\t%p\\n" 2>/dev/null | sort -nr | head -30',
        ],
    ),
]


def build_plan():
    lines = [
        "# Linux Read-Only Probe Plan",
        "",
        "Linux coverage is beta. Use this as a reviewable shell probe plan before a Linux or WSL checkup, not as a mutation script.",
        "",
        "## Boundaries",
        "",
        "- Confirm no-go paths before running any command.",
        "- Apply the no-go exclusions to every `find` command before running it.",
        "- Do not run rm, mv, mkdir, touch, chmod, chown, sed -i, package-manager commands, systemctl start/stop/enable/disable, or crontab -e.",
        "- Do not print secrets. If a value looks secret-shaped, report only path and category.",
        "- Prefer shell commands that list metadata, sizes, dates, timers, and listeners.",
        "",
        "## Roots To Confirm",
        "",
        "- `$HOME`",
        "- `$HOME/.claude`",
        "- `$HOME/.config`",
        "- Any development root such as `$HOME/dev`, `$HOME/Developer`, or `$HOME/src`",
        "- Any WSL mount paths that should be excluded, such as `/mnt/c/Users/...`",
        "",
        "## Domain Probes",
        "",
    ]
    for title, commands in DOMAINS:
        lines.extend([f"### {title}", ""])
        for command in commands:
            lines.extend(["```shell", command, "```", ""])
    return "\n".join(lines).rstrip() + "\n"


def main(argv=None):
    argv = argv or sys.argv[1:]
    if len(argv) != 1:
        print(__doc__.strip(), file=sys.stderr)
        return 1
    out = Path(argv[0])
    out.write_text(build_plan(), encoding="utf-8")
    print(f"OK {out}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
