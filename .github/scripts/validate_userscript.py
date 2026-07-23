#!/usr/bin/env python3

from __future__ import annotations

import hashlib
import json
import os
import re
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
os.environ["PYTHONDONTWRITEBYTECODE"] = "1"
sys.dont_write_bytecode = True
SOURCE = ROOT / "src" / "MissionChief_Map_Command_Toolkit.user.js"
BASELINE = ROOT / "status" / "source-baseline.json"
CHANGELOG = ROOT / "CHANGELOG.md"
DIST = ROOT / "dist"
USER_JS = DIST / "MissionChief_Map_Command_Toolkit.user.js"
TXT = DIST / "MissionChief_Map_Command_Toolkit.txt"
SUMS = DIST / "SHA256SUMS.txt"
MANIFEST = DIST / "release-manifest.json"
INTEGRITY_AUDITOR = ROOT / ".github" / "scripts" / "check_code_integrity.py"
INTEGRITY_POLICY = ROOT / ".github" / "code-integrity-policy.json"
ASSET_AUDITOR = ROOT / ".github" / "scripts" / "check_asset_health.py"
AUDIO_ALIAS_AUDITOR = ROOT / ".github" / "scripts" / "check_audio_alias_contract.py"
ISSUE391_MATRIX_RETIREMENT_CONTRACT = ROOT / ".github" / "scripts" / "test_issue391_matrix_retirement.py"
VERSION_STATUS_CONTRACT = ROOT / ".github" / "scripts" / "test_version_status_contract.py"
FINANCIAL_OVERVIEW_CONTRACT = ROOT / ".github" / "scripts" / "test_financial_overview_contract.py"
MAIN_STYLE_HEADROOM_CONTRACT = ROOT / ".github" / "scripts" / "test_main_style_source_headroom.py"
ISSUE378_REQUIREMENTS_RENDERER_CONTRACT = ROOT / ".github" / "scripts" / "test_issue378_requirements_renderer.py"
ISSUE378_OPERATIONAL_FEATURE_CONTRACT = ROOT / ".github" / "scripts" / "test_issue378_operational_feature_suite.py"
ISSUE378_OPERATIONAL_FEATURE_RUNTIME = ROOT / ".github" / "scripts" / "test_issue378_operational_feature_runtime.js"
ISSUE447_MENU_BOOT_CONTRACT = ROOT / ".github" / "scripts" / "test_issue447_menu_boot_fail_open.py"
ISSUE450_CORE_BOOTSTRAP_CONTRACT = ROOT / ".github" / "scripts" / "test_issue450_core_launcher_bootstrap.py"
ISSUE454_PREBOOT_STATE_CONTRACT = ROOT / ".github" / "scripts" / "test_issue454_preboot_state_order.py"
ISSUE456_REQUIREMENTS_TRUTH_RUNTIME = ROOT / ".github" / "scripts" / "test_issue456_requirements_truth_runtime.js"
ISSUE458_REQUIREMENTS_SOURCE_RUNTIME = ROOT / ".github" / "scripts" / "test_issue458_requirements_source_runtime.js"
ISSUE464_LAUNCHER_SETTINGS_CONTRACT = ROOT / ".github" / "scripts" / "test_issue464_launcher_settings_contract.py"
ISSUE464_OPERATIONAL_RUNTIME = ROOT / ".github" / "scripts" / "test_issue464_operational_runtime.js"

REQUIRED_KEYS = {"name", "version"}
VERSION_RE = re.compile(r"^[0-9]+\.[0-9]+\.[0-9]+(?:[-+][0-9A-Za-z.-]+)?$")
CONFLICT_RE = re.compile(r"^(?:<<<<<<< .+|=======|>>>>>>> .+)$", re.MULTILINE)
RELEASE_TAG_RE = re.compile(r"^v[0-9]+\.[0-9]+\.[0-9]+(?:[-+][0-9A-Za-z.-]+)?$")
SCRIPT_VERSION_RE = re.compile(
    r"\bconst\s+SCRIPT\s*=\s*\{\s*"
    r"name\s*:\s*['\"][^'\"]+['\"]\s*,\s*"
    r"version\s*:\s*['\"]([^'\"]+)['\"]",
    re.DOTALL,
)


def fail(message: str) -> None:
    raise SystemExit(f"VALIDATION ERROR: {message}")


