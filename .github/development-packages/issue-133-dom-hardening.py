#!/usr/bin/env python3
from __future__ import annotations

import subprocess
import sys
from pathlib import Path

ROOT = Path.cwd()
SOURCE = ROOT / "src" / "MissionChief_Map_Command_Toolkit.user.js"
VALIDATOR = ROOT / ".github" / "scripts" / "validate_userscript.py"
INSPECTION = ROOT / "docs" / "issue-133-hardening-inspection.md"


def replace_region(text: str, start_token: str, end_token: str, replacement: str, label: str) -> str:
    start = text.find(start_token)
    end = text.find(end_token, start + len(start_token))
    if start < 0 or end < 0 or end <= start:
        raise SystemExit(f"{label}: unable to resolve region start={start} end={end}")
    return text[:start] + replacement.rstrip() + "\n\n    " + text[end:]


def replace_once(text: str, old: str, new: str, label: str) -> str:
    count = text.count(old)
    if count != 1:
        raise SystemExit(f"{label}: expected one anchor, found {count}")
    return text.replace(old, new, 1)


source = SOURCE.read_text(encoding="utf-8")

source = replace_region(
    source,
    "function missionRequirementsParseText(",
    "function missionRequirementsParseSource(",
    r'''function missionRequirementsParseText(rawText, group = 'vehicles') {
        let remaining = String(rawText || '')
            .replace(/\r\n?/gu, '\n')
            .replace(/\n+/gu, '; ')
            .replace(/\s+/gu, ' ')
            .trim();
        const requirements = [];
        const definitions = MISSION_REQUIREMENT_DEFINITIONS
            .filter(definition => definition.group === group)
            .sort((left, right) => Math.max(...right.aliases.map(alias => alias.length), 0) - Math.max(...left.aliases.map(alias => alias.length), 0));
        for (const definition of definitions) {
            const found = missionRequirementsFindDefinitionMatch(remaining, definition);
            if (!found || found.missing <= 0) continue;
            requirements.push({
                key: definition.key,
                requirement: definition.label || found.label,
                missing: found.missing,
                group,
                definition
            });
            remaining = remaining.replace(found.match, ' ');
        }
        return { requirements, remaining: missionRequirementsCleanRemaining(remaining) };
    }''',
    "line-aware requirement parser",
)

source = replace_region(
    source,
    "function missionRequirementsParseSource(",
    "function missionRequirementsVehicleType(",
    r'''function missionRequirementsElementText(element) {
        if (!element) return '';
        const rendered = typeof element.innerText === 'string' && element.innerText.trim()
            ? element.innerText
            : element.textContent;
        return String(rendered || '').replace(/\u00a0/gu, ' ').trim();
    }

    function missionRequirementsParseSource(source) {
        if (!source) return { requirements: [], unresolved: [] };
        const requirements = [];
        const unresolved = [];
        const allGroups = Array.from(source.querySelectorAll?.('[data-requirement-type]') || []);
        const groupElements = allGroups.filter(element => !allGroups.some(other => other !== element && other.contains?.(element)));
        const parseGroupElement = element => {
            const rawType = String(element.getAttribute('data-requirement-type') || 'vehicles').toLowerCase();
            const group = rawType === 'personnel' || rawType === 'staff' ? 'staff' : rawType === 'other' ? 'other' : 'vehicles';
            const heading = String(element.querySelector?.('b')?.textContent || '').trim();
            const raw = missionRequirementsElementText(element).replace(heading, ' ').trim();
            const parsed = missionRequirementsParseText(raw, group);
            requirements.push(...parsed.requirements);
            if (parsed.remaining) unresolved.push({ group, text: parsed.remaining });
        };
        if (groupElements.length) groupElements.forEach(parseGroupElement);
        else {
            const raw = missionRequirementsElementText(source);
            const parsed = missionRequirementsParseText(raw, 'vehicles');
            requirements.push(...parsed.requirements);
            if (parsed.remaining) unresolved.push({ group: 'vehicles', text: parsed.remaining });
        }
        return { requirements, unresolved };
    }''',
    "rendered DOM requirement parser",
)

source = replace_region(
    source,
    "function missionRequirementsVehicleId(",
    "function missionRequirementsEquipmentTypes(",
    r'''function missionRequirementsVehicleId(element) {
        const scopes = Array.from(new Set([element, element?.closest?.('tr')].filter(Boolean)));
        const attributes = ['vehicle_id', 'data-vehicle-id', 'data-vehicle_id'];
        for (const scope of scopes) {
            for (const raw of [scope?.value, scope?.getAttribute?.('value'), scope?.dataset?.vehicleId, scope?.dataset?.vehicle_id]) {
                const value = Number.parseInt(raw, 10);
                if (Number.isFinite(value) && value >= 0) return value;
            }
            for (const attribute of attributes) {
                const value = Number.parseInt(scope?.getAttribute?.(attribute), 10);
                if (Number.isFinite(value) && value >= 0) return value;
            }
            const idMatch = String(scope?.id || '').match(/(?:^|[_-])vehicle[_-]?(\d+)(?:$|[_-])/iu);
            if (idMatch) return Number(idMatch[1]);
            const link = scope?.matches?.('a[href*="/vehicles/"]') ? scope : scope?.querySelector?.('a[href*="/vehicles/"]');
            const hrefMatch = String(link?.getAttribute?.('href') || link?.href || '').match(/\/vehicles\/(\d+)(?:\/|$)/u);
            if (hrefMatch) return Number(hrefMatch[1]);
        }
        return -1;
    }''',
    "stable vehicle identity extraction",
)

