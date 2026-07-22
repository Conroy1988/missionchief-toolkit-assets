# Issue #378 — Nuclear Operational Window Suite Contract

## Status

Phase 1 baseline for the first post-4.20 major Toolkit release.

This contract governs the retirement of the existing Mission Requirements Matrix and the Toolkit-native port of the current LSSM V.4 Extended Call Window, Extended Call List and Enhanced Transport Requests feature families.

Production publication is prohibited until every release gate in this document is satisfied.

## Source baselines

### Toolkit

- Repository: `Conroy1988/missionchief-toolkit-assets`
- Canonical branch: `main`
- Baseline commit: `d1e0f30114f3be5f17b5142ec1781868214087bc`
- Baseline version: `4.20.37`
- Canonical userscript: `src/MissionChief_Map_Command_Toolkit.user.js`

### LSSM

- Repository: `LSS-Manager/LSSM-V.4`
- Canonical development branch: `dev`
- Inspected baseline commit: `88e41646e59a7d620624f90f1d9a0a62320c2775`

The LSSM baseline must be refreshed at the start of every implementation phase. An upstream change after this baseline is not imported automatically; it must be reviewed against this contract.

## Permission basis

The Toolkit owner and LSSM developer has confirmed explicit permission to reuse, adapt, integrate and redistribute the relevant LSSM implementation in the MIT-licensed Toolkit.

The public LSSM repository is otherwise distributed under CC BY-NC-SA 4.0. The direct port therefore relies on the confirmed permission exception rather than the repository's default public licence terms.

The authorised scope is limited to the three module families named in this contract and direct dependencies required to reproduce their behaviour.

## Non-negotiable outcome

The existing Toolkit Mission Requirements Matrix is not the long-term implementation. It must be retired after the replacement suite proves parity and stability.

There must never be two active Toolkit requirements engines on the same mission document.

The old Matrix remains available only as a rollback implementation until the release candidate passes every gate. It must not be removed from the stable branch prematurely.

## Upstream module inventory

### Extended Call Window

Verified entry points:

- `src/modules/extendedCallWindow/main.ts`
- `src/modules/extendedCallWindow/settings.ts`
- `src/modules/extendedCallWindow/docs/en_GB.md`

Verified enhanced-requirements core:

- `src/modules/extendedCallWindow/assets/enhancedMissingVehicles.ts`
- `src/modules/extendedCallWindow/assets/emv/getMissingRequirements.ts`
- `src/modules/extendedCallWindow/assets/emv/getVehicleListObserveHandler.ts`
- `src/modules/extendedCallWindow/components/enhancedMissingVehicles/EMVComponent.vue`
- `src/modules/extendedCallWindow/components/enhancedMissingVehicles/EMVTable.vue`
- `typings/modules/ExtendedCallWindow/EnhancedMissingVehicles.d.ts`

Verified secondary feature entry points include:

- ARR search, counters, highlights, hover information and category colours;
- tailored tabs;
- alarm icons and alarm time;
- generation date;
- patient summary and collapsible patients;
- selected-vehicle, vehicle and player counters;
- sticky header and load-more controls;
- hide vehicle list and permanent vehicle search;
- vehicle type in list;
- mission keywords;
- centre-map action;
- remaining patient time;
- expanded release-patient controls;
- staging-area selected counter.

### Extended Call List

Verified entry points:

- `src/modules/extendedCallList/main.ts`
- `src/modules/extendedCallList/settings.ts`
- `src/modules/extendedCallList/docs/en_GB.md`

Verified behaviour families:

- mission sorting in the list and mission window;
- starring and persisted starred state;
- collapsing, collapse-all and persisted collapsed state;
- mission sharing;
- current patient and prisoner counts;
- patient/prisoner tooltip augmentation;
- remaining mission, patient and pumping time;
- average credits;
- fixed event information;
- configurable event-mission labels;
- vehicle mission participation state;
- mission-list button-group and progress-prepend coordinators.

### Enhanced Transport Requests

Verified entry points:

- `src/modules/enhancedTransportRequests/main.ts`
- `src/modules/enhancedTransportRequests/settings.ts`
- `src/modules/enhancedTransportRequests/assets/autoClickSuccessBtns.ts`
- `src/modules/enhancedTransportRequests/assets/autoOpenTransportRequest.ts`

Verified settings:

- `autoClickSuccessBtns`, default enabled upstream;
- `autoOpenTransportRequest`, default disabled upstream.

## Behavioural model: enhanced requirements

The replacement requirements engine must reproduce the upstream model rather than retaining the current Matrix's layered alias/hotfix architecture.

### Requirement source

Primary root:

```css
#missing_text
```

Requirement groups:

