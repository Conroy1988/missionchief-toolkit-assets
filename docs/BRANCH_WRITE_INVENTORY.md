# Protected-branch write inventory

**Reviewed:** 24 July 2026  
**Issue:** #41 — Migrate release state for strict main-branch protection

## Current conclusion

Strict pull-request-only protection is **not yet safe to enable**.

The repository now has two workflows that can commit directly to public `main`: controlled release recovery and guarded production publication. Two release orchestrators invoke the reusable production writer but contain no direct public-main push.

Canonical validation, release dry runs, repository audits, dashboard projection, Greasy Fork parity, announcement-state verification and stable update-manifest verification are now artifact-only. These seven workflows use read-only repository access and retain immutable evidence instead of committing generated state.

The fallback announcement tracker is now written only to `release-state`. The fallback monitor still reads the verified release dashboard from `main` during this transitional stage, preventing duplicate Discord posts while removing its direct public-main mutation.

The `release-state` and `distribution` branches remain non-live operational shadows. Read-only parity, an exact-SHA synchronization plan and same-tree administrator write probes are complete. Strict protection and external consumer cutover remain disabled.

`.github/branch-write-inventory.json` is the machine-readable write authority. `.github/shadow-branch-policy.json` governs branch roles and reviewed paths. Permanent contracts fail closed when a writer, permission, authority, branch role or release-state boundary changes.

## Direct public `main` writers

| Workflow | Current mutation | Required migration |
|---|---|---|
| `release-recovery.yml` | dashboard JSON/Markdown and announcement recovery state | Move mutable recovery state to `release-state`; retain GitHub Release API repair capability. |
| `release-toolkit.yml` | stable distribution plus atomic dashboard, update-manifest and announcement state | Split distribution and state across dedicated branches under a scoped GitHub App. |

The executable public-main push helper `.github/scripts/sync_greasyfork_root_mirror.sh` is owned by `release-toolkit.yml`. The deterministic helper `.github/scripts/build_stable_update_manifest.py` writes only the manifest projection inside that existing guarded release commit.

## Release-state branch writer

`greasyfork-release-monitor.yml` is now classified under `releaseStateBranchWriters`, not `directMainWriters`.

| Property | Enforced value |
|---|---|
| Source authority | Verified `main` dashboard |
| Target branch | `release-state` |
| Governed write | `.github/greasyfork-version.txt` only |
| Credential | `github.token` |
| Push mode | Normal fast-forward only |
| Public-main mutation | Forbidden |
| Consumer cutover | Disabled |

`.github/scripts/release_state_branch.py` owns the branch transaction:

- fetches only `release-state` into a detached worktree;
- validates `.github/branch-role.json` before every operation;
- requires the exact reviewed mutable-path allowlist;
- rejects role-file changes and unapproved paths;
- fails if the remote branch moves after preparation;
- uses compare-and-swap ancestry with no rebase, force push or history rewrite;
- pushes only `HEAD:refs/heads/release-state`;
- requires `GH_TOKEN` only for the final governed push;
- contains executable self-tests that reject `main` and allowlist expansion.

The monitor checks out `main` with `persist-credentials: false`, reads the current dashboard from `main`, reads the tracker from the release-state worktree, rechecks both remote refs before a fallback post, and records only the tracker on `release-state`.

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

## Operational branch topology

| Branch | Governed paths | Current authority | External consumers |
|---|---|---|---|
| `release-state` | dashboard JSON/Markdown, stable update manifest, announcement tracker | Transitional tracker writes; remaining state still authoritative on `main` | Disabled |
| `distribution` | stable `dist/` files and root userscript mirrors | `main` | Disabled |

Each branch contains `.github/branch-role.json` declaring:

- `mode: shadow-rehearsal`;
- `liveConsumersEnabled: false`;
- `strictProtectionEnabled: false`;
- administrator recovery is mandatory;
- Issue #41 controls cutover;
- only reviewed operational paths may become mutable.

`.github/workflows/verify-shadow-branch-parity.yml` remains read-only. During the transitional tracker migration, parity policy will be refined to distinguish the intentionally operational tracker from state that must still mirror `main`.

## Constrained shadow synchronization writer

`.github/workflows/sync-shadow-branches.yml` and `.github/scripts/sync_shadow_branches.py` remain the manual non-live rehearsal writer.

The contract remains:

- manual `workflow_dispatch` only;
- authorized actor fixed to `Conroy1988`;
- source fixed to exact current `main`;
- targets restricted to `release-state`, `distribution` or both;
- `PLAN SHADOW SYNC` and `SYNC SHADOWS` confirmation phrases;
- workflow-level `contents: read`;
- temporary `DEVELOPMENT_PR_TOKEN` only for reviewed apply operations;
- branch-specific governed paths only;
- `.github/branch-role.json` immutable;
- normal fast-forward pushes only;
- public `main` rejected as a target;
- live consumer cutover forbidden;
- replacement by a narrowly scoped GitHub App required before final cutover.

