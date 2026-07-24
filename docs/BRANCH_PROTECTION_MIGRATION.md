# Branch Protection Migration Plan

Strict pull-request-only protection is **not yet enabled**. Controlled automation commits remain because stable distribution publication, consolidated release state and recovery still mutate public `main`.

The migration is tracked by Issue #41. Authority is maintained in:

- `docs/BRANCH_WRITE_INVENTORY.md`;
- `.github/branch-write-inventory.json`;
- `.github/shadow-branch-policy.json`;
- `.github/scripts/test_branch_write_inventory.py`;
- `.github/scripts/test_validation_candidate_pipeline.py`;
- `.github/scripts/test_greasyfork_parity_pipeline.py`;
- `.github/scripts/test_release_announcement_state_pipeline.py`;
- `.github/scripts/test_update_manifest_pipeline.py`;
- `.github/scripts/test_release_state_monitor_pipeline.py`;
- `.github/scripts/test_shadow_branch_parity.py`;
- `.github/scripts/test_shadow_sync_writer.py`.

## Current safe controls

- deletion and force-push protection;
- reviewed pull requests for normal development;
- code-integrity, performance, asset, recovery and documentation validation;
- immutable Action pins and permission auditing;
- owner-authenticated review branches for packages and rollback preparation;
- explicit production, recovery and shadow-synchronization confirmation phrases;
- exact commit/ref/hash validation evidence;
- deterministic dashboard, Greasy Fork, announcement-state and update-manifest verification;
- atomic primary release dashboard, stable manifest and announcement state;
- isolated non-live `release-state` and `distribution` branches;
- a manual-only, fixed-target shadow writer with read-only workflow permission;
- verified administrator repair access to both operational branches;
- a constrained release-state worktree helper with role, path and ancestry validation.

## Completed migration stages

### Write-path inventory ✅

The 24 July 2026 baseline identified 10 direct public-main writers. Every `contents: write` workflow and executable main-ref mutation is classified by target branch and fail-closed in CI.

### Artifact-only validation and evidence ✅

Seven workflows verify with read-only repository access and retained immutable evidence instead of committing generated state:

- canonical userscript validation;
- release dry runs;
- repository/dependency audits;
- release dashboard projection;
- Greasy Fork canonical parity;
- release announcement-state verification;
- stable update-manifest verification.

### GitHub source authority ✅

Automatic source importing is retired. GitHub is authoritative. Live Greasy Fork parity accepts canonical-ahead during publication and fails on live-ahead or equal-version content drift.

### Atomic release dashboard, manifest and announcement state ✅

Normal production releases no longer require follow-up announcement or manifest commits.

After Greasy Fork verification, private backup and Discord publication, `release-toolkit.yml` commits these together:

- `status/release-dashboard.json`;
- `status/README.md`;
- `status/update-manifest.json`;
- `.github/greasyfork-version.txt`.

The manifest is built by `.github/scripts/build_stable_update_manifest.py`. The former publisher is now a read-only projection verifier with 30-day retained evidence.

The existing v5.0.7 runtime URL remains unchanged:

`raw.githubusercontent.com/Conroy1988/missionchief-toolkit-assets/main/status/update-manifest.json`

This is a compatibility stage. A later versioned Toolkit release will move the runtime consumer to the final `release-state` endpoint.

### Operational branch topology and access rehearsal ✅

PRs #506–#507 established:

- `release-state` for verified dashboard, manifest and announcement state;
- `distribution` for stable `dist/` and root userscript paths;
- read-only branch-role and governed-file verification;
- a manual exact-SHA-bound synchronizer restricted to the two operational refs.

Both branches remain in `shadow-rehearsal` mode. External consumers are disabled, strict protection is disabled and administrator recovery remains mandatory.

The connected administrator identity completed:

- an exact-current-`main` read-only plan;
- 10/10 governed-file parity at the initial baseline;
- same-tree fast-forward write probes on both branches;
- post-write role and content verification;
- no force push, history rewrite, public-main mutation or live-consumer change.

### Fallback tracker moved to release-state ✅

`greasyfork-release-monitor.yml` no longer commits to public `main`.

The transitional authority split is:

