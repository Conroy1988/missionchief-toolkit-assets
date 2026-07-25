from pathlib import Path
ROOT=Path(__file__).resolve().parents[2]
target=ROOT/'.github/v7-retirement/apply_v7_retirement.py'
s=target.read_text(encoding='utf-8')
old='<section><h2>Seven interfaces</h2>'
new='<section><h2>Seven complete interface systems</h2>'
if s.count(old)!=1: raise SystemExit(f'help heading count {s.count(old)}')
s=s.replace(old,new,1)
target.write_text(s,encoding='utf-8')
for p in [ROOT/'.github/v7-retirement/patch_builder5.py',ROOT/'.github/workflows/patch-v7-builder5.yml']:
    p.unlink(missing_ok=True)
