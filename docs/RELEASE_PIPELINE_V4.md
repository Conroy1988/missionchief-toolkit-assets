# Release Pipeline v4 — Maximum-Speed Verified Delivery

Pipeline v4 builds one immutable release-ready candidate, verifies it against the exact current `main` commit, reuses it without rebuilding, runs Greasy Fork verification and private backup concurrently, posts Discord only after both succeed, records timing telemetry, and dispatches GitHub Pages asynchronously.

The manual readiness workflow remains available for recovery releases where no immutable validation candidate is supplied.

## Targets

- Normal critical hotfix PR → verified release median: 4 minutes.
- Normal critical hotfix PR → verified release P90: 7 minutes.
- Merge → GitHub Release median: 40 seconds.
- Merge → fully verified release median: 60 seconds.

See `status/RELEASE_SPEED.md` for live measurements.
