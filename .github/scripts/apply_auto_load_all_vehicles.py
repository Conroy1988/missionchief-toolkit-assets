#!/usr/bin/env python3
"""One-time guarded patch for Issue #50.

This file is deleted by the patch before the resulting feature commit is made.
"""

from pathlib import Path

SOURCE_PATH = Path("src/MissionChief_Map_Command_Toolkit.user.js")
CHANGELOG_PATH = Path("CHANGELOG.md")
WORKFLOW_PATH = Path(".github/workflows/apply-auto-load-all-vehicles.yml")
SCRIPT_PATH = Path(".github/scripts/apply_auto_load_all_vehicles.py")

source = SOURCE_PATH.read_text(encoding="utf-8")


def replace_once(old: str, new: str, label: str) -> None:
    global source
    count = source.count(old)
    if count != 1:
        raise SystemExit(f"{label}: expected exactly one anchor, found {count}")
    source = source.replace(old, new, 1)


if "missing_vehicles_load" in source or "autoLoadAllVehicles" in source:
    raise SystemExit(
        "Auto-load vehicles feature already appears in the canonical source; "
        "refusing duplicate insertion."
    )

replace_once(
    "// @version      4.11.4",
    "// @version      4.12.0",
    "userscript metadata version",
)
replace_once(
    "version: '4.11.4'",
    "version: '4.12.0'",
    "internal runtime version",
)
replace_once(
    "styleId: 'mc-map-command-toolkit-style-v4114'",
    "styleId: 'mc-map-command-toolkit-style-v4120'",
    "stylesheet id",
)

replace_once(
    "            shortcuts: true,\n            allianceBuildingsMap: true,",
    "            shortcuts: true,\n"
    "            autoLoadAllVehicles: false,\n"
    "            allianceBuildingsMap: true,",
    "default setting",
)

replace_once(
    "            merged.commandBarOpen = merged.commandBarOpen !== false;\n"
    "            merged.allianceBuildingsMap = merged.allianceBuildingsMap !== false;",
    "            merged.commandBarOpen = merged.commandBarOpen !== false;\n"
    "            merged.autoLoadAllVehicles = merged.autoLoadAllVehicles === true;\n"
    "            merged.allianceBuildingsMap = merged.allianceBuildingsMap !== false;",
    "setting normalisation",
)

replace_once(
    "        if (feature === 'shortcuts') state.shortcuts = !state.shortcuts;\n"
    "        if (feature === 'allianceBuildingsMapBlocker') "
    "state.allianceBuildingsMap = state.allianceBuildingsMap === false;",
    "        if (feature === 'shortcuts') state.shortcuts = !state.shortcuts;\n"
    "        if (feature === 'autoLoadAllVehicles') {\n"
    "            state.autoLoadAllVehicles = !state.autoLoadAllVehicles;\n"
    "            if (state.autoLoadAllVehicles) installAutoLoadAllVehicles();\n"
    "            else stopAutoLoadAllVehicles();\n"
    "        }\n"
    "        if (feature === 'allianceBuildingsMapBlocker') "
    "state.allianceBuildingsMap = state.allianceBuildingsMap === false;",
    "toggle handler",
)

replace_once(
    "            shortcuts: state.shortcuts,\n"
    "            allianceBuildingsMapBlocker: state.allianceBuildingsMap === false,",
    "            shortcuts: state.shortcuts,\n"
    "            autoLoadAllVehicles: state.autoLoadAllVehicles,\n"
    "            allianceBuildingsMapBlocker: state.allianceBuildingsMap === false,",
    "toggle display state",
)

replace_once(
    "                    ${makeToggleButton('shortcuts', '⌨', 'Keys', "
    "'Keyboard shortcuts on/off. Map tools: 1–9. Vehicle Codes: V. "
    "Mission Age Watch: W. Menu: M.')}\n"
    "                    ${makeToggleButton('autoNight', '◑', 'AutoNight', "
    "'Automatically switch skins by time.')}",
    "                    ${makeToggleButton('shortcuts', '⌨', 'Keys', "
    "'Keyboard shortcuts on/off. Map tools: 1–9. Vehicle Codes: V. "
    "Mission Age Watch: W. Menu: M.')}\n"
    "                    ${makeToggleButton('autoLoadAllVehicles', '⇊', "
    "'Auto-load all vehicles', 'Automatically press MissionChief’s Load more "
    "vehicles control whenever an opened mission limits the vehicle list.')}\n"
    "                    ${makeToggleButton('autoNight', '◑', 'AutoNight', "
    "'Automatically switch skins by time.')}",
    "settings control",
)

