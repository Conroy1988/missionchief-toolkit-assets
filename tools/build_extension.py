#!/usr/bin/env python3
"""Build the local MV3 pilot without modifying canonical source/distribution.

Every source adaptation fails closed on upstream drift. Vendored code is verified
against extension/vendor-lock.json before it is included in the package.
"""
import hashlib
import json
from pathlib import Path
import re
import shutil
import zipfile

ROOT = Path(__file__).resolve().parents[1]
EXT = ROOT / 'extension'
OUT = ROOT / '.dev' / 'chromium-extension'


def replace_once(text, old, new):
    if text.count(old) != 1:
        raise ValueError(f'Source adaptation drift: {old[:80]}')
    return text.replace(old, new, 1)


def build():
    manifest = json.loads((EXT / 'manifest.json').read_text())
    version = manifest['version']
    original = (ROOT / 'src/MissionChief_Map_Command_Toolkit.user.js').read_text()
    if hashlib.sha256(original.encode()).hexdigest() != '8d66d8d724309192cc87d0c9e6c2bcb01b381c1fe40ffaa1449519cdd690fdbd':
        raise ValueError('Pilot source baseline changed: review adapters before updating the pinned source hash.')
    source = original
    transport = (EXT / 'transport-sweep.js').read_text()
    sections = dict(re.findall(r'// @section (\w+)\n(.*?)(?=// @section |\Z)', transport, re.S))
    for section, first, following in (
        ('hydrate', '    async function hydrateTransportSweepMobileMissions()', '    function transportSweepFallbackMissionIds('),
        ('records', '    function transportSweepMissionRecords(', '    function buildTransportSweepQueue('),
        ('scan', '    async function scanTransportSweepQueue()', '    function transportSweepHudElements()'),
        ('fetch', '    async function transportSweepFetchMissionDocument(', '    async function transportSweepFetchMissionCandidates('),
    ):
        start = source.index(first)
        end = source.index(following, start)
        source = source[:start] + sections[section] + '\n' + source[end:]
    source = replace_once(source, "            showToast('No alliance patient transports found');",
        "            const discovery = transportSweepRuntime.discovery;\n            showToast(discovery && (discovery.failed || discovery.unchecked || !missionProgressPageMissionRecords.size) ? 'Transport scan incomplete — check the scan log before retrying' : 'No alliance patient transports found');")
    start = source.index('    async function loadFastMapEngine() {')
    end = source.index('    function fastMapFeatureCollection(', start)
    source = source[:start] + '''    async function loadFastMapEngine() {
        const developmentFactory = fastMapDevelopmentEngineFactory();
        if (developmentFactory) return {kind: 'fixture', create: config => developmentFactory.create(config)};
        if (fastMapRuntime.engineLibrary) return {kind: 'maplibre', library: fastMapRuntime.engineLibrary};
        if (!fastMapRuntime.enginePromise) {
            fastMapRuntime.enginePromise = pilotLoadEngine().then(library => {
                fastMapRuntime.engineLibrary = library;
                return {kind: 'maplibre', library};
            }).catch(error => { fastMapRuntime.enginePromise = null; throw error; });
        }
        return fastMapRuntime.enginePromise;
    }

''' + source[end:]
    source = source.replace('pageWindow.localStorage', 'localStorage')
    source = source.replace("Tampermonkey cross-origin requests are unavailable.", "This request is unavailable in the extension pilot.")
    source = source.replace("Tampermonkey storage is unavailable.", "Private integrations are unavailable in the extension pilot.")
    source = replace_once(source, '    function openEncryptedSettingsImport(envelope) {',
        "    function openEncryptedSettingsImport(envelope) {\n        showToast('Use a safe settings export for this pilot. Private integrations are unavailable.'); return;")
    # Updates to the userscript are not extension updates; never invite a second install.
    source = replace_once(source, '    function versionStatusRender() {',
        "    function versionStatusRender() { const pilotButton = document.getElementById(VERSION_STATUS.buttonId); if (pilotButton) { pilotButton.textContent = 'PILOT'; pilotButton.title = 'Early Access extension — updates are managed by your browser'; pilotButton.onclick = event => { event.preventDefault(); event.stopImmediatePropagation(); showToast('Early Access: store installations update through your browser. Unpacked builds require manual replacement.'); }; } return;")
    if re.search(r'\b(?:eval|Function)\s*\(', source):
        raise ValueError('Dynamic code execution remains in the extension build.')
    if OUT.exists():
        shutil.rmtree(OUT)
    OUT.mkdir(parents=True)
    for name in ('manifest.json', 'background.js', 'policy.js', 'bridge.js', 'popup.html', 'popup.css', 'popup.js', 'privacy.html'):
        shutil.copy2(EXT / name, OUT / name)
    shutil.copytree(EXT / 'icons', OUT / 'icons')
    adapter = (EXT / 'adapter.js').read_text()
    (OUT / 'toolkit.js').write_text('(() => {\n"use strict";\n' + adapter + '\n' + source + '\npilot.state = "running";\n})();\n')
    lock = json.loads((EXT / 'vendor-lock.json').read_text())
    vendor = OUT / 'vendor'
    vendor.mkdir()
    for name, entry in lock['files'].items():
        content = (EXT / 'vendor' / name).read_bytes()
        if hashlib.sha256(content).hexdigest() != entry['sha256']:
            raise ValueError(f'Vendor integrity mismatch: {name}')
        (vendor / name).write_bytes(content)
    engine = (vendor / 'maplibre-gl-csp.js').read_text()
    # Keep the page's own maplibregl binding intact; load our packaged copy only once.
    bundle = '(() => { if (window.__MCMS_EXTENSION_MAPLIBRE__) return; const old = globalThis.maplibregl;\n'
    bundle += engine + '\nwindow.__MCMS_EXTENSION_MAPLIBRE__ = globalThis.maplibregl; if (old === undefined) delete globalThis.maplibregl; else globalThis.maplibregl = old; })();\n'
    (vendor / 'maplibre-bundle.js').write_text(bundle)
    (vendor / 'maplibre-gl-csp.js').unlink()
    shutil.copy2(EXT / 'STORE-README.md', OUT / 'README.md')
    receipt = {'extensionVersion': version, 'toolkitVersion': '10.18.1',
        'canonicalSourceSha256': hashlib.sha256(original.encode()).hexdigest(),
        'vendor': lock, 'channel': 'early-access', 'storeSubmission': 'candidate-not-yet-submitted'}
    (OUT / 'BUILD.json').write_text(json.dumps(receipt, indent=2) + '\n')
    tests = OUT.parent / 'extension-contract-results.json'
    if tests.exists():
        report = json.loads(tests.read_text())
        if report.get('testedFiles') and all(hashlib.sha256((OUT / name).read_bytes()).hexdigest() == digest for name, digest in report['testedFiles'].items()):
            shutil.copy2(tests, OUT / 'TEST-RESULTS.json')
    transport_tests = OUT.parent / 'extension-transport-results.json'
    if transport_tests.exists():
        report = json.loads(transport_tests.read_text())
        if report.get('sourceSha256') == hashlib.sha256((OUT / 'toolkit.js').read_bytes()).hexdigest():
            shutil.copy2(transport_tests, OUT / 'TRANSPORT-TEST-RESULTS.json')
    archive = OUT.parent / f'MissionChief-Toolkit-Extension-{version}.zip'
    with zipfile.ZipFile(archive, 'w', zipfile.ZIP_DEFLATED) as z:
        for path in sorted(OUT.rglob('*')):
            if path.is_file():
                info = zipfile.ZipInfo(str(path.relative_to(OUT)), (2026, 1, 1, 0, 0, 0))
                info.compress_type = zipfile.ZIP_DEFLATED
                z.writestr(info, path.read_bytes())
    print(json.dumps({'directory': str(OUT), 'archive': str(archive), 'sourceSha256': receipt['canonicalSourceSha256']}))


if __name__ == '__main__':
    build()
