#!/usr/bin/env python3
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
SOURCE = ROOT / "src" / "MissionChief_Map_Command_Toolkit.user.js"
source = SOURCE.read_text(encoding="utf-8")

required = {
    "baseline": "const OPERATIONAL_SUITE_LSSM_BASELINE = Object.freeze({",
    "baseline commit": "commit: '88e41646e59a7d620624f90f1d9a0a62320c2775'",
    "settings namespace": "operationalWindow: defaultOperationalWindowState(true)",
    "normaliser": "function normaliseOperationalWindowState(value, legacyMatrixEnabled = true)",
    "runtime shell": "function installOperationalSuiteShell()",
    "context map": "const operationalSuiteContexts = new Map();",
    "coalesced scheduler": "function scheduleOperationalSuiteScan(delay = 0)",
    "cleanup": "clearOperationalSuiteContexts();",
    "boot installation": "installOperationalSuiteShell();",
    "safe auto-open default": "autoOpenTransportRequest: false",
    "upstream continuation default": "autoClickSuccessButtons: true",
    "suite disabled default": "enabled: false,\n            phase: 'shell'",
    "legacy Matrix retained": "// Issue #133 clean-room live mission requirements matrix.",
}
for label, needle in required.items():
    if needle not in source:
        raise SystemExit(f"Issue #378 shell missing {label}: {needle}")

if source.index("installOperationalSuiteShell();") > source.index("startBootAttemptCoordinator(bootPerformanceStartedAt);"):
    raise SystemExit("Issue #378 shell must install before the boot-attempt coordinator")

if "data-mcms-operational-suite" in source or "mcms-operational-suite-panel" in source:
    raise SystemExit("Phase 2 shell must not render a competing operational-suite surface")

for path in (
    ROOT / "MissionChief_Map_Command_Toolkit.user.js",
    ROOT / "MissionChief_Map_Command_Toolkit.txt",
    ROOT / "dist" / "MissionChief_Map_Command_Toolkit.user.js",
    ROOT / "dist" / "MissionChief_Map_Command_Toolkit.txt",
):
    if path.read_text(encoding="utf-8") != source:
        raise SystemExit(f"canonical parity failed: {path}")

fixture = __import__('json').loads((ROOT / '.github' / 'fixtures' / 'main-style-source-headroom.json').read_text(encoding='utf-8'))
expected_lines = fixture['candidateSourceLines'] + fixture.get('approvedNonStyleSourceLines', 0)
if fixture.get('expectedSourceLines') != expected_lines or expected_lines != len(source.splitlines()):
    raise SystemExit('Issue #378 source-headroom additive accounting is inconsistent')
approved_changes = fixture.get('approvedNonStyleChanges', [])
if not approved_changes or approved_changes[0] != {'issue': 378, 'phase': 'operational-suite-shell', 'lines': 317}:
    raise SystemExit('Issue #378 operational-suite shell source-headroom ledger entry is missing or altered')

print("Issue #378 operational-suite lifecycle/settings shell contract passed.")
