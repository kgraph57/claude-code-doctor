#!/usr/bin/env python3
"""Validate the public example manifest.

Usage:
    python3 scripts/validate_examples_manifest.py docs/examples-manifest.json

The manifest keeps public examples honest: every advertised example must exist,
be marked fictional, and name a supported validator or renderer command.
"""
import json
import re
import sys
from pathlib import Path


SCHEMA = "claude-code-doctor-example-manifest-v1"
ALLOWED_KINDS = {
    "dashboard_fixture",
    "share_cards_fixture",
    "diff_fixture",
    "budget_fixture",
    "contributed_report",
    "renderer_bug",
    "walkthrough",
    "probe_plan",
}
ALLOWED_COMMAND_FRAGMENTS = (
    "scripts/build_dashboard.py",
    "scripts/build_share_cards.py",
    "scripts/compare_reports.py",
    "scripts/check_budgets.py",
    "scripts/validate_contributed_report.py",
    "scripts/validate_renderer_bug.py",
    "scripts/build_walkthrough.py",
    "scripts/build_windows_probe_plan.py",
    "scripts/build_linux_probe_plan.py",
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


def walk_strings(value, path="$"):
    if isinstance(value, dict):
        for key, child in value.items():
            yield from walk_strings(child, f"{path}.{key}")
    elif isinstance(value, list):
        for index, child in enumerate(value):
            yield from walk_strings(child, f"{path}[{index}]")
    elif isinstance(value, str):
        yield path, value


def repo_root_for(manifest_path):
    path = Path(manifest_path).resolve()
    return path.parents[1] if path.parent.name == "docs" else Path.cwd()


def validate_public_safety(manifest, problems):
    for path, value in walk_strings(manifest):
        if RAW_PATH.search(value):
            problems.append(f"{path}: raw path-like value is not allowed in example manifests")
        if SECRET_SHAPE.search(value):
            problems.append(f"{path}: secret-shaped value is not allowed in example manifests")


def validate_example(example, index, root, seen, problems):
    loc = f"$.examples[{index}]"
    if not isinstance(example, dict):
        problems.append(f"{loc}: must be an object")
        return
    path = example.get("path")
    if not isinstance(path, str) or not path.strip():
        problems.append(f"{loc}.path: required non-empty string")
    else:
        if path.startswith("/") or ".." in Path(path).parts:
            problems.append(f"{loc}.path: must be a repo-relative path without '..'")
        elif not (root / path).exists():
            problems.append(f"{loc}.path: {path} does not exist")
        if path in seen:
            problems.append(f"{loc}.path: duplicate example path {path}")
        seen.add(path)
    if example.get("kind") not in ALLOWED_KINDS:
        problems.append(f"{loc}.kind: must be one of {', '.join(sorted(ALLOWED_KINDS))}")
    if example.get("fictional") is not True:
        problems.append(f"{loc}.fictional: must be true")
    validator = example.get("validator")
    if not isinstance(validator, str) or not validator.strip():
        problems.append(f"{loc}.validator: required non-empty string")
    elif not any(fragment in validator for fragment in ALLOWED_COMMAND_FRAGMENTS):
        problems.append(f"{loc}.validator: must use a supported validator or renderer command")
    notes = example.get("notes")
    if notes is not None and not isinstance(notes, str):
        problems.append(f"{loc}.notes: must be a string when present")


def validate_manifest(manifest, root):
    problems = []
    if not isinstance(manifest, dict):
        return ["$: manifest must be a JSON object"]
    if manifest.get("schema") != SCHEMA:
        problems.append(f"$.schema: must be {SCHEMA}")
    examples = manifest.get("examples")
    if not isinstance(examples, list) or not examples:
        problems.append("$.examples: must be a non-empty array")
    else:
        seen = set()
        for index, example in enumerate(examples):
            validate_example(example, index, Path(root), seen, problems)
    validate_public_safety(manifest, problems)
    return problems


def load_json_object(path):
    try:
        data = json.loads(Path(path).read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        raise ValueError(f"Invalid JSON in {path}: {exc}") from exc
    if not isinstance(data, dict):
        raise ValueError("manifest must be a JSON object")
    return data


def main(argv=None):
    argv = argv or sys.argv[1:]
    if len(argv) != 1:
        print(__doc__.strip(), file=sys.stderr)
        return 2
    try:
        manifest = load_json_object(argv[0])
    except ValueError as exc:
        print(str(exc), file=sys.stderr)
        return 2
    problems = validate_manifest(manifest, repo_root_for(argv[0]))
    if problems:
        for problem in problems:
            print(f"ERROR {problem}", file=sys.stderr)
        return 1
    print(f"OK {argv[0]}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
