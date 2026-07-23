#!/usr/bin/env python3
from __future__ import annotations

import json
import re
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
SOURCE = ROOT / "src" / "MissionChief_Map_Command_Toolkit.user.js"
CANONICAL = (
    SOURCE,
    ROOT / "MissionChief_Map_Command_Toolkit.user.js",
    ROOT / "MissionChief_Map_Command_Toolkit.txt",
    ROOT / "dist" / "MissionChief_Map_Command_Toolkit.user.js",
    ROOT / "dist" / "MissionChief_Map_Command_Toolkit.txt",
)
VALIDATOR = ROOT / ".github" / "scripts" / "validate_userscript.py"
PREFLIGHT = ROOT / ".github" / "scripts" / "run_userscript_preflight.sh"
WORKFLOW = ROOT / ".github" / "workflows" / "full-userscript-audit.yml"
HEADROOM_FIXTURE = ROOT / ".github" / "fixtures" / "main-style-source-headroom.json"
HEADROOM_TEST = ROOT / ".github" / "scripts" / "test_main_style_source_headroom.py"
SHELL_TEST = ROOT / ".github" / "scripts" / "test_issue378_operational_suite_shell.py"
RENDERER_TEST = ROOT / ".github" / "scripts" / "test_issue378_requirements_renderer.py"
RETIREMENT_TEST = ROOT / ".github" / "scripts" / "test_issue391_matrix_retirement.py"
OLD_CONTRACT = ROOT / ".github" / "scripts" / "test_mission_requirements_contract.py"
OLD_RUNTIME = ROOT / ".github" / "scripts" / "test_mission_requirements_runtime.js"
OLD_FIXTURE = ROOT / ".github" / "fixtures" / "mission-requirements-contract.json"
DIAGNOSTICS = (
    ROOT / ".github" / "diagnostics" / "issue391-matrix-retirement-map.txt",
    ROOT / ".github" / "diagnostics" / "issue391-matrix-full-map.txt",
    ROOT / ".github" / "diagnostics" / "issue391-matrix-hook-map.txt",
    ROOT / ".github" / "diagnostics" / "issue391-retirement-preflight-failure.txt",
)


def replace_exact(text: str, old: str, new: str, label: str, expected: int = 1) -> str:
    count = text.count(old)
    if count != expected:
        raise RuntimeError(f"{label}: expected {expected} occurrence(s), found {count}")
    return text.replace(old, new)


def extract_declaration(text: str, name: str, lower: int, upper: int) -> str:
    token = f"    const {name} ="
    start = text.find(token, lower, upper)
    if start < 0:
        raise RuntimeError(f"shared capability declaration missing: {name}")
    quote = None
    escaped = False
    template_depth = 0
    round_depth = square_depth = brace_depth = 0
    index = start
    while index < upper:
        char = text[index]
        nxt = text[index + 1] if index + 1 < upper else ""
        if quote:
            if escaped:
                escaped = False
            elif char == "\\":
                escaped = True
            elif quote == "`" and char == "$" and nxt == "{":
                template_depth += 1
                brace_depth += 1
                index += 1
            elif char == quote and template_depth == 0:
                quote = None
            elif quote == "`" and char == "}" and template_depth > 0:
                template_depth -= 1
                brace_depth = max(0, brace_depth - 1)
        else:
            if char in "'\"`":
                quote = char
            elif char == "(":
                round_depth += 1
            elif char == ")":
                round_depth -= 1
            elif char == "[":
                square_depth += 1
            elif char == "]":
                square_depth -= 1
            elif char == "{":
                brace_depth += 1
            elif char == "}":
                brace_depth -= 1
            elif char == ";" and round_depth == square_depth == brace_depth == 0:
                end = index + 1
                if end < len(text) and text[end] == "\n":
                    end += 1
                return text[start:end]
        if min(round_depth, square_depth, brace_depth) < 0:
            raise RuntimeError(f"unbalanced shared declaration: {name}")
        index += 1
    raise RuntimeError(f"unterminated shared declaration: {name}")


