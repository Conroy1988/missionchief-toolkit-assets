#!/usr/bin/env python3
from __future__ import annotations

import py_compile
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
ORIGINAL = ROOT / ".github/development-packages/issue-285-railway-responding-fix.py"


def replace_once(text: str, old: str, new: str, label: str) -> str:
    count = text.count(old)
    if count != 1:
        raise RuntimeError(f"{label}: expected one match, found {count}")
    return text.replace(old, new, 1)


def main() -> int:
    payload = ORIGINAL.read_text(encoding="utf-8")
    payload = replace_once(
        payload,
        '        """# Issue #285 — Railway Police Responding contract\\n\\n"',
        '        "# Issue #285 — Railway Police Responding contract\\n\\n"',
        "documentation string syntax",
    )
    payload = replace_once(
        payload,
        '''    end = source.find(");", start + len(marker))
    if start < 0 or end < 0:
        raise RuntimeError("unable to locate embedded Mission Requirements definitions")
    payload_start = start + len(marker)
    definitions = json.loads(source[payload_start:end])
''',
        '''    if start < 0:
        raise RuntimeError("unable to locate embedded Mission Requirements definitions")
    payload_start = start + len(marker)
    definitions, consumed = json.JSONDecoder().raw_decode(source[payload_start:])
    end = payload_start + consumed
''',
        "exact embedded definitions JSON boundary",
    )
    old_contract = '''    railway_contract_anchor = '    assert re.search(r"(?:key|[\\'\\"]key[\\'\\"])\\\\s*:\\\\s*[\\'\\"]railway-police-officer[\\'\\"][^\\\\n]*(?:training|[\\'\\"]training[\\'\\"])\\\\s*:\\\\s*\\\\[[^\\\\]]*Railway Police", source), "Railway Police personnel must require explicit training evidence"\\n'
    railway_contract = \'\'\'    assert '\"key\":\"railway-police-officer\"' in source and '\"railway_police\"' in source, "Railway Police must use the native education key"\\n    assert "if ((definition?.group || 'vehicles') === 'staff') continue" in source, "vehicle labels must not prove specialist personnel roles"\\n    assert "missionRequirementsLinkedTrainingValues(candidate, vehicleId, vehicleElement)" in source, "responding units must resolve linked specialist metadata"\\n    assert "missionRequirementsResolvedStaffCapacity(vehicleId, typeId, vehicleElement, mode)" in source, "responding mode must reach the crew resolver"\\n    assert "mode === 'responding' ? missionRequirementsRespondingCrewCapacity(element) : null" in source, "canonical responding crew must be acquired explicitly"\\n\'\'\'
    contract = replace_once(contract, railway_contract_anchor, railway_contract_anchor + railway_contract, "Issue 285 contract assertions")
'''
    new_contract = '''    railway_contract_marker = '    assert "!reconciled.requirements.length && !reconciled.unresolved.length" in source, "unresolved authority must not collapse to an empty success state"\\n'
    railway_contract = \'\'\'    assert '\"key\":\"railway-police-officer\"' in source and '\"railway_police\"' in source, "Railway Police must use the native education key"\\n    assert "if ((definition?.group || 'vehicles') === 'staff') continue" in source, "vehicle labels must not prove specialist personnel roles"\\n    assert "missionRequirementsLinkedTrainingValues(candidate, vehicleId, vehicleElement)" in source, "responding units must resolve linked specialist metadata"\\n    assert "missionRequirementsResolvedStaffCapacity(vehicleId, typeId, vehicleElement, mode)" in source, "responding mode must reach the crew resolver"\\n    assert "mode === 'responding' ? missionRequirementsRespondingCrewCapacity(element) : null" in source, "canonical responding crew must be acquired explicitly"\\n\'\'\'
    contract = replace_once(contract, railway_contract_marker, railway_contract + railway_contract_marker, "Issue 285 contract assertions")
'''
    payload = replace_once(payload, old_contract, new_contract, "stable contract assertion insertion")
    ORIGINAL.write_text(payload, encoding="utf-8")
    py_compile.compile(str(ORIGINAL), doraise=True)
    subprocess.run(["python3", str(ORIGINAL)], cwd=ROOT, check=True)
    for path in (
        ORIGINAL,
        ROOT / ".github/development-packages/issue-285-railway-responding-fix-v2.py",
        ROOT / ".github/development-packages/issue-285-railway-responding-fix-v4.py",
        ROOT / "docs/issue-285-package-diagnostic.txt",
        ROOT / "docs/issue-285-final-package-diagnostic.txt",
    ):
        path.unlink(missing_ok=True)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
