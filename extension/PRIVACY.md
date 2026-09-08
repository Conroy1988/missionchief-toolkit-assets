# MissionChief Map Command Toolkit — Privacy


Early Access extension 0.1.3. Updated 7 September 2026. Independent community software, not an official MissionChief product.


## Purpose and information used


The extension runs on MissionChief UK when you enable it. It reads the game page and same-origin game endpoints to provide map controls, mission information, vehicle and building tools, and administration workflows. This can include game user and alliance identifiers, mission locations, vehicles, buildings, personnel and in-game financial information. Game locations and game currency are not your device GPS location or real-world banking information. Actions you confirm are sent to MissionChief using your existing signed-in game session. The extension does not ask for your MissionChief password. For native game form submissions, it uses page-provided authenticity/CSRF tokens for their intended same-origin requests; these tokens are not sent to developers or third-party asset providers.


## Storage and retention


Ordinary toolkit preferences and supported cached game data are saved in this browser's extension-local storage, separated by MissionChief origin. Existing ordinary userscript settings may be copied once without overwriting the original. Settings are not synced by this extension across browsers or devices. Transient page data and scan logs can remain in memory until the page is closed. Stored extension data remains until removed or the extension is uninstalled. Exported settings and reports are files you choose to save and manage yourself. Removing the extension does not delete your original userscript settings or your MissionChief account data.


## Network requests and other providers


MissionChief receives game reads and actions. Public guides and reference data may be downloaded from TKB Gaming and GitHub. GitHub-hosted theme images and audio, and MissionChief image assets hosted on Amazon S3, may be loaded by enabled features. Optional Fast Map requests map styles, tiles and fonts from OpenFreeMap and providers referenced by the selected map style; these requests can reveal the viewed map area. Your selected game graphics or other configured asset URLs may also be requested by the page. Network providers receive ordinary connection information such as IP address and request metadata and may receive the page origin or referrer according to browser policy. Privileged cross-origin data requests made by the extension omit credentials. The native MissionChief page continues to make its own requests independently.


## Limits and sharing


The extension does not include advertising or developer analytics, sell user data, or send game records to a developer collection server. It does not read browsing history from unrelated websites. Discord posting, private credential storage, private finance persistence and encrypted private imports are unavailable in this Early Access build. Downloaded resources are data, media and map assets, not remotely executed extension code. Support information is shared only when you deliberately send it; review and redact reports before posting publicly.


## Your choices


The toolkit is off by default. Enable it from the extension popup, disable individual features in the toolkit, or disable the extension and reload the game. Administrative actions affect the real game; review their existing confirmation screens. Uninstalling removes the extension's local settings. For questions or deletion requests concerning information you have voluntarily shared for support, contact the maintainer through [the project issue tracker](https://github.com/Conroy1988/missionchief-toolkit-assets/issues); do not post passwords or other secrets.


## Limited use


Information handled by the extension is used only to provide its stated MissionChief toolkit features and user-requested support. It is not used for advertising, credit decisions or unrelated profiling. This policy applies to the extension, not to independent services' own data handling.


