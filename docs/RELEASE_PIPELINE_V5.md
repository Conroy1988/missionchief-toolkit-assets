# Release Pipeline v5 — Direct Atomic Hotfix Lane

Pipeline v5 removes the remaining pre-merge construction bottleneck while preserving the verified Pipeline v4 publication path.

## Normal hotfix operating sequence

1. Start from the exact current `main` commit.
2. Build the complete candidate outside GitHub: canonical source, both distribution mirrors, manifests, changelog, documentation and targeted regression contracts.
3. Run JavaScript syntax, canonical validation, source/distribution parity and the complete retained preflight before the branch is changed.
4. Upload every changed file as an immutable Git blob with `create_blob`.
5. Create one repository tree with `create_tree`.
6. Create one commit with `create_commit`.
7. Advance the owner-created hotfix branch once with `update_ref`.
8. Open the pull request only after the complete candidate has passed local validation.
9. Enable auto-merge after the required CI gate is green.
10. Release the exact validated pull-request tree after merge without rebuilding or repeating canonical validation.

The normal lane must not create a temporary workflow, package fragment, permission override, diagnostic commit or self-cleaning writer.

The development-package workflow is recovery-only. It remains available when a connector cannot represent a required file, but it is not the default development transport.

## Validated-tree release authority

Canonical validation records:

- the checked-out validation commit;
- the pull-request head commit;
- the pull-request number;
- the complete Git repository tree SHA;
- the userscript SHA-256;
- the release version;
- the exact prepared release bundle.

After squash merge, the automatic release compares the merged `main` tree SHA with the validated pull-request tree SHA. An exact match authorises immediate reuse of the immutable candidate. A mismatch never releases the stale candidate; it dispatches a guarded validation of current `main` and uses that result as the fallback.

## Targets

- Candidate construction: one branch commit.
- PR opening to all release-critical checks: 90–150 seconds.
- Merge to GitHub Release: 15–30 seconds.
- Merge to fully verified release: 25–45 seconds.
- Normal critical hotfix request to verified release: 3–5 minutes.
