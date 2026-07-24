#!/usr/bin/env python3
"""Non-destructive repository and userscript dependency audit.

Audit output is immutable workflow evidence. The script never mutates the production
release dashboard or any committed repository state.
"""

from __future__ import annotations

import hashlib
import json
import os
import re
import sys
import urllib.error
import urllib.request
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
OUTPUT_DIR = ROOT / os.environ.get("REPOSITORY_AUDIT_OUTPUT_DIR", "repository-audit-output")
REPORT_MD = OUTPUT_DIR / "repository-audit.md"
REPORT_JSON = OUTPUT_DIR / "repository-audit.json"
GREASYFORK_SCRIPT = (
    "https://update.greasyfork.org/scripts/586018/"
    "MissionChief%20Map%20Command%20Toolkit.user.js"
)
REPO_RAW_PREFIX = (
    "https://raw.githubusercontent.com/Conroy1988/"
    "missionchief-toolkit-assets/"
)

TEXT_SUFFIXES = {
    ".js", ".mjs", ".cjs", ".json", ".md", ".txt", ".yml", ".yaml",
    ".html", ".css", ".svg", ".py", ".sh", ".toml", ".ini",
}
MEDIA_SUFFIXES = {
    ".png", ".jpg", ".jpeg", ".gif", ".webp", ".svg", ".mp3", ".wav",
    ".ogg", ".m4a", ".flac", ".mp4", ".webm",
}
URL_RE = re.compile(r"https://raw\.githubusercontent\.com/Conroy1988/missionchief-toolkit-assets/[^\s\"'`)<>]+")
VERSION_RE = re.compile(r"^//\s*@version\s+([^\s]+)", re.MULTILINE)


def rel(path: Path) -> str:
    return path.relative_to(ROOT).as_posix()


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def read_text(path: Path) -> str:
    return path.read_text(encoding="utf-8", errors="replace")


def download_userscript() -> tuple[str, str | None]:
    request = urllib.request.Request(
        GREASYFORK_SCRIPT,
        headers={"User-Agent": "MissionChief-Toolkit-Repository-Audit/3"},
    )
    try:
        with urllib.request.urlopen(request, timeout=45) as response:
            return response.read().decode("utf-8", errors="replace"), None
    except (urllib.error.URLError, TimeoutError, OSError) as exc:
        return "", str(exc)


def raw_url_to_repo_path(url: str) -> str | None:
    if not url.startswith(REPO_RAW_PREFIX):
        return None
    remainder = url[len(REPO_RAW_PREFIX):]
    if "/" not in remainder:
        return None
    _ref, path = remainder.split("/", 1)
    return path.split("?", 1)[0].split("#", 1)[0]


