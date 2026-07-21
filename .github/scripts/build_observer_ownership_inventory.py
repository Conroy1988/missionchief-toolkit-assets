#!/usr/bin/env python3
"""Build the reviewed observer ownership inventory from AST evidence and manual lifecycle annotations."""
from __future__ import annotations
import argparse, hashlib, json
from pathlib import Path


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main() -> int:
    ap=argparse.ArgumentParser()
    ap.add_argument('--source', default='src/MissionChief_Map_Command_Toolkit.user.js')
    ap.add_argument('--deep-json', default='docs/audits/deep-performance-audit-v4.20.24.json')
    ap.add_argument('--fixture', default='.github/fixtures/observer-ownership-v4.20.24.json')
    ap.add_argument('--json-output', default='docs/audits/observer-ownership-v4.20.24.json')
    ap.add_argument('--markdown-output', default='docs/audits/observer-ownership-v4.20.24.md')
    args=ap.parse_args()
    source=Path(args.source); deep=json.loads(Path(args.deep_json).read_text()); fixture=json.loads(Path(args.fixture).read_text())
    baseline=fixture['baseline']
    actual_sha=sha256(source)
    if actual_sha != baseline['sourceSha256']:
        raise SystemExit(f"source SHA mismatch: {actual_sha} != {baseline['sourceSha256']}")
    constructions=deep['observerConstructions']; annotations={x['key']:x for x in fixture['observers']}
    rows=[]
    for item in constructions:
        key=f"{item['function']}|{item['constructor']}|{item['variable']}"
        if key not in annotations: raise SystemExit(f'missing manual annotation: {key}')
        ann=annotations[key]
        regs=list(item.get('registrations') or [])
        regs.extend(ann.get('manualRegistrations') or [])
        row={
            'key':key,'subsystem':ann['subsystem'],'constructor':item['constructor'],'variable':item['variable'],
            'constructionLine':item['line'],'installation':ann['installation'],'registrations':regs,
            'scheduling':ann['scheduling'],'ownership':ann['ownership'],'teardown':ann['teardown'],
            'duplicateGuard':ann['duplicateGuard'],'documentReplacement':ann['documentReplacement'],
            'coverage':ann['coverage'],'status':ann['status']
        }
        rows.append(row)
    if len(rows) != baseline['observerConstructions']: raise SystemExit('observer construction count mismatch')
    mutation=sum(r['constructor']=='MutationObserver' for r in rows); resize=sum(r['constructor']=='ResizeObserver' for r in rows)
    registrations=sum(len(r['registrations']) for r in rows)
    broad=sum(bool(x.get('subtree') or x.get('broad')) for r in rows for x in r['registrations'])
    explicit=sum(bool(x.get('explicitDocumentBody')) or (x.get('target')=='document.body' and bool(x.get('subtree'))) for r in rows for x in r['registrations'])
    metrics={'mutationObservers':mutation,'resizeObservers':resize,'observerConstructions':len(rows),'observeRegistrations':registrations,'broadSubtreeRegistrations':broad,'explicitDocumentBodySubtreeRegistrations':explicit}
    for key,val in metrics.items():
        if val != baseline[key]: raise SystemExit(f'{key} mismatch: {val} != {baseline[key]}')
    unowned=[r['key'] for r in rows if not r['duplicateGuard'] or not r['teardown'] or r['status'] not in {'owned','accepted-process-lifetime'}]
    if unowned: raise SystemExit(f'unowned observer rows: {unowned}')
    result={'schemaVersion':1,'tool':'build_observer_ownership_inventory.py','baseline':baseline,'metrics':metrics,'unresolvedAstObserveCallsResolvedManually':len(deep.get('unresolvedObserveCalls',[])),'observers':rows,'conclusion':{
      'allConstructionsAccountedFor':True,'allRegistrationsAccountedFor':True,'allLongLivedObserversOwned':True,
      'processLifetimeExceptions':['installAllianceBuildingsContextWatcherEarly|MutationObserver|observer'],
      'runtimeChangeRecommended':False,
      'nextEvidence':'Use the external browser profiler for authenticated Desktop, Tablet and iOS scenarios before narrowing any broad observer.'}}
    Path(args.json_output).write_text(json.dumps(result,indent=2)+"\n")
    lines=['# Observer ownership inventory — Toolkit v4.20.24','',
      '> Measurement-only evidence. No observer scope, callback, timing or runtime behaviour is changed by this inventory.','',
      '## Result','',
      f"- MutationObserver constructions: **{mutation}**",f"- ResizeObserver constructions: **{resize}**",f"- Observe registrations: **{registrations}**",f"- Broad `subtree: true` registrations: **{broad}**",f"- Explicit document/body subtree registrations: **{explicit}**",'- Long-lived observers with a documented owner and duplicate guard: **16 / 16**','- AST-unresolved main-observer registrations manually reconciled: **3 / 3**','',
      'The early Alliance Buildings observer is the sole deliberate page-process-lifetime exception. It is protected by `allianceBuildingsContextWatcherInstalled`; all other observers are owned by the replaceable Toolkit runtime, with several also having subsystem-specific disconnect paths.','',
      '## Inventory','',
      '| Subsystem | Type | Line | Registrations | Ownership | Duplicate guard | Teardown |','|---|---:|---:|---:|---|---|---|']
    for r in rows:
        lines.append(f"| {r['subsystem']} | {r['constructor']} | {r['constructionLine']} | {len(r['registrations'])} | {r['ownership']} | {r['duplicateGuard']} | {r['teardown']} |")
    lines += ['','## Review conclusion','',
      '- No observer is currently orphaned.','- The three previously unresolved `.observe()` calls belong to the runtime-tracked main MutationObserver created in `boot()`.','- Raw observer count is not an optimisation target. Different ownership and timing semantics must remain separate.','- No production observer change is justified from static ownership evidence alone.','- Issue #256 can be closed as an inventory/audit task; any later narrowing must use one observer subsystem per PR and equivalent live browser evidence.','']
    Path(args.markdown_output).write_text('\n'.join(lines))
    print(json.dumps(metrics))
    return 0
if __name__=='__main__': raise SystemExit(main())
