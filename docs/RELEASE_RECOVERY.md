# Release Recovery and Failure Handling

This guide describes how to recover the MissionChief Map Command Toolkit release pipeline without duplicate releases, repeated Discord announcements, silent version downgrades or inconsistent operational state.

## Standard pre-release procedure

Before every public release:

1. Confirm the canonical userscript contains the intended `@version`.
2. Confirm `CHANGELOG.md` contains a matching section for that exact version.
3. Run **Actions → Release Readiness Check** with the intended version.
4. Continue only when every readiness step is green.
5. Run **Actions → Release Toolkit**.
6. Enter the exact version and type `RELEASE`.

The readiness workflow does not create a GitHub Release, change Greasy Fork, post to Discord or write to the private migration repository.

## Recovery state location

The governed recovery ledger is stored on the `release-state` branch:

- `status/release-dashboard.json`;
- `status/README.md`;
- `status/update-manifest.json`;
- `.github/greasyfork-version.txt`.

`release-recovery.yml` never commits these files to public `main`. It prepares a detached release-state worktree, validates the branch role and mutable-path allowlist, then performs a normal non-force push through `.github/scripts/release_state_branch.py`.

Existing v5.0.7 installations still read the compatibility manifest from `main`. Recovery operations update the operational ledger only; the next normal production release refreshes the compatibility copy on `main`.

## Executable recovery workflows

Two manual workflows provide controlled recovery operations:

- **Actions → Release Recovery** performs narrow, idempotent repairs on an existing release.
- **Actions → Prepare Release Rollback** restores a previously verified implementation into a new higher version and opens a review pull request.

Both workflows use explicit confirmation phrases. Replace the angle-bracket placeholders with the version values entered in the workflow form.

| Operation | Confirmation phrase | Public effect |
|---|---|---|
| Verify immutable release bundle | `VERIFY <version>` | Read-only |
| Retry Greasy Fork release event and verification | `RETRY GREASYFORK <version>` | Re-saves the existing latest GitHub Release; creates no new release |
| Retry private migration backup | `RETRY BACKUP <version>` | Creates a missing archive or reuses an identical existing archive |
| Retry Discord release announcement | `RETRY DISCORD <version>` | Posts only when the recovery ledger does not already record the announcement |
| Rebuild dashboard state | `REBUILD DASHBOARD <version>` | Reconstructs release-state from verified GitHub, Greasy Fork and private archive evidence |
| Repair stable GitHub Release asset names | `REPAIR ASSETS <version>` | Restores stable `.user.js` and `.txt` assets from immutable versioned assets |
| Prepare reviewed rollback | `PREPARE ROLLBACK <source> TO <recovery>` | Opens a PR; does not publish anything |

## Direct recovery restrictions

Write operations in **Release Recovery** may target only the current latest GitHub Release. This prevents an archived version from replacing active distribution state.

The workflow shares the `toolkit-production-release` concurrency lock with formal production and fallback monitoring. Recovery cannot overlap a production release or fallback announcement reconciliation.

The workflow checks out `main` with `persist-credentials: false`. `main` supplies source code, reviewed settings and a compatibility seed when `release-state` does not yet contain the requested release. Every later ledger transition occurs on `release-state`.

## Discord ambiguity guard

Before retrying Discord, the workflow commits a `pending` recovery claim to the release-state dashboard. Only then does it post the message.

- If the post succeeds, the workflow records `discordPosted: true`, removes the pending claim, advances the announcement tracker and regenerates the stable manifest.
- If the runner fails after Discord accepted the message but before final state is committed, the pending claim remains on `release-state`.
- A later automatic retry refuses to post while that claim exists. Discord must be inspected manually before the ambiguous state is cleared.
- Finalisation succeeds only when the expected claim nonce still matches the current release-state claim.

This deliberately prefers a missed automatic retry over a duplicate public announcement.

## Private backup idempotency

A backup retry behaves as follows:

- missing versioned archive → create it;
- existing byte-identical archive → reuse it and repair only the `current/` pointer if necessary;
- existing archive with any mismatch → fail closed without overwriting the immutable backup.

The resulting private backup commit is written to the release-state dashboard, not public `main`.

## Rollback policy

Never publish an older version number as a rollback. Userscript managers generally do not treat lower versions as an update.

**Prepare Release Rollback** instead:

1. Downloads and verifies the selected historical GitHub Release bundle.
2. Restores its executable userscript implementation.
3. Changes only the metadata version to a new version higher than the current release.
4. Adds an emergency recovery changelog section.
5. Rebuilds and validates the distribution files.
6. Runs JavaScript syntax and static performance checks.
7. Opens a labelled review PR.

