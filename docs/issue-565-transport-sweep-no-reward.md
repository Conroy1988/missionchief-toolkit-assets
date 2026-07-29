# Issue #565 — native Patient Transport Sweep restoration

Toolkit v8.2.7 follows the observed MissionChief UK flow: open the mission, open the flashing alliance-owned FMS 5 vehicle, click the visible **Cancel Transport** control, recognise **Patient isn’t transported**, then continue to the next patient and mission.

The control detector accepts links, buttons and submit inputs and supports both **Cancel Transport** and **Discharge patient**. It records the original label before clicking so an unchanged Cancel Transport label cannot be treated as successful completion.
