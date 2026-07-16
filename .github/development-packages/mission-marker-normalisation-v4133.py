#!/usr/bin/env python3
from __future__ import annotations

from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
SOURCE = ROOT / 'src' / 'MissionChief_Map_Command_Toolkit.user.js'
DIST_USER = ROOT / 'dist' / 'MissionChief_Map_Command_Toolkit.user.js'
DIST_TXT = ROOT / 'dist' / 'MissionChief_Map_Command_Toolkit.txt'
CHANGELOG = ROOT / 'CHANGELOG.md'
MARKER_TEST = ROOT / '.github' / 'scripts' / 'test_mission_marker_ingestion_contract.py'


def replace_once(text: str, old: str, new: str, label: str) -> str:
    count = text.count(old)
    if count != 1:
        raise RuntimeError(f'{label}: expected exactly one match, found {count}')
    return text.replace(old, new, 1)


def update_source() -> None:
    text = SOURCE.read_text(encoding='utf-8')
    text = replace_once(text, '// @version      4.13.2', '// @version      4.13.3', 'metadata version')
    text = replace_once(text, "version: '4.13.2'", "version: '4.13.3'", 'runtime version')
    text = replace_once(text, "styleId: 'mc-map-command-toolkit-style-v4132'", "styleId: 'mc-map-command-toolkit-style-v4133'", 'style id')
    text = replace_once(text, "guideVersion: '4.13.2'", "guideVersion: '4.13.3'", 'help guide version')
    text = replace_once(
        text,
        "    pageWindow.__MC_MAP_COMMAND_TOOLKIT_V4132__ = true;\n",
        "    pageWindow.__MC_MAP_COMMAND_TOOLKIT_V4132__ = true;\n    pageWindow.__MC_MAP_COMMAND_TOOLKIT_V4133__ = true;\n",
        'runtime sentinel',
    )

    old = '''function captureMissionMarkerData(payload) {
        if (!payload) return;
        if (Array.isArray(payload)) {
            payload.forEach(captureMissionMarkerData);
            return;
        }
        if (typeof payload !== 'object') return;

        const candidates = [payload, payload.params, payload.mission, payload.data].filter(item => item && typeof item === 'object');
        for (const item of candidates) {
            const missionId = normaliseMissionId(item.id ?? item.mission_id ?? item.missionId);
            if (missionId === null) continue;

            const existing = missionOverlayData.get(missionId) || {};
            const credits = parseCreditValue(item.average_credits ?? item.averageCredits ?? item.average_credit);
            const createdAt = parseMissionTimestamp(item.created_at ?? item.createdAt ?? item.date_created ?? item.dateCreated);
            const allianceSharedAt = parseMissionTimestamp(item.alliance_shared_at ?? item.allianceSharedAt ?? item.shared_at ?? item.sharedAt);
            const userId = item.user_id ?? item.userId;
            const allianceId = item.alliance_id ?? item.allianceId;
            const missionType = item.mission_type ?? item.missionType;
            const filterId = item.filter_id ?? item.filterId;
            const eventId = item.event_id ?? item.eventId;
            const eventFlag = item.sw ?? item.sicherheitswache ?? item.security_watch ?? item.securityWatch ?? item.is_event ?? item.isEvent ?? item.event;
            const eventName = item.event_name ?? item.eventName ?? item.event_title ?? item.eventTitle ?? item.event_caption ?? item.eventCaption;
            const specialEventFlag = item.special_event ?? item.specialEvent ?? item.is_special_event ?? item.isSpecialEvent ?? item.global_event ?? item.globalEvent ?? item.developer_event ?? item.developerEvent;
            const dateEndCalc = parseMissionTimestamp(item.date_end_calc ?? item.dateEndCalc);
            const dateEnd = parseMissionTimestamp(item.date_end ?? item.dateEnd);
            const dateNow = parseMissionTimestamp(item.date_now ?? item.dateNow);
            const dateNowUpdatedAt = dateNow !== null ? Date.now() : null;
            const rawVehicleState = item.vehicle_state ?? item.vehicleState;
            const vehicleState = Number(rawVehicleState);
            const missingTextKeys = ['missing_text', 'missingText', 'missing_text_short', 'missingTextShort'];
            const missingTextKnown = missingTextKeys.some(key => Object.prototype.hasOwnProperty.call(item, key));
            const missingText = item.missing_text ?? item.missingText ?? item.missing_text_short ?? item.missingTextShort ?? '';
            const normalisedMissingText = normaliseMissingRequirementText(missingText);
            const patientsCount = Number(item.patients_count ?? item.patientsCount);
            const possiblePatientsCount = Number(item.possible_patients_count ?? item.possiblePatientsCount);
            const prisonersCount = Number(item.prisoners_count ?? item.prisonersCount);
            const possiblePrisonersCount = Number(item.possible_prisoners_count ?? item.possiblePrisonersCount);
            const liveCurrentValue = Number(item.live_current_value ?? item.liveCurrentValue ?? item.current_value ?? item.currentValue);
            const liveCurrentValueUpdatedAt = Date.now();

            setMissionOverlayRecord(missionId, {
                ...existing,
                ...(credits !== null ? { averageCredits: credits } : {}),
                ...(createdAt !== null ? { createdAt } : {}),
                ...(allianceSharedAt !== null ? { allianceSharedAt } : {}),
                ...(userId !== undefined && userId !== null ? { userId: String(userId) } : {}),
                ...(allianceId !== undefined ? { allianceId } : {}),
                ...(missionType !== undefined && missionType !== null ? { missionType: String(missionType) } : {}),
                ...(filterId !== undefined && filterId !== null ? { filterId: String(filterId) } : {}),
                ...(eventId !== undefined && eventId !== null ? { eventId: String(eventId) } : {}),
                ...(eventFlag !== undefined && eventFlag !== null ? { isEvent: normaliseMissionBoolean(eventFlag) } : {}),
                ...(eventName !== undefined && eventName !== null && String(eventName).trim() ? { eventName: normaliseMissionCaption(eventName) } : {}),
                ...(specialEventFlag !== undefined && specialEventFlag !== null ? { isSpecialEvent: normaliseMissionBoolean(specialEventFlag) } : {}),
                ...(dateEndCalc !== null ? { dateEndCalc } : {}),
                ...(dateEnd !== null ? { dateEnd } : {}),
                ...(dateNow !== null ? { dateNow, dateNowUpdatedAt } : {}),
                ...(Number.isFinite(vehicleState) ? { vehicleState } : {}),
                ...(missingTextKnown ? { missingText: normalisedMissingText, missingTextKnown: true } : {}),
                ...(Number.isFinite(patientsCount) ? { patientsCount } : {}),
                ...(Number.isFinite(possiblePatientsCount) ? { possiblePatientsCount } : {}),
                ...(Number.isFinite(prisonersCount) ? { prisonersCount } : {}),
                ...(Number.isFinite(possiblePrisonersCount) ? { possiblePrisonersCount } : {}),
                ...(Number.isFinite(liveCurrentValue) ? { liveCurrentValue, liveCurrentValueUpdatedAt } : {}),
                ...(item.caption ? { caption: normaliseMissionCaption(item.caption) } : {})
            });
        }
    }
'''

    new = '''function normaliseMissionOverlayRecord(item, existing = {}) {
        const credits = parseCreditValue(item.average_credits ?? item.averageCredits ?? item.average_credit);
        const createdAt = parseMissionTimestamp(item.created_at ?? item.createdAt ?? item.date_created ?? item.dateCreated);
        const allianceSharedAt = parseMissionTimestamp(item.alliance_shared_at ?? item.allianceSharedAt ?? item.shared_at ?? item.sharedAt);
        const userId = item.user_id ?? item.userId;
        const allianceId = item.alliance_id ?? item.allianceId;
        const missionType = item.mission_type ?? item.missionType;
        const filterId = item.filter_id ?? item.filterId;
        const eventId = item.event_id ?? item.eventId;
        const eventFlag = item.sw ?? item.sicherheitswache ?? item.security_watch ?? item.securityWatch ?? item.is_event ?? item.isEvent ?? item.event;
        const eventName = item.event_name ?? item.eventName ?? item.event_title ?? item.eventTitle ?? item.event_caption ?? item.eventCaption;
        const specialEventFlag = item.special_event ?? item.specialEvent ?? item.is_special_event ?? item.isSpecialEvent ?? item.global_event ?? item.globalEvent ?? item.developer_event ?? item.developerEvent;
        const dateEndCalc = parseMissionTimestamp(item.date_end_calc ?? item.dateEndCalc);
        const dateEnd = parseMissionTimestamp(item.date_end ?? item.dateEnd);
        const dateNow = parseMissionTimestamp(item.date_now ?? item.dateNow);
        const dateNowUpdatedAt = dateNow !== null ? Date.now() : null;
        const rawVehicleState = item.vehicle_state ?? item.vehicleState;
        const vehicleState = Number(rawVehicleState);
        const missingTextKeys = ['missing_text', 'missingText', 'missing_text_short', 'missingTextShort'];
        const missingTextKnown = missingTextKeys.some(key => Object.prototype.hasOwnProperty.call(item, key));
        const missingText = item.missing_text ?? item.missingText ?? item.missing_text_short ?? item.missingTextShort ?? '';
        const normalisedMissingText = normaliseMissingRequirementText(missingText);
        const patientsCount = Number(item.patients_count ?? item.patientsCount);
        const possiblePatientsCount = Number(item.possible_patients_count ?? item.possiblePatientsCount);
        const prisonersCount = Number(item.prisoners_count ?? item.prisonersCount);
        const possiblePrisonersCount = Number(item.possible_prisoners_count ?? item.possiblePrisonersCount);
        const liveCurrentValue = Number(item.live_current_value ?? item.liveCurrentValue ?? item.current_value ?? item.currentValue);
        const liveCurrentValueUpdatedAt = Date.now();

        return {
            ...existing,
            ...(credits !== null ? { averageCredits: credits } : {}),
            ...(createdAt !== null ? { createdAt } : {}),
            ...(allianceSharedAt !== null ? { allianceSharedAt } : {}),
            ...(userId !== undefined && userId !== null ? { userId: String(userId) } : {}),
            ...(allianceId !== undefined ? { allianceId } : {}),
            ...(missionType !== undefined && missionType !== null ? { missionType: String(missionType) } : {}),
            ...(filterId !== undefined && filterId !== null ? { filterId: String(filterId) } : {}),
            ...(eventId !== undefined && eventId !== null ? { eventId: String(eventId) } : {}),
            ...(eventFlag !== undefined && eventFlag !== null ? { isEvent: normaliseMissionBoolean(eventFlag) } : {}),
            ...(eventName !== undefined && eventName !== null && String(eventName).trim() ? { eventName: normaliseMissionCaption(eventName) } : {}),
            ...(specialEventFlag !== undefined && specialEventFlag !== null ? { isSpecialEvent: normaliseMissionBoolean(specialEventFlag) } : {}),
            ...(dateEndCalc !== null ? { dateEndCalc } : {}),
            ...(dateEnd !== null ? { dateEnd } : {}),
            ...(dateNow !== null ? { dateNow, dateNowUpdatedAt } : {}),
            ...(Number.isFinite(vehicleState) ? { vehicleState } : {}),
            ...(missingTextKnown ? { missingText: normalisedMissingText, missingTextKnown: true } : {}),
            ...(Number.isFinite(patientsCount) ? { patientsCount } : {}),
            ...(Number.isFinite(possiblePatientsCount) ? { possiblePatientsCount } : {}),
            ...(Number.isFinite(prisonersCount) ? { prisonersCount } : {}),
            ...(Number.isFinite(possiblePrisonersCount) ? { possiblePrisonersCount } : {}),
            ...(Number.isFinite(liveCurrentValue) ? { liveCurrentValue, liveCurrentValueUpdatedAt } : {}),
            ...(item.caption ? { caption: normaliseMissionCaption(item.caption) } : {})
        };
    }

    function captureMissionMarkerData(payload) {
        if (!payload) return;
        if (Array.isArray(payload)) {
            payload.forEach(captureMissionMarkerData);
            return;
        }
        if (typeof payload !== 'object') return;

        const candidates = [payload, payload.params, payload.mission, payload.data].filter(item => item && typeof item === 'object');
        for (const item of candidates) {
            const missionId = normaliseMissionId(item.id ?? item.mission_id ?? item.missionId);
            if (missionId === null) continue;

            const existing = missionOverlayData.get(missionId) || {};
            setMissionOverlayRecord(missionId, normaliseMissionOverlayRecord(item, existing));
        }
    }
'''
    text = replace_once(text, old, new, 'mission overlay normalization extraction')

    SOURCE.write_text(text, encoding='utf-8')
    DIST_USER.write_text(text, encoding='utf-8')
    DIST_TXT.write_text(text, encoding='utf-8')


