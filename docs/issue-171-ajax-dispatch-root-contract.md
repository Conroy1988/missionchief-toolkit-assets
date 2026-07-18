# Issue #171 — AJAX dispatch Mission Requirements root contract

Mission Requirements candidates discovered inside Available Units, vehicle tables, table sections, rows or cells must resolve upward to the enclosing active mission form/content or visible lightbox root.

The panel must never be inserted into `table`, `thead`, `tbody`, `tfoot`, `tr`, `td`, `th` or `colgroup`. Operational fallbacks insert before the top-level block containing the vehicle table.

Normal dispatch-button AJAX opening and standalone mission tabs use the same mission source and header placement. A subsequent scan re-homes any panel temporarily mounted by incomplete AJAX markup.
