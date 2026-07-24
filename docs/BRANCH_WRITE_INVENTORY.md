# Protected-branch write inventory

**Reviewed:** 24 July 2026  
**Reviewed `main`:** `0b43be27b5857206adb55de85777425be9160816`  
**Issue:** #41 — Migrate release state for strict main-branch protection

## Current conclusion

Strict pull-request-only protection is **not yet safe to enable**.

The repository now has four workflows that can commit directly to public `main`. Two release orchestrators invoke the reusable production writer but contain no direct public-main push. The remaining writes are limited to fallback monitoring, stable update-manifest publication, release recovery and guarded production publication.

Canonical validation, release dry runs, repository audits, dashboard projection, Greasy Fork parity and announcement-state verification are now artifact-only. All six use read-only contents permission and retain deterministic evidence without mutating public `main`.

`.github/branch-write-inventory.json` is the machine-readable authority. Permanent contracts fail closed when a writer, permission, authority or release-state boundary changes.

## Direct public `main` writers

| Workflow | Current mutation | Required migration |
|---|---|---|
| `greasyfork-release-monitor.yml` | fallback `.github/greasyfork-version.txt` state | Move fallback announcement state to a release-state branch. |
| `publish-update-manifest.yml` | `status/update-manifest.json` | Publish from a release-state branch or immutable release asset. |
| `release-recovery.yml` | dashboard JSON/Markdown and announcement tracker | Move mutable recovery state to the release-state branch. |
| `release-toolkit.yml` | stable distribution, verified dashboard and announcement tracker | Move distribution and state to dedicated branches under a scoped GitHub App. |

The executable public-main push helper `.github/scripts/sync_greasyfork_root_mirror.sh` is owned by `release-toolkit.yml`.

## Artifact-only evidence workflows

| Workflow | Permission | Evidence | Branch effect |
|---|---|---|---|
| `validate-userscript.yml` | `contents: read` | exact candidate source/ref/hash bundle | No branch or dashboard change. |
| `release-toolkit-dry-run.yml` | `contents: read` | release bundle plus dry-run report | No publication-channel change. |
| `repository-audit.yml` | `contents: read` | repository audit JSON/Markdown | No branch or dashboard change. |
| `update-release-dashboard.yml` | `contents: read` | rendered dashboard, diff and log | No branch change. |
| `import-canonical-userscript.yml` | `contents: read` | live Greasy Fork parity evidence | No source, baseline, branch or PR change. |
| `reconcile-release-announcement-state.yml` | `contents: read` | dashboard/tracker consistency JSON/Markdown | No dashboard or tracker change. |

## Atomic announcement state

Primary release no longer requires a follow-up reconciliation commit.

After Greasy Fork verification, private backup and Discord publication, `release-toolkit.yml` now writes the following together in one commit:

- `status/release-dashboard.json`;
- `status/README.md`;
- `.github/greasyfork-version.txt`.

This guarantees that the verified release ledger and announcement tracker cannot diverge during normal publication. `reconcile-release-announcement-state.yml` now only verifies that:

- the dashboard has a latest release version;
- Greasy Fork is verified;
- Discord is recorded as posted;
- the tracker exactly matches the dashboard version.

It retains 30-day evidence and fails without attempting a repair. Recovery workflows retain their existing guarded ability to reconstruct state until the release-state branch migration is complete.

## Greasy Fork authority boundary

The former automatic importer is retired. GitHub is canonical. The read-only parity audit accepts an expected `canonical-ahead` state and fails on live-ahead or equal-version content drift. `status/source-baseline.json` is an immutable historical v4.11.2 bootstrap record.

## Production release sequence

1. Canonical validation uploads exact immutable candidate evidence.
2. Automatic release verifies that exact run and rejects stale commits.
3. Release Readiness independently rebuilds and validates distribution.
4. Production publishes stable distribution and root mirrors.
5. GitHub Release is published and Greasy Fork is verified.
6. The release is backed up privately and announced to Discord.
7. Dashboard JSON, rendered Markdown and announcement tracker are committed atomically.
8. Stable update manifest and Pages are dispatched in parallel.
9. Dashboard projection, Greasy Fork parity and announcement-state workflows verify only.

The owner command freshly validates current `main` and starts the same readiness and production workflows.

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
| `backup_release_to_private_repo.sh` | private recovery repository `main` | `MIGRATION_REPO_TOKEN` | Separate repository. |

## Target architecture

- **Public `main`:** reviewed source, workflows, tests, policy and documentation.
- **Distribution branch:** stable `dist/` and root mirrors, written by a scoped release App.
- **Release-state branch:** dashboard, manifest, announcement and recovery state.
- **Immutable evidence:** validation, parity, projections, bundles, audits and handovers.

## Migration order

1. ✅ Inventory and enforce every public-main writer.
2. ✅ Convert dry runs, audits and validation to immutable evidence.
3. ✅ Convert dashboard refresh to read-only projection.
4. ✅ Retire automatic Greasy Fork importing.
5. ✅ Make primary announcement state atomic and reconciliation read-only.
6. Move dashboard, manifest, fallback monitor and recovery state to a release-state branch.
7. Move stable distribution to a dedicated branch.
8. Introduce a scoped GitHub App.
9. Rehearse release, recovery and administrator access.
10. Enable strict protection only after all rehearsals pass.

## Current migration evidence

- PRs #498–#503 completed the inventory and first five writer removals.
- Current change removes the separate announcement reconciliation writer.
- Direct public-main writers reduced from **10 to 4**.
