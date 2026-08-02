#!/usr/bin/env python3
from __future__ import annotations

import hashlib
import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
SOURCE = ROOT / "src" / "MissionChief_Map_Command_Toolkit.user.js"
CHANGELOG = ROOT / "CHANGELOG.md"
HEADROOM = ROOT / ".github" / "fixtures" / "main-style-source-headroom.json"
PERFORMANCE = ROOT / ".github" / "performance-budget.json"
HELP = ROOT / "help" / "index.html"
RUNTIME_TEST = ROOT / ".github" / "scripts" / "test_issue645_desktop_command_workspace_runtime.mjs"
STATIC_TEST = ROOT / ".github" / "scripts" / "test_issue645_desktop_command_workspace.py"
UPDATE_UI_TEST = ROOT / ".github" / "scripts" / "test_issue255_update_ui_write_suppression_runtime.mjs"
VERSION_CONTRACTS = [
    ROOT / ".github" / "scripts" / "test_toolkit_analytics_contract.py",
    ROOT / ".github" / "scripts" / "test_issue612_command_experience_contract.py",
    ROOT / ".github" / "scripts" / "test_issue614_quick_places_contract.py",
    ROOT / ".github" / "scripts" / "test_issue616_toolkit_doctor_contract.py",
    ROOT / ".github" / "scripts" / "test_issue618_command_palette_contract.py",
    ROOT / ".github" / "scripts" / "test_issue620_personalisation_contract.py",
    ROOT / ".github" / "scripts" / "test_issue622_command_experience_contract.py",
    ROOT / ".github" / "scripts" / "test_issue624_operational_map_flow_contract.py",
]
OLD_VERSION = "10.3.2"
NEW_VERSION = "10.3.3"


def replace_once(text: str, old: str, new: str, label: str) -> str:
    count = text.count(old)
    if count != 1:
        raise SystemExit(f"{label}: expected one match, found {count}")
    return text.replace(old, new, 1)


