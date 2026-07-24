# MissionChief Map Command Toolkit

A configurable command-centre enhancement for MissionChief, combining operational mission windows, live requirements intelligence, advanced map controls, fleet identity, guarded transport, financial reconciliation and visual customisation in one userscript.

**Greasy Fork is the official installation and automatic-update channel. GitHub is the canonical development source and documentation home.**

## Main features

- Operational Window Suite with Enhanced Operational Requirements, Extended Call Window, Extended Mission List and opt-in Enhanced Transport Requests
- Mission Age Watch, Mission Value, Critical View and Mission Inspector
- Authoritative selected, en-route, on-scene and still-needed demand with amber waiting/unresolved truth states
- Patient and prisoner transport alerts plus a manual, guarded Patient Transport Sweep for eligible alliance-member ambulances
- Resource Gap, Vehicle Code Status and custom specialist vehicle identity
- Smart bookmarks, Map Jump, coverage rings and Coverage Heat Map
- Financial reconciliation and optional Discord reporting
- Cinematic payout presentations and seven complete interface systems
- Responsive Desktop, Tablet/iPad and iOS Mobile/Safari operating modes
- Performance-aware startup, bounded monitoring and deterministic cleanup

## Operational Window Suite

### Enhanced Operational Requirements

Reconciles MissionChief requirement evidence across vehicles, equipment, personnel, capacity, selected units, en-route units, on-scene units and remaining demand. Green coverage requires positive parsed evidence; unavailable or unsupported evidence remains amber rather than being guessed.

### Extended Call Window

Adds patient and vehicle summaries, selected-unit and ARR counters, search, highlighting, generation and alarm context, mission keywords and map controls without creating a competing mission-window lifecycle.

### Extended Mission List

Adds sorting, starring, collapsing, patient and prisoner indicators, credit and remaining-time badges, and native sharing controls while retaining deterministic state through live refreshes.

### Enhanced Transport Requests

Provides opt-in transport assistance through exact-route validation, visible/enabled candidate filtering, ambiguity rejection and per-route duplicate protection. Automatic transport opening remains disabled by default.

The Toolkit detects compatible native and LSSM requirement sources and suppresses matching Toolkit output when a genuinely visible equivalent LSSM panel is active.

## Installation and updates

1. Install a userscript manager such as Tampermonkey.
2. Select **Install this script** above.
3. Open or refresh MissionChief.
4. Click the Toolkit control.

Only enable one copy of the Toolkit at a time.

Updates are published through a validated GitHub release pipeline and delivered automatically through Greasy Fork.

## Documentation and support

- [Documentation centre](https://conroy1988.github.io/missionchief-toolkit-assets/)
- [GitHub source repository](https://github.com/Conroy1988/missionchief-toolkit-assets)
- [Latest release and changelog](https://github.com/Conroy1988/missionchief-toolkit-assets/releases/latest)
- [Report a bug or performance problem](https://github.com/Conroy1988/missionchief-toolkit-assets/issues/new/choose)

Please include the Toolkit version, browser, userscript manager and reproduction steps when reporting a problem.

## Privacy and permissions

- No advertising, analytics or user tracking
- No hardcoded Discord webhook or private credentials
- Optional Discord webhook details are entered by the user and stored locally
- Discord communication occurs only when the user tests or posts a report
- Exported Toolkit settings can include the saved Discord webhook and should be stored privately
- MissionChief information is processed in the browser to provide enabled Toolkit features

## Compatibility

The Toolkit is primarily developed for MissionChief UK and supports Desktop, Tablet/iPad and iOS Mobile/Safari layouts. Browser or MissionChief interface changes can temporarily affect individual features and should be reported through GitHub.

## Important information

This Toolkit is unofficial and is not affiliated with MissionChief, SHPlay GmbH, LSSM or Discord.

Any user-initiated automation, including transport tools, should be used responsibly and in accordance with alliance rules.

## Licence

Released under the MIT Licence.

Developed and maintained by Conroy1988.