After that PR is reviewed and merged, use the normal **Release Readiness Check** and **Release Toolkit** workflows. Rollback preparation never creates a release, changes Greasy Fork, writes the private backup or posts to Discord.

## Release checkpoints

The production workflow proceeds in this order:

```text
Canonical validation
      ↓
Release bundle and hashes
      ↓
GitHub Release
      ↓
Greasy Fork webhook and version verification
      ↓
Private migration backup
      ↓
Discord release announcement
      ↓
Atomic compatibility state on main
```

Recovery writes its operational ledger to `release-state`; it does not rewrite the compatibility checkpoint on `main`.

A later checkpoint is never treated as successful when an earlier checkpoint failed.

## Recovery by failure stage

### Validation or bundle preparation failed

No public state has changed.

- Correct the source, metadata, changelog or distribution mismatch.
- Run **Release Readiness Check** again.
- Start a new **Release Toolkit** run only after readiness passes.

### GitHub Release creation failed

Check whether tag `vX.Y.Z` or a release with that version already exists.

- When no release exists, correct the permission or file problem and start a new production run.
- When a partial release exists, inspect its assets before deciding whether to delete and recreate it.
- Never create a second release under a different tag for the same Toolkit version.

### Stable GitHub Release assets are missing or damaged

Run **Release Recovery → repair-stable-assets** with `REPAIR ASSETS <version>`.

The immutable versioned `.user.js`, `.txt`, manifest and checksums are the source of truth. The workflow restores only the stable asset names, verifies SHA-256 and re-saves the existing release. No repository branch is changed by this operation.

### GitHub Release exists but Greasy Fork did not update

Do not post a manual Discord announcement.

1. Verify the GitHub Release bundle with `VERIFY <version>`.
2. Run **Release Recovery → retry-greasyfork** with `RETRY GREASYFORK <version>`.
3. The workflow re-saves the existing release only when Greasy Fork is stale.
4. It waits for matching metadata and verifies public asset health plus executable-body parity.
5. It records Greasy Fork as verified on `release-state` only after those checks pass.

### Greasy Fork updated but private backup failed

The public release is live, but recovery state is incomplete.

- Fix or renew `MIGRATION_REPO_TOKEN`.
- Confirm the token has Contents read/write permission for the private repository.
- Run **Release Recovery → retry-private-backup** with `RETRY BACKUP <version>`.
- Confirm the workflow summary records the private backup commit SHA.
- Do not post a manual release announcement while backup recovery is incomplete.

### Backup succeeded but Discord failed

- Verify `DISCORD_RELEASE_WEBHOOK` still targets `Mission-Chief`.
- Confirm release-state records Greasy Fork verification and a private backup commit.
- Run **Release Recovery → retry-discord** with `RETRY DISCORD <version>`.
- When `discordPosted` is already true, the workflow exits without posting.
- When a previous retry is marked pending, inspect Discord manually rather than forcing another post.
- Never use the development webhook for a public release.

### Dashboard update failed after public actions succeeded

Run **Release Recovery → rebuild-dashboard** with `REBUILD DASHBOARD <version>`.

The workflow verifies:

- the immutable GitHub Release bundle and SHA-256;
- the matching Greasy Fork metadata version;
- the private archive version and hash;
- the private backup commit.

Choose the Discord state deliberately:

- `preserve` only when release-state already records the same release version;
- `posted` when the release message was verified in Discord;
- `not-posted` when it was not posted and should remain eligible for the guarded Discord retry.

The workflow regenerates the release-state dashboard and rendered Markdown. When Discord is recorded as posted, it also advances the tracker and regenerates the stable manifest.

## Duplicate prevention

- Do not use **Re-run all jobs** after a GitHub Release has already been created unless the checkpoint is known to be idempotent.
- Prefer the scoped **Release Recovery** operation for the failed stage.
- Do not publish the same version twice.
- Do not manually post to Discord while a guarded retry is pending.
- Do not edit recovery-ledger files directly on `main`.
- Do not use the manual shadow synchronizer to copy `main` state onto `release-state`; it has no file-copy authority there.
- Do not mark an older release as latest to simulate a downgrade.

## Private recovery verification

For any archived release, the following must agree:

- userscript `@version`;
- versioned directory name;
- release manifest version;
- changelog heading;
- GitHub tag;
- SHA-256 recorded in `SHA256SUMS` and the manifest;
- byte identity of `.user.js` and `.txt`;
- stable and versioned release assets when stable names are present.

The private repository is the authoritative disaster-recovery archive. The public GitHub Release is the distribution archive. Greasy Fork remains the installation endpoint. `release-state` is the operational recovery ledger.
