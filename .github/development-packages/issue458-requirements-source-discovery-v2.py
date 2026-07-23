#!/usr/bin/env python3
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
ORIGINAL = ROOT / '.github/development-packages/issue458-requirements-source-discovery.py'
payload = ORIGINAL.read_text(encoding='utf-8')
old = '''old = """        const requirementRoot = context.doc.querySelector?.('#missing_text');
        if (!requirementRoot?.isConnected || operationalRequirementsEquivalentLssmActive(context.doc)) {
            context.panel?.remove?.();
            context.panel = null;
            context.fingerprint = '';
            return;
        }
        const settings = state.operationalWindow?.requirements || {};
        const model = operationalRequirementCreateModel(operationalRequirementsInput(context, requirementRoot));"""
new = """        const requirementSource = operationalRequirementsResolveSource(context.doc);
        const requirementRoot = requirementSource?.root;
        if (!requirementRoot || requirementSource?.suppressed === true) {
            context.panel?.remove?.();
            context.panel = null;
            context.fingerprint = '';
            return;
        }
        const settings = state.operationalWindow?.requirements || {};
        const model = operationalRequirementCreateModel(operationalRequirementsInput(context, requirementRoot));"""
if old not in text:
    raise SystemExit('Unable to locate requirement renderer source binding')
text = text.replace(old, new, 1)
text = text.replace('''            minified: context.minified === true
        });''', '''            minified: context.minified === true,
            source: requirementSource.fingerprint
        });''', 1)
text = text.replace('        const panel = operationalRequirementsMount(context, requirementRoot);', '        const panel = operationalRequirementsMount(context, requirementSource.anchor || requirementRoot);', 1)
'''
new = '''old = """        const requirementRoot = context.doc.querySelector?.('#missing_text');
        if (!requirementRoot?.isConnected || operationalRequirementsEquivalentLssmActive(context.doc)) {
            context.panel?.remove?.();
            context.panel = null;
            context.fingerprint = '';
            return;
        }
        const settings = state.operationalWindow?.requirements || {};
        const input = operationalRequirementsInput(context, requirementRoot);
        const model = operationalRequirementCreateModel(input);"""
new = """        const requirementSource = operationalRequirementsResolveSource(context.doc);
        const requirementRoot = requirementSource?.root;
        if (!requirementRoot || requirementSource?.suppressed === true) {
            context.panel?.remove?.();
            context.panel = null;
            context.fingerprint = '';
            return;
        }
        const settings = state.operationalWindow?.requirements || {};
        const input = operationalRequirementsInput(context, requirementRoot);
        const model = operationalRequirementCreateModel(input);"""
if old not in text:
    raise SystemExit('Unable to locate the v5.0.4 requirement renderer source binding')
text = text.replace(old, new, 1)
text = text.replace('            source: input.source,', '            source: input.source,\n            sourceRoot: requirementSource.fingerprint,', 1)
text = text.replace('        const panel = operationalRequirementsMount(context, requirementRoot);', '        const panel = operationalRequirementsMount(context, requirementSource.anchor || requirementRoot);', 1)
'''
if old not in payload:
    raise SystemExit('Unable to patch the original Issue #458 package matcher')
payload = payload.replace(old, new, 1)
namespace = {'__file__': str(ORIGINAL), '__name__': '__main__'}
exec(compile(payload, str(ORIGINAL), 'exec'), namespace)
ORIGINAL.unlink(missing_ok=True)
