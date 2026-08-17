# Issue #716 — Procurement Brain and Operational Timeline

Toolkit v10.9.1 provides two read-only planning views in the existing Operational Pressure Board. Open **Toolkit → Missions → Procurement Brain** or **Operational Timeline**, use the Command Palette, or open the board with <kbd>B</kbd> and change tabs.

## Mission scope and logging

The board always monitors personal missions. **Alliance Missions** is a persistent opt-in switch and is off by default; turning it on adds joined Alliance missions to Live Pressure, Procurement Brain and the visible/exported Timeline scope.

**Timeline Logging** is also persistent and off by default. While it is off, the Toolkit returns before scanning mission snapshots for history, so no Timeline event processing is added to normal gameplay. Turning it on establishes a quiet baseline and records only later meaningful changes. Turning it off stops new logging without deleting retained history.

## Procurement Brain

Procurement Brain combines the current Operational Pressure model with recent Timeline evidence. It ranks vehicle acquisition or repositioning, reserve-depth, personnel recruitment and training-review signals. Each recommendation shows its score, priority, confidence and evidence instead of presenting an unexplained answer.

Live confirmed shortfalls have the strongest weight. Fleet conflicts, location-unverified capacity, exhausted reserve, repeated requirement events, distinct affected missions and recency then add evidence. One weak isolated historical signal is withheld; a current operational risk can appear immediately. The operator can compare **24H**, **7D** and **30D** learning windows.

Recommendations are advisory. The view never purchases a vehicle, changes a station, selects a unit or dispatches a response. Vehicle recommendations can open the existing MissionChief UK Intelligence dossier for verified unit, crew and training context.

## Operational Timeline

After Timeline Logging is enabled, the first successful mission scan establishes a quiet baseline. Later meaningful changes create events for:

- a newly observed mission;
- response commitment, arrival or release;
- exposed vehicle or personnel requirement changes;
- patient or prisoner demand changes;
- a configured no-progress stall and subsequent recovery; and
- a mission that remains absent from two consecutive scans and is recorded as completed.

Transient marker loss is not treated as immediate completion. Repeated identical signals are deduplicated. The Timeline reuses the Toolkit's existing mission-snapshot lifecycle and adds no observer, poller, interval or background request.

Operators can filter by mission, response, resource or completion events; search by mission, summary or requirement; focus a mission that is still live; and export the retained evidence as JSON.

## Local storage and clearing

Timeline data remains in the browser through the existing userscript/local-storage adapters. Records are normalised on read and write, reject malformed or oversized payloads, expire after 30 days and are capped at 1,500 entries. Rendering is separately capped at the newest 120 matching events.

**Clear History** requires explicit confirmation and removes the full Timeline plus Procurement Brain's historical learning evidence. Current live pressure can still produce a recommendation immediately after clearing.

## Scoring contract

The deterministic score combines weighted recent demand, signal count, distinct missions, live shortfall, location uncertainty, simultaneous-demand conflict and reserve exhaustion. Results sort by score, then live shortfall, recency and name. The model consumes only state already exposed to the Toolkit and does not infer a MissionChief purchase action or permission.