source = SOURCE.read_text(encoding="utf-8")
base_lines = len(source.splitlines())
start_marker = "    // Issue #133 clean-room live mission requirements matrix."
end_marker = "    function criticalMissionValueForEntry"
start = source.index(start_marker)
end = source.index(end_marker, start)
old_block = source[start:end]
if len(old_block.splitlines()) != 1395:
    raise RuntimeError(f"Matrix retirement boundary drifted: {len(old_block.splitlines())} lines")

shared_names = (
    "MISSION_REQUIREMENT_DEFINITIONS",
    "MISSION_REQUIREMENTS_DEFAULT_STAFF_BY_TYPE",
    "MISSION_REQUIREMENTS_TRACTIVE_TYPES",
)
shared = []
for name in shared_names:
    token = f"    const {name} ="
    declaration_start = source.find(token)
    if declaration_start < 0 or source.count(token) != 1:
        raise RuntimeError(f"shared capability declaration count changed: {name}")
    if start <= declaration_start < end:
        shared.append(extract_declaration(source, name, start, end))
replacement = (
    "    // Issue #378 retained UK operational capability catalogue.\n"
    + "".join(shared)
    + "    // Issue #391: legacy Mission Requirements Matrix retired; operationalWindow is authoritative.\n\n"
)
source = source[:start] + replacement + source[end:]

source = re.sub(r"^\s*missionRequirementsPanelId:\s*[^\n]+\n", "", source, count=1, flags=re.MULTILINE)
source = re.sub(r"^\s*missionRequirementsDocumentStyleId:\s*[^\n]+\n", "", source, count=1, flags=re.MULTILINE)
source = re.sub(r"^\s*missionRequirementsRecords:\s*[^\n]+\n", "", source, flags=re.MULTILINE)
source = replace_exact(source, "        missionRequirements: true,\n", "", "legacy default-state key")
source = replace_exact(
    source,
    "        merged.missionRequirements = merged.missionRequirements !== false;\n        merged.operationalWindow = normaliseOperationalWindowState(merged.operationalWindow, merged.missionRequirements);\n",
    "        const legacyRequirementsEnabled = parsed?.missionRequirements !== false;\n        merged.operationalWindow = normaliseOperationalWindowState(merged.operationalWindow, legacyRequirementsEnabled);\n        delete merged.missionRequirements;\n        merged.operationalWindow.migration.matrixRetired = true;\n",
    "legacy state migration",
)
source = replace_exact(
    source,
    "normaliseOperationalWindowState(state.operationalWindow, state.missionRequirements !== false)",
    "normaliseOperationalWindowState(state.operationalWindow, state.operationalWindow?.requirements?.enabled !== false)",
    "operational setting normalisation",
)
source = source.replace("legacyMatrixEnabled", "legacyRequirementsEnabled")
source = re.sub(r"\bmatrixEnabled\b", "legacyRequirementsEnabled", source)
source = re.sub(r"matrixRetired:\s*false", "matrixRetired: true", source)
source = re.sub(r"^\s*missionRequirements:\s*state\.missionRequirements,\s*\n", "", source, flags=re.MULTILINE)
source = re.sub(r"^\s*else if \(feature === 'missionRequirements'\) state\.missionRequirements = !state\.missionRequirements;\s*\n", "", source, flags=re.MULTILINE)
source = re.sub(r"^\s*if \(feature === 'missionRequirements'\) \{[^\n]*\}\s*\n", "", source, flags=re.MULTILINE)
source = re.sub(r"^\s*if \(state\.missionRequirements\) scheduleMissionRequirementsScan\(0\);\s*\n", "", source, flags=re.MULTILINE)
source = re.sub(r"^\s*installMissionRequirementsWindows\(\);\s*\n", "", source, flags=re.MULTILINE)
source = re.sub(r"\$\{makeToggleButton\('missionRequirements',[^\n]*\}\s*", "", source)
source = source.replace("phase: 'requirements-renderer'", "phase: 'operational-suite'")

