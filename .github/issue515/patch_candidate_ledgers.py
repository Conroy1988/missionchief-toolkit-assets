#!/usr/bin/env python3
from __future__ import annotations

import hashlib
import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
SOURCE = ROOT / "src" / "MissionChief_Map_Command_Toolkit.user.js"
FIXTURE = ROOT / ".github" / "fixtures" / "main-style-source-headroom.json"
README = ROOT / "README.md"
PREBOOT = ROOT / ".github" / "scripts" / "test_issue454_preboot_state_order.py"
SELF = ROOT / ".github" / "issue515" / "patch_candidate_ledgers.py"


def main() -> int:
    text = SOURCE.read_text(encoding="utf-8")
    if "// @version      7.0.1" not in text or "version: '7.0.1'" not in text:
        raise SystemExit("v7.0.1 source was not prepared before ledger reconciliation")

    start = text.index("function installMainStyles()")
    template_start = text.index("addStyle(`", start) + len("addStyle(`")
    metric = text.index("recordStartupMetric('stylesheetInstallMs'", template_start)
    template_end = text.rfind("`);", template_start, metric)
    raw = text[template_start:template_end]
    lines = raw.split("\n")
    canonical = re.sub(
        r"\n[\t ]*}",
        "}",
        "\n".join(
            line
            for index, line in enumerate(lines)
            if not (0 < index < len(lines) - 1 and not line.strip())
        ),
    )

    fixture = json.loads(FIXTURE.read_text(encoding="utf-8"))
    candidate = fixture["v7Candidate"]
    candidate.update({
        "issue": 515,
        "version": "7.0.1",
        "sourceBytes": len(text.encode("utf-8")),
        "sourceLines": len(text.splitlines()),
        "sourceSha256": hashlib.sha256(text.encode("utf-8")).hexdigest(),
        "templateBytes": len(raw.encode("utf-8")),
        "templateLines": len(lines),
        "templateSha256": hashlib.sha256(raw.encode("utf-8")).hexdigest(),
        "canonicalCssSha256": hashlib.sha256(canonical.encode("utf-8")).hexdigest(),
    })
    FIXTURE.write_text(json.dumps(fixture, indent=2) + "\n", encoding="utf-8")

    readme = README.read_text(encoding="utf-8")
    marker = re.compile(
        r"Current verified release: `v[^`]+` · Development candidate: `v[^`]+`[^*\n]*"
    )
    replacement = "Current verified release: `v7.0.0` · Development candidate: `v7.0.1` — Emergency launcher restoration"
    readme, count = marker.subn(replacement, readme, count=1)
    if count != 1:
        raise SystemExit(f"Expected one README release-state marker, found {count}")
    README.write_text(readme, encoding="utf-8")

    preboot = PREBOOT.read_text(encoding="utf-8")
    old = "assert meta==runtime=='7.0.0'"
    new = "assert meta==runtime\nassert tuple(int(part) for part in meta.split('.')[:3]) >= (7,0,0)"
    if preboot.count(old) != 1:
        raise SystemExit("v7 preboot version assertion is not the expected baseline")
    PREBOOT.write_text(preboot.replace(old, new, 1), encoding="utf-8")

    SELF.unlink(missing_ok=True)
    try:
        SELF.parent.rmdir()
    except OSError:
        pass
    print("Issue #515 candidate ledgers reconciled.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
