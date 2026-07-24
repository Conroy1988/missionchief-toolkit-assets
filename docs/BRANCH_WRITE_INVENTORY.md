# Protected-branch write inventory

**Reviewed:** 24 July 2026  
**Issue:** #41 — Migrate release state for strict main-branch protection

## Current conclusion

Strict pull-request-only protection is **not yet safe to enable**.

The repository has three workflows that can commit directly to public `main`. Two release orchestrators invoke the reusable production writer but contain no direct public-main push. The remaining writes are limited to fallback monitoring, release recovery and guarded production publication.

Canonical validation, release dry runs, repository audits, dashboard projection, Greasy Fork parity, announcement-state verification and stable update-manifest verification are now artifact-only. These seven workflows use read-only repository access and retain immutable evidence instead of committing generated state.

The `release-state` and `distribution` branches are non-live shadows. Read-only parity, an exact-SHA plan and same-tree write-access probes are complete. The constrained writer cannot update public `main` or enable live consumers.

`.github/branch-write-inventory.json` is the machine-readable write authority. `.github/shadow-branch-policy.json` governs the isolated shadow rehearsal. Permanent contracts fail closed when a writer, permission, authority, branch role or release-state boundary changes.

## Direct public `main` writers

| Workflow | Current mutation | Required migration |
|---|---|---|
| `greasyfork-release-monitor.yml` | fallback `.github/greasyfork-version.txt` state | Move fallback monitoring to the release-state branch. |
| `release-recovery.yml` | dashboard JSON/Markdown and announcement recovery state | Move mutable recovery state to the release-state branch. |
| `release-toolkit.yml` | stable distribution plus atomic dashboard, update-manifest and announcement state | Move distribution and state to dedicated branches under a scoped GitHub App. |

The executable public-main push helper `.github/scripts/sync_greasyfork_root_mirror.sh` is owned by `release-toolkit.yml`. The deterministic helper `.github/scripts/build_stable_update_manifest.py` writes only the manifest projection inside that existing guarded release commit.

## Artifact-only evidence workflows

| Workflow | Permission | Evidence | Branch effect |
|---|---|---|---|
| `validate-userscript.yml` | `contents: read` | exact candidate source/ref/hash bundle | No branch or dashboard change. |
| `release-toolkit-dry-run.yml` | `contents: read` | release bundle plus dry-run report | No publication-channel change. |
| `repository-audit.yml` | `contents: read` | repository audit JSON/Markdown | No branch or dashboard change. |
| `update-release-dashboard.yml` | `contents: read` | rendered dashboard, diff and log | No branch change. |
| `import-canonical-userscript.yml` | `contents: read` | live Greasy Fork parity evidence | No source, baseline, branch or PR change. |
| `reconcile-release-announcement-state.yml` | `contents: read` | dashboard/tracker consistency evidence | No dashboard or tracker change. |
| `publish-update-manifest.yml` | `contents: read` | manifest projection JSON/Markdown/log | No manifest, dashboard or branch change. |

## Shadow branch topology

| Branch | Governed paths | Current authority | Live consumers |
|---|---|---|---|
| `release-state` | dashboard JSON/Markdown, stable update manifest, announcement tracker | `main` | Disabled |
| `distribution` | stable `dist/` files and root userscript mirrors | `main` | Disabled |

Each branch contains `.github/branch-role.json` declaring:

- `mode: shadow-rehearsal`;
- `liveConsumersEnabled: false`;
- `strictProtectionEnabled: false`;
- administrator recovery is mandatory;
- Issue #41 controls cutover;
- only reviewed operational paths may become mutable.

`.github/workflows/verify-shadow-branch-parity.yml` remains read-only. It validates branch roles and governed-file parity, retains evidence for 30 days, and never commits, pushes, updates a ref or changes a live URL.

## Constrained shadow synchronization writer

`.github/workflows/sync-shadow-branches.yml` and `.github/scripts/sync_shadow_branches.py` provide the non-live rehearsal writer.

The writer contract is:

- manual `workflow_dispatch` only;
- authorized actor fixed to `Conroy1988`;
- exact source branch fixed to `main`;
- exact source commit SHA required and revalidated against `origin/main`;
- target restricted to `release-state`, `distribution` or both;
- plan confirmation must be `PLAN SHADOW SYNC`;
- apply confirmation must be `SYNC SHADOWS`;
- workflow permission remains `contents: read`;
- apply mode temporarily uses `DEVELOPMENT_PR_TOKEN` as the existing owner-authenticated credential;
- changed files must be a subset of each branch's governed paths;
- `.github/branch-role.json` remains immutable;
- pushes are fast-forward commits to the two reviewed shadow refs only;
- `main` is rejected as a target inside both the workflow and script;
- an idempotent empty probe can prove write access when governed content already matches;
- every plan/apply operation retains evidence;
- live consumer cutover remains forbidden;
- the temporary owner credential must be replaced by a narrowly scoped GitHub App before final cutover.

