# Issue #171 — AJAX dispatch Mission Requirements root contract

Mission Requirements candidates discovered inside Available Units, vehicle tables, table sections, rows or cells must resolve upward to the enclosing active mission form/content or visible lightbox root.

The panel must never be inserted into `table`, `thead`, `tbody`, `tfoot`, `tr`, `td`, `th` or `colgroup`. Operational fallbacks insert before the top-level block containing the vehicle table.

Normal dispatch-button AJAX opening and standalone mission tabs use the same mission source and header placement. If incomplete AJAX markup temporarily separates the panel from its canonical source host, the next scan restores the canonical panel beneath the mission header.
