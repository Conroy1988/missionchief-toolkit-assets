# Protected-branch write inventory

**Reviewed:** 24 July 2026  
**Reviewed `main`:** `ed04231602b67730de3854a29c4ce09ee586aaa3`  
**Issue:** #41 — Migrate release state for strict main-branch protection

## Current conclusion

Strict pull-request-only protection is **not yet safe to enable**.

The repository now has eight workflows that can commit directly to public `main`. Two additional release workflows do not push themselves, but invoke the reusable production workflow that does. The remaining writes still mix canonical source, generated distribution, release state, announcement state and human-readable dashboards in one protected branch.

Release dry runs and repository audits are now artifact-only. Both workflows use read-only contents permission, disable persisted checkout credentials and retain immutable evidence without mutating public `main` or the production release dashboard.

`.github/branch-write-inventory.json` is the machine-readable authority and `.github/scripts/test_branch_write_inventory.py` prevents unclassified write paths from being introduced.

## Direct public `main` writers

| Workflow | Current mutation | Required migration |
|---|---|---|
| `validate-userscript.yml` | `dist/`, candidate dashboard JSON and generated dashboard Markdown | Move generated candidate state outside protected `main`. |
| `greasyfork-release-monitor.yml` | `.github/greasyfork-version.txt` | Move announcement state to a release-state branch. |
| `import-canonical-userscript.yml` | canonical userscript and source baseline | Convert to an owner-created PR and retire when GitHub remains authoritative. |
| `publish-update-manifest.yml` | `status/update-manifest.json` | Publish from a release-state branch or immutable release asset. |
| `reconcile-release-announcement-state.yml` | `.github/greasyfork-version.txt` | Move announcement state to a release-state branch. |
| `release-recovery.yml` | dashboard JSON/Markdown and announcement tracker | Keep release-object repair in the API; move mutable state to the release-state branch. |
| `release-toolkit.yml` | stable root userscript mirrors and final release dashboard | Move mirrors to a distribution branch and state to a release-state branch under a scoped GitHub App. |
| `update-release-dashboard.yml` | generated `status/README.md` | Generate at Pages/deployment time or from the release-state branch. |

## Artifact-only evidence workflows

| Workflow | Permission | Retained evidence | Branch effect |
|---|---|---|---|
| `release-toolkit-dry-run.yml` | `contents: read` | release bundle plus versioned JSON/Markdown dry-run report | No branch or publication-channel change. |
| `repository-audit.yml` | `contents: read` | `repository-audit.json` and `.md` in `missionchief-repository-audit-<commit>` | No branch or release-dashboard change. |

The former committed dry-run record was stale at v4.10.4 while production was v5.0.7. The former committed repository audit described v4.13.1 and wrote a fixed `2026-07-14` timestamp into the production dashboard. Both write paths are now removed and permanently forbidden by CI.

## Production release write sequence

The production release still performs multiple branch mutations:

1. `validate-userscript.yml` commits the validated distribution candidate.
2. `release-toolkit.yml` commits stable root mirrors.
3. `release-toolkit.yml` publishes GitHub Release, verifies Greasy Fork, backs up privately and posts Discord.
4. `release-toolkit.yml` commits the verified release dashboard.
5. `publish-update-manifest.yml` commits the stable update manifest.
6. Dashboard and announcement reconciliation may create further generated-state commits.

Strict protection must preserve this sequence without permitting unrestricted bypasses or splitting the release ledger across channels.

## Indirect release orchestrators

| Workflow | Delegated writer | Role |
|---|---|---|
| `auto-release-after-validation.yml` | `release-toolkit.yml` | Starts the guarded release after successful validation. |
| `owner-release-command.yml` | `release-toolkit.yml` | Authorizes a manual release and reports the result. |

Their own jobs should ultimately use read-only contents access.

## Explicit non-public-main writers

| Automation | Target | Credential | Protection posture |
|---|---|---|---|
| `apply-development-package.yml` | Existing owner-created PR branch | `DEVELOPMENT_PR_TOKEN` | Review branch only. |
| `prepare-release-rollback.yml` | New recovery branch and PR | `DEVELOPMENT_PR_TOKEN` | Review branch only. |
| `backup_release_to_private_repo.sh` | private recovery repository `main` | `MIGRATION_REPO_TOKEN` | Separate repository; not a public-main bypass. |

## Target architecture

- **Public `main`:** reviewed source, workflows, tests, policy, documentation and stable configuration only.
- **Distribution branch:** stable Greasy Fork root mirrors, written only by the release GitHub App.
- **Release-state branch:** dashboard, manifest, announcement and recovery state; never product source.
- **Immutable evidence:** bundles, checksums, audits, dry-runs and handovers as release assets or workflow artifacts.

## Migration order

1. ✅ Inventory every public-`main` writer and enforce it in CI.
2. ✅ Convert release dry runs to artifact-only evidence.
3. ✅ Convert repository audits to artifact-only evidence.
4. Separate validated distribution, dashboard, manifest and tracker state from canonical source.
5. Move stable Greasy Fork mirrors to a distribution branch.
6. Introduce a narrowly scoped GitHub App for distribution and release-state writes.
7. Rehearse every release and recovery path without public-main mutation.
8. Enable strict protection only after all rehearsals pass.

## Current migration evidence

- PR #498: initial inventory and fail-closed enforcement.
- PR #499: dry-run writer removed.
- Repository audit writer removed; committed audit files now identify themselves as legacy snapshots.
- Direct public-main writers reduced from **10 to 8**.
