# README media system

This directory contains the public visual assets used across the Toolkit repository and documentation.

## Current flagship suite

The `readme-v3-*` set is the active GitHub README system:

| Asset | Purpose |
|---|---|
| `readme-v3-command-system.svg` | Flagship command-centre hero joining incident, fleet, map, administration and finance. |
| `readme-v3-operational-picture.svg` | Multi-agency UK operational picture and end-to-end command flow. |
| `readme-v3-administration-command.svg` | Recruitment, academy courses and alliance transport administration. |
| `readme-v3-command-surfaces.svg` | One coherent Toolkit layer across desktop, tablet and phone. |
| `readme-v3-release-integrity.svg` | Canonical source, validation, publication and recovery chain. |

Each flagship asset is a self-contained 1600 × 700 SVG. The photographic scene is embedded as a compressed JPEG and all visible brand typography is deterministic SVG text, keeping the exact product name crisp and preventing generated lettering from entering the public artwork.

The scenes were created specifically for this repository. They are conceptual—not screenshots or depictions of a real emergency operation—and contain no people, personal likenesses, player information, private data, official logos, version numbers or readable fictional interface data.

## Historical suites

- `readme-v2-*` contains the previous 1600 × 900 command-plate system.
- `readme-hero-operations.webp`, `readme-field-command.webp` and `readme-control-room.webp` contain the original photographic suite.
- The SVG command-board assets are retained for historical and downstream-reference compatibility.

Do not remove a historical asset until repository search, GitHub Pages and release documentation confirm that nothing still references it.

## Asset rules

- Flagship README scenes must remain free of people and identifiable likenesses.
- Never include player names, alliance data, addresses, credentials, tokens or live operational data.
- Do not bake version numbers, publication dates or release-state claims into artwork.
- All visible words must be composed deterministically after scene generation.
- Preserve the 1600 × 700 flagship canvas and edge-safe title geometry.
- Render every SVG at full size and at GitHub's approximate 838 px article width before publication.
- Keep each self-contained asset below 2 MB and the full active suite proportionate to the page.
- Provide descriptive alt text at every Markdown usage point.

## Capture set

For product screenshots and release evidence, capture each affected interface in:

- Desktop mode
- Tablet mode
- iOS Mobile Mode
- Both relevant base-game colour states where appearance changes
- Reduced-motion or Economy Mode where behaviour or geometry differs

Before capture, use fictitious data and inspect the frame for private information. A clean asset is part of the release contract, not a post-release tidy-up.