for token in (
    start_marker,
    "MISSION_REQUIREMENT_PARSE_DEFINITIONS",
    "function missionRequirementsParseText(",
    "function missionRequirementsResolve(",
    "function installMissionRequirementsWindows(",
    "function scanMissionRequirementsWindows(",
    "scheduleMissionRequirementsScan(",
    "clearMissionRequirementsPanels(",
    "missionRequirementsPanelId",
    "missionRequirementsDocumentStyleId",
    "data-mcms-requirements-panel",
    "state.missionRequirements",
    "merged.missionRequirements",
    "makeToggleButton('missionRequirements'",
):
    if token in source:
        raise RuntimeError(f"legacy Matrix token survived retirement: {token}")
if source.count("parsed?.missionRequirements") != 1:
    raise RuntimeError("historical Matrix preference must be consumed exactly once")
for name in shared_names:
    if source.count(f"const {name} =") != 1:
        raise RuntimeError(f"shared capability catalogue count changed: {name}")
if source.count("matrixRetired: true") < 1:
    raise RuntimeError("Matrix retirement migration flag is missing")

new_lines = len(source.splitlines())
retired_lines = base_lines - new_lines
if retired_lines < 1200:
    raise RuntimeError(f"Matrix retirement removed too little source: {retired_lines} lines")

for path in CANONICAL:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(source, encoding="utf-8")

validator = VALIDATOR.read_text(encoding="utf-8")
validator = replace_exact(
    validator,
    'MISSION_REQUIREMENTS_CONTRACT = ROOT / ".github" / "scripts" / "test_mission_requirements_contract.py"',
    'ISSUE391_MATRIX_RETIREMENT_CONTRACT = ROOT / ".github" / "scripts" / "test_issue391_matrix_retirement.py"',
    "validator retirement constant",
)
validator = validator.replace("MISSION_REQUIREMENTS_CONTRACT", "ISSUE391_MATRIX_RETIREMENT_CONTRACT")
validator = replace_exact(
    validator,
    "        mission_requirements = subprocess.run(\n            [sys.executable, str(ISSUE391_MATRIX_RETIREMENT_CONTRACT)],\n            cwd=ROOT,\n        )\n        if mission_requirements.returncode != 0:\n            fail(\"live mission requirements contract failed\")\n",
    "        matrix_retirement = subprocess.run(\n            [sys.executable, str(ISSUE391_MATRIX_RETIREMENT_CONTRACT)],\n            cwd=ROOT,\n        )\n        if matrix_retirement.returncode != 0:\n            fail(\"Issue #391 Matrix retirement contract failed\")\n",
    "validator retirement execution",
)
VALIDATOR.write_text(validator, encoding="utf-8")

preflight = PREFLIGHT.read_text(encoding="utf-8")
preflight = replace_exact(
    preflight,
    "  .github/scripts/test_mission_requirements_contract.py\n",
    "  .github/scripts/test_issue391_matrix_retirement.py\n",
    "preflight retirement contract",
)
PREFLIGHT.write_text(preflight, encoding="utf-8")

workflow = WORKFLOW.read_text(encoding="utf-8")
workflow = workflow.replace('      - ".github/fixtures/mission-requirements-contract.json"\n', '')
workflow = workflow.replace('      - ".github/scripts/test_mission_requirements_contract.py"\n', '      - ".github/scripts/test_issue391_matrix_retirement.py"\n')
workflow = workflow.replace('      - ".github/scripts/test_mission_requirements_runtime.js"\n', '')
WORKFLOW.write_text(workflow, encoding="utf-8")

