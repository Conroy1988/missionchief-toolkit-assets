#!/usr/bin/env python3
from __future__ import annotations

import hashlib
import json
import re
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
SOURCE_PATH = ROOT / "src" / "MissionChief_Map_Command_Toolkit.user.js"
DIST_JS = ROOT / "dist" / "MissionChief_Map_Command_Toolkit.user.js"
DIST_TXT = ROOT / "dist" / "MissionChief_Map_Command_Toolkit.txt"
SHA_PATH = ROOT / "dist" / "SHA256SUMS.txt"
MANIFEST_PATH = ROOT / "dist" / "release-manifest.json"
CHANGELOG_PATH = ROOT / "CHANGELOG.md"
HELP_PATH = ROOT / "help" / "index.html"
FIXTURE_PATH = ROOT / ".github" / "fixtures" / "transport-sweep-lssm-contract.json"
TEST_PATH = ROOT / ".github" / "scripts" / "test_transport_sweep_lssm_contract.py"
REPORTS = [
    ROOT / ".github" / "reports" / "issue-127-transport-sweep-inspection.md",
    ROOT / ".github" / "reports" / "issue-127-transport-sweep-flow.md",
]

OLD_VERSION = "4.14.8"
NEW_VERSION = "4.14.9"


def replace_once(text: str, old: str, new: str, label: str) -> str:
    count = text.count(old)
    if count != 1:
        raise AssertionError(f"{label}: expected exactly one anchor, found {count}")
    return text.replace(old, new, 1)


source = SOURCE_PATH.read_text(encoding="utf-8")
if NEW_VERSION in source:
    raise AssertionError("Target version already present before Issue #127 migration")

source, metadata_count = re.subn(
    r"(//\s*@version\s+)" + re.escape(OLD_VERSION) + r"\b",
    rf"\g<1>{NEW_VERSION}",
    source,
    count=1,
)
if metadata_count != 1:
    raise AssertionError("Userscript metadata version anchor not found exactly once")
source = replace_once(
    source,
    f"version: '{OLD_VERSION}'",
    f"version: '{NEW_VERSION}'",
    "runtime version",
)

source = replace_once(
    source,
    "        missionInspectorId: 'mc-map-command-toolkit-mission-inspector',\n",
    "        missionInspectorId: 'mc-map-command-toolkit-mission-inspector',\n"
    "        transportSweepHudId: 'mc-map-command-toolkit-transport-sweep-hud',\n",
    "Transport Sweep HUD script ID",
)

source = replace_once(
    source,
    "        activeWindowCreatedLayer: false,\n"
    "        lastCandidateStats: null,\n"
    "        log: []\n",
    "        activeWindowCreatedLayer: false,\n"
    "        lastCandidateStats: null,\n"
    "        startedAt: 0,\n"
    "        missionIndex: 0,\n"
    "        missionTotal: 0,\n"
    "        currentItem: '',\n"
    "        statusMessage: '',\n"
    "        statusLevel: 'info',\n"
    "        hudFinal: false,\n"
    "        hudDismissTimer: null,\n"
    "        log: []\n",
    "Transport Sweep runtime HUD state",
)

