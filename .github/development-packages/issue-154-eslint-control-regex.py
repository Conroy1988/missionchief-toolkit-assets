#!/usr/bin/env python3
from pathlib import Path
import hashlib
import json
import subprocess

ROOT = Path(__file__).resolve().parents[2]
SRC = ROOT / "src" / "MissionChief_Map_Command_Toolkit.user.js"
DIST_USER = ROOT / "dist" / "MissionChief_Map_Command_Toolkit.user.js"
DIST_TXT = ROOT / "dist" / "MissionChief_Map_Command_Toolkit.txt"
MANIFEST = ROOT / "dist" / "release-manifest.json"
source = SRC.read_text(encoding="utf-8")
old = "let text = String(value ?? '').replace(/[\\u0000-\\u001f\\u007f]+/g, ' ').replace(/\\s+/g, ' ').trim();"
new = "let text = Array.from(String(value ?? ''), ch => { const code = ch.charCodeAt(0); return code < 32 || code === 127 ? ' ' : ch; }).join('').replace(/\\s+/g, ' ').trim();"
if source.count(old) != 1:
    raise AssertionError(f"Expected one sanitizer control-regex marker, found {source.count(old)}")
source = source.replace(old, new, 1)
SRC.write_text(source, encoding="utf-8")
canonical = SRC.read_bytes()
if len(canonical) > 1_900_000 or canonical.count(b"\n") > 31_000:
    raise AssertionError(f"Candidate outside performance envelope: {len(canonical)} bytes / {canonical.count(b'\n')} lines")
DIST_USER.write_bytes(canonical)
DIST_TXT.write_bytes(canonical)
digest = hashlib.sha256(canonical).hexdigest()
(ROOT / "dist" / "SHA256SUMS.txt").write_text(
    f"{digest}  MissionChief_Map_Command_Toolkit.user.js\n{digest}  MissionChief_Map_Command_Toolkit.txt\n",
    encoding="utf-8",
)
manifest = json.loads(MANIFEST.read_text(encoding="utf-8"))
manifest["sha256"] = digest
manifest["bytes"] = len(canonical)
manifest["lines"] = canonical.count(b"\n")
MANIFEST.write_text(json.dumps(manifest, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
for command in (
    ["node", "--check", str(SRC.relative_to(ROOT))],
    ["node", ".github/scripts/test_mission_requirements_runtime.js"],
    ["python3", ".github/scripts/test_mission_requirements_contract.py"],
    ["python3", ".github/scripts/validate_userscript.py"],
):
    subprocess.run(command, cwd=ROOT, check=True)
print(f"Issue #154 ESLint correction passed: {len(canonical)} bytes, sha256={digest}")
