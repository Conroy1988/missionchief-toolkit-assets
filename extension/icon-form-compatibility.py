"""Match native unassigned dispatch values without changing form submission."""
def patch_icon_form(out):
    path = out / 'toolkit.js'
    text = path.read_text()
    old = ": boolean ? stationIconBoolean(actual) === Boolean(expected)\n            : actual === String(expected ?? '');"
    new = ": boolean ? stationIconBoolean(actual) === Boolean(expected)\n            : name === 'building[leitstelle_building_id]'\n                ? (actual.trim() || '0') === (String(expected ?? '').trim() || '0')\n                : actual === String(expected ?? '');"
    assert text.count(old) == 1
    path.write_text(text.replace(old, new))
