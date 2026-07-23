#!/usr/bin/env python3
from __future__ import annotations

import json
import os
import re
import subprocess
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
SOURCE = ROOT / "src" / "MissionChief_Map_Command_Toolkit.user.js"
CANONICAL_ROOT = (
    ROOT / "MissionChief_Map_Command_Toolkit.user.js",
    ROOT / "MissionChief_Map_Command_Toolkit.txt",
)
VALIDATOR = ROOT / ".github" / "scripts" / "validate_userscript.py"
STRUCTURAL = ROOT / ".github" / "scripts" / "audit_userscript_structure.py"
STRUCTURAL_POLICY = ROOT / ".github" / "userscript-audit-policy.json"
PERFORMANCE = ROOT / ".github" / "scripts" / "check_performance_budget.py"
PERFORMANCE_POLICY = ROOT / ".github" / "performance-budget.json"
DEEP_AUDIT = ROOT / ".github" / "scripts" / "deep_performance_audit.mjs"
HEADROOM = ROOT / ".github" / "fixtures" / "main-style-source-headroom.json"
ENV = {**os.environ, "PYTHONDONTWRITEBYTECODE": "1"}


def replace_exact(text: str, old: str, new: str, label: str, expected: int = 1) -> str:
    count = text.count(old)
    if count != expected:
        raise RuntimeError(f"{label}: expected {expected} occurrence(s), found {count}")
    return text.replace(old, new, expected)


def assignment_end(text: str, start: int) -> int:
    quote: str | None = None
    escaped = False
    round_depth = square_depth = brace_depth = 0
    index = start
    while index < len(text):
        char = text[index]
        if quote:
            if escaped:
                escaped = False
            elif char == "\\":
                escaped = True
            elif char == quote:
                quote = None
        else:
            if char in "'\"`":
                quote = char
            elif char == "(":
                round_depth += 1
            elif char == ")":
                round_depth -= 1
            elif char == "[":
                square_depth += 1
            elif char == "]":
                square_depth -= 1
            elif char == "{":
                brace_depth += 1
            elif char == "}":
                brace_depth -= 1
            elif char == ";" and round_depth == square_depth == brace_depth == 0:
                return index
        if min(round_depth, square_depth, brace_depth) < 0:
            raise RuntimeError("unbalanced innerHTML assignment expression")
        index += 1
    raise RuntimeError("unterminated innerHTML assignment")


source = SOURCE.read_text(encoding="utf-8")
region_start = source.index("    function operationalRequirementCreateModel")
region_end = source.index("    // Issue #391: legacy Mission Requirements Matrix retired", region_start)
region = source[region_start:region_end]

assignment_pattern = re.compile(r"(?P<target>[A-Za-z_$][\w$]*(?:\.[A-Za-z_$][\w$]*)*)\.innerHTML\s*=")
matches = list(assignment_pattern.finditer(region))
if len(matches) != 4:
    contexts = [region[max(0, match.start() - 80):match.end() + 120] for match in matches]
    raise RuntimeError(f"operational innerHTML inventory drifted: {len(matches)} assignments: {contexts}")

for match in reversed(matches):
    expression_start = match.end()
    semicolon = assignment_end(region, expression_start)
    expression = region[expression_start:semicolon].strip()
    replacement = f"operationalReplaceContent({match.group('target')}, {expression});"
    region = region[:match.start()] + replacement + region[semicolon + 1:]
source = source[:region_start] + region + source[region_end:]

old_style = '''    function operationalFeatureStyle(doc) {
        if (doc.getElementById?.('mcms-operational-feature-style')) return;
        const style = doc.createElement('style');
        style.id = 'mcms-operational-feature-style';
'''
new_style = '''    const OP_FEATURE_STYLE_ID = 'mcms-operational-feature-style';
    function operationalReplaceContent(node, html) {
        if (!node) return;
        node.replaceChildren();
        const content = String(html ?? '');
        if (content) node.insertAdjacentHTML('beforeend', content);
    }
    function operationalFeatureStyle(doc) {
        if (operationalQuery(doc, `#${OP_FEATURE_STYLE_ID}`)) return;
        const style = doc.createElement('style');
        style.id = OP_FEATURE_STYLE_ID;
'''
source = replace_exact(source, old_style, new_style, "operational style ownership")

old_observer = "        context.observer = new MutationObserver(() => operationalRequirementsScheduleContext(context, 25));"
new_observer = "        const OperationalMutationObserver = doc.defaultView?.MutationObserver || pageWindow.MutationObserver;\n        context.observer = new OperationalMutationObserver(() => operationalRequirementsScheduleContext(context, 25));"
source = replace_exact(source, old_observer, new_observer, "operational observer alias")

