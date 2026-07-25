#!/usr/bin/env python3
"""Apply the Issue #512 Main Toolbar bootstrap performance correction."""
from __future__ import annotations

import hashlib
import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
SOURCE = ROOT / "src/MissionChief_Map_Command_Toolkit.user.js"
STYLE_FIXTURE = ROOT / ".github/fixtures/main-style-source-headroom.json"
EVIDENCE = ROOT / "docs/audits/v6-critical-performance-evidence.json"
BASELINE = ROOT / "docs/audits/v6-critical-performance-baseline.md"
CHANGELOG = ROOT / "CHANGELOG.md"


def replace_once(text: str, old: str, new: str, label: str) -> str:
    count = text.count(old)
    if count != 1:
        raise SystemExit(f"{label}: expected one match, found {count}")
    return text.replace(old, new, 1)


def canonical_css_formatting(raw: str) -> str:
    lines = raw.split("\n")
    removable = {index for index in range(1, len(lines) - 1) if not lines[index].strip()}
    index = 1
    while index < len(lines) - 1:
        stripped = lines[index].strip()
        if not stripped.startswith("/*"):
            index += 1
            continue
        start = index
        end = index
        valid = "${" not in lines[index]
        remainder = stripped[2:]
        if "*/" in remainder:
            valid = valid and not remainder.split("*/", 1)[1].strip()
        else:
            found = False
            cursor = index + 1
            while cursor < len(lines) - 1:
                end = cursor
                if "${" in lines[cursor]:
                    valid = False
                if "*/" in lines[cursor]:
                    valid = valid and not lines[cursor].split("*/", 1)[1].strip()
                    found = True
                    break
                cursor += 1
            if not found:
                valid = False
        if valid:
            removable.update(range(start, end + 1))
        index = end + 1
    stripped = "\n".join(line for line_index, line in enumerate(lines) if line_index not in removable)
    return re.sub(r"\n[\t ]*}", "}", stripped)


def extract_main_style(source: str) -> str:
    function_start = source.index("function installMainStyles()")
    template_start = source.index("addStyle(`", function_start) + len("addStyle(`")
    end_anchor = source.index("recordStartupMetric('stylesheetInstallMs'", template_start)
    template_end = source.rfind("`);", template_start, end_anchor)
    if template_end < 0:
        raise SystemExit("installMainStyles template closing was not found")
    return source[template_start:template_end]


