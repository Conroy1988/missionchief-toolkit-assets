# Issue 279 — unchanged root-attribute write suppression

Toolkit v4.20.18 preserves the complete `applyRootAttributes()` output while avoiding redundant `setAttribute()` calls whose current string value is already correct.

## Safety boundary

- All 22 root attributes remain present and retain their original ordering.
- Device, tablet, mobile and viewport calculations still execute on every call.
- No root node, value snapshot or state cache is retained.
- No observer, timer, animation frame, event listener or network path is added.
- External attribute removal or alteration is repaired on the next invocation.

## Deterministic evidence

The contract extracts the real helper and `applyRootAttributes()` from the canonical userscript and proves 22 initial writes, zero unchanged-repeat writes, selective state updates, external repair and ordered layout/orientation changes.
