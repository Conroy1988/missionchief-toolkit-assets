#!/usr/bin/env python3
from __future__ import annotations

import os
import re
import subprocess
import textwrap
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
SOURCE = ROOT / "src/MissionChief_Map_Command_Toolkit.user.js"
RUNTIME_TEST = ROOT / ".github/scripts/test_mission_requirements_runtime.js"
CONTRACT = ROOT / ".github/scripts/test_mission_requirements_contract.py"
CHANGELOG = ROOT / "CHANGELOG.md"
HELP = ROOT / "help/index.html"
DOC = ROOT / "docs/issue-230-probability-metadata.md"


def replace_once(text: str, old: str, new: str, label: str) -> str:
    count = text.count(old)
    if count != 1:
        raise RuntimeError(f"{label}: expected one match, found {count}")
    return text.replace(old, new, 1)


def function_span(source: str, name: str) -> tuple[int, int]:
    match = re.search(rf"\bfunction\s+{re.escape(name)}\s*\(", source)
    if not match:
        raise RuntimeError(f"missing function {name}")
    opening_paren = source.find("(", match.start())
    paren_depth = 0
    quote: str | None = None
    escaped = False
    body_open: int | None = None
    for index in range(opening_paren, len(source)):
        char = source[index]
        if quote:
            if escaped:
                escaped = False
            elif char == "\\":
                escaped = True
            elif char == quote:
                quote = None
            continue
        if char in ("'", '"', "`"):
            quote = char
            continue
        if char == "(":
            paren_depth += 1
        elif char == ")":
            paren_depth -= 1
            if paren_depth == 0:
                cursor = index + 1
                while cursor < len(source) and source[cursor].isspace():
                    cursor += 1
                if cursor >= len(source) or source[cursor] != "{":
                    raise RuntimeError(f"missing body opening for {name}")
                body_open = cursor
                break
    if body_open is None:
        raise RuntimeError(f"unable to locate body for {name}")
    depth = 0
    quote = None
    escaped = False
    for index in range(body_open, len(source)):
        char = source[index]
        if quote:
            if escaped:
                escaped = False
            elif char == "\\":
                escaped = True
            elif char == quote:
                quote = None
            continue
        if char in ("'", '"', "`"):
            quote = char
        elif char == "{":
            depth += 1
        elif char == "}":
            depth -= 1
            if depth == 0:
                return match.start(), index + 1
    raise RuntimeError(f"unterminated function {name}")


def replace_function(source: str, name: str, replacement: str) -> str:
    start, end = function_span(source, name)
    return source[:start] + textwrap.dedent(replacement).strip("\n") + source[end:]


