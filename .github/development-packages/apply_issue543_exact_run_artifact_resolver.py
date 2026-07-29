#!/usr/bin/env python3
"""Issue #543: resolve the sole candidate artifact from the exact successful run."""
from __future__ import annotations

import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]


def read(path: str) -> str:
    return (ROOT / path).read_text(encoding="utf-8")


def write(path: str, value: str) -> None:
    (ROOT / path).write_text(value, encoding="utf-8")


def replace_once(value: str, old: str, new: str, label: str) -> str:
    count = value.count(old)
    if count != 1:
        raise RuntimeError(f"{label}: expected one match, found {count}")
    return value.replace(old, new, 1)


auto_path = ".github/workflows/auto-release-after-validation.yml"
auto = read(auto_path)
old_resolver = '''          gh api "repos/${GITHUB_REPOSITORY}/actions/runs/${VALIDATION_RUN_ID}/artifacts" > /tmp/validation-artifacts.json
          ARTIFACT_NAME="missionchief-toolkit-validation-candidate-${PR_HEAD_SHA}"
          ARTIFACT_ID="$(jq -r --arg name "$ARTIFACT_NAME" \\
            '[.artifacts[]
              | select(.expired == false)
              | select(.name == $name)]
             | sort_by(.created_at)
             | last
             | .id // empty' \\
            /tmp/validation-artifacts.json)"

          if [[ -z "$ARTIFACT_ID" ]]; then
            echo "Exact PR validation artifact is unavailable; dispatching guarded main fallback."
            gh workflow run validate-userscript.yml --ref main
            exit 0
          fi
'''
new_resolver = '''          gh api "repos/${GITHUB_REPOSITORY}/actions/runs/${VALIDATION_RUN_ID}/artifacts" > /tmp/validation-artifacts.json
          CANDIDATE_ARTIFACT_COUNT="$(jq -r '
            [.artifacts[]
              | select(.expired == false)
              | select(.name | startswith("missionchief-toolkit-validation-candidate-"))]
            | length' /tmp/validation-artifacts.json)"
          if [[ "$CANDIDATE_ARTIFACT_COUNT" != "1" ]]; then
            echo "Expected exactly one non-expired validation candidate artifact in exact run ${VALIDATION_RUN_ID}; found ${CANDIDATE_ARTIFACT_COUNT}. Dispatching guarded main fallback."
            gh workflow run validate-userscript.yml --ref main
            exit 0
          fi
          ARTIFACT_ID="$(jq -r '
            [.artifacts[]
              | select(.expired == false)
              | select(.name | startswith("missionchief-toolkit-validation-candidate-"))]
            | .[0].id' /tmp/validation-artifacts.json)"
          ARTIFACT_NAME="$(jq -r '
            [.artifacts[]
              | select(.expired == false)
              | select(.name | startswith("missionchief-toolkit-validation-candidate-"))]
            | .[0].name' /tmp/validation-artifacts.json)"
          [[ "$ARTIFACT_ID" =~ ^[0-9]+$ && "$ARTIFACT_NAME" == missionchief-toolkit-validation-candidate-* ]] || {
            echo "::error::Exact-run candidate artifact metadata is invalid."
            exit 1
          }
          echo "Resolved ${ARTIFACT_NAME} from exact successful run ${VALIDATION_RUN_ID}; embedded evidence will authorize PR head, PR number and repository tree."
'''
auto = replace_once(auto, old_resolver, new_resolver, "exact-run candidate artifact resolver")
write(auto_path, auto)

pipeline_path = ".github/scripts/test_release_pipeline_v4.py"
pipeline = read(pipeline_path)
pipeline = replace_once(
    pipeline,
    '''assert 'ARTIFACT_NAME="missionchief-toolkit-validation-candidate-${PR_HEAD_SHA}"' in a
assert 'select(.name == $name)' in a
''',
    '''assert 'CANDIDATE_ARTIFACT_COUNT' in a
assert 'startswith("missionchief-toolkit-validation-candidate-")' in a
assert 'Expected exactly one non-expired validation candidate artifact in exact run' in a
assert '[[ "$EVIDENCE_HEAD" == "$PR_HEAD_SHA" ]]' in a
assert '[[ "$EVIDENCE_PR" == "$PR_NUMBER" ]]' in a
assert 'ARTIFACT_NAME="missionchief-toolkit-validation-candidate-${PR_HEAD_SHA}"' not in a
''',
    "Pipeline v4 artifact resolver contract",
)
write(pipeline_path, pipeline)

candidate_path = ".github/scripts/test_validation_candidate_pipeline.py"
candidate = read(candidate_path)
candidate = replace_once(
    candidate,
    '''        'ARTIFACT_NAME="missionchief-toolkit-validation-candidate-${PR_HEAD_SHA}"',
        "select(.name == $name)",
''',
    '''        "CANDIDATE_ARTIFACT_COUNT",
        'startswith("missionchief-toolkit-validation-candidate-")',
        "Expected exactly one non-expired validation candidate artifact in exact run",
        '[[ "$EVIDENCE_HEAD" == "$PR_HEAD_SHA" ]]',
        '[[ "$EVIDENCE_PR" == "$PR_NUMBER" ]]',
''',
    "validation candidate exact-run markers",
)
candidate = replace_once(
    candidate,
    '''        '-f branch="$PR_HEAD_REF"',
''',
    '''        '-f branch="$PR_HEAD_REF"',
        'ARTIFACT_NAME="missionchief-toolkit-validation-candidate-${PR_HEAD_SHA}"',
''',
    "validation candidate forbidden exact-name assumption",
)
candidate = replace_once(
    candidate,
    '''        "Validation candidate pipeline passed: exact-head/exact-artifact PR-tree promotion, "
''',
    '''        "Validation candidate pipeline passed: exact-head/exact-run candidate-evidence PR-tree promotion, "
''',
    "validation candidate success summary",
)
write(candidate_path, candidate)

docs_path = "docs/RELEASE_PIPELINE_V4.md"
docs = read(docs_path)
docs = replace_once(
    docs,
    "Pipeline v4 builds one immutable release-ready candidate, resolves it by exact head SHA and exact artifact name, verifies it against the exact current `main` commit, reuses it without rebuilding, runs Greasy Fork verification and private backup concurrently, posts Discord only after both succeed, records timing telemetry, and dispatches GitHub Pages asynchronously.",
    "Pipeline v4 builds one immutable release-ready candidate, resolves the exact successful head run, requires exactly one non-expired candidate artifact from that run, verifies its embedded PR head, PR number and repository tree against the exact current `main` commit, reuses it without rebuilding, runs Greasy Fork verification and private backup concurrently, posts Discord only after both succeed, records timing telemetry, and dispatches GitHub Pages asynchronously.",
    "Pipeline v4 exact-run documentation",
)
docs += "\n\nThe candidate artifact filename may use GitHub's pull-request test-merge SHA. Filename suffixes are therefore not release authority; the exact successful workflow run and the candidate's embedded head/PR/tree evidence are authoritative. Zero or multiple candidate artifacts fail closed to the guarded current-`main` validation path.\n"
write(docs_path, docs)

subprocess.run([sys.executable, str(ROOT / pipeline_path)], cwd=ROOT, check=True)
subprocess.run([sys.executable, str(ROOT / candidate_path)], cwd=ROOT, check=True)
subprocess.run([sys.executable, "-m", "py_compile", str(ROOT / pipeline_path), str(ROOT / candidate_path)], cwd=ROOT, check=True)
print("Issue #543 exact-run candidate artifact resolver package applied.")
