#!/usr/bin/env python3
"""Static privacy and outcome contracts for first-party Toolkit analytics."""

from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
SOURCE = (ROOT / "src/MissionChief_Map_Command_Toolkit.user.js").read_text(encoding="utf-8")
README = (ROOT / "README.md").read_text(encoding="utf-8")


def require(token: str) -> None:
    if token not in SOURCE:
        raise AssertionError(f"Toolkit analytics contract missing: {token}")


for token in (
    "// @version      10.7.0",
    "version: '10.7.0'",
    "https://tkb-gaming.scot/api/toolkit-analytics.php",
    "runtimeFetch(TOOLKIT_ANALYTICS_ENDPOINT",
    "globalPrivacyControl",
    "navigator?.doNotTrack",
    "install_confirmed",
    "update_confirmed",
    "telemetry_enrolled",
    "active_daily",
    "active_7d",
    "active_30d",
    "core_ready",
    "feature_toggle",
    "feature_use",
    "runtime_error",
    "previousVersion",
    "toolkitFreshInstallAtLoad",
    "toolkitAnalyticsConfirmLifecycle(coreReadyMs)",
):
    require(token)

analytics_start = SOURCE.index("const TOOLKIT_ANALYTICS_ENDPOINT")
analytics_end = SOURCE.index("function runtimeFetch", analytics_start)
analytics = SOURCE[analytics_start:analytics_end]
for forbidden in (
    "currentUserId",
    "playerName",
    "visitorId",
    "clientId",
    "userAgent",
    "document.referrer",
    "document.cookie",
    "localStorage",
    "GM_xmlhttpRequest",
):
    if forbidden in analytics:
        raise AssertionError(f"Anonymous analytics block contains forbidden identity or browsing field: {forbidden}")

for feature in (
    "patientTransportSweep",
    "pressureBoard",
    "toolkitDoctor",
    "sessionCleanup",
    "unitLocator",
    "commandPalette",
    "financialIntelligence",
    "allianceCourses",
    "safeMode",
):
    require(f"toolkitAnalyticsRecordFeature('{feature}')")

if "Greasy Fork" in SOURCE or "greasyfork.org" in SOURCE.lower():
    raise AssertionError("The installed Toolkit must not advertise the retired Greasy Fork channel")
if "Greasy Fork" in README or "greasyfork.org" in README.lower():
    raise AssertionError("The primary README must not advertise the retired Greasy Fork channel")

print("First-party Toolkit analytics contract passed.")
