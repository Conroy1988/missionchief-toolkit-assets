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
VARIANT_BUILDER = ROOT / ".github" / "scripts" / "build_distribution_variants.py"
INSTALL_USER_JS = DIST / "MissionChief_Map_Command_Toolkit.install.user.js"
UPDATE_USER_JS = DIST / "MissionChief_Map_Command_Toolkit.update.user.js"
META_JS = DIST / "MissionChief_Map_Command_Toolkit.meta.js"
GREASY_FORK_USER_JS = DIST / "MissionChief_Map_Command_Toolkit.greasyfork.user.js"
MAIN_STYLESHEET = DIST / "MissionChief_Map_Command_Toolkit.css"
INTEGRITY_AUDITOR = ROOT / ".github" / "scripts" / "check_code_integrity.py"
INTEGRITY_POLICY = ROOT / ".github" / "code-integrity-policy.json"
ASSET_AUDITOR = ROOT / ".github" / "scripts" / "check_asset_health.py"
AUDIO_ALIAS_AUDITOR = ROOT / ".github" / "scripts" / "check_audio_alias_contract.py"
VERSION_STATUS_CONTRACT = ROOT / ".github" / "scripts" / "test_version_status_contract.py"
FINANCIAL_OVERVIEW_CONTRACT = ROOT / ".github" / "scripts" / "test_financial_overview_contract.py"
MAIN_STYLE_HEADROOM_CONTRACT = ROOT / ".github" / "scripts" / "test_main_style_source_headroom.py"
V7_RETIREMENT_CONTRACT = ROOT / ".github" / "scripts" / "test_v7_retirement.py"
MISSION_AGE_RETENTION_CONTRACT = ROOT / ".github" / "scripts" / "test_mission_age_retention.py"
NATIVE_TRANSPORT_SWEEP_CONTRACT = ROOT / ".github" / "scripts" / "test_transport_sweep_native_contract.py"
ISSUE447_MENU_BOOT_CONTRACT = ROOT / ".github" / "scripts" / "test_issue447_menu_boot_fail_open.py"
ISSUE450_CORE_BOOTSTRAP_CONTRACT = ROOT / ".github" / "scripts" / "test_issue450_core_launcher_bootstrap.py"
ISSUE454_PREBOOT_STATE_CONTRACT = ROOT / ".github" / "scripts" / "test_issue454_preboot_state_order.py"
ISSUE464_LAUNCHER_SETTINGS_CONTRACT = ROOT / ".github" / "scripts" / "test_issue464_launcher_settings_contract.py"

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
    required=[INTEGRITY_AUDITOR,INTEGRITY_POLICY,ASSET_AUDITOR,AUDIO_ALIAS_AUDITOR,VERSION_STATUS_CONTRACT,FINANCIAL_OVERVIEW_CONTRACT,MAIN_STYLE_HEADROOM_CONTRACT,V7_RETIREMENT_CONTRACT,MISSION_AGE_RETENTION_CONTRACT,NATIVE_TRANSPORT_SWEEP_CONTRACT,ISSUE447_MENU_BOOT_CONTRACT,ISSUE450_CORE_BOOTSTRAP_CONTRACT,ISSUE454_PREBOOT_STATE_CONTRACT,ISSUE464_LAUNCHER_SETTINGS_CONTRACT,VARIANT_BUILDER]
    missing=[path.relative_to(ROOT) for path in required if not path.exists()]
    if missing: fail("integrity tooling is incomplete: "+", ".join(map(str,missing)))
    with tempfile.TemporaryDirectory(prefix="mcms-integrity-") as temp:
        baseline_path=Path(temp)/"release-baseline.user.js";baseline_ref=latest_release_baseline(baseline_path);integrity_json=Path(temp)/"code-integrity-report.json";integrity_md=Path(temp)/"code-integrity-report.md";asset_json=Path(temp)/"asset-health-report.json";asset_md=Path(temp)/"asset-health-report.md"
        command=[sys.executable,str(INTEGRITY_AUDITOR),"--candidate",str(SOURCE),"--policy",str(INTEGRITY_POLICY),"--json-output",str(integrity_json),"--markdown-output",str(integrity_md)]
        if baseline_ref and baseline_path.exists(): command.extend(["--base",str(baseline_path)])
        if subprocess.run(command,cwd=ROOT).returncode!=0: fail("expanded code-integrity audit failed")
        if subprocess.run([sys.executable,str(ASSET_AUDITOR),"--mode","static","--json-output",str(asset_json),"--markdown-output",str(asset_md)],cwd=ROOT).returncode!=0: fail("static public-asset integrity audit failed")
        for contract in [AUDIO_ALIAS_AUDITOR,VERSION_STATUS_CONTRACT,FINANCIAL_OVERVIEW_CONTRACT,MAIN_STYLE_HEADROOM_CONTRACT,V7_RETIREMENT_CONTRACT,MISSION_AGE_RETENTION_CONTRACT,NATIVE_TRANSPORT_SWEEP_CONTRACT,ISSUE447_MENU_BOOT_CONTRACT,ISSUE450_CORE_BOOTSTRAP_CONTRACT,ISSUE454_PREBOOT_STATE_CONTRACT,ISSUE464_LAUNCHER_SETTINGS_CONTRACT]:
            if subprocess.run([sys.executable,str(contract)],cwd=ROOT).returncode!=0: fail(f"contract failed: {contract.relative_to(ROOT)}")
        report=json.loads(integrity_json.read_text());metrics=report.get("metrics",{});print(f"Code integrity passed: {metrics.get('staticSelectors',0)} selectors.")

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

    variant_result = subprocess.run(
        [sys.executable, str(VARIANT_BUILDER)],
        cwd=ROOT,
        check=False,
        capture_output=True,
        text=True,
    )
    if variant_result.returncode != 0:
        fail("distribution variant build failed: " + (variant_result.stderr or variant_result.stdout).strip())
    try:
        variant_evidence = json.loads(variant_result.stdout)
    except json.JSONDecodeError as error:
        fail(f"distribution variant evidence is invalid: {error}")

    retired_extension_token = "ls" + "sm"
    if retired_extension_token in USER_JS.read_text(encoding="utf-8").lower() or retired_extension_token in TXT.read_text(encoding="utf-8").lower():
        fail("retired integration content remains in generated distribution")

    if USER_JS.read_bytes() != TXT.read_bytes():
        fail("generated .user.js and .txt files are not byte-identical")

    user_hash = sha256(USER_JS)
    txt_hash = sha256(TXT)
    distribution_files = [
        USER_JS,
        TXT,
        INSTALL_USER_JS,
        UPDATE_USER_JS,
        META_JS,
        GREASY_FORK_USER_JS,
        MAIN_STYLESHEET,
    ]
    missing_variants = [path.name for path in distribution_files if not path.is_file()]
    if missing_variants:
        fail("distribution variants are missing: " + ", ".join(missing_variants))
    if INSTALL_USER_JS.read_bytes() != raw or UPDATE_USER_JS.read_bytes() != raw:
        fail("first-party install and update assets must match the canonical userscript")
    SUMS.write_text(
        "".join(f"{sha256(path)}  {path.name}\n" for path in distribution_files),
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
        "distributionFiles": [str(path.relative_to(ROOT)) for path in distribution_files],
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
        "distribution": {
            "officialChannel": "tkb-gaming.scot",
            "installUrl": "https://tkb-gaming.scot/mission-chief-scripts/map-command-toolkit/install/",
            "updateUrl": "https://tkb-gaming.scot/mission-chief-scripts/map-command-toolkit/update/",
            "metadataUrl": "https://tkb-gaming.scot/mission-chief-scripts/map-command-toolkit/metadata/",
            "greasyForkMirror": "non-blocking",
            "greasyForkCharacters": variant_evidence["greasyForkCharacters"],
            "greasyForkLimit": variant_evidence["greasyForkLimit"],
            "stylesheetSha256": variant_evidence["stylesheetSha256"],
        },
        "distributionStatus": "dry-run-first-party-and-mirror-assets",
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
