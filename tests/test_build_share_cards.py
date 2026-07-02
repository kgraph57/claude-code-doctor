import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

import build_share_cards  # noqa: E402


class ShareCardBuilderTests(unittest.TestCase):
    def test_numeric_fields_are_sanitized_before_rendering(self):
        data = {
            "brand": "Claude Code Doctor",
            "numbers": {
                "kicker": "NUMBERS",
                "title": "The setup rent",
                "cells": [
                    {"n": "api_key=abc123", "unit": "", "label": "should not render"},
                ],
            },
        }

        with self.assertRaises(SystemExit) as raised:
            build_share_cards.build_html(data)

        self.assertIn("refusing to render", str(raised.exception))

    def test_user_paths_are_masked_in_numeric_cards(self):
        data = {
            "brand": "Claude Code Doctor",
            "numbers": {
                "kicker": "NUMBERS",
                "title": "The setup rent",
                "cells": [
                    {"n": "/Users/alice/project", "unit": "paths", "label": "/Users/alice/.claude"},
                ],
            },
        }

        html, total = build_share_cards.build_html(data)

        self.assertEqual(total, 1)
        self.assertIn("~", html)
        self.assertNotIn("/Users/alice", html)

    def test_secret_shape_in_hero_number_fails_closed(self):
        data = {
            "brand": "Claude Code Doctor",
            "hero": {
                "kicker": "CHECKUP",
                "lines": ["Safe line"],
                "big": {"n": "Bearer abc123", "unit": "tokens", "note": "sample"},
            },
        }

        with self.assertRaises(SystemExit) as raised:
            build_share_cards.build_html(data)

        self.assertIn("refusing to render", str(raised.exception))
        self.assertIn("hero.big.n", str(raised.exception))

    def test_malformed_card_lists_do_not_crash(self):
        data = {
            "brand": "Claude Code Doctor",
            "numbers": {"cells": ["not a cell", {"n": "7", "label": "valid"}]},
            "lessons": {"items": ["not an item", {"title": "Measure", "body": "First"}]},
            "howto": {"steps": ["not a step", {"title": "Run", "body": "Tests"}], "tease": "bad"},
        }

        html, total = build_share_cards.build_html(data)

        self.assertEqual(total, 3)
        self.assertIn("valid", html)
        self.assertIn("Measure", html)
        self.assertIn("Tests", html)

    def test_allowed_markup_is_narrow_and_everything_else_is_escaped(self):
        data = {
            "brand": "Claude Code Doctor",
            "hero": {
                "kicker": "CHECKUP",
                "lines": ["Keep <em>this</em>", "Escape <strong>that</strong>"],
                "big": {"n": "12", "unit": "findings", "note": "No <script>x</script>"},
            },
        }

        html, total = build_share_cards.build_html(data)

        self.assertEqual(total, 1)
        self.assertIn("<em>this</em>", html)
        self.assertIn("&lt;strong&gt;that&lt;/strong&gt;", html)
        self.assertIn("&lt;script&gt;x&lt;/script&gt;", html)
        self.assertNotIn("<script>x</script>", html)


if __name__ == "__main__":
    unittest.main()