```css
[data-requirement-type="vehicles"]
[data-requirement-type="personnel"]
[data-requirement-type="other"]
```

Original requirement text must remain recoverable. Unparsed fragments must remain visible and unresolved rather than being promoted to a false covered state.

### Requirement graph

For each parsed requirement, build reverse indexes from:

- eligible vehicle type IDs;
- eligible equipment identifiers;
- conditional vehicle types controlled by mission metadata;
- capacity factors for vehicles/equipment;
- tractive/towing relationships.

The calculation model must support:

- unit counts;
- equipment/capacity counts;
- personnel minimum/maximum ranges;
- alternative vehicle types;
- conditional eligibility;
- trailers and tractive vehicles;
- water, foam and pump progress requirements.

### En-route source

Primary table:

```css
#mission_vehicle_driving tbody tr
```

Read stable MissionChief attributes before visible labels. Personnel contributions use the active row's staff value where exposed. Equipment contributions use `data-equipment-type` metadata.

### Selected source

Normal and occupied lists:

```css
#vehicle_show_table_body_all .vehicle_checkbox:checked
#occupied .vehicle_checkbox:checked
```

Preferred attributes:

- `value`;
- `vehicle_type_id`;
- `data-equipment-types`;
- `tractive_vehicle_id`;
- `tractive_random`.

Selected state must be recalculated from the live checked set. Increment/decrement counters are forbidden.

### Coverage state

For a numeric requirement:

```text
remaining = missing - driving - selected
covered = remaining <= 0
```

For personnel ranges, use the configured minimum/maximum interpretation without collapsing ambiguity into a false exact value.

### Observation model

Observers must be narrowly scoped to:

- requirement-root replacement;
- en-route table mutation/replacement;
- selected amount changes;
- checked-state/equipment metadata changes;
- MissionChief lightbox or AJAX mission replacement.

Mutation bursts must be coalesced. A recalculation that produces an unchanged view model must not replace the rendered DOM.

## Toolkit adaptation boundaries

LSSM's implementation depends on Vue, Pinia, webpack chunks, module settings, API stores, translation stores and utility methods. None of those runtime dependencies may be imported into the Toolkit.

Required substitutions:

| LSSM dependency | Toolkit replacement |
|---|---|
| Vue components/reactivity | Toolkit-owned DOM renderer and immutable view model |
| Pinia/settings store | Existing Toolkit state and persistence layer |
| LSSM API vehicle cache | MissionChief live attributes plus Toolkit capability catalogue |
| LSSM translations | Toolkit locale tables with UK-first verified mappings |
| webpack dynamic imports | Route-gated initialisers in the standalone userscript |
| LSSM root style manager | Collision-resistant Toolkit stylesheet rules |
| LSSM module lifecycle | Toolkit coordinator with deterministic teardown |

The port may preserve upstream algorithms and interaction semantics, but it must not emulate or bootstrap an LSSM runtime.

## Settings namespace

New settings must use an isolated namespace so rollback and migration remain deterministic.

Recommended logical groups:

- `operationalWindow.requirements.*`
- `operationalWindow.arr.*`
- `operationalWindow.patients.*`
- `operationalWindow.vehicleList.*`
- `operationalWindow.missionList.*`
- `operationalWindow.transport.*`

The final storage keys must follow the Toolkit's existing state-version convention.

## Matrix migration and retirement

### Migration

- Matrix enabled -> enhanced requirements enabled.
- Matrix layout preference -> closest safe table/text/normal-flow preference.
- Existing mission requirement reporting must remain available only for genuinely unparsed live text.
- Settings without semantic equivalents must not be guessed.
- Automatic transport actions retain their upstream safe defaults.

### Retirement gate

The following must be identified and removed from active runtime:

- Matrix parser and resolver;
- capability hotfix layers;
- Matrix renderer and responsive cards;
- Matrix selection/en-route observers;
- Matrix schedulers and lifecycle records;
- Matrix-specific state/settings;
- stale Matrix fixtures and documentation assertions.

Removal occurs only after the new engine passes the same mission fixtures plus the expanded Issue #378 suite.

## LSSM coexistence

The Toolkit must support:

1. LSSM absent;
2. LSSM present with equivalent modules disabled;
3. LSSM present with Extended Call Window active;
4. LSSM present with Extended Call List active;
5. LSSM present with Enhanced Transport Requests active;
6. both load orders.

Rules:

- Do not mutate LSSM-owned nodes.
- Suppress only the equivalent Toolkit surface/action.
- Generic MissionChief classes are not sufficient ownership markers.
- Enhanced requirements can identify the active LSSM component through explicit structure such as `.alert-missing-vehicles[data-raw-html]`.
- Mission-list coexistence must detect feature-specific controls/ownership rather than disabling the entire Toolkit mission-list suite.
- Transport coexistence must use one-action tokens so only one automation performs each navigation/click.

