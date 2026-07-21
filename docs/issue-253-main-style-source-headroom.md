# Issue #253 — main stylesheet source headroom

Toolkit v4.20.21 creates maintainable source headroom without changing stylesheet behavior.

## Bounded change

Only standalone source formatting inside the existing `installMainStyles` template is removed: blank physical lines, full-line CSS comment blocks and 15 newlines immediately before full-line closing braces. The canonical CSS content is identical before and after. The change does not group selectors, consolidate declarations, reorder rules, alter interpolation expressions, defer installation, or change specificity and cascade order.

CSS comments removed by this change occupy complete lines and contain no interpolation. They are parser-ignored documentation rather than selectors or declarations. The 15 joined lines contain only `}`; CSS does not require whitespace immediately before a closing brace.

No observer, scheduler, network, state, storage or lifecycle code is changed.

## Deterministic proof

`.github/fixtures/main-style-source-headroom.json` records:

- original and candidate source line counts;
- exact recovered line count by blank-line, standalone-comment and closing-brace-join category;
- original and candidate template line counts;
- SHA-256 of the canonical CSS content;
- SHA-256 of the exact candidate stylesheet template.

`test_main_style_source_headroom.py` is executed by canonical validation and the shared userscript preflight. It rejects returned removable formatting, altered CSS source, inconsistent line arithmetic, a recovery below 500 lines or version drift.

Source-line validation uses the same convention as `deep_performance_audit.mjs`: a terminal newline does not create an additional empty source line. This keeps the permanent contract aligned with the repository's established 31,171-line candidate measurement.

## Excluded work

This change does not implement the higher-risk stylesheet modularisation work in Issues #63 or #254. Style delivery, selector grouping, visual themes, first paint and responsive behavior remain structurally unchanged.

## Rollback

Revert the single Issue #253 implementation commit. The change introduces no persistent data migration or external dependency.
