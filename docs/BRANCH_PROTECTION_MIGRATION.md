# Branch Protection Migration Plan

Strict pull-request-only protection is **not yet enabled**. The repository still permits controlled automation commits because production validation, distribution mirroring, release state, update manifests, monitoring and recovery currently mutate public `main`.

The migration is tracked by Issue #41. The reviewed writer inventory is maintained in:

- `docs/BRANCH_WRITE_INVENTORY.md` — human architecture and migration decisions;
- `.github/branch-write-inventory.json` — machine-readable authority;
- `.github/scripts/test_branch_write_inventory.py` — fail-closed drift enforcement.

## Current safe controls

- deletion protection;
- force-push protection;
- reviewed pull requests for normal development;
- code-integrity, performance, asset, recovery and documentation validation;
- immutable GitHub Action pins and permission auditing;
- owner-authenticated review branches for development packages and rollback preparation;
- explicit production and recovery confirmation phrases.

## Stage 1 — write-path inventory ✅

The 24 July 2026 audit against `main` commit `bfd3a786a17a2cf01a0aa0d3d6f9a3f235ab1f2c` identified:

- **10 direct public-`main` writing workflows**;
- **2 indirect release orchestrators** that invoke the reusable production writer;
- **2 owner-token review-branch writers** that cannot update public `main` directly;
- **1 separate private-repository `main` writer** used only for recovery backups.

Every workflow with declared `contents: write` authority is classified. CI now scans executable automation for direct `main` pushes and ref updates and fails when an unclassified writer appears.

No branch-protection setting is changed by Stage 1.

## Why strict PR-only enforcement remains deferred

The protected branch currently mixes several distinct data classes:

1. canonical userscript source and reviewed repository policy;
2. generated distribution files;
3. stable Greasy Fork root mirrors;
4. release dashboard and announcement state;
5. stable update-manifest state;
6. repository audit output;
7. generated human-readable dashboard files.

Blocking all direct automation pushes before these responsibilities are separated would stop normal releases, recovery operations or external update reconciliation. Granting an unrestricted personal token a bypass would merely replace one architectural risk with another.

## Target architecture

### Public `main`

Reviewed source, workflows, tests, policies, documentation and stable configuration only. Human changes arrive through pull requests with required checks and resolved conversations.

### Distribution branch

Stable root userscript mirrors required by Greasy Fork or replacement distribution tooling. Written only by a narrowly scoped release GitHub App.

### Release-state branch

Mutable generated state, including:

- release dashboard JSON and Markdown;
- Greasy Fork/Discord announcement tracker;
- stable update manifest;
- repository audit summaries;
- recovery claim and completion state.

This branch is operational evidence, not a competing product-code source.

### Immutable evidence

Validated release bundles, checksums, changelog extracts, migration handovers and dry-run evidence remain GitHub Release assets or Actions artifacts.

## Remaining migration stages

1. ✅ Inventory every workflow and script capable of updating public `main`.
2. Separate immutable canonical source from generated operational state.
3. Move dashboard, announcement, manifest and audit state to a dedicated release-state branch or immutable assets.
4. Move stable Greasy Fork mirrors to a dedicated distribution branch.
5. Introduce a narrowly scoped GitHub App identity for distribution and state writes.
6. Remove unnecessary `contents: write` authority from orchestration-only workflows.
7. Rehearse all supported paths without public-`main` mutation:
   - normal Release Readiness;
   - full production publication;
   - Greasy Fork-only retry;
   - private-backup-only retry;
   - Discord-only retry;
   - dashboard reconstruction;
   - stable release-asset repair;
   - emergency rollback-candidate preparation.
8. Require pull requests, approved checks, current branches and resolved conversations for human changes.
9. Block direct human pushes and enable strict protection only after the complete rehearsal passes.

## Exit criteria

Strict protection is ready only when:

- no workflow depends on a direct public-`main` commit;
- every bypass actor is a narrowly scoped and auditable GitHub App;
- personal tokens can write only owner-created review branches or the separate private recovery repository;
- generated release state can be reconstructed from immutable evidence;
- every release and recovery path passes a non-production rehearsal;
- a failed publication stage cannot leave release state split across GitHub, Greasy Fork, private backup and Discord.
