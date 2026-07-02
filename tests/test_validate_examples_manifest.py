import subprocess
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

import validate_examples_manifest  # noqa: E402


def valid_manifest():
    return {
        "schema": "claude-code-doctor-example-manifest-v1",
        "examples": [
            {
                "path": "samples/dashboard.json",
                "kind": "dashboard_fixture",
                "fictional": True,
                "validator": "python3 scripts/build_dashboard.py samples/dashboard.json /tmp/ccd-dashboard.html",
                "notes": "Fictional dashboard fixture.",
            },
            {
                "path": "samples/contributed-report.json",
                "kind": "contributed_report",
                "fictional": True,
                "validator": "python3 scripts/validate_contributed_report.py samples/contributed-report.json",
                "notes": "Fictional contributed report fixture.",
            },
        ],
    }


class ValidateExamplesManifestTests(unittest.TestCase):
    def test_valid_manifest_passes(self):
        problems = validate_examples_manifest.validate_manifest(valid_manifest(), ROOT)

        self.assertEqual(problems, [])

    def test_cli_accepts_repo_manifest(self):
        proc = subprocess.run(
            [
                sys.executable,
                str(ROOT / "scripts" / "validate_examples_manifest.py"),
                str(ROOT / "docs" / "examples-manifest.json"),
            ],
            text=True,
            capture_output=True,
        )

        self.assertEqual(proc.returncode, 0, proc.stderr)
        self.assertIn("OK", proc.stdout)

    def test_rejects_missing_paths_and_unapproved_validators(self):
        manifest = valid_manifest()
        manifest["examples"][0]["path"] = "samples/missing.json"
        manifest["examples"][0]["validator"] = "python3 scripts/unknown.py samples/missing.json"

        problems = validate_examples_manifest.validate_manifest(manifest, ROOT)

        self.assertTrue(any("does not exist" in problem for problem in problems))
        self.assertTrue(any("validator" in problem for problem in problems))

    def test_rejects_nonfictional_and_secret_shapes(self):
        manifest = valid_manifest()
        manifest["examples"][0]["fictional"] = False
        manifest["examples"][0]["notes"] = "Real path /Users/alice/report.html with api_key=abc123"

        problems = validate_examples_manifest.validate_manifest(manifest, ROOT)

        self.assertTrue(any("fictional" in problem for problem in problems))
        self.assertTrue(any("raw path" in problem for problem in problems))
        self.assertTrue(any("secret-shaped" in problem for problem in problems))

    def test_public_docs_reference_example_manifest_validation(self):
        readme = (ROOT / "README.md").read_text(encoding="utf-8")
        readme_ja = (ROOT / "README.ja.md").read_text(encoding="utf-8")
        workflow = (ROOT / ".github" / "workflows" / "test.yml").read_text(encoding="utf-8")
        docs = (ROOT / "docs" / "examples.md").read_text(encoding="utf-8")

        self.assertIn("Current release: **v0.13.0**", readme)
        self.assertIn("## Example Manifest", readme)
        self.assertIn("scripts/validate_examples_manifest.py docs/examples-manifest.json", readme)
        self.assertIn("現在のリリース: **v0.13.0**", readme_ja)
        self.assertIn("## サンプルマニフェスト", readme_ja)
        self.assertIn("scripts/validate_examples_manifest.py docs/examples-manifest.json", workflow)
        self.assertIn("claude-code-doctor-example-manifest-v1", docs)


if __name__ == "__main__":
    unittest.main()
