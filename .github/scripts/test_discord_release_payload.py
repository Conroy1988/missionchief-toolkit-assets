#!/usr/bin/env python3

from __future__ import annotations

import argparse
import importlib.util
import tempfile
import unittest
from pathlib import Path

SCRIPT_PATH = Path(__file__).with_name("build_discord_release_payload.py")
SPEC = importlib.util.spec_from_file_location('discord_release_payload', SCRIPT_PATH)
if SPEC is None or SPEC.loader is None:
    raise RuntimeError('Unable to load Discord release payload builder.')
MODULE = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(MODULE)


class DiscordReleasePayloadTests(unittest.TestCase):
    def make_changelog(self, content: str) -> Path:
        directory = Path(tempfile.mkdtemp())
        changelog = directory / 'CHANGELOG.md'
        changelog.write_text(content, encoding='utf-8')
        self.addCleanup(lambda: directory.rmdir())
        self.addCleanup(lambda: changelog.unlink(missing_ok=True))
        return changelog

    @staticmethod
    def make_args() -> argparse.Namespace:
        return argparse.Namespace(
            version='4.20.22',
            release_url='https://github.com/example/toolkit/releases/tag/v4.20.22',
            script_url='https://greasyfork.org/scripts/123-toolkit',
            install_url='https://greasyfork.org/scripts/123-toolkit/code/toolkit.user.js',
            history_url='https://greasyfork.org/scripts/123-toolkit/versions',
            previous_version='4.20.21',
            sha256='57b89188ab780a36dc1234567890abcdefabcdefabcdefabcdefabcdefabcd',
            backup_commit='6e81faa47f1234567890abcdef1234567890abcd',
        )

    def test_changelog_prioritises_user_facing_sections_and_limits_items(self) -> None:
        changelog = self.make_changelog(
            '''# Toolkit v4.20.22
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
'''
        )

        brief = MODULE.parse_changelog(changelog)

        self.assertTrue(brief.startswith('**🛠️ FIXED**'))
        self.assertEqual(brief.count('\n> **'), 4)
        self.assertIn('+3 additional changes', brief)
        self.assertNotIn('Rebuilt public assets', brief)
        self.assertLessEqual(len(brief), MODULE.MAX_BRIEF_LENGTH)

    def test_primary_payload_uses_two_embed_release_hierarchy(self) -> None:
        args = self.make_args()
        payload = MODULE.build_primary(args, '**🛠️ FIXED**\n> **01**  Corrected Matrix counts.')

        MODULE.validate_payload(payload)
        self.assertEqual(len(payload['embeds']), 2)
        hero, intelligence = payload['embeds']

        self.assertEqual(hero['title'], '🚨 DEPLOYMENT CONFIRMED // v4.20.22')
        self.assertIn('INSTALL / UPDATE TO v4.20.22', hero['description'])
        self.assertEqual(len(hero['fields']), 3)
        self.assertEqual(intelligence['title'], '⚡ RELEASE INTELLIGENCE')
        self.assertIn('Corrected Matrix counts', intelligence['description'])
        self.assertIn('Install now', intelligence['fields'][0]['value'])

    def test_fallback_payload_remains_visually_distinct(self) -> None:
        args = self.make_args()
        payload = MODULE.build_fallback(args, '**🛠️ FIXED**\n> **01**  Corrected Matrix counts.')

        MODULE.validate_payload(payload)
        self.assertEqual(len(payload['embeds']), 2)
        hero, intelligence = payload['embeds']

        self.assertIn('PUBLIC VERSION DETECTED', hero['title'])
        self.assertEqual(hero['color'], 0xF59E0B)
        self.assertIn('v4.20.21', hero['description'])
        self.assertIn('v4.20.22', hero['description'])
        self.assertEqual(intelligence['color'], 0xD97706)


if __name__ == '__main__':
    unittest.main()
