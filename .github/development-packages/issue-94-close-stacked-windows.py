#!/usr/bin/env python3
from __future__ import annotations

import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
SOURCE = ROOT / "src/MissionChief_Map_Command_Toolkit.user.js"
CHANGELOG = ROOT / "CHANGELOG.md"
TEST = ROOT / ".github/scripts/test_transport_sweep_lssm_contract.py"


def replace_once(text: str, old: str, new: str, label: str) -> str:
    count = text.count(old)
    if count != 1:
        raise RuntimeError(f"{label}: expected one match, found {count}")
    return text.replace(old, new, 1)


source = SOURCE.read_text(encoding="utf-8")
source = replace_once(source, "// @version      4.14.1", "// @version      4.14.2", "metadata version")
source = replace_once(source, "version: '4.14.1'", "version: '4.14.2'", "runtime version")
source = replace_once(source, "styleId: 'mc-map-command-toolkit-style-v4141'", "styleId: 'mc-map-command-toolkit-style-v4142'", "style id")
source = replace_once(source, "guideVersion: '4.14.1'", "guideVersion: '4.14.2'", "help guide version")
source = replace_once(
    source,
    "    pageWindow.__MC_MAP_COMMAND_TOOLKIT_V4141__ = true;",
    "    pageWindow.__MC_MAP_COMMAND_TOOLKIT_V4141__ = true;\n    pageWindow.__MC_MAP_COMMAND_TOOLKIT_V4142__ = true;",
    "runtime compatibility flag",
)

old_open = '''    async function openTransportSweepPath(path, mode) {
        if (transportSweepRuntime.stopRequested) return false;
        if (typeof pageWindow.lightboxOpen !== 'function') throw new Error('MissionChief lightboxOpen is unavailable');

        if (mode === 'mission') {
            transportSweepRuntime.missionAnchorBaseline = new Set(transportSweepVisibleVehicleAnchors());
            transportSweepRuntime.rejectedOwn = 0;
            transportSweepRuntime.missionWindowRoot = null;
            const beforeWindowText = transportSweepVisibleWindowRoots().map(root => String(root.textContent || '').trim()).join('|');
            const missionId = normaliseMissionId(String(path || '').match(/\/missions\/(\d+)/)?.[1]);
            pageWindow.lightboxOpen(path);
            await transportSweepWaitFor(() => {
                const root = transportSweepFindMissionWindowRoot(missionId);
                if (root) {
                    const anchors = transportSweepVehicleAnchorsWithin(root);
                    const afterText = String(root.textContent || '').trim();
                    const changed = afterText && !beforeWindowText.includes(afterText);
                    if (anchors.length || changed) {
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
            }, 3200, 120);
            return !transportSweepRuntime.stopRequested;
        }

        pageWindow.lightboxOpen(path);
        await transportSweepSleep(900);
        return !transportSweepRuntime.stopRequested;
    }
'''

new_open = '''    function transportSweepTopLevelWindowRoots() {
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

    async function openTransportSweepPath(path, mode) {
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
source = replace_once(source, old_open, new_open, "transport sweep window lifecycle")

old_vehicle = '''    async function openTransportSweepVehicle(candidate) {
        if (transportSweepRuntime.stopRequested || !candidate?.href) return null;
        transportSweepRuntime.vehicleButtonBaseline = new Set(transportSweepVisibleDischargeButtons());
        const beforeRoots = transportSweepVisibleWindowRoots();
        const beforeText = beforeRoots.map(root => String(root.textContent || '').trim()).join('|');

        let anchor = candidate.anchor;
        if (!anchor?.isConnected) {
            const root = transportSweepRuntime.missionWindowRoot?.isConnected ? transportSweepRuntime.missionWindowRoot : document;
            anchor = Array.from(root.querySelectorAll?.('a[href*="/vehicles/"]') || []).find(item => transportSweepVehicleIdFromHref(item.getAttribute('href')) === String(candidate.vehicleId));
        }

        let usedMissionClick = false;
        if (anchor?.isConnected) {
            try {
                anchor.scrollIntoView?.({ block: 'nearest', inline: 'nearest' });
                anchor.click();
                usedMissionClick = true;
            } catch (err) {}
        }

        if (!usedMissionClick) {
            if (typeof pageWindow.lightboxOpen !== 'function') return null;
            pageWindow.lightboxOpen(candidate.href);
        }

        const openedAt = Date.now();
        return await transportSweepWaitFor(() => {
            const button = findVisibleDischargePatientButton(transportSweepRuntime.vehicleButtonBaseline);
            if (button) return { opened: true, button };
            const afterText = transportSweepVisibleWindowRoots().map(root => String(root.textContent || '').trim()).join('|');
            if (afterText && afterText !== beforeText && Date.now() - openedAt > 350) return { opened: true, button: null };
            return null;
        }, 7500, 140);
    }
