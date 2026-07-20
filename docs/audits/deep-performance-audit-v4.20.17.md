# Toolkit v4.20.17 deep performance audit

This audit supports Issues #247 and #277. It is measurement-only: the audit branch must not modify the production userscript, distribution assets, version, release state or Greasy Fork channel.

## Locked baseline

- Production version: `4.20.17`
- Audit-start main commit: `2ae2e963c4eab8a8a49dd38b8dbb13c10917e791`
- Reconciled post-release main commit: `e6b4ce9754db1ff3236c517f546fcdba435ada3a`
- Verified production SHA-256: `6eb3c212187c68d4ccb75aad23261c71a1769c3f94cb1c3f5ac7290dc3bfe479`
- Open pull requests at audit start: none

The latest validated static budget records 2,029,383 source bytes and 31,802 source lines. The existing 32,000-line ceiling is therefore 99.4% utilised. Embedded CSS remains 866,334 bytes with 6,621 estimated rule blocks. Observer, scheduling, DOM-write and network call-site metrics remain baseline-locked.

## Deep-audit artefact

The `Deep Performance Audit` workflow installs the exact Acorn parser, runs `.github/scripts/deep_performance_audit.mjs` and publishes:

- `deep-performance-audit.json` — machine-readable function, scheduler, observer, selector and template inventory;
- `deep-performance-audit.md` — reviewed hotspot ranking and safety interpretation.

The tool records:

- AST-resolved function and callback boundaries, lines, bytes and weighted structural pressure;
- control-flow, DOM-read and DOM-write concentration assigned to the nearest function owner;
- scheduler ownership and delay/mode expressions;
- observer constructions, registrations, roots, options, subtree scope and visible teardown or registry signals;
- large embedded CSS, HTML and text templates;
- repeated literal selectors and their owning functions.

The Acorn-backed parser is mandatory. An earlier heuristic prototype was rejected after nested JavaScript syntax produced invalid function boundaries and incomplete observer ownership evidence.

## Interpretation boundary

Static evidence identifies where to profile. It does not prove that a large function, repeated selector or broad observer is slow in a live MissionChief session.

Runtime changes require equivalent browser-profiler scenarios from `tools/mcms-performance-profiler.user.js`, deterministic behaviour fixtures and an isolated rollback boundary.

The following changes are explicitly prohibited without additional evidence:

- combining observers with different lifecycle owners merely to reduce a count;
- retaining DOM references across replaced documents, dialogs, frames or controls without invalidation;
- changing stylesheet order, specificity or initial visibility guarantees without visual contracts;
- parallelising sequential network operations solely to reduce elapsed time;
- removing debounces or refreshes that protect live MissionChief replacement behaviour;
- merging unrelated optimisation candidates into one release.

## Planned progression

1. Publish and review the v4.20.17 AST-backed static inventory.
2. Run equivalent Desktop, Tablet and iOS-compatible profiler scenarios.
3. Rank candidates by expected user impact, evidence strength and regression risk.
4. Implement one low-risk, independently reversible optimisation per pull request.
5. Compare before/after static and browser evidence while all canonical gates remain mandatory.
