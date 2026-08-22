#!/usr/bin/env python3
from __future__ import annotations

from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
SOURCE = (ROOT / "src" / "MissionChief_Map_Command_Toolkit.user.js").read_text(encoding="utf-8")
RUNTIME = ROOT / ".github" / "scripts" / "test_issue638_command_shell_route_runtime.mjs"


def section(start: str, end: str) -> str:
    left = SOURCE.index(start)
    right = SOURCE.index(end, left)
    return SOURCE[left:right]


def main() -> int:
    helpers = [
        "toolkitTopLevelDocument",
        "toolkitDocumentPathname",
        "toolkitCommandShellRouteEligible",
        "toolkitPrimaryMapElement",
        "toolkitControlHost",
        "toolkitCommandShellContextActive",
        "teardownToolkitCommandShell",
        "reconcileToolkitCommandShellRoute",
        "queueToolkitCommandShellRouteReconcile",
        "installToolkitCommandShellNavigationHooks",
    ]
    for helper in helpers:
        assert SOURCE.count(f"function {helper}(") == 1, f"{helper} declaration count changed"

    host = section("    function toolkitControlHost(", "    function toolkitCommandShellContextActive(")
    assert "return toolkitPrimaryMapElement(mapEl, doc);" in host
    assert "doc?.body" not in host and "doc?.documentElement" not in host

    primary = section("    function toolkitPrimaryMapElement(", "    function toolkitControlHost(")
    assert "toolkitCommandShellRouteEligible(doc)" in primary
    assert "#map_outer" in primary
    assert "canonicalLeafletMap" in primary
    assert "candidate.closest?.(missionSelector)" in primary

    ensure = section("    function ensureUi()", "    let toolkitCommandShellRouteReconcileQueued")
    assert "if (!toolkitCommandShellRouteEligible(document))" in ensure
    assert "teardownToolkitCommandShell('route is not the canonical top-level map')" in ensure
    assert "if (!mapEl)" in ensure
    assert "canonical map has not been positively identified" in ensure

    keyboard = section("    function handleKeyboard(", "    function buildThemeOptions(")
    assert "if (!toolkitCommandShellContextActive())" in keyboard
    assert "teardownToolkitCommandShell('keyboard event outside canonical map context')" in keyboard

    navigation = section("    function installToolkitCommandShellNavigationHooks(", "    function mutationBelongsToToolkit(")
    assert "['pushState', 'replaceState']" in navigation
    assert "queueToolkitCommandShellRouteReconcile" in navigation
    assert "runtime.hookRestorers.push" in navigation
    assert "MutationObserver" not in navigation
    assert "setInterval" not in navigation

    assert RUNTIME.is_file()
    preflight = (ROOT / ".github" / "scripts" / "run_userscript_preflight.sh").read_text(encoding="utf-8")
    assert str(RUNTIME.relative_to(ROOT)) in preflight
    print("Issue #638 command-shell route ownership static contract passed.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
