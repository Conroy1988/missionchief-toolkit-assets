"""Navigation-only overlay: leave recovered release files untouched."""
def patch_operations_navigation(out):
    path = out / 'toolkit.js'
    text = path.read_text()
    old = "nextAction.classList.add('mcms-next-action');sticky.prepend(nextAction);"
    assert text.count(old) == 1
    text = text.replace(old, old + "sticky.prepend(back);back.title='Return to tool selection. Running tasks and selections are preserved.';")
    old = "function click(e){if(e.target.closest('.mcms-tab-btn')){closeMenu();"
    assert text.count(old) == 1
    text = text.replace(old, "function click(e){const tab=e.target.closest('.mcms-tab-btn');if(tab?.dataset.tab==='administration'){e.preventDefault();e.stopPropagation();closeMenu();api.back();return;}if(tab){closeMenu();")
    path.write_text(text)
    path = out / 'command-ui.css'
    text = path.read_text()
    old = '.mcms-operation-description,.mcms-operation-back,.mcms-operation-card>.mcms-section-label'
    assert text.count(old) == 1
    text = text.replace(old, '.mcms-operation-description,.mcms-operation-card>.mcms-section-label')
    text += '\nhtml body #mc-map-command-toolkit-panel#mc-map-command-toolkit-panel#mc-map-command-toolkit-panel.mcms-command-ui .mcms-operation-sticky > .mcms-operation-back{display:inline-flex!important;align-items:center!important;min-height:44px!important;padding:8px 12px!important;color:#fff!important;background:#271416!important;border:1px solid #d83232!important;opacity:1!important;visibility:visible!important;flex:0 0 auto!important}\n'
    path.write_text(text)
