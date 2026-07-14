# Release Recovery and Failure Handling

This guide describes how to recover the MissionChief Map Command Toolkit release pipeline without creating duplicate releases, repeated Discord announcements, or inconsistent Greasy Fork state.

## Standard pre-release procedure

Before every public release:

1. Confirm the canonical userscript contains the intended `@version`.
2. Confirm `CHANGELOG.md` contains a matching section for that exact version.
3. Run **Actions → Release Readiness Check** with the intended version.
4. Continue only when every readiness step is green.
5. Run **Actions → Release Toolkit**.
6. Enter the exact version and type `RELEASE`.

The readiness workflow does not create a GitHub Release, change Greasy Fork, post to Discord, or write to the private migration repository.

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
Dashboard update
```

A later checkpoint is never treated as successful when an earlier checkpoint failed.

## Recovery by failure stage

### Validation or bundle preparation failed

No public state has changed.

- Correct the source, metadata, changelog, or distribution mismatch.
- Run **Release Readiness Check** again.
- Start a new **Release Toolkit** run only after readiness passes.

### GitHub Release creation failed

Check whether tag `vX.Y.Z` or a release with that version already exists.

- When no release exists, correct the reported permission or file problem and start a new production run.
- When a partial release exists, inspect its assets before deciding whether to delete and recreate it.
- Never create a second release under a different tag for the same Toolkit version.

### GitHub Release exists but Greasy Fork did not update

Do not post a manual Discord announcement.

1. Verify the GitHub Release contains `MissionChief_Map_Command_Toolkit.user.js`.
2. Verify Greasy Fork Source Syncing still points to the `releases/latest/download` URL.
3. Inspect the GitHub webhook delivery for the Release event.
4. Redeliver the webhook when the payload failed.
5. Use Greasy Fork **Update and sync now** only after confirming the release asset is correct.
6. Verify the Greasy Fork metadata endpoint reports the expected version.

### Greasy Fork updated but private backup failed

The public release is live, but the release is not complete.

- Do not send a manual release post.
- Fix or renew `MIGRATION_REPO_TOKEN`.
- Confirm the token has Contents read/write permission for the private repository.
- Re-run the failed backup-capable workflow job or perform a controlled recovery run.
- Confirm the private repository commit contains the complete versioned bundle and current recovery copy.

### Backup succeeded but Discord failed

- Verify `DISCORD_RELEASE_WEBHOOK` still targets `Mission-Chief`.
- Re-run only the failed Discord job when available.
- Confirm the dashboard has not already recorded `discordPosted: true` before manually retrying.
- Never use the development webhook for a public release.

### Dashboard update failed after all public actions succeeded

- Treat the release as published, but dashboard state as stale.
- Re-run the failed dashboard job or update `status/release-dashboard.json` from the verified release state.
- Regenerate `status/README.md` with `.github/scripts/generate_release_dashboard.py`.

## Duplicate prevention

- Do not use **Re-run all jobs** after a GitHub Release has already been created unless the workflow is known to be idempotent at that checkpoint.
- Prefer **Re-run failed jobs**.
- Do not publish the same version twice.
- Do not manually post to Discord while a workflow retry is pending.
- Do not change the Greasy Fork source back to `main/dist`.

## Private recovery verification

For any archived release, the following must agree:

- userscript `@version`;
- versioned directory name;
- release manifest version;
- changelog heading;
- GitHub tag;
- SHA-256 recorded in `SHA256SUMS` and the manifest;
- byte identity of `.user.js` and `.txt`.

The private repository is the authoritative disaster-recovery archive. The public GitHub Release is the distribution archive. Greasy Fork remains the installation endpoint.
