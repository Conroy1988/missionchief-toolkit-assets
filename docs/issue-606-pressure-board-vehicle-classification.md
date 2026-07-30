# Issue #606 — Pressure Board vehicle classification and location evidence

## Production defect

Toolkit v9.1.1 correctly recognised available personal vehicles through MissionChief FMS 1/2 status, but its resource resolver compared missing-requirement names with vehicle captions. Custom callsigns therefore left category pools empty even while the board reported a large available fleet.

## v9.1.2 contract

- Preserve MissionChief's numeric `vehicle_type`, `vehicleType`, `vehicle_type_id` or `vehicleTypeId` from supported record containers.
- Resolve every known UK vehicle requirement through the bundled canonical catalogue.
- Match numeric types first, own-vehicle classification evidence second, and caption/name text only when no canonical requirement is known.
- Keep FMS 1/2 and no-target eligibility unchanged.
- Allocate a personal vehicle to at most one confirmed or provisional pressure slot.
- Allocate confirmed in-radius evidence before reserving any vehicle whose location is unavailable.
- Report recognised capacity, confirmed in-radius capacity, unlocated capacity and known outside-radius capacity separately.
- Never turn absent mission or vehicle coordinates into a false claim of zero fleet availability or confirmed coverage.
- Keep the Pressure Board and Operational SITREP read-only and add no request, timer, observer or polling owner.

## Verification

The executable Issue #606 fixture covers custom callsigns, Fire/Police/Ambulance/ARV/DSU types, current Police helicopter wording, combined vehicle requirements, own-category fallback, rejection of misleading captions for known requirements, unknown-requirement text fallback, nested vehicle-type fields, unknown mission and vehicle coordinates, confirmed outside-radius capacity and global one-vehicle allocation.

The runtime test also reconstructs the complete embedded catalogue and requires byte-equivalent keys, type arrays and normalised aliases from `src/data/mission-requirements-en_GB.json`.
