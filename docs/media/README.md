# Documentation media programme

This directory is reserved for reviewed screenshots and short demonstrations used by GitHub, the TKB Website and the public documentation site.

## Repository landing visuals

The root README uses four original, photoreal editorial images:

- `readme-v2-command-centre.webp` — rain-lit British command centre and coordinated city response
- `readme-v2-operational-picture.webp` — elevated UK road and rail multi-agency operation
- `readme-v2-command-post.webp` — coherent Toolkit workspace across desktop, tablet and mobile
- `readme-v2-release-integrity.webp` — secure release validation and recovery environment

All four images are 1600 × 900 WebP assets. The photoreal scenes were generated specifically for the Toolkit and do not contain private account data, third-party logos or embedded version information. A deterministic image-composition pass adds the exact MissionChief Map Command Toolkit command plate, signal colours and product copy; this prevents generated lettering errors and keeps branding aligned at every viewport width.

The previous `readme-hero-operations.webp`, `readme-field-command.webp` and `readme-control-room.webp` assets remain available for historical documentation references.

## Required capture set

- `map-before-after`
- `theme-map-command`
- `theme-cyberpunk`
- `theme-fallout`
- `theme-umbrella`
- `theme-factorio`
- `mission-age-watch`
- `coverage-heat-map`
- `smart-bookmark-labels`
- `payout-presentations`
- `tablet-mode`
- `ios-mobile-mode`
- `critical-view`
- `mission-inspector`

## Capture rules

- Remove player names, alliance chat and other private account information.
- Use representative missions rather than sensitive real-world information.
- Capture the same feature at consistent map scale where comparisons matter.
- Prefer WebP for static captures and MP4/WebM for demonstrations; use GIF only when platform compatibility requires it.
- Keep each static image below 2 MB and each short demonstration below 8 MB.
- Do not rename or replace compatibility-critical assets already referenced by installed Toolkit releases.
- Add new documentation media under `docs/media/` and update `docs/site-data.json` through a reviewed pull request.

The first Pages release uses live CSS-rendered feature and theme previews so the site is visually complete before account-safe captures are available.
