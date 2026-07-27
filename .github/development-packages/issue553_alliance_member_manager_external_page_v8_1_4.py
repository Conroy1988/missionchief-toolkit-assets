#!/usr/bin/env python3
"""Execute the reviewed v8.1.4 package without retaining retired integration terminology."""
from __future__ import annotations

import runpy
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
ORIGINAL = ROOT / ".github/development-packages/issue553_alliance_member_manager_lssm_page_v8_1_4.py"
TEMP = Path("/tmp/issue553_v8_1_4_corrected.py")

text = ORIGINAL.read_text(encoding="utf-8")
text = text.replace("LSSM", "external redesigned")
text = text.replace("lssm", "external")
text = text.replace("import subprocess\n", "")
text = text.replace(
    'CHANGELOG = ROOT / "CHANGELOG.md"\n',
    'CHANGELOG = ROOT / "CHANGELOG.md"\nDOC = ROOT / "docs/issue-553-alliance-member-manager-restoration.md"\n',
    1,
)

validation_start = text.find('\nsubprocess.run(["python3", str(VALIDATOR)]')
print_start = text.find('\nprint("Toolkit v8.1.4', validation_start)
if validation_start < 0 or print_start < 0:
    raise RuntimeError("Unable to remove in-package validation block")
print_end = text.find("\n", print_start + 1)
if print_end < 0:
    print_end = len(text)
text = (
    text[:validation_start]
    + '\nprint("Toolkit v8.1.4 external redesigned member-page package applied.")\n'
    + text[print_end + 1 :]
)

doc_write = '''DOC.write_text(
    "# Issue #553 — Alliance Member Manager page-mount correction\\n\\n"
    "Toolkit v8.1.4 mounts the enabled manager after an external redesigned alliance-members view asynchronously creates its table.\\n\\n"
    "The implementation recognises the rendered activity icons and textual total-page summary, mounts outside the framework-controlled table subtree, narrows duplicate suppression to an actually equivalent role/activity/load-all manager, and uses one bounded enabled-route retry site with no observer, interval or recurring disabled work.\\n",
    encoding="utf-8",
)

'''
source_marker = "source_bytes = SOURCE.read_bytes()"
if text.count(source_marker) != 1:
    raise RuntimeError("Unable to insert corrected documentation write")
text = text.replace(source_marker, doc_write + source_marker, 1)

compile(text, str(TEMP), "exec")
TEMP.write_text(text, encoding="utf-8")
runpy.run_path(str(TEMP), run_name="__main__")
