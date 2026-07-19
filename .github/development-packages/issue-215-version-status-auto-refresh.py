#!/usr/bin/env python3
from __future__ import annotations

import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
SOURCE = ROOT / "src" / "MissionChief_Map_Command_Toolkit.user.js"
RUNTIME = ROOT / ".github" / "scripts" / "test_version_status_runtime.js"
CONTRACT = ROOT / ".github" / "scripts" / "test_version_status_contract.py"
CHANGELOG = ROOT / "CHANGELOG.md"


def replace_once(text: str, old: str, new: str, label: str) -> str:
    count = text.count(old)
    if count != 1:
        raise AssertionError(f"{label}: expected one exact anchor, found {count}")
    return text.replace(old, new, 1)


def replace_js_function(text: str, signature: str, replacement: str) -> str:
    start = text.index(signature)
    brace = text.index("{", start)
    depth = 0
    quote = ""
    escaped = False
    line_comment = False
    block_comment = False
    i = brace
    while i < len(text):
        char = text[i]
        nxt = text[i + 1] if i + 1 < len(text) else ""
        if line_comment:
            if char == "\n":
                line_comment = False
            i += 1
            continue
        if block_comment:
            if char == "*" and nxt == "/":
                block_comment = False
                i += 2
                continue
            i += 1
            continue
        if quote:
            if escaped:
                escaped = False
            elif char == "\\":
                escaped = True
            elif char == quote:
                quote = ""
            i += 1
            continue
        if char in ("'", '"', "`"):
            quote = char
            i += 1
            continue
        if char == "/" and nxt == "/":
            line_comment = True
            i += 2
            continue
        if char == "/" and nxt == "*":
            block_comment = True
            i += 2
            continue
        if char == "{":
            depth += 1
        elif char == "}":
            depth -= 1
            if depth == 0:
                return text[:start] + replacement + text[i + 1 :]
        i += 1
    raise AssertionError(f"Unable to resolve function boundary: {signature}")


source = SOURCE.read_text(encoding="utf-8")
if "// @version      4.20.4" not in source or "version: '4.20.4'" not in source:
    raise AssertionError("Issue #215 package requires the verified v4.20.4 source")
source = replace_once(source, "// @version      4.20.4", "// @version      4.20.5", "userscript metadata version")
source = replace_once(source, "version: '4.20.4'", "version: '4.20.5'", "runtime version")
source = replace_once(
    source,
    "        cacheMs: 30 * 60 * 1000,\n",
    "        cacheMs: 30 * 60 * 1000,\n        autoIntervalMs: 30 * 60 * 1000,\n",
    "automatic interval constant",
)
old_signature = "    function scheduleVersionStatusCheck(delay = VERSION_STATUS.bootDelayMs, force = false)"
new_scheduler = """    function versionStatusAutomaticDelay(now = Date.now()) {
        if (versionStatusModel.state === 'error') return VERSION_STATUS.failureCooldownMs;
        const checkedAt = Number(versionStatusModel.checkedAt) || 0;
        if (checkedAt > 0 && versionStatusModel.manifest) {
            const elapsed = Math.max(0, Number(now) - checkedAt);
            return Math.max(1000, VERSION_STATUS.cacheMs - Math.min(VERSION_STATUS.cacheMs, elapsed));
        }
        return VERSION_STATUS.autoIntervalMs;
    }
    function scheduleVersionStatusCheck(delay = VERSION_STATUS.bootDelayMs, force = false) {
        runtimeClearTimeout(versionStatusTimer);
        versionStatusTimer = runtimeSetTimeout(async () => {
            versionStatusTimer = null;
            if (runtime.destroyed) return;
            if (!force && document.visibilityState === 'hidden') return;
            try {
                await runVersionStatusCheck(force);
            } finally {
                if (!runtime.destroyed && document.visibilityState !== 'hidden') {
                    scheduleVersionStatusCheck(versionStatusAutomaticDelay(), false);
                }
            }
        }, Math.max(0, Number(delay) || 0));
    }"""
source = replace_js_function(source, old_signature, new_scheduler)
SOURCE.write_text(source, encoding="utf-8")

