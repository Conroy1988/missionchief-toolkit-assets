#!/usr/bin/env python3
"""Advance both microtask and task queues in the generated isolated DOM integration test."""
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
TEST = ROOT / ".github/scripts/test_ui_mount_integration.mjs"
text = TEST.read_text(encoding="utf-8")
old = '''async function flush(rounds = 80) {
  for (let index = 0; index < rounds; index += 1) await Promise.resolve();
}
'''
new = '''async function flush(rounds = 20) {
  for (let index = 0; index < rounds; index += 1) {
    await Promise.resolve();
    await new Promise(resolve => setTimeout(resolve, 0));
  }
}
'''
if text.count(old) != 1:
    raise RuntimeError("Unable to patch integration queue flush")
TEST.write_text(text.replace(old, new, 1), encoding="utf-8")
print("UI mount integration now advances microtask and task queues.")
