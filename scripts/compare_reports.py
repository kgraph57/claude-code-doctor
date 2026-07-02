#!/usr/bin/env python3
"""Compare two Claude Code Doctor dashboard JSON reports.

Usage:
    python3 scripts/compare_reports.py before.json after.json diff.md

The output is a Markdown progress report: metric deltas, domain grade changes,
red-flag movement, finding movement, and prescription progress.
"""
import json
import re
import sys
from pathlib import Path


GRADE_RANK = {"A": 5, "B": 4, "C": 3, "D": 2, "E": 1}
LOWER_IS_BETTER_METRICS = ("always_on_tokens", "permissions", "mcp_tools")
METRIC_LABELS = {
    "always_on_tokens": "Always-on tokens",
    "permissions": "Permissions",
    "mcp_tools": "MCP tools",
}


def load_report(path):
    try:
        data = json.loads(Path(path).read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        sys.exit(f"Invalid JSON in {path}: {exc}")
    if not isinstance(data, dict):
        sys.exit(f"{path} must be a JSON object.")
    return data


def parse_int(value):
    if value is None:
        return None
    text = str(value)
    match = re.search(r"-?\d[\d,]*", text)
    if not match:
        return None
    try:
        return int(match.group(0).replace(",", ""))
    except ValueError:
        return None


def metric_key(label):
    text = str(label or "").lower()
    if "always" in text or "context" in text or "token" in text:
        return "always_on_tokens"
    if "permission" in text or "allow" in text:
        return "permissions"
    if "mcp" in text or "tool" in text:
        return "mcp_tools"
    return None


def extract_metrics(report):
    metrics = {}
    raw = report.get("metrics")
    if isinstance(raw, dict):
        for key in LOWER_IS_BETTER_METRICS:
            parsed = parse_int(raw.get(key))
            if parsed is not None:
                metrics[key] = parsed
    for stat in report.get("stats", []) or []:
        if not isinstance(stat, dict):
            continue
        key = metric_key(stat.get("label"))
        parsed = parse_int(stat.get("n"))
        if key and parsed is not None and key not in metrics:
            metrics[key] = parsed
    return metrics


def extract_domains(report):
    domains = {}
    systems = report.get("checkup", {}).get("systems", []) or []
    for system in systems:
        if not isinstance(system, dict):
            continue
        name = str(system.get("domain") or system.get("short") or "").strip()
        if not name:
            continue
        score = parse_int(system.get("score"))
        grade = system.get("grade")
        domains[name] = {
            "name": name,
            "score": score,
            "grade": grade if grade in GRADE_RANK else None,
        }
    return domains


def extract_red_flags(report):
    red_flags = report.get("checkup", {}).get("red_flags", []) or []
    return {str(flag).strip() for flag in red_flags if str(flag).strip()}


def extract_findings(report):
    findings = set()
    for domain in report.get("domains", []) or []:
        if not isinstance(domain, dict):
            continue
        for finding in domain.get("findings", []) or []:
            if not isinstance(finding, dict):
                title = str(finding).strip()
            else:
                title = str(finding.get("title") or "").strip()
            if title:
                findings.add(title)
    return findings


def action_key(action):
    return str(action.get("id") or action.get("title") or "").strip()


def action_label(action):
    action_id = str(action.get("id") or "").strip()
    title = str(action.get("title") or "").strip()
    return " ".join(part for part in (action_id, title) if part)


def action_done(action):
    status = str(action.get("status") or "").lower()
    return bool(action.get("done") or action.get("completed") or status in {"done", "complete", "completed"})


def extract_actions(report):
    actions = {}
    for action in report.get("actions", []) or []:
        if not isinstance(action, dict):
            continue
        key = action_key(action)
        if key:
            actions[key] = {"label": action_label(action), "done": action_done(action)}
    return actions


def status_from_delta(delta, lower_is_better=False):
    if delta is None:
        return "unchanged"
    if delta == 0:
        return "unchanged"
    improved = delta < 0 if lower_is_better else delta > 0
    return "improved" if improved else "regressed"


def compare_metrics(before, after):
    old = extract_metrics(before)
    new = extract_metrics(after)
    out = {}
    for key in LOWER_IS_BETTER_METRICS:
        before_value = old.get(key)
        after_value = new.get(key)
        if before_value is None and after_value is None:
            continue
        delta = None if before_value is None or after_value is None else after_value - before_value
        out[key] = {
            "before": before_value,
            "after": after_value,
            "delta": delta,
            "status": status_from_delta(delta, lower_is_better=True),
        }
    return out


def compare_domains(before, after):
    old = extract_domains(before)
    new = extract_domains(after)
    out = {}
    for name in sorted(set(old) | set(new)):
        before_domain = old.get(name)
        after_domain = new.get(name)
        if before_domain is None:
            status = "new"
            delta = None
        elif after_domain is None:
            status = "removed"
            delta = None
        else:
            before_score = before_domain.get("score")
            after_score = after_domain.get("score")
            if before_score is not None and after_score is not None:
                delta = after_score - before_score
                status = status_from_delta(delta)
            else:
                delta = None
                before_grade = before_domain.get("grade")
                after_grade = after_domain.get("grade")
                grade_delta = (
                    GRADE_RANK.get(after_grade, 0) - GRADE_RANK.get(before_grade, 0)
                    if before_grade and after_grade else 0
                )
                status = status_from_delta(grade_delta)
        out[name] = {
            "before": before_domain,
            "after": after_domain,
            "delta": delta,
            "status": status,
        }
    return out


def compare_actions(before, after):
    old = extract_actions(before)
    new = extract_actions(after)
    completed = []
    remaining = []
    created = []
    for key, action in sorted(new.items()):
        if key not in old:
            created.append(action["label"])
        elif action["done"]:
            completed.append(action["label"])
        else:
            remaining.append(action["label"])
    return {"completed": completed, "remaining": remaining, "new": created}


def compare_reports(before, after):
    old_flags = extract_red_flags(before)
    new_flags = extract_red_flags(after)
    old_findings = extract_findings(before)
    new_findings = extract_findings(after)
    domains = compare_domains(before, after)
    return {
        "before_title": before.get("meta", {}).get("title", "before"),
        "after_title": after.get("meta", {}).get("title", "after"),
        "metrics": compare_metrics(before, after),
        "domains": domains,
        "red_flags": {
            "resolved": sorted(old_flags - new_flags),
            "new": sorted(new_flags - old_flags),
            "unchanged": sorted(old_flags & new_flags),
        },
        "findings": {
            "resolved": sorted(old_findings - new_findings),
            "new": sorted(new_findings - old_findings),
            "unchanged": sorted(old_findings & new_findings),
        },
        "actions": compare_actions(before, after),
    }


def fmt_num(value):
    return "n/a" if value is None else f"{value:,}"


def fmt_delta(delta):
    if delta is None:
        return "n/a"
    sign = "+" if delta > 0 else ""
    return f"{sign}{delta:,}"


def bullet_lines(values):
    return [f"- {value}" for value in values] if values else ["- None"]


def render_markdown(diff):
    lines = [
        "# Claude Code Doctor Diff",
        "",
        f"Before: {diff['before_title']}",
        f"After: {diff['after_title']}",
        "",
        "## Metric Deltas",
        "",
    ]
    if diff["metrics"]:
        for key, item in diff["metrics"].items():
            label = METRIC_LABELS[key]
            lines.append(
                f"- {label}: {fmt_num(item['before'])} -> {fmt_num(item['after'])} "
                f"({fmt_delta(item['delta'])}) [{item['status']}]"
            )
    else:
        lines.append("- No comparable metric fields found.")

    lines.extend(["", "## Domain Deltas", ""])
    if diff["domains"]:
        for name, item in diff["domains"].items():
            before = item["before"] or {}
            after = item["after"] or {}
            before_label = f"{before.get('grade') or 'n/a'} {fmt_num(before.get('score'))}"
            after_label = f"{after.get('grade') or 'n/a'} {fmt_num(after.get('score'))}"
            lines.append(
                f"- {name}: {before_label} -> {after_label} "
                f"({fmt_delta(item['delta'])}) [{item['status']}]"
            )
    else:
        lines.append("- No comparable domains found.")

    lines.extend(["", "## Red Flag Deltas", "", "### New"])
    lines.extend(bullet_lines(diff["red_flags"]["new"]))
    lines.extend(["", "### Resolved"])
    lines.extend(bullet_lines(diff["red_flags"]["resolved"]))
    lines.extend(["", "### Unchanged"])
    lines.extend(bullet_lines(diff["red_flags"]["unchanged"]))

    lines.extend(["", "## Finding Deltas", "", "### New"])
    lines.extend(bullet_lines(diff["findings"]["new"]))
    lines.extend(["", "### Resolved"])
    lines.extend(bullet_lines(diff["findings"]["resolved"]))
    lines.extend(["", "### Unchanged"])
    lines.extend(bullet_lines(diff["findings"]["unchanged"]))

    lines.extend(["", "## Prescription Progress", "", "### Completed"])
    lines.extend(bullet_lines(diff["actions"]["completed"]))
    lines.extend(["", "### Remaining"])
    lines.extend(bullet_lines(diff["actions"]["remaining"]))
    lines.extend(["", "### New"])
    lines.extend(bullet_lines(diff["actions"]["new"]))

    lines.extend(["", "## Next Progress Prescription", ""])
    regressions = [
        name for name, item in diff["domains"].items()
        if item["status"] in {"regressed", "new"}
    ]
    if diff["red_flags"]["new"]:
        lines.append("- Treat new red flags before optimizing token or tool budgets.")
    if regressions:
        lines.append("- Re-check regressed domains: " + ", ".join(regressions[:5]) + ".")
    if diff["findings"]["new"]:
        lines.append("- Triage new findings before running any cleanup prompt.")
    if not diff["red_flags"]["new"] and not regressions and not diff["findings"]["new"]:
        lines.append("- No new regressions found. Keep the monthly checkup cadence.")
    return "\n".join(lines) + "\n"


def main(argv=None):
    argv = argv or sys.argv[1:]
    if len(argv) != 3:
        print(__doc__.strip(), file=sys.stderr)
        return 1
    before = load_report(argv[0])
    after = load_report(argv[1])
    out = Path(argv[2])
    out.write_text(render_markdown(compare_reports(before, after)), encoding="utf-8")
    print(f"OK {out}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
