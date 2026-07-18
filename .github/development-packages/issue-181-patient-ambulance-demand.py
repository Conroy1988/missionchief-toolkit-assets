#!/usr/bin/env python3
from __future__ import annotations

import hashlib
import json
import re
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
SOURCE = ROOT / "src" / "MissionChief_Map_Command_Toolkit.user.js"
DIST_USER = ROOT / "dist" / "MissionChief_Map_Command_Toolkit.user.js"
DIST_TEXT = ROOT / "dist" / "MissionChief_Map_Command_Toolkit.txt"
DIST_SUMS = ROOT / "dist" / "SHA256SUMS.txt"
DIST_MANIFEST = ROOT / "dist" / "release-manifest.json"
CHANGELOG = ROOT / "CHANGELOG.md"
HELP_INDEX = ROOT / "help" / "index.html"
HELP_MANIFEST = ROOT / "help" / "manifest.json"
RUNTIME_TEST = ROOT / ".github" / "scripts" / "test_mission_requirements_runtime.js"
CONTRACT_TEST = ROOT / ".github" / "scripts" / "test_mission_requirements_contract.py"
DOC = ROOT / "docs" / "issue-181-patient-derived-ambulance-demand-contract.md"
DIAGNOSTIC = ROOT / ".github" / "diagnostics" / "issue-181-map.txt"
PREVIOUS = "4.17.0"
VERSION = "4.18.0"


def replace_once(text: str, old: str, new: str, label: str) -> str:
    count = text.count(old)
    if count != 1:
        raise AssertionError(f"{label}: expected one match, found {count}")
    return text.replace(old, new, 1)


def replace_first(text: str, old: str, new: str, label: str) -> str:
    if old not in text:
        raise AssertionError(f"{label}: match not found")
    return text.replace(old, new, 1)


def regex_once(text: str, pattern: str, replacement: str, label: str) -> str:
    updated, count = re.subn(pattern, replacement, text, count=1, flags=re.MULTILINE | re.DOTALL)
    if count != 1:
        raise AssertionError(f"{label}: expected one regex match, found {count}")
    return updated


source = SOURCE.read_text(encoding="utf-8")
source = replace_once(source, f"// @version      {PREVIOUS}", f"// @version      {VERSION}", "metadata version")
source = replace_once(source, f"        version: '{PREVIOUS}',", f"        version: '{VERSION}',", "runtime version")

