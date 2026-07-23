#!/usr/bin/env python3
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
V1 = ROOT / '.github/development-packages/issue470-release.py'
if not V1.exists():
    raise SystemExit('Issue #470 release package is missing')
code = V1.read_text(encoding='utf-8')
old_helper = """    function toolkitApplyCommandBarState(control = document.getElementById(SCRIPT.controlId)) {
        if (!control) return false;
        const open = state.commandBarOpen !== false;
        control.setAttribute('data-mcms-command-bar-open', String(open));
        const button = control.querySelector?.('.mcms-dock-toggle-btn');
        if (button) {
            const label = open ? 'Collapse command bar' : 'Expand command bar';
            button.classList.toggle('mcms-open', open);
            button.setAttribute('aria-expanded', String(open));
            button.setAttribute('aria-label', label);
            button.title = label;
            const icon = button.querySelector?.('.mcms-dock-toggle-icon');
            if (icon) icon.textContent = open ? '▴' : '▾';
        }
        return open;
    }"""
new_helper = """    function toolkitApplyCommandBarState(control = document.getElementById(SCRIPT.controlId)) {
        if (!control) return false;
        const open = state.commandBarOpen !== false;
        control.setAttribute('data-mcms-command-bar-open', String(open));
        for (const selector of ['.mcms-floating-filter', '.mcms-screen-pins']) {
            const element = control.querySelector?.(selector);
            if (!element) continue;
            if (open) element.style.removeProperty('display');
            else element.style.setProperty('display', 'none', 'important');
        }
        const button = control.querySelector?.('.mcms-dock-toggle-btn');
        if (button) {
            const label = open ? 'Collapse command bar' : 'Expand command bar';
            button.classList.toggle('mcms-open', open);
            button.setAttribute('aria-expanded', String(open));
            button.setAttribute('aria-label', label);
            button.title = label;
            const icon = button.querySelector?.('.mcms-dock-toggle-icon');
            if (icon) icon.textContent = open ? '▴' : '▾';
        }
        return open;
    }"""
if old_helper not in code:
    raise SystemExit('Issue #470 command-state helper anchor changed')
code = code.replace(old_helper, new_helper, 1)
css_start = code.index("old_css = '''")
css_end = code.index('\n\ncreate_start, create_end', css_start)
code = code[:css_start] + code[css_end + 2:]
old_test = "  '#${SCRIPT.controlId}[data-mcms-command-bar-open=\"false\"] .mcms-floating-filter',"
new_test = "  \"element.style.setProperty('display', 'none', 'important')\","
if old_test not in code:
    raise SystemExit('Issue #470 local command-state test anchor changed')
code = code.replace(old_test, new_test, 1)
old_slice = "const resolverStart = source.indexOf('    function operationalRequirementsCandidateVisible(');"
new_slice = "const resolverStart = source.indexOf('    const OPERATIONAL_REQUIREMENTS_NATIVE_SELECTOR');"
if old_slice not in code:
    raise SystemExit('Issue #470 resolver fixture anchor changed')
code = code.replace(old_slice, new_slice, 1)
exec(compile(code, __file__, 'exec'))
