#!/usr/bin/env python3
from __future__ import annotations

import base64
import re
import zlib
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
SELF = Path(__file__).resolve()
ORIGINAL = ROOT / ".github" / "development-packages" / "issue-141-mission-requirements-completeness.py"

loader = ORIGINAL.read_text(encoding="utf-8")
match = re.search(r"b64decode\('([^']+)'\)", loader)
if not match:
    raise AssertionError("Issue #141 package payload was not found")
package = zlib.decompress(base64.b64decode(match.group(1))).decode("utf-8")

version_anchor = "source = replace_once(source, f\"guideVersion: '{PREVIOUS}'\", f\"guideVersion: '{VERSION}'\", \"Help Centre version\")\n"
early_transforms = '''
source = replace_once(
    source,
    "const selector = '#missing_text, #mission_vehicle_driving, #vehicle_show_table_body_all, #occupied, .vehicle_checkbox, [vehicle_type_id], [data-equipment-types], [data-equipment-type], [id^=\\\"mission_water_holder\\\"], [id^=\\\"mission_foam_holder\\\"], [id^=\\\"mission_pump_holder\\\"]';",
    "const selector = '#missing_text, #mission_vehicle_driving, #vehicle_show_table_body_all, #occupied, .vehicle_checkbox, [vehicle_type_id], [data-vehicle-type-id], [data-vehicle_type_id], [data-equipment-types], [data-equipment-type], [data-current-personnel], [data-min-personnel], [data-max-personnel], [id^=\\\"mission_water_holder\\\"], [id^=\\\"mission_foam_holder\\\"], [id^=\\\"mission_pump_holder\\\"]';",
    "Mission Requirements record mutation selector"
)
source = replace_once(
    source,
    "attributeFilter: ['checked', 'class', 'style', 'vehicle_type_id', 'data-equipment-types', 'data-equipment-type', 'tractive_vehicle_id', 'sortvalue']",
    "attributeFilter: ['checked', 'class', 'style', 'vehicle_type_id', 'data-vehicle-type-id', 'data-vehicle_type_id', 'data-equipment-types', 'data-equipment-type', 'data-current-personnel', 'data-min-personnel', 'data-max-personnel', 'tractive_vehicle_id', 'data-tractive-vehicle-id', 'trailer_id', 'data-trailer-id', 'sortvalue']",
    "Mission Requirements record attribute filter"
)
source = replace_once(
    source,
    "const activitySelector = '#missing_text, #mission_vehicle_driving, #vehicle_show_table_body_all, #occupied, .vehicle_checkbox, [vehicle_type_id], [data-equipment-types], [id^=\\\"mission_water_holder\\\"], [id^=\\\"mission_foam_holder\\\"], [id^=\\\"mission_pump_holder\\\"], #lightbox_box, #lightbox, .lightbox_content, .modal, [role=\\\"dialog\\\"], .ui-dialog, iframe, frame';",
    "const activitySelector = '#missing_text, #mission_vehicle_driving, #vehicle_show_table_body_all, #occupied, .vehicle_checkbox, [vehicle_type_id], [data-vehicle-type-id], [data-vehicle_type_id], [data-equipment-types], [data-equipment-type], [data-current-personnel], [data-min-personnel], [data-max-personnel], [id^=\\\"mission_water_holder\\\"], [id^=\\\"mission_foam_holder\\\"], [id^=\\\"mission_pump_holder\\\"], #lightbox_box, #lightbox, .lightbox_content, .modal, [role=\\\"dialog\\\"], .ui-dialog, iframe, frame';",
    "Mission Requirements document activity selector"
)
'''
if package.count(version_anchor) != 1:
    raise AssertionError("Issue #141 package version anchor missing or duplicated")
package = package.replace(version_anchor, version_anchor + early_transforms, 1)

package = package.replace("            if (direct >= 0) return direct;", "            if (direct !== null && direct >= 0) return direct;")
package = package.replace("            if (nestedType >= 0) return nestedType;", "            if (nestedType !== null && nestedType >= 0) return nestedType;")
package = package.replace(
    "            const pairedId = tractiveId >= 0 ? tractiveId : trailerId;\n            if (vehicleId >= 0 && pairedId >= 0)",
    "            const pairedId = tractiveId !== null && tractiveId >= 0 ? tractiveId : trailerId;\n            if (vehicleId >= 0 && pairedId !== null && pairedId >= 0)"
)
package = package.replace(
    "        for (const scope of Array.from(new Set([root, candidate?.mount, doc].filter(Boolean)))) {",
    "        const missionScopes = Array.from(new Set([root, candidate?.mount].filter(scope => scope?.querySelectorAll)));\n        const scopes = missionScopes.length ? missionScopes : [doc].filter(scope => scope?.querySelectorAll);\n        for (const scope of scopes) {"
)

