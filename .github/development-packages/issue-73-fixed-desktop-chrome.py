#!/usr/bin/env python3
from __future__ import annotations

import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
SOURCE = ROOT / "src" / "MissionChief_Map_Command_Toolkit.user.js"
DIST_JS = ROOT / "dist" / "MissionChief_Map_Command_Toolkit.user.js"
DIST_TXT = ROOT / "dist" / "MissionChief_Map_Command_Toolkit.txt"
MANIFEST = ROOT / "dist" / "release-manifest.json"
SUMS = ROOT / "dist" / "SHA256SUMS.txt"
CHANGELOG = ROOT / "CHANGELOG.md"
CONTRACT = ROOT / ".github" / "scripts" / "test_desktop_panel_layout_contract.py"


def replace_once(text: str, old: str, new: str, label: str) -> str:
    count = text.count(old)
    if count != 1:
        raise RuntimeError(f"{label}: expected one match, found {count}")
    return text.replace(old, new, 1)


source = SOURCE.read_text(encoding="utf-8")

source = replace_once(source, "// @version      4.13.6", "// @version      4.13.7", "metadata version")
source = replace_once(source, "        version: '4.13.6',", "        version: '4.13.7',", "runtime version")
source = replace_once(source, "        styleId: 'mc-map-command-toolkit-style-v4136',", "        styleId: 'mc-map-command-toolkit-style-v4137',", "style id")
source = replace_once(
    source,
    "    pageWindow.__MC_MAP_COMMAND_TOOLKIT_V4136__ = true;\n",
    "    pageWindow.__MC_MAP_COMMAND_TOOLKIT_V4136__ = true;\n"
    "    pageWindow.__MC_MAP_COMMAND_TOOLKIT_V4137__ = true;\n",
    "version marker",
)
source = replace_once(source, "        guideVersion: '4.13.6',", "        guideVersion: '4.13.7',", "help guide version")

old_css = '''        html[data-mcms-device-layout="desktop"] #${SCRIPT.panelId} {
            box-sizing: border-box !important;
            max-height: var(--mcms-desktop-panel-max-height, calc(100vh - 24px)) !important;
            overflow: hidden !important;
            overscroll-behavior: contain !important;
        }
        html[data-mcms-device-layout="desktop"] #${SCRIPT.panelId}.mcms-open {
            display: flex !important;
            flex-direction: column !important;
        }
        html[data-mcms-device-layout="desktop"] #${SCRIPT.panelId} .mcms-header,
        html[data-mcms-device-layout="desktop"] #${SCRIPT.panelId} .mcms-tabs,
        html[data-mcms-device-layout="desktop"] #${SCRIPT.panelId} .mcms-footer {
            flex: 0 0 auto !important;
        }
        html[data-mcms-device-layout="desktop"] #${SCRIPT.panelId} .mcms-tab-panel.mcms-active {
            flex: 1 1 auto !important;
            min-height: 0 !important;
            overflow-y: auto !important;
            overflow-x: hidden !important;
            overscroll-behavior: contain !important;
            scrollbar-width: thin !important;
            padding-right: 2px !important;
        }
'''

new_css = '''        html[data-mcms-device-layout="desktop"] body #${SCRIPT.panelId} {
            box-sizing: border-box !important;
            max-height: var(--mcms-desktop-panel-max-height, calc(100vh - 24px)) !important;
            overflow: hidden !important;
            overscroll-behavior: contain !important;
        }
        html[data-mcms-device-layout="desktop"] body #${SCRIPT.panelId}.mcms-open {
            display: grid !important;
            grid-template-rows: auto minmax(0, 1fr) !important;
            align-content: stretch !important;
        }
        html[data-mcms-device-layout="desktop"] body #${SCRIPT.panelId} > .mcms-panel-sticky-stack {
            grid-row: 1 !important;
            min-height: 0 !important;
            flex: none !important;
            position: sticky !important;
            top: 0 !important;
            z-index: 30 !important;
            overflow: visible !important;
            transform: none !important;
        }
        html[data-mcms-device-layout="desktop"] body #${SCRIPT.panelId} > .mcms-panel-sticky-stack .mcms-header,
        html[data-mcms-device-layout="desktop"] body #${SCRIPT.panelId} > .mcms-panel-sticky-stack .mcms-tabs {
            flex: none !important;
        }
        html[data-mcms-device-layout="desktop"] body #${SCRIPT.panelId} > .mcms-tab-panel {
            grid-row: 2 !important;
            min-height: 0 !important;
            max-height: 100% !important;
        }
        html[data-mcms-device-layout="desktop"] body #${SCRIPT.panelId} > .mcms-tab-panel.mcms-active {
            display: block !important;
            height: 100% !important;
            min-height: 0 !important;
            overflow-y: auto !important;
            overflow-x: hidden !important;
            overscroll-behavior: contain !important;
            scrollbar-width: thin !important;
            padding-right: 2px !important;
        }
'''

source = replace_once(source, old_css, new_css, "Desktop panel shell CSS")
SOURCE.write_text(source, encoding="utf-8")
DIST_JS.write_text(source, encoding="utf-8")
DIST_TXT.write_text(source, encoding="utf-8")

