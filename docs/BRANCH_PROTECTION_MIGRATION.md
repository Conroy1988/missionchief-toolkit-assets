# Branch Protection Migration Plan

Issue #41 now has one remaining repository-setting action: enable strict pull-request-only protection for `main` after the TKB-only release-state cutover is verified in production.

## Completed architecture

### Public `main`

`main` contains reviewed source, workflows, tests, policy, documentation and release inputs. No workflow commits generated release state or distribution output back to it. The historical `status/` snapshot on `main` is frozen and has no live consumer.

### TKB Website

The TKB Website is the sole public install and automatic-update authority. GitHub Releases remain the immutable package archive. Greasy Fork is fully retired and has no operational role.

### Authoritative `release-state`

The `release-state` branch owns live operational data:

- release dashboard JSON and Markdown;
- stable update manifest;
- release-speed history and dashboard;
- release announcement version.

The Toolkit runtime and GitHub Pages consume this branch directly. There is no `main` manifest fallback.

`release-toolkit.yml` and `release-recovery.yml` are the only writers. Both delegate commits to `.github/scripts/release_state_branch.py`, which enforces the exact role, target, mutable paths, current ancestry and fast-forward-only push.

### Distribution branch

`distribution` remains a non-live mirror rehearsal. TKB Website delivery does not depend on it. The manual synchronizer may target only this branch; authoritative release-state is excluded from mirror synchronization.

### Immutable evidence

Canonical validation, release dry runs, audits, dashboard projection, announcement-state verification and update-manifest verification use read-only repository access and retain workflow artifacts.

## Production proof required before protection

The `v10.3.3` cutover release must demonstrate:

1. the exact validated PR tree publishes successfully;
2. TKB install, update and metadata endpoints serve the exact payload/version;
3. private backup and Discord confirmation succeed;
4. the complete verified ledger is committed only to `release-state`;
5. the merge commit remains the `main` head after release recording;
6. the Toolkit version check reads only release-state;
7. Pages deploys from reviewed `main` code plus authoritative release-state data;
8. read-only governance and recovery contracts remain green.

## Strict `main` protection target

Enable a branch rule or ruleset for `main` with:

- pull requests required;
- required status checks from the validated PR gate;
- branches required to be current before merge;
- unresolved conversations blocking merge;
- force pushes and deletions blocked;
- routine direct human and Actions pushes blocked;
- administrator access retained for explicit recovery and ruleset rollback;
- no mandatory external reviewer;
- auto-merge or merge queue retained when checks pass.

The exact rule must be applied only after the production proof above. It must then be tested with an owner branch update, PR merge, rejected direct push, and administrator rollback path.

## Authority and contracts

- `docs/BRANCH_WRITE_INVENTORY.md` — human-readable current topology;
- `.github/branch-write-inventory.json` — exact writer classification;
- `.github/shadow-branch-policy.json` — operational branch roles and consumers;
- `.github/scripts/test_branch_write_inventory.py` — direct-main mutation and permission enforcement;
- `.github/scripts/test_release_authority_pipeline.py` — TKB-only release authority;
- `.github/scripts/test_release_recovery_state_pipeline.py` — live recovery-state boundaries;
- `.github/scripts/test_shadow_branch_parity.py` — read-only operational branch governance;
- `.github/scripts/test_update_manifest_pipeline.py` — release-state-only manifest production and consumption.

## Exit criteria

Issue #41 can close when:

- `v10.3.3` is verified and recorded on release-state without a follow-up `main` commit;
- public `main` has zero direct workflow writers;
- the runtime and Pages have no `main` status fallback;
- strict protection is active and its owner/admin rehearsal succeeds;
- Issue #41 records the exact ruleset evidence and final branch SHAs.
