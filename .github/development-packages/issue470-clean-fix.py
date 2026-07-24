#!/usr/bin/env python3
from __future__ import annotations

import base64
import hashlib
import zlib
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
PACKAGE_DIR = ROOT / '.github/development-packages'
EXPECTED = [
    ('issue470-clean-v3.payload.000', '362d6ade371b3038df223461526aac822b823fef021ff37fdfd0e0f3ca29a46e'),
    ('issue470-clean-v3.payload.001', '05ef1bb229d76276233a250ff98668acb7b6487f118eb0be9972f65700c3822a'),
    ('issue470-clean-v3.payload.002', 'b4f965cdc96863dc16f804fbd3694d0fc9c3721cebb185ea8e391ca2d53006c4'),
    ('issue470-clean-v3.payload.003', '19da514b7746e552513bd6f890f6fd97f74b6b79fb6b4240c4411904dcaaa33e'),
    ('issue470-clean-v3.payload.004', '6d3fa9b242998a151608d77a0eda1cc7d84670dab05cb039e6e4766283960f12'),
    ('issue470-clean-v3.payload.005', '6d62cddcfc4c288531ee5a671a81339d83b972fdde5cc423a0de317ea2181338'),
    ('issue470-clean-v3.payload.006', '2f9c9726ff0fe1d13b8bd5cb4482b47a3c64dbc4a5fa54613788bf2e4e722ac4'),
    ('issue470-clean-v3.payload.007', '6e127e79fee8afe6e50ed0df05033393480766f364ae6734b26dc8f953e93022'),
    ('issue470-clean-v3.payload.008', '8ab5896a8c53b286ca80f2771c8501a4987b6611c6999546ec6825579de721ad'),
    ('issue470-clean-v3.payload.009', 'ddea0e43ce9c47fa4d500e7a3575c6b922555dccd42f7be17d221483e6aa41e3'),
    ('issue470-clean-v3.payload.010', 'db2f63d8b20e444bcffeee49055fea34267270b99b8d88793ef05f25060752cc'),
    ('issue470-clean-v3.payload.011', '1454d42e6359c7ed9c1011d6859017f79e8d1de9e1879d6c77dd7eea490790f9'),
    ('issue470-clean-v3.payload.012', '0e08cc756e4b570cc86c1e29c95e16dd3da8824e6e26a05cf24fcd647a2a5ea3'),
    ('issue470-clean-v3.payload.013', '695332ded40e21c9308bb86bfb9eea4823c38780ba9e072ab7981990f686e744'),
    ('issue470-clean-v3.payload.014', '97dd36510bb787be33ec86bbf049846aa9ee2ab5c55fb20d57309d1ccc31019f'),
    ('issue470-clean-v3.payload.015', 'def653d5d9287080dc02b095c06e970186f74672fd2f32e76a91e4ddff298763'),
    ('issue470-clean-v3.payload.016', '756cd905ca1ab1b6c188a16d0896bb0f14e3a9f97bc2d42a7d9200d413cff1e8'),
    ('issue470-clean-v3.payload.017', '5fe5eb5eee9321699db68e8d9ef3c584d8f9aecc22aea262c5da3096e75bc76b'),
    ('issue470-clean-v3.payload.018', 'd2e22fec355bb2054750ac0b84113eed894af3c8c8839217f054e0d257a3118d'),
]

chunks: list[str] = []
for name, expected_sha in EXPECTED:
    path = PACKAGE_DIR / name
    if not path.exists():
        raise SystemExit(f'Issue #470 verified payload part is missing: {name}')
    value = path.read_text(encoding='utf-8').strip()
    actual_sha = hashlib.sha256(value.encode('utf-8')).hexdigest()
    if actual_sha != expected_sha:
        raise SystemExit(f'Issue #470 payload checksum mismatch: {name}: {actual_sha}')
    chunks.append(value)

encoded = ''.join(chunks)
encoded_sha = hashlib.sha256(encoded.encode('utf-8')).hexdigest()
if encoded_sha != '7d3b40179cac66978313bce94d84c3fb6502860c9ec53941c8355d361e5402e7':
    raise SystemExit(f'Issue #470 complete payload checksum mismatch: {encoded_sha}')
code = zlib.decompress(base64.b64decode(encoded)).decode('utf-8')
code_sha = hashlib.sha256(code.encode('utf-8')).hexdigest()
if code_sha != 'e8ba3088536ad44254fbcf36aafa6c88af4220f10fb0762e14361455cc82ff7d':
    raise SystemExit(f'Issue #470 decoded package checksum mismatch: {code_sha}')

bad_fixture = "    }}};\n  };\n  attach(value,[...native,...carriers,...groups,missionRoot]);"
good_fixture = "    }}}\n  };\n  attach(value,[...native,...carriers,...groups,missionRoot]);"
if code.count(bad_fixture) != 1:
    raise SystemExit(f'Issue #470 runtime-fixture syntax anchor count changed: {code.count(bad_fixture)}')
code = code.replace(bad_fixture, good_fixture, 1)

for pattern in ('issue470-clean.payload.*', 'issue470-clean-v2.payload.*', 'issue470-clean-v3.payload.*'):
    for path in PACKAGE_DIR.glob(pattern):
        path.unlink(missing_ok=True)
(ROOT / '.github/diagnostics/issue470-clean-preflight.txt').unlink(missing_ok=True)
exec(compile(code, __file__, 'exec'))
