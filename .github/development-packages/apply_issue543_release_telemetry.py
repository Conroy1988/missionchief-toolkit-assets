#!/usr/bin/env python3
"""Execute the reviewed Issue #543 package with its release-env anchor narrowed."""
from __future__ import annotations

import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
PACKAGE = ".github/development-packages/apply_issue543_release_telemetry.py"
previous = subprocess.check_output(
    ["git", "show", f"HEAD^:{PACKAGE}"],
    cwd=ROOT,
    text=True,
)
old = '''release = replace_once(
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
'''
new = '''release = replace_once(
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
'''
if previous.count(old) != 1:
    raise RuntimeError(f"reviewed package anchor count changed: {previous.count(old)}")
corrected = previous.replace(old, new, 1)
runtime = ROOT / ".github/development-packages/.apply_issue543_release_telemetry_runtime.py"
runtime.write_text(corrected, encoding="utf-8")
try:
    subprocess.run([sys.executable, str(runtime)], cwd=ROOT, check=True)
finally:
    runtime.unlink(missing_ok=True)
