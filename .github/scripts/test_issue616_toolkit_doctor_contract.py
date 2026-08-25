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
    assert metadata and runtime and metadata.group(1) == runtime.group(1) == "10.18.0"

    doctor = section(source, "    function toolkitDoctorSafeText(", "    function updateBriefingBody(")
    for required in [
        "function toolkitDoctorRectInsideViewport(",
        "function toolkitDoctorResponsiveStatus(",
        "Needs reconciliation: ",
        "device-layout attribute",
        "density attribute",
        "open Settings panel bounds",
        "function toolkitDoctorRectIntersectionArea(",
        "function toolkitDoctorOwnedSurfaceSelector(",
        "SCRIPT.transportSweepHudId",
        "SCRIPT.helpCenterId",
        "SCRIPT.fullscreenExitId",
        "function toolkitDoctorOverlayConflictCount(",
        "countedRoots.some(root => root.contains(element))",
        "toolkitDoctorRectIntersectionArea(rect, protectedRect) >= 64",
        "closeCommandExperienceModal({ restoreFocus: false })",
        "const responsiveStatus = toolkitDoctorResponsiveStatus()",
        "const overlayConflicts = toolkitDoctorOverlayConflictCount()",
        "No competing high-priority page overlay intersects Toolkit controls.",
        "applyVisualViewportGeometry()",
        "refreshTabletModeUi()",
    ]:
        assert required in doctor, required

    for forbidden in [
        "getDiscordWebhookUrl()",
        "discordWebhookEndpoint(",
        "document.cookie",
        "MutationObserver",
        "runtimeSetInterval(",
    ]:
        assert forbidden not in doctor, forbidden

    print("Issue #616 Toolkit Doctor static contract passed.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
