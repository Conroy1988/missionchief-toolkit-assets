# Issue #553 — Alliance Member Manager restoration

Toolkit v8.1.2 restores the Alliance Member Manager after the published v8.1.1 scope-error rollback.

The restoration uses the verified v8.1.0 feature tree as its source, preserves the v8.1.1 release record for auditability, and adds an executable regression for the live Tools-menu structure where the Alliance Map Blocker card has no feature-specific `data-*` attribute.

The menu lookup remains attribute-first and falls back only to a `.mcms-toggle-btn` whose trimmed `.mcms-label` text is exactly `Alliance Map Blocker`. The actual member-list panel remains route-gated and disabled by default.