headroom_test = HEADROOM_TEST.read_text(encoding="utf-8")
headroom_test = replace_exact(
    headroom_test,
    "    expected_source_lines = fixture[\"candidateSourceLines\"] + approved_total\n",
    "    retired_total = fixture.get(\"retiredNonStyleSourceLines\", 0)\n    if not isinstance(retired_total, int) or retired_total < 0:\n        fail(\"retired non-style source-line total is malformed\")\n    expected_source_lines = fixture[\"candidateSourceLines\"] + approved_total - retired_total\n",
    "headroom retirement accounting",
)
HEADROOM_TEST.write_text(headroom_test, encoding="utf-8")

shell_test = SHELL_TEST.read_text(encoding="utf-8")
shell_test = shell_test.replace(
    '"normaliser": "function normaliseOperationalWindowState(value, legacyMatrixEnabled = true)",',
    '"normaliser": "function normaliseOperationalWindowState(value, legacyRequirementsEnabled = true)",',
)
shell_test = shell_test.replace(
    '"legacy Matrix retained": "// Issue #133 clean-room live mission requirements matrix.",',
    '"legacy Matrix retired": "// Issue #391: legacy Mission Requirements Matrix retired; operationalWindow is authoritative.",',
)
shell_test = replace_exact(
    shell_test,
    "expected_lines = fixture['candidateSourceLines'] + fixture.get('approvedNonStyleSourceLines', 0)\n",
    "expected_lines = fixture['candidateSourceLines'] + fixture.get('approvedNonStyleSourceLines', 0) - fixture.get('retiredNonStyleSourceLines', 0)\n",
    "shell retirement accounting",
)
shell_test = shell_test.replace("source-headroom additive accounting", "source-headroom signed accounting")
SHELL_TEST.write_text(shell_test, encoding="utf-8")

renderer_test = RENDERER_TEST.read_text(encoding="utf-8")
renderer_test = renderer_test.replace(
    '    "if (typeof operationalRequirementsActive === \'function\' && operationalRequirementsActive()) { clearMissionRequirementsPanels(); return; }",\n',
    '',
)
renderer_test += "\nif '// Issue #133 clean-room live mission requirements matrix.' in source:\n    raise SystemExit('legacy Matrix marker survived renderer cutover')\n"
RENDERER_TEST.write_text(renderer_test, encoding="utf-8")

fixture = json.loads(HEADROOM_FIXTURE.read_text(encoding="utf-8"))
if fixture.get("expectedSourceLines") != base_lines:
    raise RuntimeError(f"headroom baseline drifted: {fixture.get('expectedSourceLines')} != {base_lines}")
fixture["retiredNonStyleSourceLines"] = retired_lines
fixture["retiredNonStyleChanges"] = [
    {"issue": 391, "phase": "legacy-mission-requirements-matrix", "lines": retired_lines}
]
fixture["expectedSourceLines"] = new_lines
HEADROOM_FIXTURE.write_text(json.dumps(fixture, indent=2) + "\n", encoding="utf-8")

