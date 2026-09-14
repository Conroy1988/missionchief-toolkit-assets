# Toolkit 1.0 release candidate 2

Candidate: extension **0.9.2**, display name **1.0 Release Candidate 2**, Toolkit **10.18.1**. Baseline c328d0c (0.4.1). This is a test candidate, not the final 1.0 or a new Chrome Store submission.

## Approved scope and implementation

| # | Priority | Candidate work | Remaining acceptance |
|---|---|---|---|
| 1 | First-run setup | Once-only popup setup, duplicate-runtime detection retained, enable/reload and backup-import guidance, help always available | Fresh install on each target browser |
| 2 | Performance | Only the visible Operations tool evaluates detailed snapshots; hidden-page popup polling pauses; task polling pauses on Settings; overlapping popup refreshes coalesce; existing scheduler/cache/lazy-module safeguards retained | Busy live account, long session, memory and FPS measurements |
| 3 | Compact UI | User-approved 0.4.1 layout retained; presets/help use disclosures; task rows compacted; selected targets shown within the tool | Final theme and small-screen inspection |
| 4 | Browser acceptance | Existing startup/token/opaque callback tests retained; explicit platform matrix below | Chrome, Brave and Orion device sessions |
| 5 | Action previews | Selected names, upgrade labels and real scanned Credit prices displayed before run; original live preflight/final confirmations retained | Game-state change between scan and confirmation |
| 6 | Task centre | Human-readable names/states, owning tab, counts, progress and focus link; partial/failure outcome derived from native counters; individual Stop recorded as stopped | Two-tab real account exercise |
| 7 | Recovery | Popup distinguishes disabled/duplicate/disconnected; saving is Unknown without evidence; help covers interrupted actions and conflicts; reload blocked while this tab has active work | Background suspension and network loss on device |
| 8 | Settings | Search now uses real row labels and feature/setting aliases; reload guidance, selective transfer, migration/conflict protection retained | Older backup import and visible feature refresh |
| 9 | Health | Background, game connection, enable choice and saving status shown separately; running does not claim full compatibility | Permission-off/device-specific failure checks |
| 10 | Context help | Per-tool explanations, exact targets, safeguards disclosures, searchable settings descriptions; packaged setup/update/recovery guide | New-user walkthrough |
| 11 | Accessibility | Reduced-motion handling for toolkit shell; focus outlines; touch settings targets; labelled preset controls; popup readable text and links | Keyboard, screen reader, contrast/theme and iOS touch review |
| 12 | Updates | Extension/Toolkit versions explicit; RC identity; distinct store, unpacked Chrome/Brave and Orion ZIP instructions; last-working-package recovery | Upgrade existing installation and preserve settings |
| 13 | Distribution/support | Updated listing/reviewer draft, privacy, support template, installation guide and screenshot source generator | Capture and review current real-browser PNGs; submit after acceptance |
| 14 | Saved presets | All five tools, up to 25/account, allowlisted preferences, explicit preview/apply, durable writes, export/import and deletion confirmation; no targets or execution persisted | Real-account preset round trip |
| 15 | Controlled release | Versioned candidate, exact-package hashes/test receipts, unchanged permissions, feature freeze and promotion checklist | All blocking manual checks before final 1.0 |

## Evidence

Dan confirmed the Orion startup fix in 0.2.6 and approved the 0.4.1 compact menu after testing. These are user observations, not independent certification of every feature/browser combination. No current-device version numbers have been supplied.

`tools/verify_extension.mjs` builds and checks the complete packaged runtime, migration, settings conflicts, task ownership/history, preset validation, native scan/run control preservation, startup fallback, network boundaries and transport discovery. It embeds matching contract and transport receipts. All browser APIs in these tests are simulated.

`tools/benchmark-extension-ui.mjs` compares 0.4.1 against this candidate in Node/JSDOM using five tools with 2,000 fixture records per tool and 50 refreshes with one visible tool. Detailed snapshots decrease from 250 to 50 (80%). Timings are diagnostic only, machine-dependent and not evidence of live map FPS or real network speed. Package core grows modestly for setup/presets; CSS extraction and 81 deferred functions remain intact.

The remote browser refused the local UI preview with ERR_BLOCKED_BY_CLIENT earlier in this work. Current screenshot PNGs, visual contrast, actual touch behavior and browser-worker suspension cannot be certified from DOM simulations. Screenshot HTML uses labelled demonstration data and is not a live-account capture.

## Browser acceptance matrix

| Check | Chrome desktop | Brave desktop | Orion iOS |
|---|---|---|---|
| Fresh install, setup, enable/reload | Pending | Pending | Pending |
| Existing-install upgrade preserves settings/presets | Pending | Pending | Pending |
| Duplicate userscript detection | Pending | Pending | Pending |
| Compact navigation, all themes, resize/scroll | Pending (0.4.1 layout approved by Dan) | Pending | Pending |
| Preset save/reload/export/import/apply | Pending | Pending | Pending |
| Each tool: scan, selection, confirm/cancel, stop, results | Pending | Pending | Pending |
| Two tabs: ownership, focus, interrupted task | Pending | Pending | Pending |
| Browser background/foreground, tab close, worker suspension | Pending | Pending | Pending |
| Offline/reconnect and settings conflicts | Pending | Pending | Pending |
| Large account, busy map, sustained memory/FPS | Pending | Pending | Pending |
| Keyboard/screen reader or iOS touch | Pending | Pending | Pending |

## Promotion checklist

1. Freeze new features. Fix candidate defects only; give any changed package a new version.
2. Run the verifier and the synthetic UI benchmark on the final source. Verify ZIP CRC and each embedded tested-file hash.
3. Record browser versions and results for every blocking matrix row. Preserve exact settings and preset backup versions used.
4. Resolve failures; do not relabel pending tests as passed based on a general positive report.
5. Capture current UI screenshots from the final candidate with demonstration data; review privacy and listing text.
6. Produce final 1.0.0 with its own matching test receipts. Keep the last working package available. Export settings/presets before any reinstall.
7. Submit the existing Chrome Store item, rather than creating a duplicate. Store review and rollout are separate from ZIP availability. Do not assume approval or promise immediate updates.

## Scope boundaries

Production userscript source/distribution remains byte-identical. No new extension permission, remote executable code, analytics, developer upload endpoint or automatic game action is added. Native game eligibility, ownership, budgets and final confirmations remain authoritative. Existing unavailable Discord/private-storage features remain unavailable and are disclosed.

## Discord candidate acceptance (0.9.2)

Automated checks cover trusted-page-only credential/send access, destination changes, duplicate sends, uncertain delivery, rate limits, PNG attachments, draft expiry and account-scoped finance timestamps. Still pending: Chrome/Brave and Orion live webhook check and explicitly confirmed delivery for finance/chart, sweep and SITREP; permission acceptance on upgrade. No live messages were sent during development.
