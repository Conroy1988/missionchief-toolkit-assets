#!/usr/bin/env python3
"""Restore canonical indentation after applying the v8.2.1 hotfix package."""
from __future__ import annotations

import textwrap
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
SOURCE = ROOT / "src/MissionChief_Map_Command_Toolkit.user.js"

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
print("v8.2.1 generated source indentation normalized.")
