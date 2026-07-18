#!/usr/bin/env python3
from pathlib import Path
import subprocess

root = Path(__file__).resolve().parents[2]
for relative in [
    '.github/development-packages/issue-181-fix-contract-quoting.py',
    '.github/development-packages/issue-181-runner2.py',
    '.github/development-packages/issue-181-runner3.py',
    '.github/diagnostics/issue-181-package-result-v3.txt',
    '.github/diagnostics/issue-181-package-result.txt',
    '.github/diagnostics/issue-181-runtime-result-v4.txt',
    '.github/diagnostics/issue-181-runtime-result-v5.txt',
    '.github/diagnostics/issue-181-runtime-result-v6.txt',
]:
    (root / relative).unlink(missing_ok=True)
for cache in root.glob('.github/scripts/__pycache__/*'):
    cache.unlink(missing_ok=True)
subprocess.run(['node', '--check', str(root / 'src/MissionChief_Map_Command_Toolkit.user.js')], cwd=root, check=True)
assert (root / 'src/MissionChief_Map_Command_Toolkit.user.js').read_bytes() == (root / 'dist/MissionChief_Map_Command_Toolkit.user.js').read_bytes()
assert (root / 'src/MissionChief_Map_Command_Toolkit.user.js').read_bytes() == (root / 'dist/MissionChief_Map_Command_Toolkit.txt').read_bytes()
print('Issue 181 residue cleanup passed')
