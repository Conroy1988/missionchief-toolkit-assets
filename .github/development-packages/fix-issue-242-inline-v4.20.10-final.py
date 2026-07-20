#!/usr/bin/env python3
from pathlib import Path

PACKAGE = Path(__file__).with_name("fix-issue-242-inline-v4.20.10-scoped.py")
text = PACKAGE.read_text(encoding="utf-8")
old = 'source = replace_once(source, "guideVersion: \'4.20.9\',", "guideVersion: \'4.20.10\',", "guide version")\n'
if text.count(old) != 1:
    raise AssertionError(f"obsolete guideVersion package anchor count: {text.count(old)}")
text = text.replace(old, "", 1)
namespace = {"__name__": "__main__", "__file__": str(PACKAGE)}
exec(compile(text, str(PACKAGE), "exec"), namespace)
PACKAGE.unlink(missing_ok=True)
(ROOT := PACKAGE.resolve().parents[2])
(ROOT / ".github" / "development-packages" / "fix-issue-242-inline-v4.20.10.py").unlink(missing_ok=True)
