#!/usr/bin/env python3
from __future__ import annotations
import hashlib
import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
SOURCE = ROOT / 'src/MissionChief_Map_Command_Toolkit.user.js'
CHANGELOG = ROOT / 'CHANGELOG.md'
VALIDATOR = ROOT / '.github/scripts/validate_userscript.py'
FIXTURE = ROOT / '.github/fixtures/main-style-source-headroom.json'
TEST = ROOT / '.github/scripts/test_issue458_requirements_source_runtime.js'
text = SOURCE.read_text(encoding='utf-8')
if '// @version      5.0.4' not in text or "version: '5.0.4'," not in text or not TEST.exists():
    raise SystemExit('Issue #458 package requires the exact v5.0.4 source and reviewed runtime fixture')
text = text.replace('// @version      5.0.4', '// @version      5.0.5', 1).replace("version: '5.0.4',", "version: '5.0.5',", 1)

resolver = r'''    function operationalRequirementsCandidateVisible(node) {
        if (!node?.isConnected || node.hidden || node.getAttribute?.('aria-hidden') === 'true') return false;
        try {
            const style = node.ownerDocument?.defaultView?.getComputedStyle?.(node);
            if (style?.display === 'none' || style?.visibility === 'hidden' || style?.visibility === 'collapse') return false;
            const rect = node.getBoundingClientRect?.();
            if (rect && Number.isFinite(rect.width) && Number.isFinite(rect.height)) return rect.width > 1 || rect.height > 1;
            if (node.getClientRects?.().length) return true;
        } catch (error) {}
        return true;
    }

    function operationalRequirementsMissionContainer(node, doc = node?.ownerDocument) {
        return node?.closest?.('#mission-form, [data-mission-id], .mission-window, .mission_window, .modal-content')
            || doc?.querySelector?.('#mission-form, [data-mission-id], .mission-window, .mission_window, .modal-content')
            || null;
    }

    function operationalRequirementsRawHtmlRoot(doc, carrier) {
        const rawHtml = String(carrier?.getAttribute?.('data-raw-html') || '').trim();
        if (!rawHtml || !doc?.createElement) return null;
        const holder = doc.createElement('div');
        holder.setAttribute('data-mcms-requirement-source', 'lssm-raw');
        holder.innerHTML = rawHtml;
        return holder.querySelector?.('[data-requirement-type]') ? holder : null;
    }

    function operationalRequirementsCandidateRecord(root, anchor, kind, index) {
        if (!root || !anchor || root.closest?.('[data-mcms-operational-suite="requirements"]')) return null;
        const grouped = Array.from(root.querySelectorAll?.('[data-requirement-type]') || []);
        const raw = operationalRequirementNormaliseText(root.textContent || '');
        const missionContainer = operationalRequirementsMissionContainer(anchor);
        const missionVisible = operationalRequirementsCandidateVisible(missionContainer);
        const visible = operationalRequirementsCandidateVisible(anchor);
        const score = grouped.length * 300 + (raw ? 100 : 0) + (missionVisible ? 400 : 0)
            + (visible ? 60 : 0) + (anchor.id === 'missing_text' ? 20 : 0) + (kind === 'lssm-raw' ? 10 : 0);
        return { root, anchor, kind, index, groupedCount: grouped.length, raw, visible, missionContainer, score,
            fingerprint: `${kind}:${index}:${grouped.length}:${raw}` };
    }

    function operationalRequirementsSourceCandidates(doc) {
        if (!doc?.querySelectorAll) return [];
        const candidates = [];
        const seenRoots = new Set();
        const nativeRoots = Array.from(doc.querySelectorAll('[id="missing_text"]') || []);
        const add = (root, anchor = root, kind = 'native') => {
            if (!root || !anchor || seenRoots.has(root)) return;
            const record = operationalRequirementsCandidateRecord(root, anchor, kind, candidates.length);
            if (!record) return;
            seenRoots.add(root);
            candidates.push(record);
        };
        nativeRoots.forEach(root => add(root, root, 'native'));
        for (const group of Array.from(doc.querySelectorAll('[data-requirement-type]') || [])) {
            const root = group.closest?.('[id="missing_text"], .alert-missing-vehicles') || group.parentElement;
            add(root, root, 'grouped');
        }
        for (const carrier of Array.from(doc.querySelectorAll('.alert-missing-vehicles[data-raw-html]') || [])) {
            if (carrier.closest?.('[data-mcms-operational-suite="requirements"]')) continue;
            const rawHtml = String(carrier.getAttribute?.('data-raw-html') || '').trim();
            if (!rawHtml) continue;
            if (operationalRequirementsCandidateVisible(carrier)) {
                candidates.push({ root: carrier, anchor: carrier, kind: 'lssm-live', index: candidates.length,
                    groupedCount: 0, raw: rawHtml, visible: true,
                    missionContainer: operationalRequirementsMissionContainer(carrier), score: Number.POSITIVE_INFINITY,
                    fingerprint: `lssm-live:${rawHtml}`, suppressesToolkit: true });
                continue;
            }
            const root = operationalRequirementsRawHtmlRoot(doc, carrier);
            const preferredAnchor = nativeRoots.find(node => node?.isConnected && node?.parentNode) || carrier;
            add(root, preferredAnchor, 'lssm-raw');
        }
        return candidates;
    }

    function operationalRequirementsResolveSource(doc) {
        const candidates = operationalRequirementsSourceCandidates(doc);
        const activeLssm = candidates.find(candidate => candidate.suppressesToolkit === true);
        if (activeLssm) return { ...activeLssm, suppressed: true, candidates };
        const evidenced = candidates.filter(candidate => candidate.groupedCount > 0 || candidate.raw);
        const pool = evidenced.length ? evidenced : candidates;
        const selected = pool.slice().sort((left, right) => right.score - left.score || right.index - left.index)[0] || null;
        return selected ? { ...selected, suppressed: false, candidates } : null;
    }

    function operationalRequirementsEquivalentLssmActive(doc) {
        return operationalRequirementsResolveSource(doc)?.suppressed === true;
    }

'''
pattern = re.compile(r"    function operationalRequirementsEquivalentLssmActive\(doc\) \{.*?\n    \}\n\n    function operationalRequirementsRuntimeCatalog\(\)", re.S)
text, count = pattern.subn(resolver + '    function operationalRequirementsRuntimeCatalog()', text, count=1)
if count != 1:
    raise SystemExit('Unable to replace the v5.0.4 requirement source selector')

