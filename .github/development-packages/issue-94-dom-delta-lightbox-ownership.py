#!/usr/bin/env python3
from __future__ import annotations

import json
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
SOURCE = ROOT / "src/MissionChief_Map_Command_Toolkit.user.js"
CHANGELOG = ROOT / "CHANGELOG.md"
TEST = ROOT / ".github/scripts/test_transport_sweep_lssm_contract.py"
FIXTURE = ROOT / ".github/fixtures/transport-sweep-lssm-contract.json"


def replace_once(text: str, old: str, new: str, label: str) -> str:
    count = text.count(old)
    if count != 1:
        raise RuntimeError(f"{label}: expected one match, found {count}")
    return text.replace(old, new, 1)


source = SOURCE.read_text(encoding="utf-8")
source = replace_once(source, "// @version      4.14.3", "// @version      4.14.4", "metadata version")
source = replace_once(source, "version: '4.14.3'", "version: '4.14.4'", "runtime version")
source = replace_once(source, "styleId: 'mc-map-command-toolkit-style-v4143'", "styleId: 'mc-map-command-toolkit-style-v4144'", "style id")
source = replace_once(source, "guideVersion: '4.14.3'", "guideVersion: '4.14.4'", "help guide version")
source = replace_once(
    source,
    "    pageWindow.__MC_MAP_COMMAND_TOOLKIT_V4143__ = true;",
    "    pageWindow.__MC_MAP_COMMAND_TOOLKIT_V4143__ = true;\n    pageWindow.__MC_MAP_COMMAND_TOOLKIT_V4144__ = true;",
    "compatibility flag",
)
source = replace_once(
    source,
    "        activeWindowRoot: null,\n        lastCandidateStats: null,",
    "        activeWindowRoot: null,\n        ownedWindowLayers: new Set(),\n        activeWindowCreatedLayer: false,\n        lastCandidateStats: null,",
    "runtime ownership state",
)

old_owner = '''    function transportSweepOwnedWindowRoot(root) {
        if (!root?.isConnected) return null;
        const direct = root.closest?.('#lightbox_box, #lightbox, .modal.show, .modal.in, [role="dialog"], .ui-dialog');
        if (direct) return direct;
        return transportSweepTopLevelWindowRoots().find(candidate => candidate === root || candidate.contains?.(root)) || root;
    }
'''

new_owner = '''    const TRANSPORT_SWEEP_NATIVE_LAYER_SELECTOR = [
        '#lightbox', '#lightbox_box', '.lightbox', '[id*="lightbox"]',
        '.modal.show', '.modal.in', '.modal-backdrop.show', '.modal-backdrop.in',
        '[role="dialog"]', '.ui-dialog', '.ui-widget-overlay'
    ].join(', ');

    function transportSweepNativeWindowLayers() {
        const layers = [];
        const seen = new Set();
        for (const context of transportSweepDocumentContexts()) {
            let matches = [];
            try { matches = Array.from(context.doc.querySelectorAll(TRANSPORT_SWEEP_NATIVE_LAYER_SELECTOR)); } catch (err) {}
            for (const layer of matches) {
                if (!layer || seen.has(layer) || !layer.isConnected || layer.closest?.(`#${SCRIPT.panelId}`)) continue;
                seen.add(layer);
                layers.push(layer);
            }
        }
        return layers;
    }

    function transportSweepWindowLayerChain(root) {
        const chain = [];
        const seen = new Set();
        const collect = start => {
            let node = start;
            while (node?.nodeType === 1) {
                if (!seen.has(node) && node.matches?.(TRANSPORT_SWEEP_NATIVE_LAYER_SELECTOR)) {
                    seen.add(node);
                    chain.push(node);
                }
                node = node.parentElement;
            }
        };
        collect(root);
        try { collect(root?.ownerDocument?.defaultView?.frameElement); } catch (err) {}
        return chain;
    }

    function transportSweepOverlayLayer(layer) {
        if (!layer?.matches) return false;
        return layer.matches('.modal-backdrop, .ui-widget-overlay, .lightbox_overlay, .lightbox-overlay, #lightbox_overlay');
    }

    function transportSweepOutermostLayer(layers) {
        const candidates = Array.from(layers || []).filter(layer => layer?.isConnected && !transportSweepOverlayLayer(layer));
        return candidates.find(layer => !candidates.some(other => other !== layer && other.contains?.(layer))) || candidates[0] || null;
    }

    function transportSweepClaimWindow(root, beforeLayers = null) {
        if (!root?.isConnected) return null;
        const baseline = beforeLayers instanceof Set ? beforeLayers : new Set();
        const anchor = (() => {
            try { return root.ownerDocument?.defaultView?.frameElement || root; } catch (err) { return root; }
        })();
        const chain = transportSweepWindowLayerChain(root);
        const created = transportSweepNativeWindowLayers().filter(layer => {
            if (baseline.has(layer)) return false;
            if (layer === anchor || layer.contains?.(anchor) || anchor.contains?.(layer)) return true;
            return layer.ownerDocument === anchor.ownerDocument && transportSweepOverlayLayer(layer);
        });
        const owned = new Set([...created, ...chain.filter(layer => !baseline.has(layer))]);
        for (const layer of owned) {
            try { layer.dataset.mcmsTransportSweepOwned = '1'; } catch (err) {}
        }
        transportSweepRuntime.ownedWindowLayers = owned;
        transportSweepRuntime.activeWindowCreatedLayer = owned.size > 0;
        transportSweepRuntime.activeWindowRoot = transportSweepOutermostLayer(owned) || transportSweepOutermostLayer(chain) || root;
        return transportSweepRuntime.activeWindowRoot;
    }
'''
source = replace_once(source, old_owner, new_owner, "DOM-delta ownership helpers")

