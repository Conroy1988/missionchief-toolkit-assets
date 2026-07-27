# Issue #553 — Alliance Member Manager page-mount correction

Toolkit v8.1.3 renders the Alliance Member Manager toggle directly in the canonical Tools panel, but the enabled manager does not mount on the live UK alliance-members page when LSSM Redesign is active.

The live page uses LSSM's asynchronous `/verband/mitglieder/{allianceId}` Vue view. Its member table is created after `DOMContentLoaded`, activity icons use `user_<state>.png` without the native `online_icon` class, and the total page count is presented in summary text such as `of 568 pages` rather than native pagination markup.

Toolkit v8.1.4 must therefore use a bounded enabled-route installation retry, recognise the rendered LSSM table/activity/page-count contract, mount outside the Vue-controlled table subtree, and suppress itself only when another extension provides an actually equivalent role/activity/load-all manager. No recurring disabled work or new observer is permitted.