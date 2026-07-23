#!/usr/bin/env python3
from __future__ import annotations
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2]
SOURCE=ROOT/'src/MissionChief_Map_Command_Toolkit.user.js'
OUTPUT=ROOT/'.github/diagnostics/v5-operational-scan-path.txt'
text=SOURCE.read_text(encoding='utf-8')

def line_no(pos:int)->int:return text.count('\n',0,pos)+1

def extract(name:str)->str:
    start=text.find(f'function {name}(')
    if start<0:return f'===== {name}: NOT FOUND =====\n'
    brace=text.find('{',start); depth=0; quote=None; esc=False; line_comment=False; block=False; i=brace
    while i<len(text):
        c=text[i]; n=text[i+1] if i+1<len(text) else ''
        if line_comment:
            if c=='\n':line_comment=False
        elif block:
            if c=='*' and n=='/':block=False;i+=1
        elif quote:
            if esc:esc=False
            elif c=='\\':esc=True
            elif c==quote:quote=None
        else:
            if c=='/' and n=='/':line_comment=True;i+=1
            elif c=='/' and n=='*':block=True;i+=1
            elif c in "'\"`":quote=c
            elif c=='{':depth+=1
            elif c=='}':
                depth-=1
                if depth==0:
                    block_text=text[start:i+1]; base=line_no(start)
                    return f'===== {name} at {base} =====\n'+'\n'.join(f'{base+j:06d}: {line}' for j,line in enumerate(block_text.splitlines()))+'\n\n'
        i+=1
    return f'===== {name}: UNTERMINATED =====\n'

names=(
'scanOperationalSuiteShell','operationalSuiteDocuments','operationalSuiteDiscoverDocuments','reconcileOperationalSuiteContext',
'createOperationalSuiteContext','scheduleOperationalSuiteScan','installOperationalSuiteShell','runDeferredOperationalStartup',
'getLargestLeafletMap','findLeafletMapInstance','operationalQueryAll')
parts=['V5_OPERATIONAL_SCAN_PATH\n\n']
for name in names:parts.append(extract(name))
OUTPUT.parent.mkdir(parents=True,exist_ok=True);OUTPUT.write_text(''.join(parts),encoding='utf-8')
print(f'Wrote {OUTPUT.relative_to(ROOT)}')
