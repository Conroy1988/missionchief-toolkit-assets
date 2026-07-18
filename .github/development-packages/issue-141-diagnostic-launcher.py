#!/usr/bin/env python3
from __future__ import annotations

import runpy
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
PACKAGES = ROOT / ".github" / "development-packages"
TARGET = PACKAGES / "issue-141-mission-requirements-completeness.py"
PAYLOAD = PACKAGES / "issue-141-mission-requirements-completeness.payload.py"
DIAGNOSTIC = PACKAGES / "issue-141-diagnostic.py"

TARGET.replace(PAYLOAD)
TARGET.write_text(
    """#!/usr/bin/env python3
from __future__ import annotations
import runpy
import sys
from pathlib import Path
payload = Path(__file__).with_name('issue-141-mission-requirements-completeness.payload.py')
try:
    runpy.run_path(str(payload), run_name='__main__')
except BaseException as error:
    print(f'{type(error).__name__}: {error}', file=sys.stderr)
    raise SystemExit(1)
""",
    encoding="utf-8",
)
runpy.run_path(str(DIAGNOSTIC), run_name="__main__")
