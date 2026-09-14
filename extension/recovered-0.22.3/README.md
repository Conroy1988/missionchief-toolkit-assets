# MissionChief Map Command Toolkit — Early Access 0.2.0

This is a local test build based on Toolkit 10.18.1. It has not been submitted to the store. The independent community extension supports desktop MissionChief UK.

## Update your existing unpacked installation

Wait until the popup says Settings: Saved. Close MissionChief tabs. Extract this ZIP into the same permanent extension folder, replacing its files. At chrome://extensions (or your browser equivalent), click Reload for the existing Toolkit entry. Reopen MissionChief and confirm v0.2.0. Do not create a second installation: the existing extension identity retains your settings and triggers their migration.

For a first installation, extract to a permanent folder, enable Developer mode on the extensions page, select Load unpacked and select the folder containing manifest.json. Disable the Toolkit userscript in Tampermonkey, enable the extension in its popup and apply/reload. Other unrelated scripts can remain enabled.

## What changed

Packaged feature functions load on demand; the main stylesheet is separate. Settings writes are combined, stored by section and synchronised across tabs. Independent edits merge; conflicting edits show an error instead of overwriting another tab. The popup shows saving status, current tasks and local diagnostic export. Scans have request sharing, a short bounded read cache and cancellation. Administration tasks have per-account ownership and persistent interruption records. They never restart automatically after an interruption. Browser-managed version information replaces userscript update polling.

## Test these paths

1. Load the map, open the seven sections, change a theme and reload.
2. Open two game tabs. Change different settings in each and verify both changes remain after reload. Check Settings: Saved before closing a tab.
3. Run a small transport scan, stop it midway, and scan again. Review evidence before confirming any real game action.
4. Try starting the same administration task in another tab; it should explain that one is already running.
5. Check native map pan/zoom, fullscreen and drawing.
6. Open extension Settings, Toolkit Doctor and Export diagnostics. The exported diagnostics exclude account identifiers, mission data, settings and URLs.

## Limits and updates

Discord reports now use a dedicated extension screen for destination setup, preview and explicit sending. Private finance persistence and encrypted private imports remain unavailable. The extension does not overwrite original userscript settings. Store and unpacked installations have separate identities; safe export/import is needed to transfer between them. Store installations update through the browser; unpacked installations require manual replacement.

Automated DOM tests simulate browser APIs. Version 0.2.0 needs live-browser testing, including the stylesheet under the game CSP, packaged WebGL worker and real-account workflows. Review existing game confirmations. See privacy.html and release-notes.html.
