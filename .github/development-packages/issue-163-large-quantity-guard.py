#!/usr/bin/env python3
from __future__ import annotations

from pathlib import Path
import hashlib
import json
import subprocess

ROOT = Path(__file__).resolve().parents[2]
SRC = ROOT / "src" / "MissionChief_Map_Command_Toolkit.user.js"
FIXTURE = ROOT / ".github" / "fixtures" / "mission-catalogue-pages.json"
RUNTIME = ROOT / ".github" / "scripts" / "test_mission_requirements_runtime.js"
CONTRACT = ROOT / ".github" / "scripts" / "test_mission_requirements_contract.py"


def replace_once(text: str, old: str, new: str, label: str) -> str:
    count = text.count(old)
    if count != 1:
        raise AssertionError(f"{label}: expected one match, found {count}")
    return text.replace(old, new, 1)


def run(*cmd: str) -> None:
    subprocess.run(cmd, cwd=ROOT, check=True)


source = SRC.read_text(encoding="utf-8")
source = replace_once(
    source,
    r"const quantityMatch = rawValue.match(/^\s*(\d{1,3}(?:[\s,.]\d{3})*|\d+)/u);",
    r"const quantityMatch = rawValue.match(/^\s*(\d+(?:[\s,.]\d{3})*)/u);",
    "catalogue leading quantity parser",
)
SRC.write_text(source, encoding="utf-8")

fixture = json.loads(FIXTURE.read_text(encoding="utf-8"))
case = next(page for page in fixture["pages"] if page["name"] == "alternative and conditional requirements")
rows = case["sections"]["requirements"]
if ["Required Firefighters", "1000"] not in rows:
    rows.append(["Required Firefighters", "1000"])
case["expected"]["firefighters"] = 1000
FIXTURE.write_text(json.dumps(fixture, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")

canonical = SRC.read_bytes()
for path in [ROOT / "dist" / "MissionChief_Map_Command_Toolkit.user.js", ROOT / "dist" / "MissionChief_Map_Command_Toolkit.txt"]:
    path.write_bytes(canonical)
digest = hashlib.sha256(canonical).hexdigest()
(ROOT / "dist" / "SHA256SUMS.txt").write_text(
    f"{digest}  MissionChief_Map_Command_Toolkit.user.js\n{digest}  MissionChief_Map_Command_Toolkit.txt\n",
    encoding="utf-8",
)
manifest_path = ROOT / "dist" / "release-manifest.json"
manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
manifest["sha256"] = digest
manifest["bytes"] = len(canonical)
manifest["lines"] = canonical.count(b"\n")
manifest_path.write_text(json.dumps(manifest, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")

run("node", "--check", str(SRC.relative_to(ROOT)))
run("node", str(RUNTIME.relative_to(ROOT)))
run("python3", str(CONTRACT.relative_to(ROOT)))
print(f"Issue #163 large-quantity guard passed: sha256={digest}")
