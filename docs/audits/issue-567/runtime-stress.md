# Toolkit repeated runtime stress audit

- **Status:** `passed`
- **Repeated executions:** 88
- **Total elapsed:** 14.11 seconds
- **Per-run ceiling:** 45 seconds
- **Peak RSS ceiling:** 700,000 KiB

| Runtime contract | Repeats | Median | Maximum | Median RSS | Maximum RSS |
|---|---:|---:|---:|---:|---:|
| `.github/scripts/test_transport_sweep_runtime.js` | 8 | 0.03s | 0.04s | 50,580 KiB | 51,064 KiB |
| `.github/scripts/test_issue523_transport_sweep_progress_runtime.js` | 8 | 0.03s | 0.04s | 50,618 KiB | 50,644 KiB |
| `.github/scripts/test_issue527_transport_sweep_skipped_patients_runtime.js` | 8 | 0.03s | 0.03s | 50,580 KiB | 50,636 KiB |
| `.github/scripts/test_issue530_transport_sweep_discharge_confirmation_runtime.js` | 8 | 0.03s | 0.03s | 50,578 KiB | 51,076 KiB |
| `.github/scripts/test_issue565_transport_sweep_no_reward_runtime.mjs` | 8 | 0.40s | 0.40s | 122,478 KiB | 124,868 KiB |
| `.github/scripts/test_issue515_launcher_runtime.js` | 8 | 0.03s | 0.03s | 50,588 KiB | 51,072 KiB |
| `.github/scripts/test_issue517_incident_command_wire_runtime.js` | 8 | 0.03s | 0.04s | 50,606 KiB | 50,644 KiB |
| `.github/scripts/test_issue553_alliance_member_manager_menu_runtime.js` | 8 | 0.03s | 0.04s | 50,576 KiB | 50,640 KiB |
| `.github/scripts/test_issue553_alliance_member_manager_page_runtime.js` | 8 | 0.03s | 0.03s | 50,442 KiB | 50,484 KiB |
| `.github/scripts/test_ui_mount_integration.mjs` | 16 | 0.52s | 0.53s | 127,596 KiB | 128,748 KiB |

## Failures

- None.
