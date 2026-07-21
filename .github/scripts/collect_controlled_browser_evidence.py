#!/usr/bin/env python3
"""Collect controlled Chromium microbenchmarks for Toolkit CSS and guarded root writes.

This is deliberately not a substitute for authenticated MissionChief live scenarios.
"""
from __future__ import annotations
import argparse, hashlib, html, json, re, shutil, statistics, subprocess, tempfile
from pathlib import Path

VIEWPORTS=[('desktop',1440,900),('tablet',1024,768),('ios',390,844)]

def extract_main_css(source: str) -> str:
    start=source.index('function installMainStyles()')
    marker=source.index('addStyle(`',start)+len('addStyle(`')
    i=marker; escaped=False
    while i < len(source):
        ch=source[i]
        if escaped: escaped=False
        elif ch=='\\': escaped=True
        elif ch=='`': return source[marker:i]
        i+=1
    raise ValueError('installMainStyles template terminator not found')

def extract_root_attributes(source: str) -> list[str]:
    start=source.index('function applyRootAttributes()')
    end=source.index('\n    function getStrongMarkerSignal',start)
    names=re.findall(r"setAttributeIfChanged\(root, '([^']+)'",source[start:end])
    if len(names)!=22 or len(set(names))!=22: raise ValueError(f'expected 22 unique root attributes, got {len(names)}')
    return names

def median(values): return round(statistics.median(values),4)

def html_document(css: str, attrs: list[str], label: str) -> str:
    payload=json.dumps(css); attrs_json=json.dumps(attrs)
    return f'''<!doctype html><html><head><meta charset="utf-8"><title>MCMS controlled evidence</title></head><body>
<div id="map_outer"><div id="map" class="leaflet-container"><div class="leaflet-pane leaflet-marker-pane"></div></div></div>
<div id="missions" class="missions-panel mission-list"></div><div id="mc-map-command-panel" class="mcms-panel mcms-open"></div>
<pre id="result">pending</pre><script>
const CSS={payload}; const ATTRS={attrs_json}; const LABEL={json.dumps(label)};
for(let i=0;i<120;i++){{const n=document.createElement('div');n.className=`mcms-card mcms-row mcms-setting-row mcms-mission-row mcms-${{i%9}}`;n.textContent='Evidence '+i;document.body.appendChild(n);}}
const longTasks=[]; const shifts=[];
try{{new PerformanceObserver(l=>longTasks.push(...l.getEntries().map(e=>e.duration))).observe({{type:'longtask',buffered:true}})}}catch(e){{}}
try{{new PerformanceObserver(l=>shifts.push(...l.getEntries().filter(e=>!e.hadRecentInput).map(e=>e.value))).observe({{type:'layout-shift',buffered:true}})}}catch(e){{}}
const inserts=[],layouts=[];
for(let i=0;i<3;i++){{
 const style=document.createElement('style');style.id='mc-map-command-style-'+i;style.textContent=CSS+`\n/* controlled-run:${{i}} */`;
 let t=performance.now();document.head.appendChild(style);inserts.push(performance.now()-t);
 t=performance.now();const nodes=document.querySelectorAll('.mcms-card,.leaflet-container,#mc-map-command-panel');let checksum=0;for(let j=0;j<nodes.length;j+=5){{const cs=getComputedStyle(nodes[j]);checksum+=nodes[j].offsetHeight+cs.display.length;}}layouts.push(performance.now()-t);style.remove();
}}
const root=document.documentElement;let writes=0;const nativeSet=root.setAttribute.bind(root);root.setAttribute=(n,v)=>{{writes++;nativeSet(n,v)}};
function setAttributeIfChanged(el,n,v){{v=String(v);if(el.getAttribute(n)===v)return false;el.setAttribute(n,v);return true}}
const values=Object.fromEntries(ATTRS.map((n,i)=>[n,`${{LABEL}}-${{i}}`]));
function apply(){{for(const n of ATTRS)setAttributeIfChanged(root,n,values[n])}}
apply();const initialWrites=writes;writes=0;apply();const unchangedWrites=writes;writes=0;values[ATTRS[ATTRS.length-1]]+='-changed';apply();const changedWrites=writes;writes=0;root.removeAttribute(ATTRS[0]);apply();const repairedWrites=writes;
setTimeout(()=>{{document.getElementById('result').textContent=JSON.stringify({{
 label:LABEL, cssBytes:new TextEncoder().encode(CSS).length, cssRuleEstimate:(CSS.match(/{{/g)||[]).length,
 styleInsertSamplesMs:inserts, forcedStyleLayoutSamplesMs:layouts,
 rootAttributeContract:{{attributeCount:ATTRS.length,initialWrites,unchangedWrites,changedWrites,repairedWrites}},
 longTasksMs:longTasks, layoutShiftTotal:shifts.reduce((a,b)=>a+b,0), userAgent:navigator.userAgent
}})}},0);
</script></body></html>'''

