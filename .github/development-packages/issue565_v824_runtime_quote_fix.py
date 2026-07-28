#!/usr/bin/env python3
from pathlib import Path
ROOT = Path(__file__).resolve().parents[2]
path = ROOT / '.github/scripts/test_issue565_transport_sweep_no_reward_runtime.mjs'
text = path.read_text(encoding='utf-8')
old = 'const dom = new JSDOM("<!doctype html><html><body><div id="top-alert"></div><main id=mission></main></body></html>", {'
new = "const dom = new JSDOM('<!doctype html><html><body><div id=\"top-alert\"></div><main id=\"mission\"></main></body></html>', {"
if text.count(old) != 1:
    raise RuntimeError(f'Expected one unescaped fixture string, found {text.count(old)}')
path.write_text(text.replace(old, new, 1), encoding='utf-8')
print('v8.2.4 runtime fixture quoting corrected.')
