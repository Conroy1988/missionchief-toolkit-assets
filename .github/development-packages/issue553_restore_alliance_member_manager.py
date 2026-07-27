#!/usr/bin/env python3
"""Restore Alliance Member Manager and apply the Issue #553 menu hotfix."""
from __future__ import annotations

import hashlib
import json
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
RESTORE_REF = "232cca3144a2b4eddb104ceeaa017f5f99f9a92c"
SOURCE = ROOT / "src/MissionChief_Map_Command_Toolkit.user.js"
CONTRACT = ROOT / ".github/scripts/test_alliance_member_manager_contract.py"
PREFLIGHT = ROOT / ".github/scripts/run_userscript_preflight.sh"
HEADROOM = ROOT / ".github/fixtures/main-style-source-headroom.json"
HELP_MANIFEST = ROOT / "help/manifest.json"
HELP_INDEX = ROOT / "help/index.html"
CHANGELOG = ROOT / "CHANGELOG.md"
VALIDATOR = ROOT / ".github/scripts/validate_userscript.py"
RUNTIME_TEST = ROOT / ".github/scripts/test_issue553_alliance_member_manager_menu_runtime.js"
RUNTIME_FIXTURE = ROOT / ".github/fixtures/issue553-alliance-member-manager-menu.json"
ROLLBACK_CONTRACT = ROOT / ".github/scripts/test_issue554_alliance_member_manager_rollback.py"

RESTORE_PATHS = (
    ".github/fixtures/main-style-source-headroom.json",
    ".github/performance-budget.json",
    ".github/scripts/run_userscript_preflight.sh",
    ".github/scripts/test_alliance_member_manager_contract.py",
    "CHANGELOG.md",
    "docs/site-data.json",
    "help/index.html",
    "help/manifest.json",
    "src/MissionChief_Map_Command_Toolkit.user.js",
)


def restore(path: str) -> None:
    payload = subprocess.run(
        ["git", "show", f"{RESTORE_REF}:{path}"],
        cwd=ROOT,
        check=True,
        capture_output=True,
    ).stdout
    target = ROOT / path
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_bytes(payload)


def replace_once(path: Path, old: str, new: str) -> None:
    text = path.read_text(encoding="utf-8")
    count = text.count(old)
    if count != 1:
        raise RuntimeError(
            f"{path.relative_to(ROOT)} expected one replacement target, found {count}"
        )
    path.write_text(text.replace(old, new, 1), encoding="utf-8")


def write_new(path: Path, content: str) -> None:
    if path.exists():
        raise RuntimeError(f"Refusing to overwrite existing file: {path.relative_to(ROOT)}")
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")


for relative in RESTORE_PATHS:
    restore(relative)
ROLLBACK_CONTRACT.unlink(missing_ok=True)

replace_once(SOURCE, "// @version      8.1.0", "// @version      8.1.1")
replace_once(SOURCE, "version: '8.1.0'", "version: '8.1.1'")
replace_once(
    SOURCE,
    '''    function allianceMemberManagerMapBlockerButton(panel) {
        return panel.querySelector(
            '[data-feature="allianceBuildingsMapBlocker"], ' +
            '[data-toggle-feature="allianceBuildingsMapBlocker"], ' +
            '[data-mcms-feature="allianceBuildingsMapBlocker"]'
        );
    }
''',
    '''    function allianceMemberManagerMapBlockerButton(panel) {
        const attributed = panel.querySelector(
            '[data-feature="allianceBuildingsMapBlocker"], ' +
            '[data-toggle-feature="allianceBuildingsMapBlocker"], ' +
            '[data-mcms-feature="allianceBuildingsMapBlocker"]'
        );
        if (attributed) return attributed;
        return Array.from(panel.querySelectorAll('.mcms-toggle-btn')).find(button =>
            button.querySelector('.mcms-label')?.textContent?.trim() === 'Alliance Map Blocker'
        ) || null;
    }
''',
)

