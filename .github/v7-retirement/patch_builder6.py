from pathlib import Path
ROOT=Path(__file__).resolve().parents[2]
target=ROOT/'.github/v7-retirement/apply_v7_retirement.py'
s=target.read_text(encoding='utf-8')
old="""constants='''V7_RETIREMENT_CONTRACT = ROOT / \".github\" / \"scripts\" / \"test_v7_retirement.py\""""
new="""constants='''VERSION_STATUS_CONTRACT = ROOT / \".github\" / \"scripts\" / \"test_version_status_contract.py\"\nFINANCIAL_OVERVIEW_CONTRACT = ROOT / \".github\" / \"scripts\" / \"test_financial_overview_contract.py\"\nMAIN_STYLE_HEADROOM_CONTRACT = ROOT / \".github\" / \"scripts\" / \"test_main_style_source_headroom.py\"\nV7_RETIREMENT_CONTRACT = ROOT / \".github\" / \"scripts\" / \"test_v7_retirement.py\""""
if s.count(old)!=1: raise SystemExit(f'constant registry anchor {s.count(old)}')
s=s.replace(old,new,1)
target.write_text(s,encoding='utf-8')
for p in [ROOT/'.github/v7-retirement/patch_builder6.py',ROOT/'.github/workflows/patch-v7-builder6.yml']:
    p.unlink(missing_ok=True)
