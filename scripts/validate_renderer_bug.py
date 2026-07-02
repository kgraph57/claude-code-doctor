#!/usr/bin/env python3
"""Validate a sanitized renderer bug reproduction fixture.

Usage:
    python3 scripts/validate_renderer_bug.py bug.json

This validator is for public bug reports. It accepts minimal fictional dashboard
or share-card inputs and rejects raw user paths, emails, and secret-shaped text.
"""
import json
import re
import sys
from pathlib import Path


SCHEMA = "claude-code-doctor-renderer-bug-v1"
RENDERERS = {
    "dashboard": "scripts/build_dashboard.py",
    "share_cards": "scripts/build_share_cards.py",
}

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


def validate_reproduction(renderer, reproduction, problems):
    if not isinstance(reproduction, dict):
        problems.append("$.reproduction: must be an object")
        return
    command = reproduction.get("command")
    if not isinstance(command, str) or not command.strip():
        problems.append("$.reproduction.command: required non-empty string")
    else:
        expected_script = RENDERERS.get(renderer)
        if not expected_script or expected_script not in command:
            problems.append("$.reproduction.command: must use the matching supported renderer script")
    for key in ("expected", "actual", "environment"):
        if not isinstance(reproduction.get(key), str) or not reproduction.get(key).strip():
            problems.append(f"$.reproduction.{key}: required non-empty string")


def validate_safety(safety, problems):
    if not isinstance(safety, dict):
        problems.append("$.safety: must be an object")
        return
    for key in ("fictional_data", "no_private_paths", "no_secrets"):
        if safety.get(key) is not True:
            problems.append(f"$.safety.{key}: must be true")


def validate_input(renderer, renderer_input, problems):
    if not isinstance(renderer_input, dict):
        problems.append("$.input: must be an object")
        return
    if renderer == "dashboard":
        meta = renderer_input.get("meta")
        if not isinstance(meta, dict):
            problems.append("$.input.meta: dashboard fixture must include meta object")
        elif not isinstance(meta.get("title"), str) or not meta.get("title").strip():
            problems.append("$.input.meta.title: required non-empty string")
    elif renderer == "share_cards":
        if not any(key in renderer_input for key in ("hero", "numbers", "lessons", "howto")):
            problems.append("$.input: share_cards fixture must include at least one card section")


def validate_public_safety(bug, problems):
    for path, value in walk_strings(bug):
        if RAW_PATH.search(value):
            problems.append(f"{path}: raw path-like value is not allowed in renderer bug reports")
        if SECRET_SHAPE.search(value):
            problems.append(f"{path}: secret-shaped value is not allowed in renderer bug reports")


def validate_bug(bug):
    problems = []
    if not isinstance(bug, dict):
        return ["$: bug report must be a JSON object"]
    if bug.get("schema") != SCHEMA:
        problems.append(f"$.schema: must be {SCHEMA}")
    renderer = bug.get("renderer")
    if renderer not in RENDERERS:
        problems.append("$.renderer: must be dashboard or share_cards")
    version = bug.get("doctor_version")
    if not isinstance(version, str) or not re.match(r"^v\d+\.\d+\.\d+$", version):
        problems.append("$.doctor_version: must look like v0.12.0")
    validate_input(renderer, bug.get("input"), problems)
    validate_reproduction(renderer, bug.get("reproduction"), problems)
    validate_safety(bug.get("safety"), problems)
    validate_public_safety(bug, problems)
    return problems


def load_json_object(path):
    try:
        data = json.loads(Path(path).read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        raise ValueError(f"Invalid JSON in {path}: {exc}") from exc
    if not isinstance(data, dict):
        raise ValueError("bug report must be a JSON object")
    return data


def main(argv=None):
    argv = argv or sys.argv[1:]
    if len(argv) != 1:
        print(__doc__.strip(), file=sys.stderr)
        return 2
    try:
        bug = load_json_object(argv[0])
    except ValueError as exc:
        print(str(exc), file=sys.stderr)
        return 2
    problems = validate_bug(bug)
    if problems:
        for problem in problems:
            print(f"ERROR {problem}", file=sys.stderr)
        return 1
    print(f"OK {argv[0]}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