replace_once(
    CONTRACT,
    'assert re.search(r"^// @version\\s+8\\.1\\.0$", source, re.MULTILINE)\n'
    '    assert "version: \'8.1.0\'" in source',
    'assert re.search(r"^// @version\\s+8\\.1\\.1$", source, re.MULTILINE)\n'
    '    assert "version: \'8.1.1\'" in source',
)
replace_once(
    CONTRACT,
    '        "allianceBuildingsMapBlocker",\n'
    '        "data-mcms-alliance-member-manager-toggle",',
    '        "allianceBuildingsMapBlocker",\n'
    '        "panel.querySelectorAll(\'.mcms-toggle-btn\')",\n'
    '        "button.querySelector(\'.mcms-label\')?.textContent?.trim() === \'Alliance Map Blocker\'",\n'
    '        "data-mcms-alliance-member-manager-toggle",',
)
replace_once(
    CONTRACT,
    '    assert "## [8.1.0] - 2026-07-27" in changelog\n'
    '    assert "### Alliance Member Manager" in changelog',
    '    assert "## [8.1.1] - 2026-07-27" in changelog\n'
    '    assert "### Alliance Member Manager menu hotfix" in changelog\n'
    '    assert "## [8.1.0] - 2026-07-27" in changelog',
)
replace_once(
    CONTRACT,
    '    assert ".github/scripts/test_alliance_member_manager_contract.py" in preflight',
    '    assert ".github/scripts/test_alliance_member_manager_contract.py" in preflight\n'
    '    assert "test_issue553_alliance_member_manager_menu_runtime.js" in preflight\n'
    '    assert "test_issue554_alliance_member_manager_rollback.py" not in preflight',
)

replace_once(
    PREFLIGHT,
    "node .github/scripts/test_issue517_incident_command_wire_runtime.js\n",
    "node .github/scripts/test_issue517_incident_command_wire_runtime.js\n"
    "node .github/scripts/test_issue553_alliance_member_manager_menu_runtime.js\n",
)

fixture = {
    "schemaVersion": 1,
    "description": "Issue #553 live Tools-menu shapes for Alliance Map Blocker discovery.",
    "cases": [
        {
            "name": "live rendered card without feature attributes",
            "attributeIndex": None,
            "labels": ["Clean", "Alliance Map Blocker", "Personal Missions"],
            "expectedIndex": 1,
        },
        {
            "name": "feature attribute remains authoritative",
            "attributeIndex": 0,
            "labels": ["Legacy attributed blocker", "Alliance Map Blocker"],
            "expectedIndex": 0,
        },
        {
            "name": "trimmed rendered label is accepted",
            "attributeIndex": None,
            "labels": ["  Alliance Map Blocker  "],
            "expectedIndex": 0,
        },
        {
            "name": "similar labels do not false-match",
            "attributeIndex": None,
            "labels": ["Alliance Map Block", "Alliance Member Manager"],
            "expectedIndex": None,
        },
    ],
}
write_new(RUNTIME_FIXTURE, json.dumps(fixture, indent=2) + "\n")

runtime_test = r'''#!/usr/bin/env node
"use strict";

const assert = require("node:assert/strict");
const fs = require("node:fs");
const path = require("node:path");
const vm = require("node:vm");

const root = path.resolve(__dirname, "../..");
const source = fs.readFileSync(
  path.join(root, "src/MissionChief_Map_Command_Toolkit.user.js"),
  "utf8"
);
const fixture = JSON.parse(
  fs.readFileSync(
    path.join(root, ".github/fixtures/issue553-alliance-member-manager-menu.json"),
    "utf8"
  )
);

function extractFunction(name) {
  const marker = `    function ${name}(`;
  const start = source.indexOf(marker);
  assert.notEqual(start, -1, `${name} is missing`);
  const brace = source.indexOf("{", start);
  let depth = 0;
  let quote = "";
  let escaped = false;
  for (let index = brace; index < source.length; index += 1) {
    const char = source[index];
    if (quote) {
      if (escaped) escaped = false;
      else if (char === "\\") escaped = true;
      else if (char === quote) quote = "";
      continue;
    }
    if (char === "'" || char === '"' || char === "`") {
      quote = char;
      continue;
    }
    if (char === "{") depth += 1;
    if (char === "}") {
      depth -= 1;
      if (depth === 0) return source.slice(start, index + 1);
    }
  }
  throw new Error(`Unable to extract ${name}`);
}

const functionText = extractFunction("allianceMemberManagerMapBlockerButton");
const sandbox = {};
vm.runInNewContext(
  `${functionText}\nthis.resolveBlocker = allianceMemberManagerMapBlockerButton;`,
  sandbox
);

for (const item of fixture.cases) {
  const buttons = item.labels.map(labelText => ({
    querySelector(selector) {
      assert.equal(selector, ".mcms-label");
      return { textContent: labelText };
    },
  }));
  const panel = {
    querySelector(selector) {
      assert.match(selector, /allianceBuildingsMapBlocker/);
      return item.attributeIndex === null ? null : buttons[item.attributeIndex];
    },
    querySelectorAll(selector) {
      assert.equal(selector, ".mcms-toggle-btn");
      return buttons;
    },
  };
  const result = sandbox.resolveBlocker(panel);
  if (item.expectedIndex === null) assert.equal(result, null, item.name);
  else assert.equal(result, buttons[item.expectedIndex], item.name);
}

console.log(
  `Issue #553 menu runtime passed: ${fixture.cases.length} rendered-menu discovery cases.`
);
'''
write_new(RUNTIME_TEST, runtime_test)

