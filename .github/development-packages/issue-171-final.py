#!/usr/bin/env python3
from __future__ import annotations

from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
PACKAGE = ROOT / ".github" / "development-packages" / "issue-171-ajax-dispatch-root.py"
REMOVE = [
    ROOT / ".github" / "development-packages" / "issue-171-record-inspection.py",
    ROOT / ".github" / "development-packages" / "issue-171-final-check.py",
    ROOT / ".github" / "development-packages" / "issue-171-check2.py",
    ROOT / ".github" / "development-packages" / "issue-171-check3.py",
    ROOT / ".github" / "development-packages" / "issue-171-canonical-check.py",
    ROOT / ".github" / "diagnostics" / "issue-171-package-result.txt",
    ROOT / ".github" / "diagnostics" / "issue-171-record-refresh.txt",
    ROOT / ".github" / "diagnostics" / "issue-171-final-result.txt",
    ROOT / ".github" / "diagnostics" / "issue-171-check2-result.txt",
    ROOT / ".github" / "diagnostics" / "issue-171-check3-result.txt",
    ROOT / ".github" / "diagnostics" / "issue-171-canonical-panel.txt",
]

source = PACKAGE.read_text(encoding="utf-8")
old_fixture = '''api.scan();
flushAnimationFrames();
assert.strictEqual(issue171Record.panel.parentNode, issue171Root, 'subsequent scan re-homes a mis-mounted panel');
assert(!['TABLE', 'THEAD', 'TBODY', 'TFOOT', 'TR', 'TD', 'TH'].includes(issue171Record.panel.parentNode.tagName), 'panel host is never table structure');'''
new_fixture = '''api.scan();
flushAnimationFrames();
const issue171RehomedRecord = Array.from(api.records.values())[0];
assert.strictEqual(issue171RehomedRecord.panel.parentNode, issue171Root, 'subsequent scan re-homes a mis-mounted panel');
assert.strictEqual(issue171Record.panel.isConnected, false, 'stale table-mounted panel is removed');
assert(!['TABLE', 'THEAD', 'TBODY', 'TFOOT', 'TR', 'TD', 'TH'].includes(issue171RehomedRecord.panel.parentNode.tagName), 'panel host is never table structure');'''
if source.count(old_fixture) != 1:
    raise AssertionError("Unable to correct Issue 171 canonical panel fixture")
source = source.replace(old_fixture, new_fixture, 1)

PACKAGE.unlink()
for path in REMOVE:
    if path.exists():
        path.unlink()

namespace = {"__file__": str(PACKAGE), "__name__": "__main__"}
exec(compile(source, str(PACKAGE), "exec"), namespace)