hud_functions = r'''
    function transportSweepHudElements() {
        try { return Array.from(document.querySelectorAll(`#${SCRIPT.transportSweepHudId}`)); }
        catch (err) { return []; }
    }

    function ensureTransportSweepHud() {
        const matches = transportSweepHudElements();
        let hud = matches.shift() || null;
        for (const duplicate of matches) {
            try { duplicate.remove(); } catch (err) {}
        }
        if (hud?.isConnected) return hud;
        const mount = document.body || document.documentElement;
        if (!mount) return null;
        hud = document.createElement('section');
        hud.id = SCRIPT.transportSweepHudId;
        hud.className = 'mcms-transport-sweep-hud';
        hud.setAttribute('role', 'status');
        hud.setAttribute('aria-live', 'polite');
        hud.setAttribute('aria-atomic', 'true');
        mount.appendChild(hud);
        return hud;
    }

    function removeTransportSweepHud() {
        runtimeClearTimeout(transportSweepRuntime.hudDismissTimer);
        transportSweepRuntime.hudDismissTimer = null;
        for (const hud of transportSweepHudElements()) {
            try { hud.remove(); } catch (err) {}
        }
    }

    function scheduleTransportSweepHudDismiss(delay = 6500) {
        runtimeClearTimeout(transportSweepRuntime.hudDismissTimer);
        transportSweepRuntime.hudDismissTimer = runtimeSetTimeout(() => {
            transportSweepRuntime.hudDismissTimer = null;
            transportSweepRuntime.hudFinal = false;
            removeTransportSweepHud();
        }, Math.max(0, Number(delay) || 0));
    }

    function transportSweepHudElapsed() {
        const startedAt = Number(transportSweepRuntime.startedAt) || 0;
        if (!startedAt) return '0:00';
        const totalSeconds = Math.max(0, Math.floor((Date.now() - startedAt) / 1000));
        const minutes = Math.floor(totalSeconds / 60);
        return `${minutes}:${String(totalSeconds % 60).padStart(2, '0')}`;
    }

    function renderTransportSweepHud() {
        const sweep = transportSweepRuntime;
        const visible = sweep.running || sweep.stopRequested || sweep.hudFinal;
        if (!visible) {
            removeTransportSweepHud();
            return;
        }
        const hud = ensureTransportSweepHud();
        if (!hud) return;
        const total = Math.max(0, Number(sweep.missionTotal) || Number(sweep.queue?.length) || 0);
        const index = total ? Math.min(total, Math.max(1, Number(sweep.missionIndex) || 1)) : 0;
        const phase = sweep.hudFinal ? (sweep.statusLevel === 'error' ? 'Finished with errors' : 'Sweep complete')
            : sweep.stopRequested ? 'Stopping'
            : 'Sweep running';
        const current = String(sweep.currentItem || '').trim();
        const message = String(sweep.statusMessage || (sweep.running ? 'Preparing patient transport sweep' : phase)).trim();
        hud.dataset.state = sweep.hudFinal ? (sweep.errors ? 'error' : 'complete') : sweep.stopRequested ? 'stopping' : 'running';
        hud.innerHTML = `<div class="mcms-sweep-hud-head"><span><i></i>Patient Transport Sweep</span><b>${escapeHtml(phase)}</b></div><div class="mcms-sweep-hud-status">${escapeHtml(message)}</div>${current ? `<div class="mcms-sweep-hud-current">${escapeHtml(current)}</div>` : ''}<div class="mcms-sweep-hud-stats"><span><b>${index}/${total}</b><small>Missions</small></span><span class="mcms-sweep-hud-cleared"><b>${Math.max(0, Number(sweep.cleared) || 0)}</b><small>Patients cleared</small></span><span><b>${Math.max(0, Number(sweep.skipped) || 0)}</b><small>Skipped</small></span><span><b>${Math.max(0, Number(sweep.errors) || 0)}</b><small>Errors</small></span></div><div class="mcms-sweep-hud-foot"><span>${escapeHtml(transportSweepHudElapsed())} elapsed</span><span>${Math.max(0, Number(sweep.processed) || 0)} processed</span></div>`;
    }

    runtimeOnCleanup(removeTransportSweepHud);

'''
source = replace_once(
    source,
    "    function renderTransportSweepPanel() {\n",
    hud_functions + "    function renderTransportSweepPanel() {\n",
    "Transport Sweep HUD helpers",
)

source = replace_once(
    source,
    "    function renderTransportSweepPanel() {\n"
    "        const host = document.querySelector(`#${SCRIPT.panelId} [data-transport-sweep]`);\n"
    "        if (!host) return;\n"
    "        const runtime = transportSweepRuntime;\n",
    "    function renderTransportSweepPanel() {\n"
    "        renderTransportSweepHud();\n"
    "        const host = document.querySelector(`#${SCRIPT.panelId} [data-transport-sweep]`);\n"
    "        if (!host) return;\n"
    "        const runtime = transportSweepRuntime;\n",
    "HUD render before panel availability",
)

