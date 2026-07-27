#!/usr/bin/env python3
"""Move the v8.1.0 Alliance Member Manager before the canonical document-start bootstrap."""
from __future__ import annotations

import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
SOURCE = ROOT / "src" / "MissionChief_Map_Command_Toolkit.user.js"
HEADROOM = ROOT / ".github" / "fixtures" / "main-style-source-headroom.json"

EXPECTED_SOURCE_SHA256 = "549ad43f6c5c0b1aaaf2d7794bca0ccb0e689b69357ea6ca52e3deb400bfbf85"
EXPECTED_FIXED_SHA256 = "a4f5bf16ca9a751694e2dff090b07f984a22d757510f204ec4b90ac22f0513f1"
EXPECTED_BYTES = 1_641_511
EXPECTED_LINES = 25_006

MODULE_START = "    // <mcms-alliance-member-manager>"
MODULE_END = "    // </mcms-alliance-member-manager>\n"
BOOTSTRAP = """    if (document.readyState === 'loading') {
        runtimeListen(document, 'DOMContentLoaded', scheduleBoot, { once: true });
    } else {
        scheduleBoot();
    }

"""


def main() -> int:
    source = SOURCE.read_text(encoding="utf-8")
    source_sha = hashlib.sha256(source.encode()).hexdigest()
    if source_sha != EXPECTED_SOURCE_SHA256:
        raise SystemExit(f"Unexpected v8.1.0 source authority: {source_sha}")

    bootstrap_start = source.rfind(BOOTSTRAP)
    module_start = source.index(MODULE_START, bootstrap_start)
    module_end = source.index(MODULE_END, module_start) + len(MODULE_END)
    if bootstrap_start < 0 or bootstrap_start + len(BOOTSTRAP) != module_start:
        raise SystemExit("Alliance Member Manager is not directly after the canonical bootstrap")
    if not source[module_end:].startswith("})();"):
        raise SystemExit("Alliance Member Manager is not the final module before userscript closure")

    module = source[module_start:module_end]
    fixed = source[:bootstrap_start] + module + BOOTSTRAP + source[module_end:]
    fixed_sha = hashlib.sha256(fixed.encode()).hexdigest()
    if fixed_sha != EXPECTED_FIXED_SHA256:
        raise SystemExit(f"Unexpected fixed source hash: {fixed_sha}")
    if len(fixed.encode()) != EXPECTED_BYTES or len(fixed.splitlines()) != EXPECTED_LINES:
        raise SystemExit("Module placement changed the reviewed source footprint")
    if fixed.rfind("if (document.readyState === 'loading')") != fixed.rfind(BOOTSTRAP) + 4:
        raise SystemExit("Canonical bootstrap is not the final document-ready boundary")
    SOURCE.write_text(fixed, encoding="utf-8")

    fixture = json.loads(HEADROOM.read_text(encoding="utf-8"))
    candidate = fixture["v8Candidate"]
    if candidate.get("issue") != 551 or candidate.get("version") != "8.1.0":
        raise SystemExit("v8.1.0 source-headroom authority is missing")
    if candidate.get("sourceSha256") != EXPECTED_SOURCE_SHA256:
        raise SystemExit("v8.1.0 source-headroom pre-fix hash changed")
    candidate["sourceSha256"] = EXPECTED_FIXED_SHA256
    candidate["scope"] = (
        "Issue #551 native Alliance Member Manager with opt-in English role/activity controls, "
        "explicit sequential member-page loading, deterministic teardown and canonical boot-tail isolation"
    )
    HEADROOM.write_text(json.dumps(fixture, indent=2) + "\n", encoding="utf-8")

    print("Moved Alliance Member Manager before the canonical document-start bootstrap without changing source size or line count.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
