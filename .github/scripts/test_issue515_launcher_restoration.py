#!/usr/bin/env python3
from __future__ import annotations
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
SOURCE = ROOT / "src" / "MissionChief_Map_Command_Toolkit.user.js"


def section(text: str, start: str, end: str) -> str:
    left = text.index(start)
    right = text.index(end, left)
    return text[left:right]


def main() -> int:
    source = SOURCE.read_text(encoding="utf-8")
    metadata = re.search(r"(?m)^//\s*@version\s+([^\s]+)$", source)
    runtime = re.search(r"version:\s*'([^']+)'", source)
    assert metadata and runtime and metadata.group(1) == runtime.group(1)
    assert tuple(int(part) for part in metadata.group(1).split(".")[:3]) >= (7, 0, 1)

    helpers = [
        "toolkitTopLevelDocument",
        "toolkitDocumentPathname",
        "toolkitCommandShellRouteEligible",
        "toolkitPrimaryMapElement",
        "toolkitControlHost",
        "toolkitCommandShellContextActive",
        "teardownToolkitCommandShell",
        "toolkitApplyCommandBarState",
    ]
    for helper in helpers:
        assert source.count(f"function {helper}(") == 1, f"{helper} declaration count changed"

    toggle = source.index("    function toggleCommandBar()")
    for helper in helpers:
        assert source.index(f"    function {helper}(") < toggle, f"{helper} must exist before launcher use"

    create = section(source, "    function createControl(mapEl)", "    function createPanel()")
    assert "const primaryMap = toolkitPrimaryMapElement(mapEl, document);" in create
    assert "const host = toolkitControlHost(primaryMap, document);" in create
    assert "if (!host) return null;" in create
    assert "if (menuButton) { togglePanel(); return; }" in create
    assert "runBootIntegration('initial command-bar state', () => toolkitApplyCommandBarState(control));" in create
    assert "host.appendChild(control);" in create
    assert create.index("host.appendChild(control);") < create.index("toolkitApplyCommandBarState(control)")
    assert "control.dataset.mcmsLauncherReady = 'true';" in create

    ensure = section(source, "    function ensureUi()", "    function mutationBelongsToToolkit")
    assert "if (!toolkitCommandShellRouteEligible(document))" in ensure
    assert "teardownToolkitCommandShell('route is not the canonical top-level map')" in ensure
    assert "const mapEl = toolkitPrimaryMapElement(discoveredMap, document);" in ensure
    assert "if (!mapEl)" in ensure
    assert "const control = createControl(mapEl);" in ensure
    assert "runBootIntegration('command-bar reconciliation', () => toolkitApplyCommandBarState(control));" in ensure
    assert "return Boolean(mountedControl?.dataset?.mcmsLauncherReady === 'true');" in ensure

    assert "return toolkitPrimaryMapElement(mapEl, doc);" in source
    assert "return toolkitPrimaryMapElement(mapEl, doc) || doc?.body" not in source
    assert "#mission-form,.mission-window,.mission_window,.modal,.modal-content,.lightbox,[data-mission-id]" in source
    token = "ls" + "sm"
    assert token not in source.lower(), "retired integration reference returned"
    print("Issue #515 launcher restoration static contract passed.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
