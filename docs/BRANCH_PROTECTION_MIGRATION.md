# Branch Protection Migration Plan

Strict pull-request-only protection is **not yet enabled**. Controlled automation commits remain because production validation, distribution mirroring, release state, update manifests, monitoring and recovery still mutate public `main`.

The migration is tracked by Issue #41. Authority is maintained in:

- `docs/BRANCH_WRITE_INVENTORY.md`;
- `.github/branch-write-inventory.json`;
- `.github/scripts/test_branch_write_inventory.py`.

## Current safe controls

- deletion and force-push protection;
- reviewed pull requests for normal development;
- code-integrity, performance, asset, recovery and documentation validation;
- immutable Action pins and permission auditing;
- owner-authenticated review branches for packages and rollback preparation;
- explicit production and recovery confirmation phrases.

## Stage 1 — write-path inventory ✅

The 24 July 2026 baseline identified 10 direct public-main writers, two release orchestrators, two owner-token review-branch writers and one private-repository backup writer. Every `contents: write` workflow and executable main-ref mutation is now classified and fail-closed in CI.

## Stage 2 — generated-state separation in progress

### Release dry runs ✅

Release dry runs are read-only and artifact-only. They validate and package a candidate, retain deterministic JSON/Markdown evidence for 30 days and explicitly prove that no release or branch channel changed.

### Repository and dependency audits ✅

Repository audits are now read-only and artifact-only.

The workflow:

- checks out `main` with `persist-credentials: false`;
- audits repository files, workflows, public raw paths, Greasy Fork references, secrets and duplicate media;
- writes JSON and Markdown under `repository-audit-output/`;
- uploads `missionchief-repository-audit-<commit>` for 90 days;
- records that public `main` and the release dashboard were not changed;
- no longer rewrites production version, validation, asset or timestamp fields.

The old committed audit described v4.13.1 and wrote a fixed `2026-07-14` dashboard timestamp. Those committed files now identify themselves as legacy snapshots rather than current evidence.

Direct public-main writers are reduced from **10 to 8**.

### Remaining generated state

The protected branch still mixes:

1. canonical userscript source and policy;
2. generated distribution candidates;
3. stable Greasy Fork root mirrors;
4. release dashboard and announcement state;
5. stable update-manifest state;
6. generated human-readable dashboard files.

The remaining writers cannot be disabled until their data is moved and every release/recovery path is rehearsed.

## Target architecture

### Public `main`

Reviewed source, workflows, tests, policy, documentation and stable configuration only.

### Distribution branch

Stable root userscript mirrors required by Greasy Fork, written only by a narrowly scoped release GitHub App.

### Release-state branch

Mutable dashboard, announcement, manifest and recovery state. It is operational evidence, never a competing source for product code.

### Immutable evidence

Validated bundles, checksums, audits, dry runs, changelog extracts and handovers remain GitHub Release assets or Actions artifacts.

## Remaining migration stages

1. ✅ Inventory every workflow and script capable of updating public `main`.
2. 🟡 Separate canonical source from generated operational state.
   - [x] Convert release dry runs to artifact-only evidence.
   - [x] Convert repository audits to artifact-only evidence.
   - [ ] Move validated distribution-candidate output away from public `main`.
3. Move dashboard, announcement and manifest state to a release-state branch or immutable assets.
4. Move stable Greasy Fork mirrors to a distribution branch.
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
8. Require pull requests, approved checks, current branches and resolved conversations.
9. Block direct human pushes and enable strict protection only after complete rehearsal.

## Exit criteria

Strict protection is ready only when no workflow requires a public-main commit, every bypass actor is a scoped GitHub App, generated state is reconstructable, and every release/recovery path has passed non-production rehearsal.
