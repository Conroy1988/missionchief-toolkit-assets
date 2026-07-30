#!/usr/bin/env python3
"""Controlled Chrome microbenchmarks for Toolkit CSS and guarded root writes.

This produces synthetic browser evidence only. It is not a substitute for
an authenticated MissionChief runtime capture.
"""
from __future__ import annotations

import argparse
import hashlib
import html
import json
import re
import shutil
import statistics
import subprocess
import tempfile
from pathlib import Path

VIEWPORTS = [('desktop', 1440, 900), ('tablet', 1024, 768), ('ios', 390, 844)]
DEFAULT_SAMPLES = 11


def toolkit_version(source: str) -> str:
    match = re.search(r'(?m)^//\s*@version\s+([^\s]+)\s*$', source)
    if not match:
        raise ValueError('Toolkit metadata version not found')
    return match.group(1)


def extract_main_css(source: str) -> str:
    start = source.index('function installMainStyles()')
    marker = source.index('addStyle(`', start) + len('addStyle(`')
    escaped = False
    for index in range(marker, len(source)):
        char = source[index]
        if escaped:
            escaped = False
        elif char == '\\':
            escaped = True
        elif char == '`':
            return source[marker:index]
    raise ValueError('installMainStyles template terminator not found')


def extract_root_attributes(source: str) -> list[str]:
    start = source.index('function applyRootAttributes()')
    remainder = source[start + len('function applyRootAttributes()'):]
    next_function = re.search(r'(?m)^\s*function\s+[A-Za-z_$][\w$]*\s*\(', remainder)
    if not next_function:
        raise ValueError('applyRootAttributes boundary not found')
    end = start + len('function applyRootAttributes()') + next_function.start()
    names = re.findall(r"setAttributeIfChanged\(root, '([^']+)'", source[start:end])
    if not names or len(names) != len(set(names)):
        raise ValueError(f'expected a non-empty unique root-attribute set, got {len(names)}')
    return names


def rounded_median(values: list[float]) -> float:
    return round(statistics.median(values), 4)


def percentile(values: list[float], fraction: float) -> float:
    if not values:
        return 0.0
    ordered = sorted(values)
    index = round((len(ordered) - 1) * fraction)
    return round(ordered[max(0, min(index, len(ordered) - 1))], 4)


def html_document(css: str, attributes: list[str], label: str, samples: int) -> str:
    css_json = json.dumps(css)
    attributes_json = json.dumps(attributes)
    label_json = json.dumps(label)
    return f'''<!doctype html><html><head><meta charset="utf-8"><title>MCMS controlled evidence</title></head><body>
<div id="map_outer"><div id="map" class="leaflet-container"><div class="leaflet-pane leaflet-marker-pane"></div></div></div>
<div id="missions" class="missions-panel mission-list"></div><div id="mc-map-command-panel" class="mcms-panel mcms-open"></div>
<pre id="result">pending</pre><script>
const CSS={css_json};const ATTRS={attributes_json};const LABEL={label_json};const SAMPLES={samples};
for(let i=0;i<240;i++){{const n=document.createElement('div');n.className=`mcms-card mcms-row mcms-setting-row mcms-mission-row mcms-${{i%13}}`;n.textContent='Evidence '+i;document.body.appendChild(n);}}
const longTasks=[];const shifts=[];
try{{new PerformanceObserver(l=>longTasks.push(...l.getEntries().map(e=>e.duration))).observe({{type:'longtask',buffered:true}})}}catch(e){{}}
try{{new PerformanceObserver(l=>shifts.push(...l.getEntries().filter(e=>!e.hadRecentInput).map(e=>e.value))).observe({{type:'layout-shift',buffered:true}})}}catch(e){{}}
const inserts=[];const layouts=[];
for(let i=0;i<SAMPLES;i++){{
 const style=document.createElement('style');style.id='mc-map-command-style-'+i;style.textContent=CSS+`\n/* controlled-run:${{i}} */`;
 let t=performance.now();document.head.appendChild(style);inserts.push(performance.now()-t);
 t=performance.now();const nodes=document.querySelectorAll('.mcms-card,.leaflet-container,#mc-map-command-panel');let checksum=0;
 for(let j=0;j<nodes.length;j+=5){{const cs=getComputedStyle(nodes[j]);checksum+=nodes[j].offsetHeight+cs.display.length;}}
 layouts.push(performance.now()-t);style.remove();
}}
const root=document.documentElement;let writes=0;const nativeSet=root.setAttribute.bind(root);root.setAttribute=(n,v)=>{{writes++;nativeSet(n,v)}};
function setAttributeIfChanged(el,n,v){{v=String(v);if(el.getAttribute(n)===v)return false;el.setAttribute(n,v);return true}}
const values=Object.fromEntries(ATTRS.map((n,i)=>[n,`${{LABEL}}-${{i}}`]));
function apply(){{for(const n of ATTRS)setAttributeIfChanged(root,n,values[n])}}
apply();const initialWrites=writes;writes=0;apply();const unchangedWrites=writes;writes=0;
values[ATTRS[ATTRS.length-1]]+='-changed';apply();const changedWrites=writes;writes=0;
root.removeAttribute(ATTRS[0]);apply();const repairedWrites=writes;
setTimeout(()=>{{document.getElementById('result').textContent=JSON.stringify({{
 label:LABEL,cssBytes:new TextEncoder().encode(CSS).length,cssRuleEstimate:(CSS.match(/{{/g)||[]).length,
 styleInsertSamplesMs:inserts,forcedStyleLayoutSamplesMs:layouts,
 rootAttributeContract:{{attributeCount:ATTRS.length,initialWrites,unchangedWrites,changedWrites,repairedWrites}},
 longTasksMs:longTasks,layoutShiftTotal:shifts.reduce((a,b)=>a+b,0),userAgent:navigator.userAgent
}})}},0);
</script></body></html>'''


