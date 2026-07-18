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
SETTINGS_FIXTURE = ROOT / ".github" / "fixtures" / "settings-ui-contract.json"
SETTINGS_TEST = ROOT / ".github" / "scripts" / "test_settings_ui_contract.py"
MISSION_CONTRACT = ROOT / ".github" / "scripts" / "test_mission_requirements_contract.py"
CUSTOM_RUNTIME = ROOT / ".github" / "scripts" / "test_custom_vehicle_badges_runtime.js"
CUSTOM_CONTRACT = ROOT / ".github" / "scripts" / "test_custom_vehicle_badges_contract.py"
DOC = ROOT / "docs" / "issue-176-custom-vehicle-badges-contract.md"
PREVIOUS = "4.16.4"
VERSION = "4.17.0"


def replace_once(text: str, old: str, new: str, label: str) -> str:
    count = text.count(old)
    if count != 1:
        raise AssertionError(f"{label}: expected one match, found {count}")
    return text.replace(old, new, 1)


def insert_after_last(text: str, needle: str, addition: str, label: str) -> str:
    index = text.rfind(needle)
    if index < 0:
        raise AssertionError(f"{label}: anchor not found")
    end = index + len(needle)
    return text[:end] + addition + text[end:]


source = SOURCE.read_text(encoding="utf-8")
source = replace_once(source, f"// @version      {PREVIOUS}", f"// @version      {VERSION}", "metadata version")
source = replace_once(source, f"        version: '{PREVIOUS}',", f"        version: '{VERSION}',", "runtime version")
source = replace_once(
    source,
    "        missionRequirementsDocumentStyleId: 'mcms-mission-requirements-document-style',",
    "        missionRequirementsDocumentStyleId: 'mcms-mission-requirements-document-style',\n        customVehicleBadgeStyleId: 'mcms-custom-vehicle-badge-style',",
    "custom badge style identifier",
)
source = replace_once(
    source,
    "    const missionRequirementsRecords = new Map();",
    "    const missionRequirementsRecords = new Map();\n"
    "    let customVehicleBadgeScanTimer = null;\n"
    "    let customVehicleBadgeRefreshPromise = null;\n"
    "    let customVehicleBadgeFeatureInstalled = false;\n"
    "    const customVehicleBadgeObservedDocuments = new WeakSet();\n"
    "    const customVehicleBadgeObservedFrames = new WeakSet();\n"
    "    const customVehicleClassificationCache = new Map();\n"
    "    let customVehicleClassificationRevision = -1;",
    "custom badge runtime state",
)
source = replace_once(
    source,
    "        missionRequirements: true,",
    "        missionRequirements: true,\n        customVehicleBadges: true,",
    "default custom badge state",
)
source = replace_once(
    source,
    "        merged.autoLoadAllVehicles = merged.autoLoadAllVehicles === true;",
    "        merged.autoLoadAllVehicles = merged.autoLoadAllVehicles === true;\n        merged.customVehicleBadges = merged.customVehicleBadges !== false;",
    "normalise custom badge state",
)