patient_helpers = r'''

    // Issue #181: patient-derived ambulance demand.
    const MISSION_REQUIREMENTS_PATIENT_TRANSITION_MS = 1400;
    const MISSION_REQUIREMENTS_PATIENT_SNAPSHOT_LIMIT = 32;
    const missionRequirementsPatientSnapshots = new Map();

    function missionRequirementsPatientCount(candidate) {
        const root = missionRequirementsCandidateRoot(candidate) || candidate?.root || candidate?.mount;
        const scopes = Array.from(new Set([root, candidate?.mount].filter(scope => scope?.querySelector)));
        let patientText = null;
        let patientForm = null;
        for (const scope of scopes) {
            if (!patientText) patientText = scope.matches?.('#patient_button_text') ? scope : scope.querySelector?.('#patient_button_text');
            if (!patientForm) patientForm = scope.matches?.('#patient_button_form') ? scope : scope.querySelector?.('#patient_button_form');
            if (patientText && patientForm) break;
        }
        const holder = patientText || patientForm;
        if (!holder) return { present: false, known: true, count: 0, source: 'absent', text: '' };

        const attributeNames = ['data-patient-count', 'data-patient-total', 'data-patients', 'patient_count', 'patients_count'];
        for (const scope of Array.from(new Set([patientText, patientForm].filter(Boolean)))) {
            for (const name of attributeNames) {
                const value = missionRequirementsOptionalNumber(scope?.getAttribute?.(name));
                if (value !== null) return { present: true, known: true, count: value, source: name, text: missionRequirementsElementText(holder) };
            }
            for (const value of [scope?.dataset?.patientCount, scope?.dataset?.patientTotal, scope?.dataset?.patients]) {
                const parsed = missionRequirementsOptionalNumber(value);
                if (parsed !== null) return { present: true, known: true, count: parsed, source: 'dataset', text: missionRequirementsElementText(holder) };
            }
        }

        const strong = patientText?.querySelector?.('strong')
            || patientForm?.querySelector?.('#patient_button_text strong, strong')
            || null;
        const parseTotal = value => {
            const match = String(value || '').replace(/\u00a0/gu, ' ').match(/\b(\d{1,3}(?:[\s,.]\d{3})*)\s+patients?\b/iu);
            return match ? missionRequirementsNumber(match[1]) : null;
        };
        const strongCount = parseTotal(missionRequirementsElementText(strong));
        if (strongCount !== null) return { present: true, known: true, count: strongCount, source: 'patient-total-strong', text: missionRequirementsElementText(holder) };
        const text = missionRequirementsElementText(holder);
        const textCount = parseTotal(text);
        if (textCount !== null) return { present: true, known: true, count: textCount, source: 'patient-summary-text', text };
        return { present: true, known: false, count: null, source: 'patient-summary-unresolved', text };
    }

    function missionRequirementsPatientSnapshotPrune(now = Date.now()) {
        for (const [key, snapshot] of missionRequirementsPatientSnapshots) {
            if (now - (Number(snapshot?.updatedAt) || 0) > 60000) missionRequirementsPatientSnapshots.delete(key);
        }
        if (missionRequirementsPatientSnapshots.size <= MISSION_REQUIREMENTS_PATIENT_SNAPSHOT_LIMIT) return;
        const ordered = Array.from(missionRequirementsPatientSnapshots.entries())
            .sort((left, right) => (Number(left[1]?.updatedAt) || 0) - (Number(right[1]?.updatedAt) || 0));
        for (const [key] of ordered.slice(0, missionRequirementsPatientSnapshots.size - MISSION_REQUIREMENTS_PATIENT_SNAPSHOT_LIMIT)) {
            missionRequirementsPatientSnapshots.delete(key);
        }
    }

    function missionRequirementsPatientState(record, now = Date.now()) {
        const candidate = record?.candidate || record;
        const missionIdentity = missionRequirementsMissionIdentity(candidate, record?.source || candidate?.source);
        const current = missionRequirementsPatientCount(candidate);
        const key = missionIdentity > 0 ? String(missionIdentity) : '';
        if (current.present) {
            if (record?.patientTransitionTimer) runtimeClearTimeout(record.patientTransitionTimer);
            if (record) record.patientTransitionTimer = null;
            if (key) missionRequirementsPatientSnapshots.set(key, { state: { ...current }, updatedAt: now });
            missionRequirementsPatientSnapshotPrune(now);
            return { ...current, missionIdentity, transitional: false };
        }

        const snapshot = key ? missionRequirementsPatientSnapshots.get(key) : null;
        const age = snapshot ? now - (Number(snapshot.updatedAt) || 0) : Number.POSITIVE_INFINITY;
        if (snapshot?.state && age >= 0 && age < MISSION_REQUIREMENTS_PATIENT_TRANSITION_MS) {
            if (record && !record.patientTransitionTimer) {
                const wait = Math.max(20, MISSION_REQUIREMENTS_PATIENT_TRANSITION_MS - age + 20);
                record.patientTransitionTimer = runtimeSetTimeout(() => {
                    record.patientTransitionTimer = null;
                    missionRequirementsScheduleRecord(record);
                }, wait);
            }
            return { ...snapshot.state, missionIdentity, transitional: true };
        }
        if (key && snapshot) missionRequirementsPatientSnapshots.delete(key);
        if (record?.patientTransitionTimer) runtimeClearTimeout(record.patientTransitionTimer);
        if (record) record.patientTransitionTimer = null;
        return { ...current, missionIdentity, transitional: false };
    }

    function missionRequirementsReconcilePatientDemand(parsed, patientState) {
        const requirements = Array.from(parsed?.requirements || []).map(requirement => ({ ...requirement }));
        const unresolved = Array.from(parsed?.unresolved || []).map(item => ({ ...item }));
        const ambulanceDefinition = MISSION_REQUIREMENT_DEFINITIONS.find(definition => definition.key === 'ambulance');
        const ambulanceIndexes = requirements.map((requirement, index) => requirement.key === 'ambulance' ? index : -1).filter(index => index >= 0);
        const statedRows = ambulanceIndexes.map(index => requirements[index]);
        const statedMissing = statedRows.reduce((maximum, requirement) => Math.max(maximum, Math.max(0, Number(requirement?.missing) || 0)), 0);
        const patientPresent = patientState?.present === true || patientState?.transitional === true;
        const patientKnown = patientState?.known === true && Number.isFinite(Number(patientState?.count));
        const patientCount = patientKnown ? Math.max(0, Number(patientState.count) || 0) : null;

        if (!patientPresent && patientCount === 0) return { requirements, unresolved, patientState };
        if (patientKnown && patientCount === 0 && !statedRows.length) return { requirements, unresolved, patientState };

        if (statedRows.length) {
            for (const index of ambulanceIndexes.slice(1).reverse()) requirements.splice(index, 1);
        }
        const index = ambulanceIndexes.length ? ambulanceIndexes[0] : requirements.length;
        const base = statedRows[0] || {
            key: 'ambulance',
            requirement: 'Ambulance',
            missing: patientCount ?? 0,
            group: 'vehicles',
            definition: ambulanceDefinition
        };
        const row = {
            ...base,
            missing: statedRows.length ? statedMissing : (patientCount ?? 0),
            group: 'vehicles',
            definition: ambulanceDefinition,
            patientDerived: true,
            patientCountKnown: patientKnown,
            patientRequired: patientCount,
            statedRequirement: statedRows.length > 0,
            requirementSource: 'Patients'
        };
        if (index < requirements.length) requirements[index] = row;
        else requirements.push(row);
        if (!patientKnown && !unresolved.some(item => item?.patientDerived)) {
            unresolved.push({ group: 'vehicles', text: 'Patient total is present but could not be determined.', patientDerived: true });
        }
        return { requirements, unresolved, patientState };
    }
'''
source = replace_once(
    source,
    "    function missionRequirementsVehicleType(element) {",
    patient_helpers + "\n    function missionRequirementsVehicleType(element) {",
    "patient helpers insertion",
)

old_resolve = re.search(r"    function missionRequirementsResolve\(candidate, parsed, catalogue = null\) \{[\s\S]*?\n    \}\n\n    function missionRequirementsOverallState", source)
if not old_resolve:
    raise AssertionError("missionRequirementsResolve block not found")
