#!/usr/bin/env python3
from __future__ import annotations

from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
SOURCE = ROOT / "src" / "MissionChief_Map_Command_Toolkit.user.js"
CHANGELOG = ROOT / "CHANGELOG.md"
RUNTIME_TEST = ROOT / ".github" / "scripts" / "test_issue645_desktop_command_workspace_runtime.mjs"
STATIC_TEST = ROOT / ".github" / "scripts" / "test_issue645_desktop_command_workspace.py"


def replace_once(text: str, old: str, new: str, label: str) -> str:
    count = text.count(old)
    if count != 1:
        raise SystemExit(f"{label}: expected one match, found {count}")
    return text.replace(old, new, 1)


def main() -> int:
    source = SOURCE.read_text(encoding="utf-8")
    source = replace_once(source, "// @version      10.3.1", "// @version      10.3.2", "metadata version")
    source = replace_once(source, "version: '10.3.1',", "version: '10.3.2',", "runtime version")

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
    source = replace_once(
        source,
        "        contentWidth,\n        groupColumns,",
        "        contentWidth,\n        groupWidth,\n        groupColumns,",
        "Desktop grid evidence",
    )
    SOURCE.write_text(source, encoding="utf-8")

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
        """        "mcmsDesktopDockSize",
        "mcmsDesktopDockScroll",
""",
        """        "mcmsDesktopDockSize",
        "mcmsDesktopDockScroll",
        "preferredGroupWidth",
        "availableContentWidth",
""",
        "Desktop static density contract",
    )
    STATIC_TEST.write_text(static, encoding="utf-8")

    changelog = CHANGELOG.read_text(encoding="utf-8")
    section = """## [10.3.2] - 2026-08-02

### Compact Desktop command workspace

- Keeps the v10.3.1 adaptive Desktop command surface while capping wide-screen command groups at a compact 210px track instead of distributing every spare map pixel.
- Pulls Visibility, Intelligence, Dashboard and Performance into a denser content-sized cluster and keeps the pinned EDI/NCL/WKFD/LDN strip aligned to the same workspace width.
- Preserves the current 36px control height, readable labels, keyboard badges, state text, four-group wide layout and adaptive three-, two- and one-column fallbacks.
- Leaves Tablet, iPad and iOS geometry unchanged and retains every dock position, Incident Wire reservation, zoom range, auto-hide, launcher, pins and short-map scrolling safeguard.
- Extends the existing Desktop runtime and static contracts to reject over-wide tracks and unused horizontal space without adding a request, timer, listener or observer.

"""
    changelog = replace_once(changelog, "# Changelog\n\n", "# Changelog\n\n" + section, "changelog insertion")
    CHANGELOG.write_text(changelog, encoding="utf-8")

    print("Applied Issue #650 compact Desktop workspace package for v10.3.2")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
