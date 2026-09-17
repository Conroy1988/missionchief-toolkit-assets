# MissionChief Map Command Toolkit — Privacy


Extension 2.0.0. Updated 17 September 2026. Independent community software, not an official MissionChief product.


## Purpose and information used


The extension runs on MissionChief UK when you enable it. It reads the game page and same-origin game endpoints to provide map controls, mission information, vehicle and building tools, and administration workflows. This can include game user and alliance identifiers, mission locations, vehicles, buildings, personnel and in-game financial information. Game locations and game currency are not your device GPS location or real-world banking information. Actions you confirm are sent to MissionChief using your existing signed-in game session. The extension does not ask for your MissionChief password.


## Storage and retention


Ordinary toolkit preferences and supported cached game data are saved in this browser's extension-local storage, separated by MissionChief origin. Existing ordinary userscript settings may be copied once without overwriting the original. Settings remain local unless you choose the optional Discord account sync described below. Transient page data and scan logs can remain in memory until the page is closed. Bounded mission-read caches are held briefly in memory; public reference caches may be shared between tabs. Task checkpoints store a game-account scope, owning tab/document, status, timestamps and progress counts locally so interrupted tasks can be identified. The latest 20 previous runs are retained per origin/account in addition to current task checkpoints. Up to 25 named operation presets store only tool preferences per game account; no execution queue is stored in a preset. Setup completion is stored locally. Checkpoints and presets never cause automatic replay of game actions. Diagnostic export includes only allowlisted version, status and performance counters; it excludes account identifiers, URLs, mission data and settings. Stored extension data remains until removed or the extension is uninstalled. Exported settings and reports are files you choose to save and manage yourself. Removing the extension does not delete your original userscript settings or your MissionChief account data.


## Home Response Builder data

Builder plans, progress, selected game locations, building and vehicle references, dispatch-centre assignment and icon catalogue references are saved in MissionChief site-local browser storage, scoped to the verified game account. Icon catalogues also record the selected building type and remain until refreshed or that site's storage is cleared. Saved catalogues contain image references and counts rather than downloaded image bytes. Uninstalling the extension does not necessarily clear MissionChief site storage. Plans never resume purchases without user confirmation.

## Network requests and other providers


MissionChief receives game reads and actions. Public guides and reference data may be downloaded from TKB Gaming and GitHub. GitHub-hosted theme images and audio, and MissionChief image assets hosted on Amazon S3, may be loaded by enabled features. Your selected game graphics or other configured asset URLs may also be requested by the page. Network providers receive ordinary connection information such as IP address and request metadata and may receive the page origin or referrer according to browser policy. Public reference requests omit credentials. Authenticated game requests use your MissionChief session; optional Supabase account requests use the Toolkit authentication session. The native MissionChief page continues to make its own requests independently.


City search and map-area selection send the entered place query or clicked map coordinates to OpenStreetMap's Nominatim service to obtain public geographic boundaries. These are user-selected game-planning locations, not device GPS readings. The preview map requests OpenStreetMap tiles for the viewed area. These providers receive normal network metadata. Search results are cached temporarily and requests are rate-limited. Coastline and major-lake geometry is bundled with the extension for local water checks; map attribution and geographic-data licences are included.

## Limits and sharing


The extension does not include advertising or developer analytics, sell user data, or upload game activity records for analytics. Optional account backup uploads the specific preferences and account identifiers described below. It does not read browsing history from unrelated websites. Discord reporting is optional. Your chosen webhook URL is kept in extension-private storage and, when signed in, stored separately in your Supabase account for cross-device reporting. It is excluded from game-page settings, ordinary preference exports and diagnostics. A prepared report (including an optional PNG chart) is stored locally and expires after 30 minutes. Clicking Post to Discord sends the selected report to the saved destination. Connection checks contact Discord without posting a message. Remove webhook in Account clears the destination locally and, when signed in and synchronisation succeeds, in the cloud account. Private finance persistence and encrypted private imports remain unavailable. Downloaded resources are data, media and map assets, not remotely executed extension code. Support information is shared only when you deliberately send it; review and redact reports before posting publicly.


## Optional Discord account and preference sync

Account sign-in uses Discord OAuth through Supabase. Discord supplies account identity including an identifier, display name and email. Supabase processes authentication and stores your Discord-linked user identifier, MissionChief account identifier and allowlisted Toolkit preferences, including appearance, controls, filters, bookmarks, map profiles and tool preferences. The Toolkit project is hosted in London. Providers also receive ordinary connection metadata.

Access and refresh tokens are stored in extension-origin IndexedDB, inaccessible to MissionChief page scripts. Database ownership policies restrict each backup to its authenticated owner. The extension does not upload MissionChief cookies, active operation queues, payment confirmations or financial archives as part of preference sync. The optional Discord webhook secret and its label are stored separately under the authenticated account with owner-restricted access, and are restored across devices. The secret is not returned to MissionChief page scripts or included in ordinary settings exports.

After opting in, edits save locally and then synchronise. An existing cloud backup is restored on sign-in; local recovery copies are retained before restores. Offline edits are retained and conflicting edits require your choice. Sign-out stops sync and retains device settings. Cloud backups remain until deletion is requested; uninstalling or signing out does not delete them. Request cloud account and backup deletion through the project issue tracker, without posting secrets; identity may need to be verified privately before deletion.

## Enhanced game pages and local preferences

Awards, Tasks and Events, player profiles, alliance chat, member lists and inbox views read content already shown by MissionChief to provide local search, filtering, summaries and layout controls. This may include player names, game account identifiers, public profile statistics and loaded game communications. Chat and inbox searches do not upload message text to the developer or search unrelated websites. Awards pins, panel visibility and release-note acknowledgements are saved locally. Panel preferences are scoped to the game profile where it can be identified. The dispatch dashboard reads game buildings, vehicles and reported staffing on request. These game snapshots are not uploaded as part of settings sync.

## Building and staff operations

Building upgrades, expansions, instant completions, vehicle purchasing, vehicle replacement and staff training can retain selected game staff/building IDs, names, course choices, currency quotes and verification checkpoints in account-scoped browser storage. Scanning does not purchase anything. Explicitly requested actions are sent to MissionChief, and uncertain paid requests are verified before any retry.

## Your choices


The toolkit is off by default. Enable it from the extension popup, disable individual features in the toolkit, or disable the extension and reload the game. Administrative actions affect the real game; review their existing confirmation screens. Uninstalling removes the extension's local settings. For questions or deletion requests concerning information you have voluntarily shared for support, contact the maintainer through the project issue tracker; do not post passwords or other secrets.


## Limited use


Information handled by the extension is used only to provide its stated MissionChief toolkit features and user-requested support. It is not used for advertising, credit decisions or unrelated profiling. This policy applies to the extension, not to independent services' own data handling.