new_resolve = r'''    function missionRequirementsResolve(candidate, parsed, catalogue = null) {
        const rawSelectedUnits = missionRequirementsCollectUnits(candidate, 'selected');
        const rawRespondingUnits = missionRequirementsCollectUnits(candidate, 'responding');
        const rawOnSiteUnits = missionRequirementsCollectUnits(candidate, 'onsite');
        const buckets = missionRequirementsExclusiveUnitBuckets(rawSelectedUnits, rawRespondingUnits, rawOnSiteUnits);
        const catalogueByKey = new Map(Array.from(catalogue?.requirements || []).map(item => [item.key, item]));
        return parsed.requirements.map(requirement => {
            if (requirement.definition?.countable === false) return missionRequirementsUnknownCoverageRow(requirement);
            const condition = missionRequirementsDefinitionCondition(requirement.definition, candidate);
            if (condition !== true) {
                const unknown = missionRequirementsCapacity(0, null, false);
                const unresolvedRow = missionRequirementsCoverageRow(requirement, unknown, unknown, unknown, unknown);
                return { ...unresolvedRow, conditionKnown: condition !== null, conditionMatched: false, uncertain: true, definitelyOpen: false, coverageKnown: false };
            }
            let selected;
            let responding;
            let onSite;
            if (requirement.definition?.bar) {
                const selectedValue = missionRequirementsProgressValue(candidate, requirement.definition.bar, 'selected');
                const respondingValue = missionRequirementsProgressValue(candidate, requirement.definition.bar, 'driving');
                const onSiteMetrics = ['at_mission', 'on_site', 'onsite', 'arrived', 'actual'];
                const onSiteValue = onSiteMetrics.map(metric => missionRequirementsProgressValue(candidate, requirement.definition.bar, metric)).find(value => value !== null);
                selected = selectedValue === null ? missionRequirementsCapacity(0, null, false) : missionRequirementsCapacity(selectedValue, selectedValue, true);
                responding = respondingValue === null ? missionRequirementsCapacity(0, null, false) : missionRequirementsCapacity(respondingValue, respondingValue, true);
                onSite = onSiteValue === undefined ? missionRequirementsCapacity(0, null, false) : missionRequirementsCapacity(onSiteValue, onSiteValue, true);
            } else {
                selected = missionRequirementsAggregate(requirement, buckets.selected);
                responding = missionRequirementsAggregate(requirement, buckets.responding);
                onSite = missionRequirementsAggregate(requirement, buckets.onSite);
            }

            const catalogueRequirement = catalogueByKey.get(requirement.key);
            const baseline = missionRequirementsOptionalNumber(catalogueRequirement?.baseline ?? catalogueRequirement?.missing);
            const patientKnown = requirement.patientDerived === true && requirement.patientCountKnown === true;
            const patientUnknown = requirement.patientDerived === true && requirement.patientCountKnown === false;
            const patientRequired = patientKnown ? Math.max(0, Number(requirement.patientRequired) || 0) : null;
            const hasStatedRequirement = requirement.statedRequirement !== false;

            if (baseline !== null && hasStatedRequirement) {
                const inferredOnSite = Math.max(0, baseline - Math.max(0, Number(requirement.missing) || 0));
                if (inferredOnSite > onSite.min) {
                    const inferredMax = onSite.max === null ? null : Math.max(onSite.max, inferredOnSite);
                    onSite = missionRequirementsCapacity(inferredOnSite, inferredMax, onSite.known && inferredMax === inferredOnSite);
                }
            }

            const statedRequiredMin = hasStatedRequirement ? Math.max(0, Number(requirement.missing) || 0) + onSite.min : 0;
            const statedRequiredMax = hasStatedRequirement
                ? (onSite.max === null ? null : Math.max(0, Number(requirement.missing) || 0) + onSite.max)
                : 0;
            const fixedMinimum = Math.max(patientRequired ?? 0, baseline ?? 0, statedRequiredMin);
            let required;
            if (patientUnknown) {
                required = missionRequirementsCapacity(Math.max(baseline ?? 0, statedRequiredMin), null, false);
            } else if (patientKnown) {
                const possibleMaximum = statedRequiredMax === null ? null : Math.max(patientRequired, baseline ?? 0, statedRequiredMax);
                const exact = possibleMaximum !== null && possibleMaximum === fixedMinimum && (hasStatedRequirement ? onSite.known : true);
                required = missionRequirementsCapacity(fixedMinimum, possibleMaximum, exact);
            } else {
                const liveRequiredMin = statedRequiredMin;
                const liveRequiredMax = statedRequiredMax;
                required = baseline !== null
                    ? missionRequirementsCapacity(Math.max(baseline, liveRequiredMin), Math.max(baseline, liveRequiredMin), true)
                    : missionRequirementsCapacity(liveRequiredMin, liveRequiredMax, onSite.known && liveRequiredMax !== null && liveRequiredMin === liveRequiredMax);
            }

            const row = missionRequirementsCoverageRow(requirement, selected, responding, onSite, required);
            if (patientUnknown) {
                row.covered = false;
                row.definitelyOpen = false;
                row.uncertain = true;
                row.coverageKnown = false;
            }
            const authorities = [];
            if (requirement.patientDerived) authorities.push('patients');
            if (baseline !== null) authorities.push('catalogue');
            if (hasStatedRequirement) authorities.push('live');
            return {
                ...row,
                conditionKnown: true,
                conditionMatched: true,
                requirementAuthority: authorities.length ? authorities.join('+') : 'live-reconstructed'
            };
        });
    }

    function missionRequirementsOverallState'''
source = source[:old_resolve.start()] + new_resolve + source[old_resolve.end():]

old_panel_row = """            const status = row.covered ? 'fulfilled' : row.uncertain ? 'requires confirmation' : row.partial ? 'partially fulfilled' : 'outstanding';
            return `<tr data-row-state="${rowState}" title="${escapeHtml(`${row.requirement}: ${status}`)}"><td>${escapeHtml(prefix + row.requirement)}</td><td data-label="Required">${escapeHtml(requiredText)}</td><td data-label="On site">${escapeHtml(onSiteText)}</td><td data-label="Respond.">${escapeHtml(respondingText)}</td><td data-label="Selected">${escapeHtml(selectedText)}</td><td class="mcms-req-still" data-label="Need">${escapeHtml(stillText)}</td></tr>`;"""
