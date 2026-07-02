import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

import check_budgets  # noqa: E402


def report(metrics=None, red_flags=None, domains=None):
    return {
        "meta": {"title": "Budget fixture"},
        "metrics": metrics or {},
        "checkup": {"red_flags": red_flags or []},
        "domains": domains or [],
    }


class CheckBudgetsTests(unittest.TestCase):
    def test_budget_gate_fails_when_metrics_or_critical_findings_exceed_budget(self):
        data = report(
            metrics={"always_on_tokens": 46000, "permissions": 804, "mcp_tools": 63},
            red_flags=["private key shape found"],
            domains=[
                {
                    "name": "Settings & permissions",
                    "findings": [{"title": "Secret tracked", "critical": True}],
                }
            ],
        )
        budgets = {
            "max": {
                "always_on_tokens": 30000,
                "permissions": 900,
                "mcp_tools": 60,
                "critical_findings": 0,
            }
        }

        result = check_budgets.check_budgets(data, budgets)
        markdown = check_budgets.render_markdown(result)

        self.assertFalse(result["passed"])
        self.assertEqual(
            [breach["metric"] for breach in result["breaches"]],
            ["always_on_tokens", "mcp_tools", "critical_findings"],
        )
        self.assertIn("Budget Gate Failed", markdown)
        self.assertIn("Always-on tokens: 46,000 > 30,000", markdown)

    def test_budget_gate_passes_when_present_metrics_are_under_budget(self):
        data = report(metrics={"always_on_tokens": 18000})
        budgets = {"max": {"always_on_tokens": 30000, "mcp_tools": 40}}

        result = check_budgets.check_budgets(data, budgets)

        self.assertTrue(result["passed"])
        self.assertEqual(result["breaches"], [])
        self.assertEqual(result["missing"], ["mcp_tools"])

    def test_cli_exits_nonzero_on_budget_failure_and_writes_summary(self):
        data = report(metrics={"always_on_tokens": 46000})
        budgets = {"max": {"always_on_tokens": 30000}}

        with tempfile.TemporaryDirectory() as tmp:
            report_path = Path(tmp) / "report.json"
            budget_path = Path(tmp) / "budgets.json"
            summary_path = Path(tmp) / "summary.md"
            report_path.write_text(json.dumps(data), encoding="utf-8")
            budget_path.write_text(json.dumps(budgets), encoding="utf-8")

            proc = subprocess.run(
                [
                    sys.executable,
                    str(ROOT / "scripts" / "check_budgets.py"),
                    str(report_path),
                    str(budget_path),
                    str(summary_path),
                ],
                text=True,
                capture_output=True,
            )

            self.assertEqual(proc.returncode, 1)
            self.assertIn("Budget Gate Failed", summary_path.read_text(encoding="utf-8"))
            self.assertIn("FAILED", proc.stdout)

    def test_cli_rejects_invalid_budget_json_without_traceback(self):
        with tempfile.TemporaryDirectory() as tmp:
            report_path = Path(tmp) / "report.json"
            budget_path = Path(tmp) / "budgets.json"
            summary_path = Path(tmp) / "summary.md"
            report_path.write_text(json.dumps(report()), encoding="utf-8")
            budget_path.write_text("[]", encoding="utf-8")

            proc = subprocess.run(
                [
                    sys.executable,
                    str(ROOT / "scripts" / "check_budgets.py"),
                    str(report_path),
                    str(budget_path),
                    str(summary_path),
                ],
                text=True,
                capture_output=True,
            )

        self.assertEqual(proc.returncode, 2)
        self.assertIn("budgets must be a JSON object", proc.stderr)
        self.assertNotIn("Traceback", proc.stderr)


if __name__ == "__main__":
    unittest.main()