RETIREMENT_TEST.write_text(f'''#!/usr/bin/env python3
from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
SOURCE = ROOT / "src" / "MissionChief_Map_Command_Toolkit.user.js"
source = SOURCE.read_text(encoding="utf-8")

required = [
    "// Issue #378 retained UK operational capability catalogue.",
    "// Issue #391: legacy Mission Requirements Matrix retired; operationalWindow is authoritative.",
    "const MISSION_REQUIREMENT_DEFINITIONS = Object.freeze([",
    "const MISSION_REQUIREMENTS_DEFAULT_STAFF_BY_TYPE =",
    "const MISSION_REQUIREMENTS_TRACTIVE_TYPES =",
    "function operationalRequirementCreateModel(input = {{}})",
    "function operationalRequirementsRenderContext(context)",
    "function operationalFeatureRenderContext(context)",
    "matrixRetired: true",
    "parsed?.missionRequirements",
    "function criticalMissionValueForEntry",
    "// Issue #153: stable live Toolkit version-status control.",
]
for marker in required:
    if marker not in source:
        raise SystemExit(f"Issue #391 required marker missing: {{marker}}")

for forbidden in [
    "// Issue #133 clean-room live mission requirements matrix.",
    "MISSION_REQUIREMENT_PARSE_DEFINITIONS",
    "function missionRequirementsParseText(",
    "function missionRequirementsResolve(",
    "function missionRequirementsEnsureRecord(",
    "function installMissionRequirementsWindows(",
    "function scanMissionRequirementsWindows(",
    "scheduleMissionRequirementsScan(",
    "clearMissionRequirementsPanels(",
    "missionRequirementsPanelId",
    "missionRequirementsDocumentStyleId",
    "data-mcms-requirements-panel",
    "state.missionRequirements",
    "merged.missionRequirements",
    "makeToggleButton('missionRequirements'",
]:
    if forbidden in source:
        raise SystemExit(f"Issue #391 legacy Matrix token survived: {{forbidden}}")

for name in (
    "MISSION_REQUIREMENT_DEFINITIONS",
    "MISSION_REQUIREMENTS_DEFAULT_STAFF_BY_TYPE",
    "MISSION_REQUIREMENTS_TRACTIVE_TYPES",
):
    if source.count(f"const {{name}} =") != 1:
        raise SystemExit(f"Issue #391 shared catalogue count changed: {{name}}")
if source.count("parsed?.missionRequirements") != 1:
    raise SystemExit("Issue #391 historical preference migration must occur exactly once")

for obsolete in (
    ROOT / ".github" / "scripts" / "test_mission_requirements_contract.py",
    ROOT / ".github" / "scripts" / "test_mission_requirements_runtime.js",
    ROOT / ".github" / "fixtures" / "mission-requirements-contract.json",
    ROOT / ".github" / "diagnostics" / "issue391-matrix-retirement-map.txt",
    ROOT / ".github" / "diagnostics" / "issue391-matrix-full-map.txt",
    ROOT / ".github" / "diagnostics" / "issue391-matrix-hook-map.txt",
):
    if obsolete.exists():
        raise SystemExit(f"Issue #391 obsolete Matrix artifact remains: {{obsolete.relative_to(ROOT)}}")

fixture = json.loads((ROOT / ".github" / "fixtures" / "main-style-source-headroom.json").read_text(encoding="utf-8"))
if fixture.get("retiredNonStyleSourceLines") != {retired_lines}:
    raise SystemExit("Issue #391 retirement source ledger changed")
if fixture.get("expectedSourceLines") != len(source.splitlines()):
    raise SystemExit("Issue #391 retired source line count is inconsistent")

uk = json.loads((ROOT / "src" / "data" / "mission-requirements-en_GB.json").read_text(encoding="utf-8"))
if uk.get("locale") != "en_GB" or len(uk.get("vehicleRequirements", [])) < 68:
    raise SystemExit("Issue #391 retained UK capability dataset is incomplete")

print("Issue #391 legacy Mission Requirements Matrix retirement contract passed.")
''', encoding="utf-8")

for obsolete in (OLD_CONTRACT, OLD_RUNTIME, OLD_FIXTURE, *DIAGNOSTICS):
    obsolete.unlink(missing_ok=True)

subprocess.run(["node", "--check", str(SOURCE)], cwd=ROOT, check=True)
subprocess.run(["python3", str(RETIREMENT_TEST)], cwd=ROOT, check=True)
subprocess.run(["python3", str(SHELL_TEST)], cwd=ROOT, check=True)
subprocess.run(["python3", str(RENDERER_TEST)], cwd=ROOT, check=True)
subprocess.run(["python3", str(HEADROOM_TEST)], cwd=ROOT, check=True)
subprocess.run(["bash", str(PREFLIGHT), "--contracts"], cwd=ROOT, check=True)
print(f"Issue #391 retired the legacy Matrix and removed {retired_lines} source lines.")
