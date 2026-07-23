#!/usr/bin/env python3
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
SOURCE = ROOT / "src" / "MissionChief_Map_Command_Toolkit.user.js"
source = SOURCE.read_text(encoding="utf-8")

required = {
    "baseline": "const OPERATIONAL_SUITE_LSSM_BASELINE = Object.freeze({",
    "baseline commit": "commit: '88e41646e59a7d620624f90f1d9a0a62320c2775'",
    "settings namespace": "operationalWindow: defaultOperationalWindowState(true)",
    "normaliser": "function normaliseOperationalWindowState(value, legacyRequirementsEnabled = true)",
    "runtime shell": "function installOperationalSuiteShell()",
    "context map": "const operationalSuiteContexts = new Map();",
    "coalesced scheduler": "function scheduleOperationalSuiteScan(delay = 0)",
    "cleanup": "clearOperationalSuiteContexts();",
    "boot installation": "installOperationalSuiteShell();",
    "safe auto-open default": "autoOpenTransportRequest: false",
    "upstream continuation default": "autoClickSuccessButtons: true",
    "suite renderer default": "enabled: true,\n            phase: 'operational-suite'",
    "legacy Matrix retired": "// Issue #391: legacy Mission Requirements Matrix retired; operationalWindow is authoritative.",
}
for label, needle in required.items():
    if needle not in source:
        raise SystemExit(f"Issue #378 shell missing {label}: {needle}")

if source.index("installOperationalSuiteShell();") > source.index("startBootAttemptCoordinator(bootPerformanceStartedAt);"):
    raise SystemExit("Issue #378 shell must install before the boot-attempt coordinator")

if "data-mcms-operational-suite" not in source or "mcms-operational-suite-panel" not in source:
    raise SystemExit("Issue #378 requirements renderer surface is missing")

for path in (
    ROOT / "MissionChief_Map_Command_Toolkit.user.js",
    ROOT / "MissionChief_Map_Command_Toolkit.txt",
    ROOT / "dist" / "MissionChief_Map_Command_Toolkit.user.js",
    ROOT / "dist" / "MissionChief_Map_Command_Toolkit.txt",
):
    if path.read_text(encoding="utf-8") != source:
        raise SystemExit(f"canonical parity failed: {path}")

fixture = __import__('json').loads((ROOT / '.github' / 'fixtures' / 'main-style-source-headroom.json').read_text(encoding='utf-8'))
expected_lines = fixture['candidateSourceLines'] + fixture.get('approvedNonStyleSourceLines', 0) - fixture.get('retiredNonStyleSourceLines', 0)
if fixture.get('expectedSourceLines') != expected_lines or expected_lines != len(source.splitlines()):
    raise SystemExit('Issue #378 source-headroom signed accounting is inconsistent')
approved_changes = fixture.get('approvedNonStyleChanges', [])
expected_changes = [
    {'issue': 378, 'phase': 'operational-suite-shell', 'lines': 317},
    {'issue': 378, 'phase': 'enhanced-requirements-engine-core', 'lines': 331},
    {'issue': 378, 'phase': 'enhanced-requirements-renderer', 'lines': 412},
    {'issue': 378, 'phase': 'operational-feature-suite', 'lines': 348},
]
if approved_changes != expected_changes:
    raise SystemExit('Issue #378 source-headroom phase ledger is missing or altered')

print("Issue #378 operational-suite lifecycle/settings shell contract passed.")
