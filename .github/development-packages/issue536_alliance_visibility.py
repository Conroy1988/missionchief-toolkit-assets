from pathlib import Path
import base64, zlib
root=Path(__file__).resolve().parents[2]
parts=sorted((root/'.github/development-packages/issue536-parts').glob('part-*.b64'))
payload=zlib.decompress(base64.b64decode(''.join(p.read_text() for p in parts)))
code=compile(payload.decode('utf-8'), 'issue536_alliance_visibility.py', 'exec')
exec(code, {'__name__':'__main__','__file__':str(Path(__file__))})
contract=root/'.github/scripts/test_issue536_alliance_building_visibility.py'
value=contract.read_text(encoding='utf-8')
value=value.replace("assert \"toggleVisibility('buildings')\" in SOURCE", "assert \"data-mcms-show-buildings\" in SOURCE")
contract.write_text(value, encoding='utf-8')
changelog=root/'CHANGELOG.md'
value=changelog.read_text(encoding='utf-8')
value=value.replace('## 8.0.4 — Alliance-building native filter persistence', '## [8.0.4] - 2026-07-26\n\n### Alliance-building native filter persistence')
changelog.write_text(value, encoding='utf-8')
for relative in (
    '.github/scripts/test_issue537_godfather_css_activation.py',
    '.github/scripts/test_issue539_godfather_layout_audio.py',
    '.github/scripts/test_issue541_godfather_duration_position.py',
):
    target=root/relative
    value=target.read_text(encoding='utf-8').replace(r'8\.0\.3', r'8\.0\.4')
    target.write_text(value, encoding='utf-8')
for part in parts: part.unlink()
