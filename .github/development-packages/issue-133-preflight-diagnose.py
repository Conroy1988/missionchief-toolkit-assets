#!/usr/bin/env python3
from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

ROOT = Path.cwd()
OUTPUT = ROOT / "docs" / "issue-133-preflight-diagnostics.json"
CONTRACTS = [
    ".github/scripts/test_financial_ledger_contract.py",
    ".github/scripts/test_financial_discord_image_layout_contract.py",
    ".github/scripts/test_mission_marker_ingestion_contract.py",
    ".github/scripts/test_boot_lifecycle_contract.py",
    ".github/scripts/test_settings_ui_contract.py",
    ".github/scripts/test_desktop_panel_layout_contract.py",
    ".github/scripts/test_section_navigation_contract.py",
    ".github/scripts/test_mission_value_contract.py",
    ".github/scripts/test_transport_sweep_lssm_contract.py",
    ".github/scripts/test_mission_requirements_contract.py",
]

results = []
for relative in CONTRACTS:
    result = subprocess.run([sys.executable, relative], cwd=ROOT, text=True, capture_output=True)
    results.append({
        "contract": relative,
        "returncode": result.returncode,
        "stdout": result.stdout[-4000:],
        "stderr": result.stderr[-4000:],
    })

syntax = subprocess.run(["node", "--check", "src/MissionChief_Map_Command_Toolkit.user.js"], cwd=ROOT, text=True, capture_output=True)
results.append({"contract": "node --check", "returncode": syntax.returncode, "stdout": syntax.stdout, "stderr": syntax.stderr})
OUTPUT.parent.mkdir(parents=True, exist_ok=True)
OUTPUT.write_text(json.dumps({"results": results}, indent=2) + "\n", encoding="utf-8")
print(f"Wrote {OUTPUT.relative_to(ROOT)}; failures={sum(item['returncode'] != 0 for item in results)}")
