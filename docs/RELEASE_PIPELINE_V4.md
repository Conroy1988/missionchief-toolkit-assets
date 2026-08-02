# Release Pipeline v4 — Maximum-Speed Verified Delivery

Pipeline v4 builds one immutable release-ready candidate, resolves the exact successful head run, requires exactly one non-expired candidate artifact from that run, verifies its embedded PR head, PR number and repository tree against the exact current `main` commit, reuses it without rebuilding, verifies the live TKB Website assets, writes a private recovery backup, posts Discord only after both succeed, records timing telemetry, and dispatches GitHub Pages asynchronously.

The automatic path passes authoritative PR creation/merge timestamps plus implementation-ready and validation-completion timestamps directly into production. The release workflow captures the candidate commit before the operational release-state transaction, so telemetry remains attributed to the reviewed `main` source rather than the later state commit. Public `main` is not rewritten by release recording. The manual readiness workflow remains available for recovery releases where no immutable validation candidate is supplied.

## Targets

- Normal critical hotfix PR → verified release median: 4 minutes.
- Normal critical hotfix PR → verified release P90: 7 minutes.
- Merge → GitHub Release median: 40 seconds.
- Merge → fully verified release median: 60 seconds.

See the [`release-state` speed dashboard](https://github.com/Conroy1988/missionchief-toolkit-assets/blob/release-state/status/RELEASE_SPEED.md) for live measurements.

## Telemetry attribution

The live history records implementation-ready → green, green → merge, PR → verified, merge → GitHub Release, merge → verified ledger, first-party TKB propagation and private backup. Historical null fields are never guessed; v8.2.7 is backfilled only from immutable GitHub commit, gate, pull-request and release evidence.


The candidate artifact filename may use GitHub's pull-request test-merge SHA. Filename suffixes are therefore not release authority; the exact successful workflow run and the candidate's embedded head/PR/tree evidence are authoritative. Zero or multiple candidate artifacts fail closed to the guarded current-`main` validation path.


The workflow-run fallback listens to the live `Toolkit Hotfix Gate` workflow name. v8.3.1 is the controlled genuine-release proof for exact-run artifact promotion and complete telemetry attribution.