new_panel_row = """            const status = row.covered ? 'fulfilled' : row.uncertain ? 'requires confirmation' : row.partial ? 'partially fulfilled' : 'outstanding';
            const sourceBadge = row.requirementSource ? `<small class="mcms-req-source">${escapeHtml(row.requirementSource)}</small>` : '';
            return `<tr data-row-state="${rowState}" title="${escapeHtml(`${row.requirement}: ${status}`)}"><td><span>${escapeHtml(prefix + row.requirement)}</span>${sourceBadge}</td><td data-label="Required">${escapeHtml(requiredText)}</td><td data-label="On site">${escapeHtml(onSiteText)}</td><td data-label="Respond.">${escapeHtml(respondingText)}</td><td data-label="Selected">${escapeHtml(selectedText)}</td><td class="mcms-req-still" data-label="Need">${escapeHtml(stillText)}</td></tr>`;"""
source = replace_once(source, old_panel_row, new_panel_row, "patient source badge rendering")
source = replace_once(
    source,
    "#${SCRIPT.missionRequirementsPanelId} tbody td:first-child{padding-left:7px!important;border-left:3px solid var(--mcms-row-state)!important;font-weight:850!important;text-align:left!important;white-space:normal!important;overflow-wrap:anywhere!important;word-break:normal!important}",
    "#${SCRIPT.missionRequirementsPanelId} tbody td:first-child{padding-left:7px!important;border-left:3px solid var(--mcms-row-state)!important;font-weight:850!important;text-align:left!important;white-space:normal!important;overflow-wrap:anywhere!important;word-break:normal!important}\n#${SCRIPT.missionRequirementsPanelId} tbody td:first-child>span{display:inline!important}\n#${SCRIPT.missionRequirementsPanelId} .mcms-req-source{display:inline-flex!important;align-items:center!important;margin-left:5px!important;padding:1px 4px!important;border:1px solid color-mix(in srgb,var(--mcms-req-accent) 48%,transparent)!important;border-radius:999px!important;background:color-mix(in srgb,var(--mcms-req-accent) 12%,transparent)!important;color:var(--mcms-req-accent)!important;font-size:8px!important;line-height:1.2!important;font-weight:900!important;letter-spacing:.08px!important;text-transform:uppercase!important;vertical-align:middle!important;white-space:nowrap!important}",
    "patient source badge CSS",
)

old_render = re.search(r"    function missionRequirementsRenderRecord\(record\) \{[\s\S]*?\n    \}\n    function missionRequirementsScheduleRecord", source)
if not old_render:
    raise AssertionError("missionRequirementsRenderRecord block not found")
new_render = r'''    function missionRequirementsRenderRecord(record) {
        if (!record?.source?.isConnected || !record?.candidate?.mount?.isConnected || !record?.panel?.isConnected) {
            scheduleMissionRequirementsScan(0);
            return;
        }
        if (missionRequirementsLssmActive(record.candidate, record.source)) {
            missionRequirementsRemoveRecord(record.source);
            return;
        }
        missionRequirementsCatalogueEnsure(record);
        const presentCatalogue = reason => {
            if (!record.catalogue) return false;
            missionRequirementsRestoreSource(record.source);
            missionRequirementsPresent(record, missionRequirementsCataloguePanelHtml({ ...record.catalogue, stale: record.catalogueState === 'stale' }), reason);
            return true;
        };
        const patientState = missionRequirementsPatientState(record);
        const reconcile = parsed => missionRequirementsReconcilePatientDemand(parsed, patientState);
        const presentLive = parsed => {
            const reconciled = reconcile(parsed);
            if (!reconciled.requirements.length) return false;
            if (record.source.getAttribute?.('data-mcms-requirements-anchor') !== '1') missionRequirementsHideSource(record.source);
            else missionRequirementsRestoreSource(record.source);
            missionRequirementsPresent(
                record,
                missionRequirementsPanelHtml(missionRequirementsResolve(record.candidate, reconciled, record.catalogue), reconciled.unresolved),
                reconciled.unresolved.length ? 'partially unresolved requirement or patient data' : ''
            );
            return true;
        };
        const age = Date.now() - (record.startedAt || Date.now());
        const anchor = record.source.getAttribute?.('data-mcms-requirements-anchor') === '1';
        if (anchor) {
            if (presentLive({ requirements: [], unresolved: [] })) return;
            if (presentCatalogue('live requirement source absent; official catalogue baseline shown')) return;
            missionRequirementsRestoreSource(record.source);
            const loading = record.catalogueState === 'loading' || age < 1200;
            missionRequirementsPresent(record, missionRequirementsFallbackHtml(loading ? 'loading' : 'error'), loading ? '' : 'requirement source and catalogue unavailable');
            return;
        }
        const raw = missionRequirementsElementText(record.source);
        if (!raw) {
            if (presentLive({ requirements: [], unresolved: [] })) return;
            missionRequirementsRestoreSource(record.source);
            missionRequirementsPresent(record, missionRequirementsFallbackHtml(age < 1200 ? 'loading' : 'empty'));
            return;
        }
        let parsed;
        try { parsed = missionRequirementsParseSource(record.source); }
        catch (err) {
            const patientOnly = reconcile({ requirements: [], unresolved: [{ group: 'vehicles', text: `Requirement parser failed: ${err?.message || 'unknown'}` }] });
            if (patientOnly.requirements.length) {
                missionRequirementsHideSource(record.source);
                missionRequirementsPresent(record, missionRequirementsPanelHtml(missionRequirementsResolve(record.candidate, patientOnly, record.catalogue), patientOnly.unresolved), 'parser exception with patient demand preserved');
                return;
            }
            if (presentCatalogue(`parser exception; official catalogue baseline shown: ${err?.message || 'unknown'}`)) return;
            missionRequirementsRestoreSource(record.source);
            missionRequirementsPresent(record, missionRequirementsFallbackHtml(record.catalogueState === 'loading' ? 'loading' : 'error'), `parser exception: ${err?.message || 'unknown'}`);
            return;
        }
        const reconciled = reconcile(parsed);
        if (!reconciled.requirements.length) {
            if (presentCatalogue(reconciled.unresolved.length ? 'live requirement text unparseable; official catalogue baseline shown' : 'no quantified live requirements; official catalogue baseline shown')) return;
            missionRequirementsRestoreSource(record.source);
            missionRequirementsPresent(record, missionRequirementsFallbackHtml(record.catalogueState === 'loading' ? 'loading' : 'error'), reconciled.unresolved.length ? 'requirement text unparseable' : 'no quantified requirements detected');
            return;
        }
        missionRequirementsHideSource(record.source);
        missionRequirementsPresent(record, missionRequirementsPanelHtml(missionRequirementsResolve(record.candidate, reconciled, record.catalogue), reconciled.unresolved), reconciled.unresolved.length ? 'partially unresolved requirement or patient data' : '');
    }
    function missionRequirementsScheduleRecord'''
