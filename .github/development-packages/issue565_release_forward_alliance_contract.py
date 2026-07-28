#!/usr/bin/env python3
"""Keep the v8.1.5 Alliance Member Manager contract valid for later releases."""
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
CONTRACT = ROOT / ".github/scripts/test_alliance_member_manager_contract.py"
text = CONTRACT.read_text(encoding="utf-8")
old = '''assert re.search(r"^// @version\\s+8\\.1\\.5$", source, re.MULTILINE)
assert "version: '8.1.5'" in source
'''
new = '''metadata = re.search(r"(?m)^//\\s*@version\\s+([^\\s]+)$", source)
runtime = re.search(r"version:\\s*'([^']+)'", source)
assert metadata and runtime and metadata.group(1) == runtime.group(1)
current_version = tuple(int(part) for part in metadata.group(1).split('.'))
assert current_version >= (8, 1, 5)
'''
if text.count(old) != 1:
    raise RuntimeError(f"Expected one Alliance Member Manager version pin, found {text.count(old)}")
CONTRACT.write_text(text.replace(old, new, 1), encoding="utf-8")
print("Alliance Member Manager contract is release-forward from v8.1.5.")
