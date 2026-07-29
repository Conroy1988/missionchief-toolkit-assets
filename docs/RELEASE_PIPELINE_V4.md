# Release Pipeline v4 — Maximum-Speed Verified Delivery

Pipeline v4 builds one immutable release-ready candidate, resolves it by exact head SHA and exact artifact name, verifies it against the exact current `main` commit, reuses it without rebuilding, runs Greasy Fork verification and private backup concurrently, posts Discord only after both succeed, records timing telemetry, and dispatches GitHub Pages asynchronously.

The automatic path passes authoritative PR creation/merge timestamps plus implementation-ready and validation-completion timestamps directly into production. The release workflow also captures the candidate commit before the stable mirror commit, so telemetry cannot be attributed to release-state writes. The manual readiness workflow remains available for recovery releases where no immutable validation candidate is supplied.

## Targets

- Normal critical hotfix PR → verified release median: 4 minutes.
- Normal critical hotfix PR → verified release P90: 7 minutes.
- Merge → GitHub Release median: 40 seconds.
- Merge → fully verified release median: 60 seconds.

See `status/RELEASE_SPEED.md` for live measurements.

## Telemetry attribution

The live history records implementation-ready → green, green → merge, PR → verified, merge → GitHub Release, merge → verified ledger, Greasy Fork propagation and private backup. Historical null fields are never guessed; v8.2.7 is backfilled only from immutable GitHub commit, gate, pull-request and release evidence.
