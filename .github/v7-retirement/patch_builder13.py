from pathlib import Path
ROOT=Path(__file__).resolve().parents[2]
target=ROOT/'.github/v7-retirement/apply_v7_retirement.py'
s=target.read_text(encoding='utf-8')
old="ms=list(re.finditer(rf'\\bfunction\\s+{re.escape(name)}\\s*\\(',s))"
new="ms=list(re.finditer(rf'\\b(?:async\\s+)?function\\s+{re.escape(name)}\\s*\\(',s))"
if s.count(old)!=1: raise SystemExit(f'function remover regex count {s.count(old)}')
s=s.replace(old,new,1)
target.write_text(s,encoding='utf-8')
for p in [ROOT/'.github/v7-retirement/patch_builder13.py',ROOT/'.github/workflows/patch-v7-builder13.yml']:
    p.unlink(missing_ok=True)
