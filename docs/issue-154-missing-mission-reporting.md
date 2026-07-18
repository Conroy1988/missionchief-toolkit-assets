# Issue #154 — Missing Mission Requirements Reporting

## Runtime states

Every supported native MissionChief mission window must display one Toolkit Mission Requirements surface:

- a bounded loading state while MissionChief requirement data may still arrive;
- the normal live requirements matrix when quantified requirements parse successfully;
- an explicit no-outstanding-requirements state when MissionChief exposes an empty native requirement source;
- `Unable to pull mission requirements` when the source is absent after the bounded wait, throws during parsing, or contains non-empty text that cannot be interpreted.

The fallback surface remains in MissionChief's normal document flow and automatically upgrades to the live matrix when a valid native source appears later.

## Report Mission

The failure and partially unresolved states expose a compact `Report Mission` control. It opens GitHub's standard new-issue composer with a pre-filled title, body and `Mission Info Missing` label. The player reviews and submits the report; the Toolkit does not contain a GitHub credential and does not submit issues silently.

The report may include mission ID, title, mission type ID, MissionChief pathname, Toolkit version, layout mode, viewport, platform summary, requirement-source metadata, bounded visible requirement text, selector counts and aggregated vehicle-type counts.

The report must exclude usernames, alliance identifiers, addresses, coordinates, chat content, cookies, CSRF/authentication data, API keys, webhook URLs, vehicle IDs and unrelated page HTML. The generated URL is bounded and the body is shortened when required. Control characters are removed through explicit character-code checks rather than a control-character regular-expression range.

## Validation

Fixtures cover absent, delayed, empty, unparseable and recovered requirement sources; report sanitisation; URL-size bounds; and single-panel ownership through fallback recovery.

The v4.15.4 candidate remains inside the unchanged static performance envelope at 1,899,013 source bytes and 30,979 lines. Observer, listener, timer, animation-frame and startup-hook counts remain unchanged; the required headroom was recovered through lexical formatting compaction outside strings, comments, regular expressions and template literals.
