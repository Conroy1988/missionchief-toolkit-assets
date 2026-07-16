#!/usr/bin/env python3
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
SITE_DATA = ROOT / "docs" / "site-data.json"

text = SITE_DATA.read_text(encoding="utf-8")
old = '"description": "The flagship parchment, royal-gold and ancient-energy command interface with transparent themed artwork."'
new = '"description": "A parchment, royal-gold and ancient-energy command interface with transparent themed artwork."'
if text.count(old) != 1:
    raise RuntimeError(f"Expected one Hyrule flagship description, found {text.count(old)}")
SITE_DATA.write_text(text.replace(old, new, 1), encoding="utf-8")