contract = CONTRACT.read_text(encoding="utf-8")
contract = replace_once(
    contract,
    "        'html[data-mcms-device-layout=\"desktop\"] #${SCRIPT.panelId}.mcms-open',\n"
    "        'html[data-mcms-device-layout=\"desktop\"] #${SCRIPT.panelId} .mcms-tab-panel.mcms-active',\n"
    "        'flex-direction: column !important',\n",
    "        'html[data-mcms-device-layout=\"desktop\"] body #${SCRIPT.panelId}.mcms-open',\n"
    "        'html[data-mcms-device-layout=\"desktop\"] body #${SCRIPT.panelId} > .mcms-panel-sticky-stack',\n"
    "        'html[data-mcms-device-layout=\"desktop\"] body #${SCRIPT.panelId} > .mcms-tab-panel.mcms-active',\n"
    "        'grid-template-rows: auto minmax(0, 1fr) !important',\n"
    "        'position: sticky !important',\n"
    "        'top: 0 !important',\n",
    "static required fragments",
)
contract = replace_once(
    contract,
    '''    desktop_rule = re.search(
        r'html\\[data-mcms-device-layout="desktop"\\] #\\$\\{SCRIPT\\.panelId\\} \\.mcms-tab-panel\\.mcms-active \\{(?P<body>.*?)\\n\\s*\\}',
        source,
        re.S,
    )
    assert desktop_rule, "Desktop active-tab scroll rule missing"
    body = desktop_rule.group("body")
    assert "overflow-y: auto !important" in body
    assert "overflow-x: hidden !important" in body
    assert "min-height: 0 !important" in body
''',
    '''    shell_rule = re.search(
        r'html\\[data-mcms-device-layout="desktop"\\] body #\\$\\{SCRIPT\\.panelId\\}\\.mcms-open \\{(?P<body>.*?)\\n\\s*\\}',
        source,
        re.S,
    )
    assert shell_rule, "Desktop fixed-chrome grid shell missing"
    shell_body = shell_rule.group("body")
    assert "display: grid !important" in shell_body
    assert "grid-template-rows: auto minmax(0, 1fr) !important" in shell_body

    chrome_rule = re.search(
        r'html\\[data-mcms-device-layout="desktop"\\] body #\\$\\{SCRIPT\\.panelId\\} > \\.mcms-panel-sticky-stack \\{(?P<body>.*?)\\n\\s*\\}',
        source,
        re.S,
    )
    assert chrome_rule, "Desktop command chrome rule missing"
    chrome_body = chrome_rule.group("body")
    assert "grid-row: 1 !important" in chrome_body
    assert "position: sticky !important" in chrome_body
    assert "top: 0 !important" in chrome_body
    assert "z-index: 30 !important" in chrome_body

    desktop_rule = re.search(
        r'html\\[data-mcms-device-layout="desktop"\\] body #\\$\\{SCRIPT\\.panelId\\} > \\.mcms-tab-panel\\.mcms-active \\{(?P<body>.*?)\\n\\s*\\}',
        source,
        re.S,
    )
    assert desktop_rule, "Desktop content-only scroll rule missing"
    body = desktop_rule.group("body")
    assert "height: 100% !important" in body
    assert "overflow-y: auto !important" in body
    assert "overflow-x: hidden !important" in body
    assert "min-height: 0 !important" in body
''',
    "static CSS assertions",
)
CONTRACT.write_text(contract, encoding="utf-8")

changelog = CHANGELOG.read_text(encoding="utf-8")
entry = '''## [4.13.7] - 2026-07-16

### Fixed
- Rebuilt the Desktop panel shell as a two-row command layout so the title controls and eight-section menu rail remain permanently visible.
- Restricted vertical scrolling to the selected section content, preventing the command chrome from moving away or appearing detached on long Ops and Settings pages.
- Added a static regression contract for the fixed command-chrome row and content-only scroll region.

### Compatibility
- The v4.13.6 full operational-workspace sizing and saved-position clamping are preserved.
- Tablet Mode, iOS Mobile Mode, Economy Mode, all themes, settings and import/export contracts are unchanged.

'''
changelog = replace_once(changelog, "## [Unreleased]\n\n", "## [Unreleased]\n\n" + entry, "changelog insertion")
CHANGELOG.write_text(changelog, encoding="utf-8")

payload = source.encode("utf-8")
digest = hashlib.sha256(payload).hexdigest()
line_count = len(source.splitlines())
manifest = json.loads(MANIFEST.read_text(encoding="utf-8"))
manifest["version"] = "4.13.7"
manifest["sha256"] = digest
manifest["bytes"] = len(payload)
manifest["lines"] = line_count
manifest["metadata"]["runtimeVersion"] = "4.13.7"
manifest["distributionStatus"] = "dry-run-not-yet-greasyfork-source"
MANIFEST.write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")
SUMS.write_text(
    f"{digest}  MissionChief_Map_Command_Toolkit.user.js\n"
    f"{digest}  MissionChief_Map_Command_Toolkit.txt\n",
    encoding="utf-8",
)

print(f"Prepared Toolkit 4.13.7 fixed Desktop command chrome: {digest}")
