#!/usr/bin/env python3
"""Add exact source-context evidence for Issue #117 theme identity review."""

from __future__ import annotations

import json
import re
from pathlib import Path

SOURCE = Path("src/MissionChief_Map_Command_Toolkit.user.js")
OUTPUT = Path("status/theme-id-evidence.json")

DISPLAY_NAMES = [
    "Map Command",
    "Cyberpunk",
    "Fallout 4",
    "Umbrella",
    "Factorio",
    "007 Intelligence",
    "Hyrule Command",
]

CANDIDATE_PATTERN = re.compile(
    r"(?:(?:id|key|value|theme|themeId|uiTheme|label|name)\s*:\s*|value\s*=\s*)"
    r"(?P<q>['\"])(?P<value>[^'\"\r\n]{1,80})(?P=q)",
    re.IGNORECASE,
)
QUOTED_TOKEN_PATTERN = re.compile(r"(?P<q>['\"])(?P<value>[A-Za-z][A-Za-z0-9_-]{1,40})(?P=q)")


def main() -> None:
    if not SOURCE.is_file():
        raise RuntimeError(f"Missing canonical source: {SOURCE}")
    if OUTPUT.exists():
        raise RuntimeError(f"Evidence output already exists: {OUTPUT}")

    source = SOURCE.read_text(encoding="utf-8", errors="replace")
    lines = source.splitlines()
    evidence: dict[str, object] = {
        "schemaVersion": 1,
        "generatedAt": "2026-07-17",
        "issue": 117,
        "source": SOURCE.as_posix(),
        "displayNames": {},
    }

    for display_name in DISPLAY_NAMES:
        occurrences = []
        for index, line in enumerate(lines):
            if display_name not in line:
                continue
            start = max(0, index - 6)
            end = min(len(lines), index + 7)
            context_lines = lines[start:end]
            context = "\n".join(context_lines)
            property_candidates = sorted({match.group("value") for match in CANDIDATE_PATTERN.finditer(context)})
            quoted_tokens = sorted({match.group("value") for match in QUOTED_TOKEN_PATTERN.finditer(context)})
            occurrences.append(
                {
                    "line": index + 1,
                    "contextStartLine": start + 1,
                    "contextEndLine": end,
                    "propertyCandidates": property_candidates,
                    "quotedTokens": quoted_tokens,
                    "context": context,
                }
            )
        evidence["displayNames"][display_name] = {
            "occurrenceCount": len(occurrences),
            "occurrences": occurrences[:12],
        }

    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    OUTPUT.write_text(json.dumps(evidence, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(f"Wrote {OUTPUT} with exact source contexts for {len(DISPLAY_NAMES)} interface systems")


if __name__ == "__main__":
    main()
