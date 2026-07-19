#!/usr/bin/env python3
from pathlib import Path
import subprocess

ROOT = Path(__file__).resolve().parents[2]
SOURCE = ROOT / "src" / "MissionChief_Map_Command_Toolkit.user.js"
OUTPUT = ROOT / "status" / "issue-226-operational-diagnostic.txt"


def extract_function(source: str, name: str) -> str:
    marker = f"function {name}"
    start = source.find(marker)
    if start < 0:
        raise AssertionError(f"{marker} not found")
    brace = source.find("{", start)
    if brace < 0:
        raise AssertionError(f"{marker} opening brace not found")
    depth = 0
    quote = None
    escaped = False
    template_expression_depth = 0
    for index in range(brace, len(source)):
        char = source[index]
        if escaped:
            escaped = False
            continue
        if char == "\\":
            escaped = True
            continue
        if quote:
            if quote == "`" and char == "$" and index + 1 < len(source) and source[index + 1] == "{":
                template_expression_depth += 1
                continue
            if char == quote and template_expression_depth == 0:
                quote = None
            elif quote == "`" and char == "}" and template_expression_depth:
                template_expression_depth -= 1
            continue
        if char in ("'", '"', "`"):
            quote = char
            continue
        if char == "{":
            depth += 1
        elif char == "}":
            depth -= 1
            if depth == 0:
                return source[start:index + 1]
    raise AssertionError(f"{marker} closing brace not found")


source = SOURCE.read_text(encoding="utf-8")
functions = [
    "missionRequirementsOperationalSelectors",
    "missionRequirementsOperationalWindowScopes",
    "missionRequirementsOperationalElementActive",
    "missionRequirementsCollectUnits",
    "missionRequirementsResolve",
]
parts = ["Issue #226 operational collector diagnostic", ""]
for name in functions:
    parts.extend([f"===== {name} =====", extract_function(source, name), ""])
OUTPUT.parent.mkdir(parents=True, exist_ok=True)
OUTPUT.write_text("\n".join(parts), encoding="utf-8")
subprocess.run(["node", "--check", str(SOURCE.relative_to(ROOT))], cwd=ROOT, check=True)
print("Issue #226 operational diagnostic extracted")
