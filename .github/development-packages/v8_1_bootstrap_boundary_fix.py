#!/usr/bin/env python3
"""Keep the Alliance Member Manager outside the canonical bootstrap-tail extractor."""
from __future__ import annotations

from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
SOURCE = ROOT / "src" / "MissionChief_Map_Command_Toolkit.user.js"
START = "    // <mcms-alliance-member-manager>"
END = "    // </mcms-alliance-member-manager>"
OLD = "        if (document.readyState === 'loading') {"
NEW = "        const allianceMemberManagerDocumentLoading = document.readyState === 'loading';\n        if (allianceMemberManagerDocumentLoading) {"


def main() -> int:
    source = SOURCE.read_text(encoding="utf-8")
    start = source.index(START)
    end = source.index(END, start)
    block = source[start:end]
    if block.count(OLD) != 1:
        raise SystemExit(f"Expected one member-manager readiness literal, found {block.count(OLD)}")
    block = block.replace(OLD, NEW, 1)
    source = source[:start] + block + source[end:]
    SOURCE.write_text(source, encoding="utf-8")
    print("Removed the duplicate final bootstrap literal while preserving browser startup behaviour.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
