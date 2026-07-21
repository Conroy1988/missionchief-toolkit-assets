#!/usr/bin/env python3
from __future__ import annotations

import py_compile
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
V8 = ROOT / ".github/development-packages/issue-285-railway-responding-fix-v8.py"


def main() -> int:
    payload = V8.read_text(encoding="utf-8")
    old = '+ "\\\\n", encoding="utf-8")'
    new = '+ "\\\\\\\\n", encoding="utf-8")'
    count = payload.count(old)
    if count != 1:
        raise RuntimeError(f"nested newline escape: expected one match, found {count}")
    V8.write_text(payload.replace(old, new, 1), encoding="utf-8")
    py_compile.compile(str(V8), doraise=True)
    subprocess.run(["python3", str(V8)], cwd=ROOT, check=True)
    for path in (
        V8,
        ROOT / "docs/issue-285-v8-diagnostic.txt",
    ):
        path.unlink(missing_ok=True)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
