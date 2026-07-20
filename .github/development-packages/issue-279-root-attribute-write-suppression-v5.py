#!/usr/bin/env python3
from __future__ import annotations

import subprocess
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
V4 = ROOT / ".github/development-packages/issue-279-root-attribute-write-suppression-v4.py"


def replace_once(text: str, old: str, new: str, label: str) -> str:
    count = text.count(old)
    if count != 1:
        raise RuntimeError(f"{label}: expected exactly one match, found {count}")
    return text.replace(old, new, 1)


def main() -> None:
    text = V4.read_text(encoding="utf-8")
    text = replace_once(
        text,
        "import subprocess\nimport sys\n",
        "import hashlib\nimport subprocess\nimport sys\n",
        "hashlib import",
    )
    text = replace_once(
        text,
        "    # Rebuild source-derived distribution before repository-wide parity contracts run.\n"
        "    subprocess.run([sys.executable, str(VALIDATOR)], cwd=ROOT, check=True)\n",
        "    # Pre-stage byte-identical distribution before integrity contracts assert parity.\n"
        "    raw = SOURCE.read_bytes()\n"
        "    dist = ROOT / 'dist'\n"
        "    dist.mkdir(parents=True, exist_ok=True)\n"
        "    user_js = dist / 'MissionChief_Map_Command_Toolkit.user.js'\n"
        "    text_dist = dist / 'MissionChief_Map_Command_Toolkit.txt'\n"
        "    user_js.write_bytes(raw)\n"
        "    text_dist.write_bytes(raw)\n"
        "    digest = hashlib.sha256(raw).hexdigest()\n"
        "    (dist / 'SHA256SUMS.txt').write_text(\n"
        "        f'{digest}  {user_js.name}\\n{digest}  {text_dist.name}\\n',\n"
        "        encoding='utf-8',\n"
        "    )\n"
        "    # Canonical validation independently verifies the staged files and rewrites the manifest.\n"
        "    subprocess.run([sys.executable, str(VALIDATOR)], cwd=ROOT, check=True)\n",
        "distribution pre-stage",
    )

    with tempfile.TemporaryDirectory(prefix="mcms-issue-279-v5-") as directory:
        corrected = Path(directory) / "issue-279-root-attribute-write-suppression.py"
        corrected.write_text(text, encoding="utf-8")
        subprocess.run([sys.executable, "-m", "py_compile", str(corrected)], cwd=ROOT, check=True)
        subprocess.run([sys.executable, str(corrected)], cwd=ROOT, check=True)

    V4.unlink(missing_ok=True)
    print("Applied Issue 279 candidate with pre-staged canonical distribution parity")


if __name__ == "__main__":
    main()
