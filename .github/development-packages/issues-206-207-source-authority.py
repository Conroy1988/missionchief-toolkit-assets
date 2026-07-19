#!/usr/bin/env python3
from __future__ import annotations

import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
SOURCE = ROOT / "src" / "MissionChief_Map_Command_Toolkit.user.js"
DIST_USER = ROOT / "dist" / "MissionChief_Map_Command_Toolkit.user.js"
DIST_TEXT = ROOT / "dist" / "MissionChief_Map_Command_Toolkit.txt"
s = SOURCE.read_text(encoding='utf-8')

def one(old,new,label):
 global s
 c=s.count(old)
 if c!=1: raise Exception(f'{label} count {c}')
 s=s.replace(old,new,1)

def compact_js(value):
 return re.sub(r'\s*\n\s*', ' ', value.strip())

def fn(name,next_name,new):
 global s
 a=s.index('    function '+name)
 b=s.index('    function '+next_name,a)
 s=s[:a]+compact_js(new)+"\n\n"+s[b:]

fn('missionRequirementsCatalogueDescriptor','missionRequirementsCatalogueRequirement',r'''    function missionRequirementsCatalogueDescriptor(candidate) {
        const context = missionRequirementsPatientContext(candidate);
        const scopes = Array.from(new Set([candidate?.root, candidate?.mount, context.activeWindow, context.doc].filter(scope => scope?.querySelectorAll)));
        const links = [];
        const seen = new Set();
        for (const scope of scopes) {
            for (const link of Array.from(scope.querySelectorAll?.('a[href*="/einsaetze/"]') || [])) {
                if (seen.has(link)) continue;
                seen.add(link);
                links.push(link);
            }
        }
        links.sort((left, right) => Number(/Requirements\s+for\s+this\s+Mission/iu.test(missionRequirementsElementText(right))) - Number(/Requirements\s+for\s+this\s+Mission/iu.test(missionRequirementsElementText(left))));
        const doc = candidate?.root?.ownerDocument || candidate?.mount?.ownerDocument || context.doc;
        const location = doc?.defaultView?.location || pageWindow.location || {};
        const origin = location.origin || `${location.protocol || 'https:'}//${location.host || 'www.missionchief.co.uk'}`;
        let matched = null;
        for (const link of links) {
            const href = String(link.getAttribute?.('href') || link.href || '');
            let parsed;
            try { parsed = new URL(href, origin); } catch (err) { continue; }
            const match = parsed.pathname.match(/^\/einsaetze\/(\d+)\/?$/iu);
            if (!match) continue;
            const parameters = new URLSearchParams();
            for (const name of ['overlay_index', 'additive_overlays']) {
                for (const value of parsed.searchParams.getAll(name)) if (value !== '') parameters.append(name, value);
            }
            const query = parameters.toString();
            matched = { id: Number(match[1]), overlayIndex: missionRequirementsOptionalNumber(parsed.searchParams.get('overlay_index')), additiveOverlays: parsed.searchParams.getAll('additive_overlays'), path: `${parsed.pathname}${query ? `?${query}` : ''}` };
            break;
        }
        if (!matched) {
            const id = missionRequirementsMissionTypeId(candidate);
            if (id === null || id === undefined || !Number.isFinite(Number(id)) || Number(id) < 0) return null;
            matched = { id: Number(id), overlayIndex: null, additiveOverlays: [], path: `/einsaetze/${Number(id)}` };
        }
        return { ...matched, origin, url: `${origin}${matched.path}`, key: `${origin}${matched.path}` };
    }''')

