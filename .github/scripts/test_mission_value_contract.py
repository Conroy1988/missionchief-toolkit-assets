#!/usr/bin/env python3
"""Verify Mission Value toolbar hosting, deduplication, responsive presentation and formatting."""
from __future__ import annotations

import json
import re
import subprocess
import tempfile
from pathlib import Path

import full_userscript_audit as audit

ROOT = Path(__file__).resolve().parents[2]
SOURCE = ROOT / "src" / "MissionChief_Map_Command_Toolkit.user.js"
FIXTURE = ROOT / ".github" / "fixtures" / "mission-value-toolbar-contract.json"


def extract_function(source: str, masked: str, name: str) -> str:
    matches = list(re.finditer(rf"\bfunction\s+{re.escape(name)}\s*\(", masked))
    if len(matches) != 1:
        raise AssertionError(f"Expected one declaration for {name}, found {len(matches)}")
    start = matches[0].start()
    opening = masked.find("{", start)
    closing = audit.matching_brace(masked, opening)
    if opening < 0 or closing is None:
        raise AssertionError(f"Could not extract {name}")
    return source[start:closing + 1]


def main() -> int:
    source = SOURCE.read_text(encoding="utf-8")
    masked = audit.mask_non_code(source)
    fixture = json.loads(FIXTURE.read_text(encoding="utf-8"))
    required = [
        "missionValue: true",
        "merged.missionValue = merged.missionValue !== false",
        "makeToggleButton('missionValue', '£', 'Mission Value'",
        "if (feature === 'missionValue') state.missionValue = !state.missionValue",
        "missionValue: state.missionValue",
        "criticalMissionValueDetails({ missionId, marker, snapshot })",
        "installMissionValueWindows()",
        "ensureMissionValueDocumentStyle(doc)",
        "clearMissionValueDocumentStyles()",
        "mcms-mission-value-document-style",
        "clearMissionValueIndicators()",
        "missionValueToolbarSpacer(root, mount)",
        "missionValuePresentation(availableWidth, formatted)",
        "missionValuePreferredCandidates(candidateList)",
        "missionValueRowsForCandidate(candidate)",
        "missionValueHostObservers",
        "pruneMissionValueHostObservers(activeSpacers)",
        "new ResizeObserverCtor",
        "toolbarSpacer.appendChild(row)",
        "toolbar.parentNode.insertBefore(row, toolbar.nextSibling)",
        "row.dataset.mcmsHost = useToolbar ? 'toolbar' : 'fallback'",
        "if (!activeRows.has(row)) row.remove()",
        "#navbar-alarm-spacer",
        "[id^=\"lssmv4-shareAlliancePost_alarm\"]",
        "transportSweepVisibleWindowRoots()",
        "transportSweepDocumentContexts()",
        "data-mcms-mission-value",
        ".mcms-mission-value-row",
        ".mcms-mission-value-badge",
    ]
    missing = [fragment for fragment in required if fragment not in source]
    assert not missing, f"Mission Value contract fragments missing: {missing}"
    assert "function missionValueRightControlOffset" not in source
    assert "function positionMissionValueRow" not in source
    assert "missionValueRowsAcrossDocuments" not in source
    assert "mountRect.right - leftEdge + 16" not in source

    row_rule = re.search(r"\.mcms-mission-value-row\s*\{(?P<body>.*?)\n\s*\}", source, re.S)
    assert row_rule, "Mission Value row style missing"
    row_body = row_rule.group("body")
    assert "position: absolute" not in row_body
    assert "justify-content: flex-end" in row_body
    assert "min-width: 0" in row_body
    assert "pointer-events: none" in row_body
    assert "padding-right" not in row_body
    assert '#navbar-alarm-spacer > .mcms-mission-value-row' in source
    assert '.mcms-mission-value-row[data-mcms-host="fallback"]' in source

    functions = "\n\n".join(extract_function(source, masked, name) for name in [
        "missionValueCurrencyMeta",
        "formatMissionWindowValue",
        "missionValueIdFromUrl",
        "missionValuePresentation",
        "missionValuePreferredCandidates",
    ])
    cases = json.dumps(fixture["presentations"], ensure_ascii=False)
    candidate_cases = json.dumps(fixture["candidateScenarios"], ensure_ascii=False)
    harness = r""""use strict";
const assert = require("node:assert/strict");
global.location = { hostname: "missionchief.co.uk", href: "https://missionchief.co.uk/" };
function normaliseMissionId(value) {
  const number = Number(value);
  return Number.isInteger(number) && number > 0 ? number : null;
}
""" + functions + f"""\nconst presentationCases = {cases};\nconst candidateScenarios = {candidate_cases};\n""" + r"""
assert.equal(formatMissionWindowValue(12345, "missionchief.co.uk"), "£12,345");
assert.equal(formatMissionWindowValue(12345, "www.missionchief.com"), "$12,345");
assert.equal(formatMissionWindowValue(12345, "leitstellenspiel.de"), "€12.345");
assert.equal(formatMissionWindowValue(12345, "meldkamerspel.com"), "€12.345");
assert.equal(formatMissionWindowValue(-1, "missionchief.co.uk"), "");
assert.equal(formatMissionWindowValue("not-a-value", "missionchief.co.uk"), "");
assert.equal(missionValueIdFromUrl("/missions/98765"), 98765);
assert.equal(missionValueIdFromUrl("https://missionchief.co.uk/missions/42/missing_vehicles"), 42);
assert.equal(missionValueIdFromUrl("/vehicles/42"), null);
for (const testCase of presentationCases) {
  assert.deepEqual(
    missionValuePresentation(testCase.width, testCase.formatted),
    { mode: testCase.mode, text: testCase.text },
    `presentation mismatch at width ${testCase.width}`
  );
}
for (const scenario of candidateScenarios) {
  const refs = new Map();
  const ref = key => {
    if (!key) return null;
    if (!refs.has(key)) refs.set(key, { isConnected: true, key });
    return refs.get(key);
  };
  const candidates = scenario.candidates.map(spec => ({
    missionId: spec.missionId,
    mount: ref(spec.mount),
    toolbarSpacer: ref(spec.toolbarSpacer),
    toolbar: spec.toolbarSpacer ? ref(`${spec.toolbarSpacer}-bar`) : null,
    fixtureKey: spec.key
  }));
  assert.deepEqual(
    missionValuePreferredCandidates(candidates).map(candidate => candidate.fixtureKey),
    scenario.expected,
    `candidate ownership mismatch for ${scenario.name}`
  );
}
console.log("Mission Value formatting, route, responsive presentation and host ownership contracts passed.");
"""
    with tempfile.TemporaryDirectory(prefix="mcms-mission-value-") as temp:
        path = Path(temp) / "contract.js"
        path.write_text(harness, encoding="utf-8")
        subprocess.run(["node", str(path)], check=True, cwd=ROOT)
    print(
        "Mission Value toolbar contract passed: "
        f"{len(fixture['presentations'])} responsive presentations, canonical spacer hosting and cross-document deduplication."
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
