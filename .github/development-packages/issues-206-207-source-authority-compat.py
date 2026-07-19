#!/usr/bin/env python3
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
SOURCE = ROOT / "src" / "MissionChief_Map_Command_Toolkit.user.js"
DIST_USER = ROOT / "dist" / "MissionChief_Map_Command_Toolkit.user.js"
DIST_TEXT = ROOT / "dist" / "MissionChief_Map_Command_Toolkit.txt"

source = SOURCE.read_text(encoding="utf-8")
old = "const reconciled = reconcile(parsed); if (!reconciled.requirements.length) { if (reconciled.unresolved.length) { missionRequirementsRestoreSource(record.source); missionRequirementsPresent(record, missionRequirementsPanelHtml([], reconciled.unresolved), 'authoritative or live requirements unresolved'); return; } if (presentCatalogue('no quantified live requirements; official catalogue baseline shown')) return; missionRequirementsRestoreSource(record.source); missionRequirementsPresent(record, missionRequirementsFallbackHtml(record.catalogueState === 'loading' ? 'loading' : 'error'), 'no quantified requirements detected'); return; }"
new = "const reconciled = reconcile(parsed); if (!reconciled.requirements.length) { const authoritativeUnresolved = reconciled.unresolved.some(item => item?.catalogueDerived || item?.authoritativePending || /Requirements for this Mission/iu.test(String(item?.text || ''))); if (authoritativeUnresolved) { missionRequirementsRestoreSource(record.source); missionRequirementsPresent(record, missionRequirementsPanelHtml([], reconciled.unresolved), 'authoritative requirements unresolved'); return; } if (presentCatalogue(reconciled.unresolved.length ? 'live requirement text unparseable; official catalogue baseline shown' : 'no quantified live requirements; official catalogue baseline shown')) return; missionRequirementsRestoreSource(record.source); missionRequirementsPresent(record, missionRequirementsFallbackHtml(record.catalogueState === 'loading' ? 'loading' : 'error'), reconciled.unresolved.length ? 'requirement text unparseable' : 'no quantified requirements detected'); return; }"
count = source.count(old)
if count != 1:
    raise AssertionError(f"authority/live unresolved precedence: expected one match, found {count}")
source = source.replace(old, new, 1)
SOURCE.write_text(source, encoding="utf-8")
DIST_USER.write_text(source, encoding="utf-8")
DIST_TEXT.write_text(source, encoding="utf-8")
print("Preserved the established live-text failure state while failing closed for authoritative errors")
