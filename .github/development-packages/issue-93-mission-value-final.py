#!/usr/bin/env python3
from pathlib import Path
import hashlib
import json
import subprocess

root = Path(__file__).resolve().parents[2]
source_path = root / "src" / "MissionChief_Map_Command_Toolkit.user.js"
original_package = Path(__file__).with_name("issue-93-mission-value.py")
package_text = original_package.read_text(encoding="utf-8")
package_text = package_text.replace("test_source = r'''#!/usr/bin/env python3", 'test_source = r"""#!/usr/bin/env python3', 1)
package_text = package_text.replace("\n'''\nTEST.write_text(test_source, encoding=\"utf-8\")", '\n"""\nTEST.write_text(test_source, encoding="utf-8")', 1)

anchor = "        reconcileFeatureRefreshes({ includeSnapshots: missionSnapshotsNeeded(), positionPanel: false });\n"
variant = "        reconcileFeatureRefreshes( { includeSnapshots: missionSnapshotsNeeded(), positionPanel: false });\n"
source = source_path.read_text(encoding="utf-8")
positions = []
start = 0
while True:
    index = source.find(anchor, start)
    if index < 0:
        break
    positions.append(index)
    start = index + len(anchor)
if len(positions) != 3:
    raise AssertionError(f"Expected three shared refresh calls, found {len(positions)}")
toggle_start = source.index("    function toggleFeature(feature) {")
toggle_end = source.index("\n    function ", toggle_start + 10)
targets = [position for position in positions if toggle_start < position < toggle_end]
if len(targets) != 1:
    raise AssertionError(f"Expected one refresh call inside toggleFeature, found {len(targets)}")
target = targets[0]
parts = []
cursor = 0
for position in positions:
    parts.append(source[cursor:position])
    parts.append(anchor if position == target else variant)
    cursor = position + len(anchor)
parts.append(source[cursor:])
source_path.write_text("".join(parts), encoding="utf-8")

try:
    namespace = {"__name__": "__main__", "__file__": str(original_package)}
    exec(compile(package_text, str(original_package), "exec"), namespace, namespace)

    final_source = source_path.read_text(encoding="utf-8").replace(variant, anchor)
    if variant in final_source:
        raise AssertionError("Temporary refresh-call variant remained")
    source_path.write_text(final_source, encoding="utf-8")

    payload = source_path.read_bytes()
    digest = hashlib.sha256(payload).hexdigest()
    for path in [
        root / "dist" / "MissionChief_Map_Command_Toolkit.user.js",
        root / "dist" / "MissionChief_Map_Command_Toolkit.txt",
    ]:
        path.write_bytes(payload)
    (root / "dist" / "SHA256SUMS.txt").write_text(
        f"{digest}  MissionChief_Map_Command_Toolkit.user.js\n{digest}  MissionChief_Map_Command_Toolkit.txt\n",
        encoding="utf-8",
    )
    manifest_path = root / "dist" / "release-manifest.json"
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    manifest["sha256"] = digest
    manifest["bytes"] = len(payload)
    manifest["lines"] = len(final_source.splitlines())
    manifest_path.write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")

    subprocess.run(["python3", str(root / ".github" / "scripts" / "test_mission_value_contract.py")], check=True, cwd=root)
    subprocess.run(["node", "--check", str(source_path)], check=True, cwd=root)
finally:
    original_package.unlink(missing_ok=True)
    Path(__file__).with_name("issue-93-mission-value-fixed.py").unlink(missing_ok=True)
    (root / ".github" / "diagnostics" / "issue-93-package-error.txt").unlink(missing_ok=True)
