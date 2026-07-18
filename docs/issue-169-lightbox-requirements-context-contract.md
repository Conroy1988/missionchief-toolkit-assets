# Issue #169 — Mission Requirements lightbox context and placement contract

The matrix resolves one active mission root per document. Native requirement text, selected units, responding units, on-site units, mission identity and catalogue lookup are scoped to that root. Visible AJAX missions outrank hidden records.

The panel is inserted immediately before native `#missing_text`. While that source is delayed, its anchor is placed after the mission address/title. Incident notes, response tables and dispatch footers are not valid preferred hosts.

Mission and catalogue descriptor changes invalidate record-local catalogue data and stale asynchronous results.

Desktop uses 940px standard width, 1140px for longer labels and the full available root width only for exceptional content. Tablet and iOS use the available width, always capped at 100%.
