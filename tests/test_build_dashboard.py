import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

import build_dashboard  # noqa: E402


class DashboardBuilderTests(unittest.TestCase):
    def test_cli_reports_invalid_json_without_traceback(self):
        with tempfile.TemporaryDirectory() as tmp:
            src = Path(tmp) / "broken.json"
            out = Path(tmp) / "out.html"
            src.write_text("not json{", encoding="utf-8")

            proc = subprocess.run(
                [sys.executable, str(ROOT / "scripts" / "build_dashboard.py"), str(src), str(out)],
                text=True,
                capture_output=True,
            )

        self.assertEqual(proc.returncode, 1)
        self.assertIn("Invalid JSON", proc.stderr)
        self.assertNotIn("Traceback", proc.stderr)

    def test_normalize_fills_minimal_finding_defaults(self):
        data = {
            "meta": {"lang": "en", "title": "Fixture audit"},
            "checkup": {"systems": [{"domain": "Settings & permissions"}]},
            "domains": [
                {
                    "name": "Settings & permissions",
                    "findings": [{"title": "Unscoped allow entry"}],
                }
            ],
        }

        rendered = build_dashboard.build(build_dashboard.normalize(data))

        self.assertIn("Fixture audit", rendered)
        self.assertIn("Unscoped allow entry", rendered)
        self.assertIn("impact med", rendered)
        self.assertIn("effort med", rendered)

    def test_cli_renders_minimal_dashboard_fixture(self):
        data = {
            "meta": {"lang": "en", "title": "Minimal audit"},
            "domains": [
                {
                    "name": "Skills",
                    "findings": [
                        {
                            "title": "Trigger collision",
                            "severity": "high",
                            "effort": "low",
                            "detail": "Two skills share the same trigger.",
                            "recommendation": "Rename one trigger.",
                        }
                    ],
                }
            ],
        }
        with tempfile.TemporaryDirectory() as tmp:
            src = Path(tmp) / "findings.json"
            out = Path(tmp) / "out.html"
            src.write_text(json.dumps(data), encoding="utf-8")

            proc = subprocess.run(
                [sys.executable, str(ROOT / "scripts" / "build_dashboard.py"), str(src), str(out)],
                text=True,
                capture_output=True,
            )

            self.assertEqual(proc.returncode, 0, proc.stderr)
            self.assertIn("Minimal audit", out.read_text(encoding="utf-8"))

    def test_cli_reports_non_object_root_without_traceback(self):
        with tempfile.TemporaryDirectory() as tmp:
            src = Path(tmp) / "array.json"
            out = Path(tmp) / "out.html"
            src.write_text(json.dumps([{"not": "a dashboard"}]), encoding="utf-8")

            proc = subprocess.run(
                [sys.executable, str(ROOT / "scripts" / "build_dashboard.py"), str(src), str(out)],
                text=True,
                capture_output=True,
            )

        self.assertEqual(proc.returncode, 1)
        self.assertIn("root must be a JSON object", proc.stderr)
        self.assertNotIn("Traceback", proc.stderr)

    def test_malformed_optional_sections_do_not_crash_renderer(self):
        data = {
            "meta": "not an object",
            "stats": ["not an object", {"n": "<b>5</b>", "label": "<script>x</script>"}],
            "decisions": [{"q": "Keep?", "options": ["bad", {"tag": "OPTION A", "body": "Yes"}]}],
            "matrix": ["not", "a", "dict"],
            "actions": [
                {
                    "id": "RX-1",
                    "phase": "Phase 1",
                    "title": "Unknown risk becomes safe",
                    "risk": "laser",
                    "steps": ["Back up first"],
                },
                "not an action",
            ],
            "phases": ["not a phase"],
            "trees": ["not a tree"],
            "domains": [{"name": "Skills", "findings": ["plain string finding"]}],
        }

        rendered = build_dashboard.build(build_dashboard.normalize(data))

        self.assertIn("plain string finding", rendered)
        self.assertIn("Unknown risk becomes safe", rendered)
        self.assertIn('class="chip risk safe"', rendered)
        self.assertIn("&lt;script&gt;x&lt;/script&gt;", rendered)
        self.assertNotIn("<script>x</script>", rendered)

    def test_scoring_caps_high_findings_and_critical_findings(self):
        data = {
            "meta": {"lang": "en", "title": "Strict scoring"},
            "checkup": {
                "overall": "A",
                "systems": [
                    {"domain": "High domain"},
                    {"domain": "Critical domain"},
                ],
            },
            "domains": [
                {
                    "name": "High domain",
                    "findings": [
                        {"title": "High issue", "severity": "high", "effort": "low"},
                    ],
                },
                {
                    "name": "Critical domain",
                    "findings": [
                        {
                            "title": "Secret tracked",
                            "severity": "low",
                            "effort": "low",
                            "critical": True,
                        },
                    ],
                },
            ],
        }

        normalized = build_dashboard.normalize(data)
        rendered = build_dashboard.build(normalized)

        self.assertIn('class="gbadge g-C">C</div>', rendered)
        self.assertIn('class="gbadge g-E">E</div>', rendered)
        self.assertIn('<div class="og"><b>C</b>', rendered)

    def test_dashboard_escapes_user_supplied_html(self):
        rendered = build_dashboard.build(
            build_dashboard.normalize(
                {
                    "meta": {"lang": "en", "title": "<script>alert(1)</script>"},
                    "domains": [
                        {
                            "name": "Skills",
                            "summary": "<img src=x onerror=alert(1)>",
                            "findings": [
                                {
                                    "title": "<b>Bold finding</b>",
                                    "severity": "medium",
                                    "effort": "low",
                                    "detail": "<script>steal()</script>",
                                    "recommendation": "<em>Do this</em>",
                                }
                            ],
                        }
                    ],
                }
            )
        )

        self.assertIn("&lt;script&gt;alert(1)&lt;/script&gt;", rendered)
        self.assertIn("&lt;img src=x onerror=alert(1)&gt;", rendered)
        self.assertIn("&lt;b&gt;Bold finding&lt;/b&gt;", rendered)
        self.assertNotIn("<script>alert(1)</script>", rendered)
        self.assertNotIn("<img src=x onerror=alert(1)>", rendered)


if __name__ == "__main__":
    unittest.main()
