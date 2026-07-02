#!/usr/bin/env python3
"""Fail CI when a Claude Code Doctor report exceeds configured budgets.

Usage:
    python3 scripts/check_budgets.py report.json budgets.json summary.md

Budget schema:
{
  "max": {
    "always_on_tokens": 30000,
    "permissions": 500,
    "mcp_tools": 40,
    "critical_findings": 0
  }
}
"""
import json
import sys
from pathlib import Path

import compare_reports


METRIC_LABELS = {
    "always_on_tokens": "Always-on tokens",
    "permissions": "Permissions",
    "mcp_tools": "MCP tools",
    "critical_findings": "Critical findings",
}


def load_json_object(path, label):
    try:
        data = json.loads(Path(path).read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        raise ValueError(f"Invalid JSON in {path}: {exc}") from exc
    if not isinstance(data, dict):
        raise ValueError(f"{label} must be a JSON object.")
    return data


def budget_maxima(budgets):
    raw = budgets.get("max", budgets)
    if not isinstance(raw, dict):
        raise ValueError("budgets.max must be a JSON object.")
    maxima = {}
    for key in ("always_on_tokens", "permissions", "mcp_tools", "critical_findings"):
        parsed = compare_reports.parse_int(raw.get(key))
        if parsed is not None:
            maxima[key] = parsed
    return maxima


def count_critical_findings(report):
    count = len(compare_reports.extract_red_flags(report))
    for domain in report.get("domains", []) or []:
        if not isinstance(domain, dict):
            continue
        for finding in domain.get("findings", []) or []:
            if isinstance(finding, dict) and finding.get("critical"):
                count += 1
    return count


def observed_values(report):
    values = compare_reports.extract_metrics(report)
    values["critical_findings"] = count_critical_findings(report)
    return values


def check_budgets(report, budgets):
    maxima = budget_maxima(budgets)
    observed = observed_values(report)
    breaches = []
    missing = []
    for metric, maximum in maxima.items():
        actual = observed.get(metric)
        if actual is None:
            missing.append(metric)
            continue
        if actual > maximum:
            breaches.append({
                "metric": metric,
                "actual": actual,
                "max": maximum,
                "over_by": actual - maximum,
            })
    return {
        "title": report.get("meta", {}).get("title", "Claude Code Doctor report"),
        "passed": not breaches,
        "budgets": maxima,
        "observed": observed,
        "breaches": breaches,
        "missing": missing,
    }


def fmt_num(value):
    return "n/a" if value is None else f"{value:,}"


def render_markdown(result):
    status = "Passed" if result["passed"] else "Failed"
    lines = [
        f"# Claude Code Doctor Budget Gate {status}",
        "",
        f"Report: {result['title']}",
        "",
        "## Budgets",
        "",
    ]
    for metric, maximum in result["budgets"].items():
        actual = result["observed"].get(metric)
        label = METRIC_LABELS.get(metric, metric)
        state = "missing" if actual is None else ("fail" if actual > maximum else "pass")
        lines.append(f"- {label}: {fmt_num(actual)} <= {fmt_num(maximum)} [{state}]")

    lines.extend(["", "## Breaches", ""])
    if result["breaches"]:
        for breach in result["breaches"]:
            label = METRIC_LABELS.get(breach["metric"], breach["metric"])
            lines.append(
                f"- {label}: {fmt_num(breach['actual'])} > {fmt_num(breach['max'])} "
                f"(over by {fmt_num(breach['over_by'])})"
            )
    else:
        lines.append("- None")

    lines.extend(["", "## Missing Metrics", ""])
    if result["missing"]:
        for metric in result["missing"]:
            lines.append(f"- {METRIC_LABELS.get(metric, metric)}")
    else:
        lines.append("- None")
    return "\n".join(lines) + "\n"


def main(argv=None):
    argv = argv or sys.argv[1:]
    if len(argv) != 3:
        print(__doc__.strip(), file=sys.stderr)
        return 2
    try:
        report = load_json_object(argv[0], "report")
        budgets = load_json_object(argv[1], "budgets")
        result = check_budgets(report, budgets)
    except ValueError as exc:
        print(str(exc), file=sys.stderr)
        return 2

    out = Path(argv[2])
    out.write_text(render_markdown(result), encoding="utf-8")
    print(("PASSED" if result["passed"] else "FAILED") + f" {out}")
    return 0 if result["passed"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