- verified dashboard: `main`;
- fallback announcement tracker: `release-state`;
- external consumers: disabled;
- production tracker compatibility copy: still written atomically on `main` by `release-toolkit.yml` until the primary state cutover.

`.github/scripts/release_state_branch.py` prepares a detached release-state worktree, validates `.github/branch-role.json`, allows only reviewed paths, rejects `main`, rejects force pushes, fails on stale ancestry and pushes only `HEAD:refs/heads/release-state`.

The read-only operational verifier now distinguishes:

- **mirrored paths** — must remain byte-identical to `main`;
- **operational paths** — may differ but must satisfy a reviewed schema.

Only `.github/greasyfork-version.txt` is operational at this stage. Dashboard JSON/Markdown and the stable manifest remain mirrored.

Direct public-main writers are reduced from **10 to 2**.

## Remaining generated state

Public `main` still contains:

1. stable `dist/` and root Greasy Fork mirrors;
2. verified dashboard, stable manifest and primary announcement state;
3. guarded recovery state.

The fallback monitor no longer writes `main`. The update manifest no longer has a standalone writer, but its compatibility file remains part of the atomic production commit until the versioned consumer migration.

## Target architecture

### Public `main`

Reviewed source, workflows, tests, policy, documentation and temporary compatibility configuration only.

### Distribution branch

Stable `dist/` and root userscript mirrors required by Greasy Fork, written by a narrowly scoped release GitHub App.

### Release-state branch

Mutable dashboard, manifest, announcement, fallback-monitor and recovery state. It is operational state, never product source.

### Immutable evidence

Validation candidates, parity audits, synchronization plans, announcement checks, dashboard and manifest projections, release bundles, checksums, audits, dry runs and handovers remain GitHub Release assets or Actions artifacts.

## Access and speed requirements

The final protection design must retain fast owner operation:

- `Conroy1988` remains repository administrator and recovery authority;
- normal changes use owner-created branches and fast parallel CI;
- no mandatory external reviewer is introduced;
- administrator bypass is PR-only rather than routine direct push;
- auto-merge is enabled after rehearsal;
- distribution and release-state branches retain administrator recovery access;
- strict enforcement is not enabled until branch creation, PR update, merge, release, recovery and ruleset rollback access are proven;
- evidence checks become required only for the paths they govern.

## Remaining migration stages

1. ✅ Inventory every workflow and script capable of updating public `main`.
2. ✅ Separate validation, audit and verification evidence from public `main`.
3. ✅ Make dashboard and announcement state atomic; retire reconciliation writing.
4. ✅ Fold stable update-manifest publication into the same atomic release commit — PR #505.
5. ✅ Create and verify non-live `release-state` and `distribution` branches — PR #506.
6. ✅ Introduce the constrained shadow writer and rehearse plan/write access — PR #507 and Issue #41 evidence.
7. ✅ Move the fallback announcement tracker writer to `release-state`.
8. Move release recovery state to `release-state`.
9. Move primary dashboard, manifest and announcement authority to `release-state`.
10. Publish a versioned Toolkit migration that reads the manifest from `release-state` with a reviewed compatibility fallback.
11. Move stable `dist/` and Greasy Fork mirrors to `distribution`.
12. Replace temporary credentials with a narrowly scoped GitHub App.
13. Remove unnecessary `contents: write` from orchestration-only workflows.
14. Rehearse without public-main mutation:
    - normal Release Readiness;
    - full production publication;
    - Greasy Fork-only retry;
    - private-backup-only retry;
    - Discord-only retry;
    - dashboard reconstruction;
    - stable release-asset repair;
    - emergency rollback-candidate preparation.
15. Rehearse owner/admin access:
    - create and update an owner branch;
    - open and update a pull request;
    - auto-merge after green checks;
    - use PR-only administrator bypass where required;
    - repair distribution and release-state branches;
    - disable or amend the ruleset.
16. Require pull requests, approved checks, current branches and resolved conversations.
17. Block routine direct human pushes and enable strict protection only after complete rehearsal.

## Exit criteria

Strict protection is ready only when no workflow requires a public-main commit, every bypass actor is a scoped GitHub App or explicit administrator recovery actor, generated state is reconstructable, owner update speed is preserved, and every release/recovery/access path has passed non-production rehearsal.
