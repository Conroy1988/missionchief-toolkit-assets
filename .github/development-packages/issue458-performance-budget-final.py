#!/usr/bin/env python3
from __future__ import annotations
import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
SELF = Path(__file__).resolve()
SOURCE = ROOT / 'src/MissionChief_Map_Command_Toolkit.user.js'
TEST = ROOT / '.github/scripts/test_issue458_requirements_source_runtime.js'
FIXTURE = ROOT / '.github/fixtures/main-style-source-headroom.json'
CHANGELOG = ROOT / 'CHANGELOG.md'
DIAGNOSTIC = ROOT / '.github/diagnostics/issue458-performance-apply-validator.txt'
text = SOURCE.read_text(encoding='utf-8')
if '// @version      5.0.5' not in text:
    raise SystemExit('Final Issue #458 package requires v5.0.5')
old = '''        const holder = doc.createElement('div');
        holder.setAttribute('data-mcms-requirement-source', 'lssm-raw');
        holder.innerHTML = rawHtml;
        return holder.querySelector?.('[data-requirement-type]') ? holder : null;'''
new = '''        const range = doc.createRange?.();
        const fragment = range?.createContextualFragment?.(rawHtml);
        if (!fragment?.querySelector?.('[data-requirement-type]')) return null;
        return fragment;'''
if text.count(old) != 1:
    raise SystemExit(f'Expected one LSSM raw innerHTML parser, found {text.count(old)}')
text = text.replace(old, new, 1)
SOURCE.write_text(text, encoding='utf-8')
for target in (ROOT / 'MissionChief_Map_Command_Toolkit.user.js', ROOT / 'MissionChief_Map_Command_Toolkit.txt'):
    target.write_text(text, encoding='utf-8')

test = TEST.read_text(encoding='utf-8')
old_doc = "querySelector(selector){return selector.includes('#mission-form')?this.missionRoot:null;},createElement(){const node=new Node({visible:false});node.ownerDocument=value;return node;}};"
new_doc = '''querySelector(selector){return selector.includes('#mission-form')?this.missionRoot:null;},createRange(){return{createContextualFragment(html){
    const raw=String(html||'');
    const type=raw.match(/data-requirement-type="([^"]+)"/iu)?.[1]||'';
    const heading=raw.match(/<b>([^<]*)<\/b>/iu)?.[1]||'';
    const plain=raw.replace(/<[^>]+>/gu,' ').replace(/\s+/gu,' ').trim();
    const node=new Node({visible:false,text:plain});node.ownerDocument=value;
    if(type){const group=new Node({visible:false,text:plain,attrs:{'data-requirement-type':type}});group.ownerDocument=value;group.querySelector=selector=>selector==='b'&&heading?new Node({text:heading}):null;node.groups=[group];}
    return node;
}}}};'''
if test.count(old_doc) != 1:
    raise SystemExit('Issue #458 fake document parser anchor is missing')
test = test.replace(old_doc, new_doc, 1)
anchor = "if(!source.includes('filter(root => root && root.isConnected !== false)'))throw new Error('observer root filter admits null candidates');\n"
assertion = "if(!source.includes('createContextualFragment?.(rawHtml)')||source.includes('holder.innerHTML = rawHtml'))throw new Error('LSSM raw parser exceeds the innerHTML performance budget');\n"
if anchor not in test:
    raise SystemExit('Issue #458 performance assertion anchor is missing')
if assertion not in test:
    test = test.replace(anchor, anchor + assertion, 1)
TEST.write_text(test, encoding='utf-8')

fixture = json.loads(FIXTURE.read_text(encoding='utf-8'))
fixture['candidateSourceSha256'] = hashlib.sha256(text.encode('utf-8')).hexdigest()
if fixture['expectedSourceLines'] != len(text.splitlines()):
    raise SystemExit('Performance correction unexpectedly changed the source-line ledger')
FIXTURE.write_text(json.dumps(fixture, indent=2) + '\n', encoding='utf-8')

changelog = CHANGELOG.read_text(encoding='utf-8')
anchor = '- Rebound the operational observer whenever the authoritative source changes and added behavioural coverage for duplicate, stale, delayed, LSSM and Toolkit-owned roots.\n'
addition = '- Decoded hidden LSSM raw markup with a contextual fragment rather than adding another `innerHTML` assignment site, preserving the established performance ceiling.\n'
if anchor not in changelog:
    raise SystemExit('v5.0.5 changelog anchor is missing')
if addition not in changelog:
    changelog = changelog.replace(anchor, anchor + addition, 1)
CHANGELOG.write_text(changelog, encoding='utf-8')
DIAGNOSTIC.unlink(missing_ok=True)
SELF.unlink(missing_ok=True)
print(json.dumps({'version':'5.0.5','sha256':fixture['candidateSourceSha256'],'innerHtmlParser':'createContextualFragment','diagnosticRemoved':True}, indent=2))
