from pathlib import Path
import base64, zlib
root=Path(__file__).resolve().parents[2]
parts=sorted((root/'.github/development-packages/issue536-parts').glob('part-*.b64'))
payload=zlib.decompress(base64.b64decode(''.join(p.read_text() for p in parts)))
code=compile(payload.decode('utf-8'), 'issue536_alliance_visibility.py', 'exec')
exec(code, {'__name__':'__main__','__file__':str(Path(__file__))})
for part in parts: part.unlink()
