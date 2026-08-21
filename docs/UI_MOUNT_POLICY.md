# Toolkit UI Mount Policy

Page-level Toolkit UI is not considered implemented merely because selectors, labels or helper functions exist.

Every new or materially changed external-page UI surface must:

1. execute its real production installer against a rendered DOM fixture;
2. cover content present at startup and content inserted later without relying on the top-level route;
3. cover host-framework rerender or replacement;
4. prove deterministic teardown when disabled;
5. publish a structured mount receipt and expose a visible waiting or error state instead of failing silently;
6. avoid mocked installer and lifecycle substitutes in the blocking integration test.

The single-runner Toolkit Hotfix Gate installs a pinned, script-disabled DOM runtime and runs `.github/scripts/test_ui_mount_integration.mjs` whenever Runtime validation is selected. The gate cannot pass if the production installer fails any registered scenario.
