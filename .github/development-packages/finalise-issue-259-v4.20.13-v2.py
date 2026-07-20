#!/usr/bin/env python3
from pathlib import Path
import runpy

ROOT = Path(__file__).resolve().parents[2]
PACKAGE = ROOT / ".github/development-packages/finalise-issue-259-v4.20.13.py"
OLD_WRAPPER = ROOT / ".github/development-packages/finalise-issue-259-v4.20.13-corrected.py"
DIAGNOSTIC = ROOT / "docs/issue-259-package-diagnostic.md"

text = PACKAGE.read_text(encoding="utf-8")

resource_old = "resourceCandidate.root.queryHandler = selector => selector.includes('[id^=\"mission_water_holder\"]') ? holder : originalResourceQuery(selector);"
resource_new = "resourceCandidate.root.queryHandler = selector => /mission_(?:water|foam|pump)_holder/.test(selector) ? holder : originalResourceQuery(selector);"
if text.count(resource_old) != 1:
    raise RuntimeError("resource fixture correction anchor missing")
text = text.replace(resource_old, resource_new, 1)

training_suffix_old = ', "", "remove whole-row training inference")'
training_replacement = "const badgeTexts = Array.from(String(row?.textContent || row?.innerText || '').matchAll(/\\[([^\\]]+)\\]/gu)).map(match => missionRequirementsCapabilityLabel(match[1])).filter(Boolean); for (const badgeText of badgeTexts) { for (const definition of MISSION_REQUIREMENT_DEFINITIONS) { const aliases = Array.from(definition?.training || []).map(missionRequirementsCapabilityLabel).filter(Boolean); if (!aliases.includes(badgeText)) continue; training.add(badgeText); knownDefinitionKeys.add(definition.key); } } "
training_suffix_new = ', ' + repr(training_replacement) + ', "replace whole-row training inference with explicit badge parsing")'
if text.count(training_suffix_old) != 1:
    raise RuntimeError("training hardening correction anchor missing")
text = text.replace(training_suffix_old, training_suffix_new, 1)

report_old = "3. **Personnel reliability:** whole-row visible text is no longer accepted as proof of specialist training. Explicit MissionChief training attributes remain supported; absent evidence remains bounded or unknown."
report_new = "3. **Personnel reliability:** unrestricted whole-row prose is no longer accepted as proof of specialist training. Explicit MissionChief training attributes and bracketed qualification badges remain supported; absent evidence remains bounded or unknown."
if text.count(report_old) != 1:
    raise RuntimeError("audit report personnel wording anchor missing")
text = text.replace(report_old, report_new, 1)

PACKAGE.write_text(text, encoding="utf-8")
runpy.run_path(str(PACKAGE), run_name="__main__")
PACKAGE.unlink(missing_ok=True)
OLD_WRAPPER.unlink(missing_ok=True)
DIAGNOSTIC.unlink(missing_ok=True)
