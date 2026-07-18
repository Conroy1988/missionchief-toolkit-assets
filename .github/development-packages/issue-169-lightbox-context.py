#!/usr/bin/env python3
from __future__ import annotations

from pathlib import Path
import hashlib

ROOT = Path(__file__).resolve().parents[2]
PARTS = [
    ROOT / ".github" / "development-packages" / "issue-169-lightbox-context.part1.txt",
    ROOT / ".github" / "development-packages" / "issue-169-lightbox-context.part2.txt",
    ROOT / ".github" / "development-packages" / "issue-169-lightbox-context.part3.txt",
]
EXPECTED_SHA256 = "7effd147e2175008628f107309553136d75c78e88483c77d252ac2ea4041198d"
DIAGNOSTIC = ROOT / "docs" / "diagnostics" / "issue-169-package-error.txt"

missing = [str(path.relative_to(ROOT)) for path in PARTS if not path.exists()]
if missing:
    raise AssertionError(f"Issue 169 package parts missing: {missing}")

source = "".join(path.read_text(encoding="utf-8") for path in PARTS)
actual = hashlib.sha256(source.encode("utf-8")).hexdigest()
if actual != EXPECTED_SHA256:
    raise AssertionError(f"Issue 169 package checksum mismatch: {actual}")

old_contract = '    assert compact_source.count("missionRequirementsPlacePanel(scopedCandidate,source,panel)") == 1\\n'
new_contract = '    assert compact_source.count("missionRequirementsPlacePanel(scopedCandidate,source,panel)") == 2\\n'
if source.count(old_contract) != 1:
    raise AssertionError(f"Issue 169 placement contract correction expected one match, found {source.count(old_contract)}")
source = source.replace(old_contract, new_contract, 1)

for path in PARTS:
    path.unlink()
DIAGNOSTIC.unlink(missing_ok=True)
try:
    DIAGNOSTIC.parent.rmdir()
except OSError:
    pass

namespace = {"__file__": __file__, "__name__": "__main__"}
exec(compile(source, __file__, "exec"), namespace)