old_close = '''    async function closeTransportSweepWindows(reason = 'navigation') {
        const target = transportSweepRuntime.activeWindowRoot;
        transportSweepRuntime.missionWindowRoot = null;
        if (!target || !target.isConnected || !transportSweepElementVisible(target)) {
            transportSweepRuntime.activeWindowRoot = null;
            return true;
        }

        const waitUntilClosed = timeoutMs => transportSweepWaitFor(
            () => !target.isConnected || !transportSweepElementVisible(target) ? true : null,
            timeoutMs,
            100
        );

        let closed = false;
        if (typeof pageWindow.lightboxClose === 'function') {
            try {
                pageWindow.lightboxClose();
                closed = Boolean(await waitUntilClosed(1200));
            } catch (err) {}
        }

        if (!closed) {
            const closeControl = transportSweepWindowCloseControl(target);
            if (closeControl) {
                try {
                    closeControl.click();
                    closed = Boolean(await waitUntilClosed(1600));
                } catch (err) {}
            }
        }

        if (!closed) {
            transportSweepLog(`MissionChief did not close the sweep-owned window before ${reason}`, 'error');
            return false;
        }

        transportSweepRuntime.activeWindowRoot = null;
        await transportSweepSleep(80);
        return true;
    }
'''

new_close = '''    async function closeTransportSweepWindows(reason = 'navigation') {
        const target = transportSweepRuntime.activeWindowRoot;
        const ownedLayers = Array.from(transportSweepRuntime.ownedWindowLayers || []).filter(layer => layer?.isConnected);
        transportSweepRuntime.missionWindowRoot = null;
        if ((!target || !target.isConnected || !transportSweepElementVisible(target)) && !ownedLayers.length) {
            transportSweepRuntime.activeWindowRoot = null;
            transportSweepRuntime.ownedWindowLayers = new Set();
            transportSweepRuntime.activeWindowCreatedLayer = false;
            return true;
        }

        const waitUntilClosed = timeoutMs => transportSweepWaitFor(
            () => !target?.isConnected || !transportSweepElementVisible(target) ? true : null,
            timeoutMs,
            100
        );

        let closed = !target?.isConnected || !transportSweepElementVisible(target);
        if (!closed) {
            const closeControl = transportSweepWindowCloseControl(target);
            if (closeControl) {
                try {
                    closeControl.click();
                    closed = Boolean(await waitUntilClosed(1200));
                } catch (err) {}
            }
        }

        if (!closed && typeof pageWindow.lightboxClose === 'function') {
            try {
                pageWindow.lightboxClose();
                closed = Boolean(await waitUntilClosed(1400));
            } catch (err) {}
        }

        if (transportSweepRuntime.activeWindowCreatedLayer) {
            const removable = Array.from(new Set([...ownedLayers, target].filter(layer => layer?.isConnected)));
            removable.sort((a, b) => a.contains?.(b) ? -1 : b.contains?.(a) ? 1 : 0);
            for (const layer of removable) {
                if (!layer?.isConnected) continue;
                try {
                    layer.querySelectorAll?.('iframe, frame').forEach(frame => {
                        try { frame.src = 'about:blank'; } catch (err) {}
                    });
                    layer.remove();
                } catch (err) {}
            }
            closed = !target?.isConnected || !transportSweepElementVisible(target);
        }

        if (!closed) {
            transportSweepLog(`MissionChief did not remove the sweep-owned window before ${reason}`, 'error');
            return false;
        }

        transportSweepRuntime.activeWindowRoot = null;
        transportSweepRuntime.ownedWindowLayers = new Set();
        transportSweepRuntime.activeWindowCreatedLayer = false;
        await transportSweepSleep(80);
        return true;
    }
'''
source = replace_once(source, old_close, new_close, "exact owned-layer close")

