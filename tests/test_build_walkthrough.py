import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

import build_walkthrough  # noqa: E402


class BuildWalkthroughTests(unittest.TestCase):
    def test_markdown_walkthrough_has_six_timed_beats(self):
        markdown = build_walkthrough.build_markdown()

        self.assertIn("60-Second Walkthrough", markdown)
        for beat in ["0-10s", "10-20s", "20-30s", "30-40s", "40-50s", "50-60s"]:
            self.assertIn(beat, markdown)
        self.assertIn("Diagnose first", markdown)
        self.assertIn("Treat only after consent", markdown)

    def test_html_walkthrough_is_self_contained(self):
        html = build_walkthrough.build_html()

        self.assertIn("<!doctype html>", html.lower())
        self.assertIn("Claude Code Doctor", html)
        self.assertIn("No uploads", html)
        self.assertNotIn("<script src=", html)

    def test_cli_writes_markdown_and_html(self):
        with tempfile.TemporaryDirectory() as tmp:
            outdir = Path(tmp)

            proc = subprocess.run(
                [sys.executable, str(ROOT / "scripts" / "build_walkthrough.py"), str(outdir)],
                text=True,
                capture_output=True,
            )

            self.assertEqual(proc.returncode, 0, proc.stderr)
            self.assertIn("OK", proc.stdout)
            self.assertIn("60-Second Walkthrough", (outdir / "demo-walkthrough.md").read_text(encoding="utf-8"))
            self.assertIn("Claude Code Doctor", (outdir / "demo-walkthrough.html").read_text(encoding="utf-8"))

    def test_public_docs_reference_walkthrough(self):
        readme = (ROOT / "README.md").read_text(encoding="utf-8")
        readme_ja = (ROOT / "README.ja.md").read_text(encoding="utf-8")
        workflow = (ROOT / ".github" / "workflows" / "test.yml").read_text(encoding="utf-8")

        self.assertIn("Current release: **v0.9.0**", readme)
        self.assertIn("現在のリリース: **v0.9.0**", readme_ja)
        self.assertIn("## 60-Second Walkthrough", readme)
        self.assertIn("## 60秒ウォークスルー", readme_ja)
        self.assertIn("scripts/build_walkthrough.py docs/generated-demo", workflow)
        self.assertTrue((ROOT / "docs" / "walkthrough.md").exists())


if __name__ == "__main__":
    unittest.main()