def update_marker_contract() -> None:
    text = MARKER_TEST.read_text(encoding='utf-8')
    text = replace_once(
        text,
        '    "parseMissionTimestamp",\n    "captureMissionMarkerData",\n',
        '    "parseMissionTimestamp",\n    "normaliseMissionOverlayRecord",\n    "captureMissionMarkerData",\n',
        'marker helper extraction list',
    )

    insertion_point = '''function testCaptureAndClassification() {
'''
    helper_test = '''function testOverlayRecordNormalisation() {
    resetState();
    const originalNow = Date.now;
    Date.now = () => fixtures.fixedNow;
    try {
        const existing = {
            preservedField: "preserved",
            averageCredits: 321,
            missingText: "EXISTING REQUIREMENT",
            missingTextKnown: true
        };
        const existingCopy = { ...existing };
        const normalised = normaliseMissionOverlayRecord(fixtures.personal.payload, existing);
        assert.deepEqual(existing, existingCopy, "normalisation must not mutate the existing overlay record");
        assertSubset(normalised, {
            preservedField: "preserved",
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
        }, "normalised");
        assert.equal(normalised.missingText, "VEHICLES: 1 Pump, 1 Aerial • PATIENTS: 2");

        const partial = normaliseMissionOverlayRecord(fixtures.personal.partialUpdate.data, normalised);
        assert.equal(partial.caption, "Warehouse Fire - Updated");
        assert.equal(partial.liveCurrentValue, 81);
        assert.equal(partial.averageCredits, fixtures.personal.expected.averageCredits);
        assert.equal(partial.missingText, normalised.missingText);
        assert.equal(partial.preservedField, "preserved");

        const invalidNumbers = normaliseMissionOverlayRecord({
            average_credits: "not credits",
            vehicle_state: "not a number",
            patients_count: "unknown",
            possible_patients_count: "unknown",
            prisoners_count: "unknown",
            possible_prisoners_count: "unknown",
            live_current_value: "unknown"
        }, existing);
        assert.deepEqual(invalidNumbers, existing, "invalid optional values must preserve the existing record");
    } finally {
        Date.now = originalNow;
    }
}

function testCaptureAndClassification() {
'''
    text = replace_once(text, insertion_point, helper_test, 'direct marker helper contract')
    text = replace_once(
        text,
        '''testCaptureAndClassification();
testInlineAndDocumentCapture();
testSnapshotCoordinatesAndCacheInvalidation();
console.log("Mission marker ingestion contract passed: payload capture, partial updates, ownership, events, inline scripts, coordinates and cache invalidation.");
''',
        '''testOverlayRecordNormalisation();
testCaptureAndClassification();
testInlineAndDocumentCapture();
testSnapshotCoordinatesAndCacheInvalidation();
console.log("Mission marker ingestion contract passed: direct normalization, payload capture, partial updates, ownership, events, inline scripts, coordinates and cache invalidation.");
''',
        'marker contract invocation',
    )
    MARKER_TEST.write_text(text, encoding='utf-8')


def update_changelog() -> None:
    text = CHANGELOG.read_text(encoding='utf-8')
    entry = '''## [Unreleased]

## [4.13.3] - 2026-07-16

### Internal reliability
- Added direct fixture coverage for marker payload normalization, including field preservation, invalid optional values and non-mutating overlay updates.
- Extracted MissionChief marker payload interpretation into `normaliseMissionOverlayRecord()` while preserving candidate discovery, mission IDs, overlay versioning, ownership classification, snapshot invalidation and map lifecycle behaviour.

### Compatibility
- No settings, themes, payout presentations, public assets, Leaflet operations, observers, timers or mission snapshot outputs were changed.

'''
    text = replace_once(text, '## [Unreleased]\n\n', entry, '4.13.3 changelog entry')
    CHANGELOG.write_text(text, encoding='utf-8')


def main() -> int:
    update_source()
    update_marker_contract()
    update_changelog()
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