module_anchor = '''    function normaliseVehicleApiPayload(payload) {
        if (Array.isArray(payload)) return payload.filter(item => item && typeof item === 'object');
        if (Array.isArray(payload?.result)) return payload.result.filter(item => item && typeof item === 'object');
        if (payload && typeof payload === 'object') return Object.values(payload).filter(item => item && typeof item === 'object');
        return [];
    }
'''
module_code = r'''

    // CUSTOM VEHICLE BADGES START
    const CUSTOM_VEHICLE_BADGE_SELECTOR = '[data-mcms-custom-vehicle-badge="1"]';
    const CUSTOM_VEHICLE_AVAILABLE_SELECTOR = [
        '#vehicle_show_table_body_all .vehicle_checkbox',
        '#vehicle_show_table_body_all [vehicle_id]',
        '#vehicle_show_table_body_all [data-vehicle-id]',
        '#vehicle_show_table_body_all [data-vehicle_id]',
        '#occupied .vehicle_checkbox',
        '#occupied [vehicle_id]',
        '#occupied [data-vehicle-id]',
        '#occupied [data-vehicle_id]'
    ].join(', ');
    const CUSTOM_VEHICLE_ROW_SELECTOR = 'tr, li, .vehicle_select_table_tr, .vehicle_select_table_body_tr, .vehicle-row, .vehicle_row, .vehicle';

    function customVehicleCategoryText(value) {
        return String(value ?? '').replace(/\s+/g, ' ').trim();
    }

    function customVehicleClassificationFromRecord(record) {
        if (!record || typeof record !== 'object') return null;
        const vehicleId = vehicleRecordId(record);
        const category = customVehicleCategoryText(
            record.vehicle_type_caption
            ?? record.vehicleTypeCaption
            ?? record.own_vehicle_category
            ?? record.ownVehicleCategory
        );
        if (!vehicleId || !category) return null;
        const baseTypeRaw = record.vehicle_type ?? record.vehicleType ?? record.vehicle_type_id ?? record.vehicleTypeId;
        const baseTypeId = Number.isFinite(Number(baseTypeRaw)) ? Number(baseTypeRaw) : null;
        const locked = Boolean(
            record.ignore_aao
            ?? record.ignoreAao
            ?? record.only_dispatch_as_own_vehicle_class
            ?? record.onlyDispatchAsOwnVehicleClass
        );
        return Object.freeze({ vehicleId: String(vehicleId), category, baseTypeId, locked });
    }

    function rebuildCustomVehicleClassificationCache() {
        customVehicleClassificationCache.clear();
        for (const record of personalVehicleApiCache.values()) {
            const classification = customVehicleClassificationFromRecord(record);
            if (classification) customVehicleClassificationCache.set(classification.vehicleId, classification);
        }
        customVehicleClassificationRevision = vehicleDataRevision;
        return customVehicleClassificationCache;
    }

    function customVehicleClassificationForId(vehicleId) {
        const key = String(vehicleId ?? '').trim();
        if (!key) return null;
        if (customVehicleClassificationRevision !== vehicleDataRevision) rebuildCustomVehicleClassificationCache();
        return customVehicleClassificationCache.get(key) || null;
    }

    const customVehicleClassificationApi = Object.freeze({
        get(vehicleId) {
            const classification = customVehicleClassificationForId(vehicleId);
            return classification ? { ...classification } : null;
        },
        has(vehicleId) {
            return Boolean(customVehicleClassificationForId(vehicleId));
        },
        entries() {
            if (customVehicleClassificationRevision !== vehicleDataRevision) rebuildCustomVehicleClassificationCache();
            return Array.from(customVehicleClassificationCache.entries(), ([vehicleId, value]) => [vehicleId, { ...value }]);
        },
        get revision() {
            return customVehicleClassificationRevision;
        }
    });

    function customVehicleBadgeVehicleId(row) {
        if (!row) return '';
        const checkbox = row.matches?.('.vehicle_checkbox')
            ? row
            : row.querySelector?.('.vehicle_checkbox, input[vehicle_id], input[data-vehicle-id], input[data-vehicle_id]');
        const resolved = missionRequirementsVehicleId(checkbox || row);
        if (Number.isFinite(Number(resolved)) && Number(resolved) >= 0) return String(Number(resolved));
        const link = row.matches?.('a[href*="/vehicles/"]') ? row : row.querySelector?.('a[href*="/vehicles/"]');
        const match = String(link?.getAttribute?.('href') || link?.href || '').match(/\/vehicles\/(\d+)(?:\/|$)/u);
        return match?.[1] || '';
    }

    function customVehicleBadgeRows(doc) {
        const rows = new Set();
        let nodes = [];
        try { nodes = Array.from(doc?.querySelectorAll?.(CUSTOM_VEHICLE_AVAILABLE_SELECTOR) || []); } catch (err) {}
        for (const node of nodes) {
            const row = node?.closest?.(CUSTOM_VEHICLE_ROW_SELECTOR) || node?.parentElement || node;
            if (row) rows.add(row);
        }
        return Array.from(rows);
    }

    function customVehicleBadgeHost(row) {
        if (!row) return null;
        const checkbox = row.matches?.('.vehicle_checkbox')
            ? row
            : row.querySelector?.('.vehicle_checkbox, input[vehicle_id], input[data-vehicle-id], input[data-vehicle_id]');
        const directLabel = checkbox?.closest?.('label');
        if (directLabel) return directLabel;
        if (checkbox?.id) {
            for (const label of Array.from(row.querySelectorAll?.('label') || [])) {
                if (String(label.getAttribute?.('for') || label.htmlFor || '') === String(checkbox.id)) return label;
            }
        }
        return row.querySelector?.('.vehicle_caption, .vehicle-name, .vehicle_name, [data-vehicle-caption], a[href*="/vehicles/"]')
            || checkbox?.parentElement
            || row;
    }

    function customVehicleBadgeRemoveRow(row) {
        if (!row) return;
        try { row.querySelectorAll?.(CUSTOM_VEHICLE_BADGE_SELECTOR).forEach(badge => badge.remove?.()); } catch (err) {}
        try {
            delete row.dataset.mcmsCustomVehicleCategory;
            delete row.dataset.mcmsCustomVehicleLocked;
            delete row.dataset.mcmsCustomVehicleId;
        } catch (err) {
            row.removeAttribute?.('data-mcms-custom-vehicle-category');
            row.removeAttribute?.('data-mcms-custom-vehicle-locked');
            row.removeAttribute?.('data-mcms-custom-vehicle-id');
        }
    }

    function customVehicleBadgeApplyRow(row) {
        if (!row) return null;
        const vehicleId = customVehicleBadgeVehicleId(row);
        const classification = customVehicleClassificationForId(vehicleId);
        if (!classification) {
            customVehicleBadgeRemoveRow(row);
            return null;
        }
        const host = customVehicleBadgeHost(row);
        const doc = row.ownerDocument || host?.ownerDocument || document;
        if (!host?.appendChild || !doc?.createElement) return null;
        const badges = Array.from(row.querySelectorAll?.(CUSTOM_VEHICLE_BADGE_SELECTOR) || []);
        let badge = badges.shift() || null;
        badges.forEach(duplicate => duplicate.remove?.());
        if (!badge) {
            badge = doc.createElement('span');
            badge.setAttribute('data-mcms-custom-vehicle-badge', '1');
            badge.setAttribute('aria-label', `Own Vehicle Category: ${classification.category}`);
        }
        badge.textContent = `[${classification.category}]`;
        badge.title = `Own Vehicle Category: ${classification.category}`;
        badge.dataset.mcmsTheme = state.uiTheme;
        badge.dataset.mcmsVehicleId = classification.vehicleId;
        badge.dataset.mcmsLocked = classification.locked ? 'true' : 'false';
        host.appendChild(badge);
        row.dataset.mcmsCustomVehicleCategory = classification.category;
        row.dataset.mcmsCustomVehicleLocked = classification.locked ? 'true' : 'false';
        row.dataset.mcmsCustomVehicleId = classification.vehicleId;
        return badge;
    }

    function customVehicleBadgeDocumentCss() {
        return `
${CUSTOM_VEHICLE_BADGE_SELECTOR}{display:inline-flex!important;align-items:center!important;vertical-align:middle!important;max-width:min(240px,45vw)!important;margin-inline-start:4px!important;padding:1px 4px!important;border:1px solid rgba(116,190,255,.48)!important;border-radius:999px!important;background:rgba(24,91,140,.20)!important;color:#d8efff!important;font:800 9.5px/1.25 Arial,sans-serif!important;letter-spacing:.04px!important;white-space:nowrap!important;overflow:hidden!important;text-overflow:ellipsis!important;pointer-events:none!important;box-sizing:border-box!important}
${CUSTOM_VEHICLE_BADGE_SELECTOR}[data-mcms-theme="mapCommand"]{border-color:rgba(103,190,255,.52)!important;background:rgba(34,107,158,.22)!important;color:#d8f1ff!important}
${CUSTOM_VEHICLE_BADGE_SELECTOR}[data-mcms-theme="cyberpunk"]{border-color:rgba(0,238,255,.58)!important;background:rgba(0,238,255,.12)!important;color:#8ff8ff!important}
${CUSTOM_VEHICLE_BADGE_SELECTOR}[data-mcms-theme="fallout4"]{border-color:rgba(164,234,101,.55)!important;background:rgba(102,180,68,.14)!important;color:#d8ffad!important}
${CUSTOM_VEHICLE_BADGE_SELECTOR}[data-mcms-theme="umbrella"]{border-color:rgba(214,39,50,.62)!important;background:rgba(214,39,50,.16)!important;color:#fff1f2!important}
${CUSTOM_VEHICLE_BADGE_SELECTOR}[data-mcms-theme="factorio"]{border-color:rgba(240,164,74,.58)!important;background:rgba(240,164,74,.14)!important;color:#ffe1b7!important;border-radius:3px!important}
${CUSTOM_VEHICLE_BADGE_SELECTOR}[data-mcms-theme="bond007"]{border-color:rgba(217,189,119,.58)!important;background:rgba(217,189,119,.13)!important;color:#f6e9c7!important}
${CUSTOM_VEHICLE_BADGE_SELECTOR}[data-mcms-theme="hyrule"]{border-color:rgba(217,183,90,.58)!important;background:rgba(110,230,214,.12)!important;color:#e8fff8!important}
@media(max-width:767px){${CUSTOM_VEHICLE_BADGE_SELECTOR}{max-width:42vw!important;margin-inline-start:3px!important;padding:1px 3px!important;font-size:8.5px!important}}
`;
    }

    function ensureCustomVehicleBadgeDocumentStyle(doc) {
        if (!doc?.head?.appendChild || doc.getElementById?.(SCRIPT.customVehicleBadgeStyleId)) return;
        const style = doc.createElement('style');
        style.id = SCRIPT.customVehicleBadgeStyleId;
        style.textContent = customVehicleBadgeDocumentCss();
        doc.head.appendChild(style);
    }

    function customVehicleBadgeDocumentContexts() {
        const docs = [];
        const seen = new Set();
        const add = (doc, depth = 0) => {
            if (!doc || seen.has(doc) || depth > 3) return;
            seen.add(doc);
            docs.push(doc);
            let frames = [];
            try { frames = Array.from(doc.querySelectorAll?.('iframe, frame') || []); } catch (err) {}
            for (const frame of frames) {
                try { add(frame.contentDocument || frame.contentWindow?.document, depth + 1); } catch (err) {}
            }
        };
        add(document);
        return docs;
    }

    function customVehicleBadgeMutationRelevant(mutation) {
        const target = mutation?.target;
        if (target?.closest?.(CUSTOM_VEHICLE_BADGE_SELECTOR)) return false;
        const selector = '#vehicle_show_table_body_all, #occupied, .vehicle_checkbox, [vehicle_id], [data-vehicle-id], [data-vehicle_id], a[href*="/vehicles/"]';
        if (target?.matches?.(selector) || target?.closest?.('#vehicle_show_table_body_all, #occupied')) return true;
        for (const node of Array.from(mutation?.addedNodes || [])) {
            if (node?.nodeType !== 1) continue;
            if (node.matches?.(selector) || node.querySelector?.(selector)) return true;
        }
        return false;
    }

    function scheduleCustomVehicleBadgeScan(delay = 35) {
        runtimeClearTimeout(customVehicleBadgeScanTimer);
        customVehicleBadgeScanTimer = runtimeSetTimeout(scanCustomVehicleBadges, Math.max(0, Number(delay) || 0));
    }

    function observeCustomVehicleBadgeFrame(frame) {
        if (!frame || customVehicleBadgeObservedFrames.has(frame)) return;
        customVehicleBadgeObservedFrames.add(frame);
        runtimeListen(frame, 'load', () => scheduleCustomVehicleBadgeScan(20));
    }

    function observeCustomVehicleBadgeDocument(doc) {
        if (!doc) return;
        ensureCustomVehicleBadgeDocumentStyle(doc);
        try { doc.querySelectorAll?.('iframe, frame').forEach(observeCustomVehicleBadgeFrame); } catch (err) {}
        if (customVehicleBadgeObservedDocuments.has(doc)) return;
        customVehicleBadgeObservedDocuments.add(doc);
        const root = doc.documentElement || doc.body;
        const Observer = doc.defaultView?.MutationObserver || pageWindow.MutationObserver || MutationObserver;
        if (!root || typeof Observer !== 'function') return;
        const observer = runtimeTrackObserver(new Observer(mutations => {
            if (!mutations.some(customVehicleBadgeMutationRelevant)) return;
            try { doc.querySelectorAll?.('iframe, frame').forEach(observeCustomVehicleBadgeFrame); } catch (err) {}
            scheduleCustomVehicleBadgeScan(25);
        }));
        observer.observe(root, {
            childList: true,
            subtree: true,
            attributes: true,
            attributeFilter: ['id', 'class', 'vehicle_id', 'data-vehicle-id', 'data-vehicle_id', 'vehicle_type_id', 'data-vehicle-type-id', 'data-vehicle_type_id']
        });
    }

    function clearCustomVehicleBadges() {
        runtimeClearTimeout(customVehicleBadgeScanTimer);
        customVehicleBadgeScanTimer = null;
        for (const doc of customVehicleBadgeDocumentContexts()) {
            try { doc.querySelectorAll?.(CUSTOM_VEHICLE_BADGE_SELECTOR).forEach(badge => badge.remove?.()); } catch (err) {}
            try {
                doc.querySelectorAll?.('[data-mcms-custom-vehicle-category], [data-mcms-custom-vehicle-id]').forEach(row => {
                    row.removeAttribute?.('data-mcms-custom-vehicle-category');
                    row.removeAttribute?.('data-mcms-custom-vehicle-locked');
                    row.removeAttribute?.('data-mcms-custom-vehicle-id');
                });
            } catch (err) {}
        }
    }

    function scanCustomVehicleBadges() {
        customVehicleBadgeScanTimer = null;
        const docs = customVehicleBadgeDocumentContexts();
        if (!state.customVehicleBadges) {
            clearCustomVehicleBadges();
            return 0;
        }
        let rendered = 0;
        for (const doc of docs) {
            observeCustomVehicleBadgeDocument(doc);
            for (const row of customVehicleBadgeRows(doc)) {
                if (customVehicleBadgeApplyRow(row)) rendered += 1;
            }
        }
        if (!vehicleApiReady && !customVehicleBadgeRefreshPromise) {
            customVehicleBadgeRefreshPromise = Promise.resolve(refreshPersonalVehicleData(false))
                .then(ok => { if (ok) scheduleCustomVehicleBadgeScan(0); return ok; })
                .catch(() => false)
                .finally(() => { customVehicleBadgeRefreshPromise = null; });
        }
        return rendered;
    }

    function installCustomVehicleBadges() {
        if (!customVehicleBadgeFeatureInstalled) {
            customVehicleBadgeFeatureInstalled = true;
            runtime.customVehicleClassifications = customVehicleClassificationApi;
            try { pageWindow.__MCMS_CUSTOM_VEHICLE_CLASSIFICATIONS__ = customVehicleClassificationApi; } catch (err) {}
            runtimeOnCleanup(() => {
                clearCustomVehicleBadges();
                for (const doc of customVehicleBadgeDocumentContexts()) doc.getElementById?.(SCRIPT.customVehicleBadgeStyleId)?.remove?.();
                if (pageWindow.__MCMS_CUSTOM_VEHICLE_CLASSIFICATIONS__ === customVehicleClassificationApi) {
                    try { delete pageWindow.__MCMS_CUSTOM_VEHICLE_CLASSIFICATIONS__; } catch (err) { pageWindow.__MCMS_CUSTOM_VEHICLE_CLASSIFICATIONS__ = null; }
                }
            });
        }
        scheduleCustomVehicleBadgeScan(0);
        if (!vehicleApiReady && !customVehicleBadgeRefreshPromise) {
            customVehicleBadgeRefreshPromise = Promise.resolve(refreshPersonalVehicleData(false))
                .then(ok => { if (ok) scheduleCustomVehicleBadgeScan(0); return ok; })
                .catch(() => false)
                .finally(() => { customVehicleBadgeRefreshPromise = null; });
        }
    }

    if (pageWindow.__MCMS_TEST_HOOKS__ && typeof pageWindow.__MCMS_TEST_HOOKS__ === 'object') {
        pageWindow.__MCMS_TEST_HOOKS__.customVehicleBadges = Object.freeze({
            classificationFromRecord: customVehicleClassificationFromRecord,
            rebuildCache: rebuildCustomVehicleClassificationCache,
            classificationForId: customVehicleClassificationForId,
            vehicleId: customVehicleBadgeVehicleId,
            rows: customVehicleBadgeRows,
            host: customVehicleBadgeHost,
            applyRow: customVehicleBadgeApplyRow,
            removeRow: customVehicleBadgeRemoveRow
        });
    }
    // CUSTOM VEHICLE BADGES END
'''
source = replace_once(source, module_anchor, module_anchor + module_code, "custom badge module")

