#!/usr/bin/env python3
from pathlib import Path
import subprocess

ROOT = Path(__file__).resolve().parents[2]
result = subprocess.run(
    ['python3', '.github/scripts/test_settings_ui_contract.py'],
    cwd=ROOT,
    text=True,
    stdout=subprocess.PIPE,
    stderr=subprocess.STDOUT,
    check=False,
)
output = ROOT / '.github' / 'development-analysis' / 'settings-ui-test-result.txt'
output.parent.mkdir(parents=True, exist_ok=True)
output.write_text(f'exit_code={result.returncode}\n{result.stdout}', encoding='utf-8')
