#!/usr/bin/env python3
"""Apply the final mechanically verified userscript audit optimisations."""
from __future__ import annotations

import argparse
from pathlib import Path


def replace_exact(text: str, old: str, new: str, label: str, expected: int = 1) -> tuple[str, str]:
    count = text.count(old)
    if count != expected:
        raise SystemExit(f"{label}: expected {expected} occurrence(s), found {count}")
    return text.replace(old, new), label


def transform(text: str) -> tuple[str, list[str]]:
    changes: list[str] = []

    replacements = [
        (
            "            const compactPattern = normalisedPostcode.replace(/\\s+/g, '\\s*');\n"
            "            try { text = text.replace(new RegExp(`\\b${compactPattern}\\b`, 'iu'), ' '); } catch (err) {}\n",
            "            const compactPattern = normalisedPostcode.replace(/\\s+/g, '\\\\s*');\n"
            "            try { text = text.replace(new RegExp(`\\\\b${compactPattern}\\\\b`, 'iu'), ' '); } catch (err) {}\n",
            "correct postcode regular-expression string escaping",
            1,
        ),
        ("!Boolean(state.missionAgeWatch?.expanded)", "!state.missionAgeWatch?.expanded", "simplify Mission Age Watch expanded toggle", 1),
        ("!Boolean(state.missionAgeWatch?.advancedFiltersOpen)", "!state.missionAgeWatch?.advancedFiltersOpen", "simplify advanced-filter toggle", 1),
        ("!Boolean(state.missionAgeWatch?.hasVehiclesOnWay)", "!state.missionAgeWatch?.hasVehiclesOnWay", "simplify vehicles-on-way toggle", 1),
        ("!Boolean(state.missionAgeWatch?.onlyMyUnits)", "!state.missionAgeWatch?.onlyMyUnits", "simplify my-units toggle", 1),
        (
            "        while (estimatedHeight > availableMapHeight && pinCount && pinColumns < pinCount) {\n",
            "        while (estimatedHeight > availableMapHeight && pinColumns < pinCount) {\n",
            "remove redundant mobile pin-count loop guard",
            1,
        ),
        ("[\\s_:\\-]", "[\\s_:-]", "normalise mission separator character classes", 9),
        (
            "        const renderWhenRelevant = () => {\n",
            "        let renderTimer = null;\n        const renderWhenRelevant = () => {\n",
            "add Alliance Buildings render coalescing state",
            1,
        ),
        (
            "            const pageObserver = runtimeTrackObserver(new MutationObserver(mutations => {\n"
            "                if (!mutations.some(mutation => mutation.addedNodes?.length || mutation.removedNodes?.length)) return;\n"
            "                runtimeSetTimeout(renderWhenRelevant, 0);\n"
            "            }));\n",
            "            const pageObserver = runtimeTrackObserver(new MutationObserver(mutations => {\n"
            "                if (!mutations.some(mutation => mutation.addedNodes?.length || mutation.removedNodes?.length)) return;\n"
            "                runtimeClearTimeout(renderTimer);\n"
            "                renderTimer = runtimeSetTimeout(() => {\n"
            "                    renderTimer = null;\n"
            "                    renderWhenRelevant();\n"
            "                }, 0);\n"
            "            }));\n",
            "coalesce Alliance Buildings observer render requests",
            1,
        ),
        (
            "    let mainMutationObserver = null;\n",
            "    let mainMutationObserver = null;\n    let mainMutationObserverFallbackActive = false;\n",
            "track document-wide mutation-observer fallback state",
            1,
        ),
        (
            "        if (!roots.size) {\n"
            "            mainMutationObserver.observe(document.body, { childList: true, subtree: true });\n"
            "            return;\n"
            "        }\n\n"
            "        for (const root of roots) mainMutationObserver.observe(root, { childList: true, subtree: true });\n",
            "        if (!roots.size) {\n"
            "            mainMutationObserverFallbackActive = true;\n"
            "            mainMutationObserver.observe(document.body, { childList: true, subtree: true });\n"
            "            return;\n"
            "        }\n\n"
            "        mainMutationObserverFallbackActive = false;\n"
            "        for (const root of roots) mainMutationObserver.observe(root, { childList: true, subtree: true });\n",
            "record whether the main observer is using its startup fallback",
            1,
        ),
        (
            "                const controlMissing = Boolean(mapElement && !document.getElementById(SCRIPT.controlId));\n"
            "                if (toolkitUiRemoved || panelMissing || controlMissing) ensureUi();\n",
            "                const controlMissing = Boolean(mapElement && !document.getElementById(SCRIPT.controlId));\n"
            "                if (toolkitUiRemoved || panelMissing || controlMissing) ensureUi();\n"
            "                if (mainMutationObserverFallbackActive && (mapElement || document.querySelector('#missions, #mission_list, .missions-panel, .mission-list'))) {\n"
            "                    connectMainMutationObserver();\n"
            "                }\n",
            "leave the document-wide observer fallback when real roots appear",
            1,
        ),
        (
            "                <span>v4.11.0: Smart Bookmark Labels add compact theme-safe shortcuts, automatic abbreviations, collision protection and manual overrides.</span>",
            "                <span>Audited runtime: compact Smart Bookmark Labels, responsive modes and every interface theme remain fully preserved.</span>",
            "remove stale settings-footer version text",
            1,
        ),
        (
            "        console.debug(`[${SCRIPT.name}] v4.11.1 Performance Bootstrap ready.`);\n",
            "        console.debug(`[${SCRIPT.name}] v${SCRIPT.version} audited runtime ready.`);\n",
            "make the runtime-ready diagnostic version dynamic",
            1,
        ),
    ]

    for old, new, label, expected in replacements:
        text, change = replace_exact(text, old, new, label, expected)
        changes.append(change)

    return text, changes


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("paths", nargs="+", type=Path)
    parser.add_argument("--report", type=Path, required=True)
    args = parser.parse_args()

    reference: str | None = None
    output: list[tuple[Path, str]] = []
    report = ["# Final verified userscript audit optimisations", ""]

    for path in args.paths:
        original = path.read_text(encoding="utf-8")
        updated, changes = transform(original)
        if reference is None:
            reference = updated
        elif reference != updated:
            raise SystemExit(f"{path}: canonical and distribution outputs diverged")
        output.append((path, updated))
        report.extend([
            f"## `{path}`",
            "",
            f"- Bytes: `{len(original.encode('utf-8')):,}` → `{len(updated.encode('utf-8')):,}`",
            f"- Net change: `{len(updated.encode('utf-8')) - len(original.encode('utf-8')):+,}` bytes",
            "",
            *[f"- {change}" for change in changes],
            "",
        ])

    for path, updated in output:
        path.write_text(updated, encoding="utf-8")

    args.report.write_text("\n".join(report) + "\n", encoding="utf-8")
    print(args.report.read_text(encoding="utf-8"))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