runtime = RUNTIME.read_text(encoding="utf-8")
runtime = replace_once(
    runtime,
    "model: () => versionStatusModel, reset: () =>",
    "model: () => versionStatusModel, nextDelay: versionStatusAutomaticDelay, schedule: scheduleVersionStatusCheck, setModel: value => { versionStatusModel = { ...versionStatusModel, ...value }; }, reset: () =>",
    "runtime API exports",
)
runtime = replace_once(
    runtime,
    "    assert.strictEqual(api.failureCooling({ failedAt: now - (10 * 60 * 1000) }, now), false, '10-minute failure cooldown expires');\n",
    "    assert.strictEqual(api.failureCooling({ failedAt: now - (10 * 60 * 1000) }, now), false, '10-minute failure cooldown expires');\n"
    "    assert.strictEqual(api.constants.autoIntervalMs, 30 * 60 * 1000, 'automatic active-tab cadence is 30 minutes');\n"
    "    api.setModel({ state: 'latest', manifest: current, checkedAt: now - (29 * 60 * 1000), error: '' });\n"
    "    assert.strictEqual(api.nextDelay(now), 60 * 1000, 'automatic scheduler waits only for the remaining successful-cache lifetime');\n"
    "    api.setModel({ state: 'error', manifest: null, checkedAt: 0, error: 'offline' });\n"
    "    assert.strictEqual(api.nextDelay(now), 10 * 60 * 1000, 'failed automatic checks retry after the existing cooldown');\n"
    "    const scheduledTimers = [];\n"
    "    const originalRuntimeSetTimeout = context.runtimeSetTimeout;\n"
    "    const originalRuntimeClearTimeout = context.runtimeClearTimeout;\n"
    "    context.runtimeSetTimeout = (callback, delay) => { scheduledTimers.push({ callback, delay }); return scheduledTimers.length; };\n"
    "    context.runtimeClearTimeout = () => {};\n"
    "    document.visibilityState = 'hidden';\n"
    "    api.reset(); api.schedule(1234, false);\n"
    "    assert.strictEqual(scheduledTimers[0].delay, 1234, 'automatic scheduler honours the requested delay');\n"
    "    await scheduledTimers[0].callback();\n"
    "    assert.strictEqual(scheduledTimers.length, 1, 'hidden tabs defer without creating a background polling timer');\n"
    "    document.visibilityState = 'visible';\n"
    "    context.runtimeSetTimeout = originalRuntimeSetTimeout;\n"
    "    context.runtimeClearTimeout = originalRuntimeClearTimeout;\n",
    "automatic scheduler runtime fixtures",
)
RUNTIME.write_text(runtime, encoding="utf-8")

contract = CONTRACT.read_text(encoding="utf-8")
contract = replace_once(
    contract,
    '    assert "cacheMs: 30 * 60 * 1000" in block\n',
    '    assert "cacheMs: 30 * 60 * 1000" in block\n    assert "autoIntervalMs: 30 * 60 * 1000" in block\n',
    "automatic cadence contract",
)
contract = replace_once(
    contract,
    '    assert "setInterval(" not in block, "version checker must not poll continuously"\n',
    '    assert "setInterval(" not in block, "version checker must use a non-overlapping recursive timeout"\n    assert "scheduleVersionStatusCheck(versionStatusAutomaticDelay(), false)" in block\n    assert "document.visibilityState === \'hidden\'" in block\n',
    "recursive scheduler contract",
)
contract = replace_once(
    contract,
    '        "function scheduleVersionStatusCheck(delay = VERSION_STATUS.bootDelayMs, force = false)",\n',
    '        "function versionStatusAutomaticDelay(now = Date.now())",\n        "function scheduleVersionStatusCheck(delay = VERSION_STATUS.bootDelayMs, force = false)",\n',
    "scheduler marker contract",
)
CONTRACT.write_text(contract, encoding="utf-8")

changelog = CHANGELOG.read_text(encoding="utf-8")
entry = """## [4.20.5] - 2026-07-19

### Changed
- Added a lightweight automatic version check every 30 minutes while MissionChief remains visible, using a single recursive timeout rather than continuous polling.
- Deferred scheduled checks while the tab is hidden and retained the existing visibility-based stale refresh when play resumes.
- Based the next automatic timeout on the remaining successful-cache lifetime, preventing a manual force-check from causing a redundant network ping.
- Retained the 10-minute automatic retry cooldown after network or manifest failures.

### Validation
- Added deterministic scheduler fixtures for the 30-minute cadence, remaining-cache calculation, failure cooldown and hidden-tab deferral.

"""
changelog = replace_once(changelog, "## [Unreleased]\n\n", "## [Unreleased]\n\n" + entry, "v4.20.5 changelog")
CHANGELOG.write_text(changelog, encoding="utf-8")

for distribution in [
    ROOT / "dist" / "MissionChief_Map_Command_Toolkit.user.js",
    ROOT / "dist" / "MissionChief_Map_Command_Toolkit.txt",
]:
    distribution.write_text(SOURCE.read_text(encoding="utf-8"), encoding="utf-8")

subprocess.run(["node", "--check", str(SOURCE.relative_to(ROOT))], cwd=ROOT, check=True)
subprocess.run(["node", str(RUNTIME.relative_to(ROOT))], cwd=ROOT, check=True)
subprocess.run([sys.executable, str(CONTRACT.relative_to(ROOT))], cwd=ROOT, check=True)
subprocess.run([sys.executable, ".github/scripts/validate_userscript.py"], cwd=ROOT, check=True)

if SOURCE.stat().st_size > 3_000_000:
    raise AssertionError("v4.20.5 exceeds the owner-authorized 3,000,000-byte source ceiling")
if len(SOURCE.read_text(encoding="utf-8").splitlines()) > 32_000:
    raise AssertionError("v4.20.5 exceeds the 32,000-line source ceiling")

Path(__file__).unlink()
print("Prepared v4.20.5 automatic version scheduler with full validation")
