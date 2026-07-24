#!/usr/bin/env python3
from __future__ import annotations

import runpy
import traceback
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
SELF = Path(__file__).resolve()
TARGET = ROOT / '.github/development-packages/issue470-complete-boot-fixture.py'
FINAL = ROOT / '.github/development-packages/issue470-final-boot-fixture.py'
ALIGNMENT = ROOT / '.github/development-packages/issue470-boot-contract-alignment.py'
TEST = ROOT / '.github/scripts/test_boot_lifecycle_contract.py'
FIXTURE = ROOT / '.github/fixtures/boot-lifecycle-contract.json'
OUTPUT = ROOT / '.github/diagnostics/issue470-complete-boot-v5.txt'

originals = {
    TARGET: TARGET.read_text(encoding='utf-8'),
    FINAL: FINAL.read_text(encoding='utf-8'),
    ALIGNMENT: ALIGNMENT.read_text(encoding='utf-8'),
    TEST: TEST.read_text(encoding='utf-8'),
    FIXTURE: FIXTURE.read_text(encoding='utf-8'),
}
status = 'success'
detail = 'The complete Issue #470 boot fixture correction completed successfully.'
try:
    runpy.run_path(str(TARGET), run_name='__main__')
except BaseException as error:
    status = 'failure'
    detail = ''.join(traceback.format_exception(type(error), error, error.__traceback__))
finally:
    for path, content in originals.items():
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(content, encoding='utf-8')

OUTPUT.parent.mkdir(parents=True, exist_ok=True)
OUTPUT.write_text(
    'Issue #470 complete boot fixture diagnostic v5\n'
    f'status={status}\n\n'
    + detail[-32000:]
    + '\n',
    encoding='utf-8',
)
SELF.unlink(missing_ok=True)
print(f'Complete boot fixture diagnostic v5 captured: {status}')
