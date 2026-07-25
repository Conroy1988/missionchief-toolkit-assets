#!/usr/bin/env python3
from __future__ import annotations

import hashlib
import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
SOURCE = ROOT / "src" / "MissionChief_Map_Command_Toolkit.user.js"
FIXTURE = ROOT / ".github" / "fixtures" / "main-style-source-headroom.json"
CONTRACT = ROOT / ".github" / "scripts" / "test_issue517_incident_command_wire.py"
README = ROOT / "README.md"
SELF = ROOT / ".github" / "issue517" / "finalize_wire.py"
OLD_PATCH = ROOT / ".github" / "issue517" / "patch_budget.py"
WORKFLOW = ROOT / ".github" / "workflows" / "finalize-issue517-wire.yml"

COMPACT_CSS = r'''        /* v7.1.0 Incident Command Wire: bounded, theme-aware card navigation. */
        #${SCRIPT.majorIncidentFeedId}{--mcms-wire-accent:#68cfff;--mcms-wire-border:#467ca4;--mcms-wire-bg:#0a161f;--mcms-wire-bg2:#142734;--mcms-wire-label:linear-gradient(180deg,#24628e,#173e5b);--mcms-wire-text:#f4fbff;--mcms-wire-muted:#abc0cd;position:relative;height:44px!important;overflow:visible!important;border-color:var(--mcms-wire-border)!important;background:linear-gradient(180deg,var(--mcms-wire-bg2),var(--mcms-wire-bg))!important;color:var(--mcms-wire-text)!important}
        #${SCRIPT.majorIncidentFeedId} .mcms-incident-feed-label{min-width:148px!important;padding:0 9px!important;gap:7px!important;border-right:1px solid var(--mcms-wire-border)!important;background:var(--mcms-wire-label)!important}
        #${SCRIPT.majorIncidentFeedId} .mcms-incident-feed-label-title,#${SCRIPT.majorIncidentFeedId} .mcms-incident-name,#${SCRIPT.majorIncidentFeedId} .mcms-incident-state{overflow:hidden;text-overflow:ellipsis;white-space:nowrap}
        #${SCRIPT.majorIncidentFeedId} .mcms-incident-feed-count{flex:0 0 auto;min-width:34px;padding:3px 5px;border:1px solid currentColor;border-radius:999px;font-size:7px;line-height:1;text-align:center}
        #${SCRIPT.majorIncidentFeedId} .mcms-incident-feed-viewport{height:100%!important;min-width:0;overflow:hidden!important}
        #${SCRIPT.majorIncidentFeedId} .mcms-incident-feed-track{display:flex!important;align-items:stretch!important;width:100%!important;min-width:100%!important;height:100%!important;animation:none!important;will-change:transform;transition:transform .46s cubic-bezier(.22,.75,.18,1)!important}
        #${SCRIPT.majorIncidentFeedId} .mcms-incident-feed-item{flex:0 0 100%!important;width:100%!important;min-width:100%!important;height:100%!important;padding:0 12px!important;gap:9px!important;overflow:hidden!important;border:0!important;border-left:3px solid var(--mcms-wire-accent)!important;background:linear-gradient(90deg,rgba(104,207,255,.08),transparent 30%)!important}
        #${SCRIPT.majorIncidentFeedId} .mcms-incident-feed-copy,#${SCRIPT.majorIncidentFeedId} .mcms-incident-meta{min-width:0;display:flex;align-items:center;gap:7px;overflow:hidden}
        #${SCRIPT.majorIncidentFeedId} .mcms-incident-feed-copy{flex:1 1 auto}.mcms-incident-feed-meta{color:var(--mcms-wire-muted)}
        #${SCRIPT.majorIncidentFeedId} .mcms-incident-name{min-width:80px;max-width:52%;color:var(--mcms-wire-text)!important}
        #${SCRIPT.majorIncidentFeedId} .mcms-incident-meta{color:var(--mcms-wire-muted)!important}#${SCRIPT.majorIncidentFeedId} .mcms-incident-postcode{color:var(--mcms-wire-accent)!important}
        #${SCRIPT.majorIncidentFeedId} .mcms-incident-state{flex:0 0 auto;max-width:180px}
        #${SCRIPT.majorIncidentFeedId} .mcms-incident-feed-controls{position:relative;z-index:7;flex:0 0 auto;align-self:stretch;display:flex;align-items:center;gap:3px;padding:0 5px;border-left:1px solid var(--mcms-wire-border);background:rgba(0,0,0,.12)}
        #${SCRIPT.majorIncidentFeedId} .mcms-incident-feed-controls button{appearance:none;display:grid;place-items:center;width:27px;height:27px;min-width:27px;padding:0;border:1px solid var(--mcms-wire-border);border-radius:5px;background:rgba(255,255,255,.055);color:var(--mcms-wire-text);font:900 13px/1 Arial,sans-serif;cursor:pointer}
        #${SCRIPT.majorIncidentFeedId} .mcms-incident-feed-controls button:hover,#${SCRIPT.majorIncidentFeedId} .mcms-incident-feed-controls button:focus-visible,#${SCRIPT.majorIncidentFeedId} .mcms-incident-feed-controls [aria-pressed="true"]{background:var(--mcms-wire-accent);color:#09131a;outline:1px solid var(--mcms-wire-accent)}
        #${SCRIPT.majorIncidentFeedId} .mcms-incident-feed-panel{position:absolute;z-index:12;top:calc(100% + 5px);right:0;width:min(860px,calc(100vw - 18px));max-height:min(58vh,520px);overflow:hidden;border:1px solid var(--mcms-wire-border);border-radius:9px;background:linear-gradient(180deg,var(--mcms-wire-bg2),var(--mcms-wire-bg));box-shadow:0 15px 38px rgba(0,0,0,.52);color:var(--mcms-wire-text)}
        #${SCRIPT.majorIncidentFeedId} .mcms-incident-feed-panel[hidden]{display:none!important}
        #${SCRIPT.majorIncidentFeedId} .mcms-incident-feed-panel-head{display:flex;justify-content:space-between;align-items:center;gap:12px;padding:11px 13px;border-bottom:1px solid var(--mcms-wire-border)}
        #${SCRIPT.majorIncidentFeedId} .mcms-incident-feed-list{display:grid;gap:5px;max-height:calc(min(58vh,520px) - 43px);padding:7px;overflow:auto}
        #${SCRIPT.majorIncidentFeedId} .mcms-incident-feed-list-item{flex:none!important;width:100%!important;min-width:0!important;min-height:54px!important;height:auto!important;padding:8px 11px!important;border:1px solid var(--mcms-wire-border)!important;border-left:4px solid var(--mcms-wire-accent)!important;border-radius:6px!important;background:rgba(255,255,255,.025)!important}
        #${SCRIPT.majorIncidentFeedId} .mcms-incident-feed-list-item .mcms-incident-feed-copy{flex-direction:column;align-items:flex-start;gap:4px}#${SCRIPT.majorIncidentFeedId} .mcms-incident-feed-list-empty{padding:22px;color:var(--mcms-wire-muted);text-align:center}
        html[data-mcms-ui-theme="cyberpunk"] #${SCRIPT.majorIncidentFeedId}{--mcms-wire-accent:#00f0ff;--mcms-wire-border:#fcee0a;--mcms-wire-bg:#080d12;--mcms-wire-bg2:#10151b;--mcms-wire-label:#fcee0a;--mcms-wire-text:#f8ffff;--mcms-wire-muted:#9dd8dc}
        html[data-mcms-ui-theme="fallout4"] #${SCRIPT.majorIncidentFeedId}{--mcms-wire-accent:#9af26f;--mcms-wire-border:#78d85b;--mcms-wire-bg:#0b140d;--mcms-wire-bg2:#172419;--mcms-wire-label:#254326;--mcms-wire-text:#d9ffc7;--mcms-wire-muted:#9edb88}
        html[data-mcms-ui-theme="umbrella"] #${SCRIPT.majorIncidentFeedId}{--mcms-wire-accent:#ff4b57;--mcms-wire-border:#d82632;--mcms-wire-bg:#101216;--mcms-wire-bg2:#1d2025;--mcms-wire-label:#b1121c;--mcms-wire-text:#fff;--mcms-wire-muted:#c9cdd2}
        html[data-mcms-ui-theme="factorio"] #${SCRIPT.majorIncidentFeedId}{--mcms-wire-accent:#f6a34c;--mcms-wire-border:#d87822;--mcms-wire-bg:#20211e;--mcms-wire-bg2:#34352f;--mcms-wire-label:#6b421f;--mcms-wire-text:#fff3df;--mcms-wire-muted:#d9c8aa}
        html[data-mcms-ui-theme="bond007"] #${SCRIPT.majorIncidentFeedId}{--mcms-wire-accent:#d8bd72;--mcms-wire-border:#b99a4f;--mcms-wire-bg:#07080a;--mcms-wire-bg2:#1b1d20;--mcms-wire-label:#d8bd72;--mcms-wire-text:#f5efe2;--mcms-wire-muted:#b7babd}
        html[data-mcms-ui-theme="hyrule"] #${SCRIPT.majorIncidentFeedId}{--mcms-wire-accent:#59e3df;--mcms-wire-border:#d5b85a;--mcms-wire-bg:#07171c;--mcms-wire-bg2:#123039;--mcms-wire-label:#1b574f;--mcms-wire-text:#f4f0d8;--mcms-wire-muted:#b7d8ce}
        html[data-mcms-ui-theme="cyberpunk"] #${SCRIPT.majorIncidentFeedId} .mcms-incident-feed-label,html[data-mcms-ui-theme="bond007"] #${SCRIPT.majorIncidentFeedId} .mcms-incident-feed-label{color:#111!important}
        @media (max-width:760px){#${SCRIPT.majorIncidentFeedId} .mcms-incident-feed-label{min-width:104px!important}#${SCRIPT.majorIncidentFeedId} .mcms-incident-meta{display:none}#${SCRIPT.majorIncidentFeedId} .mcms-incident-feed-controls button{width:32px;height:32px;min-width:32px}}
        @media (max-width:480px){#${SCRIPT.majorIncidentFeedId}{height:42px!important}#${SCRIPT.majorIncidentFeedId} .mcms-incident-feed-label-title{display:none}#${SCRIPT.majorIncidentFeedId} .mcms-incident-feed-label{min-width:42px!important}#${SCRIPT.majorIncidentFeedId} .mcms-incident-feed-state{max-width:92px}}
'''


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
        "\n".join(line for index, line in enumerate(lines) if not (0 < index < len(lines) - 1 and not line.strip())),
    )
    fixture = json.loads(FIXTURE.read_text(encoding="utf-8"))
    fixture["v7Candidate"].update({
        "issue": 517,
        "version": "7.1.0",
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
    marker = "        /* v7.1.0 Incident Command Wire: bounded card rotation with a manual, theme-aware fallback. */"
    start = source.index(marker)
    end = source.index("        `);", start)
    source = source[:start] + COMPACT_CSS + source[end:]

    source = replace_once(
        source,
        "track.innerHTML = entries.map(entry => majorIncidentFeedItemHtml(entry, 'wire')).join('');",
        "track.replaceChildren(document.createRange().createContextualFragment(entries.map(entry => majorIncidentFeedItemHtml(entry, 'wire')).join('')));",
        "wire innerHTML assignment",
    )
    source = replace_once(
        source,
        "list.innerHTML = entries.map(entry => majorIncidentFeedItemHtml(entry, 'list')).join('');",
        "list.replaceChildren(document.createRange().createContextualFragment(entries.map(entry => majorIncidentFeedItemHtml(entry, 'list')).join('')));",
        "list innerHTML assignment",
    )
    SOURCE.write_text(source, encoding="utf-8")

    contract = CONTRACT.read_text(encoding="utf-8")
    contract = replace_once(
        contract,
        "assert \"track.innerHTML = entries.map(entry => majorIncidentFeedItemHtml(entry, 'wire')).join('');\" in render",
        "assert \"track.replaceChildren(document.createRange().createContextualFragment(entries.map(entry => majorIncidentFeedItemHtml(entry, 'wire')).join('')));\" in render",
        "wire contract assertion",
    )
    contract = replace_once(
        contract,
        "assert \"list.innerHTML = entries.map(entry => majorIncidentFeedItemHtml(entry, 'list')).join('');\" in render",
        "assert \"list.replaceChildren(document.createRange().createContextualFragment(entries.map(entry => majorIncidentFeedItemHtml(entry, 'list')).join('')));\" in render",
        "list contract assertion",
    )
    contract = contract.replace("assert 'mcmsIncidentWireScroll' not in render", "assert 'mcmsIncidentWireScroll' not in render\n    assert 'innerHTML = entries.map' not in render")
    CONTRACT.write_text(contract, encoding="utf-8")

    readme = README.read_text(encoding="utf-8")
    pattern = re.compile(r"## \*\*Current verified release: `v[^`]+`[^\n]*\*\*")
    readme, count = pattern.subn(
        "## **Current verified release: `v7.0.1` · Development candidate: `v7.1.0` — Incident Command Wire**",
        readme,
        count=1,
    )
    if count != 1:
        raise SystemExit(f"Expected one README release marker, found {count}")
    README.write_text(readme, encoding="utf-8")

    update_headroom(source)

    for path in (SELF, OLD_PATCH, WORKFLOW):
        path.unlink(missing_ok=True)
    try:
        SELF.parent.rmdir()
    except OSError:
        pass
    print("Issue #517 final performance and candidate reconciliation applied.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