source = replace_once(
    source,
    "        transportSweepRuntime.log.unshift({ time: Date.now(), message: clean, level });\n",
    "        transportSweepRuntime.statusMessage = clean;\n"
    "        transportSweepRuntime.statusLevel = String(level || 'info');\n"
    "        transportSweepRuntime.log.unshift({ time: Date.now(), message: clean, level });\n",
    "Transport Sweep live status",
)

source = replace_once(
    source,
    "        transportSweepRuntime.currentMissionId = missionId;\n"
    "        renderTransportSweepPanel();\n",
    "        transportSweepRuntime.currentMissionId = missionId;\n"
    "        transportSweepRuntime.currentItem = String(item?.caption || `Mission ${missionId}`);\n"
    "        renderTransportSweepPanel();\n",
    "Current mission HUD item",
)

source = replace_once(
    source,
    "        if (!missionOpen || transportSweepRuntime.stopRequested) {\n"
    "            if (!transportSweepRuntime.stopRequested) transportSweepRuntime.skipped += 1;\n"
    "            return 0;\n"
    "        }\n",
    "        if (!missionOpen || transportSweepRuntime.stopRequested) {\n"
    "            if (!transportSweepRuntime.stopRequested) {\n"
    "                transportSweepRuntime.skipped += 1;\n"
    "                transportSweepLog(`Skipped ${item.caption} because its mission window did not become available`, 'warn');\n"
    "            }\n"
    "            return 0;\n"
    "        }\n",
    "Mission-open skip HUD update",
)

source = replace_once(
    source,
    "                    transportSweepRuntime.currentVehicleHref = lssmCandidate.actionHref;\n"
    "                    renderTransportSweepPanel();\n",
    "                    transportSweepRuntime.currentVehicleHref = lssmCandidate.actionHref;\n"
    "                    transportSweepRuntime.currentItem = `${lssmCandidate.label} · ${lssmCandidate.owner}`;\n"
    "                    renderTransportSweepPanel();\n",
    "Direct LSSM current HUD item",
)

source = replace_once(
    source,
    "            transportSweepRuntime.currentVehicleHref = candidate.href;\n"
    "            renderTransportSweepPanel();\n",
    "            transportSweepRuntime.currentVehicleHref = candidate.href;\n"
    "            transportSweepRuntime.currentItem = String(candidate.label || `Vehicle ${candidate.vehicleId}`);\n"
    "            renderTransportSweepPanel();\n",
    "Fallback current HUD item",
)

source = replace_once(
    source,
    "        if (clearedHere === 0 && !transportSweepRuntime.stopRequested) transportSweepRuntime.skipped += 1;\n"
    "        return clearedHere;\n",
    "        if (clearedHere === 0 && !transportSweepRuntime.stopRequested) {\n"
    "            transportSweepRuntime.skipped += 1;\n"
    "            renderTransportSweepPanel();\n"
    "        }\n"
    "        return clearedHere;\n",
    "Mission skipped HUD render",
)

source = replace_once(
    source,
    "        transportSweepRuntime.lastCandidateStats = null;\n"
    "        transportSweepRuntime.log = [];\n"
    "        renderTransportSweepPanel();\n",
    "        transportSweepRuntime.lastCandidateStats = null;\n"
    "        runtimeClearTimeout(transportSweepRuntime.hudDismissTimer);\n"
    "        transportSweepRuntime.hudDismissTimer = null;\n"
    "        transportSweepRuntime.startedAt = Date.now();\n"
    "        transportSweepRuntime.missionIndex = 0;\n"
    "        transportSweepRuntime.missionTotal = queue.length;\n"
    "        transportSweepRuntime.currentItem = 'Preparing sweep';\n"
    "        transportSweepRuntime.statusMessage = 'Preparing patient transport sweep';\n"
    "        transportSweepRuntime.statusLevel = 'info';\n"
    "        transportSweepRuntime.hudFinal = false;\n"
    "        transportSweepRuntime.log = [];\n"
    "        renderTransportSweepPanel();\n",
    "Sweep start HUD reset",
)

