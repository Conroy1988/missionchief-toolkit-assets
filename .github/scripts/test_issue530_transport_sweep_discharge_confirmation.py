#!/usr/bin/env python3
from __future__ import annotations

import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
SOURCE = ROOT / 'src' / 'MissionChief_Map_Command_Toolkit.user.js'


def section(text: str, start: str, end: str) -> str:
    left = text.index(start)
    right = text.index(end, left)
    return text[left:right]


def main() -> int:
    source = SOURCE.read_text(encoding='utf-8')
    metadata = re.search(r'(?m)^//\s*@version\s+([^\s]+)$', source)
    runtime = re.search(r"version:\s*'([^']+)'", source)
    assert metadata and runtime
    assert metadata.group(1) == runtime.group(1) == '8.0.4'

    for marker in [
        'confirmedDischargeDialogKeys: new Set()',
        "pendingDischargeKey: ''",
        'function transportSweepDischargeConfirmationRoots()',
        'function clickTransportSweepDischargeConfirmation(releaseKey)',
        "TRANSPORT_SWEEP_DISCHARGE_DIALOG_CONFIRM = 'yes, discharge!'",
        "TRANSPORT_SWEEP_DISCHARGE_DIALOG_DISABLE = 'discharge and disable confirmation'",
    ]:
        assert marker in source, marker

    helper = section(
        source,
        '    function transportSweepDialogControlText(',
        '    function captureTransportSweepReleaseConfirmationBaseline(',
    )
    processor = re.search(
        r'async function processTransportSweepMission\(item, remainingAllowance\) \{([\s\S]*?)\n    \}\n\n    async function startTransportSweep',
        source,
    )
    assert processor
    body = processor.group(1)
    assert 'transportSweepRuntime.pendingDischargeKey !== key' in helper
    assert 'transportSweepRuntime.confirmedDischargeDialogKeys.has(key)' in helper
    assert 'TRANSPORT_SWEEP_DISCHARGE_DIALOG_ABORT' in helper
    assert 'TRANSPORT_SWEEP_DISCHARGE_DIALOG_DISABLE' in helper
    assert 'TRANSPORT_SWEEP_DISCHARGE_DIALOG_CONFIRM' in helper
    assert 'confirm.click();' in helper
    assert 'abort.click' not in helper
    assert 'disable.click' not in helper
    assert 'const releaseKey = transportSweepReleaseKey(missionId, candidate.vehicleId);' in body
    assert body.count('clickTransportSweepDischargeConfirmation(releaseKey);') == 2
    assert (
        body.index('button.click();')
        < body.index('clickTransportSweepDischargeConfirmation(releaseKey);')
        < body.index('transportSweepReleaseConfirmationVisible(confirmationBaseline)')
    )
    assert '}, 5000, 70);' in body
    assert "pendingDischargeKey = '';" in source
    assert 'MutationObserver' not in helper
    assert 'setInterval' not in helper
    print('Issue #530 discharge confirmation static contract passed for v8.')
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
