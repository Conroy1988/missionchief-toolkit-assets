#!/usr/bin/env python3
from __future__ import annotations

import base64
import json
import os
import sys
import urllib.error
import urllib.request
from pathlib import Path

REPLACEMENTS = {
    "actions/checkout@v7": "actions/checkout@9c091bb21b7c1c1d1991bb908d89e4e9dddfe3e0 # v7",
    "actions/upload-artifact@v4": "actions/upload-artifact@b7c566a772e6b6bfb58ed0dc250532a479d7789f # v6",
    "actions/upload-artifact@v6": "actions/upload-artifact@b7c566a772e6b6bfb58ed0dc250532a479d7789f # v6",
    "actions/cache/restore@v4": "actions/cache/restore@0057852bfaa89a56745cba8c7296529d2fc39830 # v4",
    "actions/cache/save@v4": "actions/cache/save@0057852bfaa89a56745cba8c7296529d2fc39830 # v4",
    "actions/configure-pages@v5": "actions/configure-pages@983d7736d9b0ae728b81ab479565c72886d7745b # v5",
    "actions/upload-pages-artifact@v3": "actions/upload-pages-artifact@56afc609e74202658d3ffba0e8f6dda462b719fa # v3",
    "actions/deploy-pages@v5": "actions/deploy-pages@cd2ce8fcbc39b97be8ca5fce6e763baed58fa128 # v5",
}
TEMPORARY = {
    ".github/workflows/actions-security-inventory.yml",
    ".github/workflows/actions-tree-inventory.yml",
    ".github/workflows/apply-actions-pinning.yml",
    ".github/workflows/prepare-actions-security-commit.yml",
    ".github/workflows/prepare-actions-security-commit-v2.yml",
    ".github/scripts/prepare_actions_security_commit.py",
}


def api_request(method: str, url: str, token: str, payload=None):
    data = None if payload is None else json.dumps(payload).encode("utf-8")
    request = urllib.request.Request(
        url,
        data=data,
        method=method,
        headers={
            "Accept": "application/vnd.github+json",
            "Authorization": f"Bearer {token}",
            "X-GitHub-Api-Version": "2022-11-28",
            "User-Agent": "missionchief-toolkit-actions-security",
            "Content-Type": "application/json",
        },
    )
    try:
        with urllib.request.urlopen(request, timeout=60) as response:
            return json.load(response)
    except urllib.error.HTTPError as error:
        body = error.read().decode("utf-8", errors="replace")
        raise RuntimeError(f"{method} {url} -> HTTP {error.code}\n{body}") from error


def main() -> int:
    token = os.environ["GH_TOKEN"]
    repository = os.environ["REPOSITORY"]
    parent = os.environ["PARENT_SHA"]
    api = f"https://api.github.com/repos/{repository}"
    changed: list[Path] = []

    for path in sorted(Path(".github/workflows").glob("*.y*ml")):
        if path.as_posix() in TEMPORARY:
            continue
        text = path.read_text(encoding="utf-8")
        updated = text
        for old, new in REPLACEMENTS.items():
            updated = updated.replace(old, new)
        if updated != text:
            path.write_text(updated, encoding="utf-8")
            changed.append(path)

    if not changed:
        raise RuntimeError("No permanent workflow references required pinning.")

    commit = api_request("GET", f"{api}/git/commits/{parent}", token)
    base_tree = commit["tree"]["sha"]
    entries = []
    for path in changed:
        blob = api_request(
            "POST",
            f"{api}/git/blobs",
            token,
            {
                "content": base64.b64encode(path.read_bytes()).decode("ascii"),
                "encoding": "base64",
            },
        )
        entries.append(
            {"path": path.as_posix(), "mode": "100644", "type": "blob", "sha": blob["sha"]}
        )

    for raw in sorted(TEMPORARY):
        entries.append({"path": raw, "mode": "100644", "type": "blob", "sha": None})

    tree = api_request(
        "POST",
        f"{api}/git/trees",
        token,
        {"base_tree": base_tree, "tree": entries},
    )
    created = api_request(
        "POST",
        f"{api}/git/commits",
        token,
        {
            "message": "Pin GitHub Actions and add supply-chain controls",
            "tree": tree["sha"],
            "parents": [parent],
        },
    )
    Path("prepared-commit-sha.txt").write_text(created["sha"] + "\n", encoding="utf-8")
    Path("prepared-parent-sha.txt").write_text(parent + "\n", encoding="utf-8")
    Path("prepared-tree-sha.txt").write_text(tree["sha"] + "\n", encoding="utf-8")
    Path("changed-workflows.txt").write_text(
        "\n".join(path.as_posix() for path in changed) + "\n", encoding="utf-8"
    )
    print(json.dumps({"parent": parent, "tree": tree["sha"], "commit": created["sha"]}, indent=2))
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except Exception as error:
        Path("prepare-error.txt").write_text(str(error) + "\n", encoding="utf-8")
        print(error, file=sys.stderr)
        raise SystemExit(0)
