#!/usr/bin/env python3
from __future__ import annotations

from pathlib import Path
import json
import subprocess

ROOT = Path(__file__).resolve().parents[2]
SOURCE = ROOT / "src" / "MissionChief_Map_Command_Toolkit.user.js"
RUNTIME = ROOT / ".github" / "scripts" / "test_mission_requirements_runtime.js"
CONTRACT = ROOT / ".github" / "scripts" / "test_mission_requirements_contract.py"
FIXTURE = ROOT / ".github" / "fixtures" / "mission-requirements-contract.json"
OUTPUT = ROOT / "docs" / "diagnostics" / "issue-167-source-extract.txt"


def extract_function(text: str, name: str) -> str:
    marker = f"    function {name}("
    start = text.find(marker)
    if start < 0:
        raise AssertionError(f"missing function: {name}")
    brace = text.find("{", start)
    if brace < 0:
        raise AssertionError(f"missing opening brace: {name}")
    depth = 0
    quote = None
    escaped = False
    template_depth = 0
    i = brace
    while i < len(text):
        ch = text[i]
        nxt = text[i + 1] if i + 1 < len(text) else ""
        if quote:
            if escaped:
                escaped = False
            elif ch == "\\":
                escaped = True
            elif quote == "`" and ch == "$" and nxt == "{":
                template_depth += 1
                i += 1
            elif quote == "`" and ch == "}" and template_depth:
                template_depth -= 1
            elif ch == quote and not template_depth:
                quote = None
        else:
            if ch in ("'", '"', "`"):
                quote = ch
            elif ch == "/" and nxt == "/":
                end = text.find("\n", i + 2)
                i = len(text) if end < 0 else end
                continue
            elif ch == "/" and nxt == "*":
                end = text.find("*/", i + 2)
                if end < 0:
                    raise AssertionError(f"unterminated comment in {name}")
                i = end + 2
                continue
            elif ch == "{":
                depth += 1
            elif ch == "}":
                depth -= 1
                if depth == 0:
                    return text[start:i + 1]
        i += 1
    raise AssertionError(f"unterminated function: {name}")


source = SOURCE.read_text(encoding="utf-8")
runtime = RUNTIME.read_text(encoding="utf-8")
contract = CONTRACT.read_text(encoding="utf-8")
fixture = json.loads(FIXTURE.read_text(encoding="utf-8"))
functions = [
    "missionRequirementsCoverageRow",
    "missionRequirementsCollectUnits",
    "missionRequirementsUnitContribution",
    "missionRequirementsAggregate",
    "missionRequirementsProgressValue",
    "missionRequirementsResolve",
    "missionRequirementsOverallState",
    "missionRequirementsDocumentCss",
    "missionRequirementsPanelHtml",
    "missionRequirementsReportUrl",
    "missionRequirementsRenderRecord",
    "observeMissionRequirementsDocument",
]
sections = ["# Issue #167 source extract", ""]
for name in functions:
    sections.extend([f"## {name}", "```javascript", extract_function(source, name), "```", ""])

for marker, label in [
    ("const equipmentRow =", "runtime capacity and lifecycle tests"),
    ("function makeMissionCandidate(doc", "runtime mission candidate fixtures"),
]:
    start = runtime.find(marker)
    if start < 0:
        raise AssertionError(f"missing runtime marker: {marker}")
    end = runtime.find("\nconst missingDoc =", start)
    if end < 0:
        end = min(len(runtime), start + 14000)
    sections.extend([f"## {label}", "```javascript", runtime[start:end], "```", ""])

sections.extend([
    "## Fixture JSON",
    "```json",
    json.dumps(fixture, indent=2, ensure_ascii=False),
    "```",
    "",
    "## Contract test",
    "```python",
    contract,
    "```",
    "",
])
OUTPUT.parent.mkdir(parents=True, exist_ok=True)
OUTPUT.write_text("\n".join(sections), encoding="utf-8")
subprocess.run(["node", "--check", str(SOURCE.relative_to(ROOT))], cwd=ROOT, check=True)
print(f"Issue #167 diagnostic written: {OUTPUT.relative_to(ROOT)}")
