import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

import build_linux_probe_plan  # noqa: E402


class LinuxProbePlanTests(unittest.TestCase):
    def test_build_linux_probe_plan_contains_read_only_domains(self):
        markdown = build_linux_probe_plan.build_plan()

        for needle in [
            "Linux Read-Only Probe Plan",
            "shell",
            "$HOME",
            "crontab -l",
            "systemctl --user list-timers",
            "ss -ltnp",
            "Do not run rm",
            "Domain 9: Automations and git hygiene",
        ]:
            self.assertIn(needle, markdown)

    def test_cli_writes_probe_plan(self):
        with tempfile.TemporaryDirectory() as tmp:
            out = Path(tmp) / "linux.md"

            proc = subprocess.run(
                [sys.executable, str(ROOT / "scripts" / "build_linux_probe_plan.py"), str(out)],
                text=True,
                capture_output=True,
            )

            self.assertEqual(proc.returncode, 0, proc.stderr)
            self.assertIn("OK", proc.stdout)
            self.assertIn("Linux Read-Only Probe Plan", out.read_text(encoding="utf-8"))

    def test_public_docs_and_skill_name_linux_beta_boundaries(self):
        docs = (ROOT / "docs" / "linux.md").read_text(encoding="utf-8")
        skill = (ROOT / "SKILL.md").read_text(encoding="utf-8")
        domains = (ROOT / "references" / "domains.md").read_text(encoding="utf-8")
        readme = (ROOT / "README.md").read_text(encoding="utf-8")
        readme_ja = (ROOT / "README.ja.md").read_text(encoding="utf-8")
        workflow = (ROOT / ".github" / "workflows" / "test.yml").read_text(encoding="utf-8")

        for text in (docs, skill, domains, readme, readme_ja):
            self.assertIn("Linux", text)
        self.assertIn("Linux coverage is beta", docs)
        self.assertIn("systemctl --user list-timers", domains)
        self.assertIn("crontab -l", skill)
        self.assertIn("Current release: **v0.10.0**", readme)
        self.assertIn("Linux beta probe plan", readme)
        self.assertIn("現在のリリース: **v0.10.0**", readme_ja)
        self.assertIn("Linux beta probe plan", readme_ja)
        self.assertIn("scripts/build_linux_probe_plan.py /tmp/claude-code-doctor-linux.md", workflow)


if __name__ == "__main__":
    unittest.main()
