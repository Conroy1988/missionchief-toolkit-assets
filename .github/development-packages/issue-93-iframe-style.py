#!/usr/bin/env python3
from __future__ import annotations

import hashlib
import json
import os
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
SOURCE = ROOT / "src" / "MissionChief_Map_Command_Toolkit.user.js"
DIST_USER = ROOT / "dist" / "MissionChief_Map_Command_Toolkit.user.js"
DIST_TEXT = ROOT / "dist" / "MissionChief_Map_Command_Toolkit.txt"
SUMS = ROOT / "dist" / "SHA256SUMS.txt"
MANIFEST = ROOT / "dist" / "release-manifest.json"
CONTRACT = ROOT / ".github" / "scripts" / "test_mission_value_contract.py"


def replace_once(text: str, old: str, new: str, label: str) -> str:
    count = text.count(old)
    if count != 1:
        raise AssertionError(f"{label}: expected one match, found {count}")
    return text.replace(old, new, 1)


source = SOURCE.read_text(encoding="utf-8")
iframe_style_functions = r'''    function ensureMissionValueDocumentStyle(doc) {
        if (!doc || doc === document) return;
        const styleId = 'mcms-mission-value-document-style';
        if (doc.getElementById?.(styleId)) return;
        const style = doc.createElement?.('style');
        if (!style) return;
        style.id = styleId;
        style.textContent = `
            .mcms-mission-value-row {
                display:flex !important;align-items:center !important;justify-content:flex-end !important;
                width:100% !important;min-height:30px !important;box-sizing:border-box !important;
                margin:0 0 8px 0 !important;padding:5px 46px 5px 8px !important;clear:both !important;
                position:relative !important;z-index:2 !important;pointer-events:none !important;
            }
            .mcms-mission-value-badge {
                display:inline-flex !important;align-items:center !important;justify-content:center !important;
                max-width:min(100%,260px) !important;min-height:25px !important;box-sizing:border-box !important;
                padding:4px 10px !important;border:1px solid rgba(235,190,64,.72) !important;border-radius:8px !important;
                background:linear-gradient(145deg,rgba(48,39,13,.96),rgba(19,21,24,.96)) !important;
                color:#ffe59a !important;box-shadow:0 2px 8px rgba(0,0,0,.34) !important;
                font:900 11px/1.25 Arial,Helvetica,sans-serif !important;letter-spacing:.15px !important;
                text-align:right !important;white-space:nowrap !important;overflow:hidden !important;
                text-overflow:ellipsis !important;pointer-events:none !important;
            }
            @media (max-width:520px) {
                .mcms-mission-value-row { padding-right:40px !important; }
                .mcms-mission-value-badge { max-width:100% !important;font-size:10px !important; }
            }
        `;
        (doc.head || doc.documentElement)?.appendChild(style);
    }

    function clearMissionValueDocumentStyles() {
        for (const context of transportSweepDocumentContexts()) {
            if (context.doc === document) continue;
            try { context.doc.getElementById?.('mcms-mission-value-document-style')?.remove(); } catch (err) {}
        }
    }

'''
source = replace_once(
    source,
    "    function observeMissionValueFrame(frame) {",
    iframe_style_functions + "    function observeMissionValueFrame(frame) {",
    "iframe style helpers",
)
source = replace_once(
    source,
    "    function observeMissionValueDocument(doc) {\n        if (!doc || missionValueObservedDocuments.has(doc)) return;",
    "    function observeMissionValueDocument(doc) {\n        if (!doc) return;\n        ensureMissionValueDocumentStyle(doc);\n        if (missionValueObservedDocuments.has(doc)) return;",
    "iframe style installation",
)
source = replace_once(
    source,
    "                clearMissionValueIndicators();\n            });",
    "                clearMissionValueIndicators();\n                clearMissionValueDocumentStyles();\n            });",
    "iframe style cleanup",
)
SOURCE.write_text(source, encoding="utf-8")

contract = CONTRACT.read_text(encoding="utf-8")
contract = replace_once(
    contract,
    '        "installMissionValueWindows()",\n',
    '        "installMissionValueWindows()",\n'
    '        "ensureMissionValueDocumentStyle(doc)",\n'
    '        "clearMissionValueDocumentStyles()",\n'
    '        "mcms-mission-value-document-style",\n',
    "iframe style contract fragments",
)
CONTRACT.write_text(contract, encoding="utf-8")

payload = SOURCE.read_bytes()
digest = hashlib.sha256(payload).hexdigest()
DIST_USER.write_bytes(payload)
DIST_TEXT.write_bytes(payload)
SUMS.write_text(
    f"{digest}  MissionChief_Map_Command_Toolkit.user.js\n{digest}  MissionChief_Map_Command_Toolkit.txt\n",
    encoding="utf-8",
)
manifest = json.loads(MANIFEST.read_text(encoding="utf-8"))
manifest["sha256"] = digest
manifest["bytes"] = len(payload)
manifest["lines"] = len(source.splitlines())
MANIFEST.write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")

env = dict(os.environ)
env["PYTHONDONTWRITEBYTECODE"] = "1"
subprocess.run(["node", "--check", str(SOURCE)], cwd=ROOT, check=True, env=env)
subprocess.run(["python3", str(CONTRACT)], cwd=ROOT, check=True, env=env)
subprocess.run(["python3", str(ROOT / ".github" / "scripts" / "test_settings_ui_contract.py")], cwd=ROOT, check=True, env=env)
print(f"Mission Value iframe styling contract passed: {digest}")
