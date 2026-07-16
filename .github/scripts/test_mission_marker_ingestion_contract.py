#!/usr/bin/env python3
"""Run deterministic contracts against the real mission-marker ingestion functions.

The contract extracts named declarations from the canonical userscript and executes
those exact functions in a controlled Node.js harness. Production logic is not
copied into a second implementation and this test does not modify runtime code.
"""
from __future__ import annotations

import json
import os
import re
import subprocess
import tempfile
from pathlib import Path

import full_userscript_audit as audit

ROOT = Path(__file__).resolve().parents[2]
SOURCE = ROOT / "src" / "MissionChief_Map_Command_Toolkit.user.js"
FIXTURES = ROOT / ".github" / "fixtures" / "mission-marker-ingestion-contract.json"

FUNCTION_NAMES = [
    "decodeMissionTextEntities",
    "normaliseMissionCaption",
    "missingRequirementKeyLabel",
    "missingRequirementValueText",
    "formatMissingRequirementObject",
    "normaliseMissingRequirementText",
    "normaliseMissionId",
    "missionIdFromMarker",
    "shallowRecordEqual",
    "setMissionOverlayRecord",
    "missionOverlayVersion",
    "parseCreditValue",
    "normaliseMissionBoolean",
    "parseMissionTimestamp",
    "captureMissionMarkerData",
    "readBalancedObject",
    "captureMissionMarkerDataFromSource",
    "captureMissionMarkerDataFromDocument",
    "missionOwnerId",
    "currentMissionUserId",
    "missionStructuredTypeSignal",
    "missionHasExplicitPersonalOwner",
    "missionHasExplicitAllianceOwner",
    "isAllianceMissionLayer",
    "isPersonalMissionLayer",
    "missionIsEvent",
    "missionWatchOwnership",
    "missionSnapshotFromMarker",
]


def extract_function(source: str, masked: str, name: str) -> str:
    pattern = re.compile(rf"\b(?:async\s+)?function\s+{re.escape(name)}\s*\(")
    matches = list(pattern.finditer(masked))
    if len(matches) != 1:
        raise AssertionError(f"Expected one declaration for {name}, found {len(matches)}")
    match = matches[0]
    open_pos = masked.find("{", match.start())
    if open_pos < 0:
        raise AssertionError(f"Opening brace not found for {name}")
    close_pos = audit.matching_brace(masked, open_pos)
    if close_pos is None:
        raise AssertionError(f"Closing brace not found for {name}")
    return source[match.start():close_pos + 1]


