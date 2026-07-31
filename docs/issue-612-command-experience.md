# Issue #612 — v9.3 Command Experience

## Scope

Version 9.3.0 adds six user-facing command-experience systems without changing MissionChief dispatch authority:

1. Toolkit Doctor.
2. Recoverable full-screen map mode.
3. Configurable Tablet Quick Wheel.
4. Authenticated encrypted settings transfer, including Discord webhooks.
5. Independent Desktop and Tablet density controls.
6. A deferrable once-per-version Update Briefing.

## Security boundary

The full transfer is a versioned JSON envelope containing AES-256-GCM ciphertext. Its key is derived locally with PBKDF2-SHA-256, 310,000 iterations, a random 16-byte salt and a user passphrase of at least 12 characters. Every export receives a random 12-byte IV. The format and schema are supplied as additional authenticated data, so an altered envelope, wrong passphrase or modified ciphertext fails closed before any settings are previewed or applied.

The decrypted payload includes the full Toolkit state, saved Discord webhook, Financial Archive credential and Financial Archive history. Those values never appear in envelope metadata. The passphrase is neither stored nor recoverable. A separate **Safe Export** remains plain JSON and explicitly omits all private integrations, archive identity and financial history. Legacy unencrypted JSON can still be reviewed and imported for migration, but the previous exposed full-export entry point is retired.

Imported settings are parsed and normalised before an explicit preview. Nothing is applied during file selection or passphrase validation. The final import writes the general state and any included private stores together through their existing persistence paths.

## Toolkit Doctor

Doctor runs only after a user selects it. It checks:

- installed versus verified stable version;
- one current runtime and one owned interface;
- readable primary and recovery settings copies;
- the primary map and launcher mount;
- public MissionChief UK Guide reachability or validated cache fallback;
- responsive device and density attributes plus open-panel bounds;
- competing visible fixed or sticky overlays.

Its copyable report contains status labels only. Webhooks, tokens, player identity, balances, coordinates, mission data and Financial Archive records are excluded. **Repair UI** rewrites the current settings copies, remounts owned controls and reconciles responsive/full-screen geometry before rerunning Doctor.

## Full-screen map

Full-screen mode fixes the live map container to the visual viewport and suppresses surrounding MissionChief page chrome without replacing the map. Toolkit controls, dialogs and operational overlays retain accessible stacking order. The saved state is reapplied after navigation or map remount. A persistent **Exit Full Screen** button and the `Escape` key always restore the standard page; Leaflet size invalidation occurs only when the full-screen ownership state changes.

## Tablet Quick Wheel

The wheel uses Leaflet's existing `contextmenu` event, which provides the native tap-hold path on supported touch devices. It adds no raw touch timer, polling loop, observer or managed listener site. Automatic opening is restricted to active Tablet layout and can be disabled. A manual Settings action remains available for keyboard and assistive operation.

Six slots are independently configurable from retained Toolkit map and command actions. The wheel centre is clamped to the visual viewport, including offsets, and map dragging is suspended only while the wheel is present. Closing, selecting an action, changing layout or destroying the runtime restores dragging and focus.

## Density and update briefing

Desktop and Tablet store independent `spacious`, `standard`, `compact` or `command` density values. iOS Mobile retains its fixed bottom-sheet presentation. Density is exposed as a root attribute so all eight interface themes use the same geometry contract.

Existing users see the v9.3 Update Briefing once per version. Fresh installs start acknowledged. Automatic presentation defers during early boot, a Transport Sweep, hidden-page state, Help or another modal dialog. Dismissal records the installed version; opt-out disables future automatic briefings, while Settings always provides a manual reopen action.

## Performance and lifecycle

The release adds no polling, managed scheduler, observer, raw event-listener, direct `getElementById`, HTML-assignment or network-request site. Doctor reuses the existing user-triggered version and UK Guide request functions. Quick Wheel interaction is attached to the existing Leaflet binding lifecycle. All modal, wheel, full-screen and root-attribute ownership is removed during deterministic teardown.

## Executable evidence

- `.github/scripts/test_issue612_command_experience_contract.py` locks version, settings migration, encryption, privacy, UI actions, lifecycle ownership and zero-scheduler contracts.
- `.github/scripts/test_issue612_command_experience_runtime.mjs` verifies encrypted Discord-webhook round trips, secret absence from the envelope, random salt/IV, wrong-passphrase and tamper rejection, Tablet wheel geometry and drag restoration, density resolution, full-screen recovery and Update Briefing deferral.
- The retained preflight, static audit, performance budget, source-headroom, ESLint and release-parity gates remain mandatory.