source = replace_once(
    source,
    "            vehicleApiLastError = 0;\n            vehicleDataRevision += 1;",
    "            vehicleApiLastError = 0;\n            vehicleDataRevision += 1;\n            rebuildCustomVehicleClassificationCache();\n            scheduleCustomVehicleBadgeScan(0);",
    "vehicle API badge refresh hook",
)
source = replace_once(
    source,
    "        if (feature === 'missionRequirements') state.missionRequirements = !state.missionRequirements;",
    "        if (feature === 'missionRequirements') state.missionRequirements = !state.missionRequirements;\n        if (feature === 'customVehicleBadges') state.customVehicleBadges = !state.customVehicleBadges;",
    "custom badge toggle route",
)
source = replace_once(
    source,
    "        if (feature === 'missionRequirements') {\n            if (state.missionRequirements) installMissionRequirementsWindows();\n            else clearMissionRequirementsPanels();\n            showToast(state.missionRequirements ? 'Mission Requirements on' : 'Mission Requirements off');\n        }",
    "        if (feature === 'missionRequirements') {\n            if (state.missionRequirements) installMissionRequirementsWindows();\n            else clearMissionRequirementsPanels();\n            showToast(state.missionRequirements ? 'Mission Requirements on' : 'Mission Requirements off');\n        }\n        if (feature === 'customVehicleBadges') {\n            if (state.customVehicleBadges) installCustomVehicleBadges();\n            else clearCustomVehicleBadges();\n            showToast(state.customVehicleBadges ? 'Custom Vehicle Badges on' : 'Custom Vehicle Badges off');\n        }",
    "custom badge toggle effect",
)
source = replace_once(
    source,
    "                    ${makeToggleButton('missionRequirements', '≡', 'Requirements', 'Show a live MissionChief requirements matrix above dispatch controls.')}",
    "                    ${makeToggleButton('missionRequirements', '≡', 'Requirements', 'Show a live MissionChief requirements matrix above dispatch controls.')}\n                    ${makeToggleButton('customVehicleBadges', '▣', 'Custom Vehicle Badges', 'Show custom vehicle categories in available vehicles list.')}",
    "custom badge menu toggle",
)

