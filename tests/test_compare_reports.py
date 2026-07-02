import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

import compare_reports  # noqa: E402


def report(title, metrics=None, systems=None, domains=None, red_flags=None, actions=None):
    return {
        "meta": {"title": title, "date": "2026-07-02"},
        "metrics": metrics or {},
        "checkup": {"systems": systems or [], "red_flags": red_flags or []},
        "domains": domains or [],
        "actions": actions or [],
    }


class CompareReportsTests(unittest.TestCase):
    def test_compare_reports_tracks_metrics_domains_red_flags_and_findings(self):
        before = report(
            "Before",
            metrics={"always_on_tokens": 45000, "permissions": 804, "mcp_tools": 63},
            systems=[
                {"domain": "CLAUDE.md hierarchy", "grade": "C", "score": 55},
                {"domain": "Settings & permissions", "grade": "B", "score": 82},
            ],
            red_flags=["plaintext token shape in scratch note"],
            domains=[
                {
                    "name": "CLAUDE.md hierarchy",
                    "findings": [
                        {
                            "title": "Rare workflow notes load every session",
                            "severity": "high",
                        }
                    ],
                },
                {
                    "name": "Settings & permissions",
                    "findings": [{"title": "Dead allow-list entries", "severity": "medium"}],
                },
            ],
        )
        after = report(
            "After",
            metrics={"always_on_tokens": 31000, "permissions": 760, "mcp_tools": 64},
            systems=[
                {"domain": "CLAUDE.md hierarchy", "grade": "B", "score": 83},
                {"domain": "Settings & permissions", "grade": "C", "score": 60},
            ],
            red_flags=["new private file tracked by git"],
            domains=[
                {
                    "name": "Settings & permissions",
                    "findings": [
                        {"title": "Dead allow-list entries", "severity": "medium"},
                        {"title": "Private file tracked by git", "severity": "high", "critical": True},
                    ],
                }
            ],
        )

        diff = compare_reports.compare_reports(before, after)
        markdown = compare_reports.render_markdown(diff)

        self.assertEqual(diff["metrics"]["always_on_tokens"]["delta"], -14000)
        self.assertEqual(diff["metrics"]["permissions"]["delta"], -44)
        self.assertEqual(diff["metrics"]["mcp_tools"]["status"], "regressed")
        self.assertEqual(diff["domains"]["CLAUDE.md hierarchy"]["status"], "improved")
        self.assertEqual(diff["domains"]["Settings & permissions"]["status"], "regressed")
        self.assertIn("plaintext token shape in scratch note", diff["red_flags"]["resolved"])
        self.assertIn("new private file tracked by git", diff["red_flags"]["new"])
        self.assertIn("Rare workflow notes load every session", diff["findings"]["resolved"])
        self.assertIn("Private file tracked by git", diff["findings"]["new"])
        self.assertIn("Next Progress Prescription", markdown)
        self.assertIn("Always-on tokens: 45,000 -> 31,000 (-14,000)", markdown)

    def test_completed_and_new_actions_are_reported(self):
        before = report(
            "Before",
            actions=[
                {"id": "RX-01", "title": "Quarantine stale notes"},
                {"id": "RX-02", "title": "Tighten permission allow-list"},
            ],
        )
        after = report(
            "After",
            actions=[
                {"id": "RX-01", "title": "Quarantine stale notes", "done": True},
                {"id": "RX-02", "title": "Tighten permission allow-list"},
                {"id": "RX-03", "title": "Remove duplicate MCP server"},
            ],
        )

        diff = compare_reports.compare_reports(before, after)

        self.assertEqual(diff["actions"]["completed"], ["RX-01 Quarantine stale notes"])
        self.assertEqual(diff["actions"]["remaining"], ["RX-02 Tighten permission allow-list"])
        self.assertEqual(diff["actions"]["new"], ["RX-03 Remove duplicate MCP server"])

    def test_cli_writes_markdown(self):
        before = report(
            "Before",
            metrics={"always_on_tokens": 18000},
            systems=[{"domain": "Skills", "grade": "C", "score": 55}],
        )
        after = report(
            "After",
            metrics={"always_on_tokens": 12000},
            systems=[{"domain": "Skills", "grade": "B", "score": 81}],
        )

        with tempfile.TemporaryDirectory() as tmp:
            before_path = Path(tmp) / "before.json"
            after_path = Path(tmp) / "after.json"
            out_path = Path(tmp) / "diff.md"
            before_path.write_text(json.dumps(before), encoding="utf-8")
            after_path.write_text(json.dumps(after), encoding="utf-8")

            proc = subprocess.run(
                [
                    sys.executable,
                    str(ROOT / "scripts" / "compare_reports.py"),
                    str(before_path),
                    str(after_path),
                    str(out_path),
                ],
                text=True,
                capture_output=True,
            )

            self.assertEqual(proc.returncode, 0, proc.stderr)
            self.assertIn("OK", proc.stdout)
            self.assertIn("Claude Code Doctor Diff", out_path.read_text(encoding="utf-8"))

    def test_cli_rejects_non_object_json_without_traceback(self):
        with tempfile.TemporaryDirectory() as tmp:
            before_path = Path(tmp) / "before.json"
            after_path = Path(tmp) / "after.json"
            out_path = Path(tmp) / "diff.md"
            before_path.write_text("[]", encoding="utf-8")
            after_path.write_text(json.dumps(report("After")), encoding="utf-8")

            proc = subprocess.run(
                [
                    sys.executable,
                    str(ROOT / "scripts" / "compare_reports.py"),
                    str(before_path),
                    str(after_path),
                    str(out_path),
                ],
                text=True,
                capture_output=True,
            )

        self.assertEqual(proc.returncode, 1)
        self.assertIn("must be a JSON object", proc.stderr)
        self.assertNotIn("Traceback", proc.stderr)


if __name__ == "__main__":
    unittest.main()
