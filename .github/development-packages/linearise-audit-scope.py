#!/usr/bin/env python3
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
REFINER = ROOT / '.github' / 'scripts' / 'refine_full_userscript_audit.py'
AUDIT_DOC = ROOT / 'docs' / 'FULL_PROJECT_AUDIT.md'


def replace_once(text: str, old: str, new: str, label: str) -> str:
    count = text.count(old)
    if count != 1:
        raise RuntimeError(f'{label}: expected one match, found {count}')
    return text.replace(old, new, 1)


def main() -> int:
    text = REFINER.read_text(encoding='utf-8')
    old_helper = '''def lexical_block_parent(masked_source: str, offset: int) -> tuple[int, int] | None:
    """Return the nearest enclosing brace block while preserving source offsets.

    Function extraction is deliberately conservative and may not inventory every
    enclosing function expression. A brace-stack parent therefore provides a more
    reliable same-scope key for local helper names without treating helpers in two
    separate Promise callbacks as duplicates.
    """
    stack: list[int] = []
    for index, character in enumerate(masked_source[:offset]):
        if character == "{":
            stack.append(index)
        elif character == "}" and stack:
            stack.pop()
    if not stack:
        return None
    opening = stack[-1]
    return opening, base.line_number(masked_source, opening)
'''
    new_helper = '''def lexical_block_parents(masked_source: str, offsets: list[int]) -> dict[int, tuple[int, int] | None]:
    """Resolve nearest enclosing brace blocks for all declarations in one pass."""
    pending = sorted(set(offsets))
    parents: dict[int, tuple[int, int] | None] = {}
    stack: list[tuple[int, int]] = []
    target_index = 0
    line = 1

    for index, character in enumerate(masked_source):
        while target_index < len(pending) and pending[target_index] <= index:
            offset = pending[target_index]
            parents[offset] = stack[-1] if stack else None
            target_index += 1
        if character == "{":
            stack.append((index, line))
        elif character == "}" and stack:
            stack.pop()
        if character == "\\n":
            line += 1

    while target_index < len(pending):
        offset = pending[target_index]
        parents[offset] = stack[-1] if stack else None
        target_index += 1
    return parents
'''
    text = replace_once(text, old_helper, new_helper, 'lexical helper')
    text = replace_once(
        text,
        '    records = [item for item in raw["details"]["functionInventory"] if item["name"] not in RESERVED]\n\n    for item in records:\n',
        '    records = [item for item in raw["details"]["functionInventory"] if item["name"] not in RESERVED]\n    scope_parents = lexical_block_parents(masked_source, [item["start"] for item in records])\n\n    for item in records:\n',
        'scope parent inventory',
    )
    text = replace_once(
        text,
        '        item["parent"] = lexical_block_parent(masked_source, item["start"])\n',
        '        item["parent"] = scope_parents.get(item["start"])\n',
        'scope parent lookup',
    )
    REFINER.write_text(text, encoding='utf-8')

    audit = AUDIT_DOC.read_text(encoding='utf-8')
    audit = audit.replace(
        'lexical block analysis replaces the previous function-inventory parent heuristic,',
        'a single-pass lexical block analysis replaces the previous function-inventory parent heuristic,',
        1,
    )
    AUDIT_DOC.write_text(audit, encoding='utf-8')
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