map_pattern = re.compile(r"(?P<indent>\s*)missionRequirements:\s*state\.missionRequirements,(?P<newline>\r?\n)")
source, map_count = map_pattern.subn(
    lambda match: f"{match.group('indent')}missionRequirements: state.missionRequirements,{match.group('newline')}"
                  f"{match.group('indent')}customVehicleBadges: state.customVehicleBadges,{match.group('newline')}",
    source,
)
if map_count != 1:
    raise AssertionError(f"toggle UI map: expected one missionRequirements entry, found {map_count}")

source = insert_after_last(
    source,
    "        installMissionRequirementsWindows();",
    "\n        installCustomVehicleBadges();",
    "startup custom badge installation",
)
SOURCE.write_text(source, encoding="utf-8")

runtime_test = r'''#!/usr/bin/env node
"use strict";
const fs = require("node:fs");
const path = require("node:path");
const vm = require("node:vm");
const assert = require("node:assert/strict");

const root = path.resolve(__dirname, "../..");
const source = fs.readFileSync(path.join(root, "src/MissionChief_Map_Command_Toolkit.user.js"), "utf8");
const startMarker = "    // CUSTOM VEHICLE BADGES START";
const endMarker = "    // CUSTOM VEHICLE BADGES END";
const start = source.indexOf(startMarker);
const end = source.indexOf(endMarker, start);
assert(start >= 0 && end > start, "custom badge source block is missing");
const block = source.slice(start, end + endMarker.length);

class FakeClassList {
    constructor(owner) { this.owner = owner; this.values = new Set(); }
    add(...values) { values.forEach(value => this.values.add(String(value))); this.owner.className = Array.from(this.values).join(" "); }
    contains(value) { return this.values.has(String(value)); }
}

class FakeElement {
    constructor(tagName, ownerDocument) {
        this.nodeType = 1;
        this.tagName = String(tagName || "div").toUpperCase();
        this.ownerDocument = ownerDocument;
        this.children = [];
        this.parentElement = null;
        this.parentNode = null;
        this.attributes = new Map();
        this.dataset = {};
        this.classList = new FakeClassList(this);
        this.className = "";
        this.id = "";
        this.value = "";
        this.textContent = "";
        this.title = "";
        this.isConnected = true;
    }
    setAttribute(name, value) {
        const text = String(value);
        this.attributes.set(String(name), text);
        if (name === "id") this.id = text;
        if (name === "class") { this.className = text; text.split(/\s+/).filter(Boolean).forEach(value => this.classList.values.add(value)); }
        if (name.startsWith("data-")) {
            const key = name.slice(5).replace(/-([a-z])/g, (_, letter) => letter.toUpperCase());
            this.dataset[key] = text;
        }
    }
    getAttribute(name) { return this.attributes.has(String(name)) ? this.attributes.get(String(name)) : null; }
    removeAttribute(name) {
        this.attributes.delete(String(name));
        if (String(name).startsWith("data-")) {
            const key = String(name).slice(5).replace(/-([a-z])/g, (_, letter) => letter.toUpperCase());
            delete this.dataset[key];
        }
    }
    appendChild(child) {
        if (child.parentElement) child.parentElement.children = child.parentElement.children.filter(item => item !== child);
        child.parentElement = this;
        child.parentNode = this;
        child.ownerDocument ||= this.ownerDocument;
        this.children.push(child);
        return child;
    }
    insertBefore(child, before) {
        if (!before || !this.children.includes(before)) return this.appendChild(child);
        if (child.parentElement) child.parentElement.children = child.parentElement.children.filter(item => item !== child);
        child.parentElement = this;
        child.parentNode = this;
        const index = this.children.indexOf(before);
        this.children.splice(index, 0, child);
        return child;
    }
    remove() {
        if (this.parentElement) this.parentElement.children = this.parentElement.children.filter(item => item !== this);
        this.parentElement = null;
        this.parentNode = null;
        this.isConnected = false;
    }
    matches(selector) {
        return String(selector).split(",").some(raw => {
            const part = raw.trim();
            if (!part) return false;
            if (part === "label") return this.tagName === "LABEL";
            if (part === "tr") return this.tagName === "TR";
            if (part === "li") return this.tagName === "LI";
            if (part === "iframe") return this.tagName === "IFRAME";
            if (part === "frame") return this.tagName === "FRAME";
            if (part === ".vehicle_checkbox") return this.classList.contains("vehicle_checkbox");
            if (part.startsWith(".")) return this.classList.contains(part.slice(1));
            if (part === '[data-mcms-custom-vehicle-badge="1"]') return this.getAttribute("data-mcms-custom-vehicle-badge") === "1";
            if (part === "[vehicle_id]") return this.getAttribute("vehicle_id") !== null;
            if (part === "[data-vehicle-id]") return this.getAttribute("data-vehicle-id") !== null;
            if (part === "[data-vehicle_id]") return this.getAttribute("data-vehicle_id") !== null;
            if (part.startsWith('a[href*="/vehicles/"]')) return this.tagName === "A" && String(this.getAttribute("href") || "").includes("/vehicles/");
            if (part.startsWith("input")) return this.tagName === "INPUT";
            if (part.startsWith("#")) return this.id === part.slice(1);
            if (part === "[data-vehicle-caption]") return this.getAttribute("data-vehicle-caption") !== null;
            return false;
        });
    }
    closest(selector) {
        let current = this;
        while (current) {
            if (current.matches(selector)) return current;
            current = current.parentElement;
        }
        return null;
    }
    querySelectorAll(selector) {
        const result = [];
        const visit = node => {
            for (const child of node.children) {
                if (child.matches(selector)) result.push(child);
                visit(child);
            }
        };
        visit(this);
        return result;
    }
    querySelector(selector) { return this.querySelectorAll(selector)[0] || null; }
}

class FakeDocument {
    constructor() {
        this.defaultView = {};
        this.documentElement = new FakeElement("html", this);
        this.head = new FakeElement("head", this);
        this.body = new FakeElement("body", this);
        this.documentElement.appendChild(this.head);
        this.documentElement.appendChild(this.body);
    }
    createElement(tag) { return new FakeElement(tag, this); }
    querySelectorAll(selector) { return this.documentElement.querySelectorAll(selector); }
    querySelector(selector) { return this.documentElement.querySelector(selector); }
    getElementById(id) { return [this.documentElement, ...this.documentElement.querySelectorAll("#" + id)].find(node => node.id === id) || null; }
}

const document = new FakeDocument();
const personalVehicleApiCache = new Map();
const cleanup = [];
const pageWindow = { __MCMS_TEST_HOOKS__: {}, MutationObserver: class { observe() {} disconnect() {} } };
const context = {
    console,
    Promise,
    Map,
    Set,
    WeakSet,
    Object,
    Array,
    String,
    Number,
    Boolean,
    Math,
    document,
    pageWindow,
    MutationObserver: pageWindow.MutationObserver,
    personalVehicleApiCache,
    customVehicleClassificationCache: new Map(),
    customVehicleClassificationRevision: -1,
    customVehicleBadgeScanTimer: null,
    customVehicleBadgeRefreshPromise: null,
    customVehicleBadgeFeatureInstalled: false,
    customVehicleBadgeObservedDocuments: new WeakSet(),
    customVehicleBadgeObservedFrames: new WeakSet(),
    vehicleDataRevision: 0,
    vehicleApiReady: true,
    vehicleApiFetchPromise: null,
    state: { uiTheme: "mapCommand", customVehicleBadges: true },
    SCRIPT: { customVehicleBadgeStyleId: "mcms-custom-vehicle-badge-style" },
    runtime: {},
    vehicleRecordId(record) { return String(record?.id ?? record?.vehicle_id ?? "") || null; },
    missionRequirementsVehicleId(element) {
        const direct = Number.parseInt(element?.value ?? element?.getAttribute?.("value") ?? element?.dataset?.vehicleId, 10);
        return Number.isFinite(direct) ? direct : -1;
    },
    refreshPersonalVehicleData() { return Promise.resolve(true); },
    runtimeClearTimeout() {},
    runtimeSetTimeout(callback) { callback(); return 1; },
    runtimeTrackObserver(observer) { return observer; },
    runtimeListen() {},
    runtimeOnCleanup(callback) { cleanup.push(callback); return callback; },
    setTimeout,
    clearTimeout,
};
vm.createContext(context);
vm.runInContext(block, context, { filename: "custom-vehicle-badges.js" });
const api = pageWindow.__MCMS_TEST_HOOKS__.customVehicleBadges;
assert(api, "test API was not exposed");

personalVehicleApiCache.set("101", { id: 101, vehicle_type: 0, vehicle_type_caption: " Railway Police Officer ", ignore_aao: true });
context.vehicleDataRevision = 1;
api.rebuildCache();
assert.deepEqual(JSON.parse(JSON.stringify(api.classificationForId("101"))), {
    vehicleId: "101",
    category: "Railway Police Officer",
    baseTypeId: 0,
    locked: true,
});

function makeRow(vehicleId) {
    const row = new FakeElement("tr", document);
    const label = new FakeElement("label", document);
    const checkbox = new FakeElement("input", document);
    checkbox.classList.add("vehicle_checkbox");
    checkbox.value = String(vehicleId);
    label.appendChild(checkbox);
    row.appendChild(label);
    document.body.appendChild(row);
    return { row, label, checkbox };
}

const specialist = makeRow(101);
let badge = api.applyRow(specialist.row);
assert(badge, "specialist badge was not rendered");
assert.equal(badge.textContent, "[Railway Police Officer]");
assert.equal(specialist.row.querySelectorAll('[data-mcms-custom-vehicle-badge="1"]').length, 1);
assert.equal(specialist.row.dataset.mcmsCustomVehicleCategory, "Railway Police Officer");
assert.equal(specialist.row.dataset.mcmsCustomVehicleLocked, "true");
assert.equal(badge.parentElement, specialist.label, "badge was not placed beside the native label");

badge = api.applyRow(specialist.row);
assert.equal(specialist.row.querySelectorAll('[data-mcms-custom-vehicle-badge="1"]').length, 1, "repeat scan duplicated badge");
assert.equal(badge.textContent, "[Railway Police Officer]");

personalVehicleApiCache.set("102", { id: 102, vehicle_type: 0, vehicle_type_caption: null, ignore_aao: false });
context.vehicleDataRevision = 2;
api.rebuildCache();
const ordinary = makeRow(102);
assert.equal(api.applyRow(ordinary.row), null, "ordinary IRV received a badge");
assert.equal(ordinary.row.querySelectorAll('[data-mcms-custom-vehicle-badge="1"]').length, 0);

const replacement = makeRow(101);
badge = api.applyRow(replacement.row);
assert(badge, "replacement AJAX row did not receive badge");
assert.equal(replacement.row.querySelectorAll('[data-mcms-custom-vehicle-badge="1"]').length, 1);

personalVehicleApiCache.set("101", { id: 101, vehicle_type: 0, vehicle_type_caption: "", ignore_aao: true });
context.vehicleDataRevision = 3;
api.rebuildCache();
assert.equal(api.applyRow(specialist.row), null, "badge remained after category removal");
assert.equal(specialist.row.querySelectorAll('[data-mcms-custom-vehicle-badge="1"]').length, 0);
assert.equal(specialist.row.dataset.mcmsCustomVehicleCategory, undefined);

console.log("Custom Vehicle Badges runtime fixtures passed");
'''
CUSTOM_RUNTIME.write_text(runtime_test, encoding="utf-8")
CUSTOM_RUNTIME.chmod(0o755)

