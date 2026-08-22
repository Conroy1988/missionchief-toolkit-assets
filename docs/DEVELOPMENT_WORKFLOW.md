# Local-first Toolkit development

The normal development loop does not use a pull request, GitHub Actions or the stable TKB distribution. GitHub remains the canonical review and publication boundary only after a candidate has been exercised locally.

## Operating model

```text
edit canonical source
        ↓
change-aware local check
        ↓
Desktop · Tablet · iOS Dev Lab
        ↓
maintainer canary when a live account is required
        ↓
one complete local promotion check
        ↓
one atomic PR · one GitHub runner · automatic verified release
```

The stable userscript, TKB install/update endpoints, release-state ledger, private backup and Discord announcement sequence remain unchanged. A canary is never a public release candidate and cannot update stable users.

## One command surface

Run commands from the repository root:

```bash
./toolkit dev --open
./toolkit check
./toolkit canary-build
./toolkit canary-publish
./toolkit promote
```

`./toolkit help` is the local command index.

The first local check or promotion automatically installs the exact disposable `jsdom` and `acorn` versions used by the one-runner GitHub gate when they are missing. The ignored `node_modules/` tree is never committed and installation scripts, audit calls and lockfile writes are disabled.

## Visual Dev Lab

`./toolkit dev --open` starts an HTTP server bound to `127.0.0.1:4173` and opens:

`http://127.0.0.1:4173/devlab/`

The Dev Lab loads the canonical `src/MissionChief_Map_Command_Toolkit.user.js` directly into a deterministic MissionChief fixture. It does not render a separately maintained imitation of the Toolkit. The controller provides:

- Desktop at 1440 × 900;
- Tablet at 1024 × 768;
- iOS at 390 × 844;
- a three-device matrix;
- every primary Toolkit command page;
- direct focus for Dispatch Recruitment, Expansion & Upgrade Planner, Station Icon Copier and Alliance Courses;
- every supported interface theme;
- automatic source identity polling and preview reload;
- live mount, page-width stability, horizontal-overflow and runtime-error probes.

The fixture cycles every primary page and measures the same panel after each selection. A width change greater than two pixels fails the stability probe. The canonical runtime is also mounted headlessly in all three viewports by `.github/scripts/test_dev_lab_runtime.mjs`.

The local server exposes only repository files, rejects path traversal, adds no-store headers to live development assets and never proxies a MissionChief account or production endpoint.

## Change-aware checks

`./toolkit check` compares the worktree with `origin/main`, syntax-checks every changed Python, JavaScript and shell file, then selects focused tests from `.github/dev-test-matrix.json`.

Examples:

| Changed implementation | Focused proof |
|---|---|
| Dispatch Recruitment | static and runtime Issue #706 contracts |
| Expansion & Upgrade Planner | static and runtime Issue #744 contracts |
| Button 3/native visibility | static and runtime native-visibility bridge contracts |
| Desktop panel sizing | panel, workspace and responsive-menu contracts |
| Dev Lab | full canonical-source Desktop/Tablet/iOS mount |
| Canary tooling | deterministic build and loader network/cache/rejection runtime tests |

Feature selection uses changed paths and changed source anchors. An unknown edit to canonical source fails closed to the complete retained runtime-contract suite. `./toolkit check --feature <name>` adds an explicit lane. `./toolkit check --all` runs the complete retained preflight.

The command writes no canonical or distribution file unless an invoked repository test already owns that output. Optional JSON evidence can be retained under ignored `.dev/` state:

```bash
./toolkit check --json-output .dev/fast-check.json
```

## Maintainer canary

The canary exists for behaviour that genuinely requires a signed-in MissionChief account. It is an opt-in development channel, not a private-code or access-control boundary; the repository remains public.

Install the loader once in a separate development browser profile:

`https://raw.githubusercontent.com/Conroy1988/missionchief-toolkit-assets/main/tools/canary-loader.user.js`

The loader:

1. runs at `document-start`;
2. downloads the fixed `canary` branch manifest from the exact repository path;
3. validates its schema, build identity, origin, byte limit and loader compatibility;
4. downloads the declared bundle with cache bypass;
5. verifies SHA-256 and exact UTF-8 byte length before execution;
6. stores one last-known-good verified bundle;
7. captures local Toolkit settings before first use;
8. replaces the stable runtime only after verification succeeds;
9. retains stable Toolkit when neither network nor cached canary is valid;
10. provides Refresh, Pause Canary and Restore Settings controls on every page.

The canary publisher creates a normal fast-forward commit on `refs/heads/canary`. That branch name matches no workflow trigger, so publication consumes zero GitHub Actions runners. It contains only:

- `canary/manifest.json`;
- `canary/MissionChief_Map_Command_Toolkit.canary.user.js`.

Before mutation, publication runs the pinned dependency bootstrap and the current change-aware local check, then proves that the validated canonical-source SHA-256 is the exact source embedded in the canary manifest. Publication is atomic and verifies the exact remote head after push. It refuses an unexpected remote, never force-pushes, never mutates `main`, never publishes a GitHub Release and never touches the TKB stable endpoints. The audited cleanup workflow treats `canary` as protected operational development state.

## Candidate promotion

`./toolkit promote` is run once after local and canary acceptance. It:

1. requires a non-default feature branch;
2. generates the one authoritative version, size, line-count and SHA-256 fingerprint;
3. runs fingerprint, documentation and JavaScript syntax checks first;
4. checks the lightweight performance budget against the branch merge base;
5. rebuilds and validates canonical distribution variants and byte parity;
6. provisions pinned runtime dependencies only after the cheap checks pass;
7. runs the same runtime, development and workflow-policy stages used by CI;
8. records ignored local evidence at `.dev/promotion-evidence.json`.

The ordered stage catalog lives in `tools/candidate_gate.py`; local promotion and the consolidated workflow call that same catalog instead of maintaining separate command lists. Only then is the exact worktree committed and opened as one pull request. The consolidated PR workflow uses one runner, repeats the independent final gate, retains one immutable release candidate and allows the existing exact-tree release automation to continue.

Development-only paths are explicitly classified. A Dev Lab or canary-tooling PR runs the development contracts but does not become a product release candidate. Canonical userscript changes run both retained product validation and the three-viewport Dev Lab proof.

## Module migration boundary

The public deliverable remains one compatible userscript. New or substantially revised subsystems should receive:

- a distinct implementation boundary and stable feature anchor;
- an entry in `.github/dev-test-matrix.json`;
- focused static and runtime contracts;
- a Dev Lab focus target when the subsystem has a material interface;
- no cross-feature state mutation without an explicit adapter contract.

Existing monolithic regions can be extracted gradually after equivalent behaviour is proven. A broad rewrite is not required to gain the faster development loop and must not bypass saved-data, Desktop, Tablet or iOS compatibility.

## Expected timings

The repository contract targets:

- focused local proof: under 15 seconds;
- visual refresh after a saved source change: under one second after polling;
- canary publication: one normal branch push and zero Actions runs;
- accepted candidate to verified production: one PR gate followed by the existing automatic release.
