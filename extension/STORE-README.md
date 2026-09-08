# MissionChief Map Command Toolkit — Early Access 0.1.3

Independent community extension for MissionChief UK desktop. Not affiliated with or endorsed by MissionChief. Based on Toolkit 10.18.1.

## Start

Disable the Map Command Toolkit userscript in Tampermonkey and any unpacked pilot copy before enabling the store extension. Open MissionChief UK, open this extension's popup, tick Enable toolkit, then Apply and reload game tab. The extension is off by default. Other unrelated userscripts can stay enabled.

## Features and limits

The extension adapts the Toolkit's map, incidents, fleet, administration, finance, status and settings interface. Private finance persistence, Discord posting, credential storage and encrypted private imports are unavailable. MapLibre and its worker are packaged locally; map tiles and media need network access. See privacy.html for data handling and network providers.

This is Early Access. Transport-sweep accuracy, real-browser Fast Map rendering, multi-tab behaviour and complete migration parity are still being tested. Use one game tab initially. Scan and review a small selection before confirming administrative actions, which change the real game. The background scan includes the 0.1.2 repair; its live-account retest is pending.

Ordinary userscript settings are copied once and then saved separately in this extension. Store installation has a different extension identity from an unpacked pilot: pilot settings do not automatically migrate. Export safe settings first if needed. The original userscript settings are not overwritten. Disable the extension, re-enable the userscript and reload to return to it.

## Updates and support

Store installations update through the browser. For unpacked testing, replace the existing folder contents and use Reload in the browser's extensions page. The PILOT label inside the game marks the Early Access adapter, not the userscript updater.

Report reproducible problems at https://github.com/Conroy1988/missionchief-toolkit-assets/issues without passwords or private account data. The packaged TEST-RESULTS.json and TRANSPORT-TEST-RESULTS.json distinguish simulated automated checks from live-browser validation.