def main() -> int:
    files = [p for p in ROOT.rglob("*") if p.is_file() and ".git" not in p.parts and OUTPUT_DIR not in p.parents]
    suffix_counts = Counter((p.suffix.lower() or "[none]") for p in files)
    media_files = sorted(rel(p) for p in files if p.suffix.lower() in MEDIA_SUFFIXES)
    workflows = sorted(rel(p) for p in (ROOT / ".github" / "workflows").glob("*.y*ml"))

    one_shot_workflows = []
    workflow_secrets = set()
    for workflow in workflows:
        text = read_text(ROOT / workflow)
        if re.search(r"one[- ]?shot|one[- ]?time|v\d+\.\d+\.\d+", text, re.I):
            one_shot_workflows.append(workflow)
        workflow_secrets.update(re.findall(r"secrets\.([A-Z0-9_]+)", text))

    local_raw_urls = set()
    for path in files:
        if path.suffix.lower() not in TEXT_SUFFIXES:
            continue
        local_raw_urls.update(URL_RE.findall(read_text(path)))

    userscript, fetch_error = download_userscript()
    userscript_version = None
    userscript_raw_urls = set()
    if userscript:
        match = VERSION_RE.search(userscript)
        userscript_version = match.group(1).strip() if match else None
        userscript_raw_urls.update(URL_RE.findall(userscript))

    all_raw_urls = sorted(local_raw_urls | userscript_raw_urls)
    referenced_paths = []
    missing_paths = []
    external_refs = []
    for url in all_raw_urls:
        path = raw_url_to_repo_path(url)
        if path is None:
            external_refs.append(url)
            continue
        referenced_paths.append(path)
        if not (ROOT / path).is_file():
            missing_paths.append(path)

    possible_userscripts = sorted(
        rel(p) for p in files if p.name.endswith(".user.js") or "userscript" in p.name.lower()
    )

    duplicate_hashes: dict[str, list[str]] = {}
    for path in files:
        if path.suffix.lower() not in MEDIA_SUFFIXES:
            continue
        duplicate_hashes.setdefault(sha256(path), []).append(rel(path))
    duplicate_groups = [paths for paths in duplicate_hashes.values() if len(paths) > 1]

    generated_at = datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")
    audit = {
        "schemaVersion": 2,
        "state": "passed" if not missing_paths else "attention-required",
        "repository": "Conroy1988/missionchief-toolkit-assets",
        "commit": os.environ.get("GITHUB_SHA", "local"),
        "generatedAt": generated_at,
        "storage": {
            "type": "workflow-artifact",
            "publicMainChanged": False,
            "releaseDashboardChanged": False,
        },
        "greasyFork": {
            "scriptFetched": bool(userscript),
            "fetchError": fetch_error,
            "version": userscript_version,
            "rawRepositoryReferences": len(userscript_raw_urls),
        },
        "inventory": {
            "files": len(files),
            "mediaFiles": len(media_files),
            "workflows": len(workflows),
            "possibleUserscripts": possible_userscripts,
            "suffixCounts": dict(sorted(suffix_counts.items())),
        },
        "dependencies": {
            "rawUrls": all_raw_urls,
            "referencedPaths": sorted(set(referenced_paths)),
            "missingPaths": sorted(set(missing_paths)),
            "externalReferences": external_refs,
        },
        "automation": {
            "workflows": workflows,
            "possibleOneShotWorkflows": one_shot_workflows,
            "referencedSecrets": sorted(workflow_secrets),
        },
        "duplicates": {
            "mediaGroups": duplicate_groups,
        },
        "policy": {
            "destructiveChangesPerformed": False,
            "existingPublicPathsPreserved": True,
        },
    }

    lines = [
        "# Repository and dependency audit",
        "",
        "> Generated as immutable GitHub Actions evidence. This audit does not rename, move or delete files and does not modify public `main` or the release dashboard.",
        "",
        "## Evidence",
        "",
        f"- Source commit: `{audit['commit']}`",
        f"- Generated: `{generated_at}`",
        f"- State: **{audit['state']}**",
        "- Storage: **workflow artifact**",
        "- Public `main` changed: **no**",
        "- Release dashboard changed: **no**",
        "",
        "## Summary",
        "",
        f"- Repository files: **{len(files)}**",
        f"- Media files: **{len(media_files)}**",
        f"- GitHub Actions workflows: **{len(workflows)}**",
        f"- Greasy Fork version: **{userscript_version or 'unavailable'}**",
        f"- Repository URLs referenced by current script/repository: **{len(all_raw_urls)}**",
        f"- Missing referenced paths: **{len(set(missing_paths))}**",
        f"- Possible one-shot workflows: **{len(one_shot_workflows)}**",
        f"- Duplicate media groups: **{len(duplicate_groups)}**",
        "",
        "## Referenced public repository paths",
        "",
    ]
    if referenced_paths:
        for path in sorted(set(referenced_paths)):
            marker = "❌ missing" if path in missing_paths else "✅ present"
            lines.append(f"- `{path}` — {marker}")
    else:
        lines.append("- No raw repository references were discovered.")

    lines.extend(["", "## Workflow inventory", ""])
    for workflow in workflows:
        suffix = " — review as possible temporary workflow" if workflow in one_shot_workflows else ""
        lines.append(f"- `{workflow}`{suffix}")

    lines.extend(["", "## Referenced GitHub Actions secrets", ""])
    if workflow_secrets:
        for secret in sorted(workflow_secrets):
            lines.append(f"- `{secret}`")
    else:
        lines.append("- No workflow secret references were discovered.")

    lines.extend(["", "## Safety findings", ""])
    if missing_paths:
        lines.append("- Some public paths referenced by the current script are missing and require review.")
    else:
        lines.append("- Every discovered raw repository path referenced by the current script exists in the repository.")
    lines.append("- Existing public media paths remain protected and should not be reorganised in place.")
    lines.append("- The production release dashboard remains authoritative and was not modified by this audit.")

    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    REPORT_MD.write_text("\n".join(lines) + "\n", encoding="utf-8")
    REPORT_JSON.write_text(json.dumps(audit, indent=2) + "\n", encoding="utf-8")

    print(json.dumps(audit, indent=2))
    return 1 if missing_paths else 0


if __name__ == "__main__":
    raise SystemExit(main())
