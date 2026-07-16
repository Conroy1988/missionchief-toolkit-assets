#!/usr/bin/env python3
from __future__ import annotations

import hashlib
import json
import os
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
SOURCE = ROOT / "src" / "MissionChief_Map_Command_Toolkit.user.js"
DIST_USER = ROOT / "dist" / "MissionChief_Map_Command_Toolkit.user.js"
DIST_TEXT = ROOT / "dist" / "MissionChief_Map_Command_Toolkit.txt"
SUMS = ROOT / "dist" / "SHA256SUMS.txt"
MANIFEST = ROOT / "dist" / "release-manifest.json"
CHANGELOG = ROOT / "CHANGELOG.md"
CONTRACT = ROOT / ".github" / "scripts" / "test_mission_value_contract.py"


def replace_once(text: str, old: str, new: str, label: str) -> str:
    count = text.count(old)
    if count != 1:
        raise AssertionError(f"{label}: expected one match, found {count}")
    return text.replace(old, new, 1)


source = SOURCE.read_text(encoding="utf-8")
source = replace_once(source, "// @version      4.13.8", "// @version      4.13.9", "metadata version")
source = replace_once(source, "version: '4.13.8',\n        author:", "version: '4.13.9',\n        author:", "runtime version")
source = replace_once(source, "styleId: 'mc-map-command-toolkit-style-v4138'", "styleId: 'mc-map-command-toolkit-style-v4139'", "style id")
source = replace_once(
    source,
    "pageWindow.__MC_MAP_COMMAND_TOOLKIT_V4138__ = true;",
    "pageWindow.__MC_MAP_COMMAND_TOOLKIT_V4138__ = true;\n    pageWindow.__MC_MAP_COMMAND_TOOLKIT_V4139__ = true;",
    "version flag",
)
source = replace_once(source, "guideVersion: '4.13.8'", "guideVersion: '4.13.9'", "guide version")

helper = r'''
    function missionValueVisibleControlRect(element) {
        if (!element?.isConnected || element.closest?.('.mcms-mission-value-row')) return null;
        try {
            const view = element.ownerDocument?.defaultView || pageWindow;
            const style = view?.getComputedStyle?.(element);
            if (style?.display === 'none' || style?.visibility === 'hidden' || style?.visibility === 'collapse' || Number(style?.opacity) === 0) return null;
        } catch (err) {}
        try {
            const rect = element.getBoundingClientRect?.();
            if (!rect || rect.width <= 2 || rect.height <= 2 || rect.width > 96 || rect.height > 64) return null;
            return rect;
        } catch (err) {
            return null;
        }
    }

    function missionValueRightControlOffset(candidate) {
        const { root, mount } = candidate || {};
        const fallback = 72;
        if (!root?.querySelectorAll || !mount?.getBoundingClientRect) return fallback;

        let mountRect = null;
        try { mountRect = mount.getBoundingClientRect(); } catch (err) {}
        if (!mountRect || mountRect.width <= 0) return fallback;

        const topBandBottom = mountRect.top + Math.min(58, Math.max(40, mountRect.height * 0.14));
        const rightBandWidth = Math.min(160, Math.max(92, mountRect.width * 0.10));
        const rightBandStart = mountRect.right - rightBandWidth;
        const selector = 'button, a, [role="button"], [onclick], [data-dismiss], [aria-label], [title], .close, .lightbox-close, .glyphicon, .fa, .fas, .far, svg';
        let controls = [];
        try { controls = Array.from(root.querySelectorAll(selector)); } catch (err) {}

        let leftEdge = null;
        for (const control of controls) {
            const rect = missionValueVisibleControlRect(control);
            if (!rect) continue;
            if (rect.bottom < mountRect.top - 2 || rect.top > topBandBottom) continue;
            if (rect.right < rightBandStart || rect.left >= mountRect.right + 2) continue;
            leftEdge = leftEdge === null ? rect.left : Math.min(leftEdge, rect.left);
        }

        if (leftEdge === null) return fallback;
        const measured = Math.ceil(mountRect.right - leftEdge + 16);
        const maximum = Math.max(fallback, Math.floor(mountRect.width * 0.42));
        return Math.max(fallback, Math.min(maximum, measured));
    }

    function positionMissionValueRow(candidate, row) {
        if (!row) return;
        const offset = missionValueRightControlOffset(candidate);
        row.style.setProperty('padding-right', `${offset}px`, 'important');
        row.dataset.mcmsRightOffset = String(offset);
    }

'''
source = replace_once(
    source,
    "    function syncMissionValueCandidate(candidate) {",
    helper + "    function syncMissionValueCandidate(candidate) {",
    "dynamic icon-clearance helper",
)
source = replace_once(
    source,
    "        badge.title = `Mission Value · ${formatted} · ${details.source}`;\n        return true;",
    "        badge.title = `Mission Value · ${formatted} · ${details.source}`;\n        positionMissionValueRow(candidate, nextRow);\n        return true;",
    "dynamic icon-clearance call",
)
SOURCE.write_text(source, encoding="utf-8")
DIST_USER.write_text(source, encoding="utf-8")
DIST_TEXT.write_text(source, encoding="utf-8")

contract = CONTRACT.read_text(encoding="utf-8")
contract = replace_once(
    contract,
    '        "clearMissionValueIndicators()",\n',
    '        "clearMissionValueIndicators()",\n        "missionValueRightControlOffset(candidate)",\n        "positionMissionValueRow(candidate, nextRow)",\n        "row.style.setProperty(\'padding-right\'",\n        "const fallback = 72",\n        "mountRect.right - leftEdge + 16",\n',
    "Mission Value clearance contract",
)
CONTRACT.write_text(contract, encoding="utf-8")

changelog = CHANGELOG.read_text(encoding="utf-8")
release_notes = """## [4.13.9] - 2026-07-16

### Fixed
- Moved the Mission Value indicator clear of MissionChief's upper-right mission-window controls.
- The indicator now measures the visible close/action icon cluster and dynamically reserves enough right-side clearance, with a conservative fallback when game markup differs.

### Compatibility
- Mission Value remains enabled by default and retains its existing persistent toggle, currency formatting, verified value sources and iframe support.
- Native MissionChief controls remain untouched and fully clickable.

"""
changelog = replace_once(changelog, "## [Unreleased]\n\n", "## [Unreleased]\n\n" + release_notes, "changelog entry")
CHANGELOG.write_text(changelog, encoding="utf-8")

payload = source.encode("utf-8")
digest = hashlib.sha256(payload).hexdigest()
SUMS.write_text(
    f"{digest}  MissionChief_Map_Command_Toolkit.user.js\n"
    f"{digest}  MissionChief_Map_Command_Toolkit.txt\n",
    encoding="utf-8",
)
manifest = json.loads(MANIFEST.read_text(encoding="utf-8"))
manifest["version"] = "4.13.9"
manifest["sha256"] = digest
manifest["bytes"] = len(payload)
manifest["lines"] = len(source.splitlines())
manifest.setdefault("metadata", {})["runtimeVersion"] = "4.13.9"
MANIFEST.write_text(json.dumps(manifest, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")

subprocess.run(["node", "--check", str(SOURCE)], cwd=ROOT, check=True)
env = os.environ.copy()
env["PYTHONDONTWRITEBYTECODE"] = "1"
subprocess.run(["python3", str(CONTRACT)], cwd=ROOT, env=env, check=True)

assert SOURCE.read_bytes() == DIST_USER.read_bytes() == DIST_TEXT.read_bytes()
print(f"Prepared Mission Value icon-clearance patch 4.13.9 ({digest}).")
