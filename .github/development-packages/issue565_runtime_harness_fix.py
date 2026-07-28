#!/usr/bin/env python3
"""Add the production mission-ID normaliser to the Issue #565 runtime harness."""
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
RUNTIME = ROOT / ".github/scripts/test_issue565_transport_sweep_no_reward_runtime.mjs"
text = RUNTIME.read_text(encoding="utf-8")
old = '''    transportSweepRuntime: runtime,
    normaliseTransportSweepReleaseText(value) {
'''
new = '''    transportSweepRuntime: runtime,
    normaliseMissionId(value) {
      const text = String(value ?? "").trim();
      return /^\\d+$/u.test(text) ? text : null;
    },
    normaliseTransportSweepReleaseText(value) {
'''
if text.count(old) != 1:
    raise RuntimeError(f"Expected one runtime sandbox insertion point, found {text.count(old)}")
RUNTIME.write_text(text.replace(old, new, 1), encoding="utf-8")
print("Issue #565 runtime harness includes production mission-ID normalisation.")
