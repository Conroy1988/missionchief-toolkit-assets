#!/usr/bin/env python3
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
PATH = ROOT / '.github' / 'scripts' / 'test_settings_ui_contract.py'
text = PATH.read_text(encoding='utf-8')
old = '''const UI_THEMES = {{ mapCommand: {{ label: "Map Command" }}, hyrule: {{ label: "Hyrule Command" }}, bond007: {{ label: "007 Intelligence" }} }};
const THEMES = {{ default: {{}}, nightshift: {{}}, fire: {{}}, police: {{}} }};
const PAYOUT_TEMPLATES = {{ gta5: {{}}, hyruleQuest: {{}}, bond007: {{}} }};
const PAYOUT_MEDIA_SOUNDS = {{}};
const PAYOUT_FLASH_DURATION_OPTIONS = [2000, 4000, 6000, 8000, 10000];
'''
new = '''const UI_THEMES = {{ mapCommand: {{ label: "Map Command" }}, hyrule: {{ label: "Hyrule Command" }}, bond007: {{ label: "007 Intelligence" }} }};
const THEMES = {{ default: {{}}, nightshift: {{}}, fire: {{}}, police: {{}} }};
const LEGACY_THEME_MAP = {{ legacyNight: "nightshift" }};
const PAYOUT_TEMPLATES = {{ gta5: {{}}, hyruleQuest: {{}}, bond007: {{}} }};
const PAYOUT_MEDIA_SOUNDS = {{}};
const PAYOUT_FLASH_MIN_MS = 2000;
const PAYOUT_FLASH_MAX_MS = 10000;
const PAYOUT_FLASH_STEP_MS = 1000;
'''
if text.count(old) != 1:
    raise RuntimeError(f'expected one harness constant block, found {text.count(old)}')
PATH.write_text(text.replace(old, new, 1), encoding='utf-8')
