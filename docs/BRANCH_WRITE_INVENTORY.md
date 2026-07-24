# Protected-branch write inventory

**Reviewed:** 24 July 2026  
**Reviewed `main`:** `bfd3a786a17a2cf01a0aa0d3d6f9a3f235ab1f2c`  
**Issue:** #41 — Migrate release state for strict main-branch protection

## Current conclusion

Strict pull-request-only protection is **not yet safe to enable**.

The repository has ten workflows that can commit directly to public `main`. Two additional release workflows do not push themselves, but invoke the reusable production workflow that does. The direct writes are deliberate and guarded, but they mix canonical source, generated distribution, release state, announcement state, audit output and human-readable dashboards in one protected branch.

This document is an inventory, not an authorization to add more bypasses. `.github/branch-write-inventory.json` is the machine-readable authority and `.github/scripts/test_branch_write_inventory.py` prevents unclassified write paths from being introduced.

## Direct public `main` writers

| Workflow | Trigger | Current mutation | Credential / actor | Required migration |
|---|---|---|---|---|
| `validate-userscript.yml` | validated `main` push or manual run | `dist/`, candidate dashboard JSON and generated dashboard Markdown | `github.token` / `github-actions[bot]` | Move generated candidate state outside protected `main`. |
| `greasyfork-release-monitor.yml` | five-minute schedule or manual run | `.github/greasyfork-version.txt` | `github.token` / `github-actions[bot]` | Move announcement state to a release-state branch. |
| `import-canonical-userscript.yml` | manual run or workflow-definition push | canonical userscript and source baseline | `github.token` / `github-actions[bot]` | Convert to an owner-created PR and retire when GitHub remains authoritative. |
| `publish-update-manifest.yml` | release-dispatched manual run | `status/update-manifest.json` | `github.token` / `github-actions[bot]` | Publish from a release-state branch or immutable release asset. |
| `reconcile-release-announcement-state.yml` | successful release completion or manual run | `.github/greasyfork-version.txt` | `github.token` / `github-actions[bot]` | Move announcement state to a release-state branch. |
| `release-recovery.yml` | explicitly confirmed manual recovery | dashboard JSON/Markdown and announcement tracker | `github.token` / `github-actions[bot]` | Keep release-object repair in the API; move mutable state to the release-state branch. |
| `release-toolkit-dry-run.yml` | manual run | dry-run dashboard state | `github.token` / `github-actions[bot]` | Make dry runs artifact-only. |
| `release-toolkit.yml` | reusable release call or manual run | stable root userscript mirrors and final release dashboard | `github.token` / `github-actions[bot]` | Move mirrors to a distribution branch and state to a release-state branch under a scoped GitHub App. |
| `repository-audit.yml` | relevant `main` push or manual run | repository audit reports and dashboard state | `github.token` / `github-actions[bot]` | Retain reports as artifacts and publish only summary state outside protected `main`. |
| `update-release-dashboard.yml` | dashboard change or manual run | generated `status/README.md` | `github.token` / `github-actions[bot]` | Generate at Pages/deployment time or from the release-state branch. |

### Production release write sequence

The production release currently performs multiple branch mutations:

1. `validate-userscript.yml` commits the validated distribution candidate.
2. `release-toolkit.yml` calls `sync_greasyfork_root_mirror.sh`, which commits stable root mirrors.
3. `release-toolkit.yml` publishes the GitHub Release, verifies Greasy Fork, backs up privately and posts Discord.
4. `release-toolkit.yml` commits the verified release dashboard.
5. `release-toolkit.yml` dispatches `publish-update-manifest.yml`, which commits the stable update manifest.
6. Dashboard and announcement reconciliation workflows may create further generated-state commits.

Strict protection must preserve this sequencing without permitting unrestricted human-token pushes or leaving the release ledger split between branches and external channels.

## Indirect release orchestrators

These workflows hold or request `contents: write` authority but contain no direct public-`main` push:

| Workflow | Delegated writer | Role |
|---|---|---|
| `auto-release-after-validation.yml` | `release-toolkit.yml` | Starts the guarded release after successful candidate validation. |
| `owner-release-command.yml` | `release-toolkit.yml` | Authorizes a manual release command and reports the result. |

Their own jobs should ultimately use read-only contents access; write authority should exist only on the called release job and its scoped GitHub App identity.

## Explicit non-public-main writers

These write paths are intentionally excluded from the public-`main` count and are machine-classified so they cannot be confused with bypasses:

| Automation | Target | Credential | Protection posture |
|---|---|---|---|
| `apply-development-package.yml` | Existing owner-created PR branch | `DEVELOPMENT_PR_TOKEN` | Review branch only; cannot create or update public `main`. |
| `prepare-release-rollback.yml` | New recovery branch and PR | `DEVELOPMENT_PR_TOKEN` | Review branch only; public release still requires merge and release gates. |
| `backup_release_to_private_repo.sh` | `Conroy1988/missionchief-map-command-toolkit-private` `main` | `MIGRATION_REPO_TOKEN` | Separate recovery repository; not a public-repository bypass. |

## Target architecture

### Canonical protected branch

Public `main` should contain only reviewed source, workflows, policies, deterministic tests, documentation and stable configuration. Human changes should arrive through pull requests with required checks and resolved conversations.

### Distribution branch

A dedicated automation-owned branch should contain the stable root mirrors required by Greasy Fork or equivalent external distribution tooling. Only the release GitHub App should be able to update it.

### Release-state branch

Mutable operational records should move together:

- release dashboard JSON;
- human-readable dashboard output;
- stable update manifest;
- Greasy Fork/Discord announcement tracker;
- repository audit summaries;
- recovery claim and completion state.

The state branch must be reconstructed deterministically from immutable release evidence and must never become a competing source for product code.

### Immutable evidence

Release bundles, checksums, changelog extracts and recovery handovers should remain GitHub Release assets and workflow artifacts. Dry-run output should be artifact-only.

### Automation identity

The final writer should be a narrowly scoped GitHub App with explicit repository permissions. Personal tokens remain appropriate only for owner-created review branches and the separate private recovery repository.

## Migration order

1. ✅ Inventory every public-`main` writer and enforce the inventory in CI.
2. Separate generated candidate, dashboard, manifest, tracker and audit state from canonical source.
3. Move stable Greasy Fork mirrors to a dedicated distribution branch.
4. Introduce a narrowly scoped GitHub App for distribution and release-state writes.
5. Rehearse normal release and every recovery operation without public-`main` mutation.
6. Configure required pull requests, required checks, current-branch enforcement and conversation resolution.
7. Enable strict protection only after all rehearsals pass.

## Stage-one exit criteria

Stage one is complete when:

- every workflow with `contents: write` authority is classified;
- every executable public-`main` push source is listed;
- private-repository and review-branch writers are explicitly separated;
- CI fails when a new writer, write-capable workflow or hidden main-ref mutation appears;
- strict branch protection remains disabled pending later migration stages.
