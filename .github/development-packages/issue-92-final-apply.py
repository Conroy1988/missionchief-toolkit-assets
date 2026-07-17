#!/usr/bin/env python3
from pathlib import Path
import runpy

root = Path(__file__).resolve().parents[2]
target = root / ".github/development-packages/issue-92-navigation-implementation.py"
text = target.read_text(encoding="utf-8")
old_duplicates = '''# Remove duplicated controls. Tools remains the canonical home for shortcuts 6–9 and transport/unit overlays.
for old, label in [
    ("                    ${makeToggleButton('transportWatcher', '7', 'Transport Watch', 'Show amber transport-required badges beside missions. Shortcut: 7')}\\n", "Resources Transport Watch duplicate"),
    ("                    ${makeToggleButton('transportWatcher', '7', 'Transport Watch', 'Show amber transport-required badges beside missions. Shortcut: 7')}\\n", "Ops Transport Watch duplicate"),
    ("                    ${makeToggleButton('unitCommitment', '8', 'Unit Count', 'Show your own committed unit counts beside missions. Shortcut: 8')}\\n", "Ops Unit Count duplicate"),
    ("                    ${makeToggleButton('criticalView', '9', 'Critical View', 'Show only personal missions aged 8 hours or more. Shortcut: 9')}\\n", "Ops Critical View duplicate"),
    ("                    ${makeToggleButton('missionAge', '6', 'Mission Age', 'Show personal mission age with 8H amber, 16H orange and 24H red warning stages. Shortcut: 6')}\\n", "Ops Mission Age duplicate"),
]:
    source = replace_once(source, old, "", label)
'''
new_duplicates = '''# Remove duplicated controls. Tools remains the canonical home for shortcuts 6–9 and transport/unit overlays.
transport_duplicate = "                    ${makeToggleButton('transportWatcher', '7', 'Transport Watch', 'Show amber transport-required badges beside missions. Shortcut: 7')}\\n"
transport_count = source.count(transport_duplicate)
if transport_count != 2:
    raise RuntimeError(f"Transport Watch duplicates: expected two matches, found {transport_count}")
source = source.replace(transport_duplicate, "", 2)
for old, label in [
    ("                    ${makeToggleButton('unitCommitment', '8', 'Unit Count', 'Show your own committed unit counts beside missions. Shortcut: 8')}\\n", "Ops Unit Count duplicate"),
    ("                    ${makeToggleButton('criticalView', '9', 'Critical View', 'Show only personal missions aged 8 hours or more. Shortcut: 9')}\\n", "Ops Critical View duplicate"),
    ("                    ${makeToggleButton('missionAge', '6', 'Mission Age', 'Show personal mission age with 8H amber, 16H orange and 24H red warning stages. Shortcut: 6')}\\n", "Ops Mission Age duplicate"),
]:
    source = replace_once(source, old, "", label)
'''
if text.count(old_duplicates) != 1:
    raise RuntimeError(f"Duplicate-control package block count: {text.count(old_duplicates)}")
text = text.replace(old_duplicates, new_duplicates, 1)
old_incident = "                    ${makeToggleButton('majorIncidentFeed', '▰', 'Incident Feed', 'Theme-aware major incident ticker in the top status bar. Hover pauses; click a mission to zoom.')}"
new_incident = "                    ${makeToggleButton('majorIncidentFeed', '▰', 'Incident Feed', 'Show the theme-aware major incident ticker in the top status bar. Hover pauses; click a mission to zoom.')}"
if text.count(old_incident) != 2:
    raise RuntimeError(f"Incident Feed package occurrences: {text.count(old_incident)}")
text = text.replace(old_incident, new_incident, 1)
old_profile_status = '                <div class="mcms-status">Profiles save your map location, zoom, skin, visibility filters and operational overlays.</div>'
new_profile_status = '                <div class="mcms-status">Profiles store your map location, zoom, skin, visibility filters and operational overlays.</div>'
if text.count(old_profile_status) != 2:
    raise RuntimeError(f"Profile status package occurrences: {text.count(old_profile_status)}")
text = text.replace(old_profile_status, new_profile_status, 1)
target.write_text(text, encoding="utf-8")
runpy.run_path(str(target), run_name="__main__")
for path in [
    target,
    root / ".github/development-packages/issue-92-navigation-rerun.py",
    root / "docs/internal/issue-92-navigation-audit.md",
    root / "docs/internal/issue-92-panel-source-extract.md",
    root / "docs/internal/issue-92-label-css-audit.md",
    root / "docs/internal/issue-92-implementation-error.txt",
    root / "docs/internal/issue-92-rerun-error.txt",
    root / "docs/internal/issue-92-full-diagnostic.txt",
]:
    path.unlink(missing_ok=True)
try:
    (root / "docs/internal").rmdir()
except OSError:
    pass