HELPERS = r'''
    function missionRequirementsCatalogueCapability(label) {
        const cleaned = String(label || '')
        .replace(/^(?:required|requirement\s+of|needed)\s+/iu, '')
        .replace(/\s+/gu, ' ')
        .trim();
        if (!cleaned) return null;
        for (const group of ['vehicles', 'staff', 'other']) {
        const parsed = missionRequirementsParseText(`1 ${cleaned}`, group);
        if (parsed.requirements.length !== 1 || parsed.remaining) continue;
        const requirement = parsed.requirements[0];
        return { key: requirement.key, group, definition: requirement.definition, label: requirement.requirement };
        }
        return null;
    }

    function missionRequirementsCatalogueModifier(label, value = '', resolveCapability = true) {
        const rawLabel = missionRequirementsCatalogueText({ textContent: label });
        const rawValue = missionRequirementsCatalogueText({ textContent: value });
        const leadingProbability = rawLabel.match(/^\s*(\d+(?:\.\d+)?)\s*%?\s+(?=(?:Probability|Chance)\b)/iu);
        const normalizedLabel = leadingProbability ? rawLabel.slice(leadingProbability[0].length).trim() : rawLabel;
        const probabilityPatterns = [
        /^Probability\s+of\s+(.+?)\s+being\s+required\s*:?\s*$/iu,
        /^Probability\s+that\s+(.+?)\s+(?:is|are)\s+required\s*:?\s*$/iu,
        /^(.+?)\s+(?:requirement\s+)?(?:probability|chance)\s*:?\s*$/iu
        ];
        for (const pattern of probabilityPatterns) {
        const match = normalizedLabel.match(pattern);
        if (!match) continue;
        const numberMatch = `${rawValue} ${rawLabel}`.match(/(\d+(?:\.\d+)?)\s*%?/u);
        const probabilityValue = numberMatch ? Math.max(0, Math.min(100, Number(numberMatch[1]))) : null;
        const capability = resolveCapability ? missionRequirementsCatalogueCapability(match[1]) : null;
        return {
            recognized: true,
            classification: 'probability',
            key: capability?.key || null,
            group: capability?.group || null,
            resource: capability?.label || String(match[1] || '').trim(),
            probability: Number.isFinite(probabilityValue) ? probabilityValue : null,
            availabilityOnly: false,
            label: rawLabel,
            value: rawValue
        };
        }
        const availability = normalizedLabel.match(/^(.+?)\s+only\s+required\s*,?\s*when\s+available\s*:?\s*$/iu);
        if (availability) {
        const capability = resolveCapability ? missionRequirementsCatalogueCapability(availability[1]) : null;
        const enabled = /^(?:yes|true|1)$/iu.test(rawValue);
        return {
            recognized: true,
            classification: 'availability',
            key: capability?.key || null,
            group: capability?.group || null,
            resource: capability?.label || String(availability[1] || '').trim(),
            probability: null,
            availabilityOnly: enabled,
            label: rawLabel,
            value: rawValue
        };
        }
        if (/\b(?:probability|chance)\b/iu.test(normalizedLabel) || /^(?:yes|no|true|false)$/iu.test(rawValue)) {
        return { recognized: true, classification: 'informational', key: null, group: null, resource: '', probability: null, availabilityOnly: false, label: rawLabel, value: rawValue };
        }
        return { recognized: false, classification: null, key: null, group: null, resource: '', probability: null, availabilityOnly: false, label: rawLabel, value: rawValue };
    }

    function missionRequirementsStripNonDemandMetadata(rawText, resolveCapability = false) {
        const fragments = String(rawText || '').replace(/\r/gu, '').split(/\n+|\s*;\s*/u);
        const operational = [];
        for (const fragment of fragments) {
        const clean = String(fragment || '').trim();
        if (!clean) continue;
        const pair = clean.match(/^(.+?)\s*(?::|\||—)\s*(.+)$/u);
        const label = pair ? pair[1] : clean;
        const value = pair ? pair[2] : '';
        if (missionRequirementsCatalogueModifier(label, value, resolveCapability).recognized) continue;
        operational.push(clean);
        }
        return operational.join('; ');
    }
'''

PARSE_TEXT = r'''
    function missionRequirementsParseText(rawText, group = 'vehicles') {
        const normalized = missionRequirementsStripNonDemandMetadata(rawText, false)
        .replace(/\r/g, '')
        .replace(/\n+/g, '; ')
        .replace(/\s+/g, ' ')
        .trim();
        if (!normalized) return { requirements: [], remaining: '' };
        let working = normalized;
        const requirements = [];
        while (true) {
        let best = null;
        for (const definition of MISSION_REQUIREMENT_PARSE_DEFINITIONS) {
            if ((definition.group || 'vehicles') !== group) continue;
            const found = missionRequirementsFindDefinitionMatch(working, definition);
            if (!found) continue;
            if (!best || found.index < best.found.index || (found.index === best.found.index && found.length > best.found.length)) {
            best = { definition, found };
            }
        }
        if (!best) break;
        requirements.push({
            key: best.definition.key,
            requirement: best.definition.label,
            missing: best.found.missing,
            group,
            definition: best.definition,
            sourceIndex: best.found.index
        });
        working = `${working.slice(0, best.found.index)}${' '.repeat(best.found.length)}${working.slice(best.found.index + best.found.length)}`;
        }
        requirements.sort((a, b) => a.sourceIndex - b.sourceIndex);
        requirements.forEach(requirement => { delete requirement.sourceIndex; });
        return { requirements, remaining: missionRequirementsCleanRemaining(working) };
    }
'''

PARSE_SOURCE = r'''
    function missionRequirementsParseSource(source) {
        const requirements = [];
        const unresolved = [];
        const parseSection = (rawText, requestedGroup) => {
        const group = missionRequirementsNormalizeGroup(requestedGroup, missionRequirementsInferGroup(rawText, 'vehicles'));
        const cleaned = missionRequirementsStripGroupHeading(rawText);
        const operational = missionRequirementsStripNonDemandMetadata(cleaned, false);
        if (!operational) return;
        const parsed = missionRequirementsParseText(operational, group);
        requirements.push(...parsed.requirements);
        const generic = missionRequirementsParseGenericText(parsed.remaining, group);
        requirements.push(...generic.requirements);
        if (generic.remaining) unresolved.push({ group, text: generic.remaining });
        };

        const allGroups = Array.from(source?.querySelectorAll?.('[data-requirement-type]') || []);
        const groupElements = allGroups.filter(element => {
        const closest = element.closest?.('#missing_text');
        return !closest || closest === source;
        });
        if (groupElements.length) {
        for (const element of groupElements) {
            const rawGroup = element.getAttribute?.('data-requirement-type') || element.dataset?.requirementType || 'vehicles';
            parseSection(missionRequirementsElementText(element), rawGroup);
        }
        } else {
        const raw = missionRequirementsElementText(source);
        for (const section of missionRequirementsSplitTextSections(raw, 'vehicles')) parseSection(section.text, section.group);
        }
        return { requirements, unresolved };
    }
'''