The connected administrator identity completed the read-only plan and same-tree branch probes. No force push, history rewrite, public-main change or live-consumer change occurred.

## Current release state

After Greasy Fork verification, private backup and Discord publication, `release-toolkit.yml` writes the following together in one public-main commit:

- `status/release-dashboard.json`;
- `status/README.md`;
- `status/update-manifest.json`;
- `.github/greasyfork-version.txt`.

The stable manifest is generated by `.github/scripts/build_stable_update_manifest.py`. `publish-update-manifest.yml` independently verifies the committed projection with read-only access.

The current v5.0.7 runtime consumer remains unchanged:

`raw.githubusercontent.com/Conroy1988/missionchief-toolkit-assets/main/status/update-manifest.json`

This compatibility URL remains on `main` until a versioned Toolkit release moves the runtime consumer to the final `release-state` endpoint.

## Production release sequence

1. Canonical validation uploads exact immutable candidate evidence.
2. Automatic release verifies the exact run and rejects stale commits.
3. Release Readiness independently rebuilds and validates distribution.
4. Production publishes stable distribution and root mirrors.
5. GitHub Release is published and Greasy Fork is verified.
6. The release is backed up privately and announced to Discord.
7. Dashboard JSON, rendered Markdown, stable update manifest and announcement tracker are committed atomically.
8. GitHub Pages is dispatched and awaited.
9. Dashboard, Greasy Fork, announcement and update-manifest workflows verify only.
10. The fallback monitor reconciles its dedicated release-state tracker without writing `main`.

## Indirect release orchestrators

| Workflow | Delegated writer | Role |
|---|---|---|
| `auto-release-after-validation.yml` | `release-toolkit.yml` | Consumes exact validation evidence and starts guarded release. |
| `owner-release-command.yml` | `release-toolkit.yml` | Performs owner authorization and fresh validation. |

Their write authority remains because the reusable production job still writes distribution and release state.

## Other non-public-main writers

| Automation | Target | Credential | Protection posture |
|---|---|---|---|
| `apply-development-package.yml` | Existing owner PR branch | `DEVELOPMENT_PR_TOKEN` | Review branch only. |
| `prepare-release-rollback.yml` | Recovery branch and PR | `DEVELOPMENT_PR_TOKEN` | Review branch only. |
| `sync-shadow-branches.yml` | `release-state` and `distribution` only | `DEVELOPMENT_PR_TOKEN` | Manual rehearsal; no `main` or consumer cutover. |
| `greasyfork-release-monitor.yml` | `release-state` tracker only | `github.token` | Scheduled transitional operational writer; no `main`. |
| `backup_release_to_private_repo.sh` | private recovery repository `main` | `MIGRATION_REPO_TOKEN` | Separate repository. |

## Target architecture

- **Public `main`:** reviewed source, workflows, tests, policy and compatibility configuration.
- **Distribution branch:** stable `dist/` and root mirrors, written by a scoped release App.
- **Release-state branch:** dashboard, manifest, announcement, fallback-monitor and recovery state.
- **Immutable evidence:** validation, parity, synchronization plans, bundles, audits and handovers.

## Migration order

1. ✅ Inventory and enforce every public-main writer.
2. ✅ Convert dry runs, audits and validation to immutable evidence.
3. ✅ Convert dashboard refresh to read-only projection.
4. ✅ Retire automatic Greasy Fork importing.
5. ✅ Make primary announcement state atomic and reconciliation read-only.
6. ✅ Fold stable update-manifest publication into the atomic release commit — PR #505.
7. ✅ Create and validate `release-state` and `distribution` branches — PR #506.
8. ✅ Add the constrained writer and rehearse plan/apply access — PR #507 and Issue #41 evidence.
9. ✅ Move the fallback announcement tracker writer from `main` to `release-state`.
10. Move release recovery state to `release-state`.
11. Move primary dashboard/manifest/announcement authority to `release-state`.
12. Migrate a versioned Toolkit runtime to the release-state manifest URL.
13. Cut stable distribution over to `distribution`.
14. Replace temporary credentials with a narrowly scoped GitHub App.
15. Rehearse release, recovery and administrator access.
16. Enable strict protection only after all rehearsals pass.

## Current migration evidence

- PRs #498–#504 reduced direct public-main writers from **10 to 4**.
- PR #505 reduced direct public-main writers from **4 to 3**.
- This migration reduces direct public-main writers from **3 to 2**.
- PRs #506–#507 established isolated operational branches, read-only parity and constrained administrator rehearsal access.
- Existing v5.0.7 installations retain their exact manifest URL.
- No userscript, production version, release object, external URL or protection setting changes in this step.
