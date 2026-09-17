# Extension source — 2.0.0

[Project](../README.md) · [User guide](../docs/EXTENSION_GUIDE.md) · [Complete changes](CHANGELOG.md)

`current/` contains **all 91 files from the 2.0.0 package submitted to Google on 17 September 2026**. The [submission record](store/SUBMISSION-2.0.0.md) distinguishes submitted and publicly available versions. Install public updates through the Chrome Web Store.

## Verify and build

Requires Python 3. From the repository root:

```sh
python3 extension/prepare-current-release.py
```

The script verifies every file against `release-2.0.0.json`, including the exact path set, SHA-256 hashes, file count and manifest version. It fails on missing, unexpected or changed files. It then builds `.dev/MissionChief-Toolkit-Extension-2.0.0.zip`, reopens it and checks every payload again. ZIP metadata and compression may differ from the submitted archive; matching payload hashes are the source-equivalence check.

For local development, load `extension/current/` as an unpacked extension. Disable the Store copy first. Do not ship a changed snapshot as 2.0.0: create a new version, review its inventory and validate the resulting package. Test builds stay out of GitHub releases.

## Repository map

| Path | Purpose |
|---|---|
| `current/` | Exact submitted extension, executable modules, UI, data, audio and artwork |
| `release-2.0.0.json` | Authoritative file inventory and original archive fingerprint |
| `prepare-current-release.py` | Current integrity gate and reproducible payload packaging |
| `store/` | Listing, privacy policy and dated submission records |
| `recovered-0.22.3/`, feature directories and `build-*-test.py` | Historical recovery and earlier implementation/test fixtures |
| `prepare-legacy-1.2.5.py` | Historical 1.2.5 composition, retained for existing fixture tests only |

The submitted package is a verified recovered working build. It is not a promise that every module can be regenerated from the older composition pipeline. Packaged documentation and validation records are preserved exactly for provenance; this README and the 2.0 submission record describe the current release.

Preserve geographic licences and original source notices. Executable code must remain packaged locally. Never commit real tokens or Discord webhook URLs. Developer: **Conroy1988**.
