#!/usr/bin/env python3
from __future__ import annotations

from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
SOURCE = ROOT / 'src' / 'MissionChief_Map_Command_Toolkit.user.js'
DIST_USER = ROOT / 'dist' / 'MissionChief_Map_Command_Toolkit.user.js'
DIST_TXT = ROOT / 'dist' / 'MissionChief_Map_Command_Toolkit.txt'
CHANGELOG = ROOT / 'CHANGELOG.md'
REFINER = ROOT / '.github' / 'scripts' / 'refine_full_userscript_audit.py'
RUNTIME_TEST = ROOT / '.github' / 'scripts' / 'test_runtime_optimisations.py'
DOC_CONTRACT = ROOT / '.github' / 'documentation-contract.json'
SITE_DATA = ROOT / 'docs' / 'site-data.json'
AUDIT_DOC = ROOT / 'docs' / 'FULL_PROJECT_AUDIT.md'


def replace_once(text: str, old: str, new: str, label: str) -> str:
    count = text.count(old)
    if count != 1:
        raise RuntimeError(f'{label}: expected exactly one match, found {count}')
    return text.replace(old, new, 1)


def update_source() -> None:
    text = SOURCE.read_text(encoding='utf-8')
    text = replace_once(text, '// @version      4.13.0', '// @version      4.13.1', 'metadata version')
    text = replace_once(text, "version: '4.13.0'", "version: '4.13.1'", 'runtime version')
    text = replace_once(text, "styleId: 'mc-map-command-toolkit-style-v4130'", "styleId: 'mc-map-command-toolkit-style-v4131'", 'style id')
    text = replace_once(text, "guideVersion: '4.13.0'", "guideVersion: '4.13.1'", 'help guide version')
    text = replace_once(
        text,
        "    pageWindow.__MC_MAP_COMMAND_TOOLKIT_V4130__ = true;\n",
        "    pageWindow.__MC_MAP_COMMAND_TOOLKIT_V4130__ = true;\n    pageWindow.__MC_MAP_COMMAND_TOOLKIT_V4131__ = true;\n",
        'runtime sentinel',
    )

    old_prune = """        for (const layer of Array.from(economyHiddenVehicleLayers)) if (!layer || (!layer._map && !getVehicleMarkerLayers().includes(layer))) economyHiddenVehicleLayers.delete(layer);\n        for (const layer of Array.from(economyHiddenBuildingLayers)) if (!layer || (!layer._map && !getBuildingMarkerLayers().includes(layer))) economyHiddenBuildingLayers.delete(layer);"""
    new_prune = """        const currentVehicleLayers = new Set(getVehicleMarkerLayers());\n        const currentBuildingLayers = new Set(getBuildingMarkerLayers());\n        for (const layer of Array.from(economyHiddenVehicleLayers)) {\n            if (!layer || (!layer._map && !currentVehicleLayers.has(layer))) economyHiddenVehicleLayers.delete(layer);\n        }\n        for (const layer of Array.from(economyHiddenBuildingLayers)) {\n            if (!layer || (!layer._map && !currentBuildingLayers.has(layer))) economyHiddenBuildingLayers.delete(layer);\n        }"""
    text = replace_once(text, old_prune, new_prune, 'runtime cache layer pruning')

    old_root = """    function autoLoadAllVehiclesResolveMissionRoot(link) {\n        const selectors = [\n            '#lightbox_box', '#lightbox', '.modal.show', '.modal.in', '[role=\"dialog\"]',\n            '.ui-dialog', '.lightbox_content', '.modal-content', '.ui-dialog-content'\n        ];\n        for (const selector of selectors) {\n            const root = link.closest?.(selector);\n            if (root) return root;\n        }\n        return link.parentElement || document.body;\n    }"""
    new_root = """    function autoLoadAllVehiclesResolveMissionRoot(link) {\n        return link.closest?.(AUTO_LOAD_ALL_VEHICLES_MISSION_ROOT_SELECTOR) || link.parentElement || document.body;\n    }"""
    text = replace_once(text, old_root, new_root, 'auto-load mission root lookup')

    old_candidates = """    function autoLoadAllVehiclesCandidateLinks() {\n        if (!state.autoLoadAllVehicles) return [];\n        return Array.from(document.querySelectorAll(AUTO_LOAD_ALL_VEHICLES_SELECTOR))\n            .reverse()\n            .map(link => ({ link, info: autoLoadAllVehiclesLinkInfo(link) }))\n            .filter(candidate => Boolean(candidate.info));\n    }"""
    new_candidates = """    function autoLoadAllVehiclesCandidateLinks() {\n        if (!state.autoLoadAllVehicles) return [];\n        const queryRoot = autoLoadAllVehiclesMissionRoot?.isConnected && autoLoadAllVehiclesElementVisible(autoLoadAllVehiclesMissionRoot)\n            ? autoLoadAllVehiclesMissionRoot\n            : document;\n        return Array.from(queryRoot.querySelectorAll(AUTO_LOAD_ALL_VEHICLES_SELECTOR))\n            .reverse()\n            .map(link => ({ link, info: autoLoadAllVehiclesLinkInfo(link) }))\n            .filter(candidate => Boolean(candidate.info));\n    }"""
    text = replace_once(text, old_candidates, new_candidates, 'auto-load scoped candidate query')

    SOURCE.write_text(text, encoding='utf-8')
    DIST_USER.write_text(text, encoding='utf-8')
    DIST_TXT.write_text(text, encoding='utf-8')


