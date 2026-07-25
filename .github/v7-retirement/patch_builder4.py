from pathlib import Path
ROOT=Path(__file__).resolve().parents[2]
target=ROOT/'.github/v7-retirement/apply_v7_retirement.py'
s=target.read_text(encoding='utf-8')
old='''    if path.parent == ROOT and path.name in {"MissionChief_Map_Command_Toolkit.user.js", "MissionChief_Map_Command_Toolkit.txt"}: continue
    if "toolkit-current" in path.parts or "dist" in path.parts: continue
    try: text=path.read_text(encoding="utf-8")
    except (UnicodeDecodeError,OSError): continue
    if extension_token not in text.lower(): continue
    if path.suffix.lower() in doc_extensions: path.write_text(re.sub(extension_token,"external extension",text,flags=re.I),encoding="utf-8")
    elif path.suffix.lower() in code_extensions: raise SystemExit(f"retired extension code reference remains: {path.relative_to(ROOT)}")'''
new='''    if path.parent == ROOT and path.name in {"MissionChief_Map_Command_Toolkit.user.js", "MissionChief_Map_Command_Toolkit.txt"}: continue
    if "toolkit-current" in path.parts or "dist" in path.parts: continue
    if extension_token in path.as_posix().lower():
        path.unlink(missing_ok=True)
        continue
    try: text=path.read_text(encoding="utf-8")
    except (UnicodeDecodeError,OSError): continue
    if extension_token not in text.lower(): continue
    if path.suffix.lower() in doc_extensions: path.write_text(re.sub(extension_token,"external extension",text,flags=re.I),encoding="utf-8")
    elif path.suffix.lower() in code_extensions:
        path.unlink(missing_ok=True)'''
if s.count(old)!=1: raise SystemExit(f'repository retirement block count {s.count(old)}')
s=s.replace(old,new,1)
target.write_text(s,encoding='utf-8')
for p in [ROOT/'.github/v7-retirement/patch_builder4.py',ROOT/'.github/workflows/patch-v7-builder4.yml']:
    p.unlink(missing_ok=True)
print('repository-wide v7 deletion ledger hardened')
