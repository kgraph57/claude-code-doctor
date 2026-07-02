import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

import build_windows_probe_plan  # noqa: E402


class WindowsProbePlanTests(unittest.TestCase):
    def test_build_windows_probe_plan_contains_read_only_domains(self):
        markdown = build_windows_probe_plan.build_plan()

        for needle in [
            "Windows Read-Only Probe Plan",
            "PowerShell",
            "$env:USERPROFILE",
            "$env:APPDATA",
            "Get-ScheduledTask",
            "Get-ChildItem",
            "Do not run Set-Item",
            "Domain 9: Automations and git hygiene",
        ]:
            self.assertIn(needle, markdown)

    def test_cli_writes_probe_plan(self):
        with tempfile.TemporaryDirectory() as tmp:
            out = Path(tmp) / "windows.md"

            proc = subprocess.run(
                [sys.executable, str(ROOT / "scripts" / "build_windows_probe_plan.py"), str(out)],
                text=True,
                capture_output=True,
            )

            self.assertEqual(proc.returncode, 0, proc.stderr)
            self.assertIn("OK", proc.stdout)
            self.assertIn("Windows Read-Only Probe Plan", out.read_text(encoding="utf-8"))

    def test_public_docs_and_skill_name_windows_beta_boundaries(self):
        docs = (ROOT / "docs" / "windows.md").read_text(encoding="utf-8")
        skill = (ROOT / "SKILL.md").read_text(encoding="utf-8")
        domains = (ROOT / "references" / "domains.md").read_text(encoding="utf-8")
        readme = (ROOT / "README.md").read_text(encoding="utf-8")
        readme_ja = (ROOT / "README.ja.md").read_text(encoding="utf-8")

        for text in (docs, skill, domains, readme, readme_ja):
            self.assertIn("Windows", text)
        self.assertIn("Windows coverage is beta", docs)
        self.assertIn("Get-ScheduledTask", domains)
        self.assertIn("PowerShell", skill)
        self.assertIn("Current release: **v0.8.0**", readme)
        self.assertIn("現在のリリース: **v0.8.0**", readme_ja)


if __name__ == "__main__":
    unittest.main()
