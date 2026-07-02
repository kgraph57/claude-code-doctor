#!/usr/bin/env python3
"""Validate Claude Code Doctor community domain-pack Markdown files.

Usage:
    python3 scripts/validate_domain_pack.py domain-packs/*.md

Required pack metadata:
    id, version, languages, compatible_reports

Required per-check fields:
    Evidence, Fails when, Safety
"""
import sys
from pathlib import Path


REQUIRED_META = ("id", "version", "languages", "compatible_reports")
REQUIRED_CHECK_FIELDS = ("evidence", "fails_when", "safety")


def normalize_key(key):
    return key.strip().lower().replace(" ", "_")


def die(source, message):
    raise SystemExit(f"{source}: {message}")


def parse_csv(value):
    return [item.strip() for item in value.split(",") if item.strip()]


def parse_pack(text, source="<text>"):
    lines = text.splitlines()
    title = None
    metadata = {}
    checks = []
    current = None

    for raw in lines:
        line = raw.strip()
        if not line:
            continue
        if line.startswith("# ") and title is None:
            title = line[2:].strip()
            continue
        if line.startswith("## Check:"):
            if current:
                checks.append(current)
            current = {
                "title": line.split(":", 1)[1].strip(),
                "evidence": "",
                "fails_when": "",
                "safety": "",
            }
            continue
        if ":" not in line:
            continue
        key, value = line.split(":", 1)
        key = normalize_key(key)
        value = value.strip()
        if current is None:
            metadata[key] = value
        elif key in REQUIRED_CHECK_FIELDS:
            current[key] = value

    if current:
        checks.append(current)

    missing_meta = [key for key in REQUIRED_META if not metadata.get(key)]
    if missing_meta:
        die(source, "missing required metadata: " + ", ".join(missing_meta))
    if not checks:
        die(source, "must include at least one '## Check:' section")

    for check in checks:
        missing = [key for key in REQUIRED_CHECK_FIELDS if not check.get(key)]
        if missing:
            label = ", ".join(key.replace("_", " ").title() for key in missing)
            die(source, f"check '{check.get('title', '')}' missing required field(s): {label}")
        if "read-only" not in check["safety"].lower():
            die(source, f"check '{check['title']}' Safety must explicitly say read-only")

    return {
        "title": title or metadata["id"],
        "id": metadata["id"],
        "version": metadata["version"],
        "languages": parse_csv(metadata["languages"]),
        "compatible_reports": parse_csv(metadata["compatible_reports"]),
        "checks": checks,
    }


def main(argv=None):
    argv = argv or sys.argv[1:]
    if not argv:
        print(__doc__.strip(), file=sys.stderr)
        return 1
    ok = []
    for path in argv:
        try:
            parsed = parse_pack(Path(path).read_text(encoding="utf-8"), path)
        except OSError as exc:
            print(f"{path}: {exc}", file=sys.stderr)
            return 1
        except SystemExit as exc:
            print(str(exc), file=sys.stderr)
            return 1
        ok.append(f"OK {path} {parsed['id']} ({len(parsed['checks'])} checks)")
    print("\n".join(ok))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