GENERIC_TEXT = r'''
    function missionRequirementsParseGenericText(rawText, group) {
        let working = missionRequirementsStripNonDemandMetadata(rawText, false).replace(/\r/g, '').replace(/\n+/g, '; ').trim();
        if (!working) return { requirements: [], remaining: '' };
        const number = '(\\d{1,3}(?:[\\s,.]\\d{3})*|\\d+)';
        const patterns = [
        {
            expression: new RegExp(`(^|[,;]\\s*)\\s*(?:at\\s+least\\s+)?(?:x\\s*)?${number}\\s*(?:x\\s*)?\\s+([^,;]+?)(?=\\s*(?:[,;]|$))`, 'giu'),
            quantity: 2,
            label: 3
        },
        {
            expression: new RegExp(`(^|[,;]\\s*)\\s*([^,;:]+?)\\s*(?::|x)\\s*${number}(?=\\s*(?:[,;]|$))`, 'giu'),
            quantity: 3,
            label: 2
        }
        ];
        const requirements = [];
        let serial = 0;
        for (const pattern of patterns) {
        pattern.expression.lastIndex = 0;
        let match;
        while ((match = pattern.expression.exec(working))) {
            const missing = missionRequirementsNumber(match[pattern.quantity]);
            const label = String(match[pattern.label] || '')
            .replace(/^\s*(?:and\s+)?(?:missing|required)\s+/iu, '')
            .replace(/\s+/g, ' ')
            .trim();
            const sourceIndex = match.index;
            if (!missing || !label || missionRequirementsCatalogueModifier(label, String(missing), false).recognized) {
            working = `${working.slice(0, sourceIndex)}${' '.repeat(match[0].length)}${working.slice(sourceIndex + match[0].length)}`;
            pattern.expression.lastIndex = sourceIndex + match[0].length;
            continue;
            }
            const slug = label.toLowerCase().replace(/[^a-z0-9]+/g, '-').replace(/^-|-$/g, '').slice(0, 48) || 'requirement';
            requirements.push({
            key: `unmapped-${slug}-${serial++}`,
            requirement: label,
            missing,
            group,
            definition: { key: `unmapped-${slug}`, label, aliases: [label], group, types: [], equipment: [], factors: {}, countable: false, generic: true },
            sourceIndex
            });
            working = `${working.slice(0, sourceIndex)}${' '.repeat(match[0].length)}${working.slice(sourceIndex + match[0].length)}`;
            pattern.expression.lastIndex = sourceIndex + match[0].length;
        }
        }
        requirements.sort((a, b) => a.sourceIndex - b.sourceIndex);
        requirements.forEach(requirement => { delete requirement.sourceIndex; });
        return { requirements, remaining: missionRequirementsCleanRemaining(working) };
    }
'''

