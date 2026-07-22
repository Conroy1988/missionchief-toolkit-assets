#!/usr/bin/env python3
from __future__ import annotations

from pathlib import Path
import shutil

ROOT = Path(__file__).resolve().parents[2]
VALIDATOR = ROOT / ".github" / "scripts" / "validate_userscript.py"

text = VALIDATOR.read_text(encoding="utf-8")


def replace_once(old: str, new: str, label: str) -> None:
    global text
    count = text.count(old)
    if count != 1:
        raise RuntimeError(f"{label}: expected one anchor, found {count}")
    text = text.replace(old, new, 1)


replace_once(
    "import hashlib\nimport json\nimport re\nimport subprocess\nimport sys\nimport tempfile\n",
    "import hashlib\nimport json\nimport os\nimport re\nimport shutil\nimport subprocess\nimport sys\nimport tempfile\n",
    "validator imports",
)

replace_once(
    "ROOT = Path(__file__).resolve().parents[2]\nSOURCE = ROOT / \"src\" / \"MissionChief_Map_Command_Toolkit.user.js\"\n",
    """ROOT = Path(__file__).resolve().parents[2]
os.environ["PYTHONDONTWRITEBYTECODE"] = "1"
sys.dont_write_bytecode = True
SOURCE = ROOT / "src" / "MissionChief_Map_Command_Toolkit.user.js"
""",
    "validator bytecode environment",
)

replace_once(
    """def fail(message: str) -> None:
    raise SystemExit(f"VALIDATION ERROR: {message}")


def sha256(path: Path) -> str:
""",
    """def fail(message: str) -> None:
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
""",
    "validator cleanup function",
)

replace_once(
    """if __name__ == "__main__":
    raise SystemExit(main())
""",
    """if __name__ == "__main__":
    try:
        raise SystemExit(main())
    finally:
        cleanup_repository_bytecode()
""",
    "validator final cleanup",
)

VALIDATOR.write_text(text, encoding="utf-8")

# Remove currently tracked/generated caches before the outer guard invokes the
# updated validator. The validator's finally block will remove any child-process
# caches created during that subsequent validation pass.
for cache_dir in sorted(ROOT.rglob("__pycache__"), reverse=True):
    if ".git" not in cache_dir.parts:
        shutil.rmtree(cache_dir, ignore_errors=True)
for suffix in ("*.pyc", "*.pyo"):
    for bytecode in ROOT.rglob(suffix):
        if ".git" not in bytecode.parts:
            bytecode.unlink(missing_ok=True)

if "PYTHONDONTWRITEBYTECODE" not in text or "cleanup_repository_bytecode()" not in text:
    raise RuntimeError("validator bytecode hygiene contract was not installed")
print("Hardened canonical validator against repository-local Python bytecode artefacts.")
