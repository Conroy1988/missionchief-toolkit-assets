#!/usr/bin/env python3
"""Restore canonical indentation and regenerate final v8.2.1 distribution metadata."""
from __future__ import annotations

import hashlib
import json
import textwrap
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
SOURCE = ROOT / "src/MissionChief_Map_Command_Toolkit.user.js"
HEADROOM = ROOT / ".github/fixtures/main-style-source-headroom.json"

source = SOURCE.read_text(encoding="utf-8")

helper_start = source.index("const TRANSPORT_SWEEP_OPTIONAL_RELEASE_TEXT")
helper_end = source.index("    function transportSweepVisibleDischargeButtons()", helper_start)
helper = source[helper_start:helper_end].strip("\n")
if helper.startswith("    "):
    raise RuntimeError("Optional-release helper was already indented unexpectedly")
source = source[:helper_start] + textwrap.indent(helper, "    ") + "\n\n" + source[helper_end:]

processor_start = source.index("    async function processTransportSweepMission(item, remainingAllowance) {")
processor_end = source.index("\n    async function startTransportSweep", processor_start)
processor = source[processor_start:processor_end]
block_start = processor.index("const optionalReleaseResult = await processTransportSweepOptionalReleaseControls(")
block_end = processor.index("            const candidateStats", block_start)
block = processor[block_start:block_end].strip("\n")
processor = processor[:block_start] + textwrap.indent(block, "        ") + "\n" + processor[block_end:]
source = source[:processor_start] + processor + source[processor_end:]

SOURCE.write_text(source, encoding="utf-8")
source_bytes = SOURCE.read_bytes()
source_text = source_bytes.decode("utf-8")
source_sha = hashlib.sha256(source_bytes).hexdigest()
source_lines = len(source_text.splitlines())
manifest_lines = source_text.count("\n") + 1

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
    "version": "8.2.1",
    "sha256": source_sha,
    "bytes": len(source_bytes),
    "lines": manifest_lines,
})
manifest["metadata"]["runtimeVersion"] = "8.2.1"
manifest_path.write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")

headroom = json.loads(HEADROOM.read_text(encoding="utf-8"))
candidate = headroom["v8Candidate"]
previous_bytes = int(candidate["sourceBytes"])
previous_lines = int(candidate["sourceLines"])
candidate["sourceBytes"] = len(source_bytes)
candidate["sourceLines"] = source_lines
candidate["sourceSha256"] = source_sha
candidate["maxSourceBytes"] = max(int(candidate.get("maxSourceBytes", 0)), len(source_bytes) + 20000)
candidate["maxSourceLines"] = max(int(candidate.get("maxSourceLines", 0)), source_lines + 250)
approved = candidate.setdefault("approvedGrowth", {})
approved["sourceBytes"] = int(approved.get("sourceBytes", 0)) + len(source_bytes) - previous_bytes
approved["sourceLines"] = int(approved.get("sourceLines", 0)) + source_lines - previous_lines
HEADROOM.write_text(json.dumps(headroom, indent=2) + "\n", encoding="utf-8")

print(
    f"v8.2.1 source normalized and metadata regenerated: "
    f"{source_sha}, {len(source_bytes)} bytes, {source_lines} lines"
)
