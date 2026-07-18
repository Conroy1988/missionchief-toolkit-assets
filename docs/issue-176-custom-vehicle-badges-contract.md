# Issue #176 — Custom Vehicle Badges contract

Available Units retains MissionChief's native vehicle label and appends one compact Own Vehicle Category badge when `/api/vehicles` provides a non-empty `vehicle_type_caption`. Vehicles without a custom category are unchanged.

Rows are resolved by stable vehicle ID through the same identity helper used by the Mission Requirements Matrix. The shared classification cache exposes category, base vehicle type and `ignore_aao` lock state without altering selection or dispatch behaviour.

The feature observes normal AJAX dispatch windows, standalone mission tabs and accessible LSSM-modified document roots. Repeated scans are idempotent, do not reinsert an already correctly hosted badge, and replacement rows receive the badge automatically.

The menu toggle is named **Custom Vehicle Badges** and is enabled by default. Its description is: **Show custom vehicle categories in available vehicles list.**