old = """            const raw = operationalRequirementNormaliseText(element.textContent || '');
            if (!raw) continue;
            texts[group] = texts[group]
                ? { raw: `${texts[group].raw}, ${raw}`, infoText: texts[group].infoText || '' }
                : { raw, infoText: operationalRequirementNormaliseText(element.getAttribute('data-info-text') || '') };"""
new = """            const infoText = operationalRequirementNormaliseText(
                element.querySelector?.('b')?.textContent || element.getAttribute('data-info-text') || ''
            );
            const fullText = operationalRequirementNormaliseText(element.textContent || '');
            const raw = operationalRequirementNormaliseText(
                infoText && fullText.startsWith(infoText) ? fullText.slice(infoText.length) : fullText
            );
            if (!raw) continue;
            texts[group] = texts[group]
                ? { raw: `${texts[group].raw}, ${raw}`, infoText: texts[group].infoText || infoText }
                : { raw, infoText };"""
if old not in text:
    raise SystemExit('Unable to locate native MissionChief requirement parsing')
text = text.replace(old, new, 1)

old = """        const requirementRoot = context.doc.querySelector?.('#missing_text');
        if (!requirementRoot?.isConnected || operationalRequirementsEquivalentLssmActive(context.doc)) {
            context.panel?.remove?.();
            context.panel = null;
            context.fingerprint = '';
            return;
        }
        const settings = state.operationalWindow?.requirements || {};
        const model = operationalRequirementCreateModel(operationalRequirementsInput(context, requirementRoot));"""
