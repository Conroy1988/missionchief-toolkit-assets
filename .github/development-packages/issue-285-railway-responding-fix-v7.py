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
    payload = replace_once(
        payload,
        '    DATA.write_text(json.dumps(dataset, separators=(",", ":"), ensure_ascii=False) + "\\n", encoding="utf-8")\n',
        '    railway["types"] = sorted(set(int(value) for value in railway.get("types", [])) | {108})\n    railway["requireExplicitTraining"] = True\n    DATA.write_text(json.dumps(dataset, separators=(",", ":"), ensure_ascii=False) + "\\n", encoding="utf-8")\n',
        "standalone Railway Police carrier contract",
    )
    payload = replace_once(
        payload,
        '    runtime_railway["countable"] = True\n',
        '    runtime_railway["countable"] = True\n    runtime_railway["types"] = sorted(set(int(value) for value in runtime_railway.get("types", [])) | {108})\n    runtime_railway["requireExplicitTraining"] = True\n',
        "embedded Railway Police carrier contract",
    )

    old_contract = '''    railway_contract_anchor = '    assert re.search(r"(?:key|[\\'\\"]key[\\'\\"])\\\\s*:\\\\s*[\\'\\"]railway-police-officer[\\'\\"][^\\\\n]*(?:training|[\\'\\"]training[\\'\\"])\\\\s*:\\\\s*\\\\[[^\\\\]]*Railway Police", source), "Railway Police personnel must require explicit training evidence"\\n'
    railway_contract = \'\'\'    assert '\"key\":\"railway-police-officer\"' in source and '\"railway_police\"' in source, "Railway Police must use the native education key"\\n    assert "if ((definition?.group || 'vehicles') === 'staff') continue" in source, "vehicle labels must not prove specialist personnel roles"\\n    assert "missionRequirementsLinkedTrainingValues(candidate, vehicleId, vehicleElement)" in source, "responding units must resolve linked specialist metadata"\\n    assert "missionRequirementsResolvedStaffCapacity(vehicleId, typeId, vehicleElement, mode)" in source, "responding mode must reach the crew resolver"\\n    assert "mode === 'responding' ? missionRequirementsRespondingCrewCapacity(element) : null" in source, "canonical responding crew must be acquired explicitly"\\n\'\'\'
    contract = replace_once(contract, railway_contract_anchor, railway_contract_anchor + railway_contract, "Issue 285 contract assertions")
'''
    new_contract = '''    railway_contract_marker = '    assert "!reconciled.requirements.length && !reconciled.unresolved.length" in source, "unresolved authority must not collapse to an empty success state"\\n'
    railway_contract = \'\'\'    assert '\"key\":\"railway-police-officer\"' in source and '\"railway_police\"' in source, "Railway Police must use the native education key"\\n    assert '\"requireExplicitTraining\":true' in source, "Railway Police carrier type must not prove specialist qualification"\\n    assert "if ((definition?.group || 'vehicles') === 'staff') continue" in source, "vehicle labels must not prove specialist personnel roles"\\n    assert "missionRequirementsLinkedTrainingValues(candidate, vehicleId, vehicleElement)" in source, "responding units must resolve linked specialist metadata"\\n    assert "missionRequirementsResolvedStaffCapacity(vehicleId, typeId, vehicleElement, mode)" in source, "responding mode must reach the crew resolver"\\n    assert "mode === 'responding' ? missionRequirementsRespondingCrewCapacity(element) : null" in source, "canonical responding crew must be acquired explicitly"\\n\'\'\'
    contract = replace_once(contract, railway_contract_marker, railway_contract + railway_contract_marker, "Issue 285 contract assertions")
'''
    payload = replace_once(payload, old_contract, new_contract, "stable contract assertion insertion")

    old_contribution = "function missionRequirementsUnitContribution(requirement, unit) { const definition = requirement.definition || {}; const definitionTypes = Array.from(definition.types || []); const typeEligible = definitionTypes.includes(unit.typeId); const equipmentEligible = Array.from(definition.equipment || []).some(equipment => unit.equipment.has(String(equipment).toLowerCase())); const labelEligible = unit.knownDefinitionKeys?.has?.(definition.key) || missionRequirementsDefinitionMatchesValues(definition, unit.labels); const compatibleTractiveTypes = Array.from(unit.compatibleTractiveTypes || []).map(Number).filter(Number.isFinite); const tractiveEligible = definition.pair !== true && compatibleTractiveTypes.length > 0 && compatibleTractiveTypes.every(type => definitionTypes.includes(type)); const trainingRequired = Array.from(definition.training || []).length > 0; const trainingEligible = trainingRequired && missionRequirementsDefinitionMatchesValues(definition, unit.training, 'training'); const arrTokens = new Set(Array.from(definition.arrAttributes || []).map(missionRequirementsCapabilityLabel).filter(Boolean)); const arrEligible = arrTokens.size > 0 && Array.from(unit.arrCapabilities || []).some(capability => arrTokens.has(missionRequirementsCapabilityLabel(capability))); const arrClassificationKnown = arrTokens.size === 0 || unit.arrCapabilityKnown === true; const eligible = requirement.group === 'staff' && trainingRequired ? trainingEligible || arrEligible || typeEligible : typeEligible || equipmentEligible || labelEligible || tractiveEligible; const classificationUnknown = requirement.group === 'staff' && trainingRequired ? Boolean(unit.staff && !eligible && !arrClassificationKnown && !unit.training?.size) : unit.typeId < 0 && !unit.knownDefinitionKeys?.size && !unit.equipment?.size && !compatibleTractiveTypes.length; if (!eligible) return { eligible: false, unknown: classificationUnknown, capacity: missionRequirementsCapacity(0, classificationUnknown ? null : 0, !classificationUnknown) }; if (requirement.group === 'staff') { const capacity = unit.staff ? missionRequirementsCapacity(unit.staff.min ?? unit.staff.value ?? 0, unit.staff.max, unit.staff.known) : missionRequirementsCapacity(0, null, false); return { eligible: true, unknown: capacity.max === null, capacity }; } const factor = tractiveEligible && !typeEligible ? 1 : Number(definition.factors?.[unit.typeId] ?? definition.factors?.[String(unit.typeId)] ?? 1); const value = Number.isFinite(factor) && factor > 0 ? factor : 1; return { eligible: true, unknown: false, capacity: missionRequirementsCapacity(value, value, true) }; }"
    new_contribution = "function missionRequirementsUnitContribution(requirement, unit) { const definition = requirement.definition || {}; const definitionTypes = Array.from(definition.types || []); const typeEligible = definitionTypes.includes(unit.typeId); const equipmentEligible = Array.from(definition.equipment || []).some(equipment => unit.equipment.has(String(equipment).toLowerCase())); const labelEligible = unit.knownDefinitionKeys?.has?.(definition.key) || missionRequirementsDefinitionMatchesValues(definition, unit.labels); const compatibleTractiveTypes = Array.from(unit.compatibleTractiveTypes || []).map(Number).filter(Number.isFinite); const tractiveEligible = definition.pair !== true && compatibleTractiveTypes.length > 0 && compatibleTractiveTypes.every(type => definitionTypes.includes(type)); const trainingRequired = Array.from(definition.training || []).length > 0; const explicitTrainingRequired = definition.requireExplicitTraining === true; const trainingEligible = trainingRequired && missionRequirementsDefinitionMatchesValues(definition, unit.training, 'training'); const arrTokens = new Set(Array.from(definition.arrAttributes || []).map(missionRequirementsCapabilityLabel).filter(Boolean)); const arrEligible = arrTokens.size > 0 && Array.from(unit.arrCapabilities || []).some(capability => arrTokens.has(missionRequirementsCapabilityLabel(capability))); const arrClassificationKnown = arrTokens.size === 0 || unit.arrCapabilityKnown === true; const eligible = requirement.group === 'staff' && trainingRequired ? trainingEligible || arrEligible || (!explicitTrainingRequired && typeEligible) : typeEligible || equipmentEligible || labelEligible || tractiveEligible; const plausibleExplicitCarrier = explicitTrainingRequired && (typeEligible || labelEligible); const classificationUnknown = requirement.group === 'staff' && trainingRequired ? Boolean(unit.staff && !eligible && !unit.training?.size && (plausibleExplicitCarrier || !arrClassificationKnown)) : unit.typeId < 0 && !unit.knownDefinitionKeys?.size && !unit.equipment?.size && !compatibleTractiveTypes.length; if (!eligible) return { eligible: false, unknown: classificationUnknown, capacity: missionRequirementsCapacity(0, classificationUnknown ? null : 0, !classificationUnknown) }; if (requirement.group === 'staff') { const capacity = unit.staff ? missionRequirementsCapacity(unit.staff.min ?? unit.staff.value ?? 0, unit.staff.max, unit.staff.known) : missionRequirementsCapacity(0, null, false); return { eligible: true, unknown: capacity.max === null, capacity }; } const factor = tractiveEligible && !typeEligible ? 1 : Number(definition.factors?.[unit.typeId] ?? definition.factors?.[String(unit.typeId)] ?? 1); const value = Number.isFinite(factor) && factor > 0 ? factor : 1; return { eligible: true, unknown: false, capacity: missionRequirementsCapacity(value, value, true) }; }"
    source_write = '    SOURCE.write_text(source, encoding="utf-8")\n'
    contribution_patch = f'''    source = replace_once(\n        source,\n        {old_contribution!r},\n        {new_contribution!r},\n        "explicit specialist carrier evidence boundary",\n    )\n'''
    payload = replace_once(payload, source_write, contribution_patch + source_write, "unit contribution transformation")

    ORIGINAL.write_text(payload, encoding="utf-8")
    py_compile.compile(str(ORIGINAL), doraise=True)
    subprocess.run(["python3", str(ORIGINAL)], cwd=ROOT, check=True)
    for path in (
        ORIGINAL,
        ROOT / ".github/development-packages/issue-285-railway-responding-fix-v2.py",
        ROOT / ".github/development-packages/issue-285-railway-responding-fix-v4.py",
        ROOT / ".github/development-packages/issue-285-railway-responding-fix-v6.py",
        ROOT / "docs/issue-285-package-diagnostic.txt",
        ROOT / "docs/issue-285-final-package-diagnostic.txt",
        ROOT / "docs/issue-285-v6-diagnostic.txt",
        ROOT / "docs/issue-285-contribution-diagnostic.txt",
    ):
        path.unlink(missing_ok=True)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
