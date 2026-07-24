#!/usr/bin/env python3
from __future__ import annotations

import re
from pathlib import Path

import full_userscript_audit as audit

ROOT = Path(__file__).resolve().parents[2]
SELF = Path(__file__).resolve()
SOURCE = ROOT / 'src/MissionChief_Map_Command_Toolkit.user.js'
OUTPUT = ROOT / '.github/diagnostics/issue470-boot-coordinator-source.txt'
text = SOURCE.read_text(encoding='utf-8')
masked = audit.mask_non_code(text)
name = 'startBootAttemptCoordinator'
match = re.search(rf'\bfunction\s+{name}\s*\(', masked)
if not match:
    raise SystemExit('Boot coordinator declaration missing')
opening = masked.find('{', masked.find(')', match.start()) + 1)
closing = audit.matching_brace(masked, opening)
if opening < 0 or closing is None:
    raise SystemExit('Boot coordinator body could not be extracted')
OUTPUT.parent.mkdir(parents=True, exist_ok=True)
OUTPUT.write_text(text[match.start():closing + 1] + '\n', encoding='utf-8')
SELF.unlink(missing_ok=True)
print(OUTPUT.relative_to(ROOT))
