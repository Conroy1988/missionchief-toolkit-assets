#!/usr/bin/env python3
"""Audit live Greasy Fork against the GitHub-authoritative canonical userscript.

The audit is deliberately read-only. A canonical version ahead of Greasy Fork is an
expected pre-publication state. A live version ahead of GitHub, or equal-version
content drift, fails closed and requires an owner-reviewed repository change.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import re
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
DEFAULT_CANONICAL = ROOT / "src" / "MissionChief_Map_Command_Toolkit.user.js"
VERSION_RE = re.compile(r"^//\s*@version\s+([^\s]+)", re.MULTILINE)
NAME_RE = re.compile(r"^//\s*@name\s+(.+?)\s*$", re.MULTILINE)
SEMVER_RE = re.compile(
    r"^(0|[1-9]\d*)\.(0|[1-9]\d*)\.(0|[1-9]\d*)"
    r"(?:-([0-9A-Za-z.-]+))?(?:\+([0-9A-Za-z.-]+))?$"
)


def sha256(payload: bytes) -> str:
    return hashlib.sha256(payload).hexdigest()


def metadata(path: Path) -> dict[str, object]:
    payload = path.read_bytes()
    text = payload.decode("utf-8")
    if "// ==UserScript==" not in text or "// ==/UserScript==" not in text:
        raise ValueError(f"userscript metadata block is missing: {path}")
    versions = VERSION_RE.findall(text)
    names = NAME_RE.findall(text)
    if len(versions) != 1:
        raise ValueError(f"userscript must contain exactly one @version: {path}")
    if len(names) != 1 or "MissionChief Map Command Toolkit" not in names[0]:
        raise ValueError(f"userscript has an unexpected @name: {path}")
    version = versions[0].strip()
    if not SEMVER_RE.fullmatch(version):
        raise ValueError(f"userscript has a non-semantic @version {version!r}: {path}")
    return {
        "name": names[0].strip(),
        "version": version,
        "sha256": sha256(payload),
        "bytes": len(payload),
        "lines": text.count("\n") + 1,
    }


def prerelease_key(value: str | None) -> tuple[tuple[int, object], ...] | None:
    if value is None:
        return None
    parts: list[tuple[int, object]] = []
    for token in value.split("."):
        if token.isdigit():
            parts.append((0, int(token)))
        else:
            parts.append((1, token))
    return tuple(parts)


def compare_semver(left: str, right: str) -> int:
    left_match = SEMVER_RE.fullmatch(left)
    right_match = SEMVER_RE.fullmatch(right)
    if not left_match or not right_match:
        raise ValueError("semantic versions are required")

    left_core = tuple(int(value) for value in left_match.groups()[:3])
    right_core = tuple(int(value) for value in right_match.groups()[:3])
    if left_core != right_core:
        return 1 if left_core > right_core else -1

    left_pre = prerelease_key(left_match.group(4))
    right_pre = prerelease_key(right_match.group(4))
    if left_pre is None and right_pre is None:
        return 0
    if left_pre is None:
        return 1
    if right_pre is None:
        return -1
    if left_pre == right_pre:
        return 0
    return 1 if left_pre > right_pre else -1


def classify(canonical: dict[str, object], live: dict[str, object]) -> tuple[str, bool, str]:
    canonical_version = str(canonical["version"])
    live_version = str(live["version"])
    canonical_hash = str(canonical["sha256"])
    live_hash = str(live["sha256"])

    if canonical_version == live_version:
        if canonical_hash == live_hash:
            return (
                "in-sync",
                True,
                "GitHub canonical source and the live Greasy Fork distribution are byte-identical.",
            )
        return (
            "equal-version-content-mismatch",
            False,
            "GitHub and Greasy Fork report the same version but different content hashes.",
        )

    ordering = compare_semver(canonical_version, live_version)
    if ordering > 0:
        return (
            "canonical-ahead",
            True,
            "GitHub canonical source is ahead of Greasy Fork; this is an expected pre-publication state.",
        )
    return (
        "live-ahead",
        False,
        "Greasy Fork is ahead of GitHub canonical source. Automatic importing is retired; owner review is required.",
    )


def build_report(
    canonical: dict[str, object],
    live: dict[str, object],
    *,
    source_url: str,
    source_commit: str,
    generated_at: str,
) -> dict[str, object]:
    state, acceptable, summary = classify(canonical, live)
    return {
        "schemaVersion": 1,
        "project": "MissionChief Map Command Toolkit",
        "authority": "GitHub canonical source",
        "state": state,
        "acceptable": acceptable,
        "summary": summary,
        "sourceCommit": source_commit,
        "generatedAt": generated_at,
        "canonical": canonical,
        "greasyFork": {
            **live,
            "sourceUrl": source_url,
        },
        "mutation": {
            "publicMainChanged": False,
            "canonicalSourceChanged": False,
            "sourceBaselineChanged": False,
            "pullRequestCreated": False,
        },
        "policy": {
            "automaticImportEnabled": False,
            "liveAheadRequiresOwnerReview": True,
            "equalVersionHashMismatchRequiresOwnerReview": True,
        },
    }


def render_markdown(report: dict[str, object]) -> str:
    canonical = report["canonical"]
    live = report["greasyFork"]
    mutation = report["mutation"]
    assert isinstance(canonical, dict)
    assert isinstance(live, dict)
    assert isinstance(mutation, dict)
    marker = "✅" if report["acceptable"] else "❌"
    return "\n".join(
        [
            "# Greasy Fork canonical parity audit",
            "",
            f"- State: **{marker} {report['state']}**",
            f"- Authority: **{report['authority']}**",
            f"- Summary: {report['summary']}",
            f"- Source commit: `{report['sourceCommit']}`",
            f"- Generated: `{report['generatedAt']}`",
            "",
            "## Canonical GitHub source",
            "",
            f"- Version: `{canonical['version']}`",
            f"- SHA-256: `{canonical['sha256']}`",
            f"- Bytes: `{canonical['bytes']}`",
            f"- Lines: `{canonical['lines']}`",
            "",
            "## Live Greasy Fork distribution",
            "",
            f"- Version: `{live['version']}`",
            f"- SHA-256: `{live['sha256']}`",
            f"- Bytes: `{live['bytes']}`",
            f"- Lines: `{live['lines']}`",
            "",
            "## Mutation proof",
            "",
            f"- Public `main` changed: **{'yes' if mutation['publicMainChanged'] else 'no'}**",
            f"- Canonical source changed: **{'yes' if mutation['canonicalSourceChanged'] else 'no'}**",
            f"- Bootstrap baseline changed: **{'yes' if mutation['sourceBaselineChanged'] else 'no'}**",
            f"- Pull request created: **{'yes' if mutation['pullRequestCreated'] else 'no'}**",
            "",
            "The former automatic importer is retired. Any live-ahead or equal-version content drift requires an owner-reviewed repository change.",
            "",
        ]
    )


def self_test() -> None:
    base = {
        "name": "MissionChief Map Command Toolkit",
        "version": "5.0.7",
        "sha256": "a" * 64,
        "bytes": 100,
        "lines": 10,
    }
    assert classify(base, dict(base))[0:2] == ("in-sync", True)

    mismatch = {**base, "sha256": "b" * 64}
    assert classify(base, mismatch)[0:2] == ("equal-version-content-mismatch", False)

    older = {**base, "version": "5.0.6", "sha256": "c" * 64}
    assert classify(base, older)[0:2] == ("canonical-ahead", True)

    newer = {**base, "version": "5.0.8", "sha256": "d" * 64}
    assert classify(base, newer)[0:2] == ("live-ahead", False)

    assert compare_semver("5.1.0", "5.0.9") > 0
    assert compare_semver("5.0.7", "5.0.7-rc.1") > 0
    assert compare_semver("5.0.7-rc.2", "5.0.7-rc.1") > 0
    print("Greasy Fork canonical parity self-tests passed.")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("--canonical", type=Path, default=DEFAULT_CANONICAL)
    parser.add_argument("--live", type=Path)
    parser.add_argument("--source-url", default="")
    parser.add_argument("--source-commit", default="local")
    parser.add_argument("--json-output", type=Path)
    parser.add_argument("--markdown-output", type=Path)
    parser.add_argument("--self-test", action="store_true")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    if args.self_test:
        self_test()
        return 0
    if not args.live or not args.json_output or not args.markdown_output:
        raise SystemExit("--live, --json-output and --markdown-output are required")

    canonical = metadata(args.canonical)
    live = metadata(args.live)
    generated_at = datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")
    report = build_report(
        canonical,
        live,
        source_url=args.source_url,
        source_commit=args.source_commit,
        generated_at=generated_at,
    )

    args.json_output.parent.mkdir(parents=True, exist_ok=True)
    args.markdown_output.parent.mkdir(parents=True, exist_ok=True)
    args.json_output.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    args.markdown_output.write_text(render_markdown(report), encoding="utf-8")
    print(json.dumps(report, indent=2))
    return 0 if report["acceptable"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
