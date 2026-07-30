# Issue #593 — Toolkit v8.3.2 controlled Chrome CSS baseline

This directory will contain measurement-only controlled Chrome evidence for parent Issues #247 and #254.

The evidence is generated from exact Toolkit v8.3.2 without modifying the production userscript, distribution files, version or release state. It measures stylesheet insertion, forced style/layout, long tasks, layout shifts and the existing guarded-root-write contract across Desktop, Tablet and iOS-sized viewports.

Controlled synthetic runner timings are hardware-specific diagnostics. They are not authenticated MissionChief runtime evidence and do not by themselves authorise CSS modularisation.
