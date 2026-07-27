# Issue #553 — Alliance Member Manager page-mount correction

Toolkit v8.1.4 mounts the enabled manager after an external redesigned alliance-members view asynchronously creates its table.

The implementation recognises the rendered activity icons and textual total-page summary, mounts outside the framework-controlled table subtree, narrows duplicate suppression to an actually equivalent role/activity/load-all manager, and uses one bounded enabled-route retry site with no observer, interval or recurring disabled work.
