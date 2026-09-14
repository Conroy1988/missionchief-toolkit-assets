"""Reproducible store packaging of the approved 0.23.14 code, as 1.0.0."""
import hashlib, json, pathlib, runpy, shutil, zipfile
root = pathlib.Path(__file__).resolve().parent
runpy.run_path(str(root / 'build-recovered.py'))
out = root.parent / '.dev/home-response-extension'
manifest = json.loads((out / 'manifest.json').read_text())
manifest.update(version='1.0.0', version_name='Extension 1.0.0 · Toolkit 10.18.1', description='Map controls, mission insights, finance and Home Response Builder for MissionChief UK. Independent community extension.')
(out / 'manifest.json').write_text(json.dumps(manifest, indent=2) + '\n')
(out / 'BUILD.json').write_text(json.dumps({'extensionVersion':'1.0.0','toolkitVersion':'10.18.1','recoveredBaseline':'0.22.3','codeBaseline':'0.23.14','channel':'stable','automatedTests':59,'liveValidation':'User-reported builder acceptance; latest speed improvement unmeasured'}, indent=2) + '\n')
p = out / 'popup.html'
p.write_text(p.read_text().replace('>Early Access<', '>1.0.0<'))
p = out / 'help.html'
s = p.read_text().replace('Extension 0.21.0 · UI test candidate · Toolkit 10.18.1','Extension 1.0.0 · Toolkit 10.18.1').replace('1.0 release-candidate testing is ongoing; compatibility status does not certify every feature on every browser.','Compatibility status does not certify every feature on every browser.')
s = s.replace('<h2>Tasks and recovery</h2>', '''<h2>Home Response Builder</h2><p>Open Operations → Home Response Builder. Choose a UK city from search or the dropdown, select an area directly on the map, draw a boundary, or use a centre and radius. City boundary is the default. Choose minimum straight-line spacing of 1, 3, 4, 6, 8 or 10 miles and up to 1,000 new buildings. The maximum is a cap, not a target. Preview proposals, existing-building exclusions, mapped water and the estimated Credit cost before building.</p><p>The nearest dispatch centre is selected automatically. Named gold map markers and the distance-sorted list let you change it. Acknowledge the assigned centre and distances before starting or resuming. Choose a supported vehicle and optionally a building icon. Scan icons by building type; the catalogue is remembered for this account in this browser until refreshed or site storage is cleared.</p><p>Construction, vehicle purchases and optional icon copying run as a saved sequence. Keep the game tab open. Use Pause, Stop or Review &amp; resume. Recovery checks existing buildings and vehicles before retrying uncertain steps. Review stage timings to see where each location spends time. Minimum spacing is not driving distance or guaranteed coverage. Check small waterways and road access visually; staffing and training are not supplied automatically.</p><h2>Tasks and recovery</h2>''')
p.write_text(s)
p = out / 'privacy.html'
s = p.read_text().replace('Extension 0.21.0, UI test candidate. Updated 12 September 2026.','Extension 1.0.0. Updated 13 September 2026.')
s = s.replace('<h2>Network requests and other providers</h2>', '''<h2>Home Response Builder data</h2><p>Builder plans, progress, selected game locations, building and vehicle references, dispatch-centre assignment and icon catalogue references are saved in MissionChief site-local browser storage, scoped to the verified game account. Icon catalogues also record the selected building type and remain until refreshed or that site's storage is cleared. Saved catalogues contain image references and counts rather than downloaded image bytes. Uninstalling the extension does not necessarily clear MissionChief site storage. Plans never resume purchases without user confirmation.</p><h2>Network requests and other providers</h2>''')
s = s.replace('<h2>Limits and sharing</h2>', '''<p>City search and map-area selection send the entered place query or clicked map coordinates to OpenStreetMap's Nominatim service to obtain public geographic boundaries. These are user-selected game-planning locations, not device GPS readings. The preview map requests OpenStreetMap tiles for the viewed area. These providers receive normal network metadata. Search results are cached temporarily and requests are rate-limited. Coastline and major-lake geometry is bundled with the extension for local water checks; map attribution and geographic-data licences are included.</p><h2>Limits and sharing</h2>''')
p.write_text(s)
for name in ['release-notes.html','README.md']:
    shutil.copyfile(root / 'store' / name, out / name)
archive = out.parent / 'MissionChief-Toolkit-Extension-1.0.0.zip'
with zipfile.ZipFile(archive, 'w', zipfile.ZIP_DEFLATED) as z:
    for p in sorted(out.rglob('*')):
        if p.is_file():
            z.writestr(zipfile.ZipInfo(str(p.relative_to(out)), (2026,1,1,0,0,0)), p.read_bytes(), compress_type=zipfile.ZIP_DEFLATED)
print(archive)
print('SHA256', hashlib.sha256(archive.read_bytes()).hexdigest())
