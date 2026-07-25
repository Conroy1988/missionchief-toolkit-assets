from pathlib import Path
ROOT=Path(__file__).resolve().parents[2]
target=ROOT/'.github/v7-retirement/apply_v7_retirement.py'
s=target.read_text(encoding='utf-8')
old='''        if not path.is_file() or ".git" in path.parts or "release-bundle" in path.parts: continue
        if TOKEN in path.as_posix().lower(): tracked.append(path.as_posix())'''
new='''        if not path.is_file() or ".git" in path.parts or "release-bundle" in path.parts: continue
        if path.parent == ROOT and path.name in {"MissionChief_Map_Command_Toolkit.user.js", "MissionChief_Map_Command_Toolkit.txt"}: continue
        if TOKEN in path.as_posix().lower(): tracked.append(path.as_posix())'''
if s.count(old)!=1: raise SystemExit(f'contract scan anchor count {s.count(old)}')
s=s.replace(old,new,1)
old2='''    if not path.is_file() or ".git" in path.parts or "release-bundle" in path.parts: continue
    try: text=path.read_text(encoding="utf-8")'''
new2='''    if not path.is_file() or ".git" in path.parts or "release-bundle" in path.parts: continue
    if path.parent == ROOT and path.name in {"MissionChief_Map_Command_Toolkit.user.js", "MissionChief_Map_Command_Toolkit.txt"}: continue
    try: text=path.read_text(encoding="utf-8")'''
if s.count(old2)!=1: raise SystemExit(f'builder scan anchor count {s.count(old2)}')
s=s.replace(old2,new2,1)
needle='''".github/workflows/issue512-lssm-coexistence-diagnostic.yml",".github/v7-retirement/apply_v7_retirement.py"'''
repl='''".github/workflows/issue512-lssm-coexistence-diagnostic.yml",".github/issue512/apply_main_toolbar_fix.py",".github/workflows/apply-issue512-main-toolbar-fix.yml",".github/v7-retirement/apply_v7_retirement.py"'''
if s.count(needle)!=1: raise SystemExit(f'obsolete anchor count {s.count(needle)}')
s=s.replace(needle,repl,1)
target.write_text(s,encoding='utf-8')
for path in [ROOT/'.github/v7-retirement/patch_builder.py',ROOT/'.github/workflows/patch-v7-builder.yml']:
    path.unlink(missing_ok=True)
print('v7 builder patched')
