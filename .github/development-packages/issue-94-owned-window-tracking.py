#!/usr/bin/env python3
from __future__ import annotations

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
source = replace_once(source, "// @version      4.14.2", "// @version      4.14.3", "metadata version")
source = replace_once(source, "version: '4.14.2'", "version: '4.14.3'", "runtime version")
source = replace_once(source, "styleId: 'mc-map-command-toolkit-style-v4142'", "styleId: 'mc-map-command-toolkit-style-v4143'", "style id")
source = replace_once(source, "guideVersion: '4.14.2'", "guideVersion: '4.14.3'", "help guide version")
source = replace_once(
    source,
    "    pageWindow.__MC_MAP_COMMAND_TOOLKIT_V4142__ = true;",
    "    pageWindow.__MC_MAP_COMMAND_TOOLKIT_V4142__ = true;\n    pageWindow.__MC_MAP_COMMAND_TOOLKIT_V4143__ = true;",
    "runtime compatibility flag",
)
source = replace_once(
    source,
    "        missionWindowRoot: null,\n        lastCandidateStats: null,",
    "        missionWindowRoot: null,\n        activeWindowRoot: null,\n        lastCandidateStats: null,",
    "transport sweep active root state",
)

old_helpers = '''    function transportSweepTopLevelWindowRoots() {
        const visible = transportSweepVisibleWindowRoots();
        return visible.filter(root => !visible.some(other => other !== root && other.contains?.(root)));
    }

    function transportSweepWindowCloseControl(root) {
        if (!root?.querySelectorAll) return null;
        const selectors = [
            '#lightbox_close', '.lightbox-close', '.lightbox_close',
            '[data-dismiss="modal"]', '[data-bs-dismiss="modal"]',
            'button.close', 'a.close', 'button[aria-label="Close"]', 'a[aria-label="Close"]',
            'button[title="Close"]', 'a[title="Close"]'
        ];
        for (const selector of selectors) {
            const control = Array.from(root.querySelectorAll(selector)).find(transportSweepElementVisible);
            if (control) return control;
        }
        return null;
    }

    async function closeTransportSweepWindows(reason = 'navigation') {
        transportSweepRuntime.missionWindowRoot = null;
        for (let pass = 0; pass < 12 && !transportSweepRuntime.stopRequested; pass += 1) {
            const roots = transportSweepTopLevelWindowRoots();
            if (!roots.length) return true;
            const target = roots[roots.length - 1];
            const beforeCount = roots.length;
            let requested = false;

            if (typeof pageWindow.lightboxClose === 'function') {
                try {
                    pageWindow.lightboxClose();
                    requested = true;
                } catch (err) {}
            }

            if (!requested) {
                const closeControl = transportSweepWindowCloseControl(target);
                if (closeControl) {
                    try {
                        closeControl.click();
                        requested = true;
                    } catch (err) {}
                }
            }

            if (!requested) {
                transportSweepLog(`Could not close the active MissionChief window before ${reason}`, 'error');
                return false;
            }

            const closed = await transportSweepWaitFor(() => {
                const remaining = transportSweepTopLevelWindowRoots();
                return !target.isConnected || !transportSweepElementVisible(target) || remaining.length < beforeCount ? true : null;
            }, 2600, 100);
            if (!closed) {
                transportSweepLog(`MissionChief did not close the active window before ${reason}`, 'error');
                return false;
            }
            await transportSweepSleep(80);
        }
        return transportSweepTopLevelWindowRoots().length === 0;
    }
'''

new_helpers = '''    function transportSweepTopLevelWindowRoots() {
        const visible = transportSweepVisibleWindowRoots();
        return visible.filter(root => !visible.some(other => other !== root && other.contains?.(root)));
    }

    function transportSweepOwnedWindowRoot(root) {
        if (!root?.isConnected) return null;
        const direct = root.closest?.('#lightbox_box, #lightbox, .modal.show, .modal.in, [role="dialog"], .ui-dialog');
        if (direct) return direct;
        return transportSweepTopLevelWindowRoots().find(candidate => candidate === root || candidate.contains?.(root)) || root;
    }

    function transportSweepWindowCloseControl(root) {
        if (!root?.querySelectorAll) return null;
        const selectors = [
            '#lightbox_close', '.lightbox-close', '.lightbox_close',
            '[data-dismiss="modal"]', '[data-bs-dismiss="modal"]',
            'button.close', 'a.close', 'button[aria-label="Close"]', 'a[aria-label="Close"]',
            'button[title="Close"]', 'a[title="Close"]'
        ];
        for (const selector of selectors) {
            const control = Array.from(root.querySelectorAll(selector)).find(transportSweepElementVisible);
            if (control) return control;
        }
        return null;
    }

    async function closeTransportSweepWindows(reason = 'navigation') {
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
source = replace_once(source, old_helpers, new_helpers, "owned window helpers")

old_open = '''    async function openTransportSweepPath(path, mode) {
        if (transportSweepRuntime.stopRequested) return false;
        if (typeof pageWindow.lightboxOpen !== 'function') throw new Error('MissionChief lightboxOpen is unavailable');
        const closed = await closeTransportSweepWindows(mode === 'mission' ? 'opening a mission' : 'opening a vehicle');
        if (!closed || transportSweepRuntime.stopRequested) return false;

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
                    if (anchors.length || afterText) {
                        transportSweepRuntime.missionWindowRoot = root;
                        return { root, anchors };
                    }
                }
                const newAnchor = transportSweepVisibleVehicleAnchors().find(anchor => !transportSweepRuntime.missionAnchorBaseline.has(anchor));
                if (newAnchor) {
                    transportSweepRuntime.missionWindowRoot = newAnchor.closest?.('#lightbox_box, #lightbox, .lightbox_content, .modal-content, [role="dialog"], .ui-dialog-content') || newAnchor.ownerDocument?.body || newAnchor.parentElement;
                    return { root: transportSweepRuntime.missionWindowRoot, anchors: [newAnchor] };
                }
                return null;
            }, 4200, 120);
            return !transportSweepRuntime.stopRequested && Boolean(transportSweepRuntime.missionWindowRoot);
        }

        pageWindow.lightboxOpen(path);
        await transportSweepSleep(900);
        return !transportSweepRuntime.stopRequested;
    }
