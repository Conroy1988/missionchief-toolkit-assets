#!/usr/bin/env python3
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
OUTPUT = ROOT / ".github" / "reports" / "issue-86-release-pages-inspection.md"
TERMS = (
    "release-dashboard",
    "github-pages",
    "GitHub Pages Documentation",
    "workflow_dispatch",
    "repository_dispatch",
    "gh workflow",
    "actions/workflows",
    "Record successful release in dashboard",
)

sections = ["# Issue #86 release-to-Pages inspection", ""]
for path in sorted((ROOT / ".github" / "workflows").glob("*.y*ml")):
    text = path.read_text(encoding="utf-8")
    matches = []
    for number, line in enumerate(text.splitlines(), 1):
        if any(term.lower() in line.lower() for term in TERMS):
            start = max(1, number - 5)
            end = min(len(text.splitlines()), number + 8)
            excerpt = "\n".join(
                f"{index:04d}: {text.splitlines()[index - 1]}"
                for index in range(start, end + 1)
            )
            matches.append(excerpt)
    if not matches:
        continue
    sections.extend([
        f"## `{path.relative_to(ROOT)}`",
        "",
        "```text",
        "\n\n---\n\n".join(matches),
        "```",
        "",
    ])

OUTPUT.parent.mkdir(parents=True, exist_ok=True)
OUTPUT.write_text("\n".join(sections), encoding="utf-8")
print(f"Wrote {OUTPUT.relative_to(ROOT)}")