CATALOGUE_REQUIREMENT = r'''
    function missionRequirementsCatalogueRequirement(label, value) {
        const rawLabel = missionRequirementsCatalogueText({ textContent: label });
        const rawValue = missionRequirementsCatalogueText({ textContent: value });
        if (missionRequirementsCatalogueModifier(rawLabel, rawValue, true).recognized) return null;
        const quantityMatch = rawValue.match(/^\s*(\d+(?:[\s,.]\d{3})*)/u);
        const quantity = quantityMatch ? missionRequirementsNumber(quantityMatch[1]) : null;
        if (quantity === null) return null;
        const cleanedLabel = rawLabel
        .replace(/^(?:required|requirement\s+of|needed)\s+/iu, '')
        .replace(/\s*\([^)]*%[^)]*\)\s*$/u, '')
        .trim();
        if (!cleanedLabel) return null;
        const probabilityMatch = `${rawLabel} ${rawValue}`.match(/(\d+(?:\.\d+)?)\s*%/u);
        const probability = probabilityMatch ? Math.max(0, Math.min(100, Number(probabilityMatch[1]))) : 100;
        const sourceText = `${quantity} ${cleanedLabel}`;
        for (const group of ['vehicles', 'staff', 'other']) {
        const parsed = missionRequirementsParseText(sourceText, group);
        if (!parsed.requirements.length) continue;
        const requirement = parsed.requirements[0];
        return {
            ...requirement,
            missing: quantity,
            baseline: quantity,
            baselineText: `${quantity.toLocaleString('en-GB')}${probability < 100 ? ` (${probability}% chance)` : ''}`,
            probability,
            availabilityOnly: false,
            catalogueLabel: rawLabel,
            catalogueValue: rawValue,
            catalogueKnown: true
        };
        }
        const inferredGroup = missionRequirementsInferGroup(cleanedLabel, 'vehicles');
        const key = `catalogue-${cleanedLabel.toLowerCase().replace(/[^a-z0-9]+/gu, '-').replace(/^-|-$/gu, '').slice(0, 70) || 'unknown'}`;
        return {
        key,
        requirement: cleanedLabel,
        missing: quantity,
        baseline: quantity,
        baselineText: `${quantity.toLocaleString('en-GB')}${probability < 100 ? ` (${probability}% chance)` : ''}`,
        probability,
        availabilityOnly: false,
        group: inferredGroup,
        definition: { key, label: cleanedLabel, aliases: [cleanedLabel], group: inferredGroup, types: [], equipment: [], factors: {}, countable: false },
        catalogueLabel: rawLabel,
        catalogueValue: rawValue,
        catalogueKnown: false
        };
    }
'''

PARSE_CATALOGUE = r'''
    function missionRequirementsCatalogueParseDocument(doc, descriptor = {}) {
        if (!doc?.querySelectorAll) throw new Error('catalogue document unavailable');
        const requirements = [];
        const unresolved = [];
        const preconditions = {};
        const other = {};
        const metadata = [];
        const modifiersByKey = new Map();
        const records = [];
        let sawAuthoritativeRequirement = false;
        const tables = Array.from(doc.querySelectorAll('table') || []);
        for (const table of tables) {
        const tableText = missionRequirementsCatalogueText(table);
        let kind = /Vehicle\s+and\s+Personnel\s+Requirements/iu.test(tableText) ? 'requirements' : /Reward\s+and\s+Precondition/iu.test(tableText) ? 'preconditions' : /Other\s+information/iu.test(tableText) ? 'other' : null;
        const rows = Array.from(table.querySelectorAll?.('tr') || []);
        for (const row of rows) {
            const cells = Array.from(row.querySelectorAll?.('th, td') || []);
            if (cells.length < 2) continue;
            const label = missionRequirementsCatalogueText(cells[0]);
            const value = missionRequirementsCatalogueText(cells[1]);
            if (!label || /^(?:Value|Vehicle\s+and\s+Personnel\s+Requirements|Reward\s+and\s+Precondition|Other\s+information)$/iu.test(label)) continue;
            if (!kind && /^(?:Required|Requirement\s+of|Needed)\b/iu.test(label)) kind = 'requirements';
            records.push({ kind, label, value });
        }
        }
        for (const record of records) {
        const modifier = missionRequirementsCatalogueModifier(record.label, record.value, true);
        if (!modifier.recognized) continue;
        metadata.push({ ...modifier, kind: record.kind });
        if (record.kind === 'other') other[record.label] = record.value;
        if (!modifier.key) continue;
        const current = modifiersByKey.get(modifier.key) || { probability: null, availabilityOnly: false };
        if (modifier.classification === 'probability' && modifier.probability !== null) current.probability = modifier.probability;
        if (modifier.classification === 'availability' && modifier.availabilityOnly) current.availabilityOnly = true;
        modifiersByKey.set(modifier.key, current);
        }
        for (const record of records) {
        const { kind, label, value } = record;
        if (missionRequirementsCatalogueModifier(label, value, true).recognized) continue;
        const personnel = missionRequirementsCataloguePersonnelRequirements(label, value, kind);
        if (personnel.recognized) {
            if (personnel.classification === 'spawn-prerequisite') {
            if (kind === 'preconditions') preconditions[label] = value;
            continue;
            }
            sawAuthoritativeRequirement = true;
            personnel.requirements.forEach(requirement => missionRequirementsCatalogueMergeRequirement(requirements, requirement));
            unresolved.push(...personnel.unresolved);
            if (kind === 'other') other[label] = value;
            continue;
        }
        if (kind === 'requirements') {
            const parsed = missionRequirementsCatalogueRequirement(label, value);
            if (parsed) {
            sawAuthoritativeRequirement = true;
            const modifier = modifiersByKey.get(parsed.key);
            const probability = modifier?.probability ?? parsed.probability ?? 100;
            missionRequirementsCatalogueMergeRequirement(requirements, {
                ...parsed,
                probability,
                availabilityOnly: modifier?.availabilityOnly === true,
                baselineText: `${parsed.baseline.toLocaleString('en-GB')}${probability < 100 ? ` (${probability}% chance)` : ''}`
            });
            } else {
            sawAuthoritativeRequirement = true;
            unresolved.push({ label, value, classification: 'operational' });
            }
        } else if (kind === 'preconditions') preconditions[label] = value;
        else if (kind === 'other') other[label] = value;
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
        const findValue = (source, pattern) => { const entry = Object.entries(source).find(([key]) => pattern.test(key)); return entry ? entry[1] : ''; };
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
        metadata,
        averageCredits: missionRequirementsOptionalNumber(findValue(preconditions, /Average\s+credits/iu)),
        maxPatients: missionRequirementsOptionalNumber(findValue(other, /Max\.?\s*Patients/iu)),
        patientTransportProbability: missionRequirementsOptionalNumber(findValue(other, /Probability.*transport/iu)),
        variations,
        fetchedAt: Date.now(),
        stale: false
        };
    }
'''

