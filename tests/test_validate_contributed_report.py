import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

import validate_contributed_report  # noqa: E402


def valid_report():
    return {
        "schema": "claude-code-doctor-contributed-report-v1",
        "environment": {
            "os": "macOS",
            "harness": "Claude Code",
            "doctor_version": "v0.11.0",
            "audit_date": "2026-07-02",
        },
        "overall": {"grade": "B", "score": 72},
        "metrics": {
            "always_on_tokens": 18400,
            "permissions": 220,
            "mcp_tools": 31,
            "critical_findings": 0,
            "total_findings": 42,
        },
        "domains": [
            {"name": f"Domain {i}", "grade": "B", "score": 70 + i % 10, "finding_count": i, "red_flag_count": 0}
            for i in range(1, 11)
        ],
        "feedback": {
            "grade_felt": "about_right",
            "notes": "The score matched the cleanup priority without exposing raw paths.",
        },
    }


class ValidateContributedReportTests(unittest.TestCase):
    def test_valid_contributed_report_passes(self):
        report = valid_report()

        problems = validate_contributed_report.validate_report(report)

        self.assertEqual(problems, [])

    def test_cli_accepts_valid_fixture(self):
        proc = subprocess.run(
            [
                sys.executable,
                str(ROOT / "scripts" / "validate_contributed_report.py"),
                str(ROOT / "samples" / "contributed-report.json"),
            ],
            text=True,
            capture_output=True,
        )

        self.assertEqual(proc.returncode, 0, proc.stderr)
        self.assertIn("OK", proc.stdout)

    def test_rejects_raw_paths_and_secret_shapes(self):
        report = valid_report()
        report["feedback"]["notes"] = "Found /Users/alice/.claude/settings.json with api_key=abc123"

        problems = validate_contributed_report.validate_report(report)

        self.assertTrue(any("raw path" in problem for problem in problems))
        self.assertTrue(any("secret-shaped" in problem for problem in problems))

    def test_cli_rejects_unsafe_report_without_printing_value(self):
        report = valid_report()
        report["feedback"]["notes"] = "Bearer abc123 in /home/alice/scratch.txt"

        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "unsafe.json"
            path.write_text(json.dumps(report), encoding="utf-8")

            proc = subprocess.run(
                [sys.executable, str(ROOT / "scripts" / "validate_contributed_report.py"), str(path)],
                text=True,
                capture_output=True,
            )

        self.assertEqual(proc.returncode, 1)
        self.assertIn("secret-shaped", proc.stderr)
        self.assertNotIn("Bearer abc123", proc.stderr)
        self.assertNotIn("/home/alice", proc.stderr)

    def test_public_docs_reference_contributed_report_validation(self):
        readme = (ROOT / "README.md").read_text(encoding="utf-8")
        readme_ja = (ROOT / "README.ja.md").read_text(encoding="utf-8")
        workflow = (ROOT / ".github" / "workflows" / "test.yml").read_text(encoding="utf-8")
        docs = (ROOT / "docs" / "contributed-reports.md").read_text(encoding="utf-8")

        self.assertIn("Current release: **v0.12.0**", readme)
        self.assertIn("## Contributed Reports", readme)
        self.assertIn("scripts/validate_contributed_report.py samples/contributed-report.json", readme)
        self.assertIn("現在のリリース: **v0.12.0**", readme_ja)
        self.assertIn("## 投稿用レポート", readme_ja)
        self.assertIn("scripts/validate_contributed_report.py samples/contributed-report.json", workflow)
        self.assertIn("claude-code-doctor-contributed-report-v1", docs)


if __name__ == "__main__":
    unittest.main()
