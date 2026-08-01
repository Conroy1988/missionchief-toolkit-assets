#!/usr/bin/env python3

from __future__ import annotations

import argparse
import importlib.util
import tempfile
import unittest
from pathlib import Path

SCRIPT_PATH = Path(__file__).with_name("build_discord_release_payload.py")
SPEC = importlib.util.spec_from_file_location("discord_release_payload", SCRIPT_PATH)
if SPEC is None or SPEC.loader is None:
    raise RuntimeError("Unable to load Discord release payload builder.")
MODULE = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(MODULE)


class DiscordReleasePayloadTests(unittest.TestCase):
    def make_changelog(self, content: str) -> Path:
        directory = Path(tempfile.mkdtemp())
        changelog = directory / "CHANGELOG.md"
        changelog.write_text(content, encoding="utf-8")
        self.addCleanup(lambda: directory.rmdir())
        self.addCleanup(lambda: changelog.unlink(missing_ok=True))
        return changelog

    @staticmethod
    def make_args() -> argparse.Namespace:
        return argparse.Namespace(
            version="4.20.23",
            release_url="https://github.com/example/toolkit/releases/tag/v4.20.23",
            script_url="https://tkb-gaming.scot/mission-chief-scripts/map-command-toolkit/",
            sha256="57b89188ab780a36dc1234567890abcdefabcdefabcdefabcdefabcdefabcd",
            backup_commit="6e81faa47f1234567890abcdef1234567890abcd",
        )

    def test_changelog_prioritises_user_facing_sections_and_limits_items(self) -> None:
        changelog = self.make_changelog(
            """# Toolkit v4.20.23
### Distribution
- Rebuilt public assets.
### Fixed
- Counted confirmed patient releases exactly once.
- Recognised global MissionChief release confirmations.
- Preserved successful totals after cleanup failures.
- Kept every sweep counter in sync.
### Validation
- Added deterministic regression coverage.
### Added
- Added another feature.
"""
        )

        brief = MODULE.parse_changelog(changelog)

        self.assertTrue(brief.startswith("**🛠️ Fixed**"))
        self.assertEqual(brief.count("\n> **"), 3)
        self.assertIn("4 additional changes", brief)
        self.assertNotIn("Rebuilt public assets", brief)
        self.assertLessEqual(len(brief), MODULE.MAX_BRIEF_LENGTH)

    def test_primary_payload_puts_summary_and_links_in_the_only_embed(self) -> None:
        args = self.make_args()
        brief = "**🛠️ Fixed**\n> **01**  Corrected Transport Sweep counts."
        payload = MODULE.build_primary(args, brief)

        MODULE.validate_payload(payload)
        self.assertEqual(len(payload["embeds"]), 1)

        embed = payload["embeds"][0]
        self.assertEqual(embed["title"], "🚨 TOOLKIT v4.20.23 // DEPLOYMENT LIVE")
        self.assertEqual(embed["fields"][0]["name"], "⚡ MISSION BRIEF")
        self.assertEqual(embed["fields"][0]["value"], brief)
        self.assertEqual(embed["fields"][1]["name"], "🔗 COMMAND LINKS")
        self.assertIn("Install / Update", embed["fields"][1]["value"])
        self.assertIn("[⬇️ Install / Update](https://tkb-gaming.scot/mission-chief-scripts/map-command-toolkit/)", embed["fields"][1]["value"])
        self.assertNotIn("/map-command-toolkit/install/", embed["fields"][1]["value"])
        self.assertIn("Release notes", embed["fields"][1]["value"])
        self.assertIn("TKB Scripts", embed["fields"][1]["value"])
        self.assertIn("available now through TKB Scripts", embed["description"])
        self.assertEqual(embed["fields"][2]["value"], "TKB Scripts\n**LIVE** ✅")
        self.assertNotIn("Greasy Fork", str(embed))
        self.assertEqual(len(embed["fields"]), 5)

if __name__ == "__main__":
    unittest.main()
