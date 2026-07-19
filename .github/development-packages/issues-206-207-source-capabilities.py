#!/usr/bin/env python3
from __future__ import annotations

import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
SOURCE = ROOT / "src" / "MissionChief_Map_Command_Toolkit.user.js"
s = SOURCE.read_text(encoding="utf-8")

def one(old, new, label):
    global s
    count = s.count(old)
    if count != 1:
        raise AssertionError(f"{label}: expected one match, found {count}")
    s = s.replace(old, new, 1)

def compact_js(value):
    return re.sub(r"\s*\n\s*", " ", value.strip())

def fn(name, next_name, new):
    global s
    start = s.index("    function " + name)
    end = s.index("    function " + next_name, start)
    s = s[:start] + compact_js(new) + "\n\n" + s[end:]

one('// @version      4.20.2','// @version      4.20.3','meta')
one("        version: '4.20.2',","        version: '4.20.3',",'runtime')
one("        { key: 'police-inspector-personnel', label: 'Police Inspector', aliases: ['Police Inspector', 'Police Inspectors'], group: 'staff', types: [], countable: false },",
"        { key: 'police-inspector-personnel', label: 'Police Inspector', aliases: ['Police Inspector', 'Police Inspectors'], group: 'staff', types: [], countable: false },\n        { key: 'railway-police-officer', label: 'Railway Police Officer', aliases: ['Railway Police Officer', 'Railway Police Officers'], group: 'staff', types: [], training: ['Railway Police Officer', 'Railway Police'], countable: true },",'definition')

fn('missionRequirementsVehicleType','missionRequirementsVehicleId',r'''    function missionRequirementsVehicleType(element) {
        const scopes = [];
        const addScope = scope => { if (scope && !scopes.includes(scope)) scopes.push(scope); };
        addScope(element);
        addScope(element?.closest?.('tr'));
        addScope(element?.closest?.('[vehicle_type_id], [data-vehicle-type-id], [data-vehicle_type_id]'));
        const read = scope => missionRequirementsOptionalNumber(
            scope?.getAttribute?.('vehicle_type_id')
            ?? scope?.getAttribute?.('data-vehicle-type-id')
            ?? scope?.getAttribute?.('data-vehicle_type_id')
            ?? scope?.dataset?.vehicleTypeId
            ?? scope?.dataset?.vehicle_type_id
        );
        for (const scope of scopes) {
            const direct = read(scope);
            if (direct !== null && direct >= 0) return direct;
            const nested = scope?.querySelector?.('[vehicle_type_id], [data-vehicle-type-id], [data-vehicle_type_id]');
            const nestedType = read(nested);
            if (nestedType !== null && nestedType >= 0) return nestedType;
        }
        const vehicleId = missionRequirementsVehicleId(element);
        const custom = vehicleId >= 0 && typeof customVehicleClassificationForId === 'function' ? customVehicleClassificationForId(vehicleId) : null;
        const customType = missionRequirementsOptionalNumber(custom?.baseTypeId);
        return customType !== null && customType >= 0 ? customType : -1;
    }''')

anchor='''    function missionRequirementsStaffCapacity(element) {'''
helpers=compact_js(r'''    function missionRequirementsCapabilityLabel(value) {
        return String(value || '')
            .replace(/\u00a0/gu, ' ')
            .replace(/&/gu, ' and ')
            .replace(/\([^)]*\)/gu, ' ')
            .replace(/[^a-z0-9]+/giu, ' ')
            .replace(/\s+/gu, ' ')
            .trim()
            .toLowerCase();
    }

    function missionRequirementsMetadataValues(element, kind = 'labels') {
        const values = new Set();
        const add = raw => String(raw || '').split(/[,;|]/u).map(missionRequirementsCapabilityLabel).filter(Boolean).forEach(value => values.add(value));
        const row = element?.closest?.('tr') || element;
        const scopes = Array.from(new Set([element, row].filter(Boolean)));
        const attributes = kind === 'training'
            ? ['data-personnel-training', 'data-training', 'data-trainings', 'data-education', 'data-educations', 'data-education-name']
            : ['data-mcms-custom-vehicle-category', 'data-custom-vehicle-category', 'data-vehicle-category', 'data-vehicle-type-name', 'data-vehicle-type'];
        for (const scope of scopes) {
            for (const attribute of attributes) add(scope?.getAttribute?.(attribute));
            scope?.querySelectorAll?.(attributes.map(attribute => `[${attribute}]`).join(', ')).forEach(node => attributes.forEach(attribute => add(node.getAttribute?.(attribute))));
        }
        if (kind === 'labels') {
            const typeCell = row?.querySelector?.('[data-column="vehicle-type"], [data-vehicle-type-name], td:nth-of-type(2)');
            add(missionRequirementsElementText(typeCell));
            const vehicleId = missionRequirementsVehicleId(element);
            const custom = vehicleId >= 0 && typeof customVehicleClassificationForId === 'function' ? customVehicleClassificationForId(vehicleId) : null;
            add(custom?.category);
        }
        return values;
    }

    function missionRequirementsDefinitionTokens(definition, property = 'aliases') {
        const raw = property === 'training' ? Array.from(definition?.training || []) : [definition?.label, ...(definition?.aliases || [])];
        return new Set(raw.map(missionRequirementsCapabilityLabel).filter(Boolean));
    }

    function missionRequirementsDefinitionMatchesValues(definition, values, property = 'aliases') {
        if (!values?.size) return false;
        const tokens = missionRequirementsDefinitionTokens(definition, property);
        for (const value of values) if (tokens.has(value)) return true;
        return false;
    }

    function missionRequirementsKnownDefinitionKeys(labels) {
        const keys = new Set();
        for (const definition of MISSION_REQUIREMENT_DEFINITIONS) {
            if (missionRequirementsDefinitionMatchesValues(definition, labels)) keys.add(definition.key);
        }
        return keys;
    }

''')+'\n\n'+anchor
one(anchor,helpers,'metadata helpers')

SOURCE.write_text(s, encoding="utf-8")
print('Applied v4.20.3 capability and trained-personnel source patch')
