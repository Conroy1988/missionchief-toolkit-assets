#!/usr/bin/env python3
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
RUNTIME = ROOT / ".github" / "scripts" / "test_mission_requirements_runtime.js"
runtime = RUNTIME.read_text(encoding="utf-8")
old = "let issue206Row = api.resolve(issue206Candidate, issue206Parsed, issue206Catalogue)[0];"
new = "const issue206DebugUnits = api.collectUnits(issue206Candidate, 'responding'); console.log('ISSUE206_DEBUG', JSON.stringify({ selectors: api.operationalSelectors('responding'), directRows: issue206Window.querySelectorAll('tbody#mission_vehicle_driving > tr').length, active: api.operationalActive(issue206Police.row, issue206Candidate), typeId: api.vehicleType(issue206Police.row), vehicleId: api.vehicleId(issue206Police.row), units: issue206DebugUnits.map(unit => ({ typeId: unit.typeId, vehicleId: unit.vehicleId, contributionKey: unit.contributionKey })), aggregate: api.aggregate({ group: 'vehicles', definition: issue206PoliceDefinition }, issue206DebugUnits) })); let issue206Row = api.resolve(issue206Candidate, issue206Parsed, issue206Catalogue)[0];"
count = runtime.count(old)
if count != 1:
    raise AssertionError(f"debug insertion: expected one match, found {count}")
RUNTIME.write_text(runtime.replace(old, new, 1), encoding="utf-8")
print("Added temporary Issue #206 unit-boundary diagnostic")