source = source[:old_render.start()] + new_render + source[old_render.end():]

source = replace_first(
    source,
    "#missing_text, [data-mcms-requirements-anchor], #mission_vehicle_driving, #mission_vehicle_at_mission, #vehicle_show_table_body_all",
    "#missing_text, [data-mcms-requirements-anchor], #patient_button_form, #patient_button_text, #patient_button_text strong, [data-patient-count], [data-patient-total], [data-patients], #mission_vehicle_driving, #mission_vehicle_at_mission, #vehicle_show_table_body_all",
    "record patient mutation selectors",
)
source = replace_first(
    source,
    "#missing_text, [data-mcms-requirements-anchor], #mission_vehicle_driving, #mission_vehicle_at_mission, #vehicle_show_table_body_all",
    "#missing_text, [data-mcms-requirements-anchor], #patient_button_form, #patient_button_text, #patient_button_text strong, [data-patient-count], [data-patient-total], [data-patients], #mission_vehicle_driving, #mission_vehicle_at_mission, #vehicle_show_table_body_all",
    "document patient activity selectors",
)
source = replace_once(
    source,
    "'data-max-personnel', 'tractive_vehicle_id'",
    "'data-max-personnel', 'data-patient-count', 'data-patient-total', 'data-patients', 'patient_count', 'patients_count', 'tractive_vehicle_id'",
    "patient observer attributes",
)
source = replace_once(
    source,
    "            `- on-site rows: ${count('#mission_vehicle_at_mission tbody tr')}`,",
    "            `- on-site rows: ${count('#mission_vehicle_at_mission tbody tr')}`,\n            `- patient summary nodes: ${count('#patient_button_form, #patient_button_text')}`,\n            `- patient state: ${missionRequirementsSafeDiagnostic(JSON.stringify(missionRequirementsPatientCount(candidate)), 240)}`,",
    "patient diagnostics",
)
source = replace_once(
    source,
    "                record.startedAt = Date.now();",
    "                record.startedAt = Date.now();\n                if (record.patientTransitionTimer) runtimeClearTimeout(record.patientTransitionTimer);\n                record.patientTransitionTimer = null;",
    "mission navigation patient transition reset",
)
source = replace_once(
    source,
    "        if (record.frame) runtimeCancelAnimationFrame(record.frame);\n        runtimeUntrackObserver(record.observer);",
    "        if (record.frame) runtimeCancelAnimationFrame(record.frame);\n        if (record.patientTransitionTimer) runtimeClearTimeout(record.patientTransitionTimer);\n        record.patientTransitionTimer = null;\n        runtimeUntrackObserver(record.observer);",
    "record patient timer cleanup",
)
source = replace_once(
    source,
    "    function clearMissionRequirementsPanels() {\n        for (const source of Array.from(missionRequirementsRecords.keys())) missionRequirementsRemoveRecord(source);",
    "    function clearMissionRequirementsPanels() {\n        for (const source of Array.from(missionRequirementsRecords.keys())) missionRequirementsRemoveRecord(source);\n        missionRequirementsPatientSnapshots.clear();",
    "patient snapshot cleanup",
)

SOURCE.write_text(source, encoding="utf-8")

