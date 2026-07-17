#!/usr/bin/env python3
from pathlib import Path

path = Path("help/index.html")
text = path.read_text(encoding="utf-8")
old = "Guide for Toolkit v4.14.5"
new = "Guide for Toolkit v4.14.6"
if text.count(old) != 1:
    raise RuntimeError(f"Expected one Help Centre version marker, found {text.count(old)}")
path.write_text(text.replace(old, new, 1), encoding="utf-8")
