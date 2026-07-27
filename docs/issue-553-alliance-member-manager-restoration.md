# Issue #553 — Alliance Member Manager menu restoration

Toolkit v8.1.2 restored the Alliance Member Manager runtime but did not reliably render its Tools control in the production panel. The remaining defect is tracked for v8.1.3.

The production card cannot be identified safely through a hard-coded `.mcms-toggle-btn` class, and a one-shot microtask can run before or be overwritten by the Toolkit's normal Tools render. The v8.1.3 correction must:

- resolve the live **Alliance Map Blocker** through its exact rendered `.mcms-label`, independent of the card's CSS class;
- clone the real rendered card structure so the new control inherits the canonical UI markup and styling;
- strip the blocker card's original action/data attributes before assigning Alliance Member Manager ownership;
- bind a panel-scoped, child-list-only observer so a normal Tools re-render restores the control deterministically;
- coalesce render reconciliation and use only bounded animation-frame retries;
- disconnect/rebind observation when the Toolkit panel instance changes;
- add executable live-DOM coverage and release as Toolkit v8.1.3.

This document supersedes the v8.1.2 menu-evidence claim only; the Alliance Member Manager remains an owner-confirmed Toolkit feature.