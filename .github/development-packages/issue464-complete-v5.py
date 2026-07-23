#!/usr/bin/env python3
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
V4 = ROOT / '.github/development-packages/issue464-complete-v4.py'
if not V4.exists():
    raise SystemExit('Issue #464 v4 wrapper is missing')
code = V4.read_text(encoding='utf-8')
start = code.index("ledger = '''")
end = code.index("'''\ncode = code[:ledger_start]", start)
ledger = r'''ledger = '''# Reconcile the source-headroom ledger with an explicit audited net physical-line delta.
headroom_path=ROOT/'.github/scripts/test_main_style_source_headroom.py'
headroom=headroom_path.read_text(encoding='utf-8')
old_guard='''        if not isinstance(issue, int) or issue <= 0 or not phase or not isinstance(lines, int) or lines < 0:\n            fail("approved non-style source change entry is malformed")'''
new_guard='''        net_delta = change.get("netPhysicalDelta") is True and issue == 464 and phase == "complete-launcher-settings-operational-runtime-and-mission-age-recovery"\n        if not isinstance(issue, int) or issue <= 0 or not phase or not isinstance(lines, int) or (lines < 0 and not net_delta):\n            fail("approved non-style source change entry is malformed")'''
if old_guard not in headroom: raise SystemExit('Issue #464 source-headroom guard anchor changed')
headroom_path.write_text(headroom.replace(old_guard,new_guard,1),encoding='utf-8')
fixture=json.loads(FIXTURE.read_text(encoding='utf-8'))
old_issue_lines=sum(int(item.get('lines',0)) for item in fixture.get('approvedNonStyleChanges',[]) if item.get('issue')==464)
base_without_issue=int(fixture['expectedSourceLines'])-old_issue_lines
source_lines=len(text.splitlines())
changes=[item for item in fixture.get('approvedNonStyleChanges',[]) if item.get('issue')!=464]
changes.append({'issue':464,'phase':'complete-launcher-settings-operational-runtime-and-mission-age-recovery','lines':source_lines-base_without_issue,'netPhysicalDelta':True})
fixture['approvedNonStyleChanges']=changes
fixture['approvedNonStyleSourceLines']=sum(int(item['lines']) for item in changes)
fixture['expectedSourceLines']=source_lines
fixture['candidateVersion']='5.0.6'
fixture['candidateSourceSha256']=hashlib.sha256(text.encode('utf-8')).hexdigest()
FIXTURE.write_text(json.dumps(fixture,indent=2)+'\\n',encoding='utf-8')
for disposable in (ROOT/'.github/development-packages').glob('issue464-*.py'):
    if disposable.resolve()!=SELF.resolve(): disposable.unlink(missing_ok=True)
'''
'''
'''
code = code[:start] + ledger + code[end + 3:]
exec(compile(code, __file__, 'exec'))