def update_changelog() -> None:
    text = CHANGELOG.read_text(encoding='utf-8')
    entry = """## [Unreleased]\n\n## [4.13.1] - 2026-07-16\n\n### Performance\n- Reduced Economy Mode cache-pruning work by building current vehicle and building layer sets once per prune pass instead of rescanning full marker collections for every cached layer.\n- Scoped **Auto-load all vehicles** link discovery to the connected, visible mission window after a mission is identified, while preserving the document-wide fallback needed for newly opened missions.\n- Reused the canonical mission-window selector for root resolution instead of rebuilding and iterating a duplicate selector list.\n\n### Audit and documentation\n- Corrected the full-audit lexical-scope analysis so identically named local helper functions in different blocks are no longer reported as same-scope duplicates.\n- Added targeted static invariants for the runtime optimisations.\n- Updated the public theme catalogue to include **007 Intelligence** and **Hyrule Command**, plus the Hyrule payout presentation and automatic vehicle loading capability.\n\n### Compatibility\n- Preserved all saved settings, import/export contracts, public asset URLs, themes, payout templates and Desktop, Tablet and iOS behaviour.\n\n"""
    text = replace_once(text, '## [Unreleased]\n\n', entry, '4.13.1 changelog entry')
    CHANGELOG.write_text(text, encoding='utf-8')


def update_refiner() -> None:
    text = REFINER.read_text(encoding='utf-8')
    old_function = """def lexical_parent(records: list[dict], target: dict) -> tuple[str, int] | None:\n    parents = [\n        item for item in records\n        if item is not target and item[\"body_start\"] <= target[\"start\"] < item[\"body_end\"]\n    ]\n    if not parents:\n        return None\n    parent = min(parents, key=lambda item: item[\"body_end\"] - item[\"body_start\"])\n    return parent[\"name\"], parent[\"line\"]\n"""
    new_function = """def lexical_block_parent(masked_source: str, offset: int) -> tuple[int, int] | None:\n    \"\"\"Return the nearest enclosing brace block while preserving source offsets.\n\n    Function extraction is deliberately conservative and may not inventory every\n    enclosing function expression. A brace-stack parent therefore provides a more\n    reliable same-scope key for local helper names without treating helpers in two\n    separate Promise callbacks as duplicates.\n    \"\"\"\n    stack: list[int] = []\n    for index, character in enumerate(masked_source[:offset]):\n        if character == \"{\":\n            stack.append(index)\n        elif character == \"}\" and stack:\n            stack.pop()\n    if not stack:\n        return None\n    opening = stack[-1]\n    return opening, base.line_number(masked_source, opening)\n"""
    text = replace_once(text, old_function, new_function, 'lexical scope helper')
    text = replace_once(
        text,
        '    source_lines = source_text.splitlines()\n    records = [item for item in raw[\"details\"][\"functionInventory\"] if item[\"name\"] not in RESERVED]\n',
        '    source_lines = source_text.splitlines()\n    masked_source = base.mask_non_code(source_text)\n    records = [item for item in raw[\"details\"][\"functionInventory\"] if item[\"name\"] not in RESERVED]\n',
        'masked source preparation',
    )
    text = replace_once(
        text,
        '        item[\"parent\"] = lexical_parent(records, item)\n',
        '        item[\"parent\"] = lexical_block_parent(masked_source, item[\"start\"])\n',
        'lexical parent assignment',
    )
    text = replace_once(
        text,
        'scope = \"top-level Toolkit scope\" if parent is None else f\"{parent[0]} at line {parent[1]}\"',
        'scope = \"top-level Toolkit scope\" if parent is None else f\"lexical block beginning at line {parent[1]}\"',
        'lexical scope description',
    )
    REFINER.write_text(text, encoding='utf-8')


