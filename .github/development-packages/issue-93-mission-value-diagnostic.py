#!/usr/bin/env python3
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
SOURCE = ROOT / "src" / "MissionChief_Map_Command_Toolkit.user.js"
OUTPUT = ROOT / ".github" / "diagnostics" / "issue-93-mission-value-context.txt"

TERMS = [
    "mission_value",
    "missionValue",
    "mission window",
    "mission-window",
    "missionWindow",
    "iframe",
    "MutationObserver",
    "missions/",
    "makeToggleButton",
    "const DEFAULT_STATE",
    "normaliseLoadedState",
    "data-setting",
    "missionInspector",
    "transportWatcher",
    "missionSpawn",
    "currency",
    "Intl.NumberFormat",
]


def context(lines, index, radius=10):
    start = max(0, index - radius)
    end = min(len(lines), index + radius + 1)
    return "\n".join(f"{line_no + 1:6d}: {lines[line_no]}" for line_no in range(start, end))


def main():
    lines = SOURCE.read_text(encoding="utf-8").splitlines()
    blocks = []
    for term in TERMS:
        hits = [i for i, line in enumerate(lines) if term.lower() in line.lower()]
        blocks.append(f"### {term} · {len(hits)} matches")
        for index in hits[:20]:
            blocks.append(context(lines, index))
            blocks.append("")
    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    OUTPUT.write_text("\n".join(blocks), encoding="utf-8")
    print(f"Wrote {OUTPUT.relative_to(ROOT)}")


if __name__ == "__main__":
    main()
