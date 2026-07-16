from pathlib import Path

Path(".github/development-package-smoke.txt").write_text(
    "Issue #80 end-to-end development-package automation smoke test.\n",
    encoding="utf-8",
)
