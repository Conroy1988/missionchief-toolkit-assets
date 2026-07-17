#!/usr/bin/env bash
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
cd "$ROOT"

MODE="${1:---all}"
if [[ "$MODE" != "--all" && "$MODE" != "--contracts" ]]; then
  echo "Usage: $0 [--all|--contracts]" >&2
  exit 2
fi

SOURCE="src/MissionChief_Map_Command_Toolkit.user.js"
DIST_JS="dist/MissionChief_Map_Command_Toolkit.user.js"
DIST_TXT="dist/MissionChief_Map_Command_Toolkit.txt"

if [[ "$MODE" == "--all" ]]; then
  echo "[preflight] Validate canonical userscript and generated distribution"
  python3 .github/scripts/validate_userscript.py
fi

echo "[preflight] Verify JavaScript syntax"
node --check "$SOURCE"

echo "[preflight] Verify distribution parity"
cmp --silent "$DIST_JS" "$DIST_TXT"

CONTRACTS=(
  .github/scripts/test_financial_ledger_contract.py
  .github/scripts/test_mission_marker_ingestion_contract.py
  .github/scripts/test_settings_ui_contract.py
  .github/scripts/test_desktop_panel_layout_contract.py
  .github/scripts/test_section_navigation_contract.py
  .github/scripts/test_mission_value_contract.py
  .github/scripts/test_transport_sweep_lssm_contract.py
)

for contract in "${CONTRACTS[@]}"; do
  [[ -f "$contract" ]] || { echo "Missing contract: $contract" >&2; exit 1; }
  echo "[preflight] Run $(basename "$contract")"
  python3 "$contract"
done

echo "[preflight] Complete"
