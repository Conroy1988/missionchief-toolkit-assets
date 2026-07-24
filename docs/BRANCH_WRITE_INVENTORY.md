# Protected-branch write inventory

**Reviewed:** 24 July 2026  
**Issue:** #41 — Migrate release state for strict main-branch protection

## Current conclusion

Strict pull-request-only protection is **not yet safe to enable**.

The repository now has one workflow that can commit directly to public `main`: `release-toolkit.yml`. It still publishes the stable distribution and writes a temporary compatibility copy of release state required by existing v5.0.7 installations.

Two workflows write governed operational state to `release-state`:

- `greasyfork-release-monitor.yml` — fallback announcement tracker;
- `release-recovery.yml` — recovery dashboard, rendered status, stable manifest and announcement tracker.

Two release orchestrators invoke the reusable production writer but contain no direct public-main push.

Canonical validation, release dry runs, repository audits, dashboard projection, Greasy Fork parity, announcement-state verification and stable update-manifest verification are artifact-only. These seven workflows use read-only repository access and retain immutable evidence instead of committing generated state.

The release recovery ledger is now written only to `release-state`. GitHub Release verification and asset repair, Greasy Fork retry, private backup and Discord HTTP side effects remain controlled API operations, but their ledger reconciliation cannot commit to `main`.

The `release-state` and `distribution` branches remain non-live operational branches. External consumers and strict protection remain disabled. Administrator recovery access has been rehearsed successfully.

`.github/branch-write-inventory.json` is the machine-readable authority. `.github/shadow-branch-policy.json` governs branch roles, path classes and operational writers. Permanent contracts fail closed when any writer, permission, branch target, mutable path or consumer boundary changes.

## Sole direct public `main` writer

| Workflow | Current mutation | Required migration |
|---|---|---|
| `release-toolkit.yml` | stable distribution plus atomic dashboard, manifest and announcement compatibility state | Split distribution and primary state across dedicated branches under a scoped GitHub App. |

The executable public-main helper `.github/scripts/sync_greasyfork_root_mirror.sh` is owned by `release-toolkit.yml`. `.github/scripts/build_stable_update_manifest.py` generates the compatibility manifest inside the same guarded release commit.

## Governed `release-state` writers

| Workflow | Operational authority | Source evidence | Public-main effect |
|---|---|---|---|
| `greasyfork-release-monitor.yml` | `.github/greasyfork-version.txt` | live Greasy Fork version and verified compatibility dashboard | None |
| `release-recovery.yml` | dashboard JSON, rendered Markdown, stable manifest and tracker | verified GitHub Release bundle plus explicit recovery inputs | None |

Both use `.github/scripts/release_state_branch.py` for branch transactions. That helper:

- prepares a detached `release-state` worktree;
- validates `.github/branch-role.json` before every operation;
- requires the exact reviewed mutable-path allowlist;
- rejects role-file changes and unapproved paths;
- fails if the remote branch moves after preparation;
- performs normal fast-forward pushes only;
- never rebases, force-pushes or rewrites branch history;
- pushes only `HEAD:refs/heads/release-state`;
- requires `GH_TOKEN` only for the final governed push;
- contains executable self-tests that reject `main` and allowlist expansion.

### Fallback monitor

The monitor checks out `main` with `persist-credentials: false`, reads the verified compatibility dashboard from `main`, reads the announcement tracker from `release-state`, rechecks both refs before posting, and commits only the tracker to `release-state`.

### Release recovery

`.github/scripts/release_recovery_state.py` owns recovery-ledger transitions:

- seeds `release-state` from a newer verified `main` compatibility snapshot when necessary;
- records Greasy Fork recovery;
- records private-backup recovery;
- claims a Discord retry before posting;
- finalises Discord state only when the expected claim nonce still matches;
- rebuilds the verified dashboard from GitHub Release and private-backup evidence;
- regenerates the rendered dashboard;
- regenerates the stable manifest only when the recovered release state is complete;
- delegates every commit to the constrained branch helper.

The recovery workflow preserves every exact confirmation phrase and the shared `toolkit-production-release` lock. `verify-release` and `repair-stable-assets` remain API/read-only with respect to repository state.

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
| `release-state` | dashboard JSON/Markdown, stable update manifest, announcement tracker | Operational recovery ledger | Disabled |
| `distribution` | stable `dist/` files and root userscript mirrors | Mirrored from `main` | Disabled |

Each branch contains `.github/branch-role.json` declaring:

- `mode: shadow-rehearsal`;
- `liveConsumersEnabled: false`;
- `strictProtectionEnabled: false`;
- administrator recovery is mandatory;
- Issue #41 controls cutover;
- only reviewed operational paths may become mutable.

`.github/workflows/verify-shadow-branch-parity.yml` remains read-only. It validates:

- role declarations;
- JSON and Markdown schemas;
- dashboard/Markdown version equality;
- manifest and tracker versions never ahead of the recovery dashboard;
- distribution files remain byte-identical to `main`;
- external consumers remain disabled.

## Manual shadow synchronizer

`.github/workflows/sync-shadow-branches.yml` remains a manual owner-authenticated rehearsal utility.

The manual synchronizer has no file-copy authority on `release-state`. All four release-state paths are operational and are preserved byte-for-byte by the synchronizer. It may only record an idempotent empty access probe on that branch.

The synchronizer may still copy reviewed mirror files from `main` to `distribution`. Its contract remains:

