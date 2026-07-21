#!/usr/bin/env python3
from __future__ import annotations

import hashlib
import json
import re
import shutil
import subprocess
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
REPORT = ROOT / "docs/issue-282-lssm-upstream-inspection.txt"
TOKENS = (
    "coastal_boat",
    "large_coastal_boat",
    "coastal_guard_boat",
    "Inland Rescue Boat",
    "Seagoing Vessel",
    "ILB or ALB",
    "ILBs or ALBs",
)


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main() -> int:
    temp_root = Path(tempfile.mkdtemp(prefix="issue-282-lssm-"))
    checkout = temp_root / "LSSM-V.4"
    try:
        subprocess.run(
            ["git", "clone", "--depth", "1", "--branch", "dev", "https://github.com/LSS-Manager/LSSM-V.4.git", str(checkout)],
            check=True,
            text=True,
        )
        commit = subprocess.check_output(["git", "-C", str(checkout), "rev-parse", "HEAD"], text=True).strip()
        output = [f"LSSM-V.4 dev commit: {commit}"]

        catalogue = checkout / "src/modules/extendedCallWindow/i18n/en_GB.json"
        vehicles = checkout / "src/i18n/en_GB/vehicles.ts"
        output.extend((
            f"EMV path: {catalogue.relative_to(checkout)}",
            f"EMV sha256: {sha256(catalogue)}",
            f"Vehicles path: {vehicles.relative_to(checkout)}",
            f"Vehicles sha256: {sha256(vehicles)}",
        ))

        emv = json.loads(catalogue.read_text(encoding="utf-8"))["enhancedMissingVehicles"]
        maritime = [entry for entry in emv.get("vehiclesByRequirement", []) if set(entry.get("vehicles", [])) & {67, 68, 69, 74}]
        output.extend(("\n===== EMV MARITIME REQUIREMENTS =====", json.dumps(maritime, indent=2, sort_keys=True)))

        vehicle_text = vehicles.read_text(encoding="utf-8")
        captions = {}
        for match in re.finditer(r"^\s*(\d+):\s*\{[\s\S]*?^\s*caption:\s*'([^']+)'", vehicle_text, re.MULTILINE):
            captions[int(match.group(1))] = match.group(2)
        output.extend(("\n===== VEHICLE CAPTIONS 57-94 =====", json.dumps({key: captions.get(key) for key in range(57, 95) if key in captions}, indent=2, sort_keys=True)))

        output.append("\n===== TOKEN MATCHES =====")
        for path in sorted(checkout.rglob("*")):
            if not path.is_file() or path.suffix.lower() not in {".ts", ".js", ".json", ".vue", ".md"}:
                continue
            try:
                text = path.read_text(encoding="utf-8")
            except UnicodeDecodeError:
                continue
            matching = [token for token in TOKENS if token.casefold() in text.casefold()]
            if not matching:
                continue
            output.append(f"\n--- {path.relative_to(checkout)} :: {', '.join(matching)} ---")
            lines = text.splitlines()
            for index, line in enumerate(lines):
                if any(token.casefold() in line.casefold() for token in matching):
                    start = max(0, index - 3)
                    end = min(len(lines), index + 4)
                    for line_no in range(start, end):
                        output.append(f"{line_no + 1:06d}: {lines[line_no]}")
                    output.append("")

        REPORT.write_text("\n".join(output) + "\n", encoding="utf-8")
        print(f"Wrote {REPORT.relative_to(ROOT)} ({REPORT.stat().st_size} bytes)")
        return 0
    finally:
        shutil.rmtree(temp_root, ignore_errors=True)


if __name__ == "__main__":
    raise SystemExit(main())
