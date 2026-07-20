#!/usr/bin/env python3
from pathlib import Path
import textwrap

ROOT = Path(__file__).resolve().parents[2]
SOURCE = ROOT / "src/MissionChief_Map_Command_Toolkit.user.js"
OUTPUT = ROOT / "docs/issue-273-resolve-wrapped.txt"


def function_block(text: str, name: str) -> str:
    marker = f"function {name}("
    start = text.find(marker)
    if start < 0:
        return f"MISSING {name}"
    brace = text.find("{", start)
    depth = 0
    quote = None
    escape = False
    for index in range(brace, len(text)):
        char = text[index]
        if quote:
            if escape:
                escape = False
            elif char == "\\":
                escape = True
            elif char == quote:
                quote = None
            continue
        if char in "'\"`":
            quote = char
            continue
        if char == "{":
            depth += 1
        elif char == "}":
            depth -= 1
            if depth == 0:
                return text[start:index + 1]
    raise RuntimeError(name)


def wrap(code: str) -> str:
    code = code.replace("; ", ";\n").replace(" { const ", " {\nconst ").replace(" } if ", "\n}\nif ").replace(" } return ", "\n}\nreturn ").replace("; const ", ";\nconst ").replace("; let ", ";\nlet ")
    lines = []
    for line in code.splitlines():
        lines.extend(textwrap.wrap(line, width=180, replace_whitespace=False, drop_whitespace=False) if len(line) > 180 else [line])
    return "\n".join(lines)


def main() -> None:
    source = SOURCE.read_text(encoding="utf-8")
    sections = []
    for name in [
        "missionRequirementsParseText",
        "missionRequirementsCatalogueRequirement",
        "missionRequirementsReconcileCatalogue",
        "missionRequirementsCapacity",
        "missionRequirementsCapacityText",
        "missionRequirementsCoverageRow",
        "missionRequirementsResolve",
        "scanMissionRequirementsWindows",
    ]:
        sections.append(f"=== {name} ===\n{wrap(function_block(source, name))}")
    contexts = []
    token = "requiredCapacity"
    start = 0
    while True:
        pos = source.find(token, start)
        if pos < 0:
            break
        contexts.append(source[max(0, pos - 600):pos + 900])
        start = pos + len(token)
    sections.append("=== requiredCapacity contexts ===\n" + "\n---\n".join(wrap(item) for item in contexts))
    OUTPUT.write_text("\n\n".join(sections) + "\n", encoding="utf-8")
    print(f"wrote {OUTPUT.relative_to(ROOT)}")


if __name__ == "__main__":
    main()
