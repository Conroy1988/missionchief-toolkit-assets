from __future__ import annotations

import json
from pathlib import Path

ROOT = Path('.')
SOURCE = ROOT / 'src' / 'MissionChief_Map_Command_Toolkit.user.js'
CHANGELOG = ROOT / 'CHANGELOG.md'
WORKFLOW = ROOT / '.github' / 'workflows' / 'full-userscript-audit.yml'
FIXTURE = ROOT / '.github' / 'fixtures' / 'desktop-panel-layout-contract.json'
TEST = ROOT / '.github' / 'scripts' / 'test_desktop_panel_layout_contract.py'


def replace_once(text: str, old: str, new: str, label: str) -> str:
    count = text.count(old)
    if count != 1:
        raise RuntimeError(f'{label}: expected one match, found {count}')
    return text.replace(old, new, 1)


source = SOURCE.read_text(encoding='utf-8')

# Version the user-facing runtime change.
source = replace_once(source, '// @version      4.13.4', '// @version      4.13.5', 'metadata version')
source = replace_once(source, "version: '4.13.4'", "version: '4.13.5'", 'runtime version')
source = replace_once(source, "styleId: 'mc-map-command-toolkit-style-v4134'", "styleId: 'mc-map-command-toolkit-style-v4135'", 'style id')
source = replace_once(
    source,
    '    pageWindow.__MC_MAP_COMMAND_TOOLKIT_V4134__ = true;\n',
    '    pageWindow.__MC_MAP_COMMAND_TOOLKIT_V4134__ = true;\n    pageWindow.__MC_MAP_COMMAND_TOOLKIT_V4135__ = true;\n',
    'runtime version marker',
)
source = replace_once(source, "guideVersion: '4.13.4'", "guideVersion: '4.13.5'", 'help guide version')

# Desktop keeps its compact visual language, but the shell no longer scrolls as one tall surface.
desktop_css_anchor = '        #${SCRIPT.panelId}.mcms-open { display: block !important; }\n'
desktop_css = '''        #${SCRIPT.panelId}.mcms-open { display: block !important; }
        html[data-mcms-device-layout="desktop"] #${SCRIPT.panelId} {
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
source = replace_once(source, desktop_css_anchor, desktop_css, 'desktop panel CSS')

# Track the map rectangle independently from the existing Tablet/iOS dock observer.
observer_anchor = '''    let tabletDockResizeObserver = null;
    let tabletDockObservedMap = null;
'''
observer_replacement = '''    let tabletDockResizeObserver = null;
    let tabletDockObservedMap = null;
    let desktopPanelResizeObserver = null;
    let desktopPanelObservedMap = null;