def apply_source_fix() -> str:
    source = SOURCE.read_text(encoding="utf-8")
    if "// @version      6.0.0" not in source:
        raise SystemExit("Issue #512 builder expected Toolkit v6.0.0")

    source = replace_once(
        source,
        "        cleanupCallbacks: [],\n        destroy(reason = 'runtime shutdown') {",
        "        cleanupCallbacks: [],\n        toolbarDiagnostics: { observerCallbacks: 0, mutationsSeen: 0, integrityChecks: 0, recoveries: 0, ensureUiCalls: 0 },\n        destroy(reason = 'runtime shutdown') {",
        "runtime toolbar diagnostics",
    )
    source = replace_once(
        source,
        "        if (pageWindow[RUNTIME_KEY] === this) {\n            try { delete pageWindow[RUNTIME_KEY]; } catch (err) { pageWindow[RUNTIME_KEY] = null; }\n        }\n        }\n    };",
        "        if (pageWindow[RUNTIME_KEY] === this) {\n            try { delete pageWindow[RUNTIME_KEY]; } catch (err) { pageWindow[RUNTIME_KEY] = null; }\n        }\n        if (pageWindow.__MCMS_TOOLBAR_DIAGNOSTICS__ === this.toolbarDiagnostics) {\n            try { delete pageWindow.__MCMS_TOOLBAR_DIAGNOSTICS__; } catch (err) { pageWindow.__MCMS_TOOLBAR_DIAGNOSTICS__ = null; }\n        }\n        }\n    };",
        "runtime toolbar diagnostics cleanup",
    )
    source = replace_once(
        source,
        "    pageWindow[RUNTIME_KEY] = runtime;\n",
        "    pageWindow[RUNTIME_KEY] = runtime;\n    pageWindow.__MCMS_TOOLBAR_DIAGNOSTICS__ = runtime.toolbarDiagnostics;\n",
        "toolbar diagnostics publication",
    )

    helpers_start = source.index("    function mutationBelongsToToolkit(mutation) {")
    helpers_end = source.index("\n\n\n    const ALLIANCE_BUILDINGS_MAP_NOTICE_ID", helpers_start)
    helpers = r'''    function toolkitMainToolbarHealthy() {
        if (!toolkitTopLevelDocument(document) || runtime.destroyed) return true;
        const control = document.getElementById(SCRIPT.controlId);
        if (!control?.isConnected) return false;
        if (!control.querySelector?.('.mcms-shell') || !control.querySelector?.('.mcms-floating-filter')) return false;
        if (settingsPanelActivated && !document.getElementById(SCRIPT.panelId)?.isConnected) return false;
        return true;
    }

    function mutationRemovesToolkitUi(mutation) {
        for (const node of mutation?.removedNodes || []) {
            if (!node || node.nodeType !== 1) continue;
            if ([SCRIPT.panelId, SCRIPT.controlId, SCRIPT.majorIncidentFeedId].includes(node.id)) return true;
            if (node.querySelector?.(`#${SCRIPT.panelId}, #${SCRIPT.controlId}, #${SCRIPT.majorIncidentFeedId}`)) return true;
        }
        return false;
    }

    function mutationReplacesPrimaryMapHost(mutation) {
        if (!mutation || mutation.type !== 'childList') return false;
        const selector = '#map, #map_outer, .leaflet-container';
        for (const collection of [mutation.addedNodes, mutation.removedNodes]) {
            for (const node of collection || []) {
                if (!node || node.nodeType !== 1) continue;
                if (node.matches?.(selector) || node.querySelector?.(selector)) return true;
            }
        }
        return false;
    }
'''
    source = source[:helpers_start] + helpers + source[helpers_end:]

    connect_start = source.index("    function connectMainMutationObserver() {")
    connect_end = source.index("\n    async function runDeferredOperationalStartup()", connect_start)
    connect = r'''    function connectMainMutationObserver() {
        if (!mainMutationObserver || runtime.destroyed || !document.body) return;
        try { mainMutationObserver.disconnect(); } catch (err) {}
        const control = document.getElementById(SCRIPT.controlId);
        const controlHost = control?.parentElement;
        if (controlHost?.isConnected && controlHost !== document.body) {
            mainMutationObserver.observe(controlHost, { childList: true, subtree: false });
        }
        mainMutationObserver.observe(document.body, { childList: true, subtree: false });
        mainMutationObserverFallbackActive = false;
    }
'''
    source = source[:connect_start] + connect + source[connect_end:]

    source = replace_once(
        source,
        "    function ensureUi() {\n        operationalWindowEnsureSettingsStyle(document);",
        "    function ensureUi() {\n        runtime.toolbarDiagnostics.ensureUiCalls += 1;\n        operationalWindowEnsureSettingsStyle(document);",
        "ensureUi diagnostics",
    )

    source = replace_once(
        source,
        "        runtimeRegisterTask('ui-integrity', 2500, () => { if (!document.hidden) return ensureUi(); }, { intervalResolver: () => document.hidden ? 30000 : 2500, economyIntervalMs: 5000, economyIntervalResolver: () => document.hidden ? 30000 : 5000 });",
        "        runtimeRegisterTask('ui-integrity', 30000, () => {\n            runtime.toolbarDiagnostics.integrityChecks += 1;\n            if (document.hidden || runtime.destroyed || toolkitMainToolbarHealthy()) return;\n            runtime.toolbarDiagnostics.recoveries += 1;\n            invalidateMapElementCache();\n            ensureUi();\n            connectMainMutationObserver();\n        }, {\n            intervalResolver: () => document.hidden ? 120000 : 30000,\n            economyIntervalMs: 60000,\n            economyIntervalResolver: () => document.hidden ? 120000 : 60000\n        });",
        "ui integrity cadence",
    )

    boot_start = source.index("    function boot() {")
    observer_start = source.index("        const observer = runtimeTrackObserver(new MutationObserver(mutations => {", boot_start)
    observer_end = source.index("        mainMutationObserver = observer;", observer_start)
    observer = r'''        const observer = runtimeTrackObserver(new MutationObserver(mutations => {
            runtime.toolbarDiagnostics.observerCallbacks += 1;
            runtime.toolbarDiagnostics.mutationsSeen += mutations.length;
            if (runtime.destroyed || document.hidden) return;
            let toolkitUiRemoved = false;
            let mapHostReplaced = false;
            for (const mutation of mutations) {
                if (!toolkitUiRemoved && mutationRemovesToolkitUi(mutation)) toolkitUiRemoved = true;
                if (!mapHostReplaced && mutationReplacesPrimaryMapHost(mutation)) mapHostReplaced = true;
                if (toolkitUiRemoved && mapHostReplaced) break;
            }
            if (!toolkitUiRemoved && !mapHostReplaced) return;
            runtimeClearTimeout(mutationTimer);
            mutationTimer = runtimeSetTimeout(() => {
                if (runtime.destroyed || document.hidden || dragState) return;
                if (mapHostReplaced) invalidateMapElementCache();
                if (!toolkitMainToolbarHealthy() || mapHostReplaced) {
                    runtime.toolbarDiagnostics.recoveries += 1;
                    ensureUi();
                }
                connectMainMutationObserver();
                if (mapHostReplaced) {
                    refreshSuppression();
                    fitControlToMap();
                    schedulePanelPosition(true, 80);
                }
            }, 120);
        }));
'''
    source = source[:observer_start] + observer + source[observer_end:]

    forbidden = [
        "mainMutationObserver.observe(document.body, { childList: true, subtree: true });",
        "runtimeRegisterTask('ui-integrity', 2500",
        "function mutationAffectsMissionData(",
        "function mutationBelongsToToolkit(",
        "function mutationAddsLeafletMarkerIcon(",
    ]
    present = [token for token in forbidden if token in source]
    if present:
        raise SystemExit(f"Issue #512 retired hot-path fragments remain: {present}")
    SOURCE.write_text(source, encoding="utf-8")
    return source


