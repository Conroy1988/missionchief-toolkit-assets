from pathlib import Path

original = Path('.github/development-packages/issue-73-desktop-menu-height.py')
old_wrappers = [
    Path('.github/development-packages/issue-73-desktop-menu-height-fixed.py'),
    Path('.github/development-packages/issue-73-desktop-menu-height-fixed2.py'),
]
text = original.read_text(encoding='utf-8')
start_old = "    harness = f'''\"use strict\";"
start_new = '    harness = f\"\"\"\"use strict\";'
end_old = "console.log(`Desktop panel layout contract passed: ${{fixtures.boundsCases.length}} bounds and ${{fixtures.clampCases.length}} saved-position cases.`);\n'''\n    with tempfile.TemporaryDirectory"
end_new = 'console.log(`Desktop panel layout contract passed: ${{fixtures.boundsCases.length}} bounds and ${{fixtures.clampCases.length}} saved-position cases.`);\n\"\"\"\n    with tempfile.TemporaryDirectory'
if text.count(start_old) != 1:
    raise RuntimeError(f'Expected one harness opening delimiter, found {text.count(start_old)}')
if text.count(end_old) != 1:
    raise RuntimeError(f'Expected one harness closing delimiter, found {text.count(end_old)}')
text = text.replace(start_old, start_new, 1).replace(end_old, end_new, 1)
compile(text, str(original), 'exec')
exec(compile(text, str(original), 'exec'), {'__name__': '__main__', '__file__': str(original)})
original.unlink()
for wrapper in old_wrappers:
    if wrapper.exists():
        wrapper.unlink()