contract_test = r'''#!/usr/bin/env python3
"""Verify Custom Vehicle Badges against the canonical userscript and runtime fixture."""
from __future__ import annotations

import re
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
SOURCE = ROOT / "src" / "MissionChief_Map_Command_Toolkit.user.js"
DIST = ROOT / "dist" / "MissionChief_Map_Command_Toolkit.user.js"
RUNTIME = ROOT / ".github" / "scripts" / "test_custom_vehicle_badges_runtime.js"


def main() -> int:
    source = SOURCE.read_text(encoding="utf-8")
    assert source == DIST.read_text(encoding="utf-8"), "source/distribution parity failed"
    runtime = subprocess.run(["node", str(RUNTIME)], cwd=ROOT, text=True, capture_output=True)
    if runtime.stdout:
        print(runtime.stdout, end="")
    if runtime.returncode != 0:
        if runtime.stderr:
            print(runtime.stderr, end="")
        raise SystemExit("Custom Vehicle Badges runtime fixtures failed")

    markers = [
        "customVehicleBadgeStyleId: 'mcms-custom-vehicle-badge-style'",
        "customVehicleBadges: true",
        "merged.customVehicleBadges = merged.customVehicleBadges !== false",
        "function customVehicleClassificationFromRecord(record)",
        "record.vehicle_type_caption",
        "record.ignore_aao",
        "function rebuildCustomVehicleClassificationCache()",
        "function customVehicleClassificationForId(vehicleId)",
        "__MCMS_CUSTOM_VEHICLE_CLASSIFICATIONS__",
        "function customVehicleBadgeApplyRow(row)",
        "data-mcms-custom-vehicle-category",
        "function observeCustomVehicleBadgeDocument(doc)",
        "function installCustomVehicleBadges()",
        "function clearCustomVehicleBadges()",
        "${makeToggleButton('customVehicleBadges', '▣', 'Custom Vehicle Badges', 'Show custom vehicle categories in available vehicles list.')}",
        "if (feature === 'customVehicleBadges') state.customVehicleBadges = !state.customVehicleBadges",
        "customVehicleBadges: state.customVehicleBadges",
        "installCustomVehicleBadges();",
    ]
    compact = re.sub(r"\s+", "", source)
    missing = [marker for marker in markers if marker not in source and re.sub(r"\s+", "", marker) not in compact]
    assert not missing, f"Missing Custom Vehicle Badges markers: {missing}"
    assert source.count("function installCustomVehicleBadges()") == 1
    assert source.count("function customVehicleBadgeApplyRow(row)") == 1
    assert source.count("/api/vehicles") == 1, "feature must reuse the shared vehicle API request"
    module = source.split("// CUSTOM VEHICLE BADGES START", 1)[1].split("// CUSTOM VEHICLE BADGES END", 1)[0]
    assert ".click(" not in module and ".click?.(" not in module, "badge module must not dispatch or select vehicles"
    for theme in ["mapCommand", "cyberpunk", "fallout4", "umbrella", "factorio", "bond007", "hyrule"]:
        assert f'data-mcms-theme=\\"{theme}\\"' in module or f'data-mcms-theme="{theme}"' in module, f"theme missing: {theme}"
    assert "max-width:min(240px,45vw)" in re.sub(r"\s+", "", module)
    assert "@media(max-width:767px)" in re.sub(r"\s+", "", module)
    print("Custom Vehicle Badges contract passed")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
'''
CUSTOM_CONTRACT.write_text(contract_test, encoding="utf-8")
CUSTOM_CONTRACT.chmod(0o755)

