#!/usr/bin/env python3
from __future__ import annotations

import hashlib
import json
import re
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
SOURCE_PATH = ROOT / "src" / "MissionChief_Map_Command_Toolkit.user.js"
DIST_USER = ROOT / "dist" / "MissionChief_Map_Command_Toolkit.user.js"
DIST_TEXT = ROOT / "dist" / "MissionChief_Map_Command_Toolkit.txt"
MANIFEST_PATH = ROOT / "dist" / "release-manifest.json"
CHECKSUMS_PATH = ROOT / "dist" / "SHA256SUMS.txt"
CHANGELOG_PATH = ROOT / "CHANGELOG.md"
HELP_PATH = ROOT / "help" / "index.html"
FIXTURE_PATH = ROOT / ".github" / "fixtures" / "boot-lifecycle-contract.json"
TEST_PATH = ROOT / ".github" / "scripts" / "test_boot_lifecycle_contract.py"
REPORT_PATH = ROOT / ".github" / "reports" / "issue-64-boot-coordinator-inspection.md"

OLD_VERSION = "4.14.9"
NEW_VERSION = "4.14.10"


def replace_once(text: str, old: str, new: str, label: str) -> str:
    count = text.count(old)
    if count != 1:
        raise AssertionError(f"Expected one {label}, found {count}")
    return text.replace(old, new, 1)


def update_source() -> str:
    source = SOURCE_PATH.read_text(encoding="utf-8")
    if NEW_VERSION in source:
        raise AssertionError(f"Source already contains {NEW_VERSION}")
    if source.count(OLD_VERSION) < 1:
        raise AssertionError(f"Source does not contain current version {OLD_VERSION}")

    boot_marker = "    function boot() {\n"
    boot_index = source.find(boot_marker)
    if boot_index < 0 or source.find(boot_marker, boot_index + 1) >= 0:
        raise AssertionError("Expected exactly one boot() declaration")

    block_start_marker = "        let attempts = 0;\n        const runBootAttempt = () => {\n"
    block_end_marker = "        runtimeSetTimeout(runBootAttempt, 250);\n"
    block_start = source.find(block_start_marker, boot_index)
    block_end_start = source.find(block_end_marker, block_start)
    if block_start < 0 or block_end_start < 0:
        raise AssertionError("Existing nested boot-attempt coordinator was not found")
    block_end = block_end_start + len(block_end_marker)
    coordinator_body = source[block_start:block_end]

    required_fragments = [
        "attempts += 1;",
        "const ready = ensureUi();",
        "const mapReady = Boolean(getLargestLeafletMap());",
        "attempts >= 12",
        "attempts >= 90 || runtime.destroyed",
        "attempts < 12 ? 350 : attempts < 30 ? 700 : 1400",
        "scheduleDeferredOperationalStartup();",
        "STARTUP_OBSERVER_DELAY_MS",
    ]
    missing = [fragment for fragment in required_fragments if fragment not in coordinator_body]
    if missing:
        raise AssertionError(f"Boot coordinator fragments missing before extraction: {missing}")
    if coordinator_body.count("runtimeSetTimeout(runBootAttempt") != 2:
        raise AssertionError("Boot coordinator timer ownership changed before extraction")

    helper = (
        "    function startBootAttemptCoordinator(bootPerformanceStartedAt) {\n"
        f"{coordinator_body}"
        "    }\n\n"
    )
    source = source[:boot_index] + helper + source[boot_index:]
    shifted_boot_index = boot_index + len(helper)
    shifted_block_start = source.find(block_start_marker, shifted_boot_index)
    shifted_block_end_start = source.find(block_end_marker, shifted_block_start)
    if shifted_block_start < 0 or shifted_block_end_start < 0:
        raise AssertionError("Unable to locate coordinator block after helper insertion")
    shifted_block_end = shifted_block_end_start + len(block_end_marker)
    source = (
        source[:shifted_block_start]
        + "        startBootAttemptCoordinator(bootPerformanceStartedAt);\n"
        + source[shifted_block_end:]
    )

    if source.count("function startBootAttemptCoordinator(") != 1:
        raise AssertionError("Coordinator helper declaration is not unique")
    boot_after = source[source.find(boot_marker):]
    if boot_after.count("startBootAttemptCoordinator(bootPerformanceStartedAt);") != 1:
        raise AssertionError("boot() does not delegate exactly once to the coordinator")
    if "const runBootAttempt = () =>" in boot_after[: boot_after.find("    function scheduleBoot()")]:
        raise AssertionError("Nested runBootAttempt remained inside boot()")

    source = source.replace(OLD_VERSION, NEW_VERSION)
    SOURCE_PATH.write_text(source, encoding="utf-8")
    return source


