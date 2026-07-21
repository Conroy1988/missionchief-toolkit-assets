#!/usr/bin/env python3
"""Regenerate and validate the pinned v4.20.24 observer ownership inventory."""
from __future__ import annotations
import json, subprocess, tempfile
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2]
with tempfile.TemporaryDirectory() as td:
    td=Path(td); deep_json=td/'deep.json'; deep_md=td/'deep.md'; inv_json=td/'inventory.json'; inv_md=td/'inventory.md'
    subprocess.run(['node','.github/scripts/deep_performance_audit.mjs','--source','src/MissionChief_Map_Command_Toolkit.user.js','--json-output',str(deep_json),'--markdown-output',str(deep_md)],check=True,cwd=ROOT)
    subprocess.run(['python3','.github/scripts/build_observer_ownership_inventory.py','--source','src/MissionChief_Map_Command_Toolkit.user.js','--deep-json',str(deep_json),'--fixture','.github/fixtures/observer-ownership-v4.20.24.json','--json-output',str(inv_json),'--markdown-output',str(inv_md)],check=True,cwd=ROOT)
    generated_inv=json.loads(inv_json.read_text())
    if (ROOT/'docs/audits/observer-ownership-v4.20.24.md').read_text() != inv_md.read_text(): raise SystemExit('committed observer inventory Markdown is stale')
    assert generated_inv['conclusion']['allLongLivedObserversOwned'] is True
    assert generated_inv['metrics']['observeRegistrations'] == 19
    assert generated_inv['metrics']['broadSubtreeRegistrations'] == 10
print('Observer ownership inventory contract passed.')
