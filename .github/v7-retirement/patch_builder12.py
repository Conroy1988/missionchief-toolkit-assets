from pathlib import Path
ROOT=Path(__file__).resolve().parents[2]
target=ROOT/'.github/v7-retirement/apply_v7_retirement.py'
s=target.read_text(encoding='utf-8')
old="expected_actions=sorted(set(fixtures['actions'])|set(fixtures.get('dynamicActions',[])));assert actions==expected_actions,(actions,expected_actions);assert settings==sorted(fixtures['settings']);assert tabs==sorted(fixtures['tabs'])"
new="external_dynamic={'profile-delete','profile-load','profile-save','toggle-economy'};expected_actions=sorted(set(fixtures['actions'])|(set(fixtures.get('dynamicActions',[]))-external_dynamic));assert actions==expected_actions,(actions,expected_actions);assert all(action in source for action in external_dynamic);assert settings==sorted(fixtures['settings']);assert tabs==sorted(fixtures['tabs'])"
if s.count(old)!=1: raise SystemExit(f'dynamic settings ownership assertion count {s.count(old)}')
s=s.replace(old,new,1)
target.write_text(s,encoding='utf-8')
for p in [ROOT/'.github/v7-retirement/patch_builder12.py',ROOT/'.github/workflows/patch-v7-builder12.yml']:
    p.unlink(missing_ok=True)
