#!/usr/bin/env python3
"""Execute the immutable reviewed Issue #543 package with narrow corrections."""
from __future__ import annotations

import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
PACKAGE = ".github/development-packages/apply_issue543_release_telemetry.py"
REVIEWED_PACKAGE_COMMIT = "642665cfe912496ac388f909904d7cb4d4b99b4a"
reviewed = subprocess.check_output(
    ["git", "show", f"{REVIEWED_PACKAGE_COMMIT}:{PACKAGE}"],
    cwd=ROOT,
    text=True,
)

anchor_old = """release = replace_once(
    release,
    '''          VALIDATED_SHA: ${{ inputs.validated_sha }}
          GH_TOKEN: ${{ github.token }}
''',
    '''          VALIDATED_SHA: ${{ inputs.validated_sha }}
          RELEASE_SOURCE_SHA: ${{ steps.release_start.outputs.source_sha }}
          SOURCE_PR_NUMBER: ${{ inputs.pull_request_number }}
          SOURCE_PR_CREATED_AT: ${{ inputs.pr_created_at }}
          SOURCE_PR_MERGED_AT: ${{ inputs.pr_merged_at }}
          SOURCE_IMPLEMENTATION_READY_AT: ${{ inputs.implementation_ready_at }}
          SOURCE_VALIDATION_COMPLETED_AT: ${{ inputs.validation_completed_at }}
          GH_TOKEN: ${{ github.token }}
''',
    "release telemetry environment",
)
"""
anchor_new = """release = replace_once(
    release,
    '''          DISCORD_AT: ${{ steps.discord.outputs.posted_at }}
          VALIDATED_SHA: ${{ inputs.validated_sha }}
          GH_TOKEN: ${{ github.token }}
''',
    '''          DISCORD_AT: ${{ steps.discord.outputs.posted_at }}
          VALIDATED_SHA: ${{ inputs.validated_sha }}
          RELEASE_SOURCE_SHA: ${{ steps.release_start.outputs.source_sha }}
          SOURCE_PR_NUMBER: ${{ inputs.pull_request_number }}
          SOURCE_PR_CREATED_AT: ${{ inputs.pr_created_at }}
          SOURCE_PR_MERGED_AT: ${{ inputs.pr_merged_at }}
          SOURCE_IMPLEMENTATION_READY_AT: ${{ inputs.implementation_ready_at }}
          SOURCE_VALIDATION_COMPLETED_AT: ${{ inputs.validation_completed_at }}
          GH_TOKEN: ${{ github.token }}
''',
    "release telemetry environment",
)
"""
if reviewed.count(anchor_old) != 1:
    raise RuntimeError(f"reviewed release-env anchor count changed: {reviewed.count(anchor_old)}")
corrected = reviewed.replace(anchor_old, anchor_new, 1)

corrections = (
    (
        "generated recorder newline",
        'path.write_text(json.dumps(data,indent=2)+"\\n",encoding="utf-8")',
        'path.write_text(json.dumps(data,indent=2)+"\\\\n",encoding="utf-8")',
    ),
    (
        "generated dashboard newline",
        '(root/"status/RELEASE_SPEED.md").write_text("\\n".join(lines),encoding="utf-8")',
        '(root/"status/RELEASE_SPEED.md").write_text("\\\\n".join(lines),encoding="utf-8")',
    ),
    (
        "recorder migration contract",
        """assert '"candidateCommit":a.source' in rec and "sourceSha256" not in rec""",
        """assert '"candidateCommit":a.source' in rec and 'previous["recordedCommit"]=previous.pop("sourceSha256")' in rec""",
    ),
)
for label, old, new in corrections:
    if corrected.count(old) != 1:
        raise RuntimeError(f"{label} count changed: {corrected.count(old)}")
    corrected = corrected.replace(old, new, 1)

runtime = ROOT / ".github/development-packages/.apply_issue543_release_telemetry_runtime.py"
runtime.write_text(corrected, encoding="utf-8")
try:
    subprocess.run([sys.executable, str(runtime)], cwd=ROOT, check=True)
finally:
    runtime.unlink(missing_ok=True)
