#!/usr/bin/env python3
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
PATHS = [
    ROOT / 'src' / 'MissionChief_Map_Command_Toolkit.user.js',
    ROOT / 'dist' / 'MissionChief_Map_Command_Toolkit.user.js',
    ROOT / 'dist' / 'MissionChief_Map_Command_Toolkit.txt',
]
OLD = 'function normaliseMissionOverlayRecord(item, existing = {}) {'
NEW = 'function normaliseMissionOverlayRecord(item, existing) {'

for path in PATHS:
    text = path.read_text(encoding='utf-8')
    if text.count(OLD) != 1:
        raise RuntimeError(f'{path}: expected one helper signature, found {text.count(OLD)}')
    path.write_text(text.replace(OLD, NEW, 1), encoding='utf-8')