anchor='''    function missionRequirementsCatalogueParseDocument(doc, descriptor = {}) {'''
cat_helpers=compact_js(r'''    function missionRequirementsCataloguePersonnelRequirements(label, value) {
        const rawLabel = missionRequirementsCatalogueText({ textContent: label });
        if (!/^Required\s+Personnel(?:\s+Available)?$/iu.test(rawLabel)) return { recognized: false, requirements: [], unresolved: [] };
        const text = missionRequirementsCatalogueText({ textContent: value }).replace(/\s*(?:\+|\/|\band\b)\s*(?=\d+\s*x?\s*[A-Za-z])/giu, '; ');
        const parsed = missionRequirementsParseText(text, 'staff');
        return { recognized: true, requirements: parsed.requirements.map(requirement => ({ ...requirement, baseline: requirement.missing, baselineText: requirement.missing.toLocaleString('en-GB'), probability: 100, catalogueLabel: rawLabel, catalogueValue: value, catalogueKnown: true })), unresolved: parsed.remaining ? [{ label: rawLabel, value: parsed.remaining, group: 'staff' }] : [] };
    }

    function missionRequirementsCatalogueMergeRequirement(target, requirement) {
        if (!requirement) return;
        const existing = target.find(item => item.key === requirement.key);
        if (!existing) { target.push(requirement); return; }
        const baseline = Math.max(missionRequirementsOptionalNumber(existing.baseline ?? existing.missing) ?? 0, missionRequirementsOptionalNumber(requirement.baseline ?? requirement.missing) ?? 0);
        existing.missing = baseline;
        existing.baseline = baseline;
        existing.baselineText = baseline.toLocaleString('en-GB');
        existing.catalogueKnown = existing.catalogueKnown !== false && requirement.catalogueKnown !== false;
    }

''')+'\n\n'+anchor
one(anchor,cat_helpers,'catalogue helpers')

fn('missionRequirementsCatalogueParseDocument','missionRequirementsCataloguePrune',r'''    function missionRequirementsCatalogueParseDocument(doc, descriptor = {}) {
        if (!doc?.querySelectorAll) throw new Error('catalogue document unavailable');
        const requirements = [];
        const unresolved = [];
        const preconditions = {};
        const other = {};
        let sawAuthoritativeRequirement = false;
        const tables = Array.from(doc.querySelectorAll('table') || []);
        for (const table of tables) {
            const tableText = missionRequirementsCatalogueText(table);
            let kind = /Vehicle\s+and\s+Personnel\s+Requirements/iu.test(tableText) ? 'requirements'
                : /Reward\s+and\s+Precondition/iu.test(tableText) ? 'preconditions'
                    : /Other\s+information/iu.test(tableText) ? 'other' : null;
            if (kind === 'requirements') sawAuthoritativeRequirement = true;
            const rows = Array.from(table.querySelectorAll?.('tr') || []);
            for (const row of rows) {
                const cells = Array.from(row.querySelectorAll?.('th, td') || []);
                if (cells.length < 2) continue;
                const label = missionRequirementsCatalogueText(cells[0]);
                const value = missionRequirementsCatalogueText(cells[1]);
                if (!label || /^(?:Value|Vehicle\s+and\s+Personnel\s+Requirements|Reward\s+and\s+Precondition|Other\s+information)$/iu.test(label)) continue;
                const personnel = missionRequirementsCataloguePersonnelRequirements(label, value);
                if (personnel.recognized) {
                    sawAuthoritativeRequirement = true;
                    personnel.requirements.forEach(requirement => missionRequirementsCatalogueMergeRequirement(requirements, requirement));
                    unresolved.push(...personnel.unresolved);
                    if (kind === 'preconditions') preconditions[label] = value;
                    else if (kind === 'other') other[label] = value;
                    continue;
                }
                if (!kind && /^(?:Required|Requirement\s+of|Needed)\b/iu.test(label)) kind = 'requirements';
                if (kind === 'requirements') {
                    sawAuthoritativeRequirement = true;
                    const parsed = missionRequirementsCatalogueRequirement(label, value);
                    if (parsed) missionRequirementsCatalogueMergeRequirement(requirements, parsed);
                    else unresolved.push({ label, value });
                } else if (kind === 'preconditions') preconditions[label] = value;
                else if (kind === 'other') other[label] = value;
            }
        }
        if (sawAuthoritativeRequirement && !requirements.length && !unresolved.length) unresolved.push({ label: 'Requirements for this Mission', value: 'No quantified vehicle or trained-personnel requirements could be parsed.' });
        const titleNode = doc.querySelector?.('h1, [data-mission-title], .mission-title');
        const title = missionRequirementsSafeDiagnostic(missionRequirementsCatalogueText(titleNode), 140) || `Mission ${descriptor.id ?? 'Unknown'}`;
        const variationLinks = Array.from(doc.querySelectorAll('a[href*="/einsaetze/"]') || []);
        const seenVariations = new Set();
        const variations = [];
        for (const link of variationLinks) {
            const href = String(link.getAttribute?.('href') || link.href || '');
            if (!/\/einsaetze\/\d+/u.test(href) || seenVariations.has(href)) continue;
            seenVariations.add(href);
            variations.push({ href: missionRequirementsSafeDiagnostic(href, 180), title: missionRequirementsSafeDiagnostic(missionRequirementsCatalogueText(link), 140) });
        }
        const findValue = (source, pattern) => {
            const entry = Object.entries(source).find(([key]) => pattern.test(key));
            return entry ? entry[1] : '';
        };
        return {
            id: descriptor.id ?? null,
            overlayIndex: descriptor.overlayIndex ?? null,
            additiveOverlays: Array.from(descriptor.additiveOverlays || []),
            path: descriptor.path || '',
            url: descriptor.url || '',
            title,
            requirements,
            unresolved,
            preconditions,
            other,
            averageCredits: missionRequirementsOptionalNumber(findValue(preconditions, /Average\s+credits/iu)),
            maxPatients: missionRequirementsOptionalNumber(findValue(other, /Max\.?\s*Patients/iu)),
            patientTransportProbability: missionRequirementsOptionalNumber(findValue(other, /Probability.*transport/iu)),
            variations,
            fetchedAt: Date.now(),
            stale: false
        };
    }''')

