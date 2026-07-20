# Toolkit v4.20.17 deep performance audit

This audit supports Issues #247 and #277. It is measurement-only: the audit branch does not modify the production userscript, distribution assets, version, release state or Greasy Fork channel.

## Locked baseline

- Production version: `4.20.17`
- Audit-start main commit: `2ae2e963c4eab8a8a49dd38b8dbb13c10917e791`
- Reconciled post-release main commit: `e6b4ce9754db1ff3236c517f546fcdba435ada3a`
- Verified production SHA-256: `6eb3c212187c68d4ccb75aad23261c71a1769c3f94cb1c3f5ac7290dc3bfe479`
- Open pull requests at audit start: none

The validated static budget records 2,029,383 source bytes and 31,802 source lines. The existing 32,000-line ceiling is therefore 99.4% utilised. Embedded CSS remains 866,334 bytes with 6,621 estimated rule blocks.

## Verified inventory

The final Acorn-backed inventory recorded:

- 1,715 functions and callbacks;
- 121 scheduler call sites;
- 12 `MutationObserver` constructions;
- 4 `ResizeObserver` constructions;
- 10 broad `subtree: true` registrations: eight locally resolved and two cross-function registrations;
- three cross-function `.observe()` calls, all associated with the shared main mutation observer;
- exact agreement with the trusted observer-construction and broad-subtree baseline.

The outer userscript wrapper is excluded from hotspot rankings. A previous heuristic parser was rejected after nested JavaScript syntax produced invalid function boundaries and incomplete observer ownership evidence.

## Highest structural pressure

1. `installMainStyles` — 12,224 lines and an 831,307-byte embedded CSS template. This is a major parsing and maintenance surface, but changing delivery or ordering is high-risk and requires live first-paint evidence plus visual contracts.
2. `updateUI` — 204 lines, 52 DOM-read sites and 49 DOM-write sites.
3. `triggerPayoutFlash` — 208 lines, 22 DOM-read sites, 10 DOM-write sites and three scheduler sites.
4. `toggleFeature` and `handleSettingChange` — high control-flow density; structural complexity is not by itself evidence of runtime cost.
5. `boot` — 309 lines, three scheduler sites and main observer lifecycle ownership.

## Ranked optimisation queue

### 1. Unchanged root-attribute writes — low risk

`applyRootAttributes()` performs 22 unconditional `setAttribute()` calls whenever `updateUI()` runs. The first isolated runtime optimisation should preserve all computed state and layout resolution while skipping only attributes whose existing string value is already identical.

Required parity contract:

- the same 22 attribute names and values are produced;
- changed state updates immediately;
- unchanged repeated calls perform zero attribute mutations;
- device-layout, tablet/mobile mode and orientation calculations still run on every invocation;
- no new cache, observer, timer or retained DOM reference is introduced.

### 2. Payout overlay query/write churn — medium risk

`triggerPayoutFlash()` repeatedly queries stable descendants and writes style/class state across each payout. Any cache must be scoped to the current overlay instance and invalidated when the overlay is removed or rebuilt. This requires dedicated payout-template and cleanup regressions.

### 3. Mission-lock and command-bar scheduling — medium risk

`createMissionLockOnReticle()` owns five scheduled position/cleanup operations and `toggleCommandBar()` owns four scheduled animation operations. Coalescing is deferred until live profiler evidence proves redundant work; the existing staggered timings may intentionally absorb asynchronous Leaflet layout and CSS transition settling.

### 4. Stylesheet and broad-observer architecture — high risk, deferred

The 831 KB stylesheet and all broad observer scopes require equivalent Desktop, Tablet and iOS-compatible profiler scenarios before any modification. Static size or observer count alone is insufficient justification.

## Audit artefacts

The `Deep Performance Audit` workflow installs exact `acorn@8.15.0` and publishes:

- `deep-performance-audit.json` — machine-readable structural inventory;
- `deep-performance-audit.md` — reconciled hotspot and ownership report;
- `deep-performance-source-evidence.md` — exact source blocks for the shortlisted functions.

The workflow fails when:

- an `audit/` pull request changes `src/` or `dist/`;
- analyser or reconciliation fixtures fail;
- measured observer constructions diverge from 12 MutationObservers or four ResizeObservers;
- broad subtree registrations diverge from the trusted total of 10;
- any required evidence artefact is missing.

## Interpretation boundary

Static evidence identifies where to profile. It does not prove that a large function, repeated selector or broad observer is slow in a live MissionChief session.

The following changes remain prohibited without additional evidence:

- combining observers with different lifecycle owners merely to reduce a count;
- retaining DOM references across replaced documents, dialogs, frames or controls without invalidation;
- changing stylesheet order, specificity or initial visibility guarantees without visual contracts;
- parallelising sequential network operations solely to reduce elapsed time;
- removing debounces or refreshes that protect live MissionChief replacement behaviour;
- merging unrelated optimisation candidates into one release.

## Progression

1. Merge the measurement-only audit tooling without creating a release.
2. Implement unchanged root-attribute write suppression in one isolated pull request.
3. Compare deterministic mutation counts and the full canonical test suite.
4. Run equivalent browser-profiler scenarios before medium- or high-risk changes.
5. Keep each optimisation independently reversible.
