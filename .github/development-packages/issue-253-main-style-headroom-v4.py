#!/usr/bin/env python3
from __future__ import annotations

import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
V3 = ROOT / ".github/development-packages/issue-253-main-style-headroom-v3.py"
RUNTIME = ROOT / ".github/development-packages/.issue-253-main-style-headroom-v4-runtime.py"

OLD = '''    raw = None
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
NEW = '''    add_style = text.find("addStyle(`", function_start)
    if add_style < 0:
        fail("installMainStyles addStyle template opening is missing")
    template_start = add_style + len("addStyle(`")
    end_anchor = text.find("recordStartupMetric('stylesheetInstallMs'", template_start)
    if end_anchor < 0:
        fail("installMainStyles startup metric anchor is missing")
    closing = text.rfind("`);", template_start, end_anchor)
    if closing < 0:
        fail("installMainStyles addStyle template closing is missing")
    raw = text[template_start:closing]
    if len(raw.encode("utf-8")) <= 800000:
        fail("reviewed main stylesheet template is unexpectedly small")
'''


def main() -> int:
    payload = V3.read_text(encoding="utf-8")
    count = payload.count(OLD)
    if count != 1:
        raise RuntimeError(f"addStyle locator replacement expected one match, found {count}")
    RUNTIME.write_text(payload.replace(OLD, NEW, 1), encoding="utf-8")
    try:
        subprocess.run(["python3", str(RUNTIME)], cwd=ROOT, check=True)
    finally:
        RUNTIME.unlink(missing_ok=True)
    for path in (
        V3,
        ROOT / ".github/development-packages/issue-253-v5-diagnostic.py",
        ROOT / ".github/development-packages/issue-253-style-assignment-inspection.mjs",
        ROOT / ".github/development-packages/issue-253-style-assignment-inspection.py",
        ROOT / "docs/issue-253-v5-package-diagnostic.txt",
        ROOT / "docs/issue-253-style-assignment-inspection.txt",
    ):
        path.unlink(missing_ok=True)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
