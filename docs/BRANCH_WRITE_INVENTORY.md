# Protected-branch write inventory

**Reviewed:** 24 July 2026  
**Reviewed `main`:** `a97c830be5cdaf786aabe8d66e1c140ef6da78f0`  
**Issue:** #41 — Migrate release state for strict main-branch protection

## Current conclusion

Strict pull-request-only protection is **not yet safe to enable**.

The repository now has seven workflows that can commit directly to public `main`. Two additional release orchestrators invoke the reusable production writer but contain no direct public-main push. The remaining writes are limited to release distribution, release state, announcement state, source import and generated dashboard output.

Canonical validation, release dry runs and repository audits are now artifact-only. All three use read-only contents permission, disable persisted checkout credentials and retain immutable evidence without mutating public `main` or the production release dashboard.

`.github/branch-write-inventory.json` is the machine-readable authority. `.github/scripts/test_branch_write_inventory.py` and `.github/scripts/test_validation_candidate_pipeline.py` fail closed when a writer, permission, evidence schema or release-consumption boundary changes.

## Direct public `main` writers

| Workflow | Current mutation | Required migration |
|---|---|---|
| `greasyfork-release-monitor.yml` | `.github/greasyfork-version.txt` | Move announcement state to a release-state branch. |
| `import-canonical-userscript.yml` | canonical userscript and source baseline | Convert to an owner-created PR and retire when GitHub remains authoritative. |
| `publish-update-manifest.yml` | `status/update-manifest.json` | Publish from a release-state branch or immutable release asset. |
| `reconcile-release-announcement-state.yml` | `.github/greasyfork-version.txt` | Move announcement state to a release-state branch. |
| `release-recovery.yml` | dashboard JSON/Markdown and announcement tracker | Keep release-object repair in the API; move mutable state to the release-state branch. |
| `release-toolkit.yml` | stable `dist/`, root Greasy Fork mirrors and final release dashboard | Move distribution output to a dedicated branch and state to a release-state branch under a scoped GitHub App. |
| `update-release-dashboard.yml` | generated `status/README.md` | Generate at Pages/deployment time or from the release-state branch. |

The executable public-main push helper `.github/scripts/sync_greasyfork_root_mirror.sh` is owned by `release-toolkit.yml`. It now publishes `dist/` and the two stable root mirrors together only after release readiness has passed and the guarded production release has started.

## Artifact-only evidence workflows

| Workflow | Permission | Retained evidence | Branch effect |
|---|---|---|---|
| `validate-userscript.yml` | `contents: read` | exact commit/ref candidate JSON, userscript, text copy, checksums and release manifest | No branch or dashboard change. |
| `release-toolkit-dry-run.yml` | `contents: read` | release bundle plus versioned JSON/Markdown dry-run report | No branch or publication-channel change. |
| `repository-audit.yml` | `contents: read` | `repository-audit.json` and `.md` in `missionchief-repository-audit-<commit>` | No branch or release-dashboard change. |

Canonical validation artifacts are named `missionchief-toolkit-validation-candidate-<commit>`. The evidence records the exact source commit, source ref, version, SHA-256 and a fixed distribution inventory. The verifier rejects stale commits, mismatched hashes, altered refs and any evidence claiming a public-main or dashboard mutation.

The former committed dry-run record was stale at v4.10.4 while production was v5.0.7. The former committed repository audit described v4.13.1 and wrote a fixed `2026-07-14` timestamp into the production dashboard. The former validation workflow committed transient candidate output and release-dashboard fields before publication. All three write paths are now removed and permanently forbidden by CI.

## Production release write sequence

1. `validate-userscript.yml` validates the exact `main` commit and uploads immutable candidate evidence.
2. `auto-release-after-validation.yml` downloads the artifact from that exact successful run, verifies it and rejects a stale commit.
3. Release Readiness independently rebuilds and validates `dist/` from canonical source.
4. `release-toolkit.yml` rebuilds again and calls `.github/scripts/sync_greasyfork_root_mirror.sh` to publish stable `dist/` and root mirrors.
5. `release-toolkit.yml` publishes GitHub Release, verifies Greasy Fork, backs up privately and posts Discord.
6. `release-toolkit.yml` commits the verified release dashboard.
7. `publish-update-manifest.yml` commits the stable update manifest.
8. Dashboard and announcement reconciliation may create further generated-state commits.

The owner command does not trust persistent candidate state. It freshly validates current `main`, verifies the requested version and hash, refuses an existing release, then starts the same readiness and production workflows.

## Indirect release orchestrators

| Workflow | Delegated writer | Role |
|---|---|---|
| `auto-release-after-validation.yml` | `release-toolkit.yml` | Consumes exact immutable validation evidence, suppresses stale runs and starts the guarded release. |
| `owner-release-command.yml` | `release-toolkit.yml` | Performs owner authorization plus fresh validation, then starts the guarded release. |

Their write authority remains only because the reusable production workflow still writes distribution and release state. It will be narrowed after the distribution/state branch migration.

## Explicit non-public-main writers

| Automation | Target | Credential | Protection posture |
|---|---|---|---|
| `apply-development-package.yml` | Existing owner-created PR branch | `DEVELOPMENT_PR_TOKEN` | Review branch only. |
| `prepare-release-rollback.yml` | New recovery branch and PR | `DEVELOPMENT_PR_TOKEN` | Review branch only. |
| `backup_release_to_private_repo.sh` | private recovery repository `main` | `MIGRATION_REPO_TOKEN` | Separate repository; not a public-main bypass. |

## Target architecture

- **Public `main`:** reviewed source, workflows, tests, policy, documentation and stable configuration only.
- **Distribution branch:** stable `dist/` and root Greasy Fork mirrors, written only by the release GitHub App.
- **Release-state branch:** dashboard, manifest, announcement and recovery state; never product source.
- **Immutable evidence:** validation candidates, bundles, checksums, audits, dry-runs and handovers as release assets or workflow artifacts.

## Migration order

1. ✅ Inventory every public-main writer and enforce it in CI.
2. ✅ Convert release dry runs to artifact-only evidence.
3. ✅ Convert repository audits to artifact-only evidence.
4. ✅ Convert canonical validation candidates to artifact-only evidence and remove persistent candidate state.
5. Separate release dashboard, manifest and announcement state from canonical source.
6. Move stable distribution output to a dedicated branch.
7. Introduce a narrowly scoped GitHub App for distribution and release-state writes.
8. Rehearse every release and recovery path without public-main mutation.
9. Enable strict protection only after all rehearsals pass.

## Current migration evidence

- PR #498: initial inventory and fail-closed enforcement.
- PR #499: dry-run writer removed.
- PR #500: repository-audit writer removed.
- Canonical validation writer removed on the current Issue #41 migration branch.
- Direct public-main writers reduced from **10 to 7**.