def update_fixture() -> None:
    fixture = json.loads(FIXTURE_PATH.read_text(encoding="utf-8"))
    boot = fixture.setdefault("boot", {})
    boot["coordinatorFunction"] = "startBootAttemptCoordinator"
    FIXTURE_PATH.write_text(json.dumps(fixture, indent=2) + "\n", encoding="utf-8")


def update_test() -> None:
    text = TEST_PATH.read_text(encoding="utf-8")
    text = replace_once(
        text,
        '    "runtimeRunWhenIdle",\n    "boot",',
        '    "runtimeRunWhenIdle",\n    "startBootAttemptCoordinator",\n    "boot",',
        "boot coordinator function-list insertion",
    )
    text = replace_once(
        text,
        '    assert fixtures["runtimeKey"] in runtime_block\n    assert fixtures["replacementReason"] in runtime_block\n',
        '    assert fixtures["runtimeKey"] in runtime_block\n    assert fixtures["replacementReason"] in runtime_block\n    coordinator_name = fixtures["boot"]["coordinatorFunction"]\n    assert coordinator_name == "startBootAttemptCoordinator"\n    assert "startBootAttemptCoordinator(bootPerformanceStartedAt);" in functions["boot"]\n    assert "const runBootAttempt = () =>" not in functions["boot"]\n    assert "const runBootAttempt = () =>" in functions[coordinator_name]\n',
        "static coordinator ownership assertions",
    )
    text = replace_once(
        text,
        '    target.boot = compileInSandbox(__BOOT_SOURCE__, sandbox);\n',
        '    target.startBootAttemptCoordinator = compileInSandbox(__BOOT_COORDINATOR_SOURCE__, sandbox);\n    target.boot = compileInSandbox(__BOOT_SOURCE__, sandbox);\n',
        "sandbox coordinator compilation",
    )
    text = replace_once(
        text,
        'function callCount(env, name) { return env.calls.filter(call => call.name === name).length; }\n\nfunction testBootLifecycle() {\n',
        '''function callCount(env, name) { return env.calls.filter(call => call.name === name).length; }\n\nfunction testBootAttemptCoordinatorDirectly() {\n    const direct = createBootEnvironment({ mapReadyAfter: 2 });\n    direct.startBootAttemptCoordinator(100);\n    for (let attempt = 0; attempt < 3; attempt += 1) direct.runNamedTimer("runBootAttempt");\n    assert.equal(direct.getMapCalls(), 3);\n    assert.deepEqual(direct.bootTimerDelays, [\n        fixtures.boot.initialDelayMs,\n        fixtures.boot.earlyRetryDelayMs,\n        fixtures.boot.earlyRetryDelayMs\n    ]);\n    assert.equal(callCount(direct, "scheduleDeferredOperationalStartup"), 1);\n    const metric = direct.calls.find(call => call.name === "recordStartupMetric");\n    assert.equal(metric.args[2].bootAttempts, 3);\n}\n\nfunction testBootLifecycle() {\n''',
        "direct coordinator fixture",
    )
    text = replace_once(
        text,
        'testRuntimeHelpers();\ntestBootLifecycle();\n',
        'testRuntimeHelpers();\ntestBootAttemptCoordinatorDirectly();\ntestBootLifecycle();\n',
        "direct coordinator invocation",
    )
    text = replace_once(
        text,
        '    replacements["__BOOT_SOURCE__"] = json.dumps(functions["boot"])\n',
        '    replacements["__BOOT_COORDINATOR_SOURCE__"] = json.dumps(functions["startBootAttemptCoordinator"])\n    replacements["__BOOT_SOURCE__"] = json.dumps(functions["boot"])\n',
        "coordinator source replacement",
    )
    text = replace_once(
        text,
        'console.log("Boot lifecycle contract passed: runtime ownership, document-start, delayed map, hidden-tab resume, retry cancellation and teardown.");',
        'console.log("Boot lifecycle contract passed: extracted boot coordinator, runtime ownership, document-start, delayed map, hidden-tab resume, retry cancellation and teardown.");',
        "contract success message",
    )
    TEST_PATH.write_text(text, encoding="utf-8")