'''

new_vehicle = '''    async function openTransportSweepVehicle(candidate) {
        if (transportSweepRuntime.stopRequested || !candidate?.href) return null;
        transportSweepRuntime.vehicleButtonBaseline = new Set(transportSweepVisibleDischargeButtons());
        const opened = await openTransportSweepPath(candidate.href, 'vehicle');
        if (!opened || transportSweepRuntime.stopRequested) return null;

        const openedAt = Date.now();
        return await transportSweepWaitFor(() => {
            const button = findVisibleDischargePatientButton(transportSweepRuntime.vehicleButtonBaseline);
            if (button) return { opened: true, button };
            const roots = transportSweepTopLevelWindowRoots();
            if (roots.length && Date.now() - openedAt > 350) return { opened: true, button: null };
            return null;
        }, 7500, 140);
    }
'''
source = replace_once(source, old_vehicle, new_vehicle, "vehicle fallback window lifecycle")

old_tail = '''        if (clearedHere === 0 && !transportSweepRuntime.stopRequested) transportSweepRuntime.skipped += 1;
        return clearedHere;
    }

    async function startTransportSweep'''
new_tail = '''        await closeTransportSweepWindows('finishing the mission');

        if (clearedHere === 0 && !transportSweepRuntime.stopRequested) transportSweepRuntime.skipped += 1;
        return clearedHere;
    }

    async function startTransportSweep'''
source = replace_once(source, old_tail, new_tail, "mission completion window close")
SOURCE.write_text(source, encoding="utf-8")

changelog = CHANGELOG.read_text(encoding="utf-8")
entry = '''## [4.14.2] - 2026-07-17

### Fixed
- Prevented Patient Transport Sweep from stacking duplicate MissionChief mission and vehicle lightboxes during repeated alliance-ambulance processing.
- The sweep now closes and verifies removal of the active native window before reopening the same mission, opening a fallback vehicle, advancing to another mission or finishing the current mission.

### Performance
- Only one MissionChief lightbox remains active during the sweep, preventing the severe DOM, rendering and memory overhead caused by accumulated hidden mission windows.

'''
changelog = replace_once(changelog, "## [Unreleased]\n\n", "## [Unreleased]\n\n" + entry, "changelog entry")
CHANGELOG.write_text(changelog, encoding="utf-8")

test = TEST.read_text(encoding="utf-8")
test = replace_once(
    test,
    '        "if (transportSweepReleaseConfirmationVisible()) return true;",\n',
    '        "if (transportSweepReleaseConfirmationVisible()) return true;",\n        "async function closeTransportSweepWindows(reason = \'navigation\')",\n        "const closed = await closeTransportSweepWindows(mode === \'mission\' ? \'opening a mission\' : \'opening a vehicle\')",\n        "const opened = await openTransportSweepPath(candidate.href, \'vehicle\')",\n        "await closeTransportSweepWindows(\'finishing the mission\')",\n',
    "window lifecycle required markers",
)
test = replace_once(
    test,
    '    assert "lssmSeen ? 8000 : 18000" not in source, "A repeated mission load must not use an eight-second LSSM timeout"\n',
    '    assert "lssmSeen ? 8000 : 18000" not in source, "A repeated mission load must not use an eight-second LSSM timeout"\n    vehicle_processor = re.search(r"async function openTransportSweepVehicle\\(candidate\\) \\{([\\s\\S]*?)\\n    \\}", source)\n    assert vehicle_processor, "transport sweep vehicle opener is missing"\n    assert "anchor.click()" not in vehicle_processor.group(1), "fallback vehicles must not stack over the mission via an in-window click"\n    assert "pageWindow.lightboxOpen(candidate.href)" not in vehicle_processor.group(1), "fallback vehicles must use the managed single-window opener"\n    opener = re.search(r"async function openTransportSweepPath\\(path, mode\\) \\{([\\s\\S]*?)\\n    \\}", source)\n    assert opener, "transport sweep path opener is missing"\n    close_index = opener.group(1).index("await closeTransportSweepWindows")\n    open_index = opener.group(1).index("pageWindow.lightboxOpen(path)")\n    assert close_index < open_index, "the current MissionChief window must close before another opens"\n',
    "window lifecycle executable assertions",
)
TEST.write_text(test, encoding="utf-8")

subprocess.run(["python3", ".github/scripts/validate_userscript.py"], cwd=ROOT, check=True)
subprocess.run(["node", "--check", "src/MissionChief_Map_Command_Toolkit.user.js"], cwd=ROOT, check=True)
subprocess.run(["python3", ".github/scripts/test_transport_sweep_lssm_contract.py"], cwd=ROOT, check=True)
subprocess.run(["cmp", "--silent", "dist/MissionChief_Map_Command_Toolkit.user.js", "dist/MissionChief_Map_Command_Toolkit.txt"], cwd=ROOT, check=True)
print("Issue #94 stacked-window lifecycle fix applied successfully")
