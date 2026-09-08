# Toolkit Chromium extension — local pilot 0.1.2

This is an unpacked testing build of Toolkit 10.18.1 for desktop Chromium browsers
on MissionChief UK. It has not been submitted to any store. It is off by default.

**Validation:** Node/DOM tests passed for startup, duplicate prevention, separate
settings persistence, native workflow settings, the Fast Map fixture and bridge
request restrictions. A real Chromium launch was blocked by the development
environment's socket restriction. Real-browser installation, page CSP behaviour,
packaged WebGL worker loading and live-account operation are still unverified.
This package is for initial controlled testing, not general release.

## 0.1.2 transport scan repair

Checks the entire finite list of current alliance patient missions with at most four
requests in flight. The previous 80-mission cutoff is removed. Discovery now accepts
the same non-owned status-5 patient vehicle rows as the release path, without requiring
a second green transport link. AJAX mission HTML is requested first; the normal page
is tried when it lacks status-5 vehicle entries. Incomplete shells remain unresolved.
The scan log reports vehicle links, status-5 entries and eligible patient vehicles.
Release actions and their confirmations remain unchanged. Live-account retest pending.

To update from 0.1.0 or 0.1.1, close your MissionChief tabs, replace the contents of the
existing extracted extension folder with this package, click **Reload** for the
extension at `chrome://extensions` (or Brave/Edge equivalent), then reopen MissionChief.
Keep using the same folder and extension entry to retain pilot settings. Do not
install a second copy. Check that the extension version is **0.1.2**.

## Install and test

1. Extract the ZIP to a permanent folder on your PC. Keep the folder after installation.
2. Open `chrome://extensions`, `brave://extensions`, or `edge://extensions`.
3. Enable **Developer mode**, select **Load unpacked**, and choose the extracted folder containing `manifest.json`.
4. Disable only the **MissionChief Map Command Toolkit** script in Tampermonkey.
5. Open MissionChief UK. Open the extension button, tick **Enable extension pilot**,
   then select **Apply and reload game tab**. Pin the extension for convenient access.
6. If the popup says **Userscript detected**, confirm that script is disabled and reload.

The pilot copies the ordinary Toolkit settings from this site's local storage on
first activation. Its changes are saved in a separate, origin-scoped extension
store. Original userscript settings are not overwritten. Data held exclusively in
Tampermonkey cannot be read automatically: use its safe settings export/import.
Private encrypted imports are intentionally blocked in this pilot.

For the initial test use one MissionChief tab. Try normal map movement, station
filters, all seven sections, your usual theme, settings persistence after reload,
Fast Map on/off, and one small reviewed administration action. Administrative
actions still operate on the real game and retain their existing confirmations.
Start by checking scans and review screens before submitting a change.

## Returning to the userscript

Switch the pilot off in its popup, re-enable the Toolkit userscript, and reload
MissionChief. The userscript uses its original settings. Uninstalling the extension
deletes its separate test settings. Export safe settings first if you want to retain them.

## Pilot boundaries

- UK desktop only for now; Chrome, Brave and Edge still need real-user verification.
- Discord credentials/posting and private finance storage are unavailable. Ordinary
  map and native same-origin game workflows use the existing Toolkit implementation.
- External requests are read-only, credential-free, size/time bounded and limited
  to specific public guide/rule/update endpoints and native marker images.
- MapLibre 5.24.0 and its worker are packaged locally and loaded only for Fast Map.
  Map tiles and images still require network access. No downloaded executable code.
- Background workers may restart; settings are persisted per write. Interrupted
  external reads fail visibly; game mutations are not retried by the extension.
- The popup reports settings persistence errors. Wait for writes before closing
  the browser. Multi-tab synchronisation is a later acceptance gate.
- The PILOT badge is not the userscript update button. Install future test builds
  manually, then use Reload on the browser's extension management page.
- This is a compatibility adapter, not the completed modular architecture. The
  packaged runtime still runs in MissionChief's page world to use its native objects.
  The bridge is treated as untrusted; it cannot access a private credential vault.
- The pilot starts at document idle so an installed userscript has first refusal.
  Early document-start performance protection needs a dedicated extension design.
- Enable/disable on the next page load. Do not inject another Toolkit dynamically
  into a page where the pilot is already running.

## Build from the repository

Run `python3 tools/build_extension.py`. The generated extension and ZIP are under
`.dev/`. Vendor files are pinned by SHA-256 in `extension/vendor-lock.json`.
The builder fails if expected source adaptations drift. Canonical userscript and
release files are never changed by the build.

Contract tests: `npm install --prefix .dev/test-deps --no-audit --no-fund jsdom@26.1.0`,
then `node extension/test-contracts.mjs`. Browser test harness:
`node extension/test-pilot.mjs` (requires Playwright, an extension-capable Chromium,
and permission to launch browser processes; set `CHROMIUM_PATH` as needed).

Before a store submission: complete privileged integration design, multi-tab and
interruption tests, document-start protection, live browser/device parity,
accessibility/performance captures, settings migration sign-off, store metadata,
icons, privacy disclosures and independent security review of the page bridge.
