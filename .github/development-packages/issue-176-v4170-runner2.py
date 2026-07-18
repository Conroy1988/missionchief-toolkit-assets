#!/usr/bin/env python3
from __future__ import annotations

import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
PACKAGE = ROOT / '.github' / 'development-packages' / 'issue-176-custom-vehicle-badges.py'
text = PACKAGE.read_text(encoding='utf-8')
old_count = '''if map_count != 2:
    raise AssertionError(f"toggle UI maps: expected two missionRequirements entries, found {map_count}")'''
new_count = '''if map_count != 1:
    raise AssertionError(f"toggle UI map: expected one missionRequirements entry, found {map_count}")'''
if text.count(old_count) != 1:
    raise AssertionError(f'Expected one UI map count contract, found {text.count(old_count)}')
text = text.replace(old_count, new_count, 1)
old_context = '''    personalVehicleApiCache,
    vehicleDataRevision: 0,
    vehicleApiReady: true,'''
new_context = '''    personalVehicleApiCache,
    customVehicleClassificationCache: new Map(),
    customVehicleClassificationRevision: -1,
    customVehicleBadgeScanTimer: null,
    customVehicleBadgeRefreshPromise: null,
    customVehicleBadgeFeatureInstalled: false,
    customVehicleBadgeObservedDocuments: new WeakSet(),
    customVehicleBadgeObservedFrames: new WeakSet(),
    vehicleDataRevision: 0,
    vehicleApiReady: true,'''
if text.count(old_context) != 1:
    raise AssertionError(f'Expected one runtime context insertion point, found {text.count(old_context)}')
text = text.replace(old_context, new_context, 1)
PACKAGE.write_text(text, encoding='utf-8')
subprocess.run(['python3', str(PACKAGE)], cwd=ROOT, check=True)
