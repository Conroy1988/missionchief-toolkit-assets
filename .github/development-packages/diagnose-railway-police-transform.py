#!/usr/bin/env python3
from pathlib import Path
import re

PACKAGE = Path(__file__).with_name("fix-railway-police-capacity-v4.20.10.py")
text = PACKAGE.read_text(encoding="utf-8")
old = '''row_text_training = "const rowText = missionRequirementsCapabilityLabel(`${row?.textContent || ''} ${row?.innerText || ''}`); if (rowText) { for (const definition of MISSION_REQUIREMENT_DEFINITIONS) { const aliases = Array.from(definition?.training || []).map(missionRequirementsCapabilityLabel).filter(Boolean); if (!aliases.some(alias => rowText.includes(alias))) continue; aliases.forEach(alias => training.add(alias)); knownDefinitionKeys.add(definition.key); } } "
source = replace_once(source, row_text_training, "", "remove generic row-text training inference")
'''
new = '''row_text_pattern = re.compile(
    r"const rowText = missionRequirementsCapabilityLabel\\(`\\$\\{row\\?\\.textContent \\|\\| ''\\} \\$\\{row\\?\\.innerText \\|\\| ''\\}`\\);\\s*"
    r"if \\(rowText\\) \\{\\s*for \\(const definition of MISSION_REQUIREMENT_DEFINITIONS\\) \\{\\s*"
    r"const aliases = Array\\.from\\(definition\\?\\.training \\|\\| \\[\\]\\)\\.map\\(missionRequirementsCapabilityLabel\\)\\.filter\\(Boolean\\);\\s*"
    r"if \\(!aliases\\.some\\(alias => rowText\\.includes\\(alias\\)\\)\\) continue;\\s*"
    r"aliases\\.forEach\\(alias => training\\.add\\(alias\\)\\);\\s*knownDefinitionKeys\\.add\\(definition\\.key\\);\\s*\\}\\s*\\}\\s*"
)
source, row_text_count = row_text_pattern.subn("", source, count=1)
if row_text_count != 1:
    raise AssertionError(f"remove generic row-text training inference: expected one match, found {row_text_count}")
'''
if text.count(old) != 1:
    raise AssertionError("diagnostic could not patch row-text package block")
text = text.replace(old, new, 1)
text = re.sub(r'^subprocess\.run\([^\n]+\)\n', '', text, flags=re.MULTILINE)
text = text.replace('print("Railway Police Officer capacity v4.20.10 hotfix validated")', 'print("Railway Police transformation stage passed")')
namespace = {"__name__": "__main__", "__file__": str(PACKAGE)}
exec(compile(text, str(PACKAGE), "exec"), namespace)