def cleanup_repository_bytecode() -> None:
    for cache_dir in sorted(ROOT.rglob("__pycache__"), reverse=True):
        if ".git" in cache_dir.parts:
            continue
        shutil.rmtree(cache_dir, ignore_errors=True)
    for suffix in ("*.pyc", "*.pyo"):
        for bytecode in ROOT.rglob(suffix):
            if ".git" not in bytecode.parts:
                bytecode.unlink(missing_ok=True)


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def metadata(text: str) -> dict[str, list[str]]:
    start = text.find("// ==UserScript==")
    end = text.find("// ==/UserScript==")
    if start < 0 or end < 0 or end <= start:
        fail("userscript metadata block is missing or malformed")

    result: dict[str, list[str]] = {}
    for line in text[start:end].splitlines():
        match = re.match(r"^//\s*@([A-Za-z0-9:_-]+)\s+(.+?)\s*$", line)
        if match:
            result.setdefault(match.group(1).lower(), []).append(match.group(2))
    return result


def one(meta: dict[str, list[str]], key: str) -> str:
    values = meta.get(key, [])
    if len(values) != 1:
        fail(f"metadata @{key} must appear exactly once")
    return values[0]


def optional_one(meta: dict[str, list[str]], key: str) -> str | None:
    values = meta.get(key, [])
    if len(values) > 1:
        fail(f"metadata @{key} must not appear more than once")
    return values[0] if values else None


def changelog_has_version(version: str) -> bool:
    if not CHANGELOG.exists():
        return False
    text = CHANGELOG.read_text(encoding="utf-8")
    return re.search(
        rf"^## \[{re.escape(version)}\](?:\s+-\s+\d{{4}}-\d{{2}}-\d{{2}})?\s*$",
        text,
        re.M,
    ) is not None


def is_missionchief_rule(value: str) -> bool:
    return "missionchief.co.uk" in value.casefold()


def internal_script_version(text: str) -> str:
    versions = SCRIPT_VERSION_RE.findall(text)
    if len(versions) != 1:
        fail("internal SCRIPT.version must appear exactly once")
    return versions[0]


def latest_release_baseline(output: Path) -> str | None:
    source_path = SOURCE.relative_to(ROOT).as_posix()
    try:
        tags = subprocess.run(
            ["git", "tag", "--merged", "HEAD", "--sort=-version:refname"],
            cwd=ROOT,
            check=True,
            capture_output=True,
            text=True,
        ).stdout.splitlines()
    except (OSError, subprocess.CalledProcessError):
        return None

    for tag in tags:
        if not RELEASE_TAG_RE.fullmatch(tag.strip()):
            continue
        object_name = f"{tag}:{source_path}"
        exists = subprocess.run(
            ["git", "cat-file", "-e", object_name],
            cwd=ROOT,
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
        )
        if exists.returncode != 0:
            continue
        try:
            payload = subprocess.run(
                ["git", "show", object_name],
                cwd=ROOT,
                check=True,
                capture_output=True,
            ).stdout
        except (OSError, subprocess.CalledProcessError):
            continue
        output.write_bytes(payload)
        return tag
    return None


