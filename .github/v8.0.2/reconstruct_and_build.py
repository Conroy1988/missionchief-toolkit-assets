#!/usr/bin/env python3
from pathlib import Path
import base64
import hashlib
import runpy

ROOT = Path(__file__).resolve().parents[2]
TARGET_LENGTH = 181672
TARGET = [None] * TARGET_LENGTH


def read(path: str) -> str:
    return ''.join((ROOT / path).read_text(encoding='ascii').split())


def place(start: int, value: str, label: str) -> None:
    end = start + len(value)
    if start < 0 or end > TARGET_LENGTH:
        raise SystemExit(f'{label}: placement {start}:{end} is out of range')
    for index, char in enumerate(value, start):
        current = TARGET[index]
        if current is not None and current != char:
            raise SystemExit(f'{label}: conflicting staged byte at encoded offset {index}')
        TARGET[index] = char


p = read('.github/v8.0.2/audio-parts/part-00.b64')
place(0, p[0:108], 'audio-parts/00 head')
place(509, p[413:7722], 'audio-parts/00 middle')
place(9487, p[7719:10232], 'audio-parts/00 tail')

p = read('.github/v8.0.2/audio-exact/part-00.b64')
place(7818, p[7785:7967], 'audio-exact/00 verified tail')

place(12000, read('.github/v8.0.2/audio-parts/part-01.b64'), 'audio-parts/01')

p = read('.github/v8.0.2/audio-parts/part-02.b64')
place(24000, p[0:6101], 'audio-parts/02 head')
place(31752, p[6080:10328], 'audio-parts/02 tail')

place(24000, read('.github/v8.0.2/audio-exact/part-03.b64'), 'audio-exact/03')
place(32000, read('.github/v8.0.2/audio-exact/part-04-0.b64'), 'audio-exact/04-0')
place(36000, read('.github/v8.0.2/audio-exact/part-04-1.b64'), 'audio-exact/04-1')

p = read('.github/v8.0.2/audio-exact/part-05.b64')
place(40000, p[0:4067], 'audio-exact/05 head')
place(38492, p[4064:5572], 'audio-exact/05 overlap')

p = read('.github/v8.0.2/audio-exact/part-07.b64')
place(56000, p[0:2554], 'audio-exact/07 head')
place(58555, p[2555:4198], 'audio-exact/07 middle')
place(61868, p[4196:6328], 'audio-exact/07 tail')

place(64000, read('.github/v8.0.2/audio-exact/part-08.b64'), 'audio-exact/08')
place(72000, read('.github/v8.0.2/audio-exact/part-09.b64'), 'audio-exact/09')
place(80000, read('.github/v8.0.2/audio-exact/part-10.b64'), 'audio-exact/10')

p = read('.github/v8.0.2/audio-exact/part-11.b64')
place(88000, p[0:5040], 'audio-exact/11')

p = read('.github/v8.0.2/audio-exact/part-12.b64')
place(96000, p[0:2637], 'audio-exact/12 head')
place(99177, p[2624:7447], 'audio-exact/12 tail')

place(104000, read('.github/v8.0.2/audio-exact/part-13.b64'), 'audio-exact/13')

p = read('.github/v8.0.2/audio-parts/part-03.b64')
place(124001, p[0:7549], 'audio-parts/03 head')
place(140468, p[7551:11083], 'audio-parts/03 tail')

p = read('.github/v8.0.2/audio-parts/part-04.b64')
place(161673, p[0:11106], 'audio-parts/04 head')
place(172780, p[11107:19779], 'audio-parts/04 tail')

gap_bundle = ''.join(
    read(str(path.relative_to(ROOT)))
    for path in sorted((ROOT / '.github/v8.0.2/gaps').glob('*.b64'))
)
if len(gap_bundle) != 57805:
    raise SystemExit(f'Gap bundle length mismatch: {len(gap_bundle)}')
if hashlib.sha256(gap_bundle.encode()).hexdigest() != 'b7897e44f4eb48a0b525742d211e8bc918c76a966ffdc6b3d4a6f8cb12b7c9c9':
    raise SystemExit('Gap bundle SHA-256 mismatch')

gap_ranges = (
    (108, 509),
    (8000, 9487),
    (44067, 56000),
    (58554, 58555),
    (60198, 61868),
    (93040, 96000),
    (98637, 99177),
    (112000, 124001),
    (131550, 140468),
    (144000, 161673),
    (172779, 172780),
    (181452, 181672),
)
cursor = 0
for start, end in gap_ranges:
    length = end - start
    place(start, gap_bundle[cursor:cursor + length], f'gap {start}:{end}')
    cursor += length
if cursor != len(gap_bundle):
    raise SystemExit(f'Unused gap bundle data: {len(gap_bundle) - cursor}')

missing = [index for index, value in enumerate(TARGET) if value is None]
if missing:
    raise SystemExit(f'Encoded audio still has {len(missing)} missing characters; first={missing[:10]}')

encoded = ''.join(TARGET)
if hashlib.sha256(encoded.encode()).hexdigest() != '11725972bc3e1779bf78c772a3d635c4e666558449dad1f8cd1e827ca110407e':
    raise SystemExit('Complete encoded audio SHA-256 mismatch')

audio = base64.b64decode(encoded, validate=True)
if len(audio) != 136254:
    raise SystemExit(f'Reconstructed audio byte-size mismatch: {len(audio)}')
if hashlib.sha256(audio).hexdigest() != '53160bd03bacf043ea3b0ffbd202163c2621e16a47ecd0f7090bfeacaf00b0d4':
    raise SystemExit('Reconstructed audio SHA-256 mismatch')

AUDIO_PATH = ROOT / 'themes/godfather/audio/godfather-flash-payout.mp3'
AUDIO_PATH.write_bytes(audio)

builder_path = ROOT / '.github/v8.0.2/build_hotfix.py'
builder = builder_path.read_text(encoding='utf-8')
start = builder.index("parts = sorted(AUDIO_PARTS.glob('part-*.b64'))")
end = builder.index('\n\nfixture_path =', start)
verification = '''audio = AUDIO_PATH.read_bytes()
if len(audio) != AUDIO_BYTES:
    raise SystemExit(f'Replacement audio size mismatch: {len(audio)}')
if hashlib.sha256(audio).hexdigest() != AUDIO_SHA:
    raise SystemExit('Replacement audio SHA-256 mismatch')'''
builder_path.write_text(builder[:start] + verification + builder[end:], encoding='utf-8')

print('Exact retained MP3 reconstructed and verified.')
print('audio_bytes', len(audio))
print('audio_sha256', hashlib.sha256(audio).hexdigest())
runpy.run_path(str(builder_path), run_name='__main__')