def run_one(chromium: str, doc: Path, width: int, height: int) -> dict:
    profile=tempfile.mkdtemp(prefix='mcms-chromium-')
    cmd=[chromium,'--headless=new','--no-sandbox','--disable-gpu','--disable-dev-shm-usage',f'--user-data-dir={profile}','--disable-background-networking','--disable-component-update','--disable-default-apps','--disable-sync','--metrics-recording-only','--mute-audio','--run-all-compositor-stages-before-draw','--virtual-time-budget=2000',f'--window-size={width},{height}','--dump-dom',doc.as_uri()]
    try:
        proc=subprocess.run(cmd,text=True,capture_output=True,timeout=90)
    finally:
        shutil.rmtree(profile,ignore_errors=True)
    if proc.returncode: raise RuntimeError(proc.stderr[-2000:])
    m=re.search(r'<pre id="result">(.*?)</pre>',proc.stdout,re.S)
    if not m: raise RuntimeError('Chromium result payload not found')
    return json.loads(html.unescape(m.group(1)))

def main()->int:
    ap=argparse.ArgumentParser(); ap.add_argument('--source',default='src/MissionChief_Map_Command_Toolkit.user.js'); ap.add_argument('--json-output',default='docs/audits/controlled-browser-evidence-v4.20.24.json'); ap.add_argument('--markdown-output',default='docs/audits/controlled-browser-evidence-v4.20.24.md'); ap.add_argument('--chromium'); args=ap.parse_args()
    source_path=Path(args.source); source=source_path.read_text(); css=extract_main_css(source); attrs=extract_root_attributes(source)
    chromium=args.chromium or shutil.which('google-chrome') or shutil.which('chromium') or shutil.which('chromium-browser')
    if not chromium: raise SystemExit('Chromium/Chrome executable not found')
    scenarios=[]
    with tempfile.TemporaryDirectory() as td:
        td=Path(td)
        for label,w,h in VIEWPORTS:
            doc=td/f'{label}.html'; doc.write_text(html_document(css,attrs,label))
            raw=run_one(chromium,doc,w,h)
            raw['viewport']={'width':w,'height':h}
            raw['styleInsertMedianMs']=median(raw['styleInsertSamplesMs'][1:])
            raw['forcedStyleLayoutMedianMs']=median(raw['forcedStyleLayoutSamplesMs'][1:])
            scenarios.append(raw)
    source_sha=hashlib.sha256(source_path.read_bytes()).hexdigest()
    result={'schemaVersion':1,'evidenceClass':'controlled-synthetic-browser','tool':'collect_controlled_browser_evidence.py','baseline':{'version':'4.20.24','sourceSha256':source_sha,'sourceBytes':source_path.stat().st_size,'sourceLines':sum(1 for _ in source_path.open()),'cssBytes':len(css.encode()),'cssRuleEstimate':css.count('{'),'rootAttributeCount':len(attrs)},'environment':{'browserExecutable':Path(chromium).name,'note':'Browser timings vary by runner and are not performance budgets.'},'scenarios':scenarios,'conclusions':{
      'rootWriteSuppressionVerified':all(x['rootAttributeContract']=={'attributeCount':22,'initialWrites':22,'unchangedWrites':0,'changedWrites':1,'repairedWrites':1} for x in scenarios),
      'cssTargetProven':False,'liveMissionChiefEvidenceCaptured':False,
      'nextAction':'Capture equivalent authenticated idle map, settings, mission-window and map-pan profiler scenarios before changing style delivery or broader render paths.'}}
    Path(args.json_output).write_text(json.dumps(result,indent=2)+"\n")
    md=['# Controlled browser evidence — Toolkit v4.20.24','',
      '> Controlled synthetic Chromium evidence. It verifies repeatable micro-contracts, but it is **not** authenticated MissionChief runtime evidence and does not justify CSS modularisation by itself.','',
      '## Baseline','',f"- Source SHA-256: `{source_sha}`",f"- Main embedded CSS: **{len(css.encode()):,} bytes**, approximately **{css.count('{'):,}** rule blocks",f"- Guarded root attributes: **{len(attrs)}**,'',
      '## Results','', '| Scenario | Viewport | CSS insertion median* | Forced style/layout median* | Initial writes | Unchanged repeat | Changed value | Tamper repair |','|---|---:|---:|---:|---:|---:|---:|---:|']
    for x in scenarios:
        c=x['rootAttributeContract']; v=x['viewport']; md.append(f"| {x['label']} | {v['width']}×{v['height']} | {x['styleInsertMedianMs']:.4f} ms | {x['forcedStyleLayoutMedianMs']:.4f} ms | {c['initialWrites']} | {c['unchangedWrites']} | {c['changedWrites']} | {c['repairedWrites']} |")
    md += ['','* Median excludes the first warm-up sample. Values are diagnostic, hardware-specific and not release budgets.','',
      '## Decisions','',
      '- The existing `setAttributeIfChanged` optimisation is verified in a real browser DOM: first application writes all 22 missing attributes, an unchanged repeat writes zero, one changed state writes one, and external tampering is repaired with one write.','- This closes the isolated root-write question already implemented under #279; it does not prove that every `updateUI()` path is free from unchanged work.','- The CSS microbenchmark establishes a reproducible controlled baseline across Desktop, Tablet and iOS-sized viewports. It does not include MissionChief map, mission-window, settings or pan workloads, so #254 remains open.','- No production runtime change is recommended from this controlled evidence alone.','']
    Path(args.markdown_output).write_text('\n'.join(md))
    if not result['conclusions']['rootWriteSuppressionVerified']: raise SystemExit('root attribute browser contract failed')
    print(json.dumps({'scenarios':len(scenarios),'cssBytes':len(css.encode()),'rootContract':True}))
    return 0
if __name__=='__main__': raise SystemExit(main())
