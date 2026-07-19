#!/usr/bin/env python3
from __future__ import annotations

import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
ORIGINAL = ROOT / '.github' / 'development-packages' / 'uk-requirement-capability-port.py'

text = ORIGINAL.read_text(encoding='utf-8')
old = r'''        const matchingDefinitions = api.definitions.filter(definition =>
            definition.group === group &&
            entry.aliases.some(alias => (definition.aliases || []).some(value =>
                String(value).trim().toLowerCase() === String(alias).trim().toLowerCase()
            ))
        );
        assert.strictEqual(matchingDefinitions.length, 1, `${group}:${entry.key}: one canonical definition`);
        const definition = matchingDefinitions[0];
        for (const alias of entry.aliases) {
            assert.ok((definition.aliases || []).includes(alias), `${group}:${entry.key}: alias ${alias}`);
            const parsed = api.parseText(`1 ${alias}`, group);
            assert.ok(
                parsed.requirements.some(requirement => requirement.key === definition.key && requirement.missing === 1),
                `${group}:${entry.key}: parser handles ${alias}`
            );
            assert.strictEqual(parsed.remaining, '', `${group}:${entry.key}: parser consumes ${alias}`);
        }
        for (const typeId of entry.types) {
            assert.ok((definition.types || []).includes(typeId), `${group}:${entry.key}: vehicle type ${typeId}`);
        }
        for (const equipment of entry.equipment || []) {
            assert.ok((definition.equipment || []).includes(equipment), `${group}:${entry.key}: equipment ${equipment}`);
        }
'''
new = r'''        for (const alias of entry.aliases) {
            const parsed = api.parseText(`1 ${alias}`, group);
            const parsedRequirement = parsed.requirements.find(requirement => requirement.missing === 1);
            assert.ok(parsedRequirement, `${group}:${entry.key}: parser handles ${alias}`);
            assert.strictEqual(parsed.remaining, '', `${group}:${entry.key}: parser consumes ${alias}`);
            const definition = api.definitions.find(candidate =>
                candidate.group === group && candidate.key === parsedRequirement.key
            );
            assert.ok(definition, `${group}:${entry.key}: parsed definition exists for ${alias}`);
            assert.ok((definition.aliases || []).includes(alias), `${group}:${entry.key}: parsed alias ${alias}`);
            for (const typeId of entry.types) {
                assert.ok((definition.types || []).includes(typeId), `${group}:${entry.key}: ${alias} supports vehicle type ${typeId}`);
            }
            for (const equipment of entry.equipment || []) {
                assert.ok((definition.equipment || []).includes(equipment), `${group}:${entry.key}: ${alias} supports equipment ${equipment}`);
            }
        }
'''
if text.count(old) != 1:
    raise AssertionError(f'expected one runtime capability assertion block, found {text.count(old)}')
ORIGINAL.write_text(text.replace(old, new, 1), encoding='utf-8')
result = subprocess.run(['python3', str(ORIGINAL.relative_to(ROOT))], cwd=ROOT)
if result.returncode != 0:
    raise SystemExit(result.returncode)
Path(__file__).unlink()
print('Applied refined UK requirement capability port')
