#!/usr/bin/env python3
from __future__ import annotations

import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
V2 = ROOT / ".github/development-packages/issue-253-main-style-headroom-v2.py"
RUNTIME = ROOT / ".github/development-packages/.issue-253-main-style-headroom-v3-runtime.py"

OLD = '''    cursor = function_start
    raw = None
    while True:
        assignment = text.find(ASSIGNMENT, cursor)
        if assignment < 0:
            break
        template_start = assignment + len(ASSIGNMENT)
        closing = text.find("`;", template_start)
        if closing < 0:
            break
        candidate = text[template_start:closing]
        if len(candidate.encode("utf-8")) > 800000:
            if raw is not None:
                fail("multiple main stylesheet template candidates were found")
            raw = candidate
        cursor = closing + 2
    if raw is None:
        fail("reviewed main stylesheet template is missing")
'''
NEW = '''    raw = None
    assignment_pattern = re.compile(r"[A-Za-z_$][A-Za-z0-9_$]*\\.textContent\\s*=\\s*`")
    for match in assignment_pattern.finditer(text, function_start):
        template_start = match.end()
        closing = text.find("`;", template_start)
        if closing < 0:
            continue
        candidate = text[template_start:closing]
        if len(candidate.encode("utf-8")) <= 800000:
            continue
        if raw is not None:
            fail("multiple main stylesheet template candidates were found")
        raw = candidate
    if raw is None:
        fail("reviewed main stylesheet template is missing")
'''


def main() -> int:
    payload = V2.read_text(encoding="utf-8")
    count = payload.count(OLD)
    if count != 1:
        raise RuntimeError(f"stylesheet locator replacement expected one match, found {count}")
    RUNTIME.write_text(payload.replace(OLD, NEW, 1), encoding="utf-8")
    try:
        subprocess.run(["python3", str(RUNTIME)], cwd=ROOT, check=True)
    finally:
        RUNTIME.unlink(missing_ok=True)
    for path in (
        V2,
        ROOT / ".github/development-packages/issue-253-v4-diagnostic.py",
        ROOT / "docs/issue-253-v4-package-diagnostic.txt",
    ):
        path.unlink(missing_ok=True)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