def run_one(chromium: str, document: Path, width: int, height: int) -> dict:
    profile = tempfile.mkdtemp(prefix='mcms-chromium-')
    command = [
        chromium, '--headless=new', '--no-sandbox', '--disable-gpu',
        '--disable-dev-shm-usage', f'--user-data-dir={profile}',
        '--disable-background-networking', '--disable-component-update',
        '--disable-default-apps', '--disable-sync', '--metrics-recording-only',
        '--mute-audio', '--run-all-compositor-stages-before-draw',
        '--virtual-time-budget=3000', f'--window-size={width},{height}',
        '--dump-dom', document.as_uri(),
    ]
    try:
        process = subprocess.run(command, text=True, capture_output=True, timeout=90)
    finally:
        shutil.rmtree(profile, ignore_errors=True)
    if process.returncode:
        raise RuntimeError(process.stderr[-2000:])
    match = re.search(r'<pre id="result">(.*?)</pre>', process.stdout, re.S)
    if not match:
        raise RuntimeError('Chromium result payload not found')
    return json.loads(html.unescape(match.group(1)))


def render_markdown(result: dict) -> str:
    baseline = result['baseline']
    lines = [
        f"# Controlled Chrome evidence — Toolkit v{baseline['version']}", '',
        '> Controlled synthetic Chromium evidence. It verifies repeatable micro-contracts, but it is **not** authenticated MissionChief runtime evidence and does not justify CSS modularisation by itself.', '',
        '## Baseline', '',
        f"- Source SHA-256: `{baseline['sourceSha256']}`",
        f"- Source: **{baseline['sourceBytes']:,} bytes**, **{baseline['sourceLines']:,} lines**",
        f"- Main embedded CSS: **{baseline['cssBytes']:,} bytes**, approximately **{baseline['cssRuleEstimate']:,}** rule blocks",
        f"- Guarded root attributes: **{baseline['rootAttributeCount']}**",
        f"- Samples per viewport: **{result['environment']['samplesPerViewport']}** (first sample excluded from summary medians)", '',
        '## Results', '',
        '| Scenario | Viewport | CSS insertion median* | CSS insertion P90* | Forced style/layout median* | Forced style/layout P90* | Long tasks | Layout shift | Unchanged root writes |',
        '|---|---:|---:|---:|---:|---:|---:|---:|---:|',
    ]
    for scenario in result['scenarios']:
        viewport = scenario['viewport']
        contract = scenario['rootAttributeContract']
        lines.append(
            f"| {scenario['label']} | {viewport['width']}×{viewport['height']} | "
            f"{scenario['styleInsertMedianMs']:.4f} ms | {scenario['styleInsertP90Ms']:.4f} ms | "
            f"{scenario['forcedStyleLayoutMedianMs']:.4f} ms | {scenario['forcedStyleLayoutP90Ms']:.4f} ms | "
            f"{len(scenario['longTasksMs'])} | {scenario['layoutShiftTotal']:.6f} | {contract['unchangedWrites']} |"
        )
    lines += [
        '', '* The first sample is a warm-up and is excluded. Values are diagnostic, hardware-specific and are not release budgets.', '',
        '## Decisions', '',
        '- The guarded root-write contract remains correct for the current authoritative attribute set: first application writes every missing attribute, an unchanged repeat writes zero, one changed value writes one and external tampering is repaired with one write.',
        '- The controlled Chrome measurements establish a current reproducible baseline across Desktop, Tablet and iOS-sized viewports.',
        '- This evidence does not contain MissionChief map, mission-window, settings or pan workloads. It does not prove a user-visible CSS bottleneck and does not authorise stylesheet modularisation.',
        '- Equivalent authenticated MissionChief profiler scenarios remain required before changing style delivery.', '',
    ]
    return '\n'.join(lines)