source = replace_region(
    source,
    "function missionRequirementsEquipmentTypes(",
    "function missionRequirementsStaffCapacity(",
    r'''function missionRequirementsEquipmentTypes(element) {
        const values = new Set();
        const add = raw => String(raw || '').split(',').map(value => value.trim().toLowerCase()).filter(Boolean).forEach(value => values.add(value));
        const scopes = Array.from(new Set([element, element?.closest?.('tr')].filter(Boolean)));
        for (const scope of scopes) {
            add(scope?.dataset?.equipmentType);
            add(scope?.dataset?.equipmentTypes);
            add(scope?.getAttribute?.('data-equipment-type'));
            add(scope?.getAttribute?.('data-equipment-types'));
            scope?.querySelectorAll?.('[data-equipment-type], [data-equipment-types]').forEach(node => {
                add(node.getAttribute('data-equipment-type'));
                add(node.getAttribute('data-equipment-types'));
            });
        }
        return values;
    }''',
    "row-owned equipment metadata",
)

source = replace_region(
    source,
    "function missionRequirementsLssmActive(",
    "function missionRequirementsSourceForCandidate(",
    r'''function missionRequirementsLssmActive(candidate, source) {
        if (!source) return false;
        try {
            if (source.matches?.('.alert-missing-vehicles')) return true;
            if (source.querySelector?.('.alert-missing-vehicles')) return true;
            return Boolean(candidate?.root?.querySelector?.('.alert-missing-vehicles[data-raw-html], .alert-missing-vehicles table, .alert-missing-vehicles .table'));
        } catch (err) {
            return false;
        }
    }''',
    "precise LSSM coexistence detection",
)

source = replace_region(
    source,
    "function missionRequirementsHideSource(",
    "function missionRequirementsPanelHtml(",
    r'''function missionRequirementsHideSource(source) {
        if (!source || source.dataset.mcmsRequirementsSourceHidden === '1') return;
        source.dataset.mcmsRequirementsSourceHidden = '1';
    }

    function missionRequirementsRestoreSource(source) {
        if (!source || source.dataset.mcmsRequirementsSourceHidden !== '1') return;
        delete source.dataset.mcmsRequirementsSourceHidden;
    }''',
    "CSS-owned source visibility",
)

source = replace_once(
    source,
    '            #${SCRIPT.missionRequirementsPanelId}[data-state="danger"]{--mcms-req-state:#ef5350}',
    '            [data-mcms-requirements-source-hidden="1"]{display:none!important}\n            #${SCRIPT.missionRequirementsPanelId}[data-state="danger"]{--mcms-req-state:#ef5350}',
    "source visibility CSS",
)

source = replace_once(
    source,
    '<th scope="col">Requirement</th><th scope="col">Missing</th><th scope="col">En route</th><th scope="col">Still needed</th><th scope="col">Selected</th>',
    '<th scope="col">Requirement</th><th scope="col">Missing on mission</th><th scope="col">En-route</th><th scope="col">Still needed</th><th scope="col">Selected</th>',
    "explicit requirement table headers",
)
source = source.replace('data-label="Missing"', 'data-label="Missing on mission"').replace('data-label="En route"', 'data-label="En-route"')

source = replace_once(
    source,
    "        const doc = source.ownerDocument || document;\n        ensureMissionRequirementsDocumentStyle(doc);\n        const panel = doc.createElement('section');",
    "        const doc = source.ownerDocument || document;\n        for (const [otherSource, otherRecord] of Array.from(missionRequirementsRecords.entries())) {\n            if (otherSource !== source && otherRecord?.source?.ownerDocument === doc) missionRequirementsRemoveRecord(otherSource);\n        }\n        ensureMissionRequirementsDocumentStyle(doc);\n        const panel = doc.createElement('section');",
    "one requirements panel per document",
)

source = replace_region(
    source,
    "function scanMissionRequirementsWindows(",
    "function missionRequirementsScheduleDocumentRecords(",
    r'''function scanMissionRequirementsWindows() {
        if (!state.missionRequirements) {
            clearMissionRequirementsPanels();
            return;
        }
        const activeSources = new Set();
        const activeDocuments = new WeakSet();
        for (const candidate of missionValueWindowCandidates()) {
            const source = missionRequirementsSourceForCandidate(candidate);
            if (!source || !source.isConnected) continue;
            const doc = source.ownerDocument || document;
            if (activeDocuments.has(doc)) continue;
            if (missionRequirementsLssmActive(candidate, source)) {
                missionRequirementsRemoveRecord(source);
                activeDocuments.add(doc);
                continue;
            }
            const raw = missionRequirementsElementText(source);
            if (!raw) {
                missionRequirementsRemoveRecord(source);
                continue;
            }
            activeDocuments.add(doc);
            activeSources.add(source);
            missionRequirementsEnsureRecord(candidate, source);
        }
        for (const source of Array.from(missionRequirementsRecords.keys())) {
            if (!activeSources.has(source) || !source.isConnected) missionRequirementsRemoveRecord(source);
        }
    }''',
    "retained-lightbox deduplication",
)

source = replace_once(
    source,
    "    function updateUI() {\n        applyRootAttributes();",
    "    function updateUI() {\n        applyRootAttributes();\n        if (state.missionRequirements) scheduleMissionRequirementsScan(0);",
    "theme and UI resynchronisation",
)

SOURCE.write_text(source, encoding="utf-8")
if INSPECTION.exists():
    INSPECTION.unlink()

validation = subprocess.run([sys.executable, str(VALIDATOR)], cwd=ROOT)
if validation.returncode != 0:
    raise SystemExit(validation.returncode)
subprocess.run(["node", "--check", str(SOURCE)], cwd=ROOT, check=True)
print("Applied Issue #133 DOM, coexistence and lifecycle hardening")
