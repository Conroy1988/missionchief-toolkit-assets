# Issue #565 — Patient Transport Sweep no-reward release path

Toolkit v8.2.5 recognises the real MissionChief multi-cell FMS 5 vehicle-row structure.

The FMS badge can occupy its own first table cell while the vehicle link and `Patient:` text are rendered in another cell. Patient discovery therefore locates the authoritative cell containing `Patient:` anywhere in the row instead of assuming the first cell contains both status and patient data.

The exact visible same-origin `Release patient (No reward)` control remains required. Own vehicles remain excluded from the verified personal vehicle set. Row and top-alert control clones are deduplicated by vehicle ID, with the authoritative row control preferred when patient-count context is available.

Delayed mission rows, delayed controls, completed requests, repeated same-vehicle releases, cancellation, allowance, failed-request handling and the native MissionChief discharge fallback remain preserved. No persistent observer, interval, additional request site or Toolkit-managed timer is added.
