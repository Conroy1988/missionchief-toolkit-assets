#!/usr/bin/env python3
from __future__ import annotations

from pathlib import Path

ROOT = Path.cwd()
ORIGINAL = ROOT / ".github" / "development-packages" / "issue-133-capacity-hardening.py"

package = ORIGINAL.read_text(encoding="utf-8")
anchor = 'SOURCE.write_text(source, encoding="utf-8")\n'
if package.count(anchor) != 1:
    raise SystemExit(f"capacity package write anchor: expected one, found {package.count(anchor)}")

parser_hardening = r"""
source = replace_region(
    source,
    "function missionRequirementsFindDefinitionMatch(",
    "function missionRequirementsParseSource(",
    r'''function missionRequirementsFindDefinitionMatch(text, definition) {
        const numberPattern = '(\\d{1,3}(?:[\\s,.]\\d{3})*|\\d+)';
        const aliases = Array.from(definition.aliases || []).sort((left, right) => right.length - left.length);
        for (const alias of aliases) {
            const labelPattern = missionRequirementsEscapeRegex(alias).replace(/\\\s+/gu, '\\s+');
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
            .replace(/\\r\\n?/gu, '\\n')
            .replace(/\\n+/gu, '; ')
            .replace(/\\s+/gu, ' ')
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
package = package.replace(anchor, parser_hardening + anchor, 1)
exec(compile(package, str(ORIGINAL), "exec"), {"__name__": "__main__", "__file__": str(ORIGINAL)})
if ORIGINAL.exists():
    ORIGINAL.unlink()
print("Applied Issue #133 capacity hardening v2 with source-ordered parsing")
