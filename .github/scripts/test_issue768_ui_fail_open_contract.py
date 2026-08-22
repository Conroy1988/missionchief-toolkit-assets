#!/usr/bin/env python3
"""Static contract for Issue #768 fail-open Toolkit UI recovery."""

from __future__ import annotations

from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
SOURCE = ROOT / "src" / "MissionChief_Map_Command_Toolkit.user.js"


def extract_function(source: str, name: str) -> str:
    marker = f"    function {name}("
    start = source.find(marker)
    assert start >= 0, f"{name} is missing"
    parameter_open = source.find("(", start)
    parameter_depth = 0
    parameter_close = -1
    for index in range(parameter_open, len(source)):
        if source[index] == "(":
            parameter_depth += 1
        elif source[index] == ")":
            parameter_depth -= 1
            if parameter_depth == 0:
                parameter_close = index
                break
    assert parameter_close >= 0, f"{name} parameters did not close"
    opening = source.find("{", parameter_close)
    depth = 0
    quote = ""
    escaped = False
    for index in range(opening, len(source)):
        char = source[index]
        if quote:
            if escaped:
                escaped = False
            elif char == "\\":
                escaped = True
            elif char == quote:
                quote = ""
            continue
        if char in {'"', "'", "`"}:
            quote = char
            continue
        if char == "{":
            depth += 1
        elif char == "}":
            depth -= 1
            if depth == 0:
                return source[start:index + 1]
    raise AssertionError(f"Unable to extract {name}")


def main() -> int:
    source = SOURCE.read_text(encoding="utf-8")
    assert "// @version      10.16.5" in source
    emergency_call = source.find("    ensureToolkitEmergencyLauncher();")
    full_bundle = source.find("    const ALLIANCE_BUILDINGS_PATH_PATTERN")
    assert 0 <= emergency_call < full_bundle, "Emergency UI does not precede the full bundle"
    assert "mcms-toolkit-emergency-launcher" in source
    assert "mcms-toolkit-emergency-style" in source
    assert "animation:mcmsToolkitEmergencyReveal 0s linear 1600ms forwards" in source
    assert "z-index:2147483647" in source

    runtime_start = source.find("    const RUNTIME_KEY =")
    runtime_end = source.find("    function runtimeSetTimeout(", runtime_start)
    runtime = source[runtime_start:runtime_end]
    assert "previousRuntime.phase === 'ready'" in runtime
    assert "previousRuntime.recoverUi({ reason: 'same-version reinjection' })" in runtime
    assert "recoveredControlOwned" in runtime
    assert "if (recovered && recoveredControlOwned)" in runtime and "return;" in runtime
    assert "phase: 'evaluating'" in runtime
    assert "runtime.phase = 'claimed'" in runtime

    create_control = extract_function(source, "createControl")
    assert "mcms-control mcms-pos-bl mcms-control-fallback" in create_control
    assert create_control.index("host.appendChild(control);") < create_control.index("toolkitApplyCommandBarState(control)")
    assert "control.dataset.mcmsLauncherReady = 'true'" in create_control
    assert "runBootIntegration('initial command-bar state'" in create_control
    assert "runBootIntegration('initial launcher render'" in create_control

    ensure_ui = extract_function(source, "ensureUi")
    assert "ensureToolkitEmergencyLauncher();" in ensure_ui
    assert "settings panel recovery" in ensure_ui
    assert "optional map UI state" in ensure_ui
    assert "startup guidance" in ensure_ui
    assert "mcmsLauncherReady === 'true'" in ensure_ui

    recovery = extract_function(source, "recoverToolkitCommandShell")
    assert "options?.emergency === true && state.cleanMode" in recovery
    assert "state.cleanMode = false" in recovery
    assert "recovery stylesheet" in recovery
    assert "recovery root attributes" in recovery
    assert "retireToolkitEmergencyLauncher" in recovery

    tail = source[source.rfind("    // Issue #766:"):]
    assert "runtime.recoverUi = recoverToolkitCommandShell" in tail
    assert "runtime.phase = 'ready'" in tail
    assert tail.index("runtime.recoverUi = recoverToolkitCommandShell") < tail.index("claimToolkitRuntime()") < tail.index("runtime.phase = 'ready'")
    assert "runBootIntegration('replacement instance cleanup'" in tail
    print("Issue #768 UI fail-open contract passed: early recovery, health-aware reinjection, safe launcher mount, guarded integrations and Clean Mode restoration are present.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
