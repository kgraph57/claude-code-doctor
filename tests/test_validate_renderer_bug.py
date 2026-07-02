import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

import validate_renderer_bug  # noqa: E402


def valid_bug():
    return {
        "schema": "claude-code-doctor-renderer-bug-v1",
        "renderer": "dashboard",
        "doctor_version": "v0.12.0",
        "input": {
            "meta": {
                "lang": "en",
                "title": "Minimal fictional renderer bug fixture",
                "date": "2026-07-02",
            },
            "stats": [
                {"n": "1", "unit": "", "label": "fictional finding", "tone": "alert"}
            ],
        },
        "reproduction": {
            "command": "python3 scripts/build_dashboard.py /tmp/ccd-bug.json /tmp/ccd-bug.html",
            "expected": "The stat card renders inside the viewport.",
            "actual": "The stat card overflows the fixture viewport.",
            "environment": "macOS, Python 3.13, Chrome 126",
        },
        "safety": {
            "fictional_data": True,
            "no_private_paths": True,
            "no_secrets": True,
        },
    }


class ValidateRendererBugTests(unittest.TestCase):
    def test_valid_renderer_bug_passes(self):
        problems = validate_renderer_bug.validate_bug(valid_bug())

        self.assertEqual(problems, [])

    def test_cli_accepts_valid_fixture(self):
        proc = subprocess.run(
            [
                sys.executable,
                str(ROOT / "scripts" / "validate_renderer_bug.py"),
                str(ROOT / "samples" / "renderer-bug-dashboard.json"),
            ],
            text=True,
            capture_output=True,
        )

        self.assertEqual(proc.returncode, 0, proc.stderr)
        self.assertIn("OK", proc.stdout)

    def test_rejects_raw_paths_and_secret_shapes(self):
        bug = valid_bug()
        bug["reproduction"]["actual"] = "See /Users/alice/Desktop/report.html with api_key=abc123"

        problems = validate_renderer_bug.validate_bug(bug)

        self.assertTrue(any("raw path" in problem for problem in problems))
        self.assertTrue(any("secret-shaped" in problem for problem in problems))

    def test_cli_rejects_unsafe_bug_without_printing_value(self):
        bug = valid_bug()
        bug["input"]["meta"]["title"] = "Bearer abc123 from /home/alice/private"

        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "unsafe.json"
            path.write_text(json.dumps(bug), encoding="utf-8")

            proc = subprocess.run(
                [sys.executable, str(ROOT / "scripts" / "validate_renderer_bug.py"), str(path)],
                text=True,
                capture_output=True,
            )

        self.assertEqual(proc.returncode, 1)
        self.assertIn("secret-shaped", proc.stderr)
        self.assertIn("raw path", proc.stderr)
        self.assertNotIn("Bearer abc123", proc.stderr)
        self.assertNotIn("/home/alice", proc.stderr)

    def test_rejects_unknown_renderer_and_unapproved_command(self):
        bug = valid_bug()
        bug["renderer"] = "spreadsheet"
        bug["reproduction"]["command"] = "python3 scripts/unknown.py"

        problems = validate_renderer_bug.validate_bug(bug)

        self.assertTrue(any("renderer" in problem for problem in problems))
        self.assertTrue(any("command" in problem for problem in problems))

    def test_public_docs_reference_renderer_bug_validation(self):
        readme = (ROOT / "README.md").read_text(encoding="utf-8")
        readme_ja = (ROOT / "README.ja.md").read_text(encoding="utf-8")
        workflow = (ROOT / ".github" / "workflows" / "test.yml").read_text(encoding="utf-8")
        docs = (ROOT / "docs" / "renderer-bug-reports.md").read_text(encoding="utf-8")

        self.assertIn("Current release: **v0.12.0**", readme)
        self.assertIn("## Renderer Bug Reports", readme)
        self.assertIn("scripts/validate_renderer_bug.py samples/renderer-bug-dashboard.json", readme)
        self.assertIn("現在のリリース: **v0.12.0**", readme_ja)
        self.assertIn("## レンダラーバグ報告", readme_ja)
        self.assertIn("scripts/validate_renderer_bug.py samples/renderer-bug-dashboard.json", workflow)
        self.assertIn("claude-code-doctor-renderer-bug-v1", docs)


if __name__ == "__main__":
    unittest.main()
