#!/usr/bin/env python3
"""Generate a Windows read-only probe plan for Claude Code Doctor.

Usage:
    python3 scripts/build_windows_probe_plan.py out.md

This does not scan a machine. It writes a checklist of read-only PowerShell
commands that an auditor can review before running a Windows setup checkup.
"""
import sys
from pathlib import Path


DOMAINS = [
    (
        "Domain 1: Directory structure",
        [
            "Get-ChildItem -Force $env:USERPROFILE | Select-Object Name,Mode,Length,LastWriteTime",
            "Get-ChildItem -Force $env:USERPROFILE\\Desktop,$env:USERPROFILE\\Downloads -ErrorAction SilentlyContinue | Select-Object FullName,Length,LastWriteTime",
        ],
    ),
    (
        "Domain 2: Development repositories",
        [
            "Get-ChildItem -Recurse -Force -Directory -Filter .git $env:USERPROFILE\\source,$env:USERPROFILE\\dev -ErrorAction SilentlyContinue | Select-Object FullName",
            "git status --short --branch",
        ],
    ),
    (
        "Domain 3: CLAUDE.md hierarchy",
        [
            "Get-ChildItem -Recurse -Force -Filter CLAUDE.md $env:USERPROFILE -ErrorAction SilentlyContinue | Select-Object FullName,Length,LastWriteTime",
        ],
    ),
    (
        "Domain 4: Settings and permissions",
        [
            "Get-ChildItem -Force $env:APPDATA,$env:LOCALAPPDATA -ErrorAction SilentlyContinue | Select-Object FullName,Mode,LastWriteTime",
            "Get-Content -TotalCount 80 $env:APPDATA\\Claude\\settings.json -ErrorAction SilentlyContinue",
        ],
    ),
    (
        "Domain 5: Skills",
        [
            "Get-ChildItem -Recurse -Force -Filter SKILL.md $env:USERPROFILE\\.claude\\skills -ErrorAction SilentlyContinue | Select-Object FullName,Length,LastWriteTime",
        ],
    ),
    (
        "Domain 6: Commands",
        [
            "Get-ChildItem -Recurse -Force $env:USERPROFILE\\.claude\\commands -ErrorAction SilentlyContinue | Select-Object FullName,Length,LastWriteTime",
        ],
    ),
    (
        "Domain 7: Subagents",
        [
            "Get-ChildItem -Recurse -Force $env:USERPROFILE\\.claude\\agents -ErrorAction SilentlyContinue | Select-Object FullName,Length,LastWriteTime",
        ],
    ),
    (
        "Domain 8: MCP and plugins",
        [
            "Get-ChildItem -Recurse -Force $env:APPDATA,$env:LOCALAPPDATA -Include *mcp*,*plugin* -ErrorAction SilentlyContinue | Select-Object FullName,Length,LastWriteTime",
            "Get-NetTCPConnection -State Listen -ErrorAction SilentlyContinue | Select-Object LocalAddress,LocalPort,OwningProcess",
        ],
    ),
    (
        "Domain 9: Automations and git hygiene",
        [
            "Get-ScheduledTask | Select-Object TaskName,TaskPath,State",
            "schtasks /Query /FO LIST /V",
        ],
    ),
    (
        "Domain 10: Usage reality and disk hygiene",
        [
            "Get-ChildItem -Force $env:USERPROFILE\\.claude -ErrorAction SilentlyContinue | Measure-Object -Property Length -Sum",
            "Get-ChildItem -Recurse -Force $env:USERPROFILE\\.claude -ErrorAction SilentlyContinue | Sort-Object Length -Descending | Select-Object -First 30 FullName,Length,LastWriteTime",
        ],
    ),
]


def build_plan():
    lines = [
        "# Windows Read-Only Probe Plan",
        "",
        "Windows coverage is beta. Use this as a reviewable probe plan before a Windows checkup, not as a mutation script.",
        "",
        "## Boundaries",
        "",
        "- Confirm no-go paths before running any command.",
        "- Do not run Set-Item, Remove-Item, New-Item, Move-Item, Copy-Item, schtasks /Change, schtasks /Delete, or any registry write.",
        "- Do not print secrets. If a value looks secret-shaped, report only path and category.",
        "- Prefer PowerShell commands that list metadata, sizes, and dates.",
        "",
        "## Roots To Confirm",
        "",
        "- `$env:USERPROFILE`",
        "- `$env:APPDATA`",
        "- `$env:LOCALAPPDATA`",
        "- Any development root such as `$env:USERPROFILE\\source` or `$env:USERPROFILE\\dev`",
        "",
        "## Domain Probes",
        "",
    ]
    for title, commands in DOMAINS:
        lines.extend([f"### {title}", ""])
        for command in commands:
            lines.extend(["```powershell", command, "```", ""])
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
