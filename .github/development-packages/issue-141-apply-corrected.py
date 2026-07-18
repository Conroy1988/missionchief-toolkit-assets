#!/usr/bin/env python3
from __future__ import annotations

import base64
import re
import subprocess
import sys
import zlib
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
PACKAGES = ROOT / ".github" / "development-packages"
TARGET = PACKAGES / "issue-141-mission-requirements-completeness.py"
SELF = Path(__file__).resolve()
CLEANUP = [
    SELF,
    PACKAGES / "issue-141-diagnostic.py",
    PACKAGES / "issue-141-diagnostic-launcher.py",
    PACKAGES / "issue-141-inspect-resolve.py",
    PACKAGES / "issue-141-mission-requirements-completeness.payload.py",
]

original_loader = TARGET.read_bytes()
loader_text = original_loader.decode("utf-8")
match = re.search(r"b64decode\('([^']+)'\)", loader_text)
if not match:
    raise AssertionError("Issue #141 package payload was not found")

package_source = zlib.decompress(base64.b64decode(match.group(1))).decode("utf-8")
start_marker = "resolve_masked = audit.mask_non_code(source)"
end_marker = "unknown_helper = r'''function missionRequirementsUnknownCoverageRow"
start = package_source.find(start_marker)
end = package_source.find(end_marker, start)
if start < 0 or end < 0:
    raise AssertionError("Issue #141 resolve transform boundaries were not found")

corrected = '''resolve_masked = audit.mask_non_code(source)
resolve_matches = list(re.finditer(r"\\bfunction\\s+missionRequirementsResolve\\s*\\(", resolve_masked))
if len(resolve_matches) != 1:
    raise AssertionError(f"Expected one declaration for missionRequirementsResolve, found {len(resolve_matches)}")
resolve_start = resolve_matches[0].start()
resolve_opening = resolve_masked.find("{", resolve_start)
resolve_closing = audit.matching_brace(resolve_masked, resolve_opening)
if resolve_opening < 0 or resolve_closing is None:
    raise AssertionError("Could not extract missionRequirementsResolve")
resolve_function = source[resolve_start:resolve_closing + 1]
resolve_needle = "return parsed.requirements.map(requirement => {\\n            const condition = missionRequirementsDefinitionCondition(requirement.definition, candidate);"
if resolve_function.count(resolve_needle) != 1:
    raise AssertionError("missionRequirementsResolve callback anchor missing or duplicated")
resolve_function = resolve_function.replace(
    resolve_needle,
    "return parsed.requirements.map(requirement => {\\n"
    "            if (requirement.definition?.countable === false) return missionRequirementsUnknownCoverageRow(requirement);\\n"
    "            const condition = missionRequirementsDefinitionCondition(requirement.definition, candidate);",
    1
)
'''
package_source = package_source[:start] + corrected + package_source[end:]
payload = base64.b64encode(zlib.compress(package_source.encode("utf-8"), 9)).decode("ascii")
patched_loader = (
    "#!/usr/bin/env python3\n"
    "import base64, zlib\n"
    f"exec(compile(zlib.decompress(base64.b64decode('{payload}')), __file__, 'exec'))\n"
)

try:
    TARGET.write_text(patched_loader, encoding="utf-8")
    result = subprocess.run([sys.executable, str(TARGET)], cwd=ROOT)
    if result.returncode != 0:
        raise SystemExit(result.returncode)
finally:
    TARGET.write_bytes(original_loader)

for path in CLEANUP:
    try:
        path.unlink(missing_ok=True)
    except TypeError:
        if path.exists():
            path.unlink()

print("Issue #141 corrected package applied; diagnostic control files removed")
