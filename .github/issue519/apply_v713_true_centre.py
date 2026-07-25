#!/usr/bin/env python3
from __future__ import annotations

import hashlib
import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
SOURCE = ROOT / "src" / "MissionChief_Map_Command_Toolkit.user.js"
STATIC = ROOT / ".github" / "scripts" / "test_issue517_incident_command_wire.py"
FIXTURE = ROOT / ".github" / "fixtures" / "main-style-source-headroom.json"
CHANGELOG = ROOT / "CHANGELOG.md"
SELF = ROOT / ".github" / "issue519" / "apply_v713_true_centre.py"
WORKFLOW = ROOT / ".github" / "workflows" / "apply-issue519-v713-true-centre.yml"


def mutate_css_block(source: str, selector: str, mutator, label: str) -> str:
    pattern = re.compile(rf"({re.escape(selector)}\{{)([^}}]*)(\}})")
    source, count = pattern.subn(
        lambda match: f"{match.group(1)}{mutator(match.group(2))}{match.group(3)}",
        source,
        count=1,
    )
    if count != 1:
        raise SystemExit(f"Expected one {label} CSS block, found {count}")
    return source


def update_headroom(source: str) -> None:
    start = source.index("function installMainStyles()")
    template_start = source.index("addStyle(`", start) + len("addStyle(`")
    metric = source.index("recordStartupMetric('stylesheetInstallMs'", template_start)
    template_end = source.rfind("`);", template_start, metric)
    raw = source[template_start:template_end]
    lines = raw.split("\n")
    canonical = re.sub(
        r"\n[\t ]*}",
        "}",
        "\n".join(
            line
            for index, line in enumerate(lines)
            if not (0 < index < len(lines) - 1 and not line.strip())
        ),
    )
    fixture = json.loads(FIXTURE.read_text(encoding="utf-8"))
    fixture["v7Candidate"].update({
        "issue": 519,
        "version": "7.1.3",
        "sourceBytes": len(source.encode("utf-8")),
        "sourceLines": len(source.splitlines()),
        "sourceSha256": hashlib.sha256(source.encode("utf-8")).hexdigest(),
        "templateBytes": len(raw.encode("utf-8")),
        "templateLines": len(lines),
        "templateSha256": hashlib.sha256(raw.encode("utf-8")).hexdigest(),
        "canonicalCssSha256": hashlib.sha256(canonical.encode("utf-8")).hexdigest(),
    })
    FIXTURE.write_text(json.dumps(fixture, indent=2) + "\n", encoding="utf-8")


def centred_padding(body: str) -> str:
    body = body.replace("padding-top:0!important;", "")
    body = body.replace("padding-bottom:0!important;", "")
    body = body.replace("padding-bottom:12px!important;", "")
    body = body.replace("box-sizing:border-box!important;", "")
    return body + "padding-top:0!important;padding-bottom:14px!important;box-sizing:border-box!important;"


def main() -> int:
    source = SOURCE.read_text(encoding="utf-8")

    lift_count = source.count("transform:translateY(-2px)!important")
    if lift_count != 2:
        raise SystemExit(f"Expected two obsolete 2px optical transforms, found {lift_count}")
    source = source.replace("transform:translateY(-2px)!important", "transform:none!important")

    source = mutate_css_block(
        source,
        '#${SCRIPT.majorIncidentFeedId} .mcms-incident-feed-label',
        centred_padding,
        "fixed label",
    )
    source = mutate_css_block(
        source,
        '#${SCRIPT.majorIncidentFeedId} .mcms-incident-feed-item',
        centred_padding,
        "moving reel item",
    )

    SOURCE.write_text(source, encoding="utf-8")

    static = STATIC.read_text(encoding="utf-8")
    old = """ assert source.count('transform:translateY(-2px)!important') == 2
 assert '.mcms-incident-level' in source and '.mcms-incident-meta' in source
 assert 'height:100%!important;line-height:1!important;margin-block:0!important;transform:none!important' not in source
"""
    new = """ assert 'transform:translateY(-2px)!important' not in source
 assert source.count('padding-bottom:14px!important') == 2
 assert source.count('padding-top:0!important') >= 2
 assert source.count('box-sizing:border-box!important') >= 4
 assert '.mcms-incident-level' in source and '.mcms-incident-meta' in source
"""
    if static.count(old) != 1:
        raise SystemExit(f"Expected one obsolete optical-lift contract, found {static.count(old)}")
    STATIC.write_text(static.replace(old, new, 1), encoding="utf-8")

    changelog = CHANGELOG.read_text(encoding="utf-8")
    old_line = "- Vertically centred the fixed label, live count, priority badge, mission title, metadata and response state, then applied a 2px upward optical baseline correction across all seven themes and supported layouts."
    new_line = "- Centred the fixed label and complete moving incident row inside the full bar height using container-level asymmetric padding, eliminating the low text baseline across all seven themes and supported layouts."
    if changelog.count(old_line) != 1:
        raise SystemExit(f"Expected one obsolete changelog alignment line, found {changelog.count(old_line)}")
    CHANGELOG.write_text(changelog.replace(old_line, new_line, 1), encoding="utf-8")

    update_headroom(source)

    for path in (SELF, WORKFLOW):
        path.unlink(missing_ok=True)
    try:
        SELF.parent.rmdir()
    except OSError:
        pass

    print("v7.1.3 true vertical-centre correction applied.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
