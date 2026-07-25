from pathlib import Path
ROOT=Path(__file__).resolve().parents[2]
target=ROOT/'.github/v7-retirement/apply_v7_retirement.py'
s=target.read_text(encoding='utf-8')
old='function findVisibleDischargePatientButton(baseline = null)'
new='function findVisibleDischargePatientButton(excludedButtons = null)'
if s.count(old)!=1: raise SystemExit(f'native discharge signature count {s.count(old)}')
s=s.replace(old,new,1)
target.write_text(s,encoding='utf-8')
for p in [ROOT/'.github/v7-retirement/patch_builder8.py',ROOT/'.github/workflows/patch-v7-builder8.yml']:
    p.unlink(missing_ok=True)
