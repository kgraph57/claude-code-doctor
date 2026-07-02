import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


class PublicSurfaceTests(unittest.TestCase):
    def read(self, relative_path):
        return (ROOT / relative_path).read_text(encoding="utf-8")

    def test_english_readme_has_star_conversion_surface(self):
        readme = self.read("README.md")

        for needle in [
            "Current release: **v0.7.0**",
            "## Paste This Into Claude Code",
            "## Demo In 10 Seconds",
            "## Diff Mode",
            "## CI Budget Gate",
            "## Community Domain Packs",
            "## Cross-Harness Checkups",
            "## Why Star This Repo?",
            "docs/roadmap.md",
            "actions/workflows/test.yml/badge.svg",
            "scripts/compare_reports.py samples/diff-before.json samples/diff-after.json",
            "scripts/check_budgets.py samples/diff-before.json samples/budgets.json",
            "scripts/validate_domain_pack.py domain-packs/security-team.md",
            "scripts/validate_adapter_notes.py docs/adapters/*.md",
        ]:
            self.assertIn(needle, readme)
        self.assertNotIn("cards.html", readme)

    def test_japanese_readme_has_matching_star_conversion_surface(self):
        readme = self.read("README.ja.md")

        for needle in [
            "現在のリリース: **v0.7.0**",
            "## Claude Codeに貼る",
            "## 10秒デモ",
            "## 差分モード",
            "## CI予算ゲート",
            "## コミュニティ領域パック",
            "## ハーネス横断チェックアップ",
            "## なぜスターするか",
            "docs/roadmap.md",
            "actions/workflows/test.yml/badge.svg",
            "scripts/compare_reports.py samples/diff-before.json samples/diff-after.json",
            "scripts/check_budgets.py samples/diff-before.json samples/budgets.json",
            "scripts/validate_domain_pack.py domain-packs/security-team.md",
            "scripts/validate_adapter_notes.py docs/adapters/*.md",
        ]:
            self.assertIn(needle, readme)
        self.assertNotIn("cards.html", readme)

    def test_changelog_leads_with_v070(self):
        changelog = self.read("CHANGELOG.md")

        self.assertLess(changelog.index("## v0.7.0"), changelog.index("## v0.6.0"))
        self.assertIn("Cross-Harness Checkups", changelog)
        self.assertIn("validate_adapter_notes.py", changelog)

    def test_roadmap_names_next_public_milestones(self):
        roadmap = self.read("docs/roadmap.md")

        for needle in [
            "v0.4.0 - Diff Mode",
            "v0.5.0 - CI Budget Gate",
            "v0.6.0 - Community Domain Packs",
            "v0.7.0 - Cross-Harness Checkups",
            "What We Will Not Build",
        ]:
            self.assertIn(needle, roadmap)

    def test_github_ci_and_issue_templates_exist(self):
        workflow = self.read(".github/workflows/test.yml")

        self.assertIn("python -m unittest discover -s tests", workflow)
        self.assertIn("scripts/build_dashboard.py samples/dashboard.json", workflow)
        self.assertIn("scripts/compare_reports.py samples/diff-before.json samples/diff-after.json", workflow)
        self.assertIn("scripts/check_budgets.py samples/diff-before.json samples/budgets.json", workflow)
        self.assertIn("scripts/validate_domain_pack.py domain-packs/*.md", workflow)
        self.assertIn("scripts/validate_adapter_notes.py docs/adapters/*.md", workflow)

        for path in [
            ".github/ISSUE_TEMPLATE/checkup-grade.yml",
            ".github/ISSUE_TEMPLATE/domain-pack.yml",
            ".github/ISSUE_TEMPLATE/bug_report.yml",
        ]:
            self.assertTrue((ROOT / path).exists(), path)

        for path in [
            "samples/diff-before.json",
            "samples/diff-after.json",
            "samples/budgets.json",
            "docs/ci-budget-gate.md",
            "docs/domain-packs.md",
            "domain-packs/security-team.md",
            "domain-packs/solo-founder.md",
            "domain-packs/teaching-workshop.md",
            "domain-packs/enterprise-locked-down.md",
            "docs/cross-harness.md",
            "docs/adapters/claude-code.md",
            "docs/adapters/codex.md",
            "docs/adapters/cursor.md",
            "docs/adapters/opencode.md",
        ]:
            self.assertTrue((ROOT / path).exists(), path)


if __name__ == "__main__":
    unittest.main()