new = """        const requirementSource = operationalRequirementsResolveSource(context.doc);
        const requirementRoot = requirementSource?.root;
        if (!requirementRoot || requirementSource?.suppressed === true) {
            context.panel?.remove?.();
            context.panel = null;
            context.fingerprint = '';
            return;
        }
        const settings = state.operationalWindow?.requirements || {};
        const model = operationalRequirementCreateModel(operationalRequirementsInput(context, requirementRoot));"""
if old not in text:
    raise SystemExit('Unable to locate requirement renderer source binding')
text = text.replace(old, new, 1)
text = text.replace('''            minified: context.minified === true
        });''', '''            minified: context.minified === true,
            source: requirementSource.fingerprint
        });''', 1)
text = text.replace('        const panel = operationalRequirementsMount(context, requirementRoot);', '        const panel = operationalRequirementsMount(context, requirementSource.anchor || requirementRoot);', 1)

old = """        const requirementRoot = doc.querySelector('#missing_text');
        const roots = Array.from(new Set([
            requirementRoot,
            doc.querySelector('#mission_vehicle_driving'),
            doc.querySelector('#vehicle_show_table_body_all'),
            doc.querySelector('#occupied'),
            ...operationalFeatureObservationRoots(doc)
        ].filter(Boolean)));
        if (!roots.length) return;
        const rootFingerprint = roots.map(root => root).join('|');
        if (context.boundRequirementRoot === requirementRoot && context.observer && context.observedRootCount === roots.length) return;
        try { context.observer?.disconnect?.(); } catch (error) {}
        context.boundRequirementRoot = requirementRoot;
        context.observedRootCount = roots.length;"""
new = """        const requirementSource = operationalRequirementsResolveSource(doc);
        const requirementRoot = requirementSource?.root || null;
        const candidateAnchors = requirementSource?.candidates?.map(candidate => candidate.anchor) || [];
        const missionHost = requirementSource?.missionContainer
            || operationalRequirementsMissionContainer(requirementSource?.anchor, doc);
        const roots = Array.from(new Set([
            ...candidateAnchors,
            missionHost,
            doc.querySelector('#mission_vehicle_driving'),
            doc.querySelector('#vehicle_show_table_body_all'),
            doc.querySelector('#occupied'),
            ...operationalFeatureObservationRoots(doc)
        ].filter(root => root?.isConnected !== false)));
        if (!roots.length) return;
        const sourceFingerprint = requirementSource?.fingerprint || '';
        if (context.boundRequirementRoot === requirementSource?.anchor
            && context.boundRequirementSource === sourceFingerprint
            && context.observer
            && context.observedRootCount === roots.length) return;
        try { context.observer?.disconnect?.(); } catch (error) {}
        context.boundRequirementRoot = requirementSource?.anchor || null;
        context.boundRequirementSource = sourceFingerprint;
        context.observedRootCount = roots.length;"""
if old not in text:
    raise SystemExit('Unable to locate requirement observer source binding')
text = text.replace(old, new, 1)
anchor = '''            boundRequirementRoot: null,
            observedRootCount: 0,'''
if anchor not in text:
    raise SystemExit('Unable to locate operational context binding state')
text = text.replace(anchor, '''            boundRequirementRoot: null,
            boundRequirementSource: '',
            observedRootCount: 0,''', 1)
SOURCE.write_text(text, encoding='utf-8')
for target in (ROOT / 'MissionChief_Map_Command_Toolkit.user.js', ROOT / 'MissionChief_Map_Command_Toolkit.txt'):
    target.write_text(text, encoding='utf-8')

validator = VALIDATOR.read_text(encoding='utf-8')
constant = 'ISSUE456_REQUIREMENTS_TRUTH_RUNTIME = ROOT / ".github" / "scripts" / "test_issue456_requirements_truth_runtime.js"\n'
if constant not in validator:
    raise SystemExit('Issue #456 validator anchor is missing')
