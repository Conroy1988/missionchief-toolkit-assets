# Toolkit repeated runtime stress audit

- **Status:** `passed`
- **Toolkit version:** `8.3.1`
- **Source SHA-256:** `363c6fa8f742840d71a65187c4b2f5b60fcffda519d63f2416c488cd86ca8089`
- **Discovery authority:** `.github/scripts/run_userscript_preflight.sh`
- **Discovered runtime contracts:** 10
- **Explicit heavier contracts:** 1
- **Repeated executions:** 96
- **Total elapsed:** 15.98 seconds
- **Per-run ceiling:** 45 seconds
- **Peak RSS ceiling:** 700,000 KiB

| Runtime contract | Repeats | Median | Maximum | Median RSS | Maximum RSS |
|---|---:|---:|---:|---:|---:|
| `.github/scripts/test_transport_sweep_runtime.js` | 8 | 0.03s | 0.03s | 49,334 KiB | 49,772 KiB |
| `.github/scripts/test_issue523_transport_sweep_progress_runtime.js` | 8 | 0.03s | 0.03s | 49,268 KiB | 49,340 KiB |
| `.github/scripts/test_issue527_transport_sweep_skipped_patients_runtime.js` | 8 | 0.03s | 0.03s | 49,292 KiB | 49,332 KiB |
| `.github/scripts/test_issue530_transport_sweep_discharge_confirmation_runtime.js` | 8 | 0.03s | 0.03s | 49,288 KiB | 49,336 KiB |
| `.github/scripts/test_issue565_transport_sweep_no_reward_runtime.mjs` | 8 | 0.42s | 0.45s | 116,214 KiB | 116,680 KiB |
| `.github/scripts/test_issue515_launcher_runtime.js` | 8 | 0.03s | 0.03s | 49,318 KiB | 49,408 KiB |
| `.github/scripts/test_issue517_incident_command_wire_runtime.js` | 8 | 0.03s | 0.03s | 49,330 KiB | 49,340 KiB |
| `.github/scripts/test_issue564_incident_feed_attended_runtime.js` | 8 | 0.04s | 0.04s | 51,268 KiB | 51,324 KiB |
| `.github/scripts/test_issue553_alliance_member_manager_menu_runtime.js` | 8 | 0.03s | 0.03s | 49,262 KiB | 49,340 KiB |
| `.github/scripts/test_issue553_alliance_member_manager_page_runtime.js` | 8 | 0.03s | 0.03s | 49,302 KiB | 49,736 KiB |
| `.github/scripts/test_ui_mount_integration.mjs` | 16 | 0.61s | 0.61s | 127,652 KiB | 129,288 KiB |

## Failures

- None.
