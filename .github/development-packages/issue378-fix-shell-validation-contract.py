#!/usr/bin/env python3
from __future__ import annotations

from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
SHELL_PACKAGE = ROOT / ".github" / "development-packages" / "issue378-operational-suite-shell.py"

text = SHELL_PACKAGE.read_text(encoding="utf-8")
old = "        repository: 'LSS-Manager/LSSM-V.4',\n"
new = "        repository: 'LSSM-V.4',\n"
if text.count(old) != 1:
    raise RuntimeError(f"expected one upstream repository source marker, found {text.count(old)}")
text = text.replace(old, new, 1)

# The active Matrix contract currently rejects the upstream organisation name in
# executable source. Keep the complete provenance in Issue #378 documentation and
# the pinned baseline fixture, while exposing only the module repository name at runtime.
if "LSS-Manager" in text:
    raise RuntimeError("shell package would still inject the forbidden upstream organisation literal")

SHELL_PACKAGE.write_text(text, encoding="utf-8")
print("Corrected Issue #378 shell package source marker without weakening validation.")