source = replace_once(
    source,
    "            for (const item of queue) {\n"
    "                if (transportSweepRuntime.stopRequested || transportSweepRuntime.cleared >= state.transportSweep.maxPerRun) break;\n"
    "                const remaining = state.transportSweep.maxPerRun - transportSweepRuntime.cleared;\n"
    "                await processTransportSweepMission(item, remaining);\n",
    "            for (let missionOffset = 0; missionOffset < queue.length; missionOffset += 1) {\n"
    "                const item = queue[missionOffset];\n"
    "                if (transportSweepRuntime.stopRequested || transportSweepRuntime.cleared >= state.transportSweep.maxPerRun) break;\n"
    "                transportSweepRuntime.missionIndex = missionOffset + 1;\n"
    "                transportSweepRuntime.currentItem = String(item?.caption || `Mission ${item?.missionId || missionOffset + 1}`);\n"
    "                renderTransportSweepPanel();\n"
    "                const remaining = state.transportSweep.maxPerRun - transportSweepRuntime.cleared;\n"
    "                await processTransportSweepMission(item, remaining);\n",
    "Indexed sweep loop",
)

source = replace_once(
    source,
    "            transportSweepRuntime.running = false;\n"
    "            transportSweepRuntime.stopRequested = false;\n"
    "            transportSweepRuntime.currentMissionId = null;\n"
    "            transportSweepRuntime.currentVehicleHref = '';\n"
    "            transportSweepRuntime.missionAnchorBaseline = new Set();\n"
    "            transportSweepRuntime.vehicleButtonBaseline = new Set();\n"
    "            transportSweepRuntime.activeWindowRoot = null;\n"
    "            transportSweepRuntime.ownedWindowLayers = new Set();\n"
    "            transportSweepRuntime.activeWindowCreatedLayer = false;\n"
    "            buildTransportSweepQueue();\n"
    "            renderTransportSweepPanel();\n"
    "            scheduleTransportWatcherRefresh(0);\n"
    "            showToast(wasStopped ? `Transport Sweep stopped · ${transportSweepRuntime.cleared} cleared` : `Transport Sweep complete · ${transportSweepRuntime.cleared} cleared`);\n"
    "            transportSweepLog(`${wasStopped ? 'Stopped' : 'Complete'}: ${transportSweepRuntime.cleared} cleared, ${transportSweepRuntime.skipped} skipped, ${transportSweepRuntime.errors} errors`);\n",
    "            transportSweepRuntime.running = false;\n"
    "            transportSweepRuntime.stopRequested = false;\n"
    "            transportSweepRuntime.currentMissionId = null;\n"
    "            transportSweepRuntime.currentVehicleHref = '';\n"
    "            transportSweepRuntime.currentItem = '';\n"
    "            transportSweepRuntime.missionAnchorBaseline = new Set();\n"
    "            transportSweepRuntime.vehicleButtonBaseline = new Set();\n"
    "            transportSweepRuntime.activeWindowRoot = null;\n"
    "            transportSweepRuntime.ownedWindowLayers = new Set();\n"
    "            transportSweepRuntime.activeWindowCreatedLayer = false;\n"
    "            transportSweepRuntime.hudFinal = true;\n"
    "            buildTransportSweepQueue();\n"
    "            scheduleTransportWatcherRefresh(0);\n"
    "            showToast(wasStopped ? `Transport Sweep stopped · ${transportSweepRuntime.cleared} cleared` : `Transport Sweep complete · ${transportSweepRuntime.cleared} cleared`);\n"
    "            transportSweepLog(`${wasStopped ? 'Stopped' : 'Complete'}: ${transportSweepRuntime.cleared} cleared, ${transportSweepRuntime.skipped} skipped, ${transportSweepRuntime.errors} errors`, transportSweepRuntime.errors ? 'error' : 'info');\n"
    "            scheduleTransportSweepHudDismiss(6500);\n",
    "Sweep final HUD summary",
)