replace_once(
    CHANGELOG,
    "# Changelog\n\n",
    '''# Changelog

## [8.1.1] - 2026-07-27

### Alliance Member Manager menu hotfix

- Restored the complete Alliance Member Manager after the unshipped rollback candidate was merged into `main` in error.
- Restored the missing **Alliance Operations** section and **Alliance Member Manager** toggle in the live Tools panel.
- Kept feature-attribute discovery as the preferred path and added an exact rendered-label fallback for the existing **Alliance Map Blocker** card.
- Added executable regression coverage using the production menu shape where the blocker button has no feature-specific `data-*` attribute.

''',
)

help_manifest = json.loads(HELP_MANIFEST.read_text(encoding="utf-8"))
help_manifest["guideVersion"] = "8.1.1"
help_manifest["toolkitVersion"] = "8.1.1"
help_manifest["runtimeGuidePatch"] = (
    "Toolkit v8.1.1 restores the complete Alliance Member Manager and the missing "
    "Alliance Operations menu section by supporting the live rendered Alliance Map "
    "Blocker card while preserving the v8.1.0 member-list lifecycle boundaries."
)
HELP_MANIFEST.write_text(json.dumps(help_manifest, indent=2) + "\n", encoding="utf-8")
HELP_INDEX.write_text(
    HELP_INDEX.read_text(encoding="utf-8").replace("v8.1.0", "v8.1.1"),
    encoding="utf-8",
)

source_bytes = SOURCE.read_bytes()
source_text = source_bytes.decode("utf-8")
headroom = json.loads(HEADROOM.read_text(encoding="utf-8"))
candidate = headroom["v8Candidate"]
candidate.update(
    {
        "issue": 553,
        "version": "8.1.1",
        "sourceBytes": len(source_bytes),
        "sourceLines": len(source_text.splitlines()),
        "sourceSha256": hashlib.sha256(source_bytes).hexdigest(),
        "baseline": "8.1.0",
        "approvedGrowth": {
            "sourceBytes": len(source_bytes) - 1641668,
            "sourceLines": len(source_text.splitlines()) - 25008,
            "templateBytes": 0,
            "templateLines": 0,
        },
        "scope": (
            "Issue #553 restoration of Alliance Member Manager after an unshipped rollback, "
            "with attribute-first and exact rendered-label menu discovery plus executable fixtures"
        ),
    }
)
HEADROOM.write_text(json.dumps(headroom, indent=2) + "\n", encoding="utf-8")

subprocess.run([sys.executable, str(VALIDATOR)], cwd=ROOT, check=True)
subprocess.run([sys.executable, str(CONTRACT)], cwd=ROOT, check=True)
subprocess.run(["node", str(RUNTIME_TEST)], cwd=ROOT, check=True)

assert not ROLLBACK_CONTRACT.exists()
assert "Alliance Member Manager" in SOURCE.read_text(encoding="utf-8")
print("Issue #553 Alliance Member Manager restoration and v8.1.1 menu hotfix validated.")
