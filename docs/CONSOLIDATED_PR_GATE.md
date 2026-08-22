# Consolidated Pull-Request Gate

Pipeline v5.3 runs release-critical pull-request validation through one path-aware **Toolkit Hotfix Gate** job on one GitHub runner.

## Sequential path-aware checks

1. **Classify** the exact changed paths without provisioning another runner.
2. **Screen** the generated source fingerprint, documentation and JavaScript syntax before expensive work.
3. **Budget** lightweight performance growth against the exact pull-request base.
4. **Validate** canonical source and generated distribution when integrity or release-candidate work is required.
5. **Provision** the pinned UI dependencies only after the cheap checks pass.
6. **Exercise** rendered UI, deterministic runtime, local-development and workflow-policy contracts when selected.
7. **Package** one immutable exact-tree release candidate on the same checkout.

Every command in these stages is owned by `tools/candidate_gate.py`. Local `./toolkit promote` runs the same ordered catalog, including documentation consistency and the performance budget, before GitHub publication.

The **Toolkit Hotfix Gate** succeeds only when every classifier-required step succeeds. Work that is explicitly unnecessary is skipped within that job, so GitHub receives one required result instead of a fan-out of parallel lanes.

Exhaustive static and ESLint analysis, deep AST analysis and external stable-channel parity remain available through dedicated scheduled or manually dispatched workflows. Unknown paths fail closed by selecting all relevant single-runner checks and candidate generation.

Legacy workflows retain their manual, scheduled and production triggers, but no longer provision separate pull-request runners. Pipeline v5 validated-tree promotion continues to consume the exact immutable candidate from product-changing pull requests, while non-product merges stop before artifact lookup or fallback validation.
