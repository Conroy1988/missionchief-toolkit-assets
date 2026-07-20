#!/usr/bin/env python3
from __future__ import annotations

import subprocess
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
ORIGINAL = ROOT / ".github/development-packages/issue-279-root-attribute-write-suppression.py"


def replace_once(text: str, old: str, new: str, label: str) -> str:
    count = text.count(old)
    if count != 1:
        raise RuntimeError(f"{label}: expected one match, found {count}")
    return text.replace(old, new, 1)


def main() -> None:
    text = ORIGINAL.read_text(encoding="utf-8")
    text = replace_once(
        text,
        '"""Verify unchanged root attributes do not trigger redundant DOM mutations."""',
        '"Verify unchanged root attributes do not trigger redundant DOM mutations."',
        "generated contract module docstring",
    )
    text = replace_once(
        text,
        '    harness = f\'\'\'"use strict";',
        '    harness = f"""\\n"use strict";',
        "generated JavaScript harness opening",
    )
    text = replace_once(
        text,
        'console.log("Root attribute write-suppression runtime fixtures passed");\n\'\'\'\n    with tempfile.TemporaryDirectory',
        'console.log("Root attribute write-suppression runtime fixtures passed");\n"""\n    with tempfile.TemporaryDirectory',
        "generated JavaScript harness closing",
    )

    with tempfile.TemporaryDirectory(prefix="mcms-issue-279-package-") as directory:
        corrected = Path(directory) / "issue-279-root-attribute-write-suppression.py"
        corrected.write_text(text, encoding="utf-8")
        subprocess.run([sys.executable, "-m", "py_compile", str(corrected)], cwd=ROOT, check=True)
        subprocess.run([sys.executable, str(corrected)], cwd=ROOT, check=True)

    ORIGINAL.unlink(missing_ok=True)
    print("Applied corrected Issue 279 root-attribute write-suppression package")


if __name__ == "__main__":
    main()
