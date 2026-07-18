#!/usr/bin/env python3
from pathlib import Path
import hashlib
import json
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[2]
SRC = ROOT / "src" / "MissionChief_Map_Command_Toolkit.user.js"
DIST_USER = ROOT / "dist" / "MissionChief_Map_Command_Toolkit.user.js"
DIST_TXT = ROOT / "dist" / "MissionChief_Map_Command_Toolkit.txt"
MANIFEST = ROOT / "dist" / "release-manifest.json"
TEST = ROOT / ".github" / "scripts" / "test_mission_requirements_runtime.js"
CONTRACT = ROOT / ".github" / "scripts" / "test_mission_requirements_contract.py"
sys.path.insert(0, str(ROOT / ".github" / "scripts"))
from full_userscript_audit import mask_non_code

source = SRC.read_text(encoding="utf-8")
if "// @version      4.15.4" not in source:
    raise AssertionError("Expected v4.15.4 candidate")

lines = source.splitlines(keepends=True)
masked_lines = mask_non_code(source).splitlines(keepends=True)
if len(lines) != len(masked_lines):
    raise AssertionError("Lexical mask line parity failed")

saved = 0
dedented = []
for raw, masked in zip(lines, masked_lines):
    if saved < 13200 and raw.startswith("            ") and masked.strip():
        raw = raw[4:]
        saved += 4
    dedented.append(raw)

compacted = "".join(dedented)
lines = compacted.splitlines(keepends=True)
masked_lines = mask_non_code(compacted).splitlines(keepends=True)
remove = set()
for index in range(1, len(lines) - 1):
    if len(remove) >= 60:
        break
    if lines[index].strip():
        continue
    if masked_lines[index - 1].strip() and masked_lines[index + 1].strip():
        remove.add(index)
compacted = "".join(line for index, line in enumerate(lines) if index not in remove)

if saved < 12300:
    raise AssertionError(f"Insufficient safe indentation headroom: {saved} bytes")
if len(remove) < 39:
    raise AssertionError(f"Insufficient safe code-separator lines: {len(remove)}")

SRC.write_text(compacted, encoding="utf-8")
canonical = SRC.read_bytes()
if len(canonical) > 1_900_000:
    raise AssertionError(f"Compacted candidate remains above byte limit: {len(canonical)}")
if canonical.count(b"\n") > 31_000:
    raise AssertionError(f"Compacted candidate remains above line limit: {canonical.count(b'\n')}")
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
    ["node", str(TEST.relative_to(ROOT))],
    ["python3", str(CONTRACT.relative_to(ROOT))],
    ["python3", ".github/scripts/validate_userscript.py"],
):
    subprocess.run(command, cwd=ROOT, check=True)
print(f"Lexical compaction passed: saved={saved}, removed_lines={len(remove)}, bytes={len(canonical)}, lines={canonical.count(b'\n')}, sha256={digest}")
