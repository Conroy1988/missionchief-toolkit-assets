from pathlib import Path
ROOT=Path(__file__).resolve().parents[2]
target=ROOT/'.github/v7-retirement/apply_v7_retirement.py'
s=target.read_text(encoding='utf-8')
old='''        if path.parent == ROOT and path.name in {"MissionChief_Map_Command_Toolkit.user.js", "MissionChief_Map_Command_Toolkit.txt"}: continue
        if "toolkit-current" in path.parts: continue
        if TOKEN in path.as_posix().lower(): tracked.append(path.as_posix())'''
new='''        if path.parent == ROOT and path.name in {"MissionChief_Map_Command_Toolkit.user.js", "MissionChief_Map_Command_Toolkit.txt"}: continue
        if "toolkit-current" in path.parts or "dist" in path.parts: continue
        if TOKEN in path.as_posix().lower(): tracked.append(path.as_posix())'''
if s.count(old)!=1: raise SystemExit(f'v7 source contract boundary count {s.count(old)}')
s=s.replace(old,new,1)
old2='''validate=validate[:run_start]+new_gate+validate[run_end:];validate_path.write_text(validate,encoding="utf-8")'''
new2='''validate=validate[:run_start]+new_gate+validate[run_end:]
dist_anchor = "    USER_JS.write_bytes(raw)\\n    TXT.write_bytes(raw)\\n"
dist_guard = dist_anchor + "\\n    retired_extension_token = \\\"ls\\\" + \\\"sm\\\"\\n    if retired_extension_token in USER_JS.read_text(encoding=\\\"utf-8\\\").lower() or retired_extension_token in TXT.read_text(encoding=\\\"utf-8\\\").lower():\\n        fail(\\\"retired integration content remains in generated distribution\\\")\\n"
if validate.count(dist_anchor) != 1:
    raise SystemExit(f"distribution guard anchor count {validate.count(dist_anchor)}")
validate = validate.replace(dist_anchor, dist_guard, 1)
validate_path.write_text(validate,encoding="utf-8")'''
if s.count(old2)!=1: raise SystemExit(f'validate write anchor count {s.count(old2)}')
s=s.replace(old2,new2,1)
target.write_text(s,encoding='utf-8')
for p in [ROOT/'.github/v7-retirement/patch_builder7.py',ROOT/'.github/workflows/patch-v7-builder7.yml']:
    p.unlink(missing_ok=True)