validator = validator.replace(constant, constant + 'ISSUE458_REQUIREMENTS_SOURCE_RUNTIME = ROOT / ".github" / "scripts" / "test_issue458_requirements_source_runtime.js"\n', 1)
validator = validator.replace('ISSUE456_REQUIREMENTS_TRUTH_RUNTIME]', 'ISSUE456_REQUIREMENTS_TRUTH_RUNTIME, ISSUE458_REQUIREMENTS_SOURCE_RUNTIME]', 1)
run_anchor = '''        if issue456_requirements_truth.returncode != 0:
            fail("Issue #456 requirements truth-state runtime failed")

'''
if run_anchor not in validator:
    raise SystemExit('Issue #456 validator execution anchor is missing')
validator = validator.replace(run_anchor, run_anchor + '''        issue458_requirements_source = subprocess.run(
            ["node", str(ISSUE458_REQUIREMENTS_SOURCE_RUNTIME)], cwd=ROOT,
        )
        if issue458_requirements_source.returncode != 0:
            fail("Issue #458 requirements source-discovery runtime failed")

''', 1)
VALIDATOR.write_text(validator, encoding='utf-8')

changelog = CHANGELOG.read_text(encoding='utf-8')
heading = '## [Unreleased]\n'
entry = '''## [5.0.5] - 2026-07-23

### Critical requirement-source discovery recovery
- Replaced first-match `#missing_text` binding with authoritative candidate discovery across active, duplicated, replaced and LSSM-transformed mission markup.
- Added active-mission and visibility scoring so retained empty or stale roots cannot trap the requirements panel in a permanent waiting state.
- Recovered requirement evidence from hidden LSSM `data-raw-html` carriers while continuing to suppress a genuinely visible equivalent LSSM panel.
- Removed native MissionChief requirement headings before parsing, matching the authorised LSSM parser contract.
- Rebound the operational observer whenever the authoritative source changes and added behavioural coverage for duplicate, stale, delayed, LSSM and Toolkit-owned roots.

'''
if heading not in changelog:
    raise SystemExit('CHANGELOG Unreleased heading is missing')
CHANGELOG.write_text(changelog.replace(heading, heading + '\n' + entry, 1), encoding='utf-8')

fixture = json.loads(FIXTURE.read_text(encoding='utf-8'))
source_lines = len(text.splitlines())
delta = source_lines - int(fixture['expectedSourceLines'])
if delta <= 0:
    raise SystemExit(f'Unexpected Issue #458 source-line delta: {delta}')
changes = [item for item in fixture['approvedNonStyleChanges'] if item.get('issue') != 458]
changes.append({'issue': 458, 'phase': 'authoritative-requirement-source-discovery', 'lines': delta})
fixture['approvedNonStyleChanges'] = changes
fixture['approvedNonStyleSourceLines'] = sum(int(item['lines']) for item in changes)
fixture['expectedSourceLines'] = int(fixture['candidateSourceLines']) + fixture['approvedNonStyleSourceLines'] - int(fixture['retiredNonStyleSourceLines'])
fixture['candidateVersion'] = '5.0.5'
fixture['candidateSourceSha256'] = hashlib.sha256(text.encode('utf-8')).hexdigest()
fixture['invariant'] = 'The reviewed compact stylesheet retains 504 recovered source lines while Operational Requirements selects and observes the authoritative active mission requirement source.'
if fixture['expectedSourceLines'] != source_lines:
    raise SystemExit('Issue #458 source-headroom ledger does not reconcile')
FIXTURE.write_text(json.dumps(fixture, indent=2) + '\n', encoding='utf-8')
print(json.dumps({'version':'5.0.5','sourceLines':source_lines,'issue458Lines':delta,'sha256':fixture['candidateSourceSha256']}, indent=2))
