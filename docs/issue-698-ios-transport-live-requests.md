# Issue #698 — iOS Patient Transport Sweep live-request hydration

Toolkit v10.6.3 repairs the post-discovery failure observed on a physical iPhone after v10.6.2 found 80 current patient missions but returned an empty `0/0` queue. The mobile hydrator no longer requires MissionChief's desktop-oriented `#missing_text` block to identify an active patient transport.

The manual scan now reads MissionChief's real mission-page transport structure: an active transport request must point to a positively identified FMS 5 ambulance or patient vehicle on the same alliance mission. A vehicle merely being present is not enough. Known personal vehicle IDs are excluded, prisoner and missing-resource-only pages still fail closed, and the sweep continues to require MissionChief's visible native discharge or cancel control before it acts.

Mission pages are requested through the existing same-origin fetch path with a 6.5-second abort deadline. Normal full-page HTML is attempted before the XHR fallback because that is the stable iOS response. The panel reports progress every ten checked missions and always records a terminal scan result, so a completed zero-result scan can no longer look like a silent stall.

The real-mobile regression contains no `missionMarkerAdd` data and now includes a mission page with no `#missing_text`. It proves that actual FMS 5 patient request controls recover the same eligible missions as desktop markers, while patient missions without an active request remain excluded.