def add_runtime_test() -> None:
    test_source = '''#!/usr/bin/env python3\n\"\"\"Static invariants for conservative v4.13.1 runtime reductions.\"\"\"\nfrom pathlib import Path\n\nROOT = Path(__file__).resolve().parents[2]\nSOURCE = ROOT / \"src\" / \"MissionChief_Map_Command_Toolkit.user.js\"\n\n\ndef section(text: str, start: str, end: str) -> str:\n    begin = text.index(start)\n    finish = text.index(end, begin)\n    return text[begin:finish]\n\n\ndef main() -> int:\n    text = SOURCE.read_text(encoding=\"utf-8\")\n    prune = section(text, \"function pruneRuntimeCaches\", \"function installAllianceBuildingsPageOptimisation\")\n    assert prune.count(\"getVehicleMarkerLayers()\") == 1\n    assert prune.count(\"getBuildingMarkerLayers()\") == 1\n    assert \"new Set(getVehicleMarkerLayers())\" in prune\n    assert \"new Set(getBuildingMarkerLayers())\" in prune\n    assert \"currentVehicleLayers.has(layer)\" in prune\n    assert \"currentBuildingLayers.has(layer)\" in prune\n\n    auto_load = section(text, \"function autoLoadAllVehiclesResolveMissionRoot\", \"function clearAutoLoadAllVehiclesReleaseTimer\")\n    assert \"closest?.(AUTO_LOAD_ALL_VEHICLES_MISSION_ROOT_SELECTOR)\" in auto_load\n    assert \"autoLoadAllVehiclesMissionRoot?.isConnected\" in auto_load\n    assert \"autoLoadAllVehiclesElementVisible(autoLoadAllVehiclesMissionRoot)\" in auto_load\n    assert \"queryRoot.querySelectorAll(AUTO_LOAD_ALL_VEHICLES_SELECTOR)\" in auto_load\n    assert \"document.querySelectorAll(AUTO_LOAD_ALL_VEHICLES_SELECTOR)\" not in auto_load\n    print(\"Runtime optimisation invariants passed.\")\n    return 0\n\n\nif __name__ == \"__main__\":\n    raise SystemExit(main())\n'''
    RUNTIME_TEST.write_text(test_source, encoding='utf-8')
    namespace = {"__name__": "runtime_optimisation_invariants", "__file__": str(RUNTIME_TEST)}
    exec(compile(test_source, str(RUNTIME_TEST), "exec"), namespace)
    if namespace["main"]() != 0:
        raise RuntimeError("Runtime optimisation invariants failed.")


