#!/usr/bin/env python3
from __future__ import annotations

import base64
import json
import os
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


def create_blob(api: str, token: str, path: Path) -> str:
    payload = json.dumps({
        "content": base64.b64encode(path.read_bytes()).decode("ascii"),
        "encoding": "base64",
    }).encode("utf-8")
    request = urllib.request.Request(
        f"{api}/git/blobs",
        data=payload,
        method="POST",
        headers={
            "Accept": "application/vnd.github+json",
            "Authorization": f"Bearer {token}",
            "X-GitHub-Api-Version": "2022-11-28",
            "User-Agent": "missionchief-toolkit-actions-security",
            "Content-Type": "application/json",
        },
    )
    with urllib.request.urlopen(request, timeout=60) as response:
        return json.load(response)["sha"]


def main() -> int:
    token = os.environ["GH_TOKEN"]
    repository = os.environ["REPOSITORY"]
    api = f"https://api.github.com/repos/{repository}"
    blobs: dict[str, str] = {}

    for path in sorted(Path(".github/workflows").glob("*.y*ml")):
        if path.as_posix() in TEMPORARY:
            continue
        text = path.read_text(encoding="utf-8")
        updated = text
        for old, new in REPLACEMENTS.items():
            updated = updated.replace(old, new)
        if updated == text:
            continue
        path.write_text(updated, encoding="utf-8")
        blobs[path.as_posix()] = create_blob(api, token, path)

    if not blobs:
        raise RuntimeError("No permanent workflow references required pinning.")

    Path("prepared-workflow-blobs.json").write_text(
        json.dumps(blobs, indent=2, sort_keys=True) + "\n", encoding="utf-8"
    )
    Path("changed-workflows.txt").write_text(
        "\n".join(sorted(blobs)) + "\n", encoding="utf-8"
    )
    print(json.dumps(blobs, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
