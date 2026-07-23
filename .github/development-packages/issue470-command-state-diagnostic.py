#!/usr/bin/env python3
from pathlib import Path
import re

ROOT=Path(__file__).resolve().parents[2]
SELF=Path(__file__).resolve()
SOURCE=ROOT/'src/MissionChief_Map_Command_Toolkit.user.js'
OUT=ROOT/'.github/diagnostics/issue470-command-state.txt'
text=SOURCE.read_text(encoding='utf-8')
lines=text.splitlines()
parts=['ISSUE #470 COMMAND STATE DIAGNOSTIC',f'source_lines={len(lines)}','']

for name,start,end in [
    ('state-hydration',1450,1740),
    ('command-toggle',28720,28895),
    ('root-attributes',27450,28280),
    ('command-css',2150,3000),
]:
    parts.extend(['='*110,f'{name} lines {start}-{end}'])
    parts.extend(f'{n:05d}: {lines[n-1]}' for n in range(start,min(end,len(lines))+1))
    parts.append('')

parts.extend(['='*110,'commandBarOpen occurrences'])
for match in re.finditer(r'commandBarOpen',text):
    ln=text.count('\n',0,match.start())+1
    lo=max(1,ln-5);hi=min(len(lines),ln+5)
    parts.extend(f'{n:05d}: {lines[n-1]}' for n in range(lo,hi+1))
    parts.append('---')

for token in ['toggleCommandBar','commandBarAnimating','mcms-dock-collapsed','mcms-floating-filter','mcms-screen-pins']:
    parts.extend(['='*110,token])
    count=0
    for match in re.finditer(re.escape(token),text,re.I):
        ln=text.count('\n',0,match.start())+1
        lo=max(1,ln-4);hi=min(len(lines),ln+4)
        parts.extend(f'{n:05d}: {lines[n-1]}' for n in range(lo,hi+1))
        parts.append('---')
        count+=1
        if count>=50:
            parts.append('[truncated]');break

OUT.parent.mkdir(parents=True,exist_ok=True)
OUT.write_text('\n'.join(parts)+'\n',encoding='utf-8')
SELF.unlink(missing_ok=True)
print(OUT.relative_to(ROOT))