runtime = RUNTIME_TEST.read_text(encoding="utf-8")
runtime = replace_once(runtime, "        version: '4.16.4'", "        version: '4.18.0'", "runtime fixture version")
runtime = replace_once(
    runtime,
    "    parseSource: missionRequirementsParseSource,",
    "    parseSource: missionRequirementsParseSource,\n    patientCount: missionRequirementsPatientCount,\n    patientState: missionRequirementsPatientState,\n    reconcilePatientDemand: missionRequirementsReconcilePatientDemand,",
    "runtime patient API exposure",
)
runtime = replace_once(
    runtime,
    "    missionRoot.onSiteRows = [];\n    missionRoot.queryHandler = selector => {\n        if (selector === '#missing_text') return sourceNode.isConnected ? sourceNode : null;",
    "    missionRoot.onSiteRows = [];\n    missionRoot.patientForm = null;\n    missionRoot.patientText = null;\n    missionRoot.queryHandler = selector => {\n        if (selector === '#missing_text') return sourceNode.isConnected ? sourceNode : null;\n        if (selector === '#patient_button_form') return missionRoot.patientForm?.isConnected === false ? null : missionRoot.patientForm;\n        if (selector === '#patient_button_text') return missionRoot.patientText?.isConnected === false ? null : missionRoot.patientText;",
    "mission fixture patient nodes",
)
runtime = replace_once(
    runtime,
    "    missionRoot.onSiteRows = [];\n    missionRoot.queryHandler = selector => {\n        if (selector === '#missing_text') return missionRoot.children.find(child => child.id === 'missing_text' && child.isConnected) || null;",
    "    missionRoot.onSiteRows = [];\n    missionRoot.patientForm = null;\n    missionRoot.patientText = null;\n    missionRoot.queryHandler = selector => {\n        if (selector === '#missing_text') return missionRoot.children.find(child => child.id === 'missing_text' && child.isConnected) || null;\n        if (selector === '#patient_button_form') return missionRoot.patientForm?.isConnected === false ? null : missionRoot.patientForm;\n        if (selector === '#patient_button_text') return missionRoot.patientText?.isConnected === false ? null : missionRoot.patientText;",
    "source-less fixture patient nodes",
)

