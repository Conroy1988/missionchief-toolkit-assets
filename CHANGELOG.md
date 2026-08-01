# Changelog

## [10.2.7] - 2026-08-01

### Desktop command dock redesigned as a wide, compact responsive grid

- Replaces the tall, narrow single-column Desktop command layout with a responsive multi-column grid that uses substantially more of the visible map width without resizing or displacing MissionChief.
- Arranges Visibility, Intelligence, Dashboard and Performance command groups as a four-group grid on wide Desktop, reducing to three, two or one columns as the available map workspace narrows or browser zoom increases.
- Adopts the proven Tablet control treatment at Desktop density: individual buttons remain compact, readable and visually clear with full labels and unambiguous ON/OFF status.
- Derives column count from the actual visible Leaflet map workspace width so wide Desktop, medium/narrow windows and 80–200% browser zoom all remain usable without horizontal scrolling or page overflow.
- Constrains dock width to the available map workspace and falls back to internal vertical overflow only when the map workspace height is genuinely insufficient.
- Keeps the launcher button and version indicator reachable at all times regardless of column layout or scroll position.
- Preserves the v10.2.6 Major Incident Wire reservation, all four dock positions, auto-hide, Compact Dock mode, saved nudges and position preferences.
- Leaves Tablet, iPad and iOS/mobile geometry, behaviour and column layout completely unchanged.
- Adds no timer, observer, listener or network request beyond the resize observer already established in v10.2.6.
- Adds static, geometry and rendered-DOM regressions covering wide/medium/narrow Desktop column counts, Bond 007 screenshot geometry, 80–200% zoom at all four dock positions, Incident Wire visible/hidden, pins present/absent, auto-hide and command-bar close/open, Tablet and mobile geometry unchanged, and source/distribution parity.

## [10.2.6] - 2026-08-01

### Critical Desktop command-dock containment

- Keeps the expanded Desktop launcher and command dock inside the actually visible Leaflet map workspace instead of allowing stacked groups to escape above the page.
- Reserves the Major Incident Wire and other verified top-of-map obstructions, along with safe map margins and any off-viewport map edge.
- Pins the launcher in reach while the command groups and screen pins gain bounded internal scrolling only when the available map height requires it.
- Recalculates through the existing fit timer and Desktop resize observer after viewport zoom or resize, map geometry changes, feed placement or removal, layout changes and dock open or close.
- Supports all four Desktop dock positions and clears every Desktop sizing override when switching to Tablet, iOS or a non-map route.
- Adds static, geometry and rendered-DOM regressions reproducing the reported 007-theme layout and 80–200% browser-zoom cases without adding a timer, listener, network request or observer.

## [10.2.5] - 2026-08-01

### Map-only command shell and live update alert

- Restricts the global Toolkit launcher, dock, command menu, overlays and map keyboard ownership to the positively identified top-level MissionChief map on the canonical root route.
- Retires the document/body fallback that allowed standalone mission, credits, alliance, building and vehicle pages to mount the map command shell.
- Tears down stale map UI on history navigation and remounts it exactly once when returning to the canonical map, without changing saved command-bar preferences or page-specific enhancements.
- Checks the guarded GitHub stable-release manifest every 60 seconds while the canonical map context remains active, using semantic numeric version comparison and one non-overlapping request/timer lifecycle.
- Makes both `LATEST` and `UPDATE` open the official TKB Toolkit product page; a newer release adds a conspicuous full-button neon pulse with a strong static reduced-motion halo.
- Preserves the last verified state during transient failures, keeps an unsuccessful first check neutral, ignores superseded responses and aborts pending update work when map ownership ends.
- Adds deterministic route, history, mission-window, non-map, persisted-state, shortcut, device-layout, cadence, destination, failure, overlap, teardown, theme-independent glow and accessibility regressions for Issues #638 and #639.

## [10.2.4] - 2026-08-01

### Alliance Member Manager page isolation

- Restricts Alliance Member Manager to a positively identified active Members or Mitglieder view instead of trusting the shared alliance navigation link.
- Prevents Applications and every other alliance page from mounting the manager even when they contain profile rows or a stale member-route URL.
- Removes an already-mounted manager immediately when in-page alliance navigation replaces the Members view, restoring the native table before returning to passive