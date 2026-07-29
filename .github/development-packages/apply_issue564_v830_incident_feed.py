#!/usr/bin/env python3
"""Execute the immutable reviewed Issue #564 package with retained-version contract updates."""
from __future__ import annotations

import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
PACKAGE = ".github/development-packages/apply_issue564_v830_incident_feed.py"
REVIEWED_PACKAGE_COMMIT = "45bdb47d08f5631aa77d239b7889b99c4ff9caf4"
reviewed = subprocess.check_output(
    ["git", "show", f"{REVIEWED_PACKAGE_COMMIT}:{PACKAGE}"],
    cwd=ROOT,
    text=True,
)

old = """write(".github/scripts/test_issue564_incident_feed_attended_runtime.js", runtime_contract)

preflight = read(".github/scripts/run_userscript_preflight.sh")
"""
new = """write(".github/scripts/test_issue564_incident_feed_attended_runtime.js", runtime_contract)

transport_retention = read(".github/scripts/test_transport_sweep_native_contract.py")
transport_retention = replace_once(
    transport_retention,
    "assert re.search(r'(?m)^//\\\\s*@version\\\\s+8\\\\.2\\\\.7$',s)",
    "version_match=re.search(r'(?m)^//\\\\s*@version\\\\s+([^\\\\s]+)$',s);assert version_match and tuple(int(part) for part in version_match.group(1).split('.')) >= (8,2,7)",
    "retained transport version floor",
)
write(".github/scripts/test_transport_sweep_native_contract.py", transport_retention)

issue565_retention = read(".github/scripts/test_issue565_transport_sweep_no_reward.py")
issue565_retention = replace_once(
    issue565_retention,
    "assert re.search(r'(?m)^//\\\\s*@version\\\\s+8\\\\.2\\\\.7$',s)",
    "version_match=re.search(r'(?m)^//\\\\s*@version\\\\s+([^\\\\s]+)$',s);assert version_match and tuple(int(part) for part in version_match.group(1).split('.')) >= (8,2,7)",
    "Issue #565 version floor",
)
issue565_retention = replace_once(
    issue565_retention,
    "assert p['transitionApproval']['version']=='8.2.7'\\nassert p['transitionApproval']['approvedNetworkRequestDelta']==0",
    "assert any(item.get('version')=='8.2.7' and item.get('approvedNetworkRequestDelta')==0 for item in p.get('approvalHistory',[]))",
    "Issue #565 approval-history retention",
)
write(".github/scripts/test_issue565_transport_sweep_no_reward.py", issue565_retention)

preflight = read(".github/scripts/run_userscript_preflight.sh")
"""
if reviewed.count(old) != 1:
    raise RuntimeError(f"reviewed Issue #564 insertion anchor count changed: {reviewed.count(old)}")
corrected = reviewed.replace(old, new, 1)
runtime = ROOT / ".github/development-packages/.apply_issue564_v830_runtime.py"
runtime.write_text(corrected, encoding="utf-8")
try:
    subprocess.run([sys.executable, str(runtime)], cwd=ROOT, check=True)
finally:
    runtime.unlink(missing_ok=True)