def write_contract() -> None:
    path = ROOT / ".github/scripts/test_issue512_main_toolbar_bootstrap_contract.py"
    path.write_text(r'''#!/usr/bin/env python3
from __future__ import annotations
import re
from pathlib import Path
ROOT = Path(__file__).resolve().parents[2]
source = (ROOT / "src/MissionChief_Map_Command_Toolkit.user.js").read_text(encoding="utf-8")

def function_body(name: str) -> str:
    match = re.search(rf"(?m)^\s*function\s+{re.escape(name)}\s*\(", source)
    assert match, f"Function not found: {name}"
    opening = source.find("{", match.start())
    depth = 0
    quote = None
    escaped = False
    for index in range(opening, len(source)):
        char = source[index]
        if quote:
            if escaped: escaped = False
            elif char == "\\": escaped = True
            elif char == quote: quote = None
            continue
        if char in "'\"`": quote = char
        elif char == "{": depth += 1
        elif char == "}":
            depth -= 1
            if depth == 0: return source[match.start():index + 1]
    raise AssertionError(f"Unclosed function: {name}")

connect = function_body("connectMainMutationObserver")
assert "subtree: true" not in connect
assert "document.querySelector('#missions" not in connect
assert "mainMutationObserver.observe(document.body, { childList: true, subtree: false });" in connect
assert "controlHost" in connect
healthy = function_body("toolkitMainToolbarHealthy")
assert "document.getElementById(SCRIPT.controlId)" in healthy
assert "settingsPanelActivated" in healthy
boot = function_body("boot")
observer_start = boot.index("const observer = runtimeTrackObserver(new MutationObserver(mutations => {")
observer_end = boot.index("mainMutationObserver = observer;", observer_start)
observer = boot[observer_start:observer_end]
for forbidden in ["mutationAffectsMissionData", "mutationBelongsToToolkit", "mutationAddsLeafletMarkerIcon", "scheduleEnabledMapRefreshes", "scheduleOperationalSuiteScan"]:
    assert forbidden not in observer, f"Broad steady-state mutation work returned: {forbidden}"
assert "mutationRemovesToolkitUi" in observer
assert "mutationReplacesPrimaryMapHost" in observer
assert "toolkitMainToolbarHealthy" in observer
maintenance = function_body("registerBootMaintenanceTasks")
assert "runtimeRegisterTask('ui-integrity', 30000" in maintenance
assert "toolkitMainToolbarHealthy()" in maintenance
assert "document.hidden ? 120000 : 30000" in maintenance
assert "runtime.toolbarDiagnostics.observerCallbacks += 1" in source
assert "runtime.toolbarDiagnostics.ensureUiCalls += 1" in source
assert "runtimeRegisterTask('ui-integrity', 2500" not in source
assert "mainMutationObserver.observe(document.body, { childList: true, subtree: true });" not in source
print("Issue #512 Main Toolbar bootstrap contract passed.")
''', encoding="utf-8")