FEATURE_CODE = r'''

    const AUTO_LOAD_ALL_VEHICLES_SELECTOR = 'a.missing_vehicles_load[href*="/missing_vehicles"]';
    const AUTO_LOAD_ALL_VEHICLES_MAX_REQUESTS = 50;
    const AUTO_LOAD_ALL_VEHICLES_SETTLE_MS = 180;
    const AUTO_LOAD_ALL_VEHICLES_TIMEOUT_MS = 6000;
    let autoLoadAllVehiclesObserver = null;
    let autoLoadAllVehiclesLinkObserver = null;
    let autoLoadAllVehiclesScanTimer = null;
    let autoLoadAllVehiclesReleaseTimer = null;
    let autoLoadAllVehiclesMissionId = null;
    let autoLoadAllVehiclesMissionRoot = null;
    let autoLoadAllVehiclesActiveLink = null;
    let autoLoadAllVehiclesInFlight = false;
    let autoLoadAllVehiclesRequestCount = 0;
    const autoLoadAllVehiclesRequestedPages = new Set();

    function autoLoadAllVehiclesLinkInfo(link) {
        if (!link || link.nodeType !== 1 || !link.matches(AUTO_LOAD_ALL_VEHICLES_SELECTOR)) return null;
        let url;
        try { url = new URL(link.getAttribute('href') || link.href, location.href); } catch (err) { return null; }
        if (url.origin !== location.origin) return null;
        const match = url.pathname.match(/^\/missions\/(\d+)\/missing_vehicles\/?$/u);
        if (!match) return null;
        const offsetPage = Math.max(0, Number(url.searchParams.get('offset_page')) || 0);
        return {
            missionId: match[1],
            offsetPage,
            signature: `${match[1]}:${offsetPage}:${url.pathname}${url.search}`,
            href: url.href
        };
    }

    function autoLoadAllVehiclesElementVisible(element) {
        if (!element?.isConnected || element.hidden || element.getAttribute('aria-hidden') === 'true') return false;
        if (element.matches?.(':disabled, .disabled, [aria-disabled="true"]')) return false;
        try {
            const style = pageWindow.getComputedStyle?.(element);
            if (style?.display === 'none' || style?.visibility === 'hidden' || Number(style?.opacity) === 0) return false;
            const rect = element.getBoundingClientRect?.();
            return !rect || (rect.width > 1 && rect.height > 1);
        } catch (err) {
            return true;
        }
    }

    function autoLoadAllVehiclesResolveMissionRoot(link) {
        const explicit = link.closest?.('#mission_general_info, #mission_content, #mission_reply, .mission_content, .mission-window, .mission_window, .modal.show, .modal.in, [role="dialog"]');
        if (explicit) return explicit;
        let current = link.parentElement;
        for (let depth = 0; current && current !== document.body && depth < 10; depth += 1, current = current.parentElement) {
            const signal = `${current.id || ''} ${typeof current.className === 'string' ? current.className : ''}`;
            if (/\bmission(?:[-_\s]|$)/iu.test(signal)) return current;
        }
        return link.parentElement || document.body;
    }

    function findAutoLoadAllVehiclesLink() {
        if (!state.autoLoadAllVehicles) return null;
        return Array.from(document.querySelectorAll(AUTO_LOAD_ALL_VEHICLES_SELECTOR)).find(link => {
            const info = autoLoadAllVehiclesLinkInfo(link);
            return info && autoLoadAllVehiclesElementVisible(link);
        }) || null;
    }

    function resetAutoLoadAllVehiclesMission() {
        autoLoadAllVehiclesMissionId = null;
        autoLoadAllVehiclesMissionRoot = null;
        autoLoadAllVehiclesActiveLink = null;
        autoLoadAllVehiclesInFlight = false;
        autoLoadAllVehiclesRequestCount = 0;
        autoLoadAllVehiclesRequestedPages.clear();
        runtimeClearTimeout(autoLoadAllVehiclesReleaseTimer);
        autoLoadAllVehiclesReleaseTimer = null;
        try { autoLoadAllVehiclesLinkObserver?.disconnect(); } catch (err) {}
        autoLoadAllVehiclesLinkObserver = null;
    }

    function observeAutoLoadAllVehiclesLink(link) {
        try { autoLoadAllVehiclesLinkObserver?.disconnect(); } catch (err) {}
        autoLoadAllVehiclesLinkObserver = null;
        if (!link) return;
        const observer = new MutationObserver(() => {
            if (!state.autoLoadAllVehicles) return;
            const currentInfo = autoLoadAllVehiclesLinkInfo(link);
            if (!link.isConnected || !currentInfo || !autoLoadAllVehiclesElementVisible(link)) {
                autoLoadAllVehiclesInFlight = false;
                scheduleAutoLoadAllVehiclesScan(AUTO_LOAD_ALL_VEHICLES_SETTLE_MS);
                return;
            }
            if (autoLoadAllVehiclesActiveLink && currentInfo.href !== autoLoadAllVehiclesActiveLink.dataset.mcmsAutoLoadHref) {
                autoLoadAllVehiclesInFlight = false;
                scheduleAutoLoadAllVehiclesScan(AUTO_LOAD_ALL_VEHICLES_SETTLE_MS);
            }
        });
        observer.observe(link, {
            attributes: true,
            attributeFilter: ['href', 'style', 'class', 'hidden', 'aria-hidden', 'aria-disabled']
        });
        autoLoadAllVehiclesLinkObserver = observer;
    }

    function scheduleAutoLoadAllVehiclesScan(delay = 0) {
        if (!state.autoLoadAllVehicles || runtime.destroyed) return;
        runtimeClearTimeout(autoLoadAllVehiclesScanTimer);
        autoLoadAllVehiclesScanTimer = runtimeSetTimeout(() => {
            autoLoadAllVehiclesScanTimer = null;
            scanAutoLoadAllVehicles();
        }, Math.max(0, Number(delay) || 0));
    }

    function scanAutoLoadAllVehicles() {
        if (!state.autoLoadAllVehicles || runtime.destroyed || autoLoadAllVehiclesInFlight) return false;
        const link = findAutoLoadAllVehiclesLink();
        if (!link) {
            if (autoLoadAllVehiclesMissionRoot && (!autoLoadAllVehiclesMissionRoot.isConnected || !autoLoadAllVehiclesElementVisible(autoLoadAllVehiclesMissionRoot))) {
                resetAutoLoadAllVehiclesMission();
            }
            return false;
        }

        const info = autoLoadAllVehiclesLinkInfo(link);
        if (!info) return false;
        const missionRoot = autoLoadAllVehiclesResolveMissionRoot(link);
        if (info.missionId !== autoLoadAllVehiclesMissionId || missionRoot !== autoLoadAllVehiclesMissionRoot) {
            resetAutoLoadAllVehiclesMission();
            autoLoadAllVehiclesMissionId = info.missionId;
            autoLoadAllVehiclesMissionRoot = missionRoot;
        }
        if (autoLoadAllVehiclesRequestedPages.has(info.signature)) return false;
        if (autoLoadAllVehiclesRequestCount >= AUTO_LOAD_ALL_VEHICLES_MAX_REQUESTS) {
            console.warn(`[${SCRIPT.name}] Auto-load all vehicles stopped after ${AUTO_LOAD_ALL_VEHICLES_MAX_REQUESTS} requests for mission ${info.missionId}.`);
            return false;
        }

        autoLoadAllVehiclesRequestedPages.add(info.signature);
        autoLoadAllVehiclesRequestCount += 1;
        autoLoadAllVehiclesInFlight = true;
        autoLoadAllVehiclesActiveLink = link;
        link.dataset.mcmsAutoLoadHref = info.href;
        link.dataset.mcmsAutoLoadRequested = 'true';
        observeAutoLoadAllVehiclesLink(link);

        try {
            link.click();
        } catch (err) {
            autoLoadAllVehiclesInFlight = false;
            autoLoadAllVehiclesRequestedPages.delete(info.signature);
            console.warn(`[${SCRIPT.name}] Auto-load all vehicles could not activate MissionChief's native control.`, err);
            return false;
        }

        runtimeClearTimeout(autoLoadAllVehiclesReleaseTimer);
        autoLoadAllVehiclesReleaseTimer = runtimeSetTimeout(() => {
            autoLoadAllVehiclesReleaseTimer = null;
            autoLoadAllVehiclesInFlight = false;
            scheduleAutoLoadAllVehiclesScan(AUTO_LOAD_ALL_VEHICLES_SETTLE_MS);
        }, AUTO_LOAD_ALL_VEHICLES_TIMEOUT_MS);
        return true;
    }

    function stopAutoLoadAllVehicles() {
        runtimeClearTimeout(autoLoadAllVehiclesScanTimer);
        autoLoadAllVehiclesScanTimer = null;
        try { autoLoadAllVehiclesObserver?.disconnect(); } catch (err) {}
        autoLoadAllVehiclesObserver = null;
        resetAutoLoadAllVehiclesMission();
    }

    function installAutoLoadAllVehicles() {
        if (!state.autoLoadAllVehicles || runtime.destroyed) {
            stopAutoLoadAllVehicles();
            return false;
        }
        if (!autoLoadAllVehiclesObserver) {
            const observer = new MutationObserver(mutations => {
                const relevant = autoLoadAllVehiclesInFlight || mutations.some(mutation => {
                    const nodes = [
                        ...Array.from(mutation.addedNodes || []),
                        ...Array.from(mutation.removedNodes || [])
                    ];
                    return nodes.some(node => node?.nodeType === 1 && (
                        node.matches?.(AUTO_LOAD_ALL_VEHICLES_SELECTOR) ||
                        node.querySelector?.(AUTO_LOAD_ALL_VEHICLES_SELECTOR) ||
                        node === autoLoadAllVehiclesMissionRoot ||
                        autoLoadAllVehiclesMissionRoot?.contains?.(node)
                    ));
                });
                if (!relevant) return;
                if (autoLoadAllVehiclesActiveLink && (!autoLoadAllVehiclesActiveLink.isConnected || !autoLoadAllVehiclesElementVisible(autoLoadAllVehiclesActiveLink))) {
                    autoLoadAllVehiclesInFlight = false;
                }
                scheduleAutoLoadAllVehiclesScan(AUTO_LOAD_ALL_VEHICLES_SETTLE_MS);
            });
            const begin = () => {
                if (document.body && !runtime.destroyed) {
                    observer.observe(document.body, { childList: true, subtree: true });
                }
            };
            if (document.body) begin();
            else runtimeListen(document, 'DOMContentLoaded', begin, { once: true });
            autoLoadAllVehiclesObserver = observer;
        }
        scheduleAutoLoadAllVehiclesScan(0);
        return true;
    }

'''

