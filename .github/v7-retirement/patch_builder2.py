from pathlib import Path
ROOT=Path(__file__).resolve().parents[2]
target=ROOT/'.github/v7-retirement/apply_v7_retirement.py'
s=target.read_text(encoding='utf-8')
old='''        if path.parent == ROOT and path.name in {"MissionChief_Map_Command_Toolkit.user.js", "MissionChief_Map_Command_Toolkit.txt"}: continue
        if TOKEN in path.as_posix().lower(): tracked.append(path.as_posix())'''
new='''        if path.parent == ROOT and path.name in {"MissionChief_Map_Command_Toolkit.user.js", "MissionChief_Map_Command_Toolkit.txt"}: continue
        if "toolkit-current" in path.parts: continue
        if TOKEN in path.as_posix().lower(): tracked.append(path.as_posix())'''
if s.count(old)!=1: raise SystemExit(f'contract anchor {s.count(old)}')
s=s.replace(old,new,1)
old2='''    if path.parent == ROOT and path.name in {"MissionChief_Map_Command_Toolkit.user.js", "MissionChief_Map_Command_Toolkit.txt"}: continue
    try: text=path.read_text(encoding="utf-8")'''
new2='''    if path.parent == ROOT and path.name in {"MissionChief_Map_Command_Toolkit.user.js", "MissionChief_Map_Command_Toolkit.txt"}: continue
    if "toolkit-current" in path.parts: continue
    try: text=path.read_text(encoding="utf-8")'''
if s.count(old2)!=1: raise SystemExit(f'builder anchor {s.count(old2)}')
s=s.replace(old2,new2,1)
target.write_text(s,encoding='utf-8')
for p in [ROOT/'.github/v7-retirement/patch_builder2.py',ROOT/'.github/workflows/patch-v7-builder2.yml']:
 p.unlink(missing_ok=True)
