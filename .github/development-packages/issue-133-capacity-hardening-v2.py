#!/usr/bin/env python3
from __future__ import annotations

from pathlib import Path

ROOT = Path.cwd()
ORIGINAL = ROOT / ".github" / "development-packages" / "issue-133-capacity-hardening.py"

package = ORIGINAL.read_text(encoding="utf-8")
write_anchor = 'SOURCE.write_text(source, encoding="utf-8")\n'
if package.count(write_anchor) != 1:
    raise SystemExit(f"capacity package write anchor: expected one, found {package.count(write_anchor)}")

parser_hardening = r"""
source = replace_region(
    source,
    "function missionRequirementsFindDefinitionMatch(",
    "function missionRequirementsParseSource(",
    r'''function missionRequirementsFindDefinitionMatch(text, definition) {
        const numberPattern = '(\\d{1,3}(?:[\\s,.]\\d{3})*|\\d+)';
        const aliases = Array.from(definition.aliases || []).sort((left, right) => right.length - left.length);
        for (const alias of aliases) {
            const labelPattern = missionRequirementsEscapeRegex(alias).replace(/\s+/gu, '\\s+');
            const before = new RegExp(`(^|[,;]\\s*)${numberPattern}\\s*x?\\s+(${labelPattern})(?=\\s*(?:[,;]|$))`, 'iu');
            const beforeMatch = before.exec(text);
            if (beforeMatch) return { match: beforeMatch[0], index: beforeMatch.index, missing: missionRequirementsNumber(beforeMatch[2]), label: beforeMatch[3] };
            const after = new RegExp(`(^|[,;]\\s*)(${labelPattern})\\s*:\\s*${numberPattern}(?=\\s*(?:[,;]|$))`, 'iu');
            const afterMatch = after.exec(text);
            if (afterMatch) return { match: afterMatch[0], index: afterMatch.index, missing: missionRequirementsNumber(afterMatch[3]), label: afterMatch[2] };
        }
        return null;
    }

    function missionRequirementsParseText(rawText, group = 'vehicles') {
        let remaining = String(rawText || '')
            .replace(/\r\n?/gu, '\n')
            .replace(/\n+/gu, '; ')
            .replace(/\s+/gu, ' ')
            .trim();
        const requirements = [];
        const definitions = MISSION_REQUIREMENT_DEFINITIONS.filter(definition => definition.group === group);
        while (remaining) {
            const matches = definitions
                .map(definition => ({ definition, found: missionRequirementsFindDefinitionMatch(remaining, definition) }))
                .filter(candidate => candidate.found && candidate.found.missing > 0)
                .sort((left, right) => left.found.index - right.found.index || right.found.match.length - left.found.match.length);
            if (!matches.length) break;
            const { definition, found } = matches[0];
            requirements.push({
                key: definition.key,
                requirement: definition.label || found.label,
                missing: found.missing,
                group,
                definition
            });
            remaining = `${remaining.slice(0, found.index)} ${remaining.slice(found.index + found.match.length)}`;
        }
        return { requirements, remaining: missionRequirementsCleanRemaining(remaining) };
    }''',
    "source-ordered requirement parser",
)

"""
package = package.replace(write_anchor, parser_hardening + write_anchor, 1)

old_tail = '''SOURCE.write_text(source, encoding="utf-8")
validation = subprocess.run([sys.executable, str(VALIDATOR)], cwd=ROOT)
if validation.returncode != 0:
    raise SystemExit(validation.returncode)
subprocess.run(["node", "--check", str(SOURCE)], cwd=ROOT, check=True)
print("Applied Issue #133 range-aware personnel and capacity hardening")
'''
new_tail = '''SOURCE.write_text(source, encoding="utf-8")
runtime_test = ROOT / ".github" / "scripts" / "test_mission_requirements_runtime.js"
runtime_check = subprocess.run(["node", str(runtime_test)], cwd=ROOT, text=True, capture_output=True)
if runtime_check.returncode != 0:
    combined = "\\n".join(part for part in [runtime_check.stdout, runtime_check.stderr] if part)
    diagnostic = " ".join(combined.strip().split())[-900:] or "unknown runtime fixture failure"
    diagnostic = diagnostic.replace("**", "").replace("`", "'")
    stage = Path(__import__("os").environ.get("RUNNER_TEMP", "/tmp")) / "development-package-stage"
    stage.write_text(f"capacity-runtime-fixture: {diagnostic}", encoding="utf-8")
    if runtime_check.stdout:
        print(runtime_check.stdout, end="")
    if runtime_check.stderr:
        print(runtime_check.stderr, end="", file=sys.stderr)
    raise SystemExit(runtime_check.returncode)
validation = subprocess.run([sys.executable, str(VALIDATOR)], cwd=ROOT)
if validation.returncode != 0:
    raise SystemExit(validation.returncode)
subprocess.run(["node", "--check", str(SOURCE)], cwd=ROOT, check=True)
print("Applied Issue #133 range-aware personnel and capacity hardening")
'''
if package.count(old_tail) != 1:
    raise SystemExit(f"capacity package validation tail: expected one, found {package.count(old_tail)}")
package = package.replace(old_tail, new_tail, 1)

exec(compile(package, str(ORIGINAL), "exec"), {"__name__": "__main__", "__file__": str(ORIGINAL)})
if ORIGINAL.exists():
    ORIGINAL.unlink()
print("Applied Issue #133 capacity hardening v2 with source-ordered parsing")