def update_documentation_catalogue() -> None:
    contract = DOC_CONTRACT.read_text(encoding='utf-8')
    theme_tail = '    "Umbrella",\n    "Factorio"\n'
    if contract.count(theme_tail) != 2:
        raise RuntimeError(f'documentation theme/source tails: expected two matches, found {contract.count(theme_tail)}')
    contract = contract.replace(
        theme_tail,
        '    "Umbrella",\n    "Factorio",\n    "007 Intelligence",\n    "Hyrule Command"\n',
        1,
    )
    contract = replace_once(
        contract,
        '    "Umbrella",\n    "Factorio"\n  ],\n  "installUrls"',
        '    "Umbrella",\n    "Factorio",\n    "007 Intelligence",\n    "Hyrule Command",\n    "Auto-load all vehicles"\n  ],\n  "installUrls"',
        'documentation source token contract',
    )
    DOC_CONTRACT.write_text(contract, encoding='utf-8')

    site = SITE_DATA.read_text(encoding='utf-8')
    fleet_tail = '''        {\n          "name": "Unit Count and Focus controls",\n          "summary": "Reduces map noise while retaining the operational layers that matter.\",\n          "details": [\n            "Unit-count overlays",\n            "Vehicle and building visibility controls",\n            "Focus Mode",\n            "Rapid navigation to active incidents"\n          ],\n          "visual": "focus",\n          "tags": [\n            "vehicles",\n            "map",\n            "focus"\n          ]\n        }\n'''
    fleet_replacement = fleet_tail.rstrip() + ''',\n        {\n          "name": "Auto-load all vehicles",\n          "summary": "Loads MissionChief's hidden vehicle batches automatically when an active mission window is opened.\",\n          "details": [\n            "Uses MissionChief's native load-more control",\n            "Scopes follow-up scans to the active mission window",\n            "Includes bounded retries and duplicate-request protection",\n            "Remains fully manual when disabled"\n          ],\n          "visual": "auto-load-vehicles",\n          "tags": [\n            "vehicles",\n            "missions",\n            "performance"\n          ]\n        }\n'''
    site = replace_once(site, fleet_tail, fleet_replacement, 'auto-load feature catalogue')

    factorio = '''    {\n      "name": "Factorio",\n      "slug": "factorio",\n      "description": "Heavy industrial controls, amber machinery highlights and mechanical status panels.\",\n      "palette": [\n        "#16130f",\n        "#2f2920",\n        "#e79227",\n        "#ffd083",\n        "#91806a"\n      ]\n    }\n'''
    theme_additions = factorio.rstrip() + ''',\n    {\n      "name": "007 Intelligence",\n      "slug": "bond-007",\n      "description": "A classified intelligence interface with gun-barrel geometry, dossier styling and champagne-gold controls.\",\n      "palette": [\n        "#050505",\n        "#161616",\n        "#d5b76d",\n        "#f5e7bb",\n        "#8d1c23"\n      ]\n    },\n    {\n      "name": "Hyrule Command",\n      "slug": "hyrule",\n      "description": "The flagship parchment, royal-gold and ancient-energy command interface with transparent themed artwork.\",\n      "palette": [\n        "#061319",\n        "#203c2b",\n        "#e8bf4d",\n        "#3de7e5",\n        "#50ec8c"\n      ]\n    }\n'''
    site = replace_once(site, factorio, theme_additions, 'theme catalogue additions')
    site = replace_once(
        site,
        '    "Biohazard Containment",\n    "Factorio"\n',
        '    "Biohazard Containment",\n    "Factorio",\n    "007 Intelligence",\n    "Hyrule Quest Reward"\n',
        'payout catalogue additions',
    )
    SITE_DATA.write_text(site, encoding='utf-8')


def update_audit_document() -> None:
    text = AUDIT_DOC.read_text(encoding='utf-8')
    addition = '''\n## Phase 2 — conservative runtime reductions\n\nThe first runtime maintenance candidate is deliberately narrow and semantics-preserving:\n\n- marker-layer collections are materialised once per cache-prune pass and reused as sets;\n- the active mission window becomes the query scope for subsequent Auto-load all vehicles scans, with a document fallback before a mission is identified or after a stale window disappears;\n- the canonical mission-root selector is reused rather than reconstructed per link;\n- targeted static invariants protect those reductions from accidental reversal;\n- lexical block analysis replaces the previous function-inventory parent heuristic, removing the false duplicate warning for independent local Promise settlement helpers.\n\nNo observer, timer, theme, payout template, saved setting or compatibility permission is removed in this phase. The legacy `discordapp.com` connect permission remains because imported settings may still contain legacy Discord webhook hosts.\n'''
    if '## Phase 2 — conservative runtime reductions' not in text:
        text = text.rstrip() + '\n' + addition
    AUDIT_DOC.write_text(text, encoding='utf-8')


def main() -> int:
    update_source()
    update_changelog()
    update_refiner()
    add_runtime_test()
    update_documentation_catalogue()
    update_audit_document()
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