def update_contract_runners() -> None:
    preflight = ROOT / ".github/scripts/run_userscript_preflight.sh"
    text = preflight.read_text(encoding="utf-8")
    marker = "  .github/scripts/test_root_attribute_write_suppression_contract.py\n"
    if "test_issue512_main_toolbar_bootstrap_contract.py" not in text:
        text = replace_once(text, marker, marker + "  .github/scripts/test_issue512_main_toolbar_bootstrap_contract.py\n", "preflight contract registration")
        preflight.write_text(text, encoding="utf-8")

    validator = ROOT / ".github/scripts/validate_userscript.py"
    text = validator.read_text(encoding="utf-8")
    if "ISSUE512_MAIN_TOOLBAR_CONTRACT" not in text:
        constant = "ISSUE470_MENU_REQUIREMENTS_RUNTIME = ROOT / \".github\" / \"scripts\" / \"test_issue470_menu_requirements_runtime.js\"\n"
        text = replace_once(text, constant, constant + "ISSUE512_MAIN_TOOLBAR_CONTRACT = ROOT / \".github\" / \"scripts\" / \"test_issue512_main_toolbar_bootstrap_contract.py\"\n", "validator constant")
        text = replace_once(text, "ISSUE464_OPERATIONAL_RUNTIME, ISSUE470_MENU_REQUIREMENTS_RUNTIME]", "ISSUE464_OPERATIONAL_RUNTIME, ISSUE470_MENU_REQUIREMENTS_RUNTIME, ISSUE512_MAIN_TOOLBAR_CONTRACT]", "validator required tooling")
        run_marker = "        if issue470_menu_requirements.returncode != 0:\n            fail(\"Issue #470 menu/requirements runtime fixtures failed\")\n"
        run_block = run_marker + "\n        issue512_main_toolbar = subprocess.run(\n            [sys.executable, str(ISSUE512_MAIN_TOOLBAR_CONTRACT)], cwd=ROOT,\n        )\n        if issue512_main_toolbar.returncode != 0:\n            fail(\"Issue #512 Main Toolbar bootstrap contract failed\")\n"
        text = replace_once(text, run_marker, run_block, "validator contract execution")
        validator.write_text(text, encoding="utf-8")

    workflow = ROOT / ".github/workflows/v6-critical-performance.yml"
    text = workflow.read_text(encoding="utf-8")
    if "test_issue512_main_toolbar_bootstrap_contract.py" not in text:
        text = replace_once(text, "      - \".github/scripts/test_v6_*.py\"\n", "      - \".github/scripts/test_v6_*.py\"\n      - \".github/scripts/test_issue512_main_toolbar_bootstrap_contract.py\"\n", "v6 path registration")
        step = "      - name: Enforce v6 runtime budgets\n        shell: bash\n        run: |\n          set -o pipefail\n          python3 .github/scripts/test_v6_operational_runtime_budget.py \\\n            | tee v6-critical-performance-budget.json\n"
        replacement = step + "\n      - name: Validate Main Toolbar bounded bootstrap\n        run: python3 .github/scripts/test_issue512_main_toolbar_bootstrap_contract.py\n"
        text = replace_once(text, step, replacement, "v6 workflow contract step")
        workflow.write_text(text, encoding="utf-8")


def update_v6_budget_contract() -> None:
    path = ROOT / ".github/scripts/test_v6_operational_runtime_budget.py"
    text = path.read_text(encoding="utf-8")
    text = text.replace('        "if (operationalSuiteEnabled()) scheduleOperationalSuiteScan(120);",\n', '        "mainMutationObserver.observe(document.body, { childList: true, subtree: false });",\n        "if (document.hidden || runtime.destroyed || toolkitMainToolbarHealthy()) return;",\n')
    forbidden_marker = '        "for (const root of roots) {\\n            context.observer.observe(root, {\\n                childList: true,\\n                subtree: true,\\n                characterData: true",\n'
    if "runtimeRegisterTask('ui-integrity', 2500" not in text:
        text = replace_once(text, forbidden_marker, forbidden_marker + '        "runtimeRegisterTask(\'ui-integrity\', 2500",\n        "mainMutationObserver.observe(document.body, { childList: true, subtree: true });",\n        "function mutationAffectsMissionData(",\n', "v6 forbidden toolbar hot paths")
    path.write_text(text, encoding="utf-8")


