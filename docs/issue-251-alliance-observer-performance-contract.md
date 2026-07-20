# Issue #251 — Alliance Buildings early observer performance contract

The early Alliance Buildings watcher exists to detect relevant map, table and layout elements being added to or removed from the live document. Its callback bases every scheduling decision on `addedNodes` and `removedNodes`.

The watcher therefore observes `childList: true` with `subtree: true` and does not request attribute-only mutation records. Navigation listeners, relevant-element selectors, early styling, Leaflet suppression guards, context detection and map repair remain unchanged.

This is a workload reduction rather than a feature change: presentation-attribute updates that could not satisfy the callback are no longer delivered to this document-wide observer.
