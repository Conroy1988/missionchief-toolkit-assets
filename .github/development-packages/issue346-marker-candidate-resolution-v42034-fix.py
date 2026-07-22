#!/usr/bin/env python3
from pathlib import Path
import runpy

ROOT = Path(__file__).resolve().parents[2]
PACKAGE = ROOT / ".github" / "development-packages" / "issue346-marker-candidate-resolution-v42034.py"
text = PACKAGE.read_text(encoding="utf-8")
old = "        if (Array.isArray(payload)) return payload.flatMap(resolveMissionMarkerCandidates);\n"
new = "        if (Array.isArray(payload)) {\n        return payload.flatMap(resolveMissionMarkerCandidates);\n        }\n"
if text.count(old) != 1:
    raise RuntimeError(f"Expected one compact array branch, found {text.count(old)}")
PACKAGE.write_text(text.replace(old, new, 1), encoding="utf-8")
runpy.run_path(str(PACKAGE), run_name="__main__")
PACKAGE.unlink()
print("Applied Issue #346 source-headroom accounting correction")