replace_once(
    "\n    function boot() {",
    FEATURE_CODE + "    function boot() {",
    "feature implementation insertion",
)
replace_once(
    "        createCleanExit();\n        scanInlineMissionMarkerData();",
    "        createCleanExit();\n"
    "        installAutoLoadAllVehicles();\n"
    "        scanInlineMissionMarkerData();",
    "boot installation",
)
replace_once(
    "            transportSweepRuntime.stopRequested = true;\n"
    "            document.removeEventListener('mousemove', movePanelDrag, true);",
    "            transportSweepRuntime.stopRequested = true;\n"
    "            stopAutoLoadAllVehicles();\n"
    "            document.removeEventListener('mousemove', movePanelDrag, true);",
    "runtime cleanup",
)

SOURCE_PATH.write_text(source, encoding="utf-8")

changelog = CHANGELOG_PATH.read_text(encoding="utf-8")
marker = "## [Unreleased]\n"
if changelog.count(marker) != 1:
    raise SystemExit("Changelog Unreleased anchor missing or duplicated.")
entry = """## [Unreleased]

## [4.12.0] - 2026-07-15

### Added
- Added an optional **Auto-load all vehicles** Toolkit setting for mission windows where MissionChief limits the displayed vehicle list.
- Added language-independent detection of MissionChief's native `.missing_vehicles_load` control and sequential loading of additional offset pages.

### Safety
- Added per-mission request deduplication, a 50-request hard limit, mutation-driven retries and six-second request timeouts.
- Preserved MissionChief's manual load-more control when the option is disabled and avoided any vehicle selection or dispatch action.

### Compatibility
- Preserved settings import/export, all interface themes and Desktop, Tablet and iOS modes.
"""
CHANGELOG_PATH.write_text(changelog.replace(marker, entry, 1), encoding="utf-8")

for path in (WORKFLOW_PATH, SCRIPT_PATH):
    path.unlink()