RECONCILE = r'''
    function missionRequirementsReconcileCatalogue(parsed, catalogue, state = 'unavailable', expected = false) {
        const requirements = Array.from(parsed?.requirements || [], item => ({ ...item }));
        const unresolved = Array.from(parsed?.unresolved || [], item => ({ ...item }));
        const byKey = new Map(requirements.map((item, index) => [item.key, index]));
        for (const item of catalogue?.requirements || []) {
        const baseline = missionRequirementsOptionalNumber(item?.baseline ?? item?.missing);
        if (baseline === null) continue;
        const probability = missionRequirementsOptionalNumber(item.probability) ?? 100;
        const availabilityOnly = item.availabilityOnly === true;
        const conditional = probability < 100 || availabilityOnly;
        const index = byKey.get(item.key);
        if (index !== undefined) {
            requirements[index] = {
            ...requirements[index],
            catalogueDerived: true,
            catalogueBaseline: baseline,
            catalogueProbability: probability,
            catalogueAvailabilityOnly: availabilityOnly,
            catalogueConditional: conditional
            };
            continue;
        }
        if (conditional && index === undefined) continue;
        const requirement = {
            ...item,
            missing: baseline,
            baseline,
            statedRequirement: false,
            catalogueDerived: true,
            catalogueProbability: probability,
            catalogueAvailabilityOnly: availabilityOnly,
            catalogueConditional: conditional,
            requirementSource: catalogue?.stale ? 'Cached mission info' : 'Mission info'
        };
        byKey.set(requirement.key, requirements.length);
        requirements.push(requirement);
        }
        const unresolvedSeen = new Set(unresolved.map(item => String(item?.text || '').toLowerCase()));
        for (const item of catalogue?.unresolved || []) {
        if (item?.classification === 'informational') continue;
        const cleanLabel = missionRequirementsSafeDiagnostic(item?.label || 'Unmapped requirement', 180);
        const cleanValue = missionRequirementsSafeDiagnostic(item?.value || '', 180);
        const text = item?.classification === 'operational' ? `${cleanLabel}${cleanValue ? ` — ${cleanValue}` : ''}` : `Mission info: ${cleanLabel}${cleanValue ? ` — ${cleanValue}` : ''}`;
        if (!unresolvedSeen.has(text.toLowerCase())) {
            unresolved.push({ group: item?.group || 'other', text, catalogueDerived: true });
            unresolvedSeen.add(text.toLowerCase());
        }
        }
        if (!catalogue && expected) {
        const text = state === 'loading' || state === 'idle' ? 'Loading Requirements for this Mission…' : 'Requirements for this Mission could not be loaded; verify the mission information manually.';
        if (!unresolvedSeen.has(text.toLowerCase())) unresolved.push({ group: 'other', text, authoritativePending: state === 'loading' || state === 'idle' });
        } else if (catalogue?.stale) unresolved.push({ group: 'other', text: 'Using cached Requirements for this Mission; verify conditional requirements manually.', catalogueDerived: true });
        return { requirements, unresolved };
    }
'''

