#!/usr/bin/env python3
"""Permanent v8 Godfather theme, payout, media and lifecycle contract."""
from __future__ import annotations

import hashlib
import json
import re
import xml.etree.ElementTree as ET
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
SOURCE_PATH = ROOT / "src/MissionChief_Map_Command_Toolkit.user.js"
SOURCE = SOURCE_PATH.read_text(encoding="utf-8")
EXPECTED_SOURCE_SHA256 = "773d6686fdcfe0af5901f54bdd58c58cf0ef8503bddaae354f32ed25879ac19b"
EXPECTED_AUDIO_SHA256 = "53160bd03bacf043ea3b0ffbd202163c2621e16a47ecd0f7090bfeacaf00b0d4"


def require(condition: bool, message: str) -> None:
    if not condition:
        raise AssertionError(message)


require(hashlib.sha256(SOURCE_PATH.read_bytes()).hexdigest() == EXPECTED_SOURCE_SHA256,
        "v8 userscript hash drifted from the reviewed deterministic build")
require("// @version      8.0.3" in SOURCE, "userscript metadata version is not 8.0.3")
require("version: '8.0.3'" in SOURCE, "runtime version is not 8.0.3")
require("godfather: Object.freeze({ label: 'The Godfather'" in SOURCE, "Godfather interface registry entry missing")
require("'hyrule', 'godfather'" in SOURCE, "Godfather interface is not last in the eight-theme order")
require("godfatherOffer: { label: 'The Godfather Offer'" in SOURCE, "Godfather payout registry entry missing")
require("'hyruleQuest', 'godfatherOffer'" in SOURCE, "Godfather payout order entry missing")
require("themes/godfather/audio/godfather-flash-payout.mp3" in SOURCE, "theme-scoped payout audio URL missing")
require("Object.freeze({ hyrule: 'hyruleQuest', godfather: 'godfatherOffer' })" in SOURCE,
        "generic interface-to-payout pairing contract missing")
require("FAMILY INCIDENT WIRE" in SOURCE, "Godfather Incident Command Wire label missing")
require("case 'godfatherOffer':" in SOURCE, "Godfather synthesized audio fallback missing")
require("audio.preload = 'none'" in SOURCE, "hosted payout media is not lazy by default")
require("document.createElement('audio')" in SOURCE, "payout audio is not created on demand")
require("disposePayoutMediaAudio" in SOURCE and "payoutMediaAudio = null" in SOURCE,
        "deterministic hosted-audio disposal contract missing")

start = SOURCE.index("/* v8.0.3 — The Godfather: complete original old-money command interface. */")
end = SOURCE.index('html[data-mcms-mobile-active="true"],', start)
theme_css = SOURCE[start:end]
for selector in (
    'html[data-mcms-ui-theme="godfather"]',
    '.mcms-ui-theme-preview-godfather',
    'data-template="godfatherOffer"',
    'data-mcms-economy="true"',
    'prefers-reduced-motion:reduce',
    'data-mcms-mobile-active="true"',
    'data-mcms-tablet-active="true"',
):
    require(selector in theme_css, f"required Godfather presentation selector missing: {selector}")
for forbidden in ('MutationObserver', 'ResizeObserver', 'setInterval(', 'runtimeSetInterval(', 'requestAnimationFrame('):
    require(forbidden not in theme_css, f"theme CSS introduced runtime work: {forbidden}")
require(theme_css.count('html[data-mcms-ui-theme="godfather"]') >= 100,
        "Godfather interface coverage fell below the reviewed complete-system threshold")
require(theme_css.count('data-template="godfatherOffer"') >= 20,
        "Godfather payout coverage fell below the reviewed threshold")

manifest_path = ROOT / "themes/godfather/manifest.json"
manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
require(manifest["theme"] == "godfather", "theme manifest identity mismatch")
require(manifest["toolkitVersion"] == "8.0.3", "theme manifest Toolkit version mismatch")
require(manifest["audio"]["sha256"] == EXPECTED_AUDIO_SHA256, "manifest audio digest mismatch")
require(manifest["audio"]["loading"].startswith("Lazy"), "manifest does not preserve lazy audio loading")
require(manifest["compatibility"]["layouts"] == ["desktop", "ultrawide", "tablet", "ios-mobile", "mobile"],
        "responsive layout contract mismatch")
require(manifest["accessibility"]["minimumTouchTargetPx"] == 44, "touch target contract mismatch")

for rel in manifest["assets"].values():
    asset = manifest_path.parent / rel
    require(asset.is_file(), f"manifest asset missing: {asset.relative_to(ROOT)}")
    if asset.suffix == '.svg':
        ET.parse(asset)
        text = asset.read_text(encoding='utf-8')
        require('<image' not in text and 'href="http' not in text,
                f"SVG must remain self-contained and original: {asset.relative_to(ROOT)}")

audio = ROOT / "themes/godfather/audio/godfather-flash-payout.mp3"
require(audio.is_file(), "Godfather payout MP3 missing")
payload = audio.read_bytes()
require(hashlib.sha256(payload).hexdigest() == EXPECTED_AUDIO_SHA256, "Godfather payout MP3 digest mismatch")
require(len(payload) == 136254, "Godfather payout MP3 byte size mismatch")
require(payload.startswith(b'ID3') or payload[:2] in (b'\xff\xfb', b'\xff\xf3', b'\xff\xf2'),
        "Godfather payout MP3 signature invalid")

alias_manifest = json.loads((ROOT / '.github/asset-compatibility-aliases.json').read_text(encoding='utf-8'))
require('themes/godfather/audio/godfather-flash-payout.mp3' in alias_manifest['canonicalAudioPaths'],
        "Godfather audio missing from canonical audio contract")

site = json.loads((ROOT / 'docs/site-data.json').read_text(encoding='utf-8'))
require(sum(1 for item in site['themes'] if item.get('slug') == 'godfather') == 1,
        "website theme registry must contain exactly one Godfather entry")
require('The Godfather Offer' in site['payoutThemes'], "website payout registry missing Godfather Offer")
help_manifest = json.loads((ROOT / 'help/manifest.json').read_text(encoding='utf-8'))
require(help_manifest['toolkitVersion'] == '8.0.3', "Help Centre version mismatch")
require(help_manifest['godfatherThemePackage'] == 'themes/godfather/manifest.json',
        "Help Centre theme package reference missing")
require('id="godfather-interface"' in (ROOT / 'help/index.html').read_text(encoding='utf-8'),
        "Help Centre Godfather section missing")
require('## [8.0.3] - 2026-07-26' in (ROOT / 'CHANGELOG.md').read_text(encoding='utf-8'),
        "v8 changelog entry missing")

print(json.dumps({
    'sourceSha256': EXPECTED_SOURCE_SHA256,
    'audioSha256': EXPECTED_AUDIO_SHA256,
    'themeSelectors': theme_css.count('html[data-mcms-ui-theme="godfather"]'),
    'payoutSelectors': theme_css.count('data-template="godfatherOffer"'),
    'assets': len(manifest['assets']),
}, indent=2))
