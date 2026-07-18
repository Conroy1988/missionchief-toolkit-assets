#!/usr/bin/env python3
from __future__ import annotations

import re
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
SOURCE = ROOT / "src" / "MissionChief_Map_Command_Toolkit.user.js"
RUNTIME_TEST = ROOT / ".github" / "scripts" / "test_mission_requirements_runtime.js"
CHANGELOG = ROOT / "CHANGELOG.md"
VERSION = "4.15.1"
PREVIOUS = "4.15.0"

sys.path.insert(0, str(ROOT / ".github" / "scripts"))
import full_userscript_audit as audit  # noqa: E402


def replace_function(source: str, name: str, replacement: str) -> str:
    masked = audit.mask_non_code(source)
    matches = list(re.finditer(rf"\bfunction\s+{re.escape(name)}\s*\(", masked))
    if len(matches) != 1:
        raise AssertionError(f"Expected one declaration for {name}, found {len(matches)}")
    start = matches[0].start()
    opening = masked.find("{", start)
    closing = audit.matching_brace(masked, opening)
    if opening < 0 or closing is None:
        raise AssertionError(f"Could not extract {name}")
    return source[:start] + replacement.rstrip() + source[closing + 1:]


def replace_once(text: str, old: str, new: str, label: str) -> str:
    count = text.count(old)
    if count != 1:
        raise AssertionError(f"Expected one {label} anchor, found {count}")
    return text.replace(old, new, 1)


def run(*command: str) -> None:
    subprocess.run(command, cwd=ROOT, check=True)


source = SOURCE.read_text(encoding="utf-8")
source = replace_once(source, f"// @version      {PREVIOUS}", f"// @version      {VERSION}", "metadata version")
source = replace_once(source, f"version: '{PREVIOUS}'", f"version: '{VERSION}'", "runtime version")
source = replace_once(source, f"guideVersion: '{PREVIOUS}'", f"guideVersion: '{VERSION}'", "Help Centre version")

replacement = r'''function missionRequirementsLssmActive(candidate, source) {
        // MissionChief and LSSM both use the generic alert-missing-vehicles class.
        // Only explicit LSSM ownership metadata may suppress the Toolkit panel.
        const ownedSelector = [
            '.alert-missing-vehicles[data-raw-html]',
            '[data-lssm-enhanced-missing-vehicles]',
            '[data-lssm-module="extendedCallWindow.enhancedMissingVehicles"]'
        ].join(', ');
        const isLssmOwned = element => {
            if (!element) return false;
            const sharedAlert = Boolean(
                element.matches?.('.alert-missing-vehicles')
                || element.classList?.contains?.('alert-missing-vehicles')
            );
            const rawHtml = element.getAttribute?.('data-raw-html');
            if (sharedAlert && rawHtml !== null && rawHtml !== undefined) return true;
            return Boolean(
                element.matches?.('[data-lssm-enhanced-missing-vehicles]')
                || element.matches?.('[data-lssm-module="extendedCallWindow.enhancedMissingVehicles"]')
            );
        };

        if (isLssmOwned(source)) return true;
        const closestOwned = source?.closest?.(ownedSelector);
        if (isLssmOwned(closestOwned)) return true;
        return isLssmOwned(candidate?.root?.querySelector?.(ownedSelector));
    }'''
source = replace_function(source, "missionRequirementsLssmActive", replacement)
SOURCE.write_text(source, encoding="utf-8")

runtime = RUNTIME_TEST.read_text(encoding="utf-8")
old_getter = r'''    getAttribute(name) {
        if (name === 'id') return this.id || null;
        return this.attributes.has(name) ? this.attributes.get(name) : null;
    }'''
new_getter = r'''    getAttribute(name) {
        if (name === 'data-raw-html' && this._lssmActive) {
            return '<div data-requirement-type="personnel">Missing Personnel</div>';
        }
        if (name === 'id') return this.id || null;
        return this.attributes.has(name) ? this.attributes.get(name) : null;
    }'''
if runtime.count(old_getter) != 1:
    raise AssertionError("FakeElement getAttribute fixture anchor not found exactly once")
runtime = runtime.replace(old_getter, new_getter, 1)

old_test = r'''const lssmSource = {
    matches(selector) { return selector === '.alert-missing-vehicles'; },
    querySelector() { return null; }
};
assert.strictEqual(api.lssmActive({ root: null }, lssmSource), true, 'active LSSM panel is detected');'''
new_test = r'''const nativeMissingSource = {
    matches(selector) { return selector === '.alert-missing-vehicles'; },
    classList: { contains(value) { return value === 'alert-missing-vehicles'; } },
    getAttribute() { return null; },
    closest() { return null; },
    querySelector() { return null; }
};
assert.strictEqual(
    api.lssmActive({ root: null }, nativeMissingSource),
    false,
    'MissionChief native missing alert must not be classified as LSSM'
);
const lssmSource = {
    matches(selector) { return selector === '.alert-missing-vehicles'; },
    classList: { contains(value) { return value === 'alert-missing-vehicles'; } },
    getAttribute(name) { return name === 'data-raw-html' ? '<div data-requirement-type="personnel">Missing Personnel</div>' : null; },
    closest() { return null; },
    querySelector() { return null; }
};
assert.strictEqual(api.lssmActive({ root: null }, lssmSource), true, 'active LSSM panel is detected by explicit ownership metadata');'''
if runtime.count(old_test) != 1:
    raise AssertionError("LSSM runtime fixture anchor not found exactly once")
runtime = runtime.replace(old_test, new_test, 1)
RUNTIME_TEST.write_text(runtime, encoding="utf-8")

changelog = CHANGELOG.read_text(encoding="utf-8")
entry = f'''## [{VERSION}] - 2026-07-18

### Fixed
- Mission Requirements now mounts against MissionChief's native mission window when the game's own missing-vehicle or missing-personnel alert uses the shared `alert-missing-vehicles` class.
- LSSM coexistence detection now requires explicit ownership metadata such as `data-raw-html`; the shared presentation class alone can no longer suppress the Toolkit.

### Compatibility
- The Toolkit remains fully independent of LSSM and continues to use MissionChief's own `#missing_text`, mission form, vehicle lists and en-route table as its data and layout sources.
- Added deterministic coverage for both MissionChief-native alerts and an active LSSM enhanced-missing-vehicles component.

'''
anchor = "## [Unreleased]\n\n"
if changelog.count(anchor) != 1:
    raise AssertionError("CHANGELOG Unreleased anchor missing or duplicated")
CHANGELOG.write_text(changelog.replace(anchor, anchor + entry, 1), encoding="utf-8")

for relative in [
    "help/index.html",
    "help/manifest.json",
    "docs/site-data.json",
    "docs/greasyfork-description.md",
]:
    path = ROOT / relative
    text = path.read_text(encoding="utf-8")
    if PREVIOUS in text:
        path.write_text(text.replace(PREVIOUS, VERSION), encoding="utf-8")

run("node", "--check", str(SOURCE))
run("node", str(RUNTIME_TEST))
run(sys.executable, str(ROOT / ".github" / "scripts" / "test_mission_requirements_contract.py"))
print(f"Issue #139 native-alert hotfix prepared for guarded v{VERSION} validation")