mission_contract = MISSION_CONTRACT.read_text(encoding="utf-8")
mission_contract = replace_once(
    mission_contract,
    'RUNTIME_TEST = ROOT / ".github/scripts/test_mission_requirements_runtime.js"',
    'RUNTIME_TEST = ROOT / ".github/scripts/test_mission_requirements_runtime.js"\nCUSTOM_VEHICLE_BADGES_CONTRACT = ROOT / ".github/scripts/test_custom_vehicle_badges_contract.py"',
    "mission contract custom badge path",
)
mission_contract = replace_once(
    mission_contract,
    '    required_markers = [',
    '    custom_badges = subprocess.run(["python3", str(CUSTOM_VEHICLE_BADGES_CONTRACT)], cwd=ROOT, text=True, capture_output=True)\n'
    '    if custom_badges.stdout:\n'
    '        print(custom_badges.stdout, end="")\n'
    '    if custom_badges.returncode != 0:\n'
    '        if custom_badges.stderr:\n'
    '            print(custom_badges.stderr, end="")\n'
    '        raise SystemExit("Custom Vehicle Badges contract failed")\n\n'
    '    required_markers = [',
    "mission contract custom badge execution",
)
MISSION_CONTRACT.write_text(mission_contract, encoding="utf-8")

settings_test = SETTINGS_TEST.read_text(encoding="utf-8")
settings_test = replace_once(
    settings_test,
    'function clearMissionRequirementsPanels() {{ record("clearMissionRequirementsPanels"); }}',
    'function clearMissionRequirementsPanels() {{ record("clearMissionRequirementsPanels"); }}\n'
    'function installCustomVehicleBadges() {{ record("installCustomVehicleBadges"); }}\n'
    'function clearCustomVehicleBadges() {{ record("clearCustomVehicleBadges"); }}',
    "settings harness custom badge stubs",
)
SETTINGS_TEST.write_text(settings_test, encoding="utf-8")

