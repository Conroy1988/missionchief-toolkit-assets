#!/usr/bin/env python3
from __future__ import annotations

import runpy
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
ORIGINAL = ROOT / ".github" / "development-packages" / "issue454-v5.0.3-preboot-tdz-recovery.py"
RUNTIME = ROOT / ".github" / "development-packages" / ".issue454-v5.0.3-runtime.py"
LEGACY_DIAGNOSTIC = ROOT / ".github" / "development-packages" / "issue454-runtime-diagnostic.py"


def replace_exact(text: str, old: str, new: str, label: str, count: int = 1) -> str:
    actual = text.count(old)
    if actual != count:
        raise RuntimeError(f"{label}: expected {count}, found {actual}")
    return text.replace(old, new, count)


package = ORIGINAL.read_text(encoding="utf-8")
package = replace_exact(
    package,
    "import os\nimport subprocess\n",
    "import os\nimport re\nimport subprocess\n",
    "package regex import",
)
package = replace_exact(
    package,
    '''late_declaration = "    const OPERATIONAL_SUITE_SETTINGS_VERSION = 1;\\n"
state_initializer = "    const state = loadState();\\n"
if source.index(state_initializer) >= source.index(late_declaration):
    raise RuntimeError("Issue #454 precondition failed: settings version is not after state initialization")
source = replace_exact(source, late_declaration, "", "remove late operational settings declaration")
source = replace_exact(
    source,
    state_initializer,
    late_declaration + state_initializer,
    "insert operational settings declaration before state hydration",
)
''',
    '''late_declaration = "    const OPERATIONAL_SUITE_SETTINGS_VERSION = 1;\\n"
state_candidates = [
    line
    for line in source.splitlines(keepends=True)
    if re.fullmatch(r"\\s*(?:const|let|var)\\s+state\\s*=\\s*loadState\\(\\);\\s*(?:\\r?\\n)?", line)
]
if len(state_candidates) != 1:
    raise RuntimeError(f"Issue #454 state hydration locator found {len(state_candidates)} candidates")
state_initializer = state_candidates[0]
if source.index(state_initializer) >= source.index(late_declaration):
    raise RuntimeError("Issue #454 precondition failed: settings version is not after state initialization")
source = replace_exact(source, late_declaration, "", "remove late operational settings declaration")
source = replace_exact(
    source,
    state_initializer,
    late_declaration + state_initializer,
    "insert operational settings declaration before state hydration",
)
''',
    "binding-agnostic state hydration locator",
)
package = replace_exact(
    package,
    '''    ROOT / ".github" / "diagnostics" / "issue454-state-region.txt",
)
''',
    '''    ROOT / ".github" / "diagnostics" / "issue454-state-region.txt",
    ROOT / ".github" / "diagnostics" / "issue454-v5.0.3-preflight.txt",
)
''',
    "diagnostic cleanup set",
)
package = replace_exact(
    package,
    '''CONTRACT.write_text(r\'\'\'#!/usr/bin/env python3
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
SOURCE = ROOT / "src" / "MissionChief_Map_Command_Toolkit.user.js"
text = SOURCE.read_text(encoding="utf-8")

settings_declaration = "    const OPERATIONAL_SUITE_SETTINGS_VERSION = 1;"
state_initializer = "    const state = loadState();"
default_function = "    function defaultOperationalWindowState"

assert text.count(settings_declaration) == 1
assert text.count(state_initializer) == 1
assert text.index(settings_declaration) < text.index(state_initializer)
assert text.index(state_initializer) < text.index(default_function)
''',
    '''CONTRACT.write_text(r\'\'\'#!/usr/bin/env python3
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
SOURCE = ROOT / "src" / "MissionChief_Map_Command_Toolkit.user.js"
text = SOURCE.read_text(encoding="utf-8")

settings_declaration = "    const OPERATIONAL_SUITE_SETTINGS_VERSION = 1;"
state_match = re.search(r"(?m)^\\s*(?:const|let|var)\\s+state\\s*=\\s*loadState\\(\\);\\s*$", text)
default_function = "    function defaultOperationalWindowState"

assert text.count(settings_declaration) == 1
assert state_match is not None
state_initializer = state_match.group(0)
assert text.index(settings_declaration) < state_match.start()
assert state_match.start() < text.index(default_function)
''',
    "binding-agnostic permanent contract",
)

RUNTIME.write_text(package, encoding="utf-8")
try:
    runpy.run_path(str(RUNTIME), run_name="__main__")
finally:
    RUNTIME.unlink(missing_ok=True)

ORIGINAL.unlink(missing_ok=True)
LEGACY_DIAGNOSTIC.unlink(missing_ok=True)
print("Completed corrected v5.0.3 preboot TDZ recovery package.")
