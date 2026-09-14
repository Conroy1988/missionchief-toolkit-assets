# Final userscript migration update

The final notice is published by [Publish final userscript migration notice](https://github.com/Conroy1988/missionchief-toolkit-assets/actions/workflows/publish-legacy-migration.yml). Its delivery evidence records whether TKB's live update endpoints serve the exact published files; installed-browser acceptance is recorded separately.

## Build

```sh
python3 legacy/build-migration.py
```

Outputs appear in `.dev/legacy-migration/`. Version **10.18.2** is newer than the repository's final historical source, 10.18.1. The generator keeps the existing script name, namespace, match patterns, grants and update/download URLs. It adds a one-time-per-load notice with a seven-day snooze and the Chrome Store/migration links. The legacy runtime remains available for settings export but is unsupported. No game request, forced navigation, setting deletion or automatic extension installation is added.

## Delivery requirements

Existing installations record these endpoints:

- Metadata: `https://tkb-gaming.scot/mission-chief-scripts/map-command-toolkit/metadata/`
- Download: `https://tkb-gaming.scot/mission-chief-scripts/map-command-toolkit/update/`
- Historical installer: `https://tkb-gaming.scot/mission-chief-scripts/map-command-toolkit/install/MissionChief_Map_Command_Toolkit.user.js`

TKB's existing PHP gateways serve assets from the latest GitHub release. The main-only publication job checks the live version, prepares all assets in a draft release, verifies their hashes, then publishes the complete release. It verifies the metadata, update and installer response hashes and saves `delivery-verification.json` in its run artifacts. It refuses to supersede an unexpected version or overwrite conflicting assets. No website deployment is required.

Test an actual existing Tampermonkey installation: check for updates, accept if prompted, reload the game, confirm the notice/links and verify settings export still works. Verify snoozing, narrow screens and disabling only the old Toolkit script. Users who disabled automatic updates must check manually.

The website product/installation page should lead new users to the Chrome Store. Old metadata/download endpoints must remain available for migration. If other published script hosts or alternate update URLs were used, they need their own migration update too; changing these paths does not reach every historical installation automatically.

**Do not describe this notice as delivered until the live endpoint and installed-script checks succeed.** Do not run the historical general release workflow merely to publish the Chrome extension.