def update_evidence(source: str) -> None:
    raw = source.encode("utf-8")
    source_sha = hashlib.sha256(raw).hexdigest()
    source_bytes = len(raw)
    source_lines = len(source.splitlines())
    template = extract_main_style(source)
    fixture = json.loads(STYLE_FIXTURE.read_text(encoding="utf-8"))
    profile = fixture["v6Candidate"]
    profile.update({
        "sourceBytes": source_bytes,
        "sourceLines": source_lines,
        "sourceSha256": source_sha,
        "templateBytes": len(template.encode("utf-8")),
        "templateLines": len(template.split("\n")),
        "templateSha256": hashlib.sha256(template.encode("utf-8")).hexdigest(),
        "canonicalCssSha256": hashlib.sha256(canonical_css_formatting(template).encode("utf-8")).hexdigest(),
    })
    STYLE_FIXTURE.write_text(json.dumps(fixture, indent=2) + "\n", encoding="utf-8")

    evidence = json.loads(EVIDENCE.read_text(encoding="utf-8"))
    evidence["candidate"].update({"sha256": source_sha, "bytes": source_bytes, "lines": source_lines})
    evidence["rootCause"] = [
        "The Main Toolbar bootstrap observed the complete map and mission-list subtrees even when ordinary Toolkit feature toggles were disabled.",
        "Every qualifying MissionChief or LSSM mutation was selector-classified and could schedule map and Operational Window refresh work.",
        "A fixed 2.5-second ui-integrity task called ensureUi even while the toolbar was healthy.",
        "Operational Window character-data observation and document-wide cleanup had previously amplified the same runtime pressure."
    ]
    evidence["mainToolbarCorrection"] = {
        "observerMode": "direct-control-host-and-body-children-only",
        "healthyIntegrityIntervalMs": 30000,
        "hiddenIntegrityIntervalMs": 120000,
        "missionMutationClassification": "removed-from-toolbar-bootstrap",
        "operationalScanScheduling": "removed-from-toolbar-bootstrap",
        "runtimeDiagnostics": "window.__MCMS_TOOLBAR_DIAGNOSTICS__"
    }
    EVIDENCE.write_text(json.dumps(evidence, indent=2) + "\n", encoding="utf-8")

    baseline = BASELINE.read_text(encoding="utf-8")
    baseline = re.sub(r"(?m)^\*\*Candidate canonical SHA-256:\*\* `[^`]+`\s*$", f"**Candidate canonical SHA-256:** `{source_sha}`  ", baseline)
    baseline = re.sub(r"(?m)^\| Source bytes \| 2,060,765 \| [^|]+ \|.*$", f"| Source bytes | 2,060,765 | {source_bytes:,} | −{2_060_765-source_bytes:,} ({(source_bytes/2_060_765-1)*100:.1f}%) |", baseline)
    baseline = re.sub(r"(?m)^\| Source lines \| 31,761 \| [^|]+ \|.*$", f"| Source lines | 31,761 | {source_lines:,} | −{31_761-source_lines:,} ({(source_lines/31_761-1)*100:.1f}%) |", baseline)
    section = """
## Issue #512 Main Toolbar emergency correction

- Removed steady-state subtree observation of the map and mission-list roots from the Main Toolbar bootstrap.
- The toolbar observer now watches only its direct host children and direct body children for explicit removal or primary map-host replacement.
- Mission/LSSM child mutations can no longer schedule map refreshes or Operational Window scans through the toolbar observer.
- The `ui-integrity` task now runs at 30 seconds, returns immediately while healthy and backs off to 120 seconds while hidden.
- Live counters are exposed at `window.__MCMS_TOOLBAR_DIAGNOSTICS__` for observer callbacks, mutation volume, integrity checks, recoveries and `ensureUi()` calls.

"""
    if "## Issue #512 Main Toolbar emergency correction" not in baseline:
        baseline = baseline.replace("## Retired runtime ownership\n", section + "## Retired runtime ownership\n", 1)
    BASELINE.write_text(baseline, encoding="utf-8")


def update_changelog() -> None:
    text = CHANGELOG.read_text(encoding="utf-8")
    block = """## [Unreleased]

### Critical Main Toolbar performance correction

- Removed the Main Toolbar's broad map and mission-list subtree observer that continued processing MissionChief and LSSM DOM churn after ordinary feature toggles were disabled.
- Stopped toolbar mutations from scheduling mission-map refreshes or Operational Window scans.
- Replaced the fixed 2.5-second toolbar rebuild check with a 30-second health-only fail-safe that performs no rebuild while healthy and backs off while hidden.
- Added live toolbar diagnostic counters and a permanent bounded-bootstrap contract.

"""
    if "### Critical Main Toolbar performance correction" not in text:
        text = replace_once(text, "## [Unreleased]\n\n", block, "changelog unreleased section")
        CHANGELOG.write_text(text, encoding="utf-8")


def main() -> int:
    source = apply_source_fix()
    write_contract()
    update_contract_runners()
    update_v6_budget_contract()
    update_evidence(source)
    update_changelog()
    print(json.dumps({
        "sourceSha256": hashlib.sha256(source.encode("utf-8")).hexdigest(),
        "sourceBytes": len(source.encode("utf-8")),
        "sourceLines": len(source.splitlines()),
    }, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
