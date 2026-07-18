#!/usr/bin/env python3
from __future__ import annotations
import shutil
import subprocess
import tempfile
from pathlib import Path
ROOT = Path(__file__).resolve().parents[2]
REPORT = ROOT / ".github" / "diagnostics" / "issue-171-check3-result.txt"
with tempfile.TemporaryDirectory(prefix="issue-171-check3-") as temp_dir:
    copy_root = Path(temp_dir) / "repository"
    shutil.copytree(ROOT, copy_root, ignore=shutil.ignore_patterns(".git"))
    result = subprocess.run(["python3", str(copy_root / ".github/development-packages/issue-171-final.py")], cwd=copy_root, text=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
    generated = (copy_root / "src/MissionChief_Map_Command_Toolkit.user.js").read_text(encoding="utf-8")
    start = generated.find("    function scanMissionRequirementsWindows()")
    end = generated.find("    function missionRequirementsScheduleDocumentRecords", start)
    excerpt = generated[start:end] if start >= 0 and end > start else "SCAN BLOCK NOT FOUND"
REPORT.parent.mkdir(parents=True, exist_ok=True)
REPORT.write_text(f"exit_code={result.returncode}\n\nOUTPUT\n{result.stdout}\n\nGENERATED SCAN\n{excerpt}\n", encoding="utf-8")
print(REPORT.relative_to(ROOT))