The connected administrator identity has completed the read-only plan and same-tree branch probes. No force push, history rewrite, public-main change or live-consumer change occurred.

## Current release state

After Greasy Fork verification, private backup and Discord publication, `release-toolkit.yml` now writes the following together in one commit:

- `status/release-dashboard.json`;
- `status/README.md`;
- `status/update-manifest.json`;
- `.github/greasyfork-version.txt`.

The stable manifest is generated by `.github/scripts/build_stable_update_manifest.py` from the verified dashboard and reviewed release settings. `publish-update-manifest.yml` independently verifies the committed projection with read-only access.

The current v5.0.7 runtime consumer remains unchanged:

`raw.githubusercontent.com/Conroy1988/missionchief-toolkit-assets/main/status/update-manifest.json`

This compatibility URL remains on `main` until a versioned Toolkit release moves the runtime consumer to the final `release-state` endpoint. Existing installations are therefore not stranded during migration.

## Production release sequence

1. Canonical validation uploads exact immutable candidate evidence.
2. Automatic release verifies that exact run and rejects stale commits.
3. Release Readiness independently rebuilds and validates distribution.
4. Production publishes stable distribution and root mirrors.
5. GitHub Release is published and Greasy Fork is verified.
6. The release is backed up privately and announced to Discord.
7. Dashboard JSON, rendered Markdown, stable update manifest and announcement tracker are committed atomically.
8. GitHub Pages is dispatched and awaited.
9. Dashboard, Greasy Fork, announcement and update-manifest workflows verify only.
10. Shadow parity remains independent until the versioned consumer cutover.

## Indirect release orchestrators

| Workflow | Delegated writer | Role |
|---|---|---|
| `auto-release-after-validation.yml` | `release-toolkit.yml` | Consumes exact validation evidence and starts guarded release. |
| `owner-release-command.yml` | `release-toolkit.yml` | Performs owner authorization and fresh validation. |

Their write authority remains only because the reusable production job still writes distribution and release state.

## Explicit non-public-main writers

| Automation | Target | Credential | Protection posture |
|---|---|---|---|
| `apply-development-package.yml` | Existing owner PR branch | `DEVELOPMENT_PR_TOKEN` | Review branch only. |
| `prepare-release-rollback.yml` | Recovery branch and PR | `DEVELOPMENT_PR_TOKEN` | Review branch only. |
| `sync-shadow-branches.yml` | `release-state` and `distribution` only | `DEVELOPMENT_PR_TOKEN` | Manual rehearsal; no `main` or consumer cutover. |
| `backup_release_to_private_repo.sh` | private recovery repository `main` | `MIGRATION_REPO_TOKEN` | Separate repository. |

## Target architecture

- **Public `main`:** reviewed source, workflows, tests, policy and documentation.
- **Distribution branch:** stable `dist/` and root mirrors, written by a scoped release App.
- **Release-state branch:** dashboard, manifest, announcement, fallback-monitor and recovery state.
- **Immutable evidence:** validation, parity, synchronization plans, bundles, audits and handovers.

## Migration order

1. ✅ Inventory and enforce every public-main writer.
2. ✅ Convert dry runs, audits and validation to immutable evidence.
3. ✅ Convert dashboard refresh to read-only projection.
4. ✅ Retire automatic Greasy Fork importing.
5. ✅ Make primary announcement state atomic and reconciliation read-only.
6. ✅ Fold stable update-manifest publication into the consolidated release-state commit.
7. ✅ Create shadow `release-state` and `distribution` branches and verify read-only parity — PR #506.
8. ✅ Add the constrained shadow writer and rehearse plan/apply access — PR #507 and Issue #41 evidence.
9. Replace the rehearsal owner token with a narrowly scoped GitHub App.
10. Move the versioned manifest consumer and consolidated release state to `release-state`.
11. Cut stable distribution over to `distribution`.
12. Rehearse release, recovery and administrator access.
13. Enable strict protection only after all rehearsals pass.

## Current migration evidence

- PRs #498–#504 reduced direct public-main writers from **10 to 4**.
- The current atomic update-manifest change reduces direct public-main writers from **4 to 3**.
- PRs #506–#507 established isolated operational branches, read-only parity and constrained administrator rehearsal access.
- Existing v5.0.7 installations retain their exact manifest URL.
- No userscript, production version, release object, live URL or protection setting is changed by this migration step.
