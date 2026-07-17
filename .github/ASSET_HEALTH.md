# Public asset-health monitoring

The Toolkit depends on public media files and distribution endpoints that can fail independently of the userscript source. The asset-health monitor validates those dependencies before they become user-facing failures.

## Coverage

The checker discovers and verifies:

- raw GitHub image and audio URLs referenced by the canonical userscript and repository configuration;
- media files committed to this repository, using their stable `raw.githubusercontent.com/.../main/...` paths;
- the latest GitHub Release userscript asset;
- the Greasy Fork install userscript;
- the Greasy Fork metadata endpoint;
- the Greasy Fork project page as a non-blocking availability signal.

For repository media, it validates local file size, file signatures, public HTTP status, content type and public size parity. Git LFS pointer files are rejected.

For public userscripts, the GitHub Release asset remains the full-file SHA-256 authority and must match `status/release-dashboard.json -> latestRelease`. Greasy Fork must expose the same `@version` and the same byte-identical executable body after the userscript metadata block; its service-generated metadata envelope may differ without weakening code-integrity verification.

## Execution

`.github/workflows/asset-health-monitor.yml` runs:

- statically on relevant pull requests;
- live after relevant changes reach `main`;
- every six hours on a staggered schedule;
- manually through `workflow_dispatch`.

Pull-request checks do not contact public services. They validate URL discovery, repository paths, media signatures and checker policy. Scheduled, manual and `main` runs perform the live network checks.

Every run uploads JSON and Markdown diagnostics for 30 days.

## Incident handling

A live failure is reconciled against one persistent issue titled:

`[Asset Health] Toolkit public assets unavailable`

The workflow creates or reopens that issue and posts one alert to the development Discord channel. Repeated checks update the same issue without sending duplicate Discord alerts. When all required checks recover, the workflow closes the incident and sends one recovery notification.

Optional endpoints such as the Greasy Fork HTML page may return automated-request blocking responses. Those are recorded as warnings and do not open an incident.

## Policy changes

Thresholds, content types, monitored hosts and explicit endpoints are controlled by `.github/asset-health-policy.json`.

Change the policy only when the asset contract genuinely changes. Do not weaken a failing check merely to make CI green; first confirm whether the public path, release hash, file type or endpoint is wrong.

## Repository audio and compatibility-alias contract

The canonical payout-audio inventory is declared in `.github/asset-compatibility-aliases.json`.

The permanent validation enforces that:

- every canonical payout-audio path exists and is referenced by the canonical userscript;
- current source code does not reference a root-level legacy alias;
- every declared root alias exists and is byte-identical to its canonical target;
- only declared legacy/canonical pairs may contain duplicate audio bytes;
- undeclared `.mp3`, `.wav` or `.ogg` files fail as orphaned media;
- missing aliases, missing canonical targets, hash mismatches and unexpected source paths fail validation.

The seven root-level MP3 files remain visible solely because older installed and published Toolkit versions load those exact raw GitHub URLs. New development must use the structured canonical paths under `themes/` or `assets/audio/payout-presets/`.
