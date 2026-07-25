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
HELP = ROOT / "help" / "index.html"
SELF = ROOT / ".github" / "issue519" / "apply_v713_optical_lift.py"
WORKFLOW = ROOT / ".github" / "workflows" / "apply-issue519-v713-optical-lift.yml"


def replace_once(text: str, old: str, new: str, label: str) -> str:
    count = text.count(old)
    if count != 1:
        raise SystemExit(f"Expected one {label}, found {count}")
    return text.replace(old, new, 1)


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


def main() -> int:
    source = SOURCE.read_text(encoding="utf-8")

    # Keep the structural flex containers stationary so nested metadata is not shifted twice.
    source = replace_once(
        source,
        "align-self:center!important;height:100%!important;line-height:1!important;margin-block:0!important;transform:none!important;",
        "align-self:center!important;height:100%!important;line-height:1!important;margin-block:0!important;",
        "stationary reel content container",
    )

    # Apply one optical lift to every visible leaf element in the wire.
    old_selector = '#${SCRIPT.majorIncidentFeedId} .mcms-incident-feed-label-title,#${SCRIPT.majorIncidentFeedId} .mcms-incident-name,#${SCRIPT.majorIncidentFeedId} .mcms-incident-state'
    new_selector = '#${SCRIPT.majorIncidentFeedId} .mcms-incident-feed-label-title,#${SCRIPT.majorIncidentFeedId} .mcms-incident-level,#${SCRIPT.majorIncidentFeedId} .mcms-incident-name,#${SCRIPT.majorIncidentFeedId} .mcms-incident-meta,#${SCRIPT.majorIncidentFeedId} .mcms-incident-state'
    source = replace_once(source, old_selector, new_selector, "visible wire text selector")
    source = replace_once(
        source,
        "align-self:center!important;line-height:1!important;margin-block:0!important;transform:none!important;",
        "align-self:center!important;line-height:1!important;margin-block:0!important;transform:translateY(-2px)!important;",
        "wire text optical lift",
    )
    source = replace_once(
        source,
        "align-self:center!important;margin-block:0!important;transform:none!important;",
        "align-self:center!important;margin-block:0!important;transform:translateY(-2px)!important;",
        "live count optical lift",
    )

    SOURCE.write_text(source, encoding="utf-8")

    static = STATIC.read_text(encoding="utf-8")
    marker = " assert source.count('align-self:center!important') >= 5\n"
    replacement = (
        " assert source.count('align-self:center!important') >= 5\n"
        " assert source.count('transform:translateY(-2px)!important') == 2\n"
        " assert '.mcms-incident-level' in source and '.mcms-incident-meta' in source\n"
        " assert 'height:100%!important;line-height:1!important;margin-block:0!important;transform:none!important' not in source\n"
    )
    static = replace_once(static, marker, replacement, "optical-lift static contract")
    STATIC.write_text(static, encoding="utf-8")

    changelog = CHANGELOG.read_text(encoding="utf-8")
    changelog = replace_once(
        changelog,
        "- Vertically centred the fixed label, live count, priority badge, mission title, metadata and response state across all seven themes and supported layouts.",
        "- Vertically centred the fixed label, live count, priority badge, mission title, metadata and response state, then applied a 2px upward optical baseline correction across all seven themes and supported layouts.",
        "v7.1.3 optical alignment changelog",
    )
    CHANGELOG.write_text(changelog, encoding="utf-8")

    help_text = HELP.read_text(encoding="utf-8")
    help_text = replace_once(
        help_text,
        "Its labels, badges and incident text are vertically centred throughout the command bar.",
        "Its labels, badges and incident text use a 2px upward optical correction for a visually centred command-bar baseline.",
        "Help Centre optical baseline notice",
    )
    HELP.write_text(help_text, encoding="utf-8")

    update_headroom(source)

    for path in (SELF, WORKFLOW):
        path.unlink(missing_ok=True)
    try:
        SELF.parent.rmdir()
    except OSError:
        pass

    print("v7.1.3 Incident Command Wire optical baseline corrected by 2px.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