settings_fixture = json.loads(SETTINGS_FIXTURE.read_text(encoding="utf-8"))
if "customVehicleBadges" not in settings_fixture["toggleRoutes"]:
    settings_fixture["toggleRoutes"].append("customVehicleBadges")
    settings_fixture["toggleRoutes"].sort()
settings_fixture["toggleStatePaths"]["customVehicleBadges"] = "customVehicleBadges"
SETTINGS_FIXTURE.write_text(json.dumps(settings_fixture, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")

changelog = CHANGELOG.read_text(encoding="utf-8")
entry = '''## [Unreleased]

## [4.17.0] - 2026-07-18

### Added
- Added **Custom Vehicle Badges**: Available Units now shows each vehicle's MissionChief Own Vehicle Category as a compact badge beside the native vehicle label, for example `IRV [Railway Police Officer]`.
- Added a stable read-only vehicle classification API keyed by vehicle ID for Mission Requirements Matrix capability matching.

### Behaviour
- Reuses the Toolkit's existing `/api/vehicles` cache and never performs a second vehicle-list request.
- Reapplies badges after MissionChief or LSSM replaces, filters or sorts the Available Units DOM, without duplicates or dispatch-side effects.
- Vehicles without an Own Vehicle Category remain unchanged.

### Validation
- Added fixture-backed classification, duplicate-prevention, category-removal and AJAX-row-replacement tests.

'''
changelog = replace_once(changelog, "## [Unreleased]\n\n", entry, "changelog entry")
CHANGELOG.write_text(changelog, encoding="utf-8")

DOC.write_text(
    "# Issue #176 — Custom Vehicle Badges contract\n\n"
    "Available Units retains MissionChief's native vehicle label and appends one compact Own Vehicle Category badge when `/api/vehicles` provides a non-empty `vehicle_type_caption`. Vehicles without a custom category are unchanged.\n\n"
    "Rows are resolved by stable vehicle ID through the same identity helper used by the Mission Requirements Matrix. The shared classification cache exposes category, base vehicle type and `ignore_aao` lock state without altering selection or dispatch behaviour.\n\n"
    "The feature observes normal AJAX dispatch windows, standalone mission tabs and accessible LSSM-modified document roots. Repeated scans are idempotent and replacement rows receive the badge automatically.\n\n"
    "The menu toggle is named **Custom Vehicle Badges** and is enabled by default. Its description is: **Show custom vehicle categories in available vehicles list.**\n",
    encoding="utf-8",
)

help_html = HELP_INDEX.read_text(encoding="utf-8").replace("Toolkit v4.16.4", "Toolkit v4.17.0")
HELP_INDEX.write_text(help_html, encoding="utf-8")
help_manifest = json.loads(HELP_MANIFEST.read_text(encoding="utf-8"))
help_manifest["guideVersion"] = VERSION
help_manifest["toolkitVersion"] = VERSION
help_manifest["updated"] = "2026-07-18"
help_manifest["runtimeGuidePatch"] = "Toolkit v4.17.0 adds Custom Vehicle Badges, showing compact Own Vehicle Category labels in Available Units and exposing the same vehicle-ID classification cache to the Mission Requirements Matrix."
HELP_MANIFEST.write_text(json.dumps(help_manifest, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")

for diagnostic in [
    ROOT / ".github" / "diagnostics" / "issue-176-source-map.txt",
    ROOT / ".github" / "diagnostics" / "issue-176-target-map.txt",
    ROOT / ".github" / "diagnostics" / "issue-176-final-map.txt",
]:
    diagnostic.unlink(missing_ok=True)

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
subprocess.run(["node", str(CUSTOM_RUNTIME)], cwd=ROOT, check=True)
subprocess.run(["python3", str(CUSTOM_CONTRACT)], cwd=ROOT, check=True)
subprocess.run(["python3", str(MISSION_CONTRACT)], cwd=ROOT, check=True)
subprocess.run(["python3", str(SETTINGS_TEST)], cwd=ROOT, check=True)
assert SOURCE.read_bytes() == DIST_USER.read_bytes() == DIST_TEXT.read_bytes()
print(f"Issue #176 v{VERSION} candidate SHA-256: {digest}")