def update_release_files(source: str) -> None:
    DIST_USER.write_text(source, encoding="utf-8")
    DIST_TEXT.write_text(source, encoding="utf-8")
    payload = source.encode("utf-8")
    digest = hashlib.sha256(payload).hexdigest()

    manifest = json.loads(MANIFEST_PATH.read_text(encoding="utf-8"))
    manifest["version"] = NEW_VERSION
    manifest["sha256"] = digest
    manifest["bytes"] = len(payload)
    manifest["lines"] = source.count("\n") + 1
    manifest.setdefault("metadata", {})["runtimeVersion"] = NEW_VERSION
    MANIFEST_PATH.write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")
    CHECKSUMS_PATH.write_text(
        f"{digest}  MissionChief_Map_Command_Toolkit.user.js\n"
        f"{digest}  MissionChief_Map_Command_Toolkit.txt\n",
        encoding="utf-8",
    )

    help_text = HELP_PATH.read_text(encoding="utf-8")
    help_text = replace_once(
        help_text,
        f"Guide for Toolkit v{OLD_VERSION}",
        f"Guide for Toolkit v{NEW_VERSION}",
        "Help Centre version",
    )
    HELP_PATH.write_text(help_text, encoding="utf-8")

    changelog = CHANGELOG_PATH.read_text(encoding="utf-8")
    marker = "## [Unreleased]\n"
    entry = f'''\n## [{NEW_VERSION}] - 2026-07-17\n\n### Changed\n- Extracted the bounded core-UI boot-attempt loop from `boot()` into the independently testable `startBootAttemptCoordinator()` lifecycle stage.\n- `boot()` now delegates once to the coordinator while retaining runtime ownership, listeners, scheduled tasks, mutation observation and teardown registration.\n\n### Compatibility\n- Initial delay, retry thresholds, 350/700/1400 ms backoff, 12-attempt map fallback, 90-attempt hard stop and destroyed-runtime cancellation are unchanged.\n- No observer, timer, listener, task, theme, setting or public asset behaviour changed.\n- Extended the fixture-backed Boot/Lifecycle contract to compile and test the extracted coordinator directly and through `boot()`.\n'''
    if f"## [{NEW_VERSION}]" in changelog:
        raise AssertionError("Changelog already contains the target version")
    changelog = replace_once(changelog, marker, marker + entry, "Unreleased changelog marker")
    CHANGELOG_PATH.write_text(changelog, encoding="utf-8")


def validate() -> None:
    subprocess.run(["python3", str(TEST_PATH)], cwd=ROOT, check=True)
    subprocess.run(["python3", ".github/scripts/validate_userscript.py"], cwd=ROOT, check=True)
    subprocess.run(["node", "--check", str(SOURCE_PATH)], cwd=ROOT, check=True)
    subprocess.run(["cmp", "--silent", str(DIST_USER), str(DIST_TEXT)], cwd=ROOT, check=True)


def main() -> int:
    source = update_source()
    update_fixture()
    update_test()
    update_release_files(source)
    REPORT_PATH.unlink(missing_ok=True)
    validate()
    print(f"Extracted boot-attempt coordinator and prepared Toolkit {NEW_VERSION}.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
