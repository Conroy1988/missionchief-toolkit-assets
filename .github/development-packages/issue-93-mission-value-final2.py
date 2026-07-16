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

source = source_path.read_text(encoding="utf-8")

def scope_shared_anchor(text, anchor, variant, target_start, target_end, expected_count):
    positions = []
    cursor = 0
    while True:
        index = text.find(anchor, cursor)
        if index < 0:
            break
        positions.append(index)
        cursor = index + len(anchor)
    if len(positions) != expected_count:
        raise AssertionError(f"Expected {expected_count} occurrences of shared anchor, found {len(positions)}")
    targets = [position for position in positions if target_start < position < target_end]
    if len(targets) != 1:
        raise AssertionError(f"Expected one scoped target, found {len(targets)}")
    target = targets[0]
    chunks = []
    cursor = 0
    for position in positions:
        chunks.append(text[cursor:position])
        chunks.append(anchor if position == target else variant)
        cursor = position + len(anchor)
    chunks.append(text[cursor:])
    return "".join(chunks)

toggle_start = source.index("    function toggleFeature(feature) {")
toggle_end = source.index("\n    function ", toggle_start + 10)
refresh_anchor = "        reconcileFeatureRefreshes({ includeSnapshots: missionSnapshotsNeeded(), positionPanel: false });\n"
refresh_variant = "        reconcileFeatureRefreshes( { includeSnapshots: missionSnapshotsNeeded(), positionPanel: false });\n"
source = scope_shared_anchor(source, refresh_anchor, refresh_variant, toggle_start, toggle_end, 3)

update_start = source.index("    function updateUI() {")
panel_values_start = source.index("        const toggleValues = {", update_start)
panel_values_end = source.index("        };", panel_values_start) + len("        };")
ui_anchor = "            missionInspector: state.missionInspector,\n"
ui_variant = "            missionInspector: Boolean(state.missionInspector),\n"
source = scope_shared_anchor(source, ui_anchor, ui_variant, panel_values_start, panel_values_end, 2)
source_path.write_text(source, encoding="utf-8")

try:
    namespace = {"__name__": "__main__", "__file__": str(original_package)}
    exec(compile(package_text, str(original_package), "exec"), namespace, namespace)

    final_source = source_path.read_text(encoding="utf-8").replace(refresh_variant, refresh_anchor).replace(ui_variant, ui_anchor)
    if refresh_variant in final_source or ui_variant in final_source:
        raise AssertionError("Temporary scoped variants remained")
    source_path.write_text(final_source, encoding="utf-8")

    payload = source_path.read_bytes()
    digest = hashlib.sha256(payload).hexdigest()
    for path in [root / "dist" / "MissionChief_Map_Command_Toolkit.user.js", root / "dist" / "MissionChief_Map_Command_Toolkit.txt"]:
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
    for name in [
        "issue-93-mission-value.py",
        "issue-93-mission-value-fixed.py",
        "issue-93-mission-value-final.py",
    ]:
        Path(__file__).with_name(name).unlink(missing_ok=True)
    for name in ["issue-93-package-error.txt", "issue-93-final-package-error.txt"]:
        (root / ".github" / "diagnostics" / name).unlink(missing_ok=True)
