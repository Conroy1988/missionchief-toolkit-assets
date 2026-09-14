"""Publish the final legacy notice as a complete, verified GitHub release.

Run only in the authorised main-branch GitHub Actions publication job.
Existing release assets are immutable; retries verify rather than overwrite them.
"""
import hashlib
import json
import os
from pathlib import Path
import re
import subprocess
import tempfile
import time
import urllib.request

ROOT = Path(__file__).resolve().parents[1]
REPO = 'Conroy1988/missionchief-toolkit-assets'
BASE = 'https://tkb-gaming.scot/mission-chief-scripts/map-command-toolkit/'


def gh(*args):
    return subprocess.check_output(['gh', *args, '--repo', REPO], text=True)


def fetch(url):
    request = urllib.request.Request(url, headers={'Cache-Control': 'no-cache', 'User-Agent': 'TKB-Legacy-Migration-Verification/1.0'})
    with urllib.request.urlopen(request, timeout=45) as response:
        if response.status != 200:
            raise RuntimeError('Endpoint did not return HTTP 200')
        body = response.read(8 * 1024 * 1024)
        if not body.startswith(b'// ==UserScript=='):
            raise RuntimeError('Endpoint did not return userscript metadata')
        return body


def digest(body):
    return hashlib.sha256(body).hexdigest()


def main():
    if os.environ.get('GITHUB_REPOSITORY') != REPO or os.environ.get('GITHUB_REF') != 'refs/heads/main':
        raise RuntimeError('Publication requires the canonical repository main branch')
    folder = ROOT / '.dev/legacy-migration'
    manifest = json.loads((folder / 'migration-manifest.json').read_text())
    version = manifest['version']
    tag = 'v' + version
    latest = json.loads(gh('release', 'view', '--json', 'tagName'))['tagName']
    if latest not in ('v' + manifest['previousVersion'], tag):
        raise RuntimeError('Latest release changed; refusing to supersede an unexpected version')
    payload = (folder / 'MissionChief_Map_Command_Toolkit.user.js').read_bytes()
    metadata = (folder / 'MissionChief_Map_Command_Toolkit.meta.js').read_bytes()
    if digest(payload) != manifest['sha256']:
        raise RuntimeError('Generated payload digest mismatch')
    # A live preflight is required before changing the latest-release pointer.
    live_meta = fetch(BASE + 'metadata/')
    live_version = re.search(rb'^//\s*@version\s+(\S+)', live_meta, re.M).group(1).decode()
    if live_version not in (manifest['previousVersion'], version):
        raise RuntimeError('Live userscript version is not the expected migration baseline')
    (folder / 'MissionChief_Map_Command_Toolkit.txt').write_bytes(payload)
    # Retain the stylesheet consumed by legacy clients and the website gateway.
    gh('release', 'download', 'v' + manifest['previousVersion'], '--pattern', 'MissionChief_Map_Command_Toolkit.css', '--dir', str(folder), '--clobber')
    css = folder / 'MissionChief_Map_Command_Toolkit.css'
    if not css.is_file() or not css.stat().st_size:
        raise RuntimeError('Prior stylesheet is missing')
    files = sorted(folder.glob('MissionChief_Map_Command_Toolkit.*'))
    expected = {p.name: digest(p.read_bytes()) for p in files}
    evidence = {'version': version, 'purpose': manifest['purpose'], 'developer': 'Conroy1988', 'assets': expected, 'sourceCommit': os.environ['GITHUB_SHA']}
    (folder / 'release-manifest.json').write_text(json.dumps(evidence, indent=2) + '\n')
    files.append(folder / 'release-manifest.json')
    expected['release-manifest.json'] = digest(files[-1].read_bytes())
    existing = subprocess.run(['gh', 'release', 'view', tag, '--repo', REPO, '--json', 'isDraft'], capture_output=True, text=True)
    if existing.returncode == 0:
        draft = json.loads(existing.stdout)['isDraft']
    else:
        notes = ('Final unsupported Tampermonkey update. Adds a migration notice linking to the Chrome Web Store. '
                 'Existing settings and the legacy runtime remain available for export. Disable the old Toolkit script after migrating. '
                 'This is not a Chrome extension release. Sole developer: Conroy1988.')
        gh('release', 'create', tag, '--draft', '--target', os.environ['GITHUB_SHA'], '--title', 'Final userscript migration notice — ' + version, '--notes', notes)
        draft = True
    if draft:
        # Upload only missing assets; never replace a conflicting draft or published asset.
        assets = json.loads(gh('release', 'view', tag, '--json', 'assets'))['assets']
        present = {a['name'] for a in assets}
        missing = [str(p) for p in files if p.name not in present]
        if missing:
            gh('release', 'upload', tag, *missing)
    with tempfile.TemporaryDirectory() as directory:
        gh('release', 'download', tag, '--dir', directory)
        for name, sha in expected.items():
            if digest((Path(directory) / name).read_bytes()) != sha:
                raise RuntimeError('Release asset verification failed: ' + name)
    if draft:
        current = json.loads(gh('release', 'view', '--json', 'tagName'))['tagName']
        if current != latest:
            raise RuntimeError('Latest release changed during preparation')
        gh('release', 'edit', tag, '--draft=false', '--latest')
    endpoints = {'metadata/': digest(metadata), 'update/': digest(payload), 'install/MissionChief_Map_Command_Toolkit.user.js': digest(payload)}
    for attempt in range(6):
        try:
            for path, sha in endpoints.items():
                if digest(fetch(BASE + path)) != sha:
                    raise RuntimeError('Live endpoint digest mismatch: ' + path)
            break
        except Exception:
            if attempt == 5:
                raise
            time.sleep(10)
    result = {'release': tag, 'sourceCommit': os.environ['GITHUB_SHA'], 'liveEndpointHashesVerified': True, 'installedBrowserAcceptance': 'not-performed', 'assets': expected}
    (folder / 'delivery-verification.json').write_text(json.dumps(result, indent=2) + '\n')
    print(json.dumps(result, indent=2))


if __name__ == '__main__':
    main()