patient_tests = r'''

function attachPatientSummary(candidate, totalText, detailText = '') {
    const doc = candidate.root.ownerDocument;
    const form = new FakeElement('div', doc);
    form.id = 'patient_button_form';
    const text = new FakeElement('span', doc);
    text.id = 'patient_button_text';
    const strong = new FakeElement('strong', doc);
    strong.textContent = strong.innerText = String(totalText || '');
    text.textContent = text.innerText = `${totalText || ''}${detailText ? ` - ${detailText}` : ''}`;
    text.queryMap.set('strong', strong);
    form.queryMap.set('#patient_button_text strong, strong', strong);
    form.queryMap.set('#patient_button_text', text);
    candidate.root.patientForm = form;
    candidate.root.patientText = text;
    candidate.root.appendChild(form);
    form.appendChild(text);
    text.appendChild(strong);
    return { form, text, strong };
}

const patientDoc = new FakeDocument();
patientDoc.defaultView = { MutationObserver: FakeMutationObserver, location: { pathname: '/missions/18101' } };
const patientCandidate = makeMissionCandidate(patientDoc, '');
patientCandidate.missionId = 18101;
const patientNodes = attachPatientSummary(patientCandidate, '1 Patient', '1 Untreated patients');
let patientState = api.patientCount(patientCandidate);
assert.deepStrictEqual(JSON.parse(JSON.stringify({ present: patientState.present, known: patientState.known, count: patientState.count, source: patientState.source })), {
    present: true, known: true, count: 1, source: 'patient-total-strong'
}, 'singular patient total is read from the strong summary rather than untreated text');

patientNodes.strong.textContent = patientNodes.strong.innerText = '3 Patients';
patientNodes.text.textContent = patientNodes.text.innerText = '3 Patients - 1 Untreated patients';
patientState = api.patientCount(patientCandidate);
assert.strictEqual(patientState.count, 3, 'plural patient total is parsed');
let reconciledPatients = api.reconcilePatientDemand({ requirements: [], unresolved: [] }, patientState);
assert.strictEqual(reconciledPatients.requirements.length, 1, 'patient-only mission creates one requirement row');
assert.strictEqual(reconciledPatients.requirements[0].key, 'ambulance', 'patient demand creates the Ambulance row');
assert.strictEqual(reconciledPatients.requirements[0].patientRequired, 3, 'one ambulance is required per patient');
assert.strictEqual(reconciledPatients.requirements[0].requirementSource, 'Patients', 'patient source is retained for the UI');

let patientResolved = api.resolve(patientCandidate, reconciledPatients)[0];
assert.strictEqual(patientResolved.requiredText, '3', 'patient-only demand sets exact required capacity');
assert.strictEqual(patientResolved.stillNeededText, '3', 'three patients with no ambulances need three');
assert.strictEqual(patientResolved.definitelyOpen, true, 'uncovered patient demand keeps the matrix red');

const patientOnSite = makeVehicleElement(patientDoc, 18111, 5);
const patientResponding = makeVehicleElement(patientDoc, 18112, 5);
const patientSelected = makeVehicleElement(patientDoc, 18113, 5);
patientCandidate.root.onSiteRows = [patientOnSite.row];
patientCandidate.root.enRouteRows = [patientResponding.row];
patientCandidate.root.selectedUnits = [patientSelected.vehicle];
patientResolved = api.resolve(patientCandidate, reconciledPatients)[0];
assert.strictEqual(patientResolved.onSiteText, '1', 'on-site ambulance capacity is counted');
assert.strictEqual(patientResolved.respondingText, '1', 'responding ambulance capacity is counted');
assert.strictEqual(patientResolved.selectedText, '1', 'selected ambulance capacity is counted separately');
assert.strictEqual(patientResolved.stillNeededText, '0', 'committed and selected ambulances cover patient demand');
assert.strictEqual(patientResolved.covered, true, 'covered patient demand allows a green row');

const patientAmbulanceDefinition = api.definitions.find(definition => definition.key === 'ambulance');
const statedLower = {
    requirements: [{ key: 'ambulance', requirement: 'Ambulance', missing: 1, group: 'vehicles', definition: patientAmbulanceDefinition }],
    unresolved: []
};
const mergedDemand = api.reconcilePatientDemand(statedLower, patientState);
assert.strictEqual(mergedDemand.requirements.filter(item => item.key === 'ambulance').length, 1, 'stated and patient demand never duplicate the Ambulance row');
assert.strictEqual(mergedDemand.requirements[0].missing, 1, 'stated missing quantity is retained for live reconstruction');
assert.strictEqual(mergedDemand.requirements[0].patientRequired, 3, 'patient total remains the minimum authoritative requirement');
patientCandidate.root.onSiteRows = [];
patientCandidate.root.enRouteRows = [];
patientCandidate.root.selectedUnits = [];
patientResolved = api.resolve(patientCandidate, mergedDemand)[0];
assert.strictEqual(patientResolved.requiredText, '3', 'lower stated requirement does not reduce patient-derived demand');

patientNodes.strong.textContent = patientNodes.strong.innerText = '0 Patients';
patientNodes.text.textContent = patientNodes.text.innerText = '0 Patients - 0 Untreated patients';
const zeroState = api.patientCount(patientCandidate);
assert.strictEqual(api.reconcilePatientDemand({ requirements: [], unresolved: [] }, zeroState).requirements.length, 0, 'zero patients create no synthetic ambulance row');

patientNodes.strong.textContent = patientNodes.strong.innerText = '';
patientNodes.text.textContent = patientNodes.text.innerText = 'Patient details loading';
const unknownState = api.patientCount(patientCandidate);
assert.strictEqual(unknownState.known, false, 'present but unparseable patient summary is unknown');
const unknownDemand = api.reconcilePatientDemand({ requirements: [], unresolved: [] }, unknownState);
assert.strictEqual(unknownDemand.requirements.length, 1, 'unknown patient total still creates a guarded Ambulance row');
assert.strictEqual(unknownDemand.unresolved.length, 1, 'unknown patient total is visible as unresolved');
const unknownResolved = api.resolve(patientCandidate, unknownDemand)[0];
assert.strictEqual(unknownResolved.uncertain, true, 'unknown patient total cannot become covered');
assert.strictEqual(unknownResolved.requiredText, '?', 'unknown patient total displays unknown required capacity');

const transitionRecord = { candidate: patientCandidate, source: patientCandidate.source, missionIdentity: 18101 };
patientNodes.strong.textContent = patientNodes.strong.innerText = '2 Patients';
patientNodes.text.textContent = patientNodes.text.innerText = '2 Patients - 2 Untreated patients';
let transition = api.patientState(transitionRecord, 1000);
assert.strictEqual(transition.count, 2, 'known patient snapshot is stored');
patientCandidate.root.patientForm = null;
patientCandidate.root.patientText = null;
patientNodes.form.isConnected = false;
patientNodes.text.isConnected = false;
transition = api.patientState(transitionRecord, 1100);
assert.strictEqual(transition.count, 2, 'brief same-mission DOM replacement preserves patient demand');
assert.strictEqual(transition.transitional, true, 'bounded replacement state is marked transitional');
const otherMissionCandidate = makeMissionCandidate(patientDoc, '');
otherMissionCandidate.missionId = 18102;
const otherMissionState = api.patientState({ candidate: otherMissionCandidate, source: otherMissionCandidate.source, missionIdentity: 18102 }, 1100);
assert.strictEqual(otherMissionState.count, 0, 'patient snapshot never leaks into a different mission');
transition = api.patientState(transitionRecord, 2501);
assert.strictEqual(transition.count, 0, 'patient snapshot expires after the bounded transition');

const patientRenderDoc = new FakeDocument();
patientRenderDoc.defaultView = { MutationObserver: FakeMutationObserver, location: { pathname: '/missions/18103' }, navigator: context.pageWindow.navigator, innerWidth: 1280, innerHeight: 720 };
const patientRenderCandidate = makeMissionCandidate(patientRenderDoc, '');
patientRenderCandidate.missionId = 18103;
attachPatientSummary(patientRenderCandidate, '1 Patient', '1 Untreated patients');
candidates = [patientRenderCandidate];
api.scan();
flushAnimationFrames();
const patientRecord = api.records.get(patientRenderCandidate.source);
assert(patientRecord, 'patient-only mission creates a normal Matrix record');
assert(patientRecord.panel.innerHTML.includes('Ambulance'), 'patient-only mission renders an Ambulance row');
assert(patientRecord.panel.innerHTML.includes('Patients'), 'patient-derived row identifies its source');
assert.strictEqual(patientRenderCandidate.root.children.filter(child => child.id === 'mc-map-command-toolkit-mission-requirements').length, 1, 'patient demand uses the existing single Matrix panel');
api.clear();
candidates = [];
'''
runtime = replace_once(runtime, "\nconst directDoc = new FakeDocument();", patient_tests + "\nconst directDoc = new FakeDocument();", "patient runtime fixtures")
RUNTIME_TEST.write_text(runtime, encoding="utf-8")

