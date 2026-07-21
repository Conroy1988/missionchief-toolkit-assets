# Observer ownership inventory — Toolkit v4.20.24

> Measurement-only evidence. No observer scope, callback, timing or runtime behaviour is changed by this inventory.

## Result

- MutationObserver constructions: **12**
- ResizeObserver constructions: **4**
- Observe registrations: **19**
- Broad `subtree: true` registrations: **10**
- Explicit document/body subtree registrations: **3**
- Long-lived observers with a documented owner and duplicate guard: **16 / 16**
- AST-unresolved main-observer registrations manually reconciled: **3 / 3**

The early Alliance Buildings observer is the sole deliberate page-process-lifetime exception. It is protected by `allianceBuildingsContextWatcherInstalled`; all other observers are owned by the replaceable Toolkit runtime, with several also having subsystem-specific disconnect paths.

## Inventory

| Subsystem | Type | Line | Registrations | Ownership | Duplicate guard | Teardown |
|---|---:|---:|---:|---|---|---|
| Alliance Buildings early suppression | MutationObserver | 421 | 1 | page-process-lifetime | allianceBuildingsContextWatcherInstalled | Browser document lifetime; not registered in the replaceable Toolkit runtime. |
| Desktop panel workspace | ResizeObserver | 13849 | 1 | runtime | desktopPanelResizeObserver singleton plus desktopPanelObservedElements set | runtime.destroy disconnects; stopDesktopPanelWorkspaceObservation unobserves current elements. |
| Tablet map area | ResizeObserver | 14028 | 1 | runtime | tabletDockResizeObserver singleton and observed-element identity | runtime.destroy disconnects; tablet observation reset disconnects/unobserves. |
| Custom vehicle badges | MutationObserver | 15301 | 1 | runtime | customVehicleBadgeObservedDocuments WeakSet | runtime.destroy disconnects all tracked observers. |
| Major Incident Feed | ResizeObserver | 19469 | 2 | runtime-and-subsystem | majorIncidentFeedObservedElement identity | resetMajorIncidentFeedObserver disconnects; runtime.destroy is final owner. |
| Mission Value host sizing | ResizeObserver | 21539 | 1 | runtime-and-record | missionValueHostObservers Map keyed by spacer | pruneMissionValueHostObservers disconnects stale records; runtime.destroy is final owner. |
| Mission Value toolbar content | MutationObserver | 21543 | 1 | runtime-and-record | missionValueHostObservers Map keyed by spacer | pruneMissionValueHostObservers disconnects stale records; runtime.destroy is final owner. |
| Mission Value document discovery | MutationObserver | 21701 | 1 | runtime | missionValueObservedDocuments WeakSet | runtime.destroy disconnects. |
| Mission Requirements live record | MutationObserver | 22986 | 1 | runtime-and-record | missionRequirementsRecords record identity | record cleanup disconnects; runtime.destroy is final owner. |
| Mission Requirements document discovery | MutationObserver | 23087 | 1 | runtime | missionRequirementsObservedDocuments WeakSet | runtime.destroy disconnects. |
| Credits total | MutationObserver | 25843 | 1 | runtime-and-element | observedCreditsElement identity plus creditsValueObserver | Explicitly disconnects and untracks before replacing; runtime.destroy is final owner. |
| Alliance Buildings page rendering | MutationObserver | 30955 | 1 | runtime | install path returns early from normal boot for the page context | runtime.destroy disconnects. |
| Auto-load mission root visibility | MutationObserver | 31163 | 1 | runtime-and-subsystem | Always disconnects previous root observer before binding. | disconnectAutoLoadAllVehiclesRootObserver and runtime.destroy. |
| Auto-load native link state | MutationObserver | 31181 | 1 | runtime-and-subsystem | Always disconnects previous link observer before binding. | disconnectAutoLoadAllVehiclesLinkObserver and runtime.destroy. |
| Auto-load document discovery | MutationObserver | 31294 | 1 | runtime-and-subsystem | autoLoadAllVehiclesObserver singleton | stopAutoLoadAllVehicles untracks/disconnects; runtime.destroy is final owner. |
| Main map and mission lifecycle | MutationObserver | 31354 | 3 | runtime | bootStarted plus replaceable runtime singleton | runtime.destroy disconnects; connectMainMutationObserver disconnects before re-targeting. |

## Review conclusion

- No observer is currently orphaned.
- The three previously unresolved `.observe()` calls belong to the runtime-tracked main MutationObserver created in `boot()`.
- Raw observer count is not an optimisation target. Different ownership and timing semantics must remain separate.
- No production observer change is justified from static ownership evidence alone.
- Issue #256 can be closed as an inventory/audit task; any later narrowing must use one observer subsystem per PR and equivalent live browser evidence.