TEST_BLOCK = r'''
// Issue #230: probability, availability and informational metadata never become demand.
{
const issue230Page = {
    title: 'Issue 230 conditional metadata fixture',
    sections: {
        reward: [],
        requirements: [
            ['Required Traffic Cars', '3'],
            ['Probability of Traffic Cars being required', '75'],
            ['Traffic Cars only required, when available', 'Yes'],
            ['Required Police Cars', '5'],
            ['Required Water Carrier', '1'],
            ['Probability that Water Carrier is required', '50%'],
            ['Required Aerial Appliance Truck', '1'],
            ['Probability of Aerial Appliance Truck being required', '5'],
            ['Unknown availability switch', 'Yes']
        ],
        other: [
            ['Probability of transport', '40'],
            ['Critical Care Probability', '25'],
            ['Unknown informational flag', 'Yes']
        ]
    },
    variations: []
};
const issue230Catalogue = api.parseCatalogueDocument(makeCatalogueDocument(issue230Page), { id: 23000 });
const issue230ByKey = new Map(issue230Catalogue.requirements.map(item => [item.key, item]));
assert.strictEqual(issue230ByKey.get('traffic-car')?.baseline, 3, 'Traffic Car quantity remains three');
assert.strictEqual(issue230ByKey.get('traffic-car')?.probability, 75, 'Traffic Car chance is attached separately');
assert.strictEqual(issue230ByKey.get('traffic-car')?.availabilityOnly, true, 'Traffic Car availability qualifier is attached separately');
assert.strictEqual(issue230ByKey.get('water-carrier')?.probability, 50, 'Water Carrier chance is attached separately');
assert.strictEqual(issue230ByKey.get('aerial')?.probability, 5, 'Aerial Appliance chance is attached separately');
assert.strictEqual(issue230ByKey.get('police-car')?.probability, 100, 'unconditional Police Cars remain unconditional');
assert.strictEqual(issue230Catalogue.requirements.some(item => item.baseline === 75), false, '75 percent is never a vehicle count');
assert.strictEqual(issue230Catalogue.unresolved.length, 0, 'availability and unknown informational booleans do not enter unresolved output');
assert(issue230Catalogue.metadata.some(item => item.classification === 'probability' && item.key === 'traffic-car'), 'probability metadata remains typed for diagnostics');
assert(issue230Catalogue.metadata.some(item => item.classification === 'availability' && item.key === 'traffic-car'), 'availability metadata remains typed for diagnostics');

const issue230CatalogueOnly = api.reconcileCatalogue({ requirements: [], unresolved: [] }, issue230Catalogue, 'ready', true);
assert.deepStrictEqual(
    JSON.parse(JSON.stringify(issue230CatalogueOnly.requirements.map(item => item.key))),
    ['police-car'],
    'catalogue-only conditional vehicles are dormant while unconditional demand remains'
);
assert.strictEqual(issue230CatalogueOnly.unresolved.length, 0, 'dormant conditional metadata keeps the Matrix neutral');

const issue230LiveTraffic = api.parseText('2 Traffic Cars', 'vehicles');
const issue230LiveReconciled = api.reconcileCatalogue({ requirements: issue230LiveTraffic.requirements, unresolved: [] }, issue230Catalogue, 'ready', true);
const issue230Traffic = issue230LiveReconciled.requirements.find(item => item.key === 'traffic-car');
assert(issue230Traffic, 'live state activates conditional Traffic Car demand');
assert.strictEqual(issue230Traffic.catalogueProbability, 75, 'activated live row retains chance metadata');
assert.strictEqual(issue230Traffic.catalogueAvailabilityOnly, true, 'activated live row retains availability metadata');
assert.strictEqual(issue230LiveReconciled.requirements.some(item => item.key === 'water-carrier'), false, 'unconfirmed Water Carrier remains dormant');
assert.strictEqual(issue230LiveReconciled.requirements.some(item => item.key === 'aerial'), false, 'unconfirmed Aerial Appliance remains dormant');

const issue230MetadataText = 'Probability of Traffic Cars being required: 75; Traffic Cars only required, when available — Yes; 2 Police Cars';
const issue230MetadataParsed = api.parseText(issue230MetadataText, 'vehicles');
assert.deepStrictEqual(
    JSON.parse(JSON.stringify(issue230MetadataParsed.requirements.map(item => ({ key: item.key, missing: item.missing })))),
    [{ key: 'police-car', missing: 2 }],
    'direct parser removes metadata before capability matching'
);
assert.strictEqual(issue230MetadataParsed.remaining, '', 'removed metadata never leaks into unresolved text');
assert.strictEqual(api.parseText('75 Probability of Traffic Cars being required', 'vehicles').requirements.length, 0, 'leading percentage is not parsed as quantity');
assert.strictEqual(api.parseText('Traffic Cars only required when available: Yes', 'vehicles').remaining, '', 'availability qualifier is consumed as metadata');
assert.strictEqual(api.catalogueRequirement('Probability of Traffic Cars being required', '75'), null, 'catalogue requirement parser rejects probability rows directly');

const issue230SourceDoc = new FakeDocument();
const issue230SourceCandidate = makeMissionCandidate(issue230SourceDoc, issue230MetadataText);
const issue230SourceParsed = api.parseSource(issue230SourceCandidate.source);
assert.deepStrictEqual(
    JSON.parse(JSON.stringify(issue230SourceParsed.requirements.map(item => ({ key: item.key, missing: item.missing })))),
    [{ key: 'police-car', missing: 2 }],
    'normal mission source excludes probability and availability fragments'
);
assert.strictEqual(issue230SourceParsed.unresolved.length, 0, 'normal mission source has no metadata unresolved warning');

const issue230UnconditionalPage = {
    title: 'Issue 230 isolation fixture',
    sections: { reward: [], requirements: [['Required Traffic Cars', '2']], other: [] },
    variations: []
};
const issue230Unconditional = api.parseCatalogueDocument(makeCatalogueDocument(issue230UnconditionalPage), { id: 23001 });
assert.strictEqual(issue230Unconditional.requirements[0].probability, 100, 'conditional modifier state never leaks between missions');
assert.strictEqual(issue230Unconditional.requirements[0].availabilityOnly, false, 'availability state never leaks between missions');
const issue230UnconditionalReconciled = api.reconcileCatalogue({ requirements: [], unresolved: [] }, issue230Unconditional, 'ready', true);
assert.strictEqual(issue230UnconditionalReconciled.requirements[0].key, 'traffic-car', 'unconditional authoritative Traffic Cars remain active');

const issue230PanelRow = {
    key: 'police-car', requirement: 'Police Car', covered: false, definitelyOpen: true, uncertain: false, partial: false,
    requiredText: '5', onSiteText: '0', respondingText: '0', selectedText: '0', stillNeededText: '5'
};
const issue230Panel = api.panelHtml([issue230PanelRow], []);
assert(issue230Panel.html.includes('1 outstanding · 0/1 covered'), 'header totals count only operational rows');
assert(!issue230Panel.html.includes('Probability of') && !issue230Panel.html.includes('only required'), 'metadata is absent from responsive Matrix rendering');
}

'''