'''

new_open = '''    async function openTransportSweepPath(path, mode) {
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
source = replace_once(source, old_open, new_open, "owned window opener")

source = replace_once(
    source,
    "        transportSweepRuntime.missionWindowRoot = null;\n        transportSweepRuntime.lastCandidateStats = null;",
    "        transportSweepRuntime.missionWindowRoot = null;\n        transportSweepRuntime.activeWindowRoot = null;\n        transportSweepRuntime.lastCandidateStats = null;",
    "start sweep active root reset",
)
source = replace_once(
    source,
    "        } finally {\n            const wasStopped = transportSweepRuntime.stopRequested;",
    "        } finally {\n            await closeTransportSweepWindows('finishing the sweep');\n            const wasStopped = transportSweepRuntime.stopRequested;",
    "final sweep cleanup",
)
source = replace_once(
    source,
    "            transportSweepRuntime.vehicleButtonBaseline = new Set();\n            buildTransportSweepQueue();",
    "            transportSweepRuntime.vehicleButtonBaseline = new Set();\n            transportSweepRuntime.activeWindowRoot = null;\n            buildTransportSweepQueue();",
    "final active root reset",
)
SOURCE.write_text(source, encoding="utf-8")

changelog = CHANGELOG.read_text(encoding="utf-8")
entry = '''## [4.14.3] - 2026-07-17

### Fixed
- Restored Patient Transport Sweep mission opening after v4.14.2 incorrectly treated unrelated persistent page dialogs as active MissionChief mission windows.
- Window cleanup now targets only the exact lightbox opened and owned by the sweep; when no owned window exists, the next mission opens immediately.
- Restored changed-content baselines so persistent page UI cannot be mistaken for a newly loaded mission or vehicle window.

### Performance and compatibility
- Retains the v4.14.2 single-window lifecycle without closing or blocking unrelated MissionChief, LSSM or Toolkit interface elements.

'''
changelog = replace_once(changelog, "## [Unreleased]\n\n", "## [Unreleased]\n\n" + entry, "changelog entry")
CHANGELOG.write_text(changelog, encoding="utf-8")

fixture = FIXTURE.read_text(encoding="utf-8")
fixture = replace_once(
    fixture,
    '    "close_after_mission_processing": true\n',
    '    "close_after_mission_processing": true,\n    "close_only_sweep_owned_window": true,\n    "ignore_unrelated_dialogs": true\n',
    "fixture owned window contract",
)
FIXTURE.write_text(fixture, encoding="utf-8")

test = TEST.read_text(encoding="utf-8")
test = replace_once(
    test,
    '        "await closeTransportSweepWindows(\'finishing the mission\')",\n',
    '        "await closeTransportSweepWindows(\'finishing the mission\')",\n        "activeWindowRoot: null",\n        "const target = transportSweepRuntime.activeWindowRoot",\n        "transportSweepRuntime.activeWindowRoot = transportSweepOwnedWindowRoot(root)",\n        "const changed = !beforeRootText.has(root) || afterText !== beforeRootText.get(root)",\n        "await closeTransportSweepWindows(\'finishing the sweep\')",\n',
    "owned window required markers",
)
test = replace_once(
    test,
    '    assert close_index < open_index, "the current MissionChief window must close before another opens"\n',
    '    assert close_index < open_index, "the current MissionChief window must close before another opens"\n    closer = re.search(r"async function closeTransportSweepWindows\\(reason = \'navigation\'\\) \\{([\\s\\S]*?)\\n    \\}", source)\n    assert closer, "transport sweep closer is missing"\n    assert "transportSweepTopLevelWindowRoots()" not in closer.group(1), "cleanup must not scan or close unrelated visible dialogs"\n    assert "if (!target || !target.isConnected" in closer.group(1), "the first mission must open immediately when the sweep owns no window"\n    assert "const target = transportSweepRuntime.activeWindowRoot" in closer.group(1), "cleanup must target only the sweep-owned window"\n',
    "owned window executable assertions",
)
TEST.write_text(test, encoding="utf-8")

subprocess.run(["python3", ".github/scripts/validate_userscript.py"], cwd=ROOT, check=True)
subprocess.run(["node", "--check", "src/MissionChief_Map_Command_Toolkit.user.js"], cwd=ROOT, check=True)
subprocess.run(["python3", ".github/scripts/test_transport_sweep_lssm_contract.py"], cwd=ROOT, check=True)
subprocess.run(["cmp", "--silent", "dist/MissionChief_Map_Command_Toolkit.user.js", "dist/MissionChief_Map_Command_Toolkit.txt"], cwd=ROOT, check=True)
print("Issue #94 owned-window tracking fix applied successfully")
