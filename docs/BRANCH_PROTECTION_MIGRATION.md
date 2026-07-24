# Branch Protection Migration Plan

Strict pull-request-only protection is **not yet enabled**. Controlled automation commits remain because stable distribution publication, release state, update manifests, monitoring and recovery still mutate public `main`.

The migration is tracked by Issue #41. Authority is maintained in:

- `docs/BRANCH_WRITE_INVENTORY.md`;
- `.github/branch-write-inventory.json`;
- `.github/scripts/test_branch_write_inventory.py`;
- `.github/scripts/test_validation_candidate_pipeline.py`.

## Current safe controls

- deletion and force-push protection;
- reviewed pull requests for normal development;
- code-integrity, performance, asset, recovery and documentation validation;
- immutable Action pins and permission auditing;
- owner-authenticated review branches for packages and rollback preparation;
- explicit production and recovery confirmation phrases;
- exact commit/ref/hash validation evidence for automatic releases;
- deterministic dashboard JSON/Markdown projection checks.

## Stage 1 — write-path inventory ✅

The 24 July 2026 baseline identified 10 direct public-main writers, two release orchestrators, two owner-token review-branch writers and one private-repository backup writer. Every `contents: write` workflow and executable main-ref mutation is classified and fail-closed in CI.

## Stage 2 — validation and generated-evidence separation ✅

### Release dry runs ✅

Release dry runs are read-only and artifact-only. They validate and package a candidate, retain deterministic JSON/Markdown evidence for 30 days and explicitly prove that no release or branch channel changed.

### Repository and dependency audits ✅

Repository audits are read-only and artifact-only. They retain commit-scoped JSON/Markdown evidence for 90 days and never rewrite production release state.

### Canonical validation candidates ✅

Canonical validation no longer commits `dist/` or transient dashboard candidate fields.

The workflow:

- has `contents: read` only;
- checks out without persisted credentials;
- validates canonical source, documentation, JavaScript syntax and distribution parity;
- writes exact commit/ref/version/SHA-256 evidence;
- uploads `missionchief-toolkit-validation-candidate-<commit>` for 14 days;
- proves that public `main` and the release dashboard were not changed.

Automatic release downloads the artifact from the exact triggering workflow run, verifies all hashes and paths, rejects a stale commit when `main` has advanced, and checks the GitHub Release tag directly. The owner release command performs a fresh validation of current `main`.

Stable public `dist/` paths remain current because `release-toolkit.yml` publishes `dist/` and the two root Greasy Fork mirrors together after readiness passes and production release begins.

### Dashboard projection ✅

The standalone dashboard refresher no longer commits `status/README.md`.

Production release and recovery already generate `status/README.md` in the same commit as `status/release-dashboard.json`. The former follow-up writer duplicated that work and created an unnecessary additional commit.

`update-release-dashboard.yml` now:

- has `contents: read` only;
- checks out the exact event state with persisted credentials disabled;
- validates the JSON ledger;
- renders the dashboard to `dashboard-projection/status-README.md` using `--check`;
- fails when ledger sanitation would change committed JSON;
- compares the generated Markdown byte-for-byte with `status/README.md`;
- uploads the projection, diff and log for 30 days;
- never commits, pushes or changes release state.

Direct public-main writers are reduced from **10 to 6**.

## Remaining generated state

The protected branch still mixes:

1. canonical userscript source and policy;
2. stable distribution and root Greasy Fork mirrors;
3. release dashboard and announcement state;
4. stable update-manifest state.

The remaining writers cannot be disabled until those data classes are moved and every release/recovery path is rehearsed.

## Target architecture

### Public `main`

Reviewed source, workflows, tests, policy, documentation and stable configuration only.

### Distribution branch

Stable `dist/` and root userscript mirrors required by Greasy Fork, written only by a narrowly scoped release GitHub App.

### Release-state branch

Mutable dashboard, announcement, manifest and recovery state. It is operational evidence, never a competing source for product code.

### Immutable evidence

Validation candidates, dashboard projections, release bundles, checksums, audits, dry runs, changelog extracts and handovers remain GitHub Release assets or Actions artifacts.

## Access and speed requirements

The final protection design must retain fast owner operation:

- `Conroy1988` remains repository administrator and recovery authority;
- normal changes use owner-created branches and fast parallel CI;
- no mandatory external reviewer is introduced;
- admin bypass, where configured, is limited to pull-request operation rather than routine direct pushes;
- auto-merge should be enabled after the workflow and settings rehearsal;
- distribution and release-state branches retain explicit administrator recovery access;
- strict enforcement is not enabled until branch creation, PR update, merge, release, recovery and ruleset rollback access are all proven.
- `Verify release-dashboard projection` is designated as a future required status check whenever the ledger, renderer or projection workflow changes.

## Remaining migration stages

1. ✅ Inventory every workflow and script capable of updating public `main`.
2. ✅ Separate validation, dry-run, audit and dashboard-projection evidence from public `main`.
3. Move dashboard, announcement and manifest state to a release-state branch or immutable assets.
4. Move stable `dist/` and Greasy Fork mirrors to a distribution branch.
5. Introduce a narrowly scoped GitHub App identity.
6. Remove unnecessary `contents: write` from orchestration-only workflows.
7. Rehearse without public-main mutation:
   - normal Release Readiness;
   - full production publication;
   - Greasy Fork-only retry;
   - private-backup-only retry;
   - Discord-only retry;
   - dashboard reconstruction;
   - stable release-asset repair;
   - emergency rollback-candidate preparation.
8. Rehearse owner/admin access:
   - create and update an owner branch;
   - open and update a pull request;
   - auto-merge after green checks;
   - use PR-only administrator bypass where required;
   - repair distribution and release-state branches;
   - disable or amend the ruleset.
9. Require pull requests, approved checks, current branches and resolved conversations.
10. Block direct human pushes and enable strict protection only after complete rehearsal.

## Exit criteria

Strict protection is ready only when no workflow requires a public-main commit, every bypass actor is a scoped GitHub App or explicit administrator recovery actor, generated state is reconstructable, owner update speed is preserved, and every release/recovery/access path has passed non-production rehearsal.
