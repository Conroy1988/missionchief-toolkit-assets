#!/usr/bin/env python3
"""Execute and record the complete Issue #567 production-health audit."""
from __future__ import annotations

import hashlib
import json
import os
import shutil
import subprocess
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
SOURCE = ROOT / "src" / "MissionChief_Map_Command_Toolkit.user.js"
DIST_JS = ROOT / "dist" / "MissionChief_Map_Command_Toolkit.user.js"
DIST_TXT = ROOT / "dist" / "MissionChief_Map_Command_Toolkit.txt"
STATIC_AUDIT = ROOT / ".github" / "scripts" / "audit_full_production_health.py"
STRESS_AUDIT = ROOT / ".github" / "scripts" / "audit_runtime_stress.mjs"
PACKAGE_PATH = ".github/development-packages/issue567_full_production_health_audit.py"
REPORT_DIR = ROOT / "docs" / "audits" / "issue-567"
WORK = Path(tempfile.mkdtemp(prefix="mcms-issue567-audit-"))
OUT = WORK / "output"
OUT.mkdir(parents=True, exist_ok=True)


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def patch_static_audit_package_allowance() -> None:
    text = STATIC_AUDIT.read_text(encoding="utf-8")
    if PACKAGE_PATH in text:
        return
    marker = '        ".github/workflows/temporary-full-production-health-audit.yml",\n'
    if marker not in text:
        raise RuntimeError("Static audit expected-file marker changed")
    replacement = marker + f'        "{PACKAGE_PATH}",\n'
    STATIC_AUDIT.write_text(text.replace(marker, replacement, 1), encoding="utf-8")


def run(label: str, command: list[str], log_name: str, time_name: str | None = None) -> dict:
    log_path = OUT / log_name
    actual = command
    if time_name:
        actual = ["/usr/bin/time", "-v", "-o", str(OUT / time_name), *command]
    started = subprocess.run(
        actual,
        cwd=ROOT,
        env={
            **os.environ,
            "MCMS_AUDIT_OUTPUT": str(OUT),
            "MCMS_AUDIT_REPEATS": "8",
            "PYTHONDONTWRITEBYTECODE": "1",
            "NODE_OPTIONS": "--unhandled-rejections=strict",
        },
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
    )
    log_path.write_text(started.stdout or "", encoding="utf-8")
    result = {
        "label": label,
        "command": command,
        "returnCode": started.returncode,
        "log": log_name,
        "time": time_name,
    }
    if started.returncode != 0:
        tail = "\n".join((started.stdout or "").splitlines()[-80:])
        raise RuntimeError(f"{label} failed with exit {started.returncode}:\n{tail}")
    return result


def copy_if_present(name: str) -> None:
    source = OUT / name
    if source.exists():
        shutil.copy2(source, REPORT_DIR / name)


def main() -> int:
    if not STATIC_AUDIT.is_file() or not STRESS_AUDIT.is_file():
        raise RuntimeError("Issue #567 audit probes are missing")

    patch_static_audit_package_allowance()
    source_before = sha256(SOURCE)
    results: list[dict] = []
    REPORT_DIR.mkdir(parents=True, exist_ok=True)

    try:
        results.append(
            run(
                "Install isolated jsdom runtime",
                ["npm", "install", "--no-save", "--package-lock=false", "--ignore-scripts", "jsdom@26.1.0"],
                "npm-install.log",
                "npm-install-time.txt",
            )
        )
        results.append(
            run(
                "Complete retained preflight — pass 1",
                ["bash", ".github/scripts/run_userscript_preflight.sh", "--all"],
                "preflight.log",
                "preflight-time.txt",
            )
        )
        results.append(
            run(
                "Lifecycle, recurring-work and teardown inventory",
                ["python3", "-X", "dev", ".github/scripts/audit_full_production_health.py"],
                "full-production-health.log",
                "full-production-health-time.txt",
            )
        )
        results.append(
            run(
                "Repeated runtime and memory stress",
                ["node", ".github/scripts/audit_runtime_stress.mjs"],
                "runtime-stress.log",
                "runtime-stress-time.txt",
            )
        )
        results.append(
            run(
                "Complete retained preflight — deterministic pass 2",
                ["bash", ".github/scripts/run_userscript_preflight.sh", "--all"],
                "preflight-repeat.log",
                "preflight-repeat-time.txt",
            )
        )

        source_after = sha256(SOURCE)
        if source_before != source_after:
            raise RuntimeError("Canonical userscript changed during the read-only audit")
        if SOURCE.read_bytes() != DIST_JS.read_bytes() or SOURCE.read_bytes() != DIST_TXT.read_bytes():
            raise RuntimeError("Canonical source and distribution mirrors diverged during the audit")

        static_report = json.loads((OUT / "full-production-health.json").read_text(encoding="utf-8"))
        stress_report = json.loads((OUT / "runtime-stress.json").read_text(encoding="utf-8"))
        if static_report.get("status") == "failed":
            raise RuntimeError("Static production-health audit reported failure")
        if stress_report.get("status") != "passed":
            raise RuntimeError("Repeated runtime stress audit reported failure")

        execution = {
            "schemaVersion": 1,
            "issue": 567,
            "version": static_report.get("version"),
            "sourceSha256Before": source_before,
            "sourceSha256After": source_after,
            "status": "passed",
            "commands": results,
            "staticAuditStatus": static_report.get("status"),
            "staticWarnings": static_report.get("warnings", []),
            "runtimeStressStatus": stress_report.get("status"),
            "repeatedRuntimeExecutions": stress_report.get("repeatedExecutions"),
            "runtimeStressSeconds": stress_report.get("totalSeconds"),
        }
        (OUT / "audit-execution.json").write_text(
            json.dumps(execution, indent=2, sort_keys=True) + "\n", encoding="utf-8"
        )
        markdown = [
            f"# Toolkit {execution['version']} complete production-health audit",
            "",
            "- **Status:** `passed`",
            f"- **Canonical SHA-256 before/after:** `{source_before}`",
            f"- **Repeated runtime executions:** {execution['repeatedRuntimeExecutions']}",
            f"- **Runtime stress elapsed:** {float(execution['runtimeStressSeconds']):.2f} seconds",
            f"- **Static audit:** `{execution['staticAuditStatus']}`",
            "- **Complete retained preflight:** passed twice",
            "- **Canonical source mutation:** none",
            "- **Distribution parity:** passed",
            "",
            "## Static warnings",
            "",
            *([f"- {item}" for item in execution["staticWarnings"]] or ["- None."]),
            "",
        ]
        (OUT / "audit-execution.md").write_text("\n".join(markdown), encoding="utf-8")

        for name in [
            "audit-execution.json",
            "audit-execution.md",
            "full-production-health.json",
            "full-production-health.md",
            "runtime-stress.json",
            "runtime-stress.md",
            "npm-install-time.txt",
            "preflight-time.txt",
            "full-production-health-time.txt",
            "runtime-stress-time.txt",
            "preflight-repeat-time.txt",
        ]:
            copy_if_present(name)
        print(json.dumps(execution, indent=2, sort_keys=True))
        return 0
    finally:
        shutil.rmtree(ROOT / "node_modules", ignore_errors=True)
        package_lock = ROOT / "package-lock.json"
        if package_lock.exists() and not subprocess.run(
            ["git", "ls-files", "--error-unmatch", "package-lock.json"],
            cwd=ROOT,
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
        ).returncode == 0:
            package_lock.unlink()
        shutil.rmtree(WORK, ignore_errors=True)


if __name__ == "__main__":
    raise SystemExit(main())