css_anchor = "        #${SCRIPT.panelId} .mcms-sweep-log { max-height:72px !important; overflow-y:auto !important; margin-top:7px !important; padding:6px !important; border-radius:7px !important; background:rgba(0,0,0,.18) !important; color:rgba(255,255,255,.64) !important; font:700 7px/1.35 Arial,Helvetica,sans-serif !important; white-space:normal !important; }\n"
hud_css = r'''        #${SCRIPT.transportSweepHudId} { position:fixed !important; top:max(12px,env(safe-area-inset-top)) !important; right:max(12px,env(safe-area-inset-right)) !important; z-index:2147482000 !important; width:min(340px,calc(100vw - 24px)) !important; padding:11px !important; border:1px solid rgba(255,184,72,.72) !important; border-radius:12px !important; background:linear-gradient(145deg,rgba(18,23,31,.97),rgba(34,22,8,.97)) !important; color:#f8fbff !important; box-shadow:0 18px 55px rgba(0,0,0,.55),0 0 0 1px rgba(255,184,72,.08) inset !important; font:800 11px/1.25 Arial,Helvetica,sans-serif !important; pointer-events:none !important; touch-action:none !important; user-select:none !important; backdrop-filter:blur(12px) !important; -webkit-backdrop-filter:blur(12px) !important; }
        #${SCRIPT.transportSweepHudId}[data-state="complete"] { border-color:rgba(70,229,139,.78) !important; background:linear-gradient(145deg,rgba(12,29,25,.98),rgba(8,47,31,.97)) !important; }
        #${SCRIPT.transportSweepHudId}[data-state="error"] { border-color:rgba(255,100,108,.82) !important; background:linear-gradient(145deg,rgba(35,17,21,.98),rgba(54,12,18,.97)) !important; }
        #${SCRIPT.transportSweepHudId} .mcms-sweep-hud-head { display:flex !important; align-items:center !important; justify-content:space-between !important; gap:10px !important; }
        #${SCRIPT.transportSweepHudId} .mcms-sweep-hud-head span { min-width:0 !important; display:flex !important; align-items:center !important; gap:7px !important; color:#ffe3ad !important; font-size:11px !important; font-weight:950 !important; letter-spacing:.15px !important; }
        #${SCRIPT.transportSweepHudId} .mcms-sweep-hud-head i { width:8px !important; height:8px !important; flex:0 0 8px !important; border-radius:50% !important; background:#ffb648 !important; box-shadow:0 0 0 4px rgba(255,182,72,.13),0 0 12px rgba(255,182,72,.58) !important; }
        #${SCRIPT.transportSweepHudId}[data-state="complete"] .mcms-sweep-hud-head i { background:#46e58b !important; box-shadow:0 0 0 4px rgba(70,229,139,.13),0 0 12px rgba(70,229,139,.58) !important; }
        #${SCRIPT.transportSweepHudId} .mcms-sweep-hud-head b { flex:0 0 auto !important; padding:3px 7px !important; border-radius:999px !important; background:rgba(255,255,255,.09) !important; color:rgba(255,255,255,.74) !important; font-size:7px !important; font-weight:950 !important; text-transform:uppercase !important; letter-spacing:.45px !important; }
        #${SCRIPT.transportSweepHudId} .mcms-sweep-hud-status { margin-top:9px !important; color:#fff !important; font-size:10px !important; font-weight:900 !important; white-space:nowrap !important; overflow:hidden !important; text-overflow:ellipsis !important; }
        #${SCRIPT.transportSweepHudId} .mcms-sweep-hud-current { margin-top:3px !important; color:rgba(255,255,255,.58) !important; font-size:8px !important; font-weight:750 !important; white-space:nowrap !important; overflow:hidden !important; text-overflow:ellipsis !important; }
        #${SCRIPT.transportSweepHudId} .mcms-sweep-hud-stats { display:grid !important; grid-template-columns:repeat(4,minmax(0,1fr)) !important; gap:5px !important; margin-top:9px !important; }
        #${SCRIPT.transportSweepHudId} .mcms-sweep-hud-stats span { min-width:0 !important; padding:7px 4px !important; border-radius:8px !important; background:rgba(255,255,255,.055) !important; text-align:center !important; }
        #${SCRIPT.transportSweepHudId} .mcms-sweep-hud-stats b { display:block !important; color:#fff !important; font-size:13px !important; line-height:1 !important; }
        #${SCRIPT.transportSweepHudId} .mcms-sweep-hud-stats small { display:block !important; margin-top:4px !important; color:rgba(255,255,255,.48) !important; font-size:6.4px !important; font-weight:950 !important; text-transform:uppercase !important; letter-spacing:.25px !important; white-space:nowrap !important; overflow:hidden !important; text-overflow:ellipsis !important; }
        #${SCRIPT.transportSweepHudId} .mcms-sweep-hud-cleared { background:rgba(70,229,139,.15) !important; box-shadow:0 0 0 1px rgba(70,229,139,.24) inset !important; }
        #${SCRIPT.transportSweepHudId} .mcms-sweep-hud-cleared b { color:#73f2ab !important; font-size:17px !important; }
        #${SCRIPT.transportSweepHudId} .mcms-sweep-hud-foot { display:flex !important; justify-content:space-between !important; gap:8px !important; margin-top:8px !important; padding-top:7px !important; border-top:1px solid rgba(255,255,255,.09) !important; color:rgba(255,255,255,.42) !important; font-size:7px !important; font-weight:850 !important; text-transform:uppercase !important; letter-spacing:.25px !important; }
        @media (max-width:700px) {
            #${SCRIPT.transportSweepHudId} { top:auto !important; right:max(8px,env(safe-area-inset-right)) !important; bottom:max(8px,env(safe-area-inset-bottom)) !important; left:max(8px,env(safe-area-inset-left)) !important; width:auto !important; padding:9px !important; }
            #${SCRIPT.transportSweepHudId} .mcms-sweep-hud-current { display:none !important; }
            #${SCRIPT.transportSweepHudId} .mcms-sweep-hud-stats { gap:3px !important; }
        }
'''
source = replace_once(source, css_anchor, css_anchor + hud_css, "Transport Sweep HUD CSS")

