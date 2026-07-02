#!/usr/bin/env python3
"""Validate a sanitized community checkup-grade report.

Usage:
    python3 scripts/validate_contributed_report.py report.json

This validator is for public issue/PR attachments. It accepts aggregate numbers
only and rejects raw user paths, emails, and secret-shaped strings.
"""
import json
import re
import sys
from pathlib import Path


SCHEMA = "claude-code-doctor-contributed-report-v1"
GRADES = {"A", "B", "C", "D", "E"}
REQUIRED_METRICS = (
    "always_on_tokens",
    "permissions",
    "mcp_tools",
    "critical_findings",
    "total_findings",
)

RAW_PATH = re.compile(
    r"(/Users/[^/\s]+|/home/[^/\s]+|/mnt/[a-zA-Z]/Users/[^/\s]+|"
    r"[A-Za-z]:\\Users\\[^\\\s]+|/(?:private/)?var/folders/\S+)"
)
SECRET_SHAPE = re.compile(
    r"([\w.+-]+@[\w-]+\.[\w.-]+|sk-[A-Za-z0-9_-]{8,}|ghp_[A-Za-z0-9]{8,}|"
    r"github_pat_[A-Za-z0-9_]{8,}|AKIA[0-9A-Z]{12,}|api[_-]?key\s*[:=]|"
    r"secret\s*[:=]|password\s*[:=]|Bearer\s+[A-Za-z0-9])",
    re.I,
)


def is_int(value):
    return isinstance(value, int) and not isinstance(value, bool)


def valid_score(value):
    return is_int(value) and 0 <= value <= 100


def walk_strings(value, path="$"):
    if isinstance(value, dict):
        for key, child in value.items():
            yield from walk_strings(child, f"{path}.{key}")
    elif isinstance(value, list):
        for index, child in enumerate(value):
            yield from walk_strings(child, f"{path}[{index}]")
    elif isinstance(value, str):
        yield path, value


def validate_environment(environment, problems):
    if not isinstance(environment, dict):
        problems.append("$.environment: must be an object")
        return
    for key in ("os", "harness", "doctor_version", "audit_date"):
        if not isinstance(environment.get(key), str) or not environment.get(key).strip():
            problems.append(f"$.environment.{key}: required non-empty string")
    if environment.get("os") not in {"macOS", "Linux", "Windows", "Mixed / other"}:
        problems.append("$.environment.os: must be macOS, Linux, Windows, or Mixed / other")
    if environment.get("harness") not in {"Claude Code", "Codex", "Cursor", "OpenCode", "Other"}:
        problems.append("$.environment.harness: must name a supported harness or Other")
    if not re.match(r"^v\d+\.\d+\.\d+$", str(environment.get("doctor_version", ""))):
        problems.append("$.environment.doctor_version: must look like v0.11.0")
    if not re.match(r"^\d{4}-\d{2}-\d{2}$", str(environment.get("audit_date", ""))):
        problems.append("$.environment.audit_date: must be YYYY-MM-DD")


def validate_overall(overall, problems):
    if not isinstance(overall, dict):
        problems.append("$.overall: must be an object")
        return
    if overall.get("grade") not in GRADES:
        problems.append("$.overall.grade: must be A, B, C, D, E")
    if not valid_score(overall.get("score")):
        problems.append("$.overall.score: must be an integer from 0 to 100")


def validate_metrics(metrics, problems):
    if not isinstance(metrics, dict):
        problems.append("$.metrics: must be an object")
        return
    for key in REQUIRED_METRICS:
        value = metrics.get(key)
        if not is_int(value) or value < 0:
            problems.append(f"$.metrics.{key}: must be a non-negative integer")


def validate_domains(domains, problems):
    if not isinstance(domains, list):
        problems.append("$.domains: must be an array")
        return
    if len(domains) != 10:
        problems.append("$.domains: must contain exactly 10 domain summaries")
    for index, domain in enumerate(domains):
        loc = f"$.domains[{index}]"
        if not isinstance(domain, dict):
            problems.append(f"{loc}: must be an object")
            continue
        if not isinstance(domain.get("name"), str) or not domain.get("name").strip():
            problems.append(f"{loc}.name: required non-empty string")
        if domain.get("grade") not in GRADES:
            problems.append(f"{loc}.grade: must be A, B, C, D, E")
        if not valid_score(domain.get("score")):
            problems.append(f"{loc}.score: must be an integer from 0 to 100")
        for key in ("finding_count", "red_flag_count"):
            value = domain.get(key)
            if not is_int(value) or value < 0:
                problems.append(f"{loc}.{key}: must be a non-negative integer")


def validate_public_safety(report, problems):
    for path, value in walk_strings(report):
        if RAW_PATH.search(value):
            problems.append(f"{path}: raw path-like value is not allowed in contributed reports")
        if SECRET_SHAPE.search(value):
            problems.append(f"{path}: secret-shaped value is not allowed in contributed reports")


def validate_report(report):
    problems = []
    if not isinstance(report, dict):
        return ["$: report must be a JSON object"]
    if report.get("schema") != SCHEMA:
        problems.append(f"$.schema: must be {SCHEMA}")
    validate_environment(report.get("environment"), problems)
    validate_overall(report.get("overall"), problems)
    validate_metrics(report.get("metrics"), problems)
    validate_domains(report.get("domains"), problems)
    feedback = report.get("feedback", {})
    if feedback is not None and not isinstance(feedback, dict):
        problems.append("$.feedback: must be an object when present")
    validate_public_safety(report, problems)
    return problems


def load_json_object(path):
    try:
        data = json.loads(Path(path).read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        raise ValueError(f"Invalid JSON in {path}: {exc}") from exc
    if not isinstance(data, dict):
        raise ValueError("report must be a JSON object")
    return data


def main(argv=None):
    argv = argv or sys.argv[1:]
    if len(argv) != 1:
        print(__doc__.strip(), file=sys.stderr)
        return 2
    try:
        report = load_json_object(argv[0])
    except ValueError as exc:
        print(str(exc), file=sys.stderr)
        return 2
    problems = validate_report(report)
    if problems:
        for problem in problems:
            print(f"ERROR {problem}", file=sys.stderr)
        return 1
    print(f"OK {argv[0]}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
