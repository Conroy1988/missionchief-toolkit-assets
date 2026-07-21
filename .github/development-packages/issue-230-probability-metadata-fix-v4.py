#!/usr/bin/env python3
from __future__ import annotations

import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
ORIGINAL = ROOT / ".github/development-packages/issue-230-probability-metadata-fix.py"
V3 = ROOT / ".github/development-packages/issue-230-probability-metadata-fix-v3.py"

REPLACEMENTS = (
    (
        '''def replace_function(source: str, name: str, replacement: str) -> str:
    start, end = function_span(source, name)
    return source[:start] + textwrap.dedent(replacement).strip("\\n") + source[end:]
''',
        '''def compact_js(value: str) -> str:
    return " ".join(line.strip() for line in textwrap.dedent(value).strip().splitlines() if line.strip())


def replace_function(source: str, name: str, replacement: str) -> str:
    start, end = function_span(source, name)
    return source[:start] + compact_js(replacement) + source[end:]
''',
        "compact runtime helper",
    ),
    (
        '''    source = source.replace(marker, HELPERS.rstrip() + "\\n\\n" + marker, 1)
''',
        '''    source = source.replace(marker, compact_js(HELPERS) + "\\n\\n" + marker, 1)
''',
        "compact inserted metadata helpers",
    ),
)


def main() -> int:
    payload = ORIGINAL.read_text(encoding="utf-8")
    for old, new, label in REPLACEMENTS:
        count = payload.count(old)
        if count != 1:
            raise RuntimeError(f"{label}: expected one match, found {count}")
        payload = payload.replace(old, new, 1)
    ORIGINAL.write_text(payload, encoding="utf-8")
    subprocess.run(["python3", str(V3)], cwd=ROOT, check=True)
    for path in (
        V3,
        ROOT / ".github/development-packages/issue-230-probability-v3-diagnostic.py",
        ROOT / "docs/issue-230-probability-v3-diagnostic.txt",
    ):
        path.unlink(missing_ok=True)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
