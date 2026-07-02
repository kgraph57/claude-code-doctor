#!/usr/bin/env python3
"""Build a 60-second Claude Code Doctor walkthrough in Markdown and HTML.

Usage:
    python3 scripts/build_walkthrough.py outdir/
"""
import html
import sys
from pathlib import Path


BEATS = [
    (
        "0-10s",
        "The hidden layer",
        "Claude Code Doctor audits the AI-workspace layer before the agent writes code.",
        "Show the 104-finding proof: context tax, dead permissions, MCP bloat, and zombie automations.",
    ),
    (
        "10-20s",
        "Safe first run",
        "Paste the read-only prompt and confirm scan scope, no-go paths, and one report destination.",
        "Diagnose first. Treat only after consent.",
    ),
    (
        "20-30s",
        "Dashboard",
        "Render the fictional fixture to preview the local dashboard without scanning a real machine.",
        "No uploads. No telemetry. Local HTML only.",
    ),
    (
        "30-40s",
        "Diff Mode",
        "Compare before and after checkups to prove what improved and what regressed.",
        "The second checkup is the point of the first one.",
    ),
    (
        "40-50s",
        "CI Budget Gate",
        "Fail a pull request when context, permissions, tools, or critical findings cross a budget.",
        "Useful teams make drift visible before it becomes normal.",
    ),
    (
        "50-60s",
        "Extend safely",
        "Validate community domain packs and adapter notes before expanding the checkup.",
        "Same protocol across Claude Code, Codex, Cursor, and Windows beta probes.",
    ),
]


def build_markdown():
    lines = [
        "# 60-Second Walkthrough",
        "",
        "A concise demo script for Claude Code Doctor. Use it as narration for a GIF, screen recording, or live walkthrough.",
        "",
    ]
    for timing, title, body, cue in BEATS:
        lines.extend([
            f"## {timing} - {title}",
            "",
            body,
            "",
            f"Visual cue: {cue}",
            "",
        ])
    lines.extend([
        "## Demo Commands",
        "",
        "```bash",
        "python3 scripts/build_dashboard.py samples/dashboard.json /tmp/claude-code-doctor-dashboard.html",
        "python3 scripts/compare_reports.py samples/diff-before.json samples/diff-after.json /tmp/claude-code-doctor-diff.md",
        "python3 scripts/check_budgets.py samples/diff-before.json samples/budgets.json /tmp/claude-code-doctor-budget.md",
        "python3 scripts/validate_domain_pack.py domain-packs/*.md",
        "python3 scripts/validate_adapter_notes.py docs/adapters/*.md",
        "python3 scripts/build_windows_probe_plan.py /tmp/claude-code-doctor-windows.md",
        "```",
        "",
    ])
    return "\n".join(lines)


def build_html():
    cards = []
    for timing, title, body, cue in BEATS:
        cards.append(
            "<section>"
            f"<p class=\"time\">{html.escape(timing)}</p>"
            f"<h2>{html.escape(title)}</h2>"
            f"<p>{html.escape(body)}</p>"
            f"<small>{html.escape(cue)}</small>"
            "</section>"
        )
    return f"""<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Claude Code Doctor 60-Second Walkthrough</title>
<style>
body{{font-family:Inter,-apple-system,BlinkMacSystemFont,"Segoe UI",sans-serif;margin:0;color:#1a1a1a;background:#fff}}
main{{max-width:980px;margin:0 auto;padding:64px 28px}}
h1{{font-size:48px;line-height:1.1;margin:0 0 12px}}
.lede{{color:#5c6166;font-size:18px;max-width:700px;line-height:1.7}}
.grid{{display:grid;grid-template-columns:repeat(2,minmax(0,1fr));gap:18px;margin-top:38px}}
section{{border:1px solid #e3e5e7;padding:24px;min-height:210px}}
.time{{font-weight:800;color:#0B7DA3;letter-spacing:.08em;margin:0 0 12px}}
h2{{font-size:24px;margin:0 0 12px}}
p{{line-height:1.65}}
small{{display:block;color:#5c6166;line-height:1.6;margin-top:18px}}
.footer{{border-top:1px solid #1a1a1a;margin-top:40px;padding-top:18px;color:#5c6166}}
@media(max-width:760px){{.grid{{grid-template-columns:1fr}}h1{{font-size:34px}}}}
</style>
</head>
<body>
<main>
<h1>Claude Code Doctor</h1>
<p class="lede">60-Second Walkthrough. Diagnose first. Treat only after consent. No uploads. No telemetry. Local reports only.</p>
<div class="grid">
{''.join(cards)}
</div>
<p class="footer">Use this page as a capture surface for a GIF, short video, or live demo.</p>
</main>
</body>
</html>
"""


def main(argv=None):
    argv = argv or sys.argv[1:]
    if len(argv) != 1:
        print(__doc__.strip(), file=sys.stderr)
        return 1
    outdir = Path(argv[0])
    outdir.mkdir(parents=True, exist_ok=True)
    md = outdir / "demo-walkthrough.md"
    html_path = outdir / "demo-walkthrough.html"
    md.write_text(build_markdown(), encoding="utf-8")
    html_path.write_text(build_html(), encoding="utf-8")
    print(f"OK {md}")
    print(f"OK {html_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