def main() -> int:
    source = SOURCE.read_text(encoding="utf-8")
    if source.count("4.20.19") != 2:
        raise RuntimeError(f"source version marker count changed: {source.count('4.20.19')}")
    source = source.replace("4.20.19", "4.20.20")
    source = replace_function(source, "missionRequirementsParseText", PARSE_TEXT)
    source = replace_function(source, "missionRequirementsParseSource", PARSE_SOURCE)
    source = replace_function(source, "missionRequirementsParseGenericText", GENERIC_TEXT)
    marker = "    function missionRequirementsCatalogueRequirement(label, value) {"
    if source.count(marker) != 1:
        raise RuntimeError("catalogue requirement insertion marker changed")
    source = source.replace(marker, HELPERS.rstrip() + "\n\n" + marker, 1)
    source = replace_function(source, "missionRequirementsCatalogueRequirement", CATALOGUE_REQUIREMENT)
    source = replace_function(source, "missionRequirementsCatalogueParseDocument", PARSE_CATALOGUE)
    source = replace_function(source, "missionRequirementsReconcileCatalogue", RECONCILE)
    SOURCE.write_text(source, encoding="utf-8")

    runtime = RUNTIME_TEST.read_text(encoding="utf-8")
    runtime = replace_once(runtime, "version: '4.20.19'", "version: '4.20.20'", "runtime version")
    runtime = replace_once(
        runtime,
        "    catalogueDescriptor: missionRequirementsCatalogueDescriptor,\n    parseCatalogueDocument: missionRequirementsCatalogueParseDocument,",
        "    catalogueDescriptor: missionRequirementsCatalogueDescriptor,\n    catalogueModifier: missionRequirementsCatalogueModifier,\n    stripNonDemandMetadata: missionRequirementsStripNonDemandMetadata,\n    catalogueRequirement: missionRequirementsCatalogueRequirement,\n    parseCatalogueDocument: missionRequirementsCatalogueParseDocument,",
        "runtime API exports",
    )
    runtime = replace_once(runtime, "// Issue #260: clean labels and typed Mission Info personnel classification.\n", TEST_BLOCK + "// Issue #260: clean labels and typed Mission Info personnel classification.\n", "Issue 230 runtime fixtures")
    RUNTIME_TEST.write_text(runtime, encoding="utf-8")

    contract = CONTRACT.read_text(encoding="utf-8")
    contract = replace_once(
        contract,
        '        "function missionRequirementsCataloguePersonnelRequirements(label, value, kind = null)",\n',
        '        "function missionRequirementsCataloguePersonnelRequirements(label, value, kind = null)",\n        "function missionRequirementsCatalogueModifier(label, value = \'\', resolveCapability = true)",\n        "function missionRequirementsStripNonDemandMetadata(rawText, resolveCapability = false)",\n',
        "contract markers",
    )
    contract = replace_once(
        contract,
        '    assert "catalogueOnly && catalogueProbability < 100" in source, "probabilistic authoritative requirements must remain uncertain"\n',
        '    assert "catalogueOnly && catalogueProbability < 100" in source, "probabilistic authoritative requirements must remain uncertain"\n    assert "if (conditional && index === undefined) continue" in source, "catalogue-only conditional demand must remain dormant"\n    assert "classification: \'probability\'" in source and "classification: \'availability\'" in source, "probability and availability metadata need typed separation"\n    assert "missionRequirementsStripNonDemandMetadata(rawText, false)" in source, "live parser must classify metadata before requirement matching"\n',
        "contract assertions",
    )
    CONTRACT.write_text(contract, encoding="utf-8")

    changelog = CHANGELOG.read_text(encoding="utf-8")
    entry = """## [4.20.20] - 2026-07-21\n\n### Fixed\n- Mission Info probability values can no longer become vehicle quantities; `75` probability now remains metadata rather than `75 Traffic Cars`.\n- `only required, when available` qualifiers no longer appear as Matrix rows or unresolved MissionChief requirements.\n- Probability-qualified and availability-only catalogue counts remain dormant until the live mission confirms that the resource is active.\n- Patient transport, critical-care and unknown boolean catalogue metadata remain outside operational Matrix demand.\n\n### Validation\n- Added deterministic normal-page, parser, catalogue, conditional-activation, mission-isolation and Matrix-summary regressions based on the official LSSM V4 separation of `requirements`, `chances` and `prerequisites`.\n\n"""
    changelog = replace_once(changelog, "## [Unreleased]\n\n", "## [Unreleased]\n\n" + entry, "changelog release entry")
    CHANGELOG.write_text(changelog, encoding="utf-8")

    help_text = HELP.read_text(encoding="utf-8")
    help_text = replace_once(help_text, "Guide for Toolkit v4.20.19", "Guide for Toolkit v4.20.20", "help version")
    HELP.write_text(help_text, encoding="utf-8")

    DOC.write_text(
        """# Issue #230 — Probability and availability metadata\n\n## Corrected model\n\nThe Mission Requirements Matrix now follows the same structural separation used by the official LSSM V4 Mission Helper:\n\n- `requirements` supplies resource quantities;\n- `chances` supplies probability metadata;\n- `prerequisites` and availability rules remain non-operational metadata.\n\nThe Toolkit has no LSSM runtime dependency. The reviewed LSSM implementation was used only to verify the semantic model.\n\n## Runtime behaviour\n\n- Probability and chance captions are classified before capability matching or generic fallback.\n- Availability-only boolean rows are consumed as modifiers and never become unresolved requirements.\n- Conditional catalogue quantities are associated by canonical capability key.\n- Catalogue-only conditional quantities remain dormant.\n- A live MissionChief requirement activates the corresponding row and retains its catalogue baseline and modifier metadata.\n- Unconditional catalogue requirements and patient-derived Ambulance demand remain unchanged.\n- Modifier state is local to one parsed mission catalogue and cannot leak across AJAX or normal-page mission transitions.\n\n## Regression coverage\n\nFixtures cover Traffic Cars, Water Carrier, Aerial Appliance Truck, patient transport probability, critical-care probability, unknown booleans, direct parsing, normal source parsing, conditional activation, unconditional preservation, cross-mission isolation and header totals.\n""",
        encoding="utf-8",
    )

    for path in (
        ROOT / "docs/issue-230-probability-source-inspection.txt",
        ROOT / "docs/issue-230-probability-source-inspection-v2.txt",
        ROOT / "docs/issue-230-catalogue-parser-body.txt",
    ):
        path.unlink(missing_ok=True)

    env = {**os.environ, "PYTHONDONTWRITEBYTECODE": "1"}
    commands = [
        ["node", "--check", str(SOURCE)],
        ["node", str(RUNTIME_TEST)],
        ["python3", str(CONTRACT)],
        ["python3", str(ROOT / ".github/scripts/validate_userscript.py")],
        ["git", "diff", "--check"],
    ]
    for command in commands:
        subprocess.run(command, cwd=ROOT, env=env, check=True)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