'''
source = replace_once(source, observer_anchor, observer_replacement, 'desktop observer state')

# Pure geometry is fixture-tested; DOM sizing and observation stay narrowly scoped to Desktop.
layout_anchor = '    function getIosBrowserSignals() {\n'
layout_helpers = '''    function resolveDesktopPanelBounds(mapRect, viewport = getViewportMetrics(), margin = 12) {
        const finite = value => typeof value === 'number' && Number.isFinite(value);
        const viewportLeft = finite(viewport?.offsetLeft) ? viewport.offsetLeft : 0;
        const viewportTop = finite(viewport?.offsetTop) ? viewport.offsetTop : 0;
        const viewportWidth = Math.max(1, finite(viewport?.width) ? viewport.width : 1);
        const viewportHeight = Math.max(1, finite(viewport?.height) ? viewport.height : 1);
        const viewportRight = viewportLeft + viewportWidth;
        const viewportBottom = viewportTop + viewportHeight;
        const safeMargin = Math.max(0, finite(margin) ? margin : 12);

        const mapValid = mapRect
            && finite(mapRect.left)
            && finite(mapRect.right)
            && finite(mapRect.top)
            && finite(mapRect.bottom)
            && mapRect.right > mapRect.left
            && mapRect.bottom > mapRect.top;
        const visibleLeft = mapValid ? Math.max(viewportLeft, mapRect.left) : viewportLeft;
        const visibleRight = mapValid ? Math.min(viewportRight, mapRect.right) : viewportRight;
        const visibleTop = mapValid ? Math.max(viewportTop, mapRect.top) : viewportTop;
        const visibleBottom = mapValid ? Math.min(viewportBottom, mapRect.bottom) : viewportBottom;
        const usableMap = visibleRight > visibleLeft + 1 && visibleBottom > visibleTop + 1;
        const areaLeft = usableMap ? visibleLeft : viewportLeft;
        const areaRight = usableMap ? visibleRight : viewportRight;
        const areaTop = usableMap ? visibleTop : viewportTop;
        const areaBottom = usableMap ? visibleBottom : viewportBottom;
        const left = Math.min(areaRight, areaLeft + safeMargin);
        const right = Math.max(left, areaRight - safeMargin);
        const top = Math.min(areaBottom, areaTop + safeMargin);
        const bottom = Math.max(top, areaBottom - safeMargin);

        return {
            left: Math.round(left),
            right: Math.round(right),
            top: Math.round(top),
            bottom: Math.round(bottom),
            maxHeight: Math.max(1, Math.floor(bottom - top))
        };
    }

    function clampDesktopPanelPoint(left, top, panelWidth, panelHeight, bounds) {
        const safeBounds = bounds || resolveDesktopPanelBounds(null);
        const availableWidth = Math.max(1, safeBounds.right - safeBounds.left);
        const availableHeight = Math.max(1, safeBounds.bottom - safeBounds.top);
        const width = Math.min(availableWidth, Math.max(1, Number(panelWidth) || 318));
        const height = Math.min(availableHeight, Math.max(1, Number(panelHeight) || availableHeight));
        const desiredLeft = Number.isFinite(Number(left)) ? Number(left) : safeBounds.left;
        const desiredTop = Number.isFinite(Number(top)) ? Number(top) : safeBounds.top;
        return {
            left: Math.round(Math.max(safeBounds.left, Math.min(desiredLeft, safeBounds.right - width))),
            top: Math.round(Math.max(safeBounds.top, Math.min(desiredTop, safeBounds.bottom - height)))
        };
    }

    function stopDesktopPanelMapObservation() {
        if (desktopPanelResizeObserver && desktopPanelObservedMap) {
            try { desktopPanelResizeObserver.unobserve(desktopPanelObservedMap); } catch (err) {}
        }
        desktopPanelObservedMap = null;
    }

    function clearDesktopPanelSizing(panel = document.getElementById(SCRIPT.panelId)) {
        if (panel) {
            panel.style.removeProperty('--mcms-desktop-panel-max-height');
            panel.style.removeProperty('max-height');
            delete panel.dataset.mcmsDesktopFit;
        }
        stopDesktopPanelMapObservation();
    }

    function observeDesktopPanelMapArea(mapEl) {
        if (activeDeviceLayout !== 'desktop' || !mapEl) {
            stopDesktopPanelMapObservation();
            return;
        }
        const ResizeObserverCtor = pageWindow.ResizeObserver;
        if (typeof ResizeObserverCtor !== 'function') return;
        if (!desktopPanelResizeObserver) {
            desktopPanelResizeObserver = runtimeTrackObserver(new ResizeObserverCtor(entries => {
                if (runtime.destroyed || activeDeviceLayout !== 'desktop') return;
                if (!entries.some(entry => entry?.target === desktopPanelObservedMap)) return;
                const panel = document.getElementById(SCRIPT.panelId);
                if (!panel) return;
                applyDesktopPanelSizing(panel, desktopPanelObservedMap);
                if (!dragState && panel.classList.contains('mcms-open')) schedulePanelPosition(true, 20);
            }));
        }
        if (desktopPanelObservedMap === mapEl) return;
        stopDesktopPanelMapObservation();
        desktopPanelObservedMap = mapEl;
        try { desktopPanelResizeObserver.observe(mapEl); } catch (err) {}
    }

    function applyDesktopPanelSizing(panel = document.getElementById(SCRIPT.panelId), mapEl = getLargestLeafletMap()) {
        if (!panel || activeDeviceLayout !== 'desktop' || isTouchLayoutActive()) return null;
        let mapRect = null;
        try { mapRect = mapEl?.getBoundingClientRect?.() || null; } catch (err) {}
        const bounds = resolveDesktopPanelBounds(mapRect);
        panel.style.setProperty('--mcms-desktop-panel-max-height', `${bounds.maxHeight}px`);
        panel.style.setProperty('max-height', `${bounds.maxHeight}px`, 'important');
        panel.dataset.mcmsDesktopFit = `${bounds.left}:${bounds.top}:${bounds.right}:${bounds.bottom}:${bounds.maxHeight}`;
        return bounds;
    }

