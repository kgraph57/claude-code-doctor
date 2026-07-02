#!/usr/bin/env python3
"""Validate cross-harness adapter notes.

Usage:
    python3 scripts/validate_adapter_notes.py docs/adapters/*.md

Required metadata:
    harness, status, report_schema

Required sections:
    Scope, No-Go Paths, Permission Boundary, Evidence Export, Known Gaps
"""
import sys
from pathlib import Path


REQUIRED_META = ("harness", "status", "report_schema")
REQUIRED_SECTIONS = (
    "Scope",
    "No-Go Paths",
    "Permission Boundary",
    "Evidence Export",
    "Known Gaps",
)


def normalize_key(key):
    return key.strip().lower().replace(" ", "_")


def die(source, message):
    raise SystemExit(f"{source}: {message}")


def parse_adapter(text, source="<text>"):
    metadata = {}
    sections = {}
    current = None
    for raw in text.splitlines():
        line = raw.strip()
        if not line:
            continue
        if line.startswith("## "):
            current = line[3:].strip()
            sections[current] = []
            continue
        if current:
            sections[current].append(line)
            continue
        if ":" in line and not line.startswith("#"):
            key, value = line.split(":", 1)
            metadata[normalize_key(key)] = value.strip()

    missing_meta = [key for key in REQUIRED_META if not metadata.get(key)]
    if missing_meta:
        die(source, "missing required metadata: " + ", ".join(missing_meta))

    missing_sections = [
        section for section in REQUIRED_SECTIONS
        if not sections.get(section) or not " ".join(sections[section]).strip()
    ]
    if missing_sections:
        die(source, "missing required section(s): " + ", ".join(missing_sections))

    boundary = " ".join(sections["Permission Boundary"]).lower()
    if "do not route around" not in boundary and "never route around" not in boundary:
        die(source, "Permission Boundary must forbid routing around guards")

    return {
        "harness": metadata["harness"],
        "status": metadata["status"],
        "report_schema": metadata["report_schema"],
        "sections": sections,
    }


def main(argv=None):
    argv = argv or sys.argv[1:]
    if not argv:
        print(__doc__.strip(), file=sys.stderr)
        return 1
    ok = []
    for path in argv:
        try:
            parsed = parse_adapter(Path(path).read_text(encoding="utf-8"), path)
        except OSError as exc:
            print(f"{path}: {exc}", file=sys.stderr)
            return 1
        except SystemExit as exc:
            print(str(exc), file=sys.stderr)
            return 1
        ok.append(f"OK {path} {parsed['harness']} ({parsed['status']})")
    print("\n".join(ok))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
