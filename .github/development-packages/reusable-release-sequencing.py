#!/usr/bin/env python3
from pathlib import Path
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[2]
OWNER = ROOT / ".github" / "workflows" / "owner-release-command.yml"
READINESS = ROOT / ".github" / "workflows" / "release-readiness-check.yml"
RELEASE = ROOT / ".github" / "workflows" / "release-toolkit.yml"


def replace_once(text: str, old: str, new: str, label: str) -> str:
    count = text.count(old)
    if count != 1:
        raise AssertionError(f"{label}: expected one match, found {count}")
    return text.replace(old, new, 1)


readiness = READINESS.read_text(encoding="utf-8")
readiness_header = '''on:
  workflow_dispatch:
    inputs:
      version:
        description: "Toolkit version to validate without publishing"
        required: true
        default: "4.10.4"
        type: string
'''
readiness_reusable_header = '''on:
  workflow_call:
    inputs:
      version:
        description: "Toolkit version to validate without publishing"
        required: true
        type: string
    secrets:
      DISCORD_RELEASE_WEBHOOK:
        required: true
      MIGRATION_REPO_TOKEN:
        required: true
  workflow_dispatch:
    inputs:
      version:
        description: "Toolkit version to validate without publishing"
        required: true
        default: "4.10.4"
        type: string
'''
readiness = replace_once(readiness, readiness_header, readiness_reusable_header, "readiness trigger")
READINESS.write_text(readiness, encoding="utf-8")

release = RELEASE.read_text(encoding="utf-8")
release_header = '''on:
  workflow_dispatch:
    inputs:
      version:
        description: "Validated Toolkit version to publish"
        required: true
        type: string
      confirmation:
        description: "Type RELEASE to confirm a public release"
        required: true
        type: string
'''
release_reusable_header = '''on:
  workflow_call:
    inputs:
      version:
        description: "Validated Toolkit version to publish"
        required: true
        type: string
      confirmation:
        description: "Type RELEASE to confirm a public release"
        required: true
        type: string
    secrets:
      DISCORD_RELEASE_WEBHOOK:
        required: true
      MIGRATION_REPO_TOKEN:
        required: true
  workflow_dispatch:
    inputs:
      version:
        description: "Validated Toolkit version to publish"
        required: true
        type: string
      confirmation:
        description: "Type RELEASE to confirm a public release"
        required: true
        type: string
'''
release = replace_once(release, release_header, release_reusable_header, "production trigger")
RELEASE.write_text(release, encoding="utf-8")

