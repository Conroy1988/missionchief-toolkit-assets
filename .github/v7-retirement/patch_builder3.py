from pathlib import Path
ROOT=Path(__file__).resolve().parents[2]
target=ROOT/'.github/v7-retirement/apply_v7_retirement.py'
s=target.read_text(encoding='utf-8')
old='''    if "toolkit-current" in path.parts: continue
    try: text=path.read_text(encoding="utf-8")'''
new='''    if "toolkit-current" in path.parts or "dist" in path.parts: continue
    try: text=path.read_text(encoding="utf-8")'''
if s.count(old)!=1: raise SystemExit(f'anchor {s.count(old)}')
s=s.replace(old,new,1)
target.write_text(s,encoding='utf-8')
for p in [ROOT/'.github/v7-retirement/patch_builder3.py',ROOT/'.github/workflows/patch-v7-builder3.yml']:
 p.unlink(missing_ok=True)
