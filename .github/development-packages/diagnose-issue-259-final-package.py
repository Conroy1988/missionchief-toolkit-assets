#!/usr/bin/env python3
from __future__ import annotations

import shutil
import subprocess
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
REPORT = ROOT / "docs/issue-259-package-diagnostic.md"


def main() -> None:
    with tempfile.TemporaryDirectory(prefix="issue-259-") as temp_dir:
        workspace = Path(temp_dir) / "repo"
        shutil.copytree(
            ROOT,
            workspace,
            ignore=shutil.ignore_patterns(".git", "__pycache__", "*.pyc"),
        )
        package = workspace / ".github/development-packages/finalise-issue-259-v4.20.13-corrected.py"
        completed = subprocess.run(
            ["python3", str(package)],
            cwd=workspace,
            text=True,
            capture_output=True,
            timeout=240,
        )
        stdout = completed.stdout[-18000:]
        stderr = completed.stderr[-18000:]
        REPORT.write_text(
            "# Issue #259 final-package diagnostic\n\n"
            "The reviewed v4.20.13 package was executed in an isolated temporary copy. "
            "No production or real branch runtime file was changed by this diagnostic.\n\n"
            f"- Return code: `{completed.returncode}`\n\n"
            "## Standard output\n\n```text\n"
            + stdout
            + "\n```\n\n## Standard error\n\n```text\n"
            + stderr
            + "\n```\n",
            encoding="utf-8",
        )


if __name__ == "__main__":
    main()