resolve_start = package.find("resolve_masked = audit.mask_non_code(source)")
resolve_end = package.find("unknown_helper = r'''function missionRequirementsUnknownCoverageRow", resolve_start)
if resolve_start < 0 or resolve_end < 0:
    raise AssertionError("Issue #141 resolve transform boundaries were not found")
resolve_transform = '''resolve_masked = audit.mask_non_code(source)
resolve_matches = list(re.finditer(r"\\bfunction\\s+missionRequirementsResolve\\s*\\(", resolve_masked))
if len(resolve_matches) != 1:
    raise AssertionError(f"Expected one declaration for missionRequirementsResolve, found {len(resolve_matches)}")
resolve_start = resolve_matches[0].start()
resolve_opening = resolve_masked.find("{", resolve_start)
resolve_closing = audit.matching_brace(resolve_masked, resolve_opening)
if resolve_opening < 0 or resolve_closing is None:
    raise AssertionError("Could not extract missionRequirementsResolve")
resolve_function = source[resolve_start:resolve_closing + 1]
resolve_needle = "return parsed.requirements.map(requirement => {\\n            const condition = missionRequirementsDefinitionCondition(requirement.definition, candidate);"
if resolve_function.count(resolve_needle) != 1:
    raise AssertionError("missionRequirementsResolve callback anchor missing or duplicated")
resolve_function = resolve_function.replace(
    resolve_needle,
    "return parsed.requirements.map(requirement => {\\n"
    "            if (requirement.definition?.countable === false) return missionRequirementsUnknownCoverageRow(requirement);\\n"
    "            const condition = missionRequirementsDefinitionCondition(requirement.definition, candidate);",
    1
)
'''
package = package[:resolve_start] + resolve_transform + package[resolve_end:]

mutation_start = package.find('source = replace_function(source, "missionRequirementsMutationRelevant"')
scan_start = package.find('source = replace_function(source, "scanMissionRequirementsWindows"', mutation_start)
if mutation_start < 0 or scan_start < 0:
    raise AssertionError("Issue #141 mutation/scan package boundaries were not found")
package = package[:mutation_start] + package[scan_start:]

scan_start = package.find('source = replace_function(source, "scanMissionRequirementsWindows"')
scan_end = package.find('\n\nSOURCE.write_text(source, encoding="utf-8")', scan_start)
if scan_start < 0 or scan_end < 0:
    raise AssertionError("Issue #141 scan package boundaries were not found")
scan_transform = """source = replace_function(source, \"scanMissionRequirementsWindows\", r'''function scanMissionRequirementsWindows() {
        if (runtime.destroyed) return;
        if (!state.missionRequirements) {
            clearMissionRequirementsPanels();
            return;
        }
        const activeSources = new Set();
        const activeDocuments = new WeakSet();
        for (const candidate of missionRequirementsWindowCandidates()) {
            const source = missionRequirementsSourceForCandidate(candidate);
            if (!source || source.isConnected === false) continue;
            const doc = source.ownerDocument || candidate?.root?.ownerDocument || document;
            if (!doc || activeDocuments.has(doc)) continue;
            activeDocuments.add(doc);
            ensureMissionRequirementsDocumentStyle(doc);
            if (missionRequirementsLssmActive(candidate, source)) {
                missionRequirementsRemoveRecord(source);
                continue;
            }
            const raw = missionRequirementsElementText(source);
            if (!raw) {
                missionRequirementsRemoveRecord(source);
                continue;
            }
            activeSources.add(source);
            missionRequirementsEnsureRecord(candidate, source);
        }
        for (const source of Array.from(missionRequirementsRecords.keys())) {
            if (source.isConnected === false || !activeSources.has(source)) missionRequirementsRemoveRecord(source);
        }
    }''')"""
package = package[:scan_start] + scan_transform + package[scan_end:]

namespace = {"__file__": str(ORIGINAL), "__name__": "__main__"}
exec(compile(package, str(ORIGINAL), "exec"), namespace, namespace)
SELF.unlink(missing_ok=True)
