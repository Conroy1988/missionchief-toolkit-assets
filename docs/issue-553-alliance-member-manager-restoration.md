# Issue #553 — hardened Alliance Member Manager UI mounting

Toolkit v8.1.5 repairs the undefined lifecycle call proven by the full rendered-page diagnostic and replaces route-only retries with one enabled-only coalesced mount observer. The setting is mirrored through userscript storage, mount states are published under `window.__MCMS_UI_MOUNTS__`, the Toolkit control displays WAIT or ERR when appropriate, and the required Runtime lane executes the real installer against direct, delayed and rerendered member views.