## Desktop, Tablet and iOS contract

### Desktop

- Full sortable table permitted.
- Normal-flow and optional overlay modes permitted.
- Overlay position bounded to the viewport and persisted.

### Tablet

- No horizontal page overflow.
- Controls must remain touch-safe.
- Overlay defaults must not obscure dispatch controls.

### iOS Mobile Mode

- Normal-flow presentation is the safe default.
- Drag-only controls are forbidden.
- Safe-area insets must be respected.
- Requirements table must collapse into responsive rows/cards where required.
- Dispatch, ARR, patient, prisoner and transport actions must remain visible and usable.

## Transport action safety

Automatic transport features are high-impact UI automation.

Each action requires:

- an explicit setting;
- route and DOM precondition validation;
- an idempotency token scoped to the current vehicle/patient/prisoner request;
- one action per qualifying request;
- no repeated history navigation;
- no click on hidden, disabled, stale or ambiguous controls;
- teardown on route/lightbox replacement.

## Mission-list mutation model

The mission list is dynamic. The replacement must process added, updated and removed missions incrementally.

Forbidden patterns:

- unconditional full-list rebuild after every mutation;
- duplicate button groups;
- sorting that destroys MissionChief event handlers;
- stale starred/collapsed IDs retained indefinitely;
- tooltip augmentation that duplicates on repeated refreshes.

## Test matrix

### Enhanced requirements

- simple vehicle requirement;
- multiple vehicle counts;
- alternative/combined types;
- selected and occupied lists;
- dispatch, refresh and arrival transitions;
- personnel ranges;
- equipment and capacity factors;
- trailers/tractives;
- water/foam/pump;
- unknown fragments;
- ARR selection and vehicle-group refresh;
- repeated scans without duplicate observers or panels.

### Extended Call Window secondary features

- each setting independently enabled/disabled;
- combinations that share ARR/vehicle-list DOM;
- patient summary and collapse thresholds;
- normal-flow/overlay/minimised/text/table state;
- position persistence and viewport clamping;
- lightbox replacement.

### Extended Call List

- dynamic add/update/remove;
- sorting modes and direction;
- mission-window next/previous order;
- star/collapse persistence;
- collapse-all;
- patient/prisoner counts and tooltips;
- time displays;
- average credits;
- event labels;
- share controls;
- no duplicate controls after repeated updates.

### Transport

- auto-open disabled/enabled;
- success click disabled/enabled;
- patient, prisoner and supported vehicle routes;
- one-action idempotency;
- hidden/disabled controls;
- navigation replacement;
- coexistence with LSSM.

### Compatibility

Every release fixture runs in:

- Desktop;
- Tablet Mode;
- iOS Mobile Mode;
- light and dark MissionChief themes;
- LSSM absent/present;
- both load orders.

## Performance gates

- one coordinator per active surface;
- no unbounded document observer;
- mutation bursts coalesced to one scheduled pass;
- no DOM replacement when the view model is unchanged;
- incremental mission-list processing;
- route-gated initialisation;
- observer/listener counts return to baseline after teardown;
- no regression against the active Toolkit performance budgets.

## Delivery phases

1. **Inventory and contracts** — this document, dependency map and test plan.
2. **Lifecycle/settings shell** — isolated suite coordinator, settings namespace and coexistence detector.
3. **Enhanced requirements engine** — parser, graph, selected/en-route calculation and renderer.
4. **Extended Call Window parity** — remaining alarm-window features.
5. **Extended Call List parity** — mission-list feature family.
6. **Enhanced Transport Requests** — idempotent transport automation.
7. **Matrix retirement** — migration and removal of old runtime.
8. **Hardening** — browser, coexistence, performance and regression validation.
9. **Major release** — guarded candidate, GitHub release, Greasy Fork, manifest and Discord verification.

## Pull-request policy

All implementation remains on the dedicated Issue #378 branch/PR until the suite is complete enough to replace the Matrix safely.

Small commits and phase-specific tests are required. Partial production publication is forbidden.

## Release gate

A major release may proceed only when:

- all Issue #378 acceptance criteria are complete;
- old Matrix runtime is absent from the candidate;
- all new settings and migration paths are verified;
- deterministic fixtures pass;
- live UK mission validation passes;
- Desktop, Tablet and iOS pass;
- LSSM coexistence passes;
- performance budgets pass;
- all required workflows are green;
- rollback has been rehearsed;
- the release candidate has been manually approved by the Toolkit owner.
