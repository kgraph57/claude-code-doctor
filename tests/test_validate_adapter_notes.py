import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

import validate_adapter_notes  # noqa: E402


VALID_ADAPTER = """# Claude Code Adapter

harness: claude-code
status: supported
report_schema: dashboard-json-v1

## Scope

Use Claude Code skills, commands, settings, MCP tools, subagents, transcripts, and local automation evidence.

## No-Go Paths

Confirm personal, credential, patient, and customer-data exclusions before scanning.

## Permission Boundary

Treat permission-denied probes as findings. Do not route around a deny rule.

## Evidence Export

Export dashboard JSON with metrics, checkup systems, red flags, domains, findings, and actions.

## Known Gaps

Windows-specific checks need separate coverage.
"""


class ValidateAdapterNotesTests(unittest.TestCase):
    def test_valid_adapter_note_parses_metadata_and_sections(self):
        parsed = validate_adapter_notes.parse_adapter(VALID_ADAPTER, "claude-code.md")

        self.assertEqual(parsed["harness"], "claude-code")
        self.assertEqual(parsed["status"], "supported")
        self.assertIn("Permission Boundary", parsed["sections"])

    def test_missing_permission_boundary_is_invalid(self):
        text = VALID_ADAPTER.replace("## Permission Boundary\n\nTreat permission-denied probes as findings. Do not route around a deny rule.\n\n", "")

        with self.assertRaises(SystemExit) as raised:
            validate_adapter_notes.parse_adapter(text, "broken.md")

        self.assertIn("Permission Boundary", str(raised.exception))

    def test_cli_validates_all_adapter_notes(self):
        paths = sorted((ROOT / "docs" / "adapters").glob("*.md"))
        self.assertGreaterEqual(len(paths), 4)

        proc = subprocess.run(
            [sys.executable, str(ROOT / "scripts" / "validate_adapter_notes.py"), *map(str, paths)],
            text=True,
            capture_output=True,
        )

        self.assertEqual(proc.returncode, 0, proc.stderr)
        self.assertIn("OK", proc.stdout)
        self.assertIn("claude-code", proc.stdout)

    def test_cli_rejects_broken_adapter_without_traceback(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "broken.md"
            path.write_text("# Broken\n\nharness: broken\nstatus: draft\n", encoding="utf-8")

            proc = subprocess.run(
                [sys.executable, str(ROOT / "scripts" / "validate_adapter_notes.py"), str(path)],
                text=True,
                capture_output=True,
            )

        self.assertEqual(proc.returncode, 1)
        self.assertIn("missing required metadata", proc.stderr)
        self.assertNotIn("Traceback", proc.stderr)


if __name__ == "__main__":
    unittest.main()
