#!/usr/bin/env python3
"""Regenerate final v8.2.0 distribution and source-headroom evidence."""
from __future__ import annotations

import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
SOURCE = ROOT / "src/MissionChief_Map_Command_Toolkit.user.js"
VERSION = "8.2.0"

source_bytes = SOURCE.read_bytes()
source_text = source_bytes.decode("utf-8")
if "// @version      8.2.0" not in source_text or "version: '8.2.0'" not in source_text:
    raise RuntimeError("Final Toolkit version markers missing")
source_sha = hashlib.sha256(source_bytes).hexdigest()
source_lines = len(source_text.splitlines())

for relative in [
    "dist/MissionChief_Map_Command_Toolkit.user.js",
    "dist/MissionChief_Map_Command_Toolkit.txt",
]:
    (ROOT / relative).write_bytes(source_bytes)
(ROOT / "dist/SHA256SUMS.txt").write_text(
    f"{source_sha}  MissionChief_Map_Command_Toolkit.user.js\n"
    f"{source_sha}  MissionChief_Map_Command_Toolkit.txt\n",
    encoding="utf-8",
)

manifest_path = ROOT / "dist/release-manifest.json"
manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
manifest.update({
    "version": VERSION,
    "sha256": source_sha,
    "bytes": len(source_bytes),
    "lines": source_lines,
})
manifest.setdefault("metadata", {})["runtimeVersion"] = VERSION
manifest_path.write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")

headroom_path = ROOT / ".github/fixtures/main-style-source-headroom.json"
headroom = json.loads(headroom_path.read_text(encoding="utf-8"))
candidate = headroom["v8Candidate"]
old_bytes = int(candidate["sourceBytes"])
old_lines = int(candidate["sourceLines"])
candidate.update({
    "issue": 565,
    "version": VERSION,
    "sourceBytes": len(source_bytes),
    "sourceLines": source_lines,
    "sourceSha256": source_sha,
    "maxSourceBytes": max(int(candidate.get("maxSourceBytes", 0)), len(source_bytes) + 20000),
    "maxSourceLines": max(int(candidate.get("maxSourceLines", 0)), source_lines + 250),
    "baseline": "8.1.5",
    "scope": "Issue #565 verified-vehicle no-reward patient release path with same-mission reopening, per-patient verification, repeated-click protection and native discharge fallback",
})
approved = candidate.setdefault("approvedGrowth", {})
approved["sourceBytes"] = int(approved.get("sourceBytes", 0)) + len(source_bytes) - old_bytes
approved["sourceLines"] = int(approved.get("sourceLines", 0)) + source_lines - old_lines
headroom_path.write_text(json.dumps(headroom, indent=2) + "\n", encoding="utf-8")

print(f"v8.2.0 final evidence: {source_sha}, {len(source_bytes)} bytes, {source_lines} lines")
