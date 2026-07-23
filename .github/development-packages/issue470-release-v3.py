#!/usr/bin/env python3
from pathlib import Path

ROOT=Path(__file__).resolve().parents[2]
V2=ROOT/'.github/development-packages/issue470-release-v2.py'
if not V2.exists(): raise SystemExit('Issue #470 v2 package is missing')
wrapper=V2.read_text(encoding='utf-8')
anchor="exec(compile(code, __file__, 'exec'))"
injection=r'''old_carrier = "        for (const carrier of Array.from(doc.querySelectorAll('[data-raw-html]') || [])) {"
new_carrier = """        const rawCarriers = Array.from(new Set([
            ...Array.from(doc.querySelectorAll('.alert-missing-vehicles[data-raw-html]') || []),
            ...Array.from(doc.querySelectorAll('[data-raw-html]') || [])
        ]));
        for (const carrier of rawCarriers) {"""
if old_carrier not in code:
    raise SystemExit('Issue #470 raw-carrier anchor changed')
code = code.replace(old_carrier, new_carrier, 1)
'''
if wrapper.count(anchor)!=1: raise SystemExit('Issue #470 v2 execution anchor changed')
wrapper=wrapper.replace(anchor,injection+anchor,1)
exec(compile(wrapper,__file__,'exec'))