contract = CONTRACT_TEST.read_text(encoding="utf-8")
contract = replace_once(
    contract,
    '        "function missionRequirementsParseText(rawText, group = \'vehicles\')",',
    '        "function missionRequirementsParseText(rawText, group = \'vehicles\')",\n        "function missionRequirementsParseSource(source)",\n        "function missionRequirementsPatientCount(candidate)",\n        "function missionRequirementsPatientState(record, now = Date.now())",\n        "function missionRequirementsReconcilePatientDemand(parsed, patientState)",\n        "MISSION_REQUIREMENTS_PATIENT_TRANSITION_MS = 1400",',
    "patient contract markers",
)
contract = replace_once(
    contract,
    '        "#mission_vehicle_driving",',
    '        "#patient_button_form",\n        "#patient_button_text",\n        "#mission_vehicle_driving",',
    "patient selector markers",
)
contract = replace_once(
    contract,
    '    assert "const operational = root.querySelector?." not in source\n',
    '    assert "const operational = root.querySelector?." not in source\n'
    '    assert source.count("function missionRequirementsPatientCount(candidate)") == 1\n'
    '    assert source.count("function missionRequirementsReconcilePatientDemand(parsed, patientState)") == 1\n'
    '    assert "setInterval(" not in re.search(r"// Issue #181: patient-derived ambulance demand\\.([\\s\\S]*?)function missionRequirementsVehicleType", source).group(1)\n'
    '    assert re.search(r"key:\\s*[\'\\\"]ambulance[\'\\\"][^\\n]*types:\\s*\\[5\\]", source), "patient demand must use the conservative UK transport ambulance mapping"\n',
    "patient structural assertions",
)
CONTRACT_TEST.write_text(contract, encoding="utf-8")

changelog = CHANGELOG.read_text(encoding="utf-8")
entry = '''## [Unreleased]\n\n## [4.18.0] - 2026-07-18\n\n### Fixed\n- Mission Requirements now derives Ambulance demand from the live patient total even when MissionChief does not list ambulances in `#missing_text`.\n- Patient-derived demand reconciles with stated Ambulance requirements using the larger authoritative total instead of adding both values.\n- Unknown patient totals can no longer produce a false covered/green Matrix state.\n\n### Behaviour\n- One current patient requires one ordinary UK Ambulance by default.\n- On-site, responding and selected Ambulances use the existing exclusive vehicle-ID buckets and are never double-counted.\n- Patient counts update through the existing mission-window observer lifecycle, including bounded AJAX replacement recovery and mission-ID isolation.\n- The Ambulance row carries a compact `Patients` source marker and remains inside the existing Matrix panel.\n\n### Validation\n- Added deterministic singular/plural parsing, zero/unknown state, stated-demand reconciliation, live capacity, transition and mission-navigation fixtures.\n\n'''
changelog = replace_once(changelog, "## [Unreleased]\n\n", entry, "changelog entry")
CHANGELOG.write_text(changelog, encoding="utf-8")

DOC.write_text(
    "# Issue #181 — Patient-derived ambulance demand contract\n\n"
    "The Mission Requirements Matrix treats the live patient total as an independent UK ambulance-demand authority. One current patient requires one ordinary Ambulance by default. The implementation reads `#patient_button_text` / `#patient_button_form`, preferring numeric attributes and the patient-total `<strong>` element before bounded text parsing.\n\n"
    "Patient demand and MissionChief's stated Ambulance requirement are reconciled with `max(patient total, reconstructed live requirement, catalogue baseline)`. They are never summed blindly. Type 5 remains the conservative transport-Ambulance mapping; non-transport medical responders are excluded.\n\n"
    "The existing Selected, Responding and On-site vehicle-ID buckets remain exclusive. Unknown patient totals keep the row unresolved and prevent a green Matrix state. A 1.4-second same-mission transition cache covers temporary AJAX replacement, is isolated by mission ID and expires without polling.\n\n"
    "The feature adds no second panel and performs no vehicle selection, dispatch or patient transport. Desktop, Tablet and iOS use the existing Matrix layout, with a compact `Patients` source marker on the Ambulance row.\n",
    encoding="utf-8",
)

help = HELP_INDEX.read_text(encoding="utf-8")
help = help.replace("Toolkit v4.17.0", "Toolkit v4.18.0")
HELP_INDEX.write_text(help, encoding="utf-8")
help_manifest = json.loads(HELP_MANIFEST.read_text(encoding="utf-8"))
help_manifest["guideVersion"] = VERSION
help_manifest["toolkitVersion"] = VERSION
help_manifest["updated"] = "2026-07-18"
help_manifest["runtimeGuidePatch"] = "Toolkit v4.18.0 adds patient-derived Ambulance demand to Mission Requirements, with live patient lifecycle reconciliation and no double counting against stated requirements."
HELP_MANIFEST.write_text(json.dumps(help_manifest, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")

DIAGNOSTIC.unlink(missing_ok=True)

source = SOURCE.read_text(encoding="utf-8")
DIST_USER.write_text(source, encoding="utf-8")
DIST_TEXT.write_text(source, encoding="utf-8")
digest = hashlib.sha256(source.encode("utf-8")).hexdigest()
DIST_SUMS.write_text(
    f"{digest}  MissionChief_Map_Command_Toolkit.user.js\n{digest}  MissionChief_Map_Command_Toolkit.txt\n",
    encoding="utf-8",
)
manifest = json.loads(DIST_MANIFEST.read_text(encoding="utf-8"))
manifest["version"] = VERSION
manifest["sha256"] = digest
manifest["bytes"] = len(source.encode("utf-8"))
manifest["lines"] = len(source.splitlines())
manifest["metadata"]["runtimeVersion"] = VERSION
manifest["metadata"]["warnings"] = []
manifest["baselineHashMatch"] = None
manifest["distributionStatus"] = "dry-run-not-yet-greasyfork-source"
DIST_MANIFEST.write_text(json.dumps(manifest, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")

subprocess.run(["node", "--check", str(SOURCE)], cwd=ROOT, check=True)
subprocess.run(["node", str(RUNTIME_TEST)], cwd=ROOT, check=True)
subprocess.run(["python3", str(CONTRACT_TEST)], cwd=ROOT, check=True)
assert SOURCE.read_bytes() == DIST_USER.read_bytes() == DIST_TEXT.read_bytes()
print(f"Issue #181 v{VERSION} candidate SHA-256: {digest}")
