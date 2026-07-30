#!/usr/bin/env python3
import json, re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
source = (ROOT / 'src/MissionChief_Map_Command_Toolkit.user.js').read_text(encoding='utf-8')
metadata = re.search(r'(?m)^//\s*@version\s+([^\s]+)$', source)
runtime = re.search(r"version:\s*'([^']+)'", source)
assert metadata and runtime and metadata.group(1) == runtime.group(1) == '8.3.2'

for name in ['updateUiToggleClass', 'updateUiSetStyleProperty', 'updateUiSetAttribute', 'updateUiSetDataset', 'updateUiSetProperty', 'updateUiSetText']:
    assert source.count(f'function {name}(') == 1, name

start = source.index('    function updateUI() {')
end = source.index('    function ensureUi() {', start)
block = source[start:end]
for pattern in [
    r'\.classList\.toggle\(',
    r'\.style\.setProperty\(',
    r'\.setAttribute\(',
    r'\.textContent\s*=',
    r'\.title\s*=',
    r'\.tabIndex\s*=',
    r'\.hidden\s*=',
    r'\.value\s*=',
    r'\.dataset\.[A-Za-z_$][\w$]*\s*=(?!=)',
]:
    assert not re.search(pattern, block), pattern

report = json.loads((ROOT / 'docs/audits/issue-255/write-suppression-v832.json').read_text(encoding='utf-8'))
assert report['sourceSha256'] == 'e719dd7f26686895cd1ba9e31dd006c775134af86000eb7d32800feea6843cfa'
assert report['before']['writeAttempts'] == 14500 and report['after']['writeAttempts'] == 0
assert report['before']['mutationRecords'] == 7100 and report['after']['mutationRecords'] == 0
assert report['stateTransition']['changed']['counters']['changedWriteAttempts'] > 0
assert report['stateTransition']['changed']['mutations']['records'] > 0
assert report['stateTransition']['stableRepeat']['counters']['writeAttempts'] == 0
assert report['stateTransition']['stableRepeat']['mutations']['records'] == 0
assert report['frameworkReplacement']['changed']['counters']['changedWriteAttempts'] > 0
assert report['frameworkReplacement']['changed']['mutations']['records'] > 0
assert report['frameworkReplacement']['stableRepeat']['counters']['writeAttempts'] == 0
assert report['frameworkReplacement']['stableRepeat']['mutations']['records'] == 0
print('Issue #255 v8.3.2 updateUI same-value write suppression contract passed.')
