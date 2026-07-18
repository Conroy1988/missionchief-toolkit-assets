# Issue #169 — Mission Requirements lightbox context and placement contract

The matrix resolves one active mission root per document. Native requirement text, selected units, responding units, on-site units, mission identity and catalogue lookup are scoped to that root. Visible AJAX missions outrank hidden records.

The panel is inserted immediately before native `#missing_text`. While that source is delayed, its anchor is placed after the mission address/title. Incident notes, response tables and dispatch footers are not valid preferred hosts.

Mission and catalogue descriptor changes invalidate record-local catalogue data and stale asynchronous results.

Desktop uses a left-aligned 940px standard width, expands to 1140px for longer labels, and uses the full available root width only for exceptional content. Every mode remains capped at 100% of its mission root, so long text can expand the matrix without creating horizontal page overflow. Tablet and iOS use the available width. The same placement and width contract applies across all seven interface systems.
