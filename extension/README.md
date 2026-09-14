# Extension source

The Chrome Web Store is the public distribution channel. Start with the [project README](../README.md) or [user guide](../docs/EXTENSION_GUIDE.md).

## Current build

Extension **1.2.5**, bundled Toolkit **10.18.1**. This records the submitted package, not a claim of Google approval.

| Path | Purpose |
|---|---|
| `recovered-0.22.3/` | Recovered baseline with recorded security amendments |
| `home-response/` | Coverage planning, native actions, saved queues, geography and UI |
| `hospital-upgrades/` | Direct target-level hospital upgrades |
| `unit-switcher/` | Home Response vehicle replacement and native Credit-shop discovery |
| `build-*-test.py` | Compose the baseline with maintained modules for testing |
| `prepare-current-release.py` | Produce the stable 1.2.5 Store package |
| `store/` | Listing text, privacy disclosure and submission records |

## Build and test

From the repository root, with Python 3 and Node.js installed:

```sh
npm ci --prefix extension/home-response
python3 extension/prepare-current-release.py
node --test extension/home-response/*.test.mjs extension/hospital-upgrades/*.test.mjs extension/unit-switcher/*.test.mjs
```

Output: `.dev/MissionChief-Toolkit-Extension-1.2.5.zip`. Load an unpacked test build from `.dev/home-response-extension` only for development. Do not enable it alongside the Store edition or a legacy Toolkit script.

The package is composed from a recovered release rather than a clean original extension project. Feature changes belong in the maintained modules and build scripts. The two recorded security amendments are verified against the original baseline hashes; see [recovery provenance](RECOVERY.md). Retain geographic data attribution and licence files. All executable code must remain packaged locally.

111 automated tests passed for the 1.2.5 submission. User previews and removal were tested, but complete live replacement after the latest full-slot fix remains unverified. Tests are not evidence that an in-game purchase completed.

[Changelog](CHANGELOG.md) · [Privacy](store/PRIVACY.md) · [Submission receipt](store/SUBMISSION-1.2.5.md)

Developer: MartyBlyth. Helper: Conroy1988.
