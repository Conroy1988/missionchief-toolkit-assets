#!/usr/bin/env python3
from __future__ import annotations

import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
SOURCE = ROOT / "src" / "MissionChief_Map_Command_Toolkit.user.js"
RUNTIME = ROOT / ".github" / "scripts" / "test_version_status_runtime.js"
CONTRACT = ROOT / ".github" / "scripts" / "test_version_status_contract.py"


def replace_once(text: str, old: str, new: str, label: str) -> str:
    count = text.count(old)
    if count != 1:
        raise AssertionError(f"{label}: expected one exact anchor, found {count}")
    return text.replace(old, new, 1)


def replace_count(text: str, old: str, new: str, expected: int, label: str) -> str:
    count = text.count(old)
    if count != expected:
        raise AssertionError(f"{label}: expected {expected} anchors, found {count}")
    return text.replace(old, new)


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
            if char == "\n": line_comment = False
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
            if escaped: escaped = False
            elif char == "\\": escaped = True
            elif char == quote: quote = ""
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
        if char == "{": depth += 1
        elif char == "}":
            depth -= 1
            if depth == 0:
                return text[:start] + replacement + text[i + 1:]
        i += 1
    raise AssertionError(f"Unable to resolve function boundary: {signature}")


source = SOURCE.read_text(encoding="utf-8")
if "// @version      4.20.5" not in source or "autoIntervalMs: 30 * 60 * 1000" not in source:
    raise AssertionError("Issue #215 refinement requires the validated v4.20.5 implementation")
source = replace_once(
    source,
    "let versionStatusModel = { state: 'idle', manifest: null, checkedAt: 0, error: '' };",
    "let versionStatusModel = { state: 'idle', manifest: null, checkedAt: 0, failedAt: 0, error: '' };",
    "version status model timestamp",
)
source = replace_count(
    source,
    "versionStatusModel = { state: 'error', manifest: null, checkedAt: 0, error: 'cooldown' };",
    "versionStatusModel = { state: 'error', manifest: null, checkedAt: 0, failedAt: Number(failure.failedAt) || now, error: 'cooldown' };",
    2,
    "cooldown model timestamps",
)
source = replace_once(
    source,
    "versionStatusModel = { state: 'error', manifest: null, checkedAt: 0, error: String(err?.message || err || 'failed') };",
    "versionStatusModel = { state: 'error', manifest: null, checkedAt: 0, failedAt, error: String(err?.message || err || 'failed') };",
    "failed request timestamp",
)
next_delay = """    function versionStatusAutomaticDelay(now = Date.now()) {
        const current = Number(now) || Date.now();
        if (versionStatusModel.state === 'error') {
            const failedAt = Number(versionStatusModel.failedAt) || 0;
            if (failedAt > 0) {
                const elapsed = Math.max(0, current - failedAt);
                return Math.max(1000, VERSION_STATUS.failureCooldownMs - Math.min(VERSION_STATUS.failureCooldownMs, elapsed));
            }
            return VERSION_STATUS.failureCooldownMs;
        }
        const checkedAt = Number(versionStatusModel.checkedAt) || 0;
        if (checkedAt > 0 && versionStatusModel.manifest) {
            const elapsed = Math.max(0, current - checkedAt);
            return Math.max(1000, VERSION_STATUS.cacheMs - Math.min(VERSION_STATUS.cacheMs, elapsed));
        }
        return VERSION_STATUS.autoIntervalMs;
    }"""
source = replace_js_function(source, "    function versionStatusAutomaticDelay(now = Date.now())", next_delay)
scheduler = """    function scheduleVersionStatusCheck(delay = VERSION_STATUS.bootDelayMs, force = false) {
        if (runtime.destroyed) return;
        ensureVersionStatusButton();
        if (versionStatusTimer !== null) {
            if (!force && Number(delay) === VERSION_STATUS.bootDelayMs) return;
            runtimeClearTimeout(versionStatusTimer);
        }
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
source = replace_js_function(source, "    function scheduleVersionStatusCheck(delay = VERSION_STATUS.bootDelayMs, force = false)", scheduler)
SOURCE.write_text(source, encoding="utf-8")

runtime = RUNTIME.read_text(encoding="utf-8")
runtime = replace_once(
    runtime,
    "versionStatusModel = { state: 'idle', manifest: null, checkedAt: 0, error: '' };",
    "versionStatusModel = { state: 'idle', manifest: null, checkedAt: 0, failedAt: 0, error: '' };",
    "runtime reset model timestamp",
)
runtime = replace_once(
    runtime,
    "    api.setModel({ state: 'error', manifest: null, checkedAt: 0, error: 'offline' });\n    assert.strictEqual(api.nextDelay(now), 10 * 60 * 1000, 'failed automatic checks retry after the existing cooldown');\n",
    "    api.setModel({ state: 'error', manifest: null, checkedAt: 0, failedAt: now - (9 * 60 * 1000), error: 'offline' });\n    assert.strictEqual(api.nextDelay(now), 60 * 1000, 'automatic failure retry waits only for the remaining cooldown');\n",
    "remaining failure cooldown fixture",
)
RUNTIME.write_text(runtime, encoding="utf-8")

contract = CONTRACT.read_text(encoding="utf-8")
contract = replace_once(
    contract,
    '    assert "document.visibilityState === \'hidden\'" in block\n',
    '    assert "document.visibilityState === \'hidden\'" in block\n    assert "Number(versionStatusModel.failedAt)" in block\n    assert "ensureVersionStatusButton();" in block\n    assert "Number(delay) === VERSION_STATUS.bootDelayMs" in block\n',
    "scheduler lifecycle contract",
)
CONTRACT.write_text(contract, encoding="utf-8")

for distribution in [
    ROOT / "dist" / "MissionChief_Map_Command_Toolkit.user.js",
    ROOT / "dist" / "MissionChief_Map_Command_Toolkit.txt",
]:
    distribution.write_text(SOURCE.read_text(encoding="utf-8"), encoding="utf-8")

subprocess.run(["node", "--check", str(SOURCE.relative_to(ROOT))], cwd=ROOT, check=True)
subprocess.run(["node", str(RUNTIME.relative_to(ROOT))], cwd=ROOT, check=True)
subprocess.run([sys.executable, str(CONTRACT.relative_to(ROOT))], cwd=ROOT, check=True)
subprocess.run([sys.executable, ".github/scripts/validate_userscript.py"], cwd=ROOT, check=True)

Path(__file__).unlink()
print("Refined v4.20.5 scheduler lifecycle with full validation")