owner = '''name: Owner Release Command

on:
  issue_comment:
    types: [created]

permissions:
  actions: write
  contents: write
  issues: write

concurrency:
  group: toolkit-owner-release-command
  cancel-in-progress: false

jobs:
  authorize:
    name: Authorize and validate owner release command
    if: >-
      github.event.issue.pull_request == null &&
      startsWith(github.event.comment.body, '/release-toolkit ')
    runs-on: ubuntu-latest
    timeout-minutes: 10
    outputs:
      version: ${{ steps.command.outputs.version }}

    steps:
      - name: Authorize owner command
        id: command
        env:
          COMMENT_BODY: ${{ github.event.comment.body }}
          COMMENT_AUTHOR: ${{ github.event.comment.user.login }}
          AUTHOR_ASSOCIATION: ${{ github.event.comment.author_association }}
        shell: bash
        run: |
          set -euo pipefail
          [[ "$COMMENT_AUTHOR" == "Conroy1988" ]] || { echo "::error::Only Conroy1988 may dispatch a production release."; exit 1; }
          [[ "$AUTHOR_ASSOCIATION" == "OWNER" ]] || { echo "::error::Release command author is not the repository owner."; exit 1; }
          if [[ "$COMMENT_BODY" =~ ^/release-toolkit[[:space:]]+([0-9]+\.[0-9]+\.[0-9]+([+-][0-9A-Za-z.-]+)?)[[:space:]]+RELEASE[[:space:]]*$ ]]; then
            VERSION="${BASH_REMATCH[1]}"
          else
            echo "::error::Expected: /release-toolkit X.Y.Z RELEASE"
            exit 1
          fi
          echo "version=$VERSION" >> "$GITHUB_OUTPUT"

      - name: Check out current main
        uses: actions/checkout@9c091bb21b7c1c1d1991bb908d89e4e9dddfe3e0 # v7
        with:
          ref: main
          fetch-depth: 1
          persist-credentials: false

      - name: Verify requested version is a validated candidate
        env:
          VERSION: ${{ steps.command.outputs.version }}
        shell: bash
        run: |
          set -euo pipefail
          SOURCE="src/MissionChief_Map_Command_Toolkit.user.js"
          grep -Eq "^//[[:space:]]*@version[[:space:]]+${VERSION//./\.}[[:space:]]*$" "$SOURCE"
          test "$(jq -r '.currentVersion' status/release-dashboard.json)" = "$VERSION"
          test "$(jq -r '.status.validation' status/release-dashboard.json)" = "passed"
          test "$(jq -r '.distributionCandidate.version' status/release-dashboard.json)" = "$VERSION"
          test "$(jq -r '.distributionCandidate.state' status/release-dashboard.json)" = "validated"

      - name: Record guarded release start
        env:
          GH_TOKEN: ${{ github.token }}
          VERSION: ${{ steps.command.outputs.version }}
          ISSUE_NUMBER: ${{ github.event.issue.number }}
        shell: bash
        run: |
          gh issue comment "$ISSUE_NUMBER" --body "Toolkit v${VERSION} passed owner authorization and candidate validation. The native reusable release-readiness workflow is starting; production cannot begin unless it succeeds. Owner-command run: \`${GITHUB_RUN_ID}\`."

  readiness:
    name: Run mandatory release readiness
    needs: authorize
    permissions:
      actions: write
      contents: read
    uses: ./.github/workflows/release-readiness-check.yml
    with:
      version: ${{ needs.authorize.outputs.version }}
    secrets: inherit

  production:
    name: Run guarded production release
    needs: [authorize, readiness]
    permissions:
      actions: write
      contents: write
    uses: ./.github/workflows/release-toolkit.yml
    with:
      version: ${{ needs.authorize.outputs.version }}
      confirmation: RELEASE
    secrets: inherit

  report:
    name: Record owner release result
    needs: [authorize, readiness, production]
    if: always() && needs.authorize.result == 'success'
    runs-on: ubuntu-latest
    timeout-minutes: 5

    steps:
      - name: Record verified completion
        if: needs.readiness.result == 'success' && needs.production.result == 'success'
        env:
          GH_TOKEN: ${{ github.token }}
          VERSION: ${{ needs.authorize.outputs.version }}
          ISSUE_NUMBER: ${{ github.event.issue.number }}
        shell: bash
        run: |
          gh issue comment "$ISSUE_NUMBER" --body "Toolkit v${VERSION} completed mandatory readiness and the guarded production release as native reusable workflows in Actions run \`${GITHUB_RUN_ID}\`. GitHub Release, Greasy Fork verification, private backup, Discord publication, dashboard reconciliation, stable manifest publication and documentation deployment are owned by the completed production workflow."

      - name: Record guarded failure
        if: needs.readiness.result != 'success' || needs.production.result != 'success'
        env:
          GH_TOKEN: ${{ github.token }}
          VERSION: ${{ needs.authorize.outputs.version }}
          ISSUE_NUMBER: ${{ github.event.issue.number }}
          READINESS_RESULT: ${{ needs.readiness.result }}
          PRODUCTION_RESULT: ${{ needs.production.result }}
        shell: bash
        run: |
          gh issue comment "$ISSUE_NUMBER" --body "Toolkit v${VERSION} release stopped fail-closed. Readiness result: \`${READINESS_RESULT}\`; production result: \`${PRODUCTION_RESULT}\`. No safeguard was bypassed. Diagnostics: ${GITHUB_SERVER_URL}/${GITHUB_REPOSITORY}/actions/runs/${GITHUB_RUN_ID}"
'''
OWNER.write_text(owner, encoding="utf-8")

for path in (OWNER, READINESS, RELEASE):
    text = path.read_text(encoding="utf-8")
    if "\t" in text:
        raise AssertionError(f"tab indentation found in {path}")
    if not text.endswith("\n"):
        raise AssertionError(f"missing final newline in {path}")

owner_text = OWNER.read_text(encoding="utf-8")
readiness_text = READINESS.read_text(encoding="utf-8")
release_text = RELEASE.read_text(encoding="utf-8")
assert "uses: ./.github/workflows/release-readiness-check.yml" in owner_text
assert "uses: ./.github/workflows/release-toolkit.yml" in owner_text
assert "needs: [authorize, readiness]" in owner_text
assert "confirmation: RELEASE" in owner_text
assert owner_text.index("uses: ./.github/workflows/release-readiness-check.yml") < owner_text.index("uses: ./.github/workflows/release-toolkit.yml")
assert "gh workflow run release-readiness-check.yml" not in owner_text
assert "actions/workflows/release-readiness-check.yml/dispatches" not in owner_text
assert "workflow_call:" in readiness_text and "workflow_dispatch:" in readiness_text
assert "workflow_call:" in release_text and "workflow_dispatch:" in release_text
assert "DISCORD_RELEASE_WEBHOOK:" in readiness_text and "MIGRATION_REPO_TOKEN:" in readiness_text
assert "DISCORD_RELEASE_WEBHOOK:" in release_text and "MIGRATION_REPO_TOKEN:" in release_text

subprocess.run([sys.executable, ".github/scripts/audit_action_security.py"], cwd=ROOT, check=True)
subprocess.run([sys.executable, ".github/scripts/validate_userscript.py"], cwd=ROOT, check=True)
subprocess.run(["node", "--check", "src/MissionChief_Map_Command_Toolkit.user.js"], cwd=ROOT, check=True)
subprocess.run(["cmp", "--silent", "dist/MissionChief_Map_Command_Toolkit.user.js", "dist/MissionChief_Map_Command_Toolkit.txt"], cwd=ROOT, check=True)
print("Reusable release sequencing validated")
