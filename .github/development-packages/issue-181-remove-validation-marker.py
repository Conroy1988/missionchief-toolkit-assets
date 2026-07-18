#!/usr/bin/env python3
from pathlib import Path

root = Path(__file__).resolve().parents[2]
(root / '.github/validation/issue-181-human-trigger.txt').unlink(missing_ok=True)
print('Issue 181 validation marker removed')
