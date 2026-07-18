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
OUTPUT = PACKAGES / "issue-141-last-diagnostic.txt"

loader_text = TARGET.read_text(encoding="utf-8")
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
TARGET.write_text(
    "#!/usr/bin/env python3\nimport base64, zlib\n"
    f"exec(compile(zlib.decompress(base64.b64decode('{payload}')), __file__, 'exec'))\n",
    encoding="utf-8",
)
result = subprocess.run(
    [sys.executable, str(TARGET)],
    cwd=ROOT,
    text=True,
    stdout=subprocess.PIPE,
    stderr=subprocess.STDOUT,
)
lines = [line if len(line) <= 800 else "[oversized generated line omitted]" for line in result.stdout.splitlines()]
bounded = "\n".join(lines[-240:])[-24000:]
subprocess.run(["git", "reset", "--hard", "HEAD"], cwd=ROOT, check=True)
subprocess.run(["git", "clean", "-fd"], cwd=ROOT, check=True)
OUTPUT.write_text(f"returncode={result.returncode}\n\n{bounded}\n", encoding="utf-8")
print(f"Captured Issue #141 corrected-package result: {result.returncode}")
