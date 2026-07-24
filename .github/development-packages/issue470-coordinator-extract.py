#!/usr/bin/env python3
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
SELF = Path(__file__).resolve()
SOURCE = ROOT / 'src/MissionChief_Map_Command_Toolkit.user.js'
OUTPUT = ROOT / '.github/diagnostics/issue470-current-coordinator.txt'

text = SOURCE.read_text(encoding='utf-8')
start = text.index('    function runBootIntegration')
end = text.index('    function registerBootMaintenanceTasks', start)
OUTPUT.parent.mkdir(parents=True, exist_ok=True)
OUTPUT.write_text(text[start:end], encoding='utf-8')
SELF.unlink(missing_ok=True)
print('Captured current boot integration and coordinator source.')