def main() -> int:
    source = SOURCE.read_text(encoding="utf-8")
    source = replace_once(source, f"// @version      {OLD_VERSION}", f"// @version      {NEW_VERSION}", "metadata version")
    source = replace_once(source, f"version: '{OLD_VERSION}',", f"version: '{NEW_VERSION}',", "runtime version")

    old_grid = """        const dockWidth = Math.min(1180, safeWidth);
        const safeLaunchWidth = Math.min(dockWidth, Math.max(56, Math.floor(finite(launchWidth) ? launchWidth : 117)));
        const contentWidth = Math.max(1, dockWidth - safeLaunchWidth - safeGap);
        const groupColumns = contentWidth >= 900 ? 4 : contentWidth >= 620 ? 3 : contentWidth >= 360 ? 2 : 1;
        const groupWidth = Math.max(1, Math.floor((contentWidth - (safeGap * Math.max(0, groupColumns - 1))) / groupColumns));
"""
    new_grid = """        const availableDockWidth = Math.min(1180, safeWidth);
        const safeLaunchWidth = Math.min(availableDockWidth, Math.max(56, Math.floor(finite(launchWidth) ? launchWidth : 117)));
        const availableContentWidth = Math.max(1, availableDockWidth - safeLaunchWidth - safeGap);
        const groupColumns = availableContentWidth >= 900 ? 4 : availableContentWidth >= 620 ? 3 : availableContentWidth >= 360 ? 2 : 1;
        const preferredGroupWidth = groupColumns >= 3 ? 210 : groupColumns === 2 ? 220 : availableContentWidth;
        const contentWidth = Math.min(
            availableContentWidth,
            (preferredGroupWidth * groupColumns) + (safeGap * Math.max(0, groupColumns - 1))
        );
        const dockWidth = Math.min(availableDockWidth, safeLaunchWidth + safeGap + contentWidth);
        const groupWidth = Math.max(1, Math.floor((contentWidth - (safeGap * Math.max(0, groupColumns - 1))) / groupColumns));
"""
    source = replace_once(source, old_grid, new_grid, "Desktop grid width resolver")
    source = replace_once(
        source,
        "size: dockWidth >= 1000 ? 'wide' : dockWidth >= 760 ? 'standard' : dockWidth >= 520 ? 'compact' : 'tight'",
        "size: availableDockWidth >= 1000 ? 'wide' : availableDockWidth >= 760 ? 'standard' : availableDockWidth >= 520 ? 'compact' : 'tight'",
        "Desktop density tier",
    )
    source = replace_once(source, "        contentWidth,\n        groupColumns,", "        contentWidth,\n        groupWidth,\n        groupColumns,", "Desktop grid evidence")
    SOURCE.write_text(source, encoding="utf-8")
    source_hash = hashlib.sha256(source.encode()).hexdigest()

    runtime = RUNTIME_TEST.read_text(encoding="utf-8")
    runtime = replace_once(
        runtime,
        """  assert.ok(grid.dockWidth <= scenario.width, `${scenario.name} exceeded the visible map width`);
  assert.equal(grid.groupColumns, scenario.columns, `${scenario.name} chose the wrong group grid`);
""",
        """  assert.ok(grid.dockWidth <= scenario.width, `${scenario.name} exceeded the visible map width`);
  assert.equal(grid.groupColumns, scenario.columns, `${scenario.name} chose the wrong group grid`);
  assert.ok(grid.groupWidth > 0, `${scenario.name} lost its command-group width`);
  if (scenario.columns >= 3) {
    assert.ok(grid.groupWidth <= 210, `${scenario.name} spread command groups beyond the compact Desktop track`);
    assert.equal(
      grid.contentWidth,
      (grid.groupWidth * grid.groupColumns) + (6 * (grid.groupColumns - 1)),
      `${scenario.name} left unused horizontal space inside the command cluster`,
    );
  }
  if (scenario.width >= 1200) assert.ok(grid.dockWidth <= 981, `${scenario.name} retained the over-wide Desktop deck`);
""",
        "Desktop runtime density assertions",
    )
    RUNTIME_TEST.write_text(runtime, encoding="utf-8")

    static = STATIC_TEST.read_text(encoding="utf-8")
    static = replace_once(
        static,
        """    layout = section("    function applyDesktopDockLayout(", "    function stopDesktopPanelWorkspaceObservation(")
    for fragment in (
""",
        """    resolver = section("    function resolveDesktopDockGrid(", "    function applyDesktopDockLayout(")
    layout = section("    function applyDesktopDockLayout(", "    function stopDesktopPanelWorkspaceObservation(")
    for fragment in (
        "preferredGroupWidth",
        "availableContentWidth",
        "groupWidth",
    ):
        assert fragment in resolver, f"compact Desktop resolver is missing {fragment}"
    for fragment in (
""",
        "Desktop static resolver scope",
    )
    STATIC_TEST.write_text(static, encoding="utf-8")

    update_ui = UPDATE_UI_TEST.read_text(encoding="utf-8")
    update_ui = replace_once(update_ui, f'const EXPECTED_VERSION = "{OLD_VERSION}";', f'const EXPECTED_VERSION = "{NEW_VERSION}";', "updateUI expected version")
    update_ui = re.sub(r'const EXPECTED_SHA = "[0-9a-f]{64}";', f'const EXPECTED_SHA = "{source_hash}";', update_ui, count=1)
    UPDATE_UI_TEST.write_text(update_ui, encoding="utf-8")

    for path in VERSION_CONTRACTS:
        text = path.read_text(encoding="utf-8")
        if OLD_VERSION not in text:
            raise SystemExit(f"Current-version contract missing {OLD_VERSION}: {path.relative_to(ROOT)}")
        path.write_text(text.replace(OLD_VERSION, NEW_VERSION), encoding="utf-8")

    help_text = HELP.read_text(encoding="utf-8")
    if help_text.count(OLD_VERSION) < 4:
        raise SystemExit(f"Help Centre current-version references are incomplete for {OLD_VERSION}")
    help_text = help_text.replace(OLD_VERSION, NEW_VERSION)
    help_text = replace_once(
        help_text,
        "The Desktop launcher and version tile remain reachable while four operational groups spread across the safe map width. Compact 36px buttons wrap cleanly, pinned locations use their own row, the Major Incident Wire remains reserved and scrolling is needed only for genuinely short workspaces.",
        "The Desktop launcher and version tile remain reachable while four operational groups form a compact content-sized cluster inside the safe map width. Compact 36px buttons remain readable, pinned locations align to the same cluster, the Major Incident Wire remains reserved and scrolling is needed only for genuinely short workspaces.",
        "Help Centre Desktop summary",
    )
    HELP.write_text(help_text, encoding="utf-8")

    changelog = CHANGELOG.read_text(encoding="utf-8")
    section_text = """## [10.3.3] - 2026-08-02

### Compact Desktop command workspace

- Caps wide-screen Desktop command groups at a compact 210px track instead of distributing every spare map pixel.
- Pulls Visibility, Intelligence, Dashboard and Performance into a denser content-sized cluster and aligns the EDI/NCL/WKFD/LDN shortcut strip to the same width.
- Preserves current 36px controls, labels, keyboard badges, four-group layout and adaptive three-, two- and one-column fallbacks.
- Leaves Tablet, iPad and iOS geometry unchanged and adds no request, timer, listener or observer.

"""
    changelog = replace_once(changelog, "# Changelog\n\n", "# Changelog\n\n" + section_text, "changelog insertion")
    CHANGELOG.write_text(changelog, encoding="utf-8")

    fixture = json.loads(HEADROOM.read_text(encoding="utf-8"))
    candidate = fixture["v10Candidate"]
    start = source.index("function installMainStyles()")
    template_start = source.index("addStyle(`", start) + len("addStyle(`")
    metric = source.index("recordStartupMetric('stylesheetInstallMs'", template_start)
    template_end = source.rfind("`);", template_start, metric)
    raw_template = source[template_start:template_end]
    template_lines = raw_template.split("\n")
    canonical = re.sub(r"\n[\t ]*}", "}", "\n".join(line for index, line in enumerate(template_lines) if not (0 < index < len(template_lines) - 1 and not line.strip())))
    previous_bytes = int(candidate["sourceBytes"])
    previous_lines = int(candidate["sourceLines"])
    candidate.update({
        "issue": 650,
        "version": NEW_VERSION,
        "sourceBytes": len(source.encode()),
        "sourceLines": len(source.splitlines()),
        "sourceSha256": source_hash,
        "templateBytes": len(raw_template.encode()),
        "templateLines": len(template_lines),
        "templateSha256": hashlib.sha256(raw_template.encode()).hexdigest(),
        "canonicalCssSha256": hashlib.sha256(canonical.encode()).hexdigest(),
        "baseline": OLD_VERSION,
        "approvedGrowth": {
            "sourceBytes": len(source.encode()) - previous_bytes,
            "sourceLines": len(source.splitlines()) - previous_lines,
            "templateBytes": 0,
            "templateLines": 0,
        },
        "scope": "Issue #650 compact content-sized Desktop command workspace tracks and aligned pinned shortcuts",
    })
    HEADROOM.write_text(json.dumps(fixture, indent=2) + "\n", encoding="utf-8")

    performance = json.loads(PERFORMANCE.read_text(encoding="utf-8"))
    prior = performance["transitionApproval"]
    history = performance.setdefault("approvalHistory", [])
    if not any(item.get("issue") == prior.get("issue") and item.get("version") == prior.get("version") for item in history):
        history.insert(0, prior)
    performance["revision"] = "2026-08-02-issue-650-compact-desktop-workspace-v10-3-3"
    performance["rationale"] = "Approve the Issue #650 content-sized Desktop command workspace using the existing fit lifecycle, with zero growth in request sites, observers, managed timers or managed listeners."
    performance["transitionApproval"] = {
        "issue": 650,
        "version": NEW_VERSION,
        "approvedNetworkRequestDelta": 0,
        "scope": "Issue #650: cap wide Desktop command tracks, compact the total workspace and align pinned shortcuts without reducing control readability or changing Tablet/iOS geometry.",
        "approvedMutationObserverDelta": 0,
        "approvedManagedListenerDelta": 0,
    }
    PERFORMANCE.write_text(json.dumps(performance, indent=2) + "\n", encoding="utf-8")

    print(f"Applied Issue #650 compact Desktop workspace package for v{NEW_VERSION} ({source_hash})")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
