#!/usr/bin/env python3
from pathlib import Path
import re
import sys

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / ".github" / "scripts"))
import full_userscript_audit as audit

source = (ROOT / "src" / "MissionChief_Map_Command_Toolkit.user.js").read_text(encoding="utf-8")
masked = audit.mask_non_code(source)


def extract(name: str) -> str:
    pattern = re.compile(rf"\b(?:async\s+)?function\s+{re.escape(name)}\s*\(")
    matches = list(pattern.finditer(masked))
    if len(matches) != 1:
        raise RuntimeError(f"Expected one declaration for {name}, found {len(matches)}")
    start = matches[0].start()
    open_pos = masked.find("{", start)
    close_pos = audit.matching_brace(masked, open_pos)
    if close_pos is None:
        raise RuntimeError(f"Could not match closing brace for {name}")
    return source[start:close_pos + 1]

content = "\n\n".join(extract(name) for name in (
    "normaliseMissionId",
    "normaliseMissionOverlayRecord",
    "captureMissionMarkerData",
)) + "\n"
output = ROOT / ".github" / "diagnostics" / "issue346-marker-candidate-boundary.txt"
output.parent.mkdir(parents=True, exist_ok=True)
output.write_text(content, encoding="utf-8")
print("Exported current mission-marker candidate boundary for Issue #346")