- manual `workflow_dispatch` only;
- authorized actor fixed to `Conroy1988`;
- source fixed to exact current `main`;
- targets restricted to `release-state`, `distribution` or both;
- `PLAN SHADOW SYNC` and `SYNC SHADOWS` confirmation phrases;
- workflow-level `contents: read`;
- temporary `DEVELOPMENT_PR_TOKEN` only for reviewed apply operations;
- `.github/branch-role.json` immutable;
- normal non-force pushes only;
- public `main` rejected as a target;
- live consumer cutover forbidden;
- replacement by a narrowly scoped GitHub App required before final cutover.

## Compatibility state on `main`

After Greasy Fork verification, private backup and Discord publication, `release-toolkit.yml` still writes these together in one compatibility commit:

- `status/release-dashboard.json`;
- `status/README.md`;
- `status/update-manifest.json`;
- `.github/greasyfork-version.txt`.

Existing v5.0.7 installations still read:

`raw.githubusercontent.com/Conroy1988/missionchief-toolkit-assets/main/status/update-manifest.json`

That URL remains valid until a later versioned Toolkit release migrates the runtime consumer to `release-state`. Recovery actions do not rewrite this compatibility copy; only the next normal production release does.

## Production release sequence

1. Canonical validation uploads exact immutable candidate evidence.
2. Automatic release verifies the exact run and rejects stale commits.
3. Release Readiness independently rebuilds and validates distribution.
4. Production publishes stable distribution and root mirrors.
5. GitHub Release is published and Greasy Fork is verified.
6. The release is backed up privately and announced to Discord.
7. Dashboard JSON, rendered Markdown, stable update manifest and announcement tracker are committed atomically as compatibility state.
8. GitHub Pages is dispatched and awaited.
9. Dashboard, Greasy Fork, announcement and update-manifest workflows verify only.
10. Fallback and recovery operations write their governed ledger to `release-state` only.

## Indirect release orchestrators

| Workflow | Delegated writer | Role |
|---|---|---|
| `auto-release-after-validation.yml` | `release-toolkit.yml` | Consumes exact successful validation evidence and invokes the guarded production writer. |
| `owner-release-command.yml` | `release-toolkit.yml` | Performs owner authorization, fresh validation and guarded release invocation. |

Neither orchestrator contains a direct public-main push. Their `contents: write` authority remains transitional because the reusable production workflow still writes public compatibility state and stable distribution.

## Other non-public-main writers

| Automation | Target | Credential | Protection posture |
|---|---|---|---|
| `apply-development-package.yml` | Existing owner PR branch | `DEVELOPMENT_PR_TOKEN` | Review branch only. |
| `prepare-release-rollback.yml` | Recovery branch and PR | `DEVELOPMENT_PR_TOKEN` | Review branch only. |
| `sync-shadow-branches.yml` | `release-state` access probe and `distribution` mirrors | `DEVELOPMENT_PR_TOKEN` | Manual rehearsal; no `main` or consumer cutover. |
| `greasyfork-release-monitor.yml` | `release-state` tracker only | `github.token` | Scheduled operational writer; no `main`. |
| `release-recovery.yml` | complete `release-state` recovery ledger | `github.token` | Manually confirmed recovery writer; no `main`. |
| `backup_release_to_private_repo.sh` | private recovery repository `main` | `MIGRATION_REPO_TOKEN` | Separate repository. |

## Target architecture

- **Public `main`:** reviewed source, workflows, tests, policy and temporary compatibility configuration.
- **Distribution branch:** stable `dist/` and root mirrors, written by a scoped release App.
- **Release-state branch:** primary dashboard, manifest, announcement, fallback-monitor and recovery state.
- **Immutable evidence:** validation, parity, synchronization plans, bundles, audits and handovers.

## Migration order

1. ✅ Inventory and enforce every public-main writer.
2. ✅ Convert dry runs, audits and validation to immutable evidence.
3. ✅ Convert dashboard refresh to read-only projection.
4. ✅ Retire automatic Greasy Fork importing.
5. ✅ Make primary announcement state atomic and reconciliation read-only.
6. ✅ Fold stable update-manifest publication into the atomic release commit — PR #505.
7. ✅ Create and validate `release-state` and `distribution` branches — PR #506.
8. ✅ Add the constrained writer and rehearse access — PR #507 and Issue #41 evidence.
9. ✅ Move fallback announcement tracking to `release-state` — PR #508.
10. ✅ Move the release recovery ledger to `release-state`.
11. Move primary production state authority to `release-state`.
12. Migrate a versioned Toolkit runtime to the release-state manifest URL.
13. Cut stable distribution over to `distribution`.
14. Replace temporary credentials with a narrowly scoped GitHub App.
15. Rehearse production release, recovery and administrator access.
16. Enable strict protection only after all rehearsals pass.

## Current migration evidence

- PRs #498–#504 reduced direct public-main writers from **10 to 4**.
- PR #505 reduced direct public-main writers from **4 to 3**.
- PR #508 reduced direct public-main writers from **3 to 2**.
- This migration reduces direct public-main writers from **2 to 1**.
- Two workflows write governed operational state to `release-state`.
- The release recovery ledger is now written only to `release-state`.
- Seven workflows use read-only repository access for immutable verification evidence.
- Existing v5.0.7 installations retain their exact manifest URL.
- No userscript, production version, release object, external URL or protection setting changes in this step.