old_open = '''    async function openTransportSweepPath(path, mode) {
        if (transportSweepRuntime.stopRequested) return false;
        if (typeof pageWindow.lightboxOpen !== 'function') throw new Error('MissionChief lightboxOpen is unavailable');
        const closed = await closeTransportSweepWindows(mode === 'mission' ? 'opening a mission' : 'opening a vehicle');
        if (!closed || transportSweepRuntime.stopRequested) return false;

        const beforeRoots = transportSweepVisibleWindowRoots();
        const beforeRootText = new Map(beforeRoots.map(root => [root, String(root.textContent || '').trim()]));

        if (mode === 'mission') {
            transportSweepRuntime.missionAnchorBaseline = new Set(transportSweepVisibleVehicleAnchors());
            transportSweepRuntime.rejectedOwn = 0;
            transportSweepRuntime.missionWindowRoot = null;
            const missionId = normaliseMissionId(String(path || '').match(/\/missions\/(\d+)/)?.[1]);
            pageWindow.lightboxOpen(path);
            await transportSweepWaitFor(() => {
                const root = transportSweepFindMissionWindowRoot(missionId);
                if (root) {
                    const anchors = transportSweepVehicleAnchorsWithin(root);
                    const afterText = String(root.textContent || '').trim();
                    const changed = !beforeRootText.has(root) || afterText !== beforeRootText.get(root);
                    if (anchors.length || (afterText && changed)) {
                        transportSweepRuntime.missionWindowRoot = root;
                        transportSweepRuntime.activeWindowRoot = transportSweepOwnedWindowRoot(root);
                        return { root, anchors };
                    }
                }
                const newAnchor = transportSweepVisibleVehicleAnchors().find(anchor => !transportSweepRuntime.missionAnchorBaseline.has(anchor));
                if (newAnchor) {
                    transportSweepRuntime.missionWindowRoot = newAnchor.closest?.('#lightbox_box, #lightbox, .lightbox_content, .modal-content, [role="dialog"], .ui-dialog-content') || newAnchor.parentElement;
                    transportSweepRuntime.activeWindowRoot = transportSweepOwnedWindowRoot(transportSweepRuntime.missionWindowRoot);
                    return { root: transportSweepRuntime.missionWindowRoot, anchors: [newAnchor] };
                }
                return null;
            }, 4200, 120);
            return !transportSweepRuntime.stopRequested && Boolean(transportSweepRuntime.activeWindowRoot);
        }

        pageWindow.lightboxOpen(path);
        const vehicleWindow = await transportSweepWaitFor(() => {
            const button = findVisibleDischargePatientButton(transportSweepRuntime.vehicleButtonBaseline);
            if (button) {
                const root = button.closest?.('#lightbox_box, #lightbox, .lightbox_content, .modal-content, [role="dialog"], .ui-dialog-content') || button.parentElement;
                return { root };
            }
            const root = transportSweepVisibleWindowRoots().find(candidate => {
                const text = String(candidate.textContent || '').trim();
                return !beforeRootText.has(candidate) || text !== beforeRootText.get(candidate);
            });
            return root ? { root } : null;
        }, 4200, 120);
        transportSweepRuntime.activeWindowRoot = transportSweepOwnedWindowRoot(vehicleWindow?.root);
        return !transportSweepRuntime.stopRequested && Boolean(transportSweepRuntime.activeWindowRoot);
    }
'''

