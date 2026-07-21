# Issue #285 — Railway Police Responding contract

MissionChief Railway Police Officers use the native education key `railway_police`. The separate key `railway_police_command` represents Mobile Operations Managers and does not satisfy this requirement.

The Matrix reads Units Responding from the canonical `#mission_vehicle_driving` table, resolves the stable vehicle identity, uses the responding crew cell `sortvalue` only within that canonical table, and combines it with explicit or linked qualification evidence.

Accepted specialist evidence includes MissionChief-native education attributes, compatible filter payloads, and existing discrete bracketed badges. Generic vehicle captions, custom categories, vehicle type alone and total crew without qualification evidence do not prove Railway Police capacity.

If crew is known but the specialist qualification cannot be proven, capacity remains bounded/unknown instead of being reported as a confident zero.
