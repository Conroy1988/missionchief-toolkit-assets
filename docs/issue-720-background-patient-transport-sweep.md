# Background-first Patient Transport Sweep

Toolkit v10.9.2 adds a faster processing mode to **Toolkit → Administration → Patient Transport Sweep**. It keeps the existing Scan, confirmation, maximum-per-run, pacing and Stop controls.

## How it works

1. The sweep refreshes the signed-in player's vehicle API and builds an authoritative personal-vehicle exclusion set.
2. It fetches the eligible alliance mission and identifies non-personal FMS 5 patient vehicles from MissionChief's current HTML.
3. For each candidate, it fetches that exact vehicle page without opening a lightbox.
4. It proceeds in the background only when that page exposes exactly one enabled **Cancel Transport** link on the current MissionChief origin with the path `/vehicles/{same vehicle}/patient/{numeric patient}` and no query string or fragment.
5. It sends that exact native GET request once and counts the patient only when the returned MissionChief document contains fresh release-confirmation evidence.

No mission or vehicle lightbox is opened for a background-confirmed release.

## Fail-safe behaviour

- A missing, disabled, malformed, external, wrong-vehicle or conflicting action is rejected before any release request.
- A vehicle page that exposes only **Discharge patient** is not inferred into a background request; the sweep switches to the proven visible native workflow.
- If a background release request is sent but its response cannot be verified, the result is recorded as ambiguous and is never retried through the background or visible path.
- Verified personal vehicle IDs are rejected before the vehicle page is requested.
- Ownership verification failure cancels the complete run.
- Processing remains sequential and respects the configured delay and maximum.
- Prisoner transports remain outside the feature.

## Operator controls

**Background first (faster)** is enabled by default for existing and new installations. Choose **Visible native only** in Processing mode to retain the previous lightbox-only behaviour.

The feature remains manual: Scan and Start Sweep are deliberate actions, Start requires confirmation, and no observer, poller or interval was added.
