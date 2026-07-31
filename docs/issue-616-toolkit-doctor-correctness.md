# Issue #616 — Toolkit Doctor diagnostic correctness

## Report

Toolkit v9.3.1 could continue showing `Responsive layout` and `Overlay safety` warnings on Tablet after **Repair UI**. The warnings were produced by diagnostic classification rather than a Quick Jump or settings fault.

## Root cause

Doctor mounted its own modal before measuring the background Settings panel. It also treated every visible fixed or sticky descendant above `z-index: 1000` as an independent competitor, even when the element was normal MissionChief navigation, nested inside an already-counted overlay or owned by the Toolkit itself.

## v9.3.2 correction

- Doctor closes its previous diagnostic modal and snapshots the live operational interface before opening the progress view.
- Responsive checks independently verify the device-layout attribute, density attribute and visible open Settings-panel bounds.
- The safe report names the exact failed responsive component without exposing viewport coordinates.
- Overlay detection excludes all Toolkit-owned controls, panels, HUDs, Help, full-screen recovery and operational boards.
- A foreign fixed or sticky element must visibly intersect a Toolkit surface by a meaningful area before it can warn.
- Descendants of an already-counted foreign overlay root are consolidated into the same conflict.
- **Repair UI** refreshes visual-viewport variables and Tablet presentation state before repositioning and rerunning Doctor.

## Safety boundary

The patch adds no observer, poller, timer, background request or automatic action. It does not suppress a real foreign overlay that intersects Toolkit controls. Copied Doctor reports continue to exclude webhooks, tokens, player identity, balances, coordinates and operational data.

## Verification

- Static contract locks the exact diagnostics, ownership exclusions, privacy boundary and zero-scheduler behaviour.
- Rendered runtime cases cover Tablet attribute health, density mismatch, out-of-bounds Settings geometry, harmless MissionChief navigation, Toolkit-owned panels, nested foreign overlays and genuine collisions.
- Canonical and distribution userscript copies remain byte-identical.
