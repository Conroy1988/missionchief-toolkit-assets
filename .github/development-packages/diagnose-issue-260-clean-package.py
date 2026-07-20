#!/usr/bin/env python3
from __future__ import annotations

import shutil
import subprocess
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
REPORT = ROOT / "docs/issue-260-clean-package-diagnostic.md"


def main() -> None:
    with tempfile.TemporaryDirectory(prefix="issue-260-clean-") as temp_dir:
        workspace = Path(temp_dir) / "repo"
        shutil.copytree(ROOT, workspace, ignore=shutil.ignore_patterns(".git", "__pycache__", "*.pyc"))
        package = workspace / ".github/development-packages/fix-issue-260-v4.20.14.py"
        completed = subprocess.run(["python3", str(package)], cwd=workspace, text=True, capture_output=True, timeout=300)
        REPORT.write_text(
            "# Issue #260 clean-package diagnostic\n\n"
            f"- Return code: `{completed.returncode}`\n\n"
            "## Standard output\n\n```text\n" + completed.stdout[-40000:] + "\n```\n\n"
            "## Standard error\n\n```text\n" + completed.stderr[-40000:] + "\n```\n",
            encoding="utf-8",
        )


if __name__ == "__main__":
    main()