fixture = json.loads(FIXTURE_PATH.read_text(encoding="utf-8"))
fixture["description"] = "LSSM direct alliance-patient release, persistent live HUD, multi-ambulance loop and DOM-delta-owned single-window lifecycle contract"
fixture["hud"] = {
    "id": "mc-map-command-toolkit-transport-sweep-hud",
    "final_summary_delay_ms": 6500,
    "required_stats": ["Missions", "Patients cleared", "Skipped", "Errors"],
    "mount": "document body outside sweep-owned lightbox layers",
    "desktop_anchor": "top-right",
    "mobile_anchor": "bottom-safe-area",
}
FIXTURE_PATH.write_text(json.dumps(fixture, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")

test_source = TEST_PATH.read_text(encoding="utf-8")
test_anchor = '    print("LSSM transport sweep contract passed")\n'
hud_test = r'''    hud = data["hud"]
    assert f"transportSweepHudId: '{hud['id']}'" in source, "HUD ID must be owned by SCRIPT"
    required_hud_markers = [
        "function transportSweepHudElements()",
        "function ensureTransportSweepHud()",
        "function removeTransportSweepHud()",
        "function scheduleTransportSweepHudDismiss(delay = 6500)",
        "function renderTransportSweepHud()",
        "runtimeOnCleanup(removeTransportSweepHud);",
        "document.body || document.documentElement",
        "pointer-events:none !important",
        "env(safe-area-inset-bottom)",
        "Patients cleared",
    ]
    missing_hud = [marker for marker in required_hud_markers if marker not in source]
    assert not missing_hud, f"Missing Transport Sweep HUD contract markers: {missing_hud}"
    assert source.count("runtimeOnCleanup(removeTransportSweepHud);") == 1, "HUD cleanup must be registered exactly once"
    assert source.count("transportSweepRuntime.cleared += 1") == 2, "Only the two confirmed direct/fallback release paths may increment cleared"

    renderer = re.search(r"function renderTransportSweepPanel\(\) \{([\s\S]*?)\n    \}", source)
    assert renderer, "Transport Sweep panel renderer is missing"
    renderer_text = renderer.group(1)
    assert renderer_text.index("renderTransportSweepHud();") < renderer_text.index("const host = document.querySelector"), "HUD must render even when the main Toolkit panel is unavailable"

    hud_renderer = re.search(r"function renderTransportSweepHud\(\) \{([\s\S]*?)\n    \}", source)
    assert hud_renderer, "Transport Sweep HUD renderer is missing"
    hud_text = hud_renderer.group(1)
    for stat in hud["required_stats"]:
        assert stat in hud_text, f"HUD is missing required stat: {stat}"
    assert "sweep.running || sweep.stopRequested || sweep.hudFinal" in hud_text, "HUD visibility must follow the complete sweep lifecycle"
    assert "sweep.cleared" in hud_text and "sweep.skipped" in hud_text and "sweep.errors" in hud_text, "HUD totals must come from the canonical runtime counters"

    ensure_hud = re.search(r"function ensureTransportSweepHud\(\) \{([\s\S]*?)\n    \}", source)
    remove_hud = re.search(r"function removeTransportSweepHud\(\) \{([\s\S]*?)\n    \}", source)
    assert ensure_hud and remove_hud, "HUD ownership helpers are missing"
    assert "matches.shift()" in ensure_hud.group(1) and "duplicate.remove()" in ensure_hud.group(1), "HUD creation must deduplicate existing instances"
    assert "for (const hud of transportSweepHudElements())" in remove_hud.group(1), "HUD teardown must remove every remaining instance"

    start_flow = re.search(r"async function startTransportSweep\(\) \{([\s\S]*?)\n    \}\n\n    function stopTransportSweep", source)
    assert start_flow, "Transport Sweep start flow is missing"
    start_text = start_flow.group(1)
    assert "transportSweepRuntime.startedAt = Date.now()" in start_text
    assert "transportSweepRuntime.missionTotal = queue.length" in start_text
    assert "transportSweepRuntime.hudFinal = false" in start_text
    assert "transportSweepRuntime.missionIndex = missionOffset + 1" in start_text
    assert "transportSweepRuntime.hudFinal = true" in start_text
    assert f"scheduleTransportSweepHudDismiss({hud['final_summary_delay_ms']})" in start_text

    direct_click = processor_text.index("const cleared = await activateTransportSweepLssmRelease")
    direct_increment = processor_text.index("transportSweepRuntime.cleared += 1", direct_click)
    direct_log = processor_text.index("transportSweepLog(`Released", direct_increment)
    assert direct_click < direct_increment < direct_log, "Direct LSSM HUD count must update only after confirmed release and then render through the canonical log"

    fallback_click = processor_text.index("button.click()")
    fallback_confirmation = processor_text.index("const cleared = await transportSweepWaitFor", fallback_click)
    fallback_increment = processor_text.index("transportSweepRuntime.cleared += 1", fallback_confirmation)
    fallback_log = processor_text.index("transportSweepLog(`Cleared", fallback_increment)
    assert fallback_click < fallback_confirmation < fallback_increment < fallback_log, "Fallback HUD count must update only after confirmed discharge and then render through the canonical log"

    assert hud["id"] not in closer.group(1), "MissionChief lightbox cleanup must not target the persistent HUD"
    assert "removeTransportSweepHud" not in closer.group(1), "Window replacement must not remove the persistent HUD"
'''
test_source = replace_once(test_source, test_anchor, hud_test + test_anchor, "Transport Sweep HUD contract tests")
TEST_PATH.write_text(test_source, encoding="utf-8")

changelog = CHANGELOG_PATH.read_text(encoding="utf-8")
entry = '''## [4.14.9] - 2026-07-17

### Added
- Ambulance Transport Sweep now displays a compact persistent live HUD while MissionChief and LSSM mission/vehicle windows are opening, processing and closing.
- The HUD shows current sweep status, mission progress, confirmed patients cleared, skipped items, errors, processed count and elapsed time.
- Successful clear totals update immediately after the existing confirmed LSSM or fallback discharge gate succeeds.

### Compatibility
- The HUD is mounted outside sweep-owned lightbox layers, deduplicated, non-blocking and removed on completion, cancellation or Toolkit runtime teardown.
- Desktop uses a top-right presentation; Tablet and iOS use a compact safe-area-aware bottom presentation.
- Manual start, personal-vehicle exclusion, prisoner handling, request sequencing and single-window safeguards remain unchanged.
- Added fixture-backed regression coverage for HUD ownership, lifecycle, confirmed counting and final-summary dismissal.

'''
changelog = replace_once(changelog, "## [Unreleased]\n\n", "## [Unreleased]\n\n" + entry, "4.14.9 changelog")
CHANGELOG_PATH.write_text(changelog, encoding="utf-8")

help_html = HELP_PATH.read_text(encoding="utf-8")
help_count = help_html.count("Guide for Toolkit v4.14.8")
if help_count != 1:
    raise AssertionError(f"Help version anchor expected once, found {help_count}")
HELP_PATH.write_text(help_html.replace("Guide for Toolkit v4.14.8", "Guide for Toolkit v4.14.9", 1), encoding="utf-8")

SOURCE_PATH.write_text(source, encoding="utf-8")
DIST_JS.write_text(source, encoding="utf-8")
DIST_TXT.write_text(source, encoding="utf-8")

digest = hashlib.sha256(source.encode("utf-8")).hexdigest()
SHA_PATH.write_text(
    f"{digest}  MissionChief_Map_Command_Toolkit.user.js\n"
    f"{digest}  MissionChief_Map_Command_Toolkit.txt\n",
    encoding="utf-8",
)

manifest = json.loads(MANIFEST_PATH.read_text(encoding="utf-8"))
manifest["version"] = NEW_VERSION
manifest["sha256"] = digest
manifest["bytes"] = len(source.encode("utf-8"))
manifest["lines"] = len(source.splitlines())
manifest.setdefault("metadata", {})["runtimeVersion"] = NEW_VERSION
manifest["baselineHashMatch"] = None
manifest["distributionStatus"] = "dry-run-not-yet-greasyfork-source"
MANIFEST_PATH.write_text(json.dumps(manifest, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")

for report in REPORTS:
    if report.exists():
        report.unlink()

assert source.count(f"version: '{NEW_VERSION}'") == 1
assert re.search(rf"//\s*@version\s+{re.escape(NEW_VERSION)}\b", source)
assert source.count("transportSweepHudId: 'mc-map-command-toolkit-transport-sweep-hud'") == 1
assert source.count("runtimeOnCleanup(removeTransportSweepHud);") == 1
assert source.count("transportSweepRuntime.cleared += 1") == 2
assert DIST_JS.read_bytes() == DIST_TXT.read_bytes() == SOURCE_PATH.read_bytes()

commands = [
    ["python3", ".github/scripts/test_transport_sweep_lssm_contract.py"],
    ["python3", ".github/scripts/validate_userscript.py"],
    ["node", "--check", str(SOURCE_PATH.relative_to(ROOT))],
    ["bash", ".github/scripts/run_userscript_preflight.sh", "--all"],
]
for command in commands:
    print("+", " ".join(command), flush=True)
    subprocess.run(command, cwd=ROOT, check=True)

print(f"Prepared Toolkit v{NEW_VERSION} with persistent Transport Sweep HUD")
