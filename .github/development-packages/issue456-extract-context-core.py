#!/usr/bin/env python3
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
SOURCE = ROOT / "src" / "MissionChief_Map_Command_Toolkit.user.js"
REPORT = ROOT / ".github" / "diagnostics" / "issue456-context-core.txt"
lines = SOURCE.read_text(encoding="utf-8").splitlines()
needles = ["const operationalSuiteContexts", "operationalSuiteContexts.set", "operationalSuiteContexts.get", "function installOperationalSuiteShell"]
indices = []
for needle in needles:
    indices.extend(i for i, line in enumerate(lines) if needle in line)
out = []
for index in sorted(set(indices)):
    start = max(0, index - 80)
    end = min(len(lines), index + 161)
    out.append(f"===== MATCH line {index + 1}: {lines[index]} =====")
    out.extend(f"{i + 1:05d}: {lines[i]}" for i in range(start, end))
REPORT.parent.mkdir(parents=True, exist_ok=True)
REPORT.write_text("\n".join(out) + "\n", encoding="utf-8")
print(f"matches={len(indices)} lines={len(out)}")
