from pathlib import Path

original = Path('.github/development-packages/issue-73-desktop-menu-height.py')
old_wrappers = [
    Path('.github/development-packages/issue-73-desktop-menu-height-fixed.py'),
    Path('.github/development-packages/issue-73-desktop-menu-height-fixed2.py'),
    Path('.github/development-packages/issue-73-desktop-menu-height-fixed3.py'),
]
text = original.read_text(encoding='utf-8')
start_old = "    harness = f'''\"use strict\";"
start_new = '    harness = f\"\"\"\"use strict\";'
end_old = "console.log(`Desktop panel layout contract passed: ${{fixtures.boundsCases.length}} bounds and ${{fixtures.clampCases.length}} saved-position cases.`);\n'''\n    with tempfile.TemporaryDirectory"
end_new = 'console.log(`Desktop panel layout contract passed: ${{fixtures.boundsCases.length}} bounds and ${{fixtures.clampCases.length}} saved-position cases.`);\n\"\"\"\n    with tempfile.TemporaryDirectory'
if text.count(start_old) != 1 or text.count(end_old) != 1:
    raise RuntimeError('Embedded harness delimiters were not found exactly once')
text = text.replace(start_old, start_new, 1).replace(end_old, end_new, 1)
workflow_start = text.index("workflow = WORKFLOW.read_text(encoding='utf-8')")
workflow_end_marker = "WORKFLOW.write_text(workflow, encoding='utf-8')"
workflow_end = text.index(workflow_end_marker, workflow_start) + len(workflow_end_marker)
text = text[:workflow_start] + "print('Audit workflow hook deferred to the reviewed PR branch.')" + text[workflow_end:]
compile(text, str(original), 'exec')
exec(compile(text, str(original), 'exec'), {'__name__': '__main__', '__file__': str(original)})
original.unlink()
for wrapper in old_wrappers:
    if wrapper.exists():
        wrapper.unlink()
