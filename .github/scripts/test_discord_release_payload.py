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
            version="4.20.22",
            release_url="https://github.com/example/toolkit/releases/tag/v4.20.22",
            script_url="https://greasyfork.org/scripts/123-toolkit",
            install_url="https://greasyfork.org/scripts/123-toolkit/code/toolkit.user.js",
            history_url="https://greasyfork.org/scripts/123-toolkit/versions",
            previous_version="4.20.21",
            sha256="57b89188ab780a36dc1234567890abcdefabcdefabcdefabcdefabcdefabcd",
            backup_commit="6e81faa47f1234567890abcdef1234567890abcd",
        )

    def test_changelog_prioritises_user_facing_sections_and_limits_items(self) -> None:
        changelog = self.make_changelog(
            """# Toolkit v4.20.22
### Distribution
- Rebuilt public assets.
### Fixed
- Fixed firefighter capacity reconciliation.
- Fixed Police Sergeant responding counts.
- Fixed Police Inspector selected counts.
- Fixed Railway Police responding counts.
- Fixed BASU capability resolution.
### Added
- Added another feature.
"""
        )

        brief = MODULE.parse_changelog(changelog)

        self.assertTrue(brief.startswith("**🛠️ Fixed**"))
        self.assertEqual(brief.count("\n• "), 4)
        self.assertIn("3 more changes", brief)
        self.assertNotIn("Rebuilt public assets", brief)
        self.assertLessEqual(len(brief), MODULE.MAX_BRIEF_LENGTH)

    def test_primary_payload_is_compact_and_valid(self) -> None:
        args = self.make_args()
        payload = MODULE.build_primary(args, "**🛠️ Fixed**\n• Corrected Matrix counts.")

        MODULE.validate_payload(payload)
        embed = payload["embeds"][0]

        self.assertEqual(embed["title"], "✅ Toolkit v4.20.22 is live")
        self.assertEqual(len(embed["fields"]), 6)
        self.assertEqual(embed["fields"][3]["name"], "What changed")
        self.assertIn("Install / Update", embed["fields"][-1]["value"])
        self.assertNotIn("MISSION CONTROL", str(payload))

    def test_fallback_payload_remains_visually_distinct(self) -> None:
        args = self.make_args()
        payload = MODULE.build_fallback(args, "**🛠️ Fixed**\n• Corrected Matrix counts.")

        MODULE.validate_payload(payload)
        embed = payload["embeds"][0]

        self.assertIn("detected on Greasy Fork", embed["title"])
        self.assertEqual(embed["color"], 0xF39C12)
        self.assertIn("v4.20.21", embed["fields"][0]["value"])
        self.assertIn("v4.20.22", embed["fields"][0]["value"])


if __name__ == "__main__":
    unittest.main()