new_open = '''    async function openTransportSweepPath(path, mode) {
        if (transportSweepRuntime.stopRequested) return false;
        if (typeof pageWindow.lightboxOpen !== 'function') throw new Error('MissionChief lightboxOpen is unavailable');
        const closed = await closeTransportSweepWindows(mode === 'mission' ? 'opening a mission' : 'opening a vehicle');
        if (!closed || transportSweepRuntime.stopRequested) return false;

        const beforeRoots = transportSweepVisibleWindowRoots();
        const beforeRootText = new Map(beforeRoots.map(root => [root, String(root.textContent || '').trim()]));
        const beforeLayers = new Set(transportSweepNativeWindowLayers());

        if (mode === 'mission') {
            transportSweepRuntime.missionAnchorBaseline = new Set(transportSweepVisibleVehicleAnchors());
            transportSweepRuntime.rejectedOwn = 0;
            transportSweepRuntime.missionWindowRoot = null;
            const missionId = normaliseMissionId(String(path || '').match(/\/missions\/(\d+)/)?.[1]);
            pageWindow.lightboxOpen(path);
            await transportSweepWaitFor(() => {
                const root = transportSweepFindMissionWindowRoot(missionId);
                if (root) {
                    const anchors = transportSweepVehicleAnchorsWithin(root);
                    const afterText = String(root.textContent || '').trim();
                    const changed = !beforeRootText.has(root) || afterText !== beforeRootText.get(root);
                    if (anchors.length || (afterText && changed)) {
                        transportSweepRuntime.missionWindowRoot = root;
                        transportSweepClaimWindow(root, beforeLayers);
                        return { root, anchors };
                    }
                }
                const newAnchor = transportSweepVisibleVehicleAnchors().find(anchor => !transportSweepRuntime.missionAnchorBaseline.has(anchor));
                if (newAnchor) {
                    transportSweepRuntime.missionWindowRoot = newAnchor.closest?.('#lightbox_box, #lightbox, .lightbox_content, .modal-content, [role="dialog"], .ui-dialog-content') || newAnchor.parentElement;
                    transportSweepClaimWindow(transportSweepRuntime.missionWindowRoot, beforeLayers);
                    return { root: transportSweepRuntime.missionWindowRoot, anchors: [newAnchor] };
                }
                return null;
            }, 4200, 120);
            return !transportSweepRuntime.stopRequested && Boolean(transportSweepRuntime.activeWindowRoot);
        }

        pageWindow.lightboxOpen(path);
        const vehicleWindow = await transportSweepWaitFor(() => {
            const button = findVisibleDischargePatientButton(transportSweepRuntime.vehicleButtonBaseline);
            if (button) {
                const root = button.closest?.('#lightbox_box, #lightbox, .lightbox_content, .modal-content, [role="dialog"], .ui-dialog-content') || button.parentElement;
                return { root };
            }
            const root = transportSweepVisibleWindowRoots().find(candidate => {
                const text = String(candidate.textContent || '').trim();
                return !beforeRootText.has(candidate) || text !== beforeRootText.get(candidate);
            });
            return root ? { root } : null;
        }, 4200, 120);
        transportSweepClaimWindow(vehicleWindow?.root, beforeLayers);
        return !transportSweepRuntime.stopRequested && Boolean(transportSweepRuntime.activeWindowRoot);
    }
'''
source = replace_once(source, old_open, new_open, "DOM-delta open path")

source = replace_once(
    source,
    "        transportSweepRuntime.activeWindowRoot = null;\n        transportSweepRuntime.lastCandidateStats = null;",
    "        transportSweepRuntime.activeWindowRoot = null;\n        transportSweepRuntime.ownedWindowLayers = new Set();\n        transportSweepRuntime.activeWindowCreatedLayer = false;\n        transportSweepRuntime.lastCandidateStats = null;",
    "sweep start ownership reset",
)
source = replace_once(
    source,
    "            transportSweepRuntime.vehicleButtonBaseline = new Set();\n            transportSweepRuntime.activeWindowRoot = null;\n            buildTransportSweepQueue();",
    "            transportSweepRuntime.vehicleButtonBaseline = new Set();\n            transportSweepRuntime.activeWindowRoot = null;\n            transportSweepRuntime.ownedWindowLayers = new Set();\n            transportSweepRuntime.activeWindowCreatedLayer = false;\n            buildTransportSweepQueue();",
    "sweep finish ownership reset",
)
SOURCE.write_text(source, encoding="utf-8")

