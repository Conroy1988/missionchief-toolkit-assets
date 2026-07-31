#!/usr/bin/env bash
set -euo pipefail
ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"; cd "$ROOT"
MODE="${1:---all}"; SOURCE="src/MissionChief_Map_Command_Toolkit.user.js"; DIST_JS="dist/MissionChief_Map_Command_Toolkit.user.js"; DIST_TXT="dist/MissionChief_Map_Command_Toolkit.txt"
if [[ "$MODE" == "--all" ]]; then python3 .github/scripts/validate_userscript.py; fi
node --check "$SOURCE"; cmp --silent "$DIST_JS" "$DIST_TXT"
for contract in .github/scripts/test_financial_ledger_contract.py .github/scripts/test_financial_overview_contract.py .github/scripts/test_financial_discord_complexity_contract.py .github/scripts/test_financial_discord_image_layout_contract.py .github/scripts/test_mission_marker_ingestion_contract.py .github/scripts/test_boot_lifecycle_contract.py .github/scripts/test_settings_ui_contract.py .github/scripts/test_root_attribute_write_suppression_contract.py .github/scripts/test_ios_safari_usability_contract.py .github/scripts/test_main_style_source_headroom.py .github/scripts/test_desktop_panel_layout_contract.py .github/scripts/test_section_navigation_contract.py .github/scripts/test_mission_value_contract.py .github/scripts/test_issue515_launcher_restoration.py .github/scripts/test_issue517_incident_command_wire.py .github/scripts/test_issue564_incident_feed_attended.py .github/scripts/test_v7_retirement.py .github/scripts/test_mission_age_retention.py .github/scripts/test_transport_sweep_native_contract.py .github/scripts/test_issue523_transport_sweep_progress.py .github/scripts/test_issue527_transport_sweep_skipped_patients.py .github/scripts/test_issue530_transport_sweep_discharge_confirmation.py .github/scripts/test_issue565_transport_sweep_no_reward.py .github/scripts/test_issue537_godfather_css_activation.py .github/scripts/test_issue539_godfather_layout_audio.py .github/scripts/test_issue541_godfather_duration_position.py .github/scripts/test_issue536_alliance_building_visibility.py .github/scripts/test_alliance_member_manager_contract.py .github/scripts/test_issue601_operational_pressure_contract.py .github/scripts/test_issue606_pressure_vehicle_classification_contract.py .github/scripts/test_issue610_uk_knowledge_contract.py .github/scripts/test_issue612_command_experience_contract.py .github/scripts/test_issue614_quick_places_contract.py .github/scripts/test_ui_mount_policy.py; do PYTHONDONTWRITEBYTECODE=1 python3 "$contract"; done
python3 .github/scripts/test_release_pipeline_v4.py
python3 .github/scripts/test_consolidated_pr_gate.py
python3 .github/scripts/test_path_aware_blocking.py
python3 .github/scripts/test_issue588_v831_performance_baseline.py
python3 .github/scripts/test_issue255_unchanged_update_ui.py
python3 .github/scripts/test_issue255_update_ui_write_suppression.py
node .github/scripts/test_transport_sweep_runtime.js
node .github/scripts/test_issue523_transport_sweep_progress_runtime.js
node .github/scripts/test_issue527_transport_sweep_skipped_patients_runtime.js
node .github/scripts/test_issue530_transport_sweep_discharge_confirmation_runtime.js
node .github/scripts/test_issue565_transport_sweep_no_reward_runtime.mjs
node .github/scripts/test_issue515_launcher_runtime.js
node .github/scripts/test_issue517_incident_command_wire_runtime.js
node .github/scripts/test_issue564_incident_feed_attended_runtime.js
node .github/scripts/test_issue255_update_ui_write_suppression_runtime.mjs
node .github/scripts/test_issue597_command_interface_runtime.mjs
node .github/scripts/test_issue601_operational_pressure_runtime.mjs
node .github/scripts/test_issue606_pressure_vehicle_classification_runtime.mjs
node .github/scripts/test_issue603_settings_persistence_runtime.mjs
node .github/scripts/test_issue604_tablet_controls_runtime.mjs
node .github/scripts/test_issue608_pressure_board_tablet_geometry.mjs
node .github/scripts/test_issue610_uk_knowledge_runtime.mjs
node .github/scripts/test_issue612_command_experience_runtime.mjs
node .github/scripts/test_issue614_quick_places_runtime.mjs
node .github/scripts/test_issue553_alliance_member_manager_menu_runtime.js
node .github/scripts/test_issue553_alliance_member_manager_page_runtime.js
echo "[preflight] Complete"
