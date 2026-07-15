# Visual Documentation Capture Plan

The public documentation gallery must use real Toolkit captures. Generated mock MissionChief screens must not be presented as operational evidence.

## Capture standards

- Use the latest verified Toolkit release.
- Use the default Map Command theme for baseline captures.
- Redact player names, alliance chat, coordinates that identify private locations, account balances where sensitive, and personal browser information.
- Keep the MissionChief map and Toolkit controls readable at normal browser zoom.
- Prefer PNG for static captures and MP4/WebM source plus an optimised GIF fallback for short demonstrations.
- Do not include copyrighted music or private Discord content.

## Required static captures

| File | Mode | Subject |
|---|---|---|
| `desktop-map-command-overview.png` | Desktop | Full Toolkit dock and shortcut bar |
| `desktop-mission-age-watch.png` | Desktop | Mission Age Watch with multiple states |
| `desktop-critical-view.png` | Desktop | Critical View and Mission Inspector |
| `desktop-coverage-heat-map.png` | Desktop | Coverage Heat Map on an operational area |
| `desktop-smart-bookmarks.png` | Desktop | Compact bookmark labels and full-name preview |
| `desktop-vehicle-code-status.png` | Desktop | Vehicle code counts including Out of Service |
| `tablet-overview.png` | Tablet | Landscape layout fitted to available map space |
| `ios-overview.png` | iOS Mobile | Safari/Tampermonkey mobile-safe controls |
| `theme-map-command.png` | Desktop | Default theme |
| `theme-cyberpunk.png` | Desktop | Cyberpunk theme |
| `theme-fallout.png` | Desktop | Fallout 4 theme |
| `theme-umbrella.png` | Desktop | Umbrella theme |
| `theme-factorio.png` | Desktop | Factorio theme |

## Required short demonstrations

| File | Maximum duration | Workflow |
|---|---:|---|
| `mission-age-watch-demo.webm` | 20 s | Open, refresh, zoom and inspect a mission |
| `coverage-heat-map-demo.webm` | 15 s | Enable, inspect and disable coverage |
| `smart-bookmarks-demo.webm` | 15 s | Generated label, tooltip/long press and manual override |
| `critical-view-demo.webm` | 20 s | Open critical workflow and Mission Inspector |
| `payout-presentation-demo.webm` | 20 s | Completion banner, counter and history |
| `responsive-modes-demo.webm` | 20 s | Desktop, Tablet and iOS layout comparison |

## File locations

Store approved sources under:

```text
docs/media/screenshots/
docs/media/demos/
```

The Pages generator should reference only reviewed files committed to those locations. Keep raw editing projects outside the public repository.

## Review checklist

- [ ] Current Toolkit version visible or recorded in metadata
- [ ] No personal or alliance-sensitive information visible
- [ ] Theme and operating mode correctly named
- [ ] Text remains readable at documentation-page width
- [ ] Motion capture has no long idle section
- [ ] File size is reasonable for GitHub Pages
- [ ] Alt text and caption prepared
- [ ] Capture added to `docs/site-data.json`
- [ ] Documentation and asset-health checks pass
