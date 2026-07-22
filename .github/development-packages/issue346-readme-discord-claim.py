#!/usr/bin/env python3
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
README = ROOT / "README.md"
text = README.read_text(encoding="utf-8")
old = "| **Discord financial reports** | Sends the canonical reconciled model through configured webhook reporting |"
new = "| **Discord financial reports** | Sends the canonical reconciled model through the saved Discord webhook |"
count = text.count(old)
if count != 1:
    raise RuntimeError(f"Expected one Discord financial report row, found {count}")
README.write_text(text.replace(old, new, 1), encoding="utf-8")
print("Restored the required saved Discord webhook README claim")
