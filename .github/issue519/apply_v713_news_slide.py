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
SELF = ROOT / ".github" / "issue519" / "apply_v713_news_slide.py"
WORKFLOW = ROOT / ".github" / "workflows" / "apply-issue519-v713-news-slide.yml"


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
    source = replace_once(
        source,
        "transition:transform .46s cubic-bezier(.22,.75,.18,1)!important",
        "transition:transform .85s cubic-bezier(.22,.75,.18,1)!important",
        "Incident Wire base slide transition",
    )
    source = replace_once(
        source,
        "@media (prefers-reduced-motion:reduce){#${SCRIPT.majorIncidentFeedId} .mcms-incident-feed-track{transition:none!important}}",
        "@media (prefers-reduced-motion:reduce){#${SCRIPT.majorIncidentFeedId} .mcms-incident-feed-track{transition:transform .85s cubic-bezier(.22,.75,.18,1)!important}}",
        "reduced-motion instant override",
    )
    SOURCE.write_text(source, encoding="utf-8")

    static = STATIC.read_text(encoding="utf-8")
    static = replace_once(
        static,
        "    assert '.mcms-incident-feed-track{transition:none!important}' in source\n",
        "    assert source.count('transition:transform .85s cubic-bezier(.22,.75,.18,1)!important') == 2\n"
        "    assert 'mcms-incident-feed-track{transition:none!important}' not in source\n",
        "news-slide static assertion",
    )
    STATIC.write_text(static, encoding="utf-8")

    changelog = CHANGELOG.read_text(encoding="utf-8")
    changelog = replace_once(
        changelog,
        "- Disabled the sliding track transition under reduced motion so cards change instantly without motion animation.",
        "- Restored a smooth 0.85-second horizontal news-banner slide so the outgoing incident exits left while the next incident enters from the right.",
        "v7.1.3 changelog animation line",
    )
    CHANGELOG.write_text(changelog, encoding="utf-8")

    help_text = HELP.read_text(encoding="utf-8")
    help_text = replace_once(
        help_text,
        "Reduced-motion mode now removes the sliding animation without disabling automatic incident progression. Play remains active and cards change instantly at the normal cadence.",
        "Automatic progression now uses a smooth horizontal news-banner slide even when the browser reports reduced motion. Pause remains the authoritative control and stops the wire immediately.",
        "Help Centre v7.1.3 notice",
    )
    HELP.write_text(help_text, encoding="utf-8")

    update_headroom(source)

    for path in (SELF, WORKFLOW):
        path.unlink(missing_ok=True)
    try:
        SELF.parent.rmdir()
    except OSError:
        pass

    print("v7.1.3 Incident Command Wire news-slide candidate applied.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