changelog = CHANGELOG.read_text(encoding="utf-8")
entry = '''## [4.14.4] - 2026-07-17

### Fixed
- Replaced content-derived Transport Sweep window ownership with DOM-delta ownership of the exact native lightbox layer created by each `lightboxOpen()` call.
- The sweep now closes the owned layer through its own close control first and force-removes only newly created sweep-owned layers when MissionChief leaves their outer wrappers behind.

### Performance
- Prevents mission and vehicle lightbox shells, iframes and backdrops from accumulating underneath later sweep windows while preserving unrelated MissionChief, LSSM and Toolkit dialogs.

'''
changelog = replace_once(changelog, "## [Unreleased]\n\n", "## [Unreleased]\n\n" + entry, "changelog entry")
CHANGELOG.write_text(changelog, encoding="utf-8")

fixture = json.loads(FIXTURE.read_text(encoding="utf-8"))
fixture.setdefault("window_lifecycle", {}).update({
    "claim_new_outer_layer_from_dom_delta": True,
    "prefer_owned_close_control": True,
    "force_remove_only_new_owned_layers": True,
    "remove_owned_iframes_and_backdrops": True,
})
FIXTURE.write_text(json.dumps(fixture, indent=2) + "\n", encoding="utf-8")

test = TEST.read_text(encoding="utf-8")
test = replace_once(
    test,
    '"""Verify LSSM ownership, delayed controls and explicit same-mission multi-ambulance returns."""',
    '"""Verify LSSM ownership, delayed controls, multi-ambulance returns and DOM-delta window cleanup."""',
    "test docstring",
)
test = replace_once(
    test,
    '        "activeWindowRoot: null",\n',
    '        "activeWindowRoot: null",\n        "ownedWindowLayers: new Set()",\n        "activeWindowCreatedLayer: false",\n        "function transportSweepNativeWindowLayers()",\n        "function transportSweepClaimWindow(root, beforeLayers = null)",\n        "const beforeLayers = new Set(transportSweepNativeWindowLayers())",\n        "transportSweepClaimWindow(root, beforeLayers)",\n        "layer.dataset.mcmsTransportSweepOwned = \'1\'",\n        "layer.remove()",\n',
    "required DOM-delta markers",
)
old_assertions = '''    assert "transportSweepTopLevelWindowRoots()" not in closer.group(1), "cleanup must not scan or close unrelated visible dialogs"
    assert "if (!target || !target.isConnected" in closer.group(1), "the first mission must open immediately when the sweep owns no window"
    assert "const target = transportSweepRuntime.activeWindowRoot" in closer.group(1), "cleanup must target only the sweep-owned window"
'''
new_assertions = '''    assert "transportSweepTopLevelWindowRoots()" not in closer.group(1), "cleanup must not scan or close unrelated visible dialogs"
    assert "const target = transportSweepRuntime.activeWindowRoot" in closer.group(1), "cleanup must target only the sweep-owned window"
    assert "transportSweepRuntime.ownedWindowLayers" in closer.group(1), "cleanup must retain the exact DOM-delta layer set"
    control_index = closer.group(1).index("transportSweepWindowCloseControl(target)")
    global_index = closer.group(1).index("pageWindow.lightboxClose")
    assert control_index < global_index, "the owned window close control must be preferred over the global lightbox closer"
    assert "transportSweepRuntime.activeWindowCreatedLayer" in closer.group(1), "forced teardown must be limited to newly created sweep layers"
    assert "layer.remove()" in closer.group(1), "newly created owned layers must be removed if MissionChief leaves them connected"
'''
test = replace_once(test, old_assertions, new_assertions, "DOM-delta executable assertions")
TEST.write_text(test, encoding="utf-8")

subprocess.run(["python3", ".github/scripts/validate_userscript.py"], cwd=ROOT, check=True)
subprocess.run(["node", "--check", "src/MissionChief_Map_Command_Toolkit.user.js"], cwd=ROOT, check=True)
subprocess.run(["python3", ".github/scripts/test_transport_sweep_lssm_contract.py"], cwd=ROOT, check=True)
subprocess.run(["cmp", "--silent", "dist/MissionChief_Map_Command_Toolkit.user.js", "dist/MissionChief_Map_Command_Toolkit.txt"], cwd=ROOT, check=True)
print("Issue #94 DOM-delta lightbox ownership fix applied successfully")
