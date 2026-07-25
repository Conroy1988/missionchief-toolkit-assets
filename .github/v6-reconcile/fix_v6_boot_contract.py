#!/usr/bin/env python3
"""Remove retired v6 lifecycle ownership from the boot fixture."""
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
PATH = ROOT / ".github" / "fixtures" / "boot-lifecycle-contract.json"


def main() -> int:
    data = json.loads(PATH.read_text(encoding="utf-8"))
    retired = {
        "data-mcms-critical-view",
        "auto-night",
        "critical-countdowns",
        "pointerover",
        "pointermove",
        "pointerout",
        "criticalMissionStableCache",
        "clearCoverageHeatmap",
    }
    for key, value in data.items():
        if isinstance(value, list):
            data[key] = [item for item in value if item not in retired]
    PATH.write_text(json.dumps(data, indent=2) + "\n", encoding="utf-8")
    print("v6 boot fixture retired ownership removed")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
