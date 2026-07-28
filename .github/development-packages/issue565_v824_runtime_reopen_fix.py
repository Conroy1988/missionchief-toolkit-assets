#!/usr/bin/env python3
from pathlib import Path
ROOT = Path(__file__).resolve().parents[2]
path = ROOT / '.github/scripts/test_issue565_transport_sweep_no_reward_runtime.mjs'
text = path.read_text(encoding='utf-8')
old = '''      generation += 1;
      poll = 0;
      missionRowsReady = options.deferMissionRowsOnReopen === true ? false : true;
      render(false);
'''
new = '''      generation += 1;
      poll = 0;
      dom.window.document.querySelector("#top-alert").innerHTML = "";
      missionRowsReady = options.deferMissionRowsOnReopen === true ? false : true;
      render(false);
'''
if text.count(old) != 1:
    raise RuntimeError(f'Expected one reopen fixture block, found {text.count(old)}')
path.write_text(text.replace(old, new, 1), encoding='utf-8')
print('v8.2.4 simulated reopen now clears cloned top-alert control.')
