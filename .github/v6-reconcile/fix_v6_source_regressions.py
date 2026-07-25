#!/usr/bin/env python3
"""Apply exact post-retirement source corrections and refresh static evidence."""
from __future__ import annotations

import hashlib
import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
SOURCE = ROOT / "src" / "MissionChief_Map_Command_Toolkit.user.js"
EVIDENCE = ROOT / "docs" / "audits" / "v6-critical-performance-evidence.json"
BASELINE = ROOT / "docs" / "audits" / "v6-critical-performance-baseline.md"


def main() -> int:
    source = SOURCE.read_text(encoding="utf-8")
    old = "        if (state.cleanMode) closePanel();\n        applyRootAttributes();\n"
    new = "        if (state.cleanMode) closePanel();\n        saveState();\n        applyRootAttributes();\n"
    if old in source:
        if source.count(old) != 1:
            raise SystemExit("Unexpected toggle persistence insertion count")
        source = source.replace(old, new, 1)
        SOURCE.write_text(source, encoding="utf-8")
    elif new not in source:
        raise SystemExit("Shared toggle persistence anchor not found")

    raw = SOURCE.read_bytes()
    sha256 = hashlib.sha256(raw).hexdigest()
    line_count = raw.decode("utf-8").count("\n") + 1

    evidence = json.loads(EVIDENCE.read_text(encoding="utf-8"))
    evidence["candidate"]["sha256"] = sha256
    evidence["candidate"]["bytes"] = len(raw)
    evidence["candidate"]["lines"] = line_count
    EVIDENCE.write_text(json.dumps(evidence, indent=2) + "\n", encoding="utf-8")

    baseline = BASELINE.read_text(encoding="utf-8")
    baseline = re.sub(r"(?m)^\*\*Candidate canonical SHA-256:\*\* `[^`]+`", f"**Candidate canonical SHA-256:** `{sha256}`", baseline)
    baseline = re.sub(r"(?m)^\| Source bytes \| 2,060,765 \| [0-9,]+ \|", f"| Source bytes | 2,060,765 | {len(raw):,} |", baseline)
    baseline = re.sub(r"(?m)^\| Source lines \| 31,761 \| [0-9,]+ \|", f"| Source lines | 31,761 | {line_count:,} |", baseline)
    BASELINE.write_text(baseline, encoding="utf-8")

    print(json.dumps({"sha256": sha256, "bytes": len(raw), "lines": line_count}))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