def run_integrity_gate() -> None:
    required = [INTEGRITY_AUDITOR, INTEGRITY_POLICY, ASSET_AUDITOR, AUDIO_ALIAS_AUDITOR, ISSUE391_MATRIX_RETIREMENT_CONTRACT, VERSION_STATUS_CONTRACT, FINANCIAL_OVERVIEW_CONTRACT, MAIN_STYLE_HEADROOM_CONTRACT, ISSUE378_REQUIREMENTS_RENDERER_CONTRACT, ISSUE378_OPERATIONAL_FEATURE_CONTRACT, ISSUE378_OPERATIONAL_FEATURE_RUNTIME, ISSUE456_REQUIREMENTS_TRUTH_RUNTIME, ISSUE458_REQUIREMENTS_SOURCE_RUNTIME, ISSUE464_LAUNCHER_SETTINGS_CONTRACT, ISSUE464_OPERATIONAL_RUNTIME]
    missing = [path.relative_to(ROOT) for path in required if not path.exists()]
    if missing:
        fail(
            "integrity tooling is incomplete: "
            + ", ".join(str(path) for path in missing)
        )

    with tempfile.TemporaryDirectory(prefix="mcms-integrity-") as temp:
        baseline_path = Path(temp) / "release-baseline.user.js"
        baseline_ref = latest_release_baseline(baseline_path)
        integrity_json = Path(temp) / "code-integrity-report.json"
        integrity_markdown = Path(temp) / "code-integrity-report.md"
        asset_json = Path(temp) / "asset-health-report.json"
        asset_markdown = Path(temp) / "asset-health-report.md"

        command = [
            sys.executable,
            str(INTEGRITY_AUDITOR),
            "--candidate",
            str(SOURCE),
            "--policy",
            str(INTEGRITY_POLICY),
            "--json-output",
            str(integrity_json),
            "--markdown-output",
            str(integrity_markdown),
        ]
        if baseline_ref and baseline_path.exists():
            command.extend(["--base", str(baseline_path)])
            print(f"Code-integrity release baseline: {baseline_ref}")
        else:
            print(
                "Code-integrity release baseline unavailable; "
                "current-state checks will still run."
            )

        integrity = subprocess.run(command, cwd=ROOT)
        if integrity.returncode != 0:
            if integrity_markdown.exists():
                print(integrity_markdown.read_text(encoding="utf-8"))
            fail("expanded code-integrity audit failed")

        assets = subprocess.run(
            [
                sys.executable,
                str(ASSET_AUDITOR),
                "--mode",
                "static",
                "--json-output",
                str(asset_json),
                "--markdown-output",
                str(asset_markdown),
            ],
            cwd=ROOT,
        )
        if assets.returncode != 0:
            if asset_markdown.exists():
                print(asset_markdown.read_text(encoding="utf-8"))
            fail("static public-asset integrity audit failed")

        audio_aliases = subprocess.run(
            [sys.executable, str(AUDIO_ALIAS_AUDITOR)],
            cwd=ROOT,
        )
        if audio_aliases.returncode != 0:
            fail("audio compatibility alias contract failed")

        matrix_retirement = subprocess.run(
            [sys.executable, str(ISSUE391_MATRIX_RETIREMENT_CONTRACT)],
            cwd=ROOT,
        )
        if matrix_retirement.returncode != 0:
            fail("Issue #391 Matrix retirement contract failed")

        version_status = subprocess.run(
            [sys.executable, str(VERSION_STATUS_CONTRACT)],
            cwd=ROOT,
        )
        if version_status.returncode != 0:
            fail("live version-status contract failed")

        financial_overview = subprocess.run(
            [sys.executable, str(FINANCIAL_OVERVIEW_CONTRACT)],
            cwd=ROOT,
        )
        if financial_overview.returncode != 0:
            fail("financial overview reconciliation contract failed")

        main_style_headroom = subprocess.run(
            [sys.executable, str(MAIN_STYLE_HEADROOM_CONTRACT)],
            cwd=ROOT,
        )
        if main_style_headroom.returncode != 0:
            fail("main-style source-headroom contract failed")

        issue378_renderer = subprocess.run(
            [sys.executable, str(ISSUE378_REQUIREMENTS_RENDERER_CONTRACT)],
            cwd=ROOT,
        )
        if issue378_renderer.returncode != 0:
            fail("Issue #378 requirements renderer contract failed")

        issue378_feature = subprocess.run(
            [sys.executable, str(ISSUE378_OPERATIONAL_FEATURE_CONTRACT)],
            cwd=ROOT,
        )
        if issue378_feature.returncode != 0:
            fail("Issue #378 operational feature-suite contract failed")

        issue378_feature_runtime = subprocess.run(
            ["node", str(ISSUE378_OPERATIONAL_FEATURE_RUNTIME)],
            cwd=ROOT,
        )
        if issue378_feature_runtime.returncode != 0:
            fail("Issue #378 operational feature runtime fixtures failed")

        issue447_menu_boot = subprocess.run(
            [sys.executable, str(ISSUE447_MENU_BOOT_CONTRACT)],
            cwd=ROOT,
        )
        if issue447_menu_boot.returncode != 0:
            fail("Issue #447 menu boot fail-open contract failed")

        issue450_core_bootstrap = subprocess.run(
            [sys.executable, str(ISSUE450_CORE_BOOTSTRAP_CONTRACT)],
            cwd=ROOT,
        )
        if issue450_core_bootstrap.returncode != 0:
            fail("Issue #450 core launcher bootstrap contract failed")

        issue454_preboot_state = subprocess.run(
            [sys.executable, str(ISSUE454_PREBOOT_STATE_CONTRACT)],
            cwd=ROOT,
        )
        if issue454_preboot_state.returncode != 0:
            fail("Issue #454 preboot state-order contract failed")

        issue456_requirements_truth = subprocess.run(
            ["node", str(ISSUE456_REQUIREMENTS_TRUTH_RUNTIME)],
            cwd=ROOT,
        )
        if issue456_requirements_truth.returncode != 0:
            fail("Issue #456 requirements truth-state runtime failed")

        issue458_requirements_source = subprocess.run(
            ["node", str(ISSUE458_REQUIREMENTS_SOURCE_RUNTIME)], cwd=ROOT,
        )
        if issue458_requirements_source.returncode != 0:
            fail("Issue #458 requirements source-discovery runtime failed")

        issue464_launcher_settings = subprocess.run(
            [sys.executable, str(ISSUE464_LAUNCHER_SETTINGS_CONTRACT)], cwd=ROOT,
        )
        if issue464_launcher_settings.returncode != 0:
            fail("Issue #464 launcher/settings contract failed")

        issue464_operational_runtime = subprocess.run(
            ["node", str(ISSUE464_OPERATIONAL_RUNTIME)], cwd=ROOT,
        )
        if issue464_operational_runtime.returncode != 0:
            fail("Issue #464 operational runtime fixtures failed")

        report = json.loads(integrity_json.read_text(encoding="utf-8"))
        metrics = report.get("metrics", {})
        print(
            "Code integrity passed: "
            f"{metrics.get('staticSelectors', 0)} static selectors, "
            f"{metrics.get('shortcutBindings', 0)} shortcut bindings, "
            f"{metrics.get('repositoryTextFiles', 0)} repository text files."
        )


