#!/usr/bin/env python3
from __future__ import annotations

import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
ORIGINAL = ROOT / ".github/development-packages/issue-253-main-style-headroom.py"
RUNTIME = ROOT / ".github/development-packages/.issue-253-main-style-headroom-runtime.py"


def replace_once(text: str, old: str, new: str, label: str) -> str:
    count = text.count(old)
    if count != 1:
        raise RuntimeError(f"{label}: expected one match, found {count}")
    return text.replace(old, new, 1)


def main() -> int:
    payload = ORIGINAL.read_text(encoding="utf-8")
    payload = replace_once(
        payload,
        '''    return ranges


def main() -> int:
''',
        '''    return ranges


def canonical_css_formatting(raw: str) -> str:
    lines = raw.split("\\n")
    removable = {index for index in range(1, len(lines) - 1) if not lines[index].strip()}
    for start, end in standalone_comment_ranges(lines):
        removable.update(range(start, end + 1))
    stripped = "\\n".join(line for index, line in enumerate(lines) if index not in removable)
    return re.sub(r"\\n[\\t ]*}", "}", stripped)


def main() -> int:
''',
        "canonical CSS contract helper",
    )
    payload = replace_once(
        payload,
        '''    semantic_lines = list(lines)
    digest = hashlib.sha256("\\n".join(semantic_lines).encode("utf-8")).hexdigest()
    if digest != fixture["semanticLinesSha256"]:
        fail("ordered non-formatting stylesheet lines differ from the reviewed fixture")
    if len(semantic_lines) != fixture["semanticLineCount"]:
        fail("semantic stylesheet line count differs from the reviewed fixture")
''',
        '''    candidate_template_hash = hashlib.sha256(raw.encode("utf-8")).hexdigest()
    if candidate_template_hash != fixture["candidateTemplateSha256"]:
        fail("exact candidate stylesheet template differs from the reviewed fixture")
    canonical_hash = hashlib.sha256(canonical_css_formatting(raw).encode("utf-8")).hexdigest()
    if canonical_hash != fixture["canonicalCssSha256"]:
        fail("canonical CSS content differs from the reviewed fixture")
    if len(lines) != fixture["candidateTemplateLines"]:
        fail("candidate stylesheet template line count differs from the reviewed fixture")
''',
        "candidate and canonical CSS hashes",
    )
    payload = replace_once(
        payload,
        '''    if fixture["removedBlankLines"] + fixture["removedStandaloneCommentLines"] != fixture["recoveredSourceLines"]:
        fail("fixture formatting-category arithmetic is inconsistent")
''',
        '''    if fixture["removedBlankLines"] + fixture["removedStandaloneCommentLines"] + fixture["joinedClosingBraceLines"] != fixture["recoveredSourceLines"]:
        fail("fixture formatting-category arithmetic is inconsistent")
    if fixture["joinedClosingBraceLines"] != 15:
        fail("reviewed closing-brace join count changed")
''',
        "formatting-category arithmetic",
    )
    payload = replace_once(
        payload,
        '''        f"({fixture['removedBlankLines']} blank, "
        f"{fixture['removedStandaloneCommentLines']} standalone comment), "
''',
        '''        f"({fixture['removedBlankLines']} blank, "
        f"{fixture['removedStandaloneCommentLines']} standalone comment, "
        f"{fixture['joinedClosingBraceLines']} closing-brace joins), "
''',
        "contract summary categories",
    )
    payload = replace_once(
        payload,
        '- Recovered source headroom by removing only blank physical lines and standalone full-line CSS comments from the existing `installMainStyles` template.\n',
        '- Recovered source headroom by removing only blank physical lines, standalone full-line CSS comments and 15 newlines immediately before full-line closing braces from the existing `installMainStyles` template.\n',
        "changelog formatting categories",
    )
    payload = replace_once(
        payload,
        '- Preserved every ordered selector, declaration, interpolation, inline comment and rule line byte-for-byte, including cascade order.\n',
        '- Preserved the canonical CSS content byte-for-byte after normalising only parser-ignored comments and whitespace immediately before closing braces.\n',
        "changelog equivalence wording",
    )
    payload = replace_once(
        payload,
        '''Only standalone source formatting inside the existing `installMainStyles` template is removed: blank physical lines and full-line CSS comment blocks. Every ordered selector, declaration, interpolation, inline comment and rule line remains byte-for-byte identical. The change does not group selectors, consolidate declarations, reorder rules, alter interpolation expressions, defer installation, or change specificity and cascade order.

CSS comments removed by this change occupy complete lines and contain no interpolation. They are parser-ignored documentation rather than selectors or declarations. Adjacent retained lines remain separated by a newline.
''',
        '''Only standalone source formatting inside the existing `installMainStyles` template is removed: blank physical lines, full-line CSS comment blocks and 15 newlines immediately before full-line closing braces. The canonical CSS content is identical before and after. The change does not group selectors, consolidate declarations, reorder rules, alter interpolation expressions, defer installation, or change specificity and cascade order.

CSS comments removed by this change occupy complete lines and contain no interpolation. They are parser-ignored documentation rather than selectors or declarations. The 15 joined lines contain only `}`; CSS does not require whitespace immediately before a closing brace.
''',
        "engineering documentation bounded change",
    )
    payload = replace_once(
        payload,
        '''- exact recovered line count by blank-line and standalone-comment category;
- original and candidate template line counts;
- semantic stylesheet line count;
- SHA-256 of every ordered non-formatting stylesheet line.
''',
        '''- exact recovered line count by blank-line, standalone-comment and closing-brace-join category;
- original and candidate template line counts;
- SHA-256 of the canonical CSS content;
- SHA-256 of the exact candidate stylesheet template.
''',
        "engineering documentation proof fields",
    )
    payload = replace_once(
        payload,
        '''            ROOT / "docs/issue-253-style-formatting-diagnostic.txt",
            ROOT / "docs/issue-253-style-formatting-inventory.json",
''',
        '''            ROOT / "docs/issue-253-style-formatting-diagnostic.txt",
            ROOT / "docs/issue-253-style-formatting-inventory.json",
            ROOT / "docs/issue-253-final-package-diagnostic.txt",
''',
        "diagnostic cleanup",
    )

    RUNTIME.write_text(payload, encoding="utf-8")
    try:
        subprocess.run(["python3", str(RUNTIME)], cwd=ROOT, check=True)
    finally:
        RUNTIME.unlink(missing_ok=True)
    ORIGINAL.unlink(missing_ok=True)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
