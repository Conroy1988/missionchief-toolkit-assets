#!/usr/bin/env python3
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
SOURCE = (ROOT / "src" / "MissionChief_Map_Command_Toolkit.user.js").read_text(encoding="utf-8")
PREFLIGHT = (ROOT / ".github" / "scripts" / "run_userscript_preflight.sh").read_text(encoding="utf-8")


def section(start: str, end: str) -> str:
    left = SOURCE.index(start)
    return SOURCE[left:SOURCE.index(end, left)]


def main() -> int:
    resolver = section("    function resolveDesktopDockGrid(", "    function clearDesktopDockSizing(")
    for fragment in (
        "Math.min(1680, safeWidth)",
        "groupWidthForColumns",
        "measurePinTrack",
        "candidates.sort",
        "pinsInline",
        "groupWidths",
    ):
        assert fragment in resolver, f"wide Desktop allocator is missing {fragment}"

    layout = section("    function clearDesktopDockSizing(", "    function stopDesktopPanelWorkspaceObservation(")
    for fragment in (
        "--mcms-desktop-content-width",
        "--mcms-desktop-filter-width",
        "--mcms-desktop-group-width",
        "--mcms-desktop-pin-width",
        "mcmsDesktopPinsInline",
    ):
        assert fragment in layout, f"wide Desktop renderer is missing {fragment}"
    assert "ResizeObserver" not in layout and "setInterval" not in layout

    for fragment in (
        'grid-template-areas:"menu filters pins"',
        "var(--mcms-desktop-filter-width,858px)",
        "var(--mcms-desktop-group-width,210px)",
        "var(--mcms-desktop-pin-width,100%)",
        'data-mcms-desktop-pins-inline="true"',
    ):
        assert fragment in SOURCE, f"wide Desktop CSS is missing {fragment}"

    assert ".github/scripts/test_issue664_wide_desktop_command_band.py" in PREFLIGHT
    assert "node .github/scripts/test_issue664_wide_desktop_command_band_runtime.mjs" in PREFLIGHT
    print("Issue #664 wide Desktop command band static contract passed.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
