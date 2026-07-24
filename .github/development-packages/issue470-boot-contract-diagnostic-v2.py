#!/usr/bin/env python3
from __future__ import annotations

import runpy
import traceback
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
SELF = Path(__file__).resolve()
TARGET = ROOT / '.github/development-packages/issue470-boot-contract-alignment.py'
TEST = ROOT / '.github/scripts/test_boot_lifecycle_contract.py'
OUTPUT = ROOT / '.github/diagnostics/issue470-boot-contract-latest.txt'

original_target = TARGET.read_text(encoding='utf-8')
original_test = TEST.read_text(encoding='utf-8')
status = 'success'
detail = 'Boot contract alignment package completed without raising an exception.'
try:
    runpy.run_path(str(TARGET), run_name='__main__')
except BaseException as error:
    status = 'failure'
    detail = ''.join(traceback.format_exception(type(error), error, error.__traceback__))
finally:
    TEST.write_text(original_test, encoding='utf-8')
    TARGET.parent.mkdir(parents=True, exist_ok=True)
    TARGET.write_text(original_target, encoding='utf-8')

OUTPUT.parent.mkdir(parents=True, exist_ok=True)
OUTPUT.write_text(
    'Issue #470 boot-contract alignment diagnostic\n'
    f'status={status}\n\n'
    + detail[-20000:]
    + '\n',
    encoding='utf-8',
)
SELF.unlink(missing_ok=True)
print(f'Boot contract diagnostic captured: {status}')