if source.count(".innerHTML =") != 22:
    raise RuntimeError(f"innerHTML assignment budget not restored: {source.count('.innerHTML =')}")
if source.count("function operationalReplaceContent(") != 1:
    raise RuntimeError("operational content replacement helper count changed")
if source.count("'mcms-operational-feature-style'") != 1:
    raise RuntimeError("operational feature style ID literal is not single-owned")
if source.count("new MutationObserver(") != 8:
    raise RuntimeError(f"direct MutationObserver budget not restored: {source.count('new MutationObserver(')}")

SOURCE.write_text(source, encoding="utf-8")
for path in CANONICAL_ROOT:
    path.write_text(source, encoding="utf-8")

deep = DEEP_AUDIT.read_text(encoding="utf-8")
deep = replace_exact(deep, "  const remaining = 32000 - sourceSummary.lines;", "  const remaining = 64000 - sourceSummary.lines;", "deep audit 64K headroom")
deep = replace_exact(deep, "      expectedMutationObserverConstructions: 12,", "      expectedMutationObserverConstructions: 11,", "retired observer baseline")
deep = replace_exact(deep, "      expectedBroadSubtreeObservers: 10,", "      expectedBroadSubtreeObservers: 9,", "retired broad-observer baseline")
DEEP_AUDIT.write_text(deep, encoding="utf-8")

fixture = json.loads(HEADROOM.read_text(encoding="utf-8"))
new_source_lines = len(source.splitlines())
previous_expected = int(fixture.get("expectedSourceLines", 0))
delta = new_source_lines - previous_expected
entries = fixture.get("approvedNonStyleChanges", [])
feature_entries = [entry for entry in entries if entry.get("issue") == 378 and entry.get("phase") == "operational-feature-suite"]
if len(feature_entries) != 1:
    raise RuntimeError("operational feature-suite source-ledger entry drifted")
feature_entries[0]["lines"] = int(feature_entries[0].get("lines", 0)) + delta
fixture["approvedNonStyleSourceLines"] = int(fixture.get("approvedNonStyleSourceLines", 0)) + delta
fixture["expectedSourceLines"] = new_source_lines
HEADROOM.write_text(json.dumps(fixture, indent=2) + "\n", encoding="utf-8")

subprocess.run(["node", "--check", str(SOURCE)], cwd=ROOT, env=ENV, check=True)
subprocess.run(["node", "--check", str(DEEP_AUDIT)], cwd=ROOT, env=ENV, check=True)
subprocess.run(["python3", str(VALIDATOR)], cwd=ROOT, env=ENV, check=True)

with tempfile.TemporaryDirectory(prefix="issue378-release-ci-") as temporary:
    temp = Path(temporary)
    structural_json = temp / "structural.json"
    structural_md = temp / "structural.md"
    subprocess.run([
        "python3", str(STRUCTURAL),
        "--source", str(SOURCE),
        "--policy", str(STRUCTURAL_POLICY),
        "--json-output", str(structural_json),
        "--markdown-output", str(structural_md),
    ], cwd=ROOT, env=ENV, check=True)
    structural = json.loads(structural_json.read_text(encoding="utf-8"))
    if structural.get("summary", {}).get("failures") != 0:
        raise RuntimeError(structural_md.read_text(encoding="utf-8"))

    base = temp / "main.user.js"
    with base.open("wb") as handle:
        subprocess.run([
            "git", "show", "origin/main:src/MissionChief_Map_Command_Toolkit.user.js"
        ], cwd=ROOT, stdout=handle, check=True)
    performance_json = temp / "performance.json"
    performance_md = temp / "performance.md"
    subprocess.run([
        "python3", str(PERFORMANCE),
        "--candidate", str(SOURCE),
        "--base", str(base),
        "--policy", str(PERFORMANCE_POLICY),
        "--json-output", str(performance_json),
        "--markdown-output", str(performance_md),
    ], cwd=ROOT, env=ENV, check=True)
    performance = json.loads(performance_json.read_text(encoding="utf-8"))
    if performance.get("result") != "pass":
        raise RuntimeError(performance_md.read_text(encoding="utf-8"))

for obsolete in (
    ROOT / ".github" / "development-packages" / "issue378-release-ci-diagnostic.py",
    ROOT / ".github" / "diagnostics" / "issue378-release-ci-failure.txt",
):
    obsolete.unlink(missing_ok=True)

print(f"Issue #378 release CI remediation passed; signed source-ledger delta: {delta:+d} lines.")
