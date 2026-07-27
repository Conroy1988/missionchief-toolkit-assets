# Issue #553 — Alliance Member Manager UI lifecycle failure

Toolkit v8.1.4 publishes the member manager and its Tools toggle, but the redesigned member view can still remain empty.

The full released installer was executed against realistic rendered-page fixtures. A direct route with an already-present table mounts successfully. A neutral top-level route before the redesigned member DOM appears enters the ineligible reconciliation path and throws because it calls `teardownAllianceMemberManager()`, while the production lifecycle function is named `disposeAllianceMemberManager()`.

The earlier runtime contract concealed this defect by providing a fake `teardownAllianceMemberManager()` stub and mocking `installAllianceMemberManager()` instead of executing the released installer.

The v8.1.5 correction must repair lifecycle naming, remove route-only mounting assumptions, use an enabled-only coalesced DOM mount observer, persist the setting through userscript storage, expose mount diagnostics, and require a full rendered-page integration test for direct, delayed and rerendered UI states.