def collect(source_path: Path, chromium: str, samples: int) -> dict:
    source = source_path.read_text(encoding='utf-8')
    css = extract_main_css(source)
    attributes = extract_root_attributes(source)
    scenarios = []
    with tempfile.TemporaryDirectory() as temporary:
        root = Path(temporary)
        for label, width, height in VIEWPORTS:
            document = root / f'{label}.html'
            document.write_text(html_document(css, attributes, label, samples), encoding='utf-8')
            raw = run_one(chromium, document, width, height)
            raw['viewport'] = {'width': width, 'height': height}
            insert_samples = raw['styleInsertSamplesMs'][1:]
            layout_samples = raw['forcedStyleLayoutSamplesMs'][1:]
            raw['styleInsertMedianMs'] = rounded_median(insert_samples)
            raw['styleInsertP90Ms'] = percentile(insert_samples, 0.9)
            raw['forcedStyleLayoutMedianMs'] = rounded_median(layout_samples)
            raw['forcedStyleLayoutP90Ms'] = percentile(layout_samples, 0.9)
            scenarios.append(raw)
    source_bytes = source_path.read_bytes()
    expected_contract = {
        'attributeCount': len(attributes),
        'initialWrites': len(attributes),
        'unchangedWrites': 0,
        'changedWrites': 1,
        'repairedWrites': 1,
    }
    return {
        'schemaVersion': 2,
        'evidenceClass': 'controlled-synthetic-browser',
        'tool': 'collect_controlled_browser_evidence.py',
        'baseline': {
            'version': toolkit_version(source),
            'sourceSha256': hashlib.sha256(source_bytes).hexdigest(),
            'sourceBytes': len(source_bytes),
            'sourceLines': len(source.splitlines()),
            'cssBytes': len(css.encode('utf-8')),
            'cssRuleEstimate': css.count('{'),
            'rootAttributeCount': len(attributes),
        },
        'environment': {
            'browserExecutable': Path(chromium).name,
            'samplesPerViewport': samples,
            'note': 'Browser timings vary by runner and are not performance budgets.',
        },
        'scenarios': scenarios,
        'conclusions': {
            'rootWriteSuppressionVerified': all(scenario['rootAttributeContract'] == expected_contract for scenario in scenarios),
            'cssTargetProven': False,
            'liveMissionChiefEvidenceCaptured': False,
            'nextAction': 'Capture equivalent authenticated idle map, settings, mission-window and map-pan profiler scenarios before changing style delivery.',
        },
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument('--source', default='src/MissionChief_Map_Command_Toolkit.user.js')
    parser.add_argument('--json-output', default='docs/audits/issue-593/controlled-browser-evidence.json')
    parser.add_argument('--markdown-output', default='docs/audits/issue-593/controlled-browser-evidence.md')
    parser.add_argument('--chromium')
    parser.add_argument('--samples', type=int, default=DEFAULT_SAMPLES)
    args = parser.parse_args()
    if not 3 <= args.samples <= 50:
        raise SystemExit('--samples must be between 3 and 50')
    source_path = Path(args.source)
    chromium = args.chromium or shutil.which('google-chrome') or shutil.which('google-chrome-stable') or shutil.which('chromium') or shutil.which('chromium-browser')
    if not chromium:
        raise SystemExit('Chromium/Chrome executable not found')
    result = collect(source_path, chromium, args.samples)
    json_path = Path(args.json_output)
    markdown_path = Path(args.markdown_output)
    json_path.parent.mkdir(parents=True, exist_ok=True)
    markdown_path.parent.mkdir(parents=True, exist_ok=True)
    json_path.write_text(json.dumps(result, indent=2) + '\n', encoding='utf-8')
    markdown_path.write_text(render_markdown(result), encoding='utf-8')
    if not result['conclusions']['rootWriteSuppressionVerified']:
        raise SystemExit('root attribute browser contract failed')
    print(json.dumps({
        'version': result['baseline']['version'],
        'scenarios': len(result['scenarios']),
        'samplesPerViewport': args.samples,
        'cssBytes': result['baseline']['cssBytes'],
        'rootAttributeCount': result['baseline']['rootAttributeCount'],
        'rootContract': True,
    }))
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
