import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

import validate_domain_pack  # noqa: E402


VALID_PACK = """# Security Team Pack

id: security-team
version: 1
languages: en, ja
compatible_reports: dashboard-json-v1

## Check: Plaintext secret shapes

Evidence: Search configured settings and skill files for secret-shaped strings without printing the matched secret.
Fails when: A secret-shaped string is found outside a documented test fixture.
Safety: Read-only search only; redact values and report path plus category.
"""


class ValidateDomainPackTests(unittest.TestCase):
    def test_valid_domain_pack_returns_checks_and_metadata(self):
        parsed = validate_domain_pack.parse_pack(VALID_PACK, "security-team.md")

        self.assertEqual(parsed["id"], "security-team")
        self.assertEqual(parsed["languages"], ["en", "ja"])
        self.assertEqual(parsed["checks"][0]["title"], "Plaintext secret shapes")
        self.assertEqual(parsed["checks"][0]["safety"].startswith("Read-only"), True)

    def test_missing_safety_field_is_invalid(self):
        text = VALID_PACK.replace("Safety: Read-only search only; redact values and report path plus category.\n", "")

        with self.assertRaises(SystemExit) as raised:
            validate_domain_pack.parse_pack(text, "broken.md")

        self.assertIn("Safety", str(raised.exception))

    def test_cli_validates_all_example_packs(self):
        paths = sorted((ROOT / "domain-packs").glob("*.md"))
        self.assertGreaterEqual(len(paths), 4)

        proc = subprocess.run(
            [sys.executable, str(ROOT / "scripts" / "validate_domain_pack.py"), *map(str, paths)],
            text=True,
            capture_output=True,
        )

        self.assertEqual(proc.returncode, 0, proc.stderr)
        self.assertIn("OK", proc.stdout)
        self.assertIn("security-team", proc.stdout)

    def test_cli_rejects_broken_pack_without_traceback(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "broken.md"
            path.write_text("# Broken\n\nid: broken\n\n## Check: Missing fields\n", encoding="utf-8")

            proc = subprocess.run(
                [sys.executable, str(ROOT / "scripts" / "validate_domain_pack.py"), str(path)],
                text=True,
                capture_output=True,
            )

        self.assertEqual(proc.returncode, 1)
        self.assertIn("missing required metadata", proc.stderr)
        self.assertNotIn("Traceback", proc.stderr)


if __name__ == "__main__":
    unittest.main()
