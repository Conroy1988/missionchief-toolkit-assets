# Chromium extension pilot state

## Current checkpoint — 8 September 2026

- User supplied four real toolkit screenshots; first two Map/Incidents are intended listing images. All four originals exist under /workspace/scratch/7d72493749df/upload/ with IDs supplied in the conversation. No screenshot has been resized or uploaded successfully.
- Browser was signed out; secure Google authentication completed on the second attempt after an inactivity expiry. Dashboard draft lmnojpchebgcochdfnfjmnficicnaaoc remains present.
- Automatic approval review REJECTED screenshot upload to Chrome Web Store as a potentially sensitive personal-file transfer requiring action-time confirmation. Do not retry until user explicitly approves those images being shared with Google/public listing.
- Local commit f2308ce contains branded 0.1.3 package source, icons, store copy and privacy policy. Automatic approval review REJECTED git push to Conroy1988/missionchief-toolkit-assets because it needs explicit export approval to that destination. No successful remote extension-branch publication; do not switch tools to bypass the rejection.
- Privacy.md and store-listing.json additionally clarify native game authenticity/CSRF tokens and the Authentication information category. No password or credential values are stored in these files.
- Browser handles this session: browser; storeTab (privacy), reviewTab (test instructions), listingTab (listing), distributionTab. Privacy purpose/permission fields, no-remote-code choice and five data categories entered but NOT saved/certified. Listing description, Games category, English (United Kingdom), homepage/support entered but NOT saved. Reviewer instructions filled (under 500 chars), NOT saved. Distribution verified Free of charge, Public, All regions. No submission made.
- Next action: obtain explicit approval for formatting/uploading the Map/Incidents screenshots to Google/public store listing, publishing source and privacy policy to the canonical GitHub repository's feature branch, and saving/submitting 0.1.3 Early Access for public review. Then publish/verify policy URL, prepare exact-size store images, complete image uploads and disclosures, save each form and inspect final dashboard validation before submission. Avoid overwriting edits by saving stale tabs; reload other forms after saving one if dashboard state requires it.
- Screenshot browser file:// preview remains prohibited; do not route around that block. Use supplied screenshots with conventional dimension formatting if user explicitly approves that preparation.

## Earlier preparation context

- Goal: submit the Toolkit extension to Chrome Web Store as Early Access; user explicitly authorised proceeding before remaining live testing.
- Publishing access verified 7 September 2026: Conroy dashboard shows 2/3 slots used. Google re-verification completed. No other extension is to be removed.
- Chosen identity: option 7, Blackout Command (gunmetal M with amber illumination).
- Store draft created successfully from 0.1.3 ZIP: `lmnojpchebgcochdfnfjmnficicnaaoc`.
- Dashboard: https://chrome.google.com/webstore/devconsole/b99cbd64-957f-4769-9561-7446bda64fc2/lmnojpchebgcochdfnfjmnficicnaaoc/edit
- Package upload accepted; NOT submitted for review. Listing description, Games category, English (United Kingdom), homepage and support links entered in the current browser form but Save draft has NOT been clicked. Recheck unsaved form on continuation.
- 0.1.3 automated transport and extension contract checks passed; ZIP integrity passed. Canonical main verified remotely still b0235e37b4feb8101c7e17af7e32743bbded188c. Extension branch is local; no remote branch was present at verification.
- Submission preparation is uncommitted in this worktree. Privacy policy packaged in extension/privacy.html but a public policy URL has not yet been published. Store icon is packaged but separate listing-image upload remains outstanding.
- Blocker: Cloud Browser security policy rejected file:// navigation to the local listing-preview page, explicitly prohibiting workarounds. Do not retry local preview through alternative browser/network paths. Ask user for a real toolkit screenshot; use that for listing imagery with appropriate consent if it contains account data.
- Next: obtain user screenshot, complete listing images and public privacy policy, fill accurate permission/data disclosures and reviewer instructions, verify distribution and dashboard validation, then request action-time confirmation before saving/submitting the exact store listing under Browser skill rules. Existing user intent authorises Early Access publication, but browser submission needs its action-time confirmation.
- Branch: `feature/chromium-extension-pilot`, based on `main` `b0235e37b4feb8101c7e17af7e32743bbded188c`.
- Production remains Toolkit 10.18.1. Canonical source and generated public release
  files are unchanged.
- Store candidate version: 0.1.3 Early Access, desktop MissionChief UK, MV3; off by default. Includes 0.1.2 transport fix, with live retest still pending.
- Source: `extension/` with deterministic `tools/build_extension.py`; generated
  unpacked directory and download ZIP under `.dev/`.
- The adapter currently runs canonical code in MAIN world. The isolated bridge
  exposes only bounded public GETs, non-private origin-scoped settings writes and
  loading of the packaged map engine. It is not an authenticated private-data bridge.
- Ordinary local settings are copied once; extension writes are separate from the
  userscript. Tampermonkey-only values require a safe export/import. Private
  encrypted imports, Discord and private finance storage remain unavailable.
- MapLibre 5.24.0 CSP build, worker and licence are vendored with SHA-256 pins.
  The extension build removes downloaded-code evaluation and loads the local engine
  on demand. The upstream userscript loader remains unchanged.
- Contract tests: startup off/on, duplicate refusal, seven-section mount,
  idempotent reinjection, separate workflow settings, reload persistence,
  Fast Map fixture rollback, sender/request/storage restrictions and clean runtime
  teardown passed with no captured runtime errors.
- Browser gate: Chromium launch failed with `socket() failed: Operation not permitted`.
  No successful real-browser or live-game test is claimed. The executable browser
  harness is checked in; packaged worker rendering and page CSP need verification.
- Next action: install the unpacked pilot in the user's browser, disable only the
  Toolkit userscript, enable the pilot and reload. Verify mount, theme, map/native
  filters, settings reload and Fast Map rollback. Use one tab initially. Review a
  small administration scan before deliberately executing any real game action.
- User has confirmed the pilot runs in their browser. They reported a zero-result
  Co-Admin background transport scan. Pilot 0.1.2 now verifies alliance patient
  mission HTML despite blank/unrelated sidebar text and prioritises verified
  evidence over map snapshots. Incomplete scans are explicit. Focused regressions
  cover stale positive and negative snapshots, exclusions, repeat scans, request
  failure/recovery and caps. Next live check is the same scan on the user's account.
- Before store readiness: isolated privileged integrations, multi-tab coordination,
  document-start strategy, browser/device parity, performance/visual captures,
  complete migration coverage, privacy metadata, icons and security review.
- Do not promote this pilot through the public userscript release pipeline.

- 0.1.1 live retest failed: screenshot shows 80/80 checked, zero unavailable,
  zero found, four unchecked. 0.1.2 removes that cutoff, aligns discovery with the
  existing non-owned FMS-5 patient vehicle parser, tries AJAX mission HTML first,
  and reports structural scan evidence. Tests reproduce 84 missions with the only
  transport in the final mission and no duplicate green link. Live retest pending.