def build_harness(source: str, fixtures: dict) -> str:
    masked = audit.mask_non_code(source)
    functions = "\n\n".join(extract_function(source, masked, name) for name in FUNCTION_NAMES)
    template = r'''"use strict";
const assert = require("node:assert/strict");
const fixtures = __FIXTURES__;

function decodeEntities(value) {
    return String(value ?? "")
        .replaceAll("&amp;", "&")
        .replaceAll("&quot;", "\"")
        .replaceAll("&#39;", "'")
        .replaceAll("&lt;", "<")
        .replaceAll("&gt;", ">");
}

const document = {
    createElement() {
        return {
            _value: "",
            set innerHTML(value) { this._value = decodeEntities(value); },
            get value() { return this._value; }
        };
    },
    getElementById() { return null; },
    querySelectorAll() { return []; }
};

const missionOverlayData = new Map();
const missionOverlayVersions = new Map();
const missionSnapshotCache = new Map();
const missionPanelCache = new Map();
let missionRegistryRevision = 1;
let vehicleDataRevision = 1;
const MISSION_SNAPSHOT_REUSE_MS = 1000;
const CRITICAL_OWNERSHIP_KEYS = ["personal", "alliance"];

function currentUserIdCached() { return fixtures.currentUserId; }
function getMissionPanelElement() { return null; }
function getStrongMarkerSignal() { return { classes: "", text: "", hrefs: [], srcs: [] }; }
function classifyMarker() { return "unknown"; }
function missionDeveloperEventInfo(marker, missionId) {
    const overlay = missionOverlayData.get(String(missionId)) || {};
    return overlay.isSpecialEvent
        ? { active: true, label: String(overlay.eventName || "SPECIAL EVENT").toUpperCase(), eventId: String(overlay.eventId || "") }
        : { active: false, label: "", eventId: "" };
}
function missionWatchCategory(marker, missionId, snapshot, specialEvent) {
    if (specialEvent?.active) return "special";
    return missionIsEvent(marker, missionId, snapshot) ? "event" : "standard";
}
function missionPersonalUnitState() {
    return {
        hasUnit: false,
        commitment: {
            total: 0, onScene: 0, onWay: 0, travelling: 0, transporting: 0,
            awaitingPickup: 0, requestingDispatch: 0, outOfService: 0,
            available: 0, unknownStatus: 0, known: true, source: "fixture"
        }
    };
}
function getMissionAddress(marker) { return String(marker?.address || "Fixture Address"); }
function normaliseMissionPostcode(value) {
    return /[A-Z]{1,2}\d[A-Z\d]?\s*\d[A-Z]{2}/i.exec(String(value || ""))?.[0]?.toUpperCase() || "";
}
function normaliseMissionCity() { return "Edinburgh"; }
function resolveMissionLiveCurrentValue(marker, missionId, overlay) {
    const value = Number(overlay?.liveCurrentValue ?? marker?.live_current_value);
    return Number.isFinite(value) ? value : null;
}
function getMissionCaption(marker, missionId) {
    return missionOverlayData.get(String(missionId))?.caption || String(marker?.caption || "");
}
function getMissionAverageCredits(marker, missionId) {
    const value = Number(missionOverlayData.get(String(missionId))?.averageCredits ?? marker?.average_credits);
    return Number.isFinite(value) ? value : null;
}
function getMissionCreatedAt(marker, missionId) {
    const value = Number(missionOverlayData.get(String(missionId))?.createdAt ?? marker?.created_at);
    return Number.isFinite(value) ? value : null;
}

__FUNCTIONS__

function resetState() {
    missionOverlayData.clear();
    missionOverlayVersions.clear();
    missionSnapshotCache.clear();
    missionPanelCache.clear();
    missionRegistryRevision = 1;
    vehicleDataRevision = 1;
}

function record(id) { return missionOverlayData.get(String(id)); }
function assertSubset(actual, expected, label) {
    for (const [key, value] of Object.entries(expected)) {
        assert.deepEqual(actual?.[key], value, `${label}.${key}`);
    }
}

function testCaptureAndClassification() {
    resetState();
    const originalNow = Date.now;
    Date.now = () => fixtures.fixedNow;
    try {
        captureMissionMarkerData(fixtures.personal.payload);
        const personal = record(fixtures.personal.expected.missionId);
        assertSubset(personal, {
            averageCredits: fixtures.personal.expected.averageCredits,
            createdAt: fixtures.personal.expected.createdAt,
            userId: fixtures.personal.expected.userId,
            missionType: fixtures.personal.expected.missionType,
            filterId: fixtures.personal.expected.filterId,
            dateEndCalc: fixtures.personal.expected.dateEndCalc,
            dateEnd: fixtures.personal.expected.dateEnd,
            dateNow: fixtures.personal.expected.dateNow,
            dateNowUpdatedAt: fixtures.fixedNow,
            vehicleState: fixtures.personal.expected.vehicleState,
            patientsCount: fixtures.personal.expected.patientsCount,
            possiblePatientsCount: fixtures.personal.expected.possiblePatientsCount,
            prisonersCount: fixtures.personal.expected.prisonersCount,
            possiblePrisonersCount: fixtures.personal.expected.possiblePrisonersCount,
            liveCurrentValue: fixtures.personal.expected.liveCurrentValue,
            liveCurrentValueUpdatedAt: fixtures.fixedNow,
            caption: fixtures.personal.expected.caption,
            missingTextKnown: true
        }, "personal");
        assert.equal(personal.missingText, "VEHICLES: 1 Pump, 1 Aerial • PATIENTS: 2");
        assert.equal(missionOverlayVersion("1001"), 1);
        assert.equal(missionWatchOwnership({ mission_id: 1001 }, 1001), fixtures.personal.expected.ownership);

        captureMissionMarkerData(fixtures.personal.payload);
        assert.equal(missionOverlayVersion("1001"), 1, "identical payload must not invalidate caches");

        captureMissionMarkerData(fixtures.personal.partialUpdate);
        const updated = record("1001");
        assert.equal(updated.caption, "Warehouse Fire - Updated");
        assert.equal(updated.liveCurrentValue, 81);
        assert.equal(updated.averageCredits, fixtures.personal.expected.averageCredits);
        assert.equal(updated.missingText, personal.missingText);
        assert.equal(missionOverlayVersion("1001"), 2);

        captureMissionMarkerData(fixtures.alliance.payload);
        const alliance = record(fixtures.alliance.expected.missionId);
        assertSubset(alliance, {
            userId: fixtures.alliance.expected.userId,
            allianceId: fixtures.alliance.expected.allianceId,
            allianceSharedAt: fixtures.alliance.expected.allianceSharedAt,
            missionType: fixtures.alliance.expected.missionType
        }, "alliance");
        assert.equal(missionWatchOwnership({ mission_id: 2002 }, 2002), fixtures.alliance.expected.ownership);

        captureMissionMarkerData(fixtures.event.payload);
        const event = record(fixtures.event.expected.missionId);
        assertSubset(event, {
            eventId: fixtures.event.expected.eventId,
            isEvent: fixtures.event.expected.isEvent,
            eventName: fixtures.event.expected.eventName,
            isSpecialEvent: fixtures.event.expected.isSpecialEvent
        }, "event");
        assert.equal(missionIsEvent({ mission_id: 3003 }, 3003), true);
        assert.equal(missionWatchOwnership({ mission_id: 3003 }, 3003), fixtures.event.expected.ownership);

        captureMissionMarkerData(fixtures.allianceWithoutOwner.payload);
        assert.equal(missionWatchOwnership({ mission_id: 2100 }, 2100), fixtures.allianceWithoutOwner.expectedOwnership);

        captureMissionMarkerData(fixtures.personalOwnerOverridesAllianceSignal.payload);
        assert.equal(missionWatchOwnership({ mission_id: 1100 }, 1100), fixtures.personalOwnerOverridesAllianceSignal.expectedOwnership);

        const sizeBeforeIgnored = missionOverlayData.size;
        for (const payload of fixtures.ignoredPayloads) captureMissionMarkerData(payload);
        assert.equal(missionOverlayData.size, sizeBeforeIgnored);
    } finally {
        Date.now = originalNow;
    }
}

function testInlineAndDocumentCapture() {
    resetState();
    assert.equal(captureMissionMarkerDataFromSource(fixtures.source.script), fixtures.source.expectedCaptured);
    assert.deepEqual(fixtures.source.expectedIds.map(id => missionOverlayData.has(id)), [true, true]);
    assert.equal(record("5005").caption, "Inline {Alarm}");
    assert.equal(missionWatchOwnership({ mission_id: 5006 }, 5006), "alliance");

    const doc = { scripts: fixtures.documentScripts.map(textContent => ({ textContent })) };
    assert.equal(captureMissionMarkerDataFromDocument(doc), 2);
    assert.equal(record("6006").caption, "Document Mission");
    assert.equal(missionIsEvent({ mission_id: 6007 }, 6007), true);
}

function testSnapshotCoordinatesAndCacheInvalidation() {
    resetState();
    const originalNow = Date.now;
    Date.now = () => fixtures.fixedNow;
    try {
        captureMissionMarkerData(fixtures.personal.payload);
        const marker = {
            mission_id: fixtures.snapshot.missionId,
            address: "1 Princes Street, Edinburgh EH2 2EQ",
            getLatLng() { return { lat: fixtures.snapshot.lat, lng: fixtures.snapshot.lng }; }
        };
        const first = missionSnapshotFromMarker(marker, fixtures.snapshot.firstNow);
        assert.equal(first.missionId, fixtures.snapshot.missionId);
        assert.equal(first.ownership, "personal");
        assert.equal(first.category, "standard");
        assert.equal(first.lat, fixtures.snapshot.lat);
        assert.equal(first.lng, fixtures.snapshot.lng);
        assert.equal(first.averageCredits, fixtures.personal.expected.averageCredits);
        assert.equal(first.createdAt, fixtures.personal.expected.createdAt);
        assert.equal(first.vehicleState, fixtures.personal.expected.vehicleState);
        assert.equal(first.liveCurrentValue, fixtures.personal.expected.liveCurrentValue);

        const second = missionSnapshotFromMarker(marker, fixtures.snapshot.secondNow);
        assert.equal(second, first, "unchanged marker data must reuse the cached snapshot");
        assert.equal(second.lastSeen, fixtures.snapshot.secondNow);

        captureMissionMarkerData({ id: fixtures.snapshot.missionId, caption: fixtures.snapshot.updatedCaption });
        const third = missionSnapshotFromMarker(marker, fixtures.snapshot.updatedNow);
        assert.notEqual(third, first, "overlay changes must invalidate the snapshot cache");
        assert.equal(third.caption, fixtures.snapshot.updatedCaption);
        assert.equal(third.lat, fixtures.snapshot.lat);
        assert.equal(third.lng, fixtures.snapshot.lng);
        assert.equal(missionSnapshotFromMarker({}, fixtures.snapshot.updatedNow), null);
    } finally {
        Date.now = originalNow;
    }
}

testCaptureAndClassification();
testInlineAndDocumentCapture();
testSnapshotCoordinatesAndCacheInvalidation();
console.log("Mission marker ingestion contract passed: payload capture, partial updates, ownership, events, inline scripts, coordinates and cache invalidation.");
'''
    return template.replace("__FIXTURES__", json.dumps(fixtures, ensure_ascii=False)).replace("__FUNCTIONS__", functions)


def main() -> int:
    source = SOURCE.read_text(encoding="utf-8")
    fixtures = json.loads(FIXTURES.read_text(encoding="utf-8"))
    harness = build_harness(source, fixtures)
    with tempfile.TemporaryDirectory(prefix="missionchief-marker-contract-") as temporary:
        harness_path = Path(temporary) / "mission-marker-ingestion-contract.cjs"
        harness_path.write_text(harness, encoding="utf-8")
        completed = subprocess.run(
            ["node", str(harness_path)],
            cwd=ROOT,
            text=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            check=False,
            env={**os.environ, "TZ": "Europe/London"},
        )
    print(completed.stdout, end="")
    if completed.returncode != 0:
        raise SystemExit(completed.returncode)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
