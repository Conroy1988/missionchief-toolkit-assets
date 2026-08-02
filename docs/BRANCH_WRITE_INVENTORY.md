# Protected-branch write inventory

**Reviewed:** 2 August 2026
**Issue:** #41 — TKB-only release-state cutover and strict `main` protection

## Current conclusion

No workflow can commit directly to public `main`; in machine-checked terms, no workflow can commit directly to public `main`. Production release recording and recovery state are isolated on the authoritative `release-state` branch, while source, workflows and reviewed distribution inputs remain pull-request-only on `main`.

Two workflows write governed operational state to `release-state`:

The enforced inventory therefore records that two workflows write governed operational state to `release-state`.

- `release-toolkit.yml` records the verified production dashboard, rendered status, stable manifest, release-speed telemetry and announcement version.
- `release-recovery.yml` performs guarded dashboard, backup, Discord and manifest recovery transitions.

The release and recovery ledgers are written only to `release-state`. Both writers use `.github/scripts/release_state_branch.py`, which validates the branch role and exact mutable-path allowlist, rejects force pushes and role mutations, detects concurrent branch movement and can never target `main`.

All external userscript distribution and parity monitoring is retired. The TKB Website is the sole install and automatic-update channel. Greasy Fork has no publication, verification, recovery, discovery or announcement role.

`.github/branch-write-inventory.json` is the machine-readable writer authority. `.github/shadow-branch-policy.json` declares the live release-state role and the still non-live distribution mirror.

## Public `main`

The direct writer inventory and direct-main push-source inventory are empty. Release automation checks out the exact validated `main` candidate with persisted credentials disabled, performs external publication, then commits operational evidence only through the constrained release-state helper.

The `status/` files retained on `main` are a frozen historical snapshot. They are not the version-check, Pages or release-recovery authority and are not rewritten after releases.

The two reusable-release orchestrators remain:

| Workflow | Role | Direct branch mutation |
|---|---|---|
| `auto-release-after-validation.yml` | Promotes the exact successful PR validation tree | None |
| `owner-release-command.yml` | Owner-authorized fresh validation and release invocation | None |

## Authoritative `release-state`

The live governed paths are:

- `status/release-dashboard.json`;
- `status/README.md`;
- `status/update-manifest.json`;
- `status/release-speed-history.json`;
- `status/RELEASE_SPEED.md`;
- `.github/release-announcement-version.txt`.

The branch role declares `mode: operational-release-state`, enables live consumers and states that release-state is authoritative for verified production status. Administrator recovery remains mandatory. Normal writers perform fast-forward-only `HEAD:refs/heads/release-state` pushes using `github.token`; the role file remains immutable to those writers.

The Toolkit runtime reads only:

`raw.githubusercontent.com/Conroy1988/missionchief-toolkit-assets/release-state/status/update-manifest.json`

There is no `main` manifest fallback.

## Production release sequence

1. Canonical validation uploads exact immutable candidate evidence.
2. Automatic release verifies that evidence and the exact merged `main` SHA.
3. The release workflow validates the live release-state role before public side effects.
4. GitHub Release and TKB Website publication complete and the live TKB install, update and metadata endpoints are byte/version verified.
5. Private backup and Discord release announcement complete.
6. Dashboard, manifest, telemetry and announcement state are generated in a detached release-state worktree.
7. The constrained helper commits the complete operational transaction to `release-state`; public `main` is unchanged.
8. GitHub Pages is dispatched asynchronously and overlays its status inputs from release-state.

## Release recovery

`.github/scripts/release_recovery_state.py` owns recovery-ledger transitions on the current authoritative branch state. It no longer seeds from a compatibility snapshot on `main`.

Recovery can:

- record a verified private-backup retry;
- claim a Discord retry before posting and finalise only the matching nonce;
- rebuild the dashboard from verified GitHub Release, TKB and private-backup evidence;
- regenerate the stable manifest only after complete evidence;
- repair stable GitHub Release assets without repository-state mutation.

The release recovery ledger is now written only to `release-state`, and every state commit is delegated to `release_state_branch.py`.

## Pages and read-only verification

Pages checks out reviewed site code from `main`, then overlays dashboard, manifest and telemetry files from the exact current release-state ref before validation and deployment. The production monitor applies the same overlay before comparing live pages with the verified version.

Canonical validation, release dry runs, repository audits, dashboard projection, announcement-state verification and stable update-manifest verification remain artifact-only. These six workflows use read-only repository access and retain immutable evidence instead of committing generated state.

The exact artifact-only workflows are `validate-userscript.yml`, `release-toolkit-dry-run.yml`, `repository-audit.yml`, `update-release-dashboard.yml`, `reconcile-release-announcement-state.yml` and `publish-update-manifest.yml`.

## Distribution branch rehearsal

The `distribution` branch remains non-live and mirror-only. `.github/workflows/sync-shadow-branches.yml` may synchronize only `distribution` from an exact reviewed `main` SHA, using the temporary `DEVELOPMENT_PR_TOKEN` in an owner-confirmed manual rehearsal.

The manual synchronizer has no file-copy authority on `release-state`; that branch is excluded as a synchronization target. Its remaining contract keeps public `main` rejected as a target, uses normal non-force pushes, preserves `.github/branch-role.json` and forbids live distribution cutover.

The read-only `verify-shadow-branch-parity.yml` still validates both branch roles. It schema-checks live release-state operational files and verifies distribution mirrors against `main`.

## Writer inventory

| Class | Workflows | Target |
|---|---|---|
| Direct public-main writers | None | — |
| Release-state writers | `release-toolkit.yml`, `release-recovery.yml` | `release-state` |
| Release orchestrators | `auto-release-after-validation.yml`, `owner-release-command.yml` | Reusable workflow invocation |
| Artifact-only evidence | Six read-only workflows | Workflow artifacts |
| Review-branch writers | Development-package and rollback workflows | Owner PR branches only |
| Distribution rehearsal | `sync-shadow-branches.yml` | `distribution` only |
| External backup | `backup_release_to_private_repo.sh` | Private repository `main` |

## Migration evidence

- PRs #498–#504 reduced direct public-main writers from 10 to 4.
- PR #505 reduced them from 4 to 3.
- PR #508 reduced them from 3 to 2.
- The recovery-ledger migration reduced them from 2 to 1.
- PR #653 released the `v10.3.2` release-state-first compatibility bridge and seeded its exact verified production state.
- This cutover removes the final main writer, removes the runtime fallback and makes release-state the sole production-state authority.
- TKB Website remains the sole distribution authority throughout.

Strict `main` protection is the remaining repository-setting action after the production cutover is verified.
