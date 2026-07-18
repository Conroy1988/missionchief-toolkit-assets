#!/usr/bin/env python3
from __future__ import annotations

from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
PACKAGE = ROOT / ".github" / "development-packages" / "issue-171-ajax-dispatch-root.py"
REMOVE = [
    ROOT / ".github" / "development-packages" / "issue-171-record-inspection.py",
    ROOT / ".github" / "diagnostics" / "issue-171-package-result.txt",
    ROOT / ".github" / "diagnostics" / "issue-171-record-refresh.txt",
]

source = PACKAGE.read_text(encoding="utf-8")
old_write = '''source = replace_once(source, old_root, new_root, "candidate root promotion")
SOURCE.write_text(source, encoding="utf-8")'''
new_write = '''source = replace_once(source, old_root, new_root, "candidate root promotion")
source = replace_once(
    source,
    "            missionRequirementsEnsureRecord({ ...candidate, source }, source);",
    "            const activeRecord = missionRequirementsEnsureRecord({ ...candidate, source }, source);\\n            if (activeRecord?.panel) missionRequirementsPlacePanel({ ...candidate, source }, source, activeRecord.panel);",
    "active record placement reconciliation",
)
SOURCE.write_text(source, encoding="utf-8")'''
if source.count(old_write) != 1:
    raise AssertionError("Unable to inject active-record placement reconciliation")
source = source.replace(old_write, new_write, 1)

old_contract = '''contract = replace_once(
    contract,
    '    assert source.count("missionRequirementsPanelId: \\\'mc-map-command-toolkit-mission-requirements\\\'") == 1\\n',
    '    assert source.count("missionRequirementsPanelId: \\\'mc-map-command-toolkit-mission-requirements\\\'") == 1\\n    assert "return { root, parent: operational.parentNode, before: operational };" not in source\\n    assert "missionRequirementsPlacementBlock(root, operational)" in source\\n',
    "contract table-host assertions",
)
CONTRACT_TEST.write_text(contract, encoding="utf-8")'''
new_contract = '''contract = replace_once(
    contract,
    '    assert source.count("missionRequirementsPanelId: \\\'mc-map-command-toolkit-mission-requirements\\\'") == 1\\n',
    '    assert source.count("missionRequirementsPanelId: \\\'mc-map-command-toolkit-mission-requirements\\\'") == 1\\n    assert "return { root, parent: operational.parentNode, before: operational };" not in source\\n    assert "missionRequirementsPlacementBlock(root, operational)" in source\\n',
    "contract table-host assertions",
)
contract = replace_once(
    contract,
    '    assert compact_source.count("missionRequirementsPlacePanel(scopedCandidate,source,panel)") == 2',
    '    assert compact_source.count("missionRequirementsPlacePanel(scopedCandidate,source,panel)") == 2\\n    assert compact_source.count("missionRequirementsPlacePanel({...candidate,source},source,activeRecord.panel)") == 1',
    "active placement contract",
)
CONTRACT_TEST.write_text(contract, encoding="utf-8")'''
if source.count(old_contract) != 1:
    raise AssertionError("Unable to update active placement contract")
source = source.replace(old_contract, new_contract, 1)

PACKAGE.unlink()
for path in REMOVE:
    if path.exists():
        path.unlink()

namespace = {"__file__": str(PACKAGE), "__name__": "__main__"}
exec(compile(source, str(PACKAGE), "exec"), namespace)
