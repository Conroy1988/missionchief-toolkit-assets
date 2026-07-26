#!/usr/bin/env python3
from pathlib import Path
import json
r=Path(__file__).resolve().parents[2]
v=(r/".github/workflows/validate-userscript.yml").read_text()
a=(r/".github/workflows/auto-release-after-validation.yml").read_text()
p=(r/".github/workflows/release-toolkit.yml").read_text()
assert "Prepare immutable release-ready bundle" in v and "release-bundle/" in v
assert "release-readiness-check.yml" not in a and "validation_run_id:" in a and "validated_sha:" in a
assert "Consume exact successful PR validation tree" in a
assert "Upload promoted merged-main candidate" in a
assert "Post-merge userscript validation used: no" in a
for token in ("Resolve exact immutable release candidate","Verify Greasy Fork and back up concurrently","BACKUP_PID=$!","GF_PID=$!","sleep 2","sleep 5","sleep 15","Dispatch GitHub Pages asynchronously","status/release-speed-history.json","status/RELEASE_SPEED.md"):
    assert token in p, token
assert "gh run watch" not in p
h=json.loads((r/"status/release-speed-history.json").read_text())
assert h["targets"]["normalHotfixPrToVerifiedMedianSeconds"]==240
assert "Expected reduction" in (r/"status/RELEASE_SPEED.md").read_text()

assert chr(1) not in p
assert p.count("      - name: Record successful release, manifest, announcement and speed state") == 1
assert 'echo "- ✅ Greasy Fork verification and private backup ran concurrently"' in p
assert 'GitHub Pages deployment dispatched asynchronously: ${PAGES_DISPATCHED}' in p

print("Release Pipeline v4 publication contract passed with v5 validated-tree promotion.")