'''
source = replace_once(source, layout_anchor, layout_helpers + layout_anchor, 'desktop layout helpers')

# Touch layouts retain their existing independently sized bottom-sheet behaviour.
tablet_position_anchor = '''    function applyTabletPanelPosition() {
        const panel = document.getElementById(SCRIPT.panelId);
        if (!panel || !panel.classList.contains('mcms-open') || !isTouchLayoutActive()) return false;

        const viewport = getViewportMetrics();
'''
tablet_position_replacement = '''    function applyTabletPanelPosition() {
        const panel = document.getElementById(SCRIPT.panelId);
        if (!panel || !panel.classList.contains('mcms-open') || !isTouchLayoutActive()) return false;
        clearDesktopPanelSizing(panel);

        const viewport = getViewportMetrics();
'''
source = replace_once(source, tablet_position_anchor, tablet_position_replacement, 'touch panel separation')

fit_old = '''    function fitControlToMap() {
        runtimeClearTimeout(fitTimer);
        fitTimer = runtimeSetTimeout(() => {
            const panel = document.getElementById(SCRIPT.panelId);
            const mapEl = getLargestLeafletMap();
            if (!mapEl) return;
            if (mobileModeActive) applyMobileDockLayout(mapEl);
            else if (tabletModeActive) applyTabletDockLayout(mapEl);
            else clearTabletDockSizing();
            if (!panel) return;
            const rect = mapEl.getBoundingClientRect();
            panel.classList.toggle('mcms-map-small', rect.height < 560 || rect.width < 650);
        }, 60);
    }
'''
fit_new = '''    function fitControlToMap() {
        runtimeClearTimeout(fitTimer);
        fitTimer = runtimeSetTimeout(() => {
            const panel = document.getElementById(SCRIPT.panelId);
            const mapEl = getLargestLeafletMap();
            if (!mapEl) {
                if (!isTouchLayoutActive()) clearDesktopPanelSizing(panel);
                return;
            }
            if (mobileModeActive) {
                clearDesktopPanelSizing(panel);
                applyMobileDockLayout(mapEl);
            } else if (tabletModeActive) {
                clearDesktopPanelSizing(panel);
                applyTabletDockLayout(mapEl);
            } else {
                clearTabletDockSizing();
                observeDesktopPanelMapArea(mapEl);
                applyDesktopPanelSizing(panel, mapEl);
            }
            if (!panel) return;
            const rect = mapEl.getBoundingClientRect();
            panel.classList.toggle('mcms-map-small', rect.height < 560 || rect.width < 650);
        }, 60);
    }
'''
source = replace_once(source, fit_old, fit_new, 'map-aware fitting')

clamp_old = '''    function clampPanelPosition(left, top) {
        const panel = document.getElementById(SCRIPT.panelId);
        if (!panel) return { left: 12, top: 12 };

        const margin = 12;
        const viewportWidth = pageWindow.innerWidth || document.documentElement.clientWidth;
        const viewportHeight = pageWindow.innerHeight || document.documentElement.clientHeight;

        panel.style.setProperty('max-height', '', '');

        let panelWidth = panel.offsetWidth || 318;
        let panelHeight = panel.offsetHeight || 500;
        const maxPanelHeight = Math.max(260, viewportHeight - (margin * 2));

        if (panelHeight > maxPanelHeight) {
            panel.style.setProperty('max-height', `${maxPanelHeight}px`, 'important');
            panelHeight = maxPanelHeight;
        }

        panelWidth = Math.min(panelWidth, viewportWidth - (margin * 2));

        return {
            left: Math.round(Math.max(margin, Math.min(left, viewportWidth - panelWidth - margin))),
            top: Math.round(Math.max(margin, Math.min(top, viewportHeight - panelHeight - margin)))
        };
    }
'''
clamp_new = '''    function clampPanelPosition(left, top) {
        const panel = document.getElementById(SCRIPT.panelId);
        if (!panel) return { left: 12, top: 12 };
        const mapEl = getLargestLeafletMap();
        const bounds = applyDesktopPanelSizing(panel, mapEl) || resolveDesktopPanelBounds(null);
        const panelWidth = Math.min(panel.offsetWidth || 318, Math.max(1, bounds.right - bounds.left));
        const panelHeight = Math.min(panel.offsetHeight || 500, bounds.maxHeight);
        return clampDesktopPanelPoint(left, top, panelWidth, panelHeight, bounds);
    }
'''
source = replace_once(source, clamp_old, clamp_new, 'desktop map clamp')

# Explicit cleanup keeps the new observer lifecycle auditable.
cleanup_anchor = '''            runtimeUntrackObserver(majorIncidentFeedResizeObserver);
            majorIncidentFeedResizeObserver = null;
'''
cleanup_replacement = '''            stopDesktopPanelMapObservation();
            runtimeUntrackObserver(desktopPanelResizeObserver);
            desktopPanelResizeObserver = null;
            runtimeUntrackObserver(majorIncidentFeedResizeObserver);
            majorIncidentFeedResizeObserver = null;
'''
source = replace_once(source, cleanup_anchor, cleanup_replacement, 'desktop observer cleanup')

SOURCE.write_text(source, encoding='utf-8')

changelog = CHANGELOG.read_text(encoding='utf-8')
release_notes = '''## [Unreleased]

## [4.13.5] - 2026-07-16

### Changed
- Constrained the Desktop Mode command menu to the visible MissionChief map area instead of the full browser viewport.
- Kept the Desktop header, tab rail and footer accessible while only the active tab content scrolls internally.
- Added map-resize observation and saved-position clamping so shorter windows and changing map layouts remain usable.

### Compatibility
- Desktop retains its compact draggable layout and saved coordinates.
- Tablet Mode, iOS Mobile Mode, Economy Mode, all interface themes, settings and import/export contracts are unchanged.

'''
changelog = replace_once(changelog, '## [Unreleased]\n\n', release_notes, '4.13.5 changelog')
CHANGELOG.write_text(changelog, encoding='utf-8')

fixtures = {
    'boundsCases': [
        {
            'name': 'standard map below navigation',
            'mapRect': {'left': 50, 'top': 100, 'right': 1150, 'bottom': 850},
            'viewport': {'width': 1200, 'height': 900, 'offsetLeft': 0, 'offsetTop': 0},
            'margin': 12,
            'expected': {'left': 62, 'right': 1138, 'top': 112, 'bottom': 838, 'maxHeight': 726},
        },
        {
            'name': 'map clipped above viewport',
            'mapRect': {'left': 0, 'top': -50, 'right': 1000, 'bottom': 700},
            'viewport': {'width': 1000, 'height': 800, 'offsetLeft': 0, 'offsetTop': 0},
            'margin': 12,
            'expected': {'left': 12, 'right': 988, 'top': 12, 'bottom': 688, 'maxHeight': 676},
        },
        {
            'name': 'visual viewport offset',
            'mapRect': {'left': 10, 'top': 50, 'right': 990, 'bottom': 900},
            'viewport': {'width': 1000, 'height': 600, 'offsetLeft': 0, 'offsetTop': 100},
            'margin': 12,
            'expected': {'left': 22, 'right': 978, 'top': 112, 'bottom': 688, 'maxHeight': 576},
        },
        {
            'name': 'short map still remains authoritative',
            'mapRect': {'left': 100, 'top': 300, 'right': 900, 'bottom': 430},
            'viewport': {'width': 1000, 'height': 800, 'offsetLeft': 0, 'offsetTop': 0},
            'margin': 12,
            'expected': {'left': 112, 'right': 888, 'top': 312, 'bottom': 418, 'maxHeight': 106},
        },
        {
            'name': 'invalid map falls back to viewport',
            'mapRect': {'left': 100, 'top': 100, 'right': 100, 'bottom': 100},
            'viewport': {'width': 1200, 'height': 900, 'offsetLeft': 0, 'offsetTop': 0},
            'margin': 12,
            'expected': {'left': 12, 'right': 1188, 'top': 12, 'bottom': 888, 'maxHeight': 876},
        },
    ],
    'clampCases': [
        {
            'name': 'saved point above and left',
            'point': {'left': -200, 'top': -100},
            'panel': {'width': 318, 'height': 500},
            'bounds': {'left': 62, 'right': 1138, 'top': 112, 'bottom': 838, 'maxHeight': 726},
            'expected': {'left': 62, 'top': 112},
        },
        {
            'name': 'saved point below and right',
            'point': {'left': 1100, 'top': 800},
            'panel': {'width': 318, 'height': 500},
            'bounds': {'left': 62, 'right': 1138, 'top': 112, 'bottom': 838, 'maxHeight': 726},
            'expected': {'left': 820, 'top': 338},
        },
        {
            'name': 'valid saved point preserved',
            'point': {'left': 300, 'top': 180},
            'panel': {'width': 318, 'height': 500},
            'bounds': {'left': 62, 'right': 1138, 'top': 112, 'bottom': 838, 'maxHeight': 726},
            'expected': {'left': 300, 'top': 180},
        },
        {
            'name': 'panel larger than short map anchors to map origin',
            'point': {'left': 400, 'top': 350},
            'panel': {'width': 900, 'height': 500},
            'bounds': {'left': 112, 'right': 888, 'top': 312, 'bottom': 418, 'maxHeight': 106},
            'expected': {'left': 112, 'top': 312},
        },
    ],
}
FIXTURE.parent.mkdir(parents=True, exist_ok=True)
FIXTURE.write_text(json.dumps(fixtures, indent=2) + '\n', encoding='utf-8')

TEST.parent.mkdir(parents=True, exist_ok=True)
TEST.write_text(r'''#!/usr/bin/env python3
"""Fixture-backed Desktop panel geometry and static layout contract."""
from __future__ import annotations

import json
import re
import subprocess
import tempfile
from pathlib import Path

import full_userscript_audit as audit

ROOT = Path(__file__).resolve().parents[2]
SOURCE = ROOT / "src" / "MissionChief_Map_Command_Toolkit.user.js"
FIXTURES = ROOT / ".github" / "fixtures" / "desktop-panel-layout-contract.json"


def extract_function(source: str, masked: str, name: str) -> str:
    matches = list(re.finditer(rf"\bfunction\s+{re.escape(name)}\s*\(", masked))
    if len(matches) != 1:
        raise AssertionError(f"Expected one declaration for {name}, found {len(matches)}")
    start = matches[0].start()
    opening = masked.find("{", start)
    closing = audit.matching_brace(masked, opening)
    if opening < 0 or closing is None:
        raise AssertionError(f"Could not extract {name}")
    return source[start:closing + 1]


def assert_static_contract(source: str) -> None:
    required = [
        'html[data-mcms-device-layout="desktop"] #${SCRIPT.panelId}.mcms-open',
        'html[data-mcms-device-layout="desktop"] #${SCRIPT.panelId} .mcms-tab-panel.mcms-active',
        'flex-direction: column !important',
        'overflow-y: auto !important',
        'min-height: 0 !important',
        'html[data-mcms-tablet-active="true"] #${SCRIPT.panelId}',
        'html[data-mcms-mobile-active="true"] #${SCRIPT.panelId}',
        'observeDesktopPanelMapArea(mapEl)',
        'applyDesktopPanelSizing(panel, mapEl)',
        'clampDesktopPanelPoint(left, top, panelWidth, panelHeight, bounds)',
        "panel.dataset.mcmsDesktopFit",
    ]
    missing = [fragment for fragment in required if fragment not in source]
    assert not missing, f"Desktop layout contract fragments missing: {missing}"

    desktop_rule = re.search(
        r'html\[data-mcms-device-layout="desktop"\] #\$\{SCRIPT\.panelId\} \.mcms-tab-panel\.mcms-active \{(?P<body>.*?)\n\s*\}',
        source,
        re.S,
    )
    assert desktop_rule, "Desktop active-tab scroll rule missing"
    body = desktop_rule.group("body")
    assert "overflow-y: auto !important" in body
    assert "overflow-x: hidden !important" in body
    assert "min-height: 0 !important" in body


def main() -> int:
    source = SOURCE.read_text(encoding="utf-8")
    fixtures = json.loads(FIXTURES.read_text(encoding="utf-8"))
    assert_static_contract(source)
    masked = audit.mask_non_code(source)
    functions = "\n\n".join(
        extract_function(source, masked, name)
        for name in ["resolveDesktopPanelBounds", "clampDesktopPanelPoint"]
    )
    harness = f'''"use strict";
const assert = require("node:assert/strict");
const fixtures = {json.dumps(fixtures)};
function getViewportMetrics() {{ throw new Error("Explicit fixture viewport expected"); }}
{functions}
for (const item of fixtures.boundsCases) {{
  assert.deepEqual(resolveDesktopPanelBounds(item.mapRect, item.viewport, item.margin), item.expected, item.name);
}}
for (const item of fixtures.clampCases) {{
  assert.deepEqual(
    clampDesktopPanelPoint(item.point.left, item.point.top, item.panel.width, item.panel.height, item.bounds),
    item.expected,
    item.name
  );
}}
console.log(`Desktop panel layout contract passed: ${{fixtures.boundsCases.length}} bounds and ${{fixtures.clampCases.length}} saved-position cases.`);
'''
    with tempfile.TemporaryDirectory(prefix="mcms-desktop-layout-") as temp:
        path = Path(temp) / "contract.js"
        path.write_text(harness, encoding="utf-8")
        subprocess.run(["node", str(path)], check=True, cwd=ROOT)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
''', encoding='utf-8')

workflow = WORKFLOW.read_text(encoding='utf-8')
workflow = replace_once(
    workflow,
    '      - ".github/fixtures/settings-ui-contract.json"\n',
    '      - ".github/fixtures/settings-ui-contract.json"\n      - ".github/fixtures/desktop-panel-layout-contract.json"\n',
    'audit fixture path',
)
workflow = replace_once(
    workflow,
    '      - ".github/scripts/test_settings_ui_contract.py"\n',
    '      - ".github/scripts/test_settings_ui_contract.py"\n      - ".github/scripts/test_desktop_panel_layout_contract.py"\n',
    'audit test path',
)
workflow = replace_once(
    workflow,
    '''      - name: Run settings migration and UI routing contract fixtures
        run: python3 .github/scripts/test_settings_ui_contract.py

''',
    '''      - name: Run settings migration and UI routing contract fixtures
        run: python3 .github/scripts/test_settings_ui_contract.py

      - name: Run Desktop panel layout contract fixtures
        run: python3 .github/scripts/test_desktop_panel_layout_contract.py

''',
    'audit test step',
)
WORKFLOW.write_text(workflow, encoding='utf-8')

print('Issue #73 Desktop map-aware panel implementation prepared for guarded validation.')