one("if (!reconciled.requirements.length) return false; if (record.source.getAttribute?.('data-mcms-requirements-anchor') !== '1')", "if (!reconciled.requirements.length && !reconciled.unresolved.length) return false; if (record.source.getAttribute?.('data-mcms-requirements-anchor') !== '1')",'presentLive unresolved')
old="const reconciled = reconcile(parsed); if (!reconciled.requirements.length) { if (presentCatalogue(reconciled.unresolved.length ? 'live requirement text unparseable; official catalogue baseline shown' : 'no quantified live requirements; official catalogue baseline shown')) return; missionRequirementsRestoreSource(record.source); missionRequirementsPresent(record, missionRequirementsFallbackHtml(record.catalogueState === 'loading' ? 'loading' : 'error'), reconciled.unresolved.length ? 'requirement text unparseable' : 'no quantified requirements detected'); return; }"
new="const reconciled = reconcile(parsed); if (!reconciled.requirements.length) { if (reconciled.unresolved.length) { missionRequirementsRestoreSource(record.source); missionRequirementsPresent(record, missionRequirementsPanelHtml([], reconciled.unresolved), 'authoritative or live requirements unresolved'); return; } if (presentCatalogue('no quantified live requirements; official catalogue baseline shown')) return; missionRequirementsRestoreSource(record.source); missionRequirementsPresent(record, missionRequirementsFallbackHtml(record.catalogueState === 'loading' ? 'loading' : 'error'), 'no quantified requirements detected'); return; }"
one(old,new,'final unresolved')

SOURCE.write_text(s, encoding="utf-8")
DIST_USER.write_text(s, encoding="utf-8")
DIST_TEXT.write_text(s, encoding="utf-8")
print("Applied v4.20.3 authoritative Matrix source patch")
