#!/usr/bin/env python3
import hashlib,json,re
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2];text=(ROOT/'src'/'MissionChief_Map_Command_Toolkit.user.js').read_text(encoding='utf-8');p=json.loads((ROOT/'.github/fixtures/main-style-source-headroom.json').read_text(encoding='utf-8'))['v7Candidate']
start=text.index('function installMainStyles()');a=text.index('addStyle(`',start)+len('addStyle(`');metric=text.index("recordStartupMetric('stylesheetInstallMs'",a);b=text.rfind('`);',a,metric);raw=text[a:b]
lines=raw.split('\n');canonical=re.sub(r'\n[\t ]*}','}','\n'.join(line for i,line in enumerate(lines) if not (0<i<len(lines)-1 and not line.strip())))
actual={'sourceBytes':len(text.encode()),'sourceLines':len(text.splitlines()),'sourceSha256':hashlib.sha256(text.encode()).hexdigest(),'templateBytes':len(raw.encode()),'templateLines':len(lines),'templateSha256':hashlib.sha256(raw.encode()).hexdigest(),'canonicalCssSha256':hashlib.sha256(canonical.encode()).hexdigest()}
assert all(actual[k]==p[k] for k in actual),(actual,p);print('Main-style source-headroom contract passed for v7.')