def main() -> int:
    if not SOURCE.exists():
        fail(f"canonical source is missing: {SOURCE.relative_to(ROOT)}")

    raw = SOURCE.read_bytes()
    if len(raw) < 100_000:
        fail(f"source is unexpectedly small: {len(raw)} bytes")

    try:
        text = raw.decode("utf-8")
    except UnicodeDecodeError as exc:
        fail(f"source is not valid UTF-8: {exc}")

    if CONFLICT_RE.search(text):
        fail("unresolved merge-conflict markers were found")

    meta = metadata(text)
    missing = sorted(REQUIRED_KEYS - set(meta))
    if missing:
        fail("missing required metadata: " + ", ".join("@" + key for key in missing))

    name = one(meta, "name")
    version = one(meta, "version")
    author = optional_one(meta, "author")
    license_name = optional_one(meta, "license")

    if "missionchief map command toolkit" not in name.casefold():
        fail(f"unexpected @name: {name}")
    if not VERSION_RE.fullmatch(version):
        fail(f"invalid semantic @version: {version}")

    runtime_version = internal_script_version(text)
    if runtime_version != version:
        fail(
            "userscript @version and internal SCRIPT.version differ: "
            f"{version} != {runtime_version}"
        )

    matches = meta.get("match", []) + meta.get("include", [])
    missionchief_rules = [value for value in matches if is_missionchief_rule(value)]
    if not missionchief_rules:
        fail("no MissionChief UK @match or @include rule was found")

    if not changelog_has_version(version):
        fail(f"CHANGELOG.md has no release heading for version {version}")

    source_hash = hashlib.sha256(raw).hexdigest()
    baseline_match = None
    if BASELINE.exists():
        baseline = json.loads(BASELINE.read_text(encoding="utf-8"))
        if baseline.get("importedVersion") == version:
            baseline_match = baseline.get("sha256") == source_hash
            if not baseline_match:
                fail("source changed without a version bump from the imported baseline")

    run_integrity_gate()

    DIST.mkdir(parents=True, exist_ok=True)
    USER_JS.write_bytes(raw)
    TXT.write_bytes(raw)

    if USER_JS.read_bytes() != TXT.read_bytes():
        fail("generated .user.js and .txt files are not byte-identical")

    user_hash = sha256(USER_JS)
    txt_hash = sha256(TXT)
    SUMS.write_text(
        f"{user_hash}  {USER_JS.name}\n{txt_hash}  {TXT.name}\n",
        encoding="utf-8",
    )

    metadata_warnings = []
    if not author:
        metadata_warnings.append("@author is absent from the imported legacy baseline")
    elif "conroy1988" not in author.casefold():
        metadata_warnings.append(f"legacy @author value is {author!r}")
    if not license_name:
        metadata_warnings.append("@license is absent from the imported legacy baseline")
    elif "mit" not in license_name.casefold():
        metadata_warnings.append(f"legacy @license value is {license_name!r}")

    manifest = {
        "project": "MissionChief Map Command Toolkit",
        "version": version,
        "source": str(SOURCE.relative_to(ROOT)),
        "distributionFiles": [str(USER_JS.relative_to(ROOT)), str(TXT.relative_to(ROOT))],
        "sha256": user_hash,
        "bytes": len(raw),
        "lines": text.count("\n") + 1,
        "metadata": {
            "name": name,
            "runtimeVersion": runtime_version,
            "author": author,
            "license": license_name,
            "missionChiefRules": missionchief_rules,
            "warnings": metadata_warnings,
        },
        "baselineHashMatch": baseline_match,
        "distributionStatus": "dry-run-not-yet-greasyfork-source",
    }
    MANIFEST.write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")

    print(
        json.dumps(
            {
                "version": version,
                "sha256": user_hash,
                "bytes": len(raw),
                "lines": manifest["lines"],
                "baselineHashMatch": baseline_match,
                "metadataWarnings": metadata_warnings,
                "codeIntegrity": "passed",
                "staticAssetIntegrity": "passed",
            },
            indent=2,
        )
    )
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    finally:
        cleanup_repository_bytecode()
