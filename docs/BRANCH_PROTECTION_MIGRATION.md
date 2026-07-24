# Branch Protection Migration Plan

Strict pull-request-only protection is **not yet enabled**. Controlled automation commits remain because stable distribution publication, the stable update manifest, consolidated release state, fallback monitoring and recovery still mutate public `main`.

The migration is tracked by Issue #41. Authority is maintained in:

- `docs/BRANCH_WRITE_INVENTORY.md`;
- `.github/branch-write-inventory.json`;
- `.github/shadow-branch-policy.json`;
- `.github/scripts/test_branch_write_inventory.py`;
- `.github/scripts/test_validation_candidate_pipeline.py`;
- `.github/scripts/test_greasyfork_parity_pipeline.py`;
- `.github/scripts/test_release_announcement_state_pipeline.py`;
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
- deterministic dashboard, Greasy Fork and announcement-state verification;
- atomic primary release dashboard and announcement state;
- isolated non-live `release-state` and `distribution` branches;
- a manual-only, fixed-target shadow writer with read-only workflow permission.

## Completed migration stages

### Write-path inventory ✅

The 24 July 2026 baseline identified 10 direct public-main writers. Every `contents: write` workflow and executable main-ref mutation is classified and fail-closed in CI.

### Artifact-only validation and evidence ✅

Six workflows verify with read-only repository access and retained immutable evidence instead of committing generated state:

- canonical userscript validation;
- release dry runs;
- repository/dependency audits;
- release dashboard projection;
- Greasy Fork canonical parity;
- release announcement-state verification.

### GitHub source authority ✅

Automatic source importing is retired. GitHub is authoritative. Live Greasy Fork parity accepts canonical-ahead during publication and fails on live-ahead or equal-version content drift.

### Atomic primary announcement state ✅

Normal production releases no longer require a follow-up announcement reconciliation commit.

After Greasy Fork verification, private backup and Discord publication, `release-toolkit.yml` commits these together:

- `status/release-dashboard.json`;
- `status/README.md`;
- `.github/greasyfork-version.txt`.

The stable update manifest remains a separate guarded writer. It is dispatched and awaited in parallel with GitHub Pages.

Direct public-main writers remain reduced from **10 to 4**.

### Shadow branch topology and read-only parity ✅

PR #506 established:

- `release-state` for verified dashboard, manifest and announcement state;
- `distribution` for stable `dist/` and root userscript paths.

Both branches remain in `shadow-rehearsal` mode. `main` remains authoritative, live consumers are disabled, strict protection is disabled and administrator recovery remains mandatory.

`Verify Shadow Branch Parity` has read-only contents permission. It validates role declarations and governed-file parity, retains evidence for 30 days and performs no branch mutation.

## Constrained shadow writer rehearsal 🟡

The next stage introduces `.github/workflows/sync-shadow-branches.yml` and `.github/scripts/sync_shadow_branches.py` without changing live authority.

### Dispatch and authorization

- manual `workflow_dispatch` only;
- repository fixed to `Conroy1988/missionchief-toolkit-assets`;
- actor fixed to `Conroy1988`;
- dispatch ref must be `main`;
- checkout and `origin/main` must both equal an explicitly supplied 40-character source SHA;
- plan mode requires `PLAN SHADOW SYNC`;
- apply mode requires `SYNC SHADOWS`.

### Target and file boundaries

- allowed targets are exactly `release-state` and `distribution`;
- `main` is rejected as a target in both workflow and script;
- target branch roles must remain `shadow-rehearsal` and preserve main authority;
- only branch-specific governed paths may change;
- `.github/branch-role.json` cannot be copied or modified;
- pushes are fast-forward commits to the two reviewed shadow refs only;
- public `main` and live consumers remain unchanged.

### Credential boundary

The workflow itself retains `contents: read`. Plan mode uses no write credential. Apply mode temporarily receives the existing owner-authenticated `DEVELOPMENT_PR_TOKEN` solely for the reviewed shadow push.

This is a rehearsal identity, not the final architecture. It must be replaced by a narrowly scoped GitHub App restricted to the two operational branches before consumer cutover or strict protection.

### Rehearsal evidence

- plan/apply JSON, Markdown and logs retained for 30 days;
- post-operation read-only parity verification;
- optional idempotent empty probe commits to prove branch access when governed content already matches;
- no duplicate probe commit for the same source/target fingerprint;
- permanent static and executable contracts reject target expansion, workflow write permission, live cutover and `main` mutation.

## Remaining generated state

Public `main` still contains:

1. stable `dist/` and root Greasy Fork mirrors;
2. verified dashboard and announcement state;
3. stable update-manifest state;
4. fallback monitor state;
5. guarded recovery state.

These responsibilities must move before strict protection is safe.

## Target architecture

### Public `main`

Reviewed source, workflows, tests, policy, documentation and stable configuration only.

### Distribution branch

Stable `dist/` and root userscript mirrors required by Greasy Fork, written by a narrowly scoped release GitHub App.

### Release-state branch

Mutable dashboard, manifest, announcement, fallback-monitor and recovery state. It is operational evidence, never product source.

### Immutable evidence

Validation candidates, parity audits, synchronization plans, announcement checks, dashboard projections, release bundles, checksums, audits, dry runs and handovers remain GitHub Release assets or Actions artifacts.

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
3. ✅ Make dashboard and announcement state atomic; retire the reconciliation writer.
4. ⬜ Fold stable update-manifest publication into the consolidated release-state commit.
5. ✅ Create and verify non-live `release-state` and `distribution` branches — PR #506.
6. 🟡 Introduce the constrained owner-token shadow writer and rehearse plan/apply synchronization.
7. Replace the rehearsal credential with a narrowly scoped GitHub App.
8. Move consolidated release state and recovery state to `release-state`.
9. Move stable `dist/` and Greasy Fork mirrors to `distribution`.
10. Remove unnecessary `contents: write` from orchestration-only workflows.
11. Rehearse without public-main mutation:
   - normal Release Readiness;
   - full production publication;
   - Greasy Fork-only retry;
   - private-backup-only retry;
   - Discord-only retry;
   - dashboard reconstruction;
   - stable release-asset repair;
   - emergency rollback-candidate preparation.
12. Rehearse owner/admin access:
   - create and update an owner branch;
   - open and update a pull request;
   - auto-merge after green checks;
   - use PR-only administrator bypass where required;
   - repair distribution and release-state branches;
   - disable or amend the ruleset.
13. Require pull requests, approved checks, current branches and resolved conversations.
14. Block routine direct human pushes and enable strict protection only after complete rehearsal.

## Exit criteria

Strict protection is ready only when no workflow requires a public-main commit, every bypass actor is a scoped GitHub App or explicit administrator recovery actor, generated state is reconstructable, owner update speed is preserved, and every release/recovery/access path has passed non-production rehearsal.
