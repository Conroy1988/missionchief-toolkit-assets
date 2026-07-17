# Issue #133 — Integration context

Generated mechanically from the canonical userscript. Inspection only.

## `const SCRIPT =`

### Match 1 · canonical line 491

```javascript
00461:             })));
00462:             if (relevant) queueAllianceBuildingsEarlyCheck();
00463:         });
00464:         const begin = () => {
00465:             const root = document.documentElement;
00466:             if (root) observer.observe(root, { childList: true, subtree: true, attributes: true, attributeFilter: ['style', 'class', 'hidden', 'aria-hidden'] });
00467:         };
00468:         if (document.documentElement) begin();
00469:         else document.addEventListener('readystatechange', begin, { once: true });
00470: 
00471:         pageWindow.addEventListener?.('popstate', queueAllianceBuildingsEarlyCheck);
00472:         pageWindow.addEventListener?.('hashchange', queueAllianceBuildingsEarlyCheck);
00473:         pageWindow.addEventListener?.('pageshow', queueAllianceBuildingsEarlyCheck);
00474:         pageWindow.addEventListener?.('load', queueAllianceBuildingsEarlyCheck, { once: true });
00475:         applyAllianceBuildingsEarlySuppression();
00476:     }
00477: 
00478:     const earlyAllianceBuildingsPage = isAllianceBuildingsPath();
00479:     const earlyAllianceBuildingsMapEnabled = readAllianceBuildingsMapPreferenceEarly();
00480:     if (earlyAllianceBuildingsPage) {
00481:         document.documentElement?.setAttribute('data-mcms-alliance-buildings-page', 'true');
00482:         document.documentElement?.setAttribute('data-mcms-alliance-buildings-map', earlyAllianceBuildingsMapEnabled ? 'enabled' : 'disabled');
00483:     }
00484:     if (!earlyAllianceBuildingsMapEnabled) {
00485:         installAllianceBuildingsEarlyStyle();
00486:         installAllianceBuildingsLeafletAssignmentGuard();
00487:         installAllianceBuildingsContextWatcherEarly();
00488:     }
00489: 
00490: 
00491:     const SCRIPT = {
00492:         name: 'MissionChief Map Command Toolkit',
00493:         version: '4.14.10',
00494:         author: 'Conroy1988',
00495:         controlId: 'mc-map-command-toolkit-control',
00496:         panelId: 'mc-map-command-toolkit-panel',
00497:         toastId: 'mc-map-command-toolkit-toast',
00498:         payoutFlashId: 'mc-map-command-toolkit-payout-flash',
00499:         criticalDrawerId: 'mc-map-command-toolkit-critical-drawer',
00500:         vehicleStatusId: 'mc-map-command-toolkit-vehicle-status',
00501:         majorIncidentFeedId: 'mc-map-command-toolkit-major-incident-feed',
00502:         missionInspectorId: 'mc-map-command-toolkit-mission-inspector',
00503:         transportSweepHudId: 'mc-map-command-toolkit-transport-sweep-hud',
00504:         helpCenterId: 'mc-map-command-toolkit-help-center',
00505:         cleanExitId: 'mcms-clean-exit',
00506:         styleId: 'mc-map-command-toolkit-style-v4146',
00507:         oldControlId: 'mc-map-command-skins-control',
00508:         oldGeoLabelLayerId: 'mcms-persistent-label-layer',
00509:         storageState: 'mc_map_command_toolkit_state_v150',
00510:         payoutHistoryState: 'mc_map_command_toolkit_payout_history_v200',
00511:         sessionPerformanceState: 'mc_map_command_toolkit_session_v200',
00512:         missionProgressState: 'mc_map_command_toolkit_mission_progress_v250',
00513:         discordWebhookState: 'mc_map_command_toolkit_discord_webhook_v300',
00514:         discordLastReportState: 'mc_map_command_toolkit_discord_last_report_v310',
00515:         financeVaultState: 'mc_map_command_toolkit_finance_vault_v450',
00516:         financeVaultCredentialState: 'mc_map_command_toolkit_finance_vault_credential_v450',
00517:         financeRulesCacheState: 'mc_map_command_toolkit_finance_rules_v450',
00518:         financePolicyCacheState: 'mc_map_command_toolkit_finance_policy_v460',
00519:         oldStorageKeys: [
00520:             'mc_map_command_toolkit_state_v149',
00521:             'mc_map_command_toolkit_state_v148',
00522:             'mc_map_command_toolkit_state_v147',
00523:             'mc_map_command_toolkit_state_v146',
00524:             'mc_map_command_toolkit_state_v145',
00525:             'mc_map_command_toolkit_state_v144',
00526:             'mc_map_command_toolkit_state_v143',
00527:             'mc_map_command_toolkit_state_v142',
00528:             'mc_map_command_toolkit_state_v141',
00529:             'mc_map_command_toolkit_state_v140',
00530:             'mc_map_command_toolkit_state_v130'
00531:         ],
00532:         legacyTheme: 'mc_map_command_skins_theme_v2',
00533:         legacyPosition: 'mc_map_command_skins_position_v1'
00534:     };
00535: 
00536:     const RUNTIME_KEY = '__MC_MAP_COMMAND_TOOLKIT_RUNTIME__';
00537:     const previousRuntime = pageWindow[RUNTIME_KEY];
00538:     if (previousRuntime?.version === SCRIPT.version && previousRuntime.destroyed !== true) return;
00539:     try { previousRuntime?.destroy?.('replaced by a newer toolkit runtime'); } catch (err) {}
00540: 
00541:     const runtime = {
00542:         version: SCRIPT.version,
00543:         destroyed: false,
00544:         timeouts: new Set(),
00545:         intervals: new Set(),
00546:         animationFrames: new Set(),
00547:         observers: new Set(),
00548:         waiters: new Set(),
00549:         requests: new Set(),
00550:         fetchControllers: new Set(),
00551:         listeners: [],
00552:         mapBindings: [],
00553:         hookRestorers: [],
00554:         cleanupCallbacks: [],
00555:         destroy(reason = 'runtime shutdown') {
00556:             if (this.destroyed) return;
00557:             this.destroyed = true;
00558:             for (const id of this.timeouts) { try { pageWindow.clearTimeout(id); } catch (err) {} }
00559:             for (const id of this.intervals) { try { pageWindow.clearInterval(id); } catch (err) {} }
00560:             for (const id of this.animationFrames) { try { pageWindow.cancelAnimationFrame(id); } catch (err) {} }
00561:             this.timeouts.clear();
00562:             this.intervals.clear();
00563:             this.animationFrames.clear();
00564:             for (const settle of Array.from(this.waiters)) { try { settle(false); } catch (err) {} }
00565:             this.waiters.clear();
00566:             for (const request of Array.from(this.requests)) { try { request.abort?.(); } catch (err) {} }
00567:             this.requests.clear();
00568:             for (const controller of Array.from(this.fetchControllers)) { try { controller.abort(); } catch (err) {} }
00569:             this.fetchControllers.clear();
00570:             for (const observer of this.observers) { try { observer.disconnect(); } catch (err) {} }
00571:             this.observers.clear();
00572:             for (const { target, type, listener, options } of this.listeners.splice(0)) {
00573:                 try { target.removeEventListener(type, listener, options); } catch (err) {}
00574:             }
00575:             for (const binding of this.mapBindings.splice(0)) {
00576:                 try { binding.map.off(binding.types, binding.handler); } catch (err) {}
00577:             }
00578:             for (const restore of this.hookRestorers.splice(0).reverse()) { try { restore(); } catch (err) {} }
00579:             for (const cleanup of this.cleanupCallbacks.splice(0).reverse()) { try { cleanup(reason); } catch (err) {} }
00580:             if (pageWindow[RUNTIME_KEY] === this) {
00581:                 try { delete pageWindow[RUNTIME_KEY]; } catch (err) { pageWindow[RUNTIME_KEY] = null; }
```

## `const UI_THEMES =`

### Match 1 · canonical line 972

```javascript
00952:         bond007DossierGrid: 'https://raw.githubusercontent.com/Conroy1988/missionchief-toolkit-assets/main/themes/james-bond/ui/classified-dossier-grid.svg',
00953:         bond007Agent: 'https://raw.githubusercontent.com/Conroy1988/missionchief-toolkit-assets/main/themes/james-bond/ui/agent-silhouette.svg',
00954:         bond007Portrait: 'https://raw.githubusercontent.com/Conroy1988/missionchief-toolkit-assets/main/themes/james-bond/payout/daniel-craig-007-portrait.png',
00955:         bond007GoldDivider: 'https://raw.githubusercontent.com/Conroy1988/missionchief-toolkit-assets/main/themes/james-bond/ui/gold-divider.svg',
00956:         bond007PayoutSeal: 'https://raw.githubusercontent.com/Conroy1988/missionchief-toolkit-assets/main/themes/james-bond/payout/funds-authorised-seal.svg',
00957:         umbrellaEmblem: 'https://raw.githubusercontent.com/Conroy1988/missionchief-toolkit-assets/main/themes/umbrella/ui/umbrella-containment-emblem.svg',
00958:         umbrellaContainmentBadge: 'https://raw.githubusercontent.com/Conroy1988/missionchief-toolkit-assets/main/themes/umbrella/ui/containment-division-badge.svg',
00959:         umbrellaFacilitySchematic: 'https://raw.githubusercontent.com/Conroy1988/missionchief-toolkit-assets/main/themes/umbrella/ui/facility-schematic.svg',
00960:         umbrellaSurveillanceTerminal: 'https://raw.githubusercontent.com/Conroy1988/missionchief-toolkit-assets/main/themes/umbrella/ui/surveillance-terminal.svg',
00961:         umbrellaSpecimenVial: 'https://raw.githubusercontent.com/Conroy1988/missionchief-toolkit-assets/main/themes/umbrella/ui/specimen-vial.svg',
00962:         umbrellaPayoutSeal: 'https://raw.githubusercontent.com/Conroy1988/missionchief-toolkit-assets/main/themes/umbrella/payout/transfer-authorized-seal.svg',
00963:         hyruleCrest: 'https://raw.githubusercontent.com/Conroy1988/missionchief-toolkit-assets/main/themes/hyrule/ui/hyrule-command-crest.svg',
00964:         hyruleEye: 'https://raw.githubusercontent.com/Conroy1988/missionchief-toolkit-assets/main/themes/hyrule/ui/ancient-eye-rune.svg',
00965:         hyruleEnergyRing: 'https://raw.githubusercontent.com/Conroy1988/missionchief-toolkit-assets/main/themes/hyrule/ui/zonai-energy-ring.svg',
00966:         hyruleSwordShield: 'https://raw.githubusercontent.com/Conroy1988/missionchief-toolkit-assets/main/themes/hyrule/ui/master-sword-shield-silhouette.svg',
00967:         hyruleMap: 'https://raw.githubusercontent.com/Conroy1988/missionchief-toolkit-assets/main/themes/hyrule/ui/parchment-command-map.svg',
00968:         hyruleQuestSeal: 'https://raw.githubusercontent.com/Conroy1988/missionchief-toolkit-assets/main/themes/hyrule/payout/quest-complete-seal.svg',
00969:         hyruleRupeeBurst: 'https://raw.githubusercontent.com/Conroy1988/missionchief-toolkit-assets/main/themes/hyrule/payout/rupee-burst.svg'
00970:     });
00971: 
00972:     const UI_THEMES = Object.freeze({
00973:         mapCommand: Object.freeze({ label: 'Map Command', short: 'DEFAULT', icon: '▦', description: 'The original operational command interface.' }),
00974:         cyberpunk: Object.freeze({ label: 'Cyberpunk', short: 'NEON', icon: '⚡', description: 'Neon tactical interface with angular panels, signal animations and high-contrast controls.' }),
00975:         fallout4: Object.freeze({ label: 'Fallout 4', short: 'PIP-BOY', icon: '☢', description: 'Retro-futurist Pip-Boy terminal interface with phosphor display effects and high-contrast Vault-Tec controls.' }),
00976:         umbrella: Object.freeze({ label: 'Umbrella Containment', short: 'BSL-4', icon: '☣', description: 'Corporate BSL-4 containment interface with original transparent artwork, classified facility schematics, surveillance graphics and protected operational states.' }),
00977:         factorio: Object.freeze({ label: 'Factorio', short: 'AUTOMATION', icon: '⚙', description: 'Industrial automation interface with riveted steel panels, copper controls, hazard markings and factory-line motion.' }),
00978:         bond007: Object.freeze({ label: '007 Intelligence', short: 'MI6', icon: '◉', description: 'Complete Section 00 intelligence interface with original transparent MI6 artwork, gun-barrel targeting graphics, classified dossiers, champagne-gold controls and protected operational states.' }),
00979:         hyrule: Object.freeze({ label: 'Hyrule Command', short: 'TRIFORCE', icon: '△', description: 'Fantasy command interface with parchment cartography, royal gold, ancient blue technology, green energy glyphs and transparent Hyrule-inspired artwork.' })
00980:     });
00981:     const UI_THEME_ORDER = Object.freeze(['mapCommand', 'cyberpunk', 'fallout4', 'umbrella', 'factorio', 'bond007', 'hyrule']);
00982: 
00983:     const THEMES = {
00984:         default: { full: 'Default', label: 'Default', short: 'STD', icon: '□' },
00985:         control: { full: 'Control Room', label: 'Control', short: 'CTL', icon: '◐' },
00986:         incident: { full: 'Incident Focus', label: 'Incident', short: 'INC', icon: '▣' },
00987:         roads: { full: 'Road Priority', label: 'Roads', short: 'RD', icon: '═' },
00988:         urban: { full: 'Urban Grey', label: 'Urban', short: 'URB', icon: '◫' },
00989:         rural: { full: 'Rural Watch', label: 'Rural', short: 'RUR', icon: '◇' },
00990:         nightshift: { full: 'Night Shift', label: 'Night', short: 'NIT', icon: '◆' },
00991:         fireCommand: { full: 'Fire Command', label: 'Fire', short: 'FIRE', icon: '🔥' },
00992:         policeTactical: { full: 'Police Tactical', label: 'Police', short: 'POL', icon: '◆' },
00993:         medicalControl: { full: 'Medical Control', label: 'Medical', short: 'MED', icon: '✚' },
00994:         coastalCommand: { full: 'Coastal Command', label: 'Coastal', short: 'SEA', icon: '⚓' }
00995:     };
00996: 
00997:     const PAYOUT_TEMPLATES = {
00998:         gta5: { label: 'GTA V Inspired', kicker: 'PAYOUT RECEIVED', titleCase: false, particleMode: 'none' },
00999:         viceCity: { label: 'Vice City Inspired', kicker: 'PAYOUT RECEIVED', titleCase: true, particleMode: 'none' },
01000:         badCompany: { label: 'Bad Company Inspired', kicker: 'PAYOUT RECEIVED', titleCase: false, particleMode: 'embers' },
01001:         scarface: { label: 'Scarface Inspired', kicker: 'EMPIRE PAYOUT CONFIRMED', titleCase: false, particleMode: 'stars' },
01002:         cyberpunk: { label: 'Cyberpunk Inspired', kicker: 'CREDIT TRANSFER CONFIRMED', titleCase: false, particleMode: 'glitch' },
01003:         hellfire: { label: 'Hellfire Inspired', kicker: 'REWARD CLAIMED', titleCase: false, particleMode: 'embers' },
01004:         wasteland: { label: 'Fallout Inspired', kicker: 'VAULT-TEC REWARD AUTHORIZED', titleCase: false, particleMode: 'dust' },
01005:         factorio: { label: 'Factorio Industrial', kicker: 'AUTOMATION REWARD CONFIRMED', titleCase: false, particleMode: 'embers' },
01006:         galactic: { label: 'Galactic Command', kicker: 'CREDIT ALLOCATION CONFIRMED', titleCase: false, particleMode: 'stars' },
01007:         darkFantasy: { label: 'Dark Fantasy Inspired', kicker: 'REWARD BESTOWED', titleCase: true, particleMode: 'ash' },
01008:         biohazard: { label: 'Umbrella Containment', kicker: 'CREDIT TRANSFER AUTHORIZED', titleCase: false, particleMode: 'none' },
01009:         underworld: { label: 'Underworld Inspired', kicker: 'REWARD CLAIMED', titleCase: true, particleMode: 'embers' },
01010:         pixelArcade: { label: 'Pixel Arcade Inspired', kicker: 'SCORE BONUS AWARDED', titleCase: false, particleMode: 'pixels' },
01011:         jamesBond: { label: '007 Intelligence', kicker: 'MI6 FUNDS TRANSFER AUTHORISED', titleCase: false, particleMode: 'none' },
01012:         hyruleQuest: { label: 'Hyrule Quest Reward', kicker: 'RUPEE REWARD ACQUIRED', titleCase: false, particleMode: 'rupees' }
01013:     };
01014: 
01015:     const PAYOUT_TEMPLATE_ORDER = ['gta5', 'viceCity', 'badCompany', 'scarface', 'cyberpunk', 'hellfire', 'wasteland', 'factorio', 'jamesBond', 'hyruleQuest', 'galactic', 'darkFantasy', 'biohazard', 'underworld', 'pixelArcade'];
01016: 
01017:     // Hosted real-audio cues remain lazy-loaded through direct raw GitHub URLs.
01018:     // Hosted payout cues are mapped by template and lazy-loaded only when played.
01019:     const PAYOUT_MEDIA_SOUNDS = Object.freeze({
01020:         viceCity: Object.freeze({
01021:             label: 'GTA Vice City Cashout',
01022:             url: 'https://raw.githubusercontent.com/Conroy1988/missionchief-toolkit-assets/main/assets/audio/payout-presets/gta-vice-city-cashout.mp3'
01023:         }),
01024:         badCompany: Object.freeze({
01025:             label: 'BF Bad Company Cashout',
01026:             url: 'https://raw.githubusercontent.com/Conroy1988/missionchief-toolkit-assets/main/assets/audio/payout-presets/bf-bad-company-cashout.mp3'
01027:         }),
01028:         scarface: Object.freeze({
01029:             label: 'Scarface Cashout',
01030:             url: 'https://raw.githubusercontent.com/Conroy1988/missionchief-toolkit-assets/main/assets/audio/payout-presets/scarface-cashout.mp3'
01031:         }),
01032:         cyberpunk: Object.freeze({
01033:             label: 'Cyberpunk Cashout',
01034:             url: 'https://raw.githubusercontent.com/Conroy1988/missionchief-toolkit-assets/main/themes/cyberpunk/audio/cyberpunk-cashout.mp3'
01035:         }),
01036:         wasteland: Object.freeze({
01037:             label: 'Fallout Cashout',
01038:             url: 'https://raw.githubusercontent.com/Conroy1988/missionchief-toolkit-assets/main/themes/fallout/audio/fallout-cashout.mp3'
01039:         }),
01040:         factorio: Object.freeze({
01041:             label: 'Factorio Cashout',
01042:             url: 'https://raw.githubusercontent.com/Conroy1988/missionchief-toolkit-assets/main/themes/factorio/audio/factorio-cashout.mp3'
01043:         }),
01044:         biohazard: Object.freeze({
01045:             label: 'Umbrella Containment Cashout',
01046:             url: 'https://raw.githubusercontent.com/Conroy1988/missionchief-toolkit-assets/main/themes/umbrella/audio/umbrella-containment-cashout.mp3'
01047:         }),
01048:         jamesBond: Object.freeze({
01049:             label: '007 Intelligence Cashout',
01050:             url: 'https://raw.githubusercontent.com/Conroy1988/missionchief-toolkit-assets/main/themes/james-bond/audio/james-bond-cashout.mp3'
01051:         }),
01052:         hyruleQuest: Object.freeze({
01053:             label: 'Hyrule Quest Reward',
01054:             url: 'https://raw.githubusercontent.com/Conroy1988/missionchief-toolkit-assets/main/themes/hyrule/audio/hyrule-quest-reward.mp3'
01055:         })
01056:     });
01057: 
01058:     const CORE_THEME_ORDER = ['default', 'control', 'incident', 'roads', 'urban', 'rural', 'nightshift'];
01059:     const SERVICE_THEME_ORDER = ['fireCommand', 'policeTactical', 'medicalControl', 'coastalCommand'];
01060:     const THEME_ORDER = [...CORE_THEME_ORDER, ...SERVICE_THEME_ORDER];
01061:     const PAYOUT_FLASH_MIN_MS = 2000;
01062:     const PAYOUT_FLASH_MAX_MS = 30000;
01063:     const PAYOUT_FLASH_STEP_MS = 2000;
01064:     const PAYOUT_HISTORY_LIMIT = 40;
01065:     const PAYOUT_MATCH_WINDOW_MS = 20000;
01066:     const CRITICAL_VIEW_MIN_AGE_MS = 8 * 60 * 60 * 1000;
01067:     const CRITICAL_AGE_FILTERS = Object.freeze({
01068:         all: Object.freeze({ label: 'ALL', minAgeMs: 0, sort: 'newest', summaryLabel: 'All Missions', title: 'Show every mission regardless of age · newest first' }),
01069:         '8h': Object.freeze({ label: '8H+', minAgeMs: 8 * 60 * 60 * 1000, sort: 'oldest', summaryLabel: '8H+ Missions', title: 'Show missions aged 8 hours or more · oldest first' }),
01070:         '16h': Object.freeze({ label: '16H+', minAgeMs: 16 * 60 * 60 * 1000, sort: 'oldest', summaryLabel: '16H+ Missions', title: 'Show missions aged 16 hours or more · oldest first' }),
01071:         '24h': Object.freeze({ label: '24H+', minAgeMs: 24 * 60 * 60 * 1000, sort: 'oldest', summaryLabel: '24H+ Missions', title: 'Show missions aged 24 hours or more · oldest first' })
01072:     });
01073:     const CRITICAL_AGE_FILTER_KEYS = Object.freeze(Object.keys(CRITICAL_AGE_FILTERS));
01074:     const CRITICAL_SORT_KEYS = Object.freeze(['age', 'closest', 'furthest']);
01075:     const CRITICAL_OWNERSHIP_KEYS = Object.freeze(['personal', 'alliance']);
01076:     const CRITICAL_OWNERSHIP_FILTER_KEYS = Object.freeze(['all', ...CRITICAL_OWNERSHIP_KEYS]);
01077:     const CRITICAL_CATEGORY_KEYS = Object.freeze(['standard', 'event', 'special']);
01078:     const CRITICAL_CATEGORY_FILTER_KEYS = Object.freeze(['all', ...CRITICAL_CATEGORY_KEYS]);
01079:     const CRITICAL_PRIMARY_STATUS_KEYS = Object.freeze(['all', 'attention', 'no-scene', 'assistance', 'clearing', 'on-scene']);
01080:     const CRITICAL_VALUE_MODE_KEYS = Object.freeze(['total', 'eligible']);
01081:     const CRITICAL_RENDER_BATCH_SIZE = 60;
01082:     const CRITICAL_PROGRESS_REFRESH_ACTIVE_MS = 30 * 1000;
01083:     const CRITICAL_PROGRESS_REFRESH_IDLE_MS = 90 * 1000;
01084:     const MISSION_AGE_LABEL_REFRESH_MS = 60 * 1000;
01085:     const MISSION_AGE_LABEL_RETRY_MS = 2500;
01086:     const STUCK_MIN_MINUTES = 5;
01087:     const STUCK_MAX_MINUTES = 180;
01088:     const MISSION_SPAWN_DURATION_MS = 2400;
01089:     const MAP_PROFILE_LIMIT = 5;
01090:     const MAJOR_INCIDENT_FEED_MINIMUM_OPTIONS = [10000, 25000, 50000, 100000];
01091:     const MAJOR_INCIDENT_FEED_MAX_ITEMS = 12;
01092:     const MAJOR_INCIDENT_MASS_CASUALTY_PATIENTS = 10;
01093:     const MAJOR_INCIDENT_MASS_CASUALTY_PRISONERS = 5;
01094:     const UK_POSTCODE_PATTERN = /\b(?:GIR\s?0AA|(?:(?:[A-PR-UWYZ][0-9][0-9A-HJKSTUW]?|[A-PR-UWYZ][A-HK-Y][0-9][0-9ABEHMNPRV-Y]?)\s?[0-9][ABD-HJLNP-UW-Z]{2}))\b/iu;
01095:     const VEHICLE_API_REFRESH_MS = 2 * 60 * 1000;
01096:     const VEHICLE_CODE_STATUS_DEFINITIONS = Object.freeze([
01097:         Object.freeze({ code: 1, label: 'Clear and Available' }),
01098:         Object.freeze({ code: 2, label: 'Available at Station' }),
01099:         Object.freeze({ code: 3, label: 'Responding' }),
01100:         Object.freeze({ code: 4, label: 'On Scene' }),
01101:         Object.freeze({ code: 5, label: 'Requesting Dispatch' }),
01102:         Object.freeze({ code: 6, label: 'Out of Service' }),
01103:         Object.freeze({ code: 7, label: 'Transporting' }),
01104:         Object.freeze({ code: 9, label: 'Awaiting Pickup' })
01105:     ]);
01106:     const VEHICLE_CODE_STATUS_BY_CODE = new Map(VEHICLE_CODE_STATUS_DEFINITIONS.map(item => [item.code, item]));
01107:     const VEHICLE_API_MIN_REFRESH_MS = 20 * 1000;
01108:     const DOM_REFRESH_DEBOUNCE_MS = 260;
01109:     const STARTUP_IDLE_TIMEOUT_MS = 2500;
01110:     const STARTUP_OPERATIONAL_DELAY_MS = 700;
01111:     const STARTUP_OBSERVER_DELAY_MS = 900;
01112:     const STARTUP_SETTLE_WINDOW_MS = 8000;
01113:     const STARTUP_MUTATION_DEBOUNCE_MS = 520;
01114:     const BUILDING_VISIBILITY_RECHECK_MS = 4000;
01115:     const MAP_DISCOVERY_RETRY_MS = 2000;
01116:     const FALLBACK_MISSION_REFRESH_MS = 15 * 1000;
01117:     const MISSION_PROGRESS_PAGE_REFRESH_MS = 30 * 1000;
01118:     const MARKER_REGISTRY_CACHE_MS = 350;
01119:     const PERSONAL_BUILDING_ID_CACHE_MS = 1200;
01120:     const MAP_ELEMENT_CACHE_MS = 750;
01121:     const MISSION_SNAPSHOT_REUSE_MS = 30000;
01122:     const RUNTIME_CACHE_PRUNE_MS = 60 * 1000;
01123:     const VEHICLE_API_ERROR_BACKOFF_MS = 60 * 1000;
01124:     const HEATMAP_SOURCE_CACHE_MS = 3000;
01125:     const MISSION_CACHE_RETENTION_MS = 10 * 60 * 1000;
01126:     const RESOURCE_GAP_REFRESH_MS = 15 * 1000;
01127:     const RESOURCE_GAP_RADIUS_OPTIONS = [10, 25, 50, 100];
01128:     const TRANSPORT_SWEEP_DELAY_OPTIONS = [1500, 2000, 2500, 3000, 4000, 5000];
01129:     const TRANSPORT_SWEEP_MAX_REQUESTS = 50;
01130:     const TRANSPORT_SWEEP_MAX_CANDIDATES_PER_MISSION = 40;
01131:     const LEGACY_THEME_MAP = { night: 'control', grey: 'urban', blue: 'nightshift', muted: 'rural', contrast: 'incident' };
01132:     const POSITIONS = {
01133:         tl: { label: 'Top left', short: 'TL' },
01134:         tr: { label: 'Top right', short: 'TR' },
01135:         bl: { label: 'Bottom left', short: 'BL' },
01136:         br: { label: 'Bottom right', short: 'BR' }
01137:     };
01138: 
01139:     const QUICK_PLACES = [
01140:         { id: 'edi', label: 'EDI', name: 'Edinburgh', lat: 55.9533, lng: -3.1883, zoom: 11 },
01141:         { id: 'fife', label: 'FIFE', name: 'Fife', lat: 56.2082, lng: -3.1495, zoom: 10 },
01142:         { id: 'glas', label: 'GLAS', name: 'Glasgow', lat: 55.8642, lng: -4.2518, zoom: 11 },
01143:         { id: 'dund', label: 'DUND', name: 'Dundee', lat: 56.4620, lng: -2.9707, zoom: 11 },
01144:         { id: 'stir', label: 'STIR', name: 'Stirling', lat: 56.1165, lng: -3.9369, zoom: 11 }
01145:     ];
01146: 
01147: 
01148:     const SMART_BOOKMARK_LABEL_MAX = 12;
01149:     const SMART_BOOKMARK_SINGLE_WORD_MAX = 5;
01150:     const SMART_BOOKMARK_WORDS = Object.freeze({
01151:         edinburgh: 'EDIN', glasgow: 'GLA', london: 'LDN', manchester: 'MAN', liverpool: 'LIV',
01152:         birmingham: 'BHM', newcastle: 'NCL', aberdeen: 'ABDN', dundee: 'DND', stirling: 'STIR',
```

## `function toggleFeature(`

### Match 1 · canonical line 27330

```javascript
27300:             item.style.setProperty('opacity', computed.opacity || '1', 'important');
27301:             item.style.setProperty('transform', computed.transform === 'none' ? 'none' : computed.transform, 'important');
27302:             item.style.setProperty('will-change', 'opacity, transform', 'important');
27303:             item.dataset.mcmsCollapseDelay = String(Math.min(index * stagger, 70));
27304:         });
27305:         void control.offsetWidth;
27306: 
27307:         runtimeRequestAnimationFrame(() => {
27308:             for (const item of animatedItems) {
27309:                 item.style.setProperty('transition', `opacity ${duration}ms cubic-bezier(.4,0,.2,1), transform ${duration}ms cubic-bezier(.4,0,.2,1)`, 'important');
27310:                 item.style.setProperty('transition-delay', `${item.dataset.mcmsCollapseDelay || 0}ms`, 'important');
27311:                 item.style.setProperty('opacity', '0', 'important');
27312:                 item.style.setProperty('transform', 'translateX(-10px) scale(.94)', 'important');
27313:                 delete item.dataset.mcmsCollapseDelay;
27314:             }
27315:         });
27316: 
27317:         commandBarAnimationTimer = runtimeSetTimeout(() => {
27318:             commandBarAnimationTimer = null;
27319:             state.commandBarOpen = false;
27320:             saveState();
27321:             updateUI();
27322:             fitControlToMap();
27323:             clearAnimationStyles();
27324:             commandBarAnimating = false;
27325:         }, duration + maxDelay + 25);
27326: 
27327:         showToast('Command bar collapsed');
27328:     }
27329: 
27330:     function toggleFeature(feature) {
27331:         if (feature === 'clean') state.cleanMode = !state.cleanMode;
27332:         if (feature === 'markerFocus') state.markerFocus = !state.markerFocus;
27333:         if (feature === 'missionPulse') state.missionPulse = !state.missionPulse;
27334:         if (feature === 'roadPriority') state.roadPriority = !state.roadPriority;
27335:         if (feature === 'coverage') state.coverage.enabled = !state.coverage.enabled;
27336:         if (feature === 'heatmap') state.heatmap.enabled = !state.heatmap.enabled;
27337:         if (feature === 'shortcuts') state.shortcuts = !state.shortcuts;
27338:         if (feature === 'autoLoadAllVehicles') {
27339:             state.autoLoadAllVehicles = !state.autoLoadAllVehicles;
27340:             if (state.autoLoadAllVehicles) installAutoLoadAllVehicles();
27341:             else stopAutoLoadAllVehicles();
27342:         }
27343:         if (feature === 'allianceBuildingsMapBlocker') state.allianceBuildingsMap = state.allianceBuildingsMap === false;
27344:         if (feature === 'majorIncidentFeed') state.majorIncidentFeed.enabled = !state.majorIncidentFeed.enabled;
27345:         if (feature === 'missionLockAudio') {
27346:             state.missionLockAudio = !state.missionLockAudio;
27347:             if (state.missionLockAudio) unlockPayoutAudio(true);
27348:         }
27349:         if (feature === 'allianceCredits') state.allianceCredits = !state.allianceCredits;
27350:         if (feature === 'missionAge') state.missionAge = !state.missionAge;
27351:         if (feature === 'unitCommitment') state.unitCommitment = !state.unitCommitment;
27352:         if (feature === 'transportWatcher') state.transportWatcher = !state.transportWatcher;
27353:         if (feature === 'missionInspector') state.missionInspector = !state.missionInspector;
27354:         if (feature === 'missionValue') state.missionValue = !state.missionValue;
27355:         if (feature === 'stuckDetector') state.stuckDetector.enabled = !state.stuckDetector.enabled;
27356:         if (feature === 'missionSpawn') state.missionSpawn.enabled = !state.missionSpawn.enabled;
27357:         if (feature === 'missionSpawn') {
27358:             missionSpawnArmed = false;
27359:             runtimeClearTimeout(missionSpawnPrimeTimer);
27360:             knownMissionIds.clear();
27361:             if (state.missionSpawn.enabled) primeMissionSpawnDetector();
27362:         }
27363:         if (feature === 'resourceGap') state.resourceGap.enabled = !state.resourceGap.enabled;
27364:         if (feature === 'criticalView') { toggleCriticalView(); return; }
27365:         if (feature === 'payoutFlash') state.payoutFlash.enabled = !state.payoutFlash.enabled;
27366:         if (feature === 'payoutSound') {
27367:             state.payoutFlash.soundEnabled = !state.payoutFlash.soundEnabled;
27368:             if (state.payoutFlash.soundEnabled) unlockPayoutAudio();
27369:             else disposePayoutMediaAudio();
27370:         }
27371:         if (feature === 'compactDock') state.compactDock = !state.compactDock;
27372:         if (feature === 'autoNight') {
27373:             state.autoNight.enabled = !state.autoNight.enabled;
27374:             state.autoNight.lastBucket = '';
27375:         }
27376:         if (feature === 'allianceMissions') state.visibility.allianceMissions = !state.visibility.allianceMissions;
27377:         if (feature === 'myMissions') state.visibility.myMissions = !state.visibility.myMissions;
27378:         if (feature === 'vehicles') state.visibility.vehicles = !state.visibility.vehicles;
27379:         if (feature === 'buildings') state.visibility.buildings = !state.visibility.buildings;
27380: 
27381:         if (state.cleanMode) closePanel();
27382: 
27383:         if (!criticalViewActive) saveState();
27384:         applyRootAttributes();
27385:         updateUI();
27386:         if (feature === 'vehicles') synchroniseVehicleMarkerClasses();
27387:         if (feature === 'buildings') synchronisePersonalBuildingVisibility();
27388:         if (state.economyMode && (feature === 'vehicles' || feature === 'buildings')) scheduleEconomyLayerSync(0);
27389:         reconcileFeatureRefreshes({ includeSnapshots: missionSnapshotsNeeded(), positionPanel: false });
27390:         if (feature === 'missionValue') {
27391:             if (state.missionValue) installMissionValueWindows();
27392:             else clearMissionValueIndicators();
27393:             showToast(state.missionValue ? 'Mission Value on' : 'Mission Value off');
27394:         }
27395:         if (feature === 'autoLoadAllVehicles') showToast(state.autoLoadAllVehicles ? 'Auto-load all vehicles on' : 'Auto-load all vehicles off');
27396:         if (feature === 'allianceCredits') showToast(state.allianceCredits ? 'Alliance credits on' : 'Alliance credits off');
27397:         if (feature === 'missionAge') showToast(state.missionAge ? 'Personal mission age on' : 'Personal mission age off');
27398:         if (feature === 'unitCommitment') {
27399:             if (state.unitCommitment) {
27400:                 showToast('Loading unit assignments…');
27401:                 refreshPersonalVehicleData(true).then(ok => {
27402:                     scheduleUnitCommitmentRefresh(0);
27403:                     showToast(ok ? 'Unit Count on' : 'Unit Count on · live vehicle data unavailable');
27404:                 });
27405:             } else showToast('Unit Count off');
27406:         }
27407:         if (feature === 'transportWatcher') showToast(state.transportWatcher ? 'Transport Watcher on' : 'Transport Watcher off');
27408:         if (feature === 'majorIncidentFeed') {
27409:             if (state.majorIncidentFeed.enabled) {
27410:                 refreshMissionSnapshots();
27411:                 scheduleMajorIncidentFeedRender(0);
27412:             } else removeMajorIncidentFeed();
27413:             showToast(state.majorIncidentFeed.enabled ? 'Major Incident Feed on' : 'Major Incident Feed off');
27414:         }
27415:         if (feature === 'missionLockAudio') showToast(state.missionLockAudio ? 'Mission tracking audio on' : 'Mission tracking audio off');
27416:         if (feature === 'allianceBuildingsMapBlocker') {
27417:             if (state.allianceBuildingsMap === false) {
27418:                 installAllianceBuildingsEarlyStyle();
27419:                 installAllianceBuildingsLeafletAssignmentGuard();
27420:                 installAllianceBuildingsContextWatcherEarly();
27421:             } else {
27422:                 clearAllianceBuildingsEarlyContext();
27423:             }
27424:             showToast(state.allianceBuildingsMap === false ? 'Alliance Map Blocker ON · reloading' : 'Alliance Map Blocker OFF · reloading');
27425:             if (isAllianceBuildingsContext()) runtimeSetTimeout(() => location.reload(), 180);
27426:         }
27427:         if (feature === 'missionInspector') showToast(state.missionInspector ? 'Mission Inspector on' : 'Mission Inspector off');
27428:         if (feature === 'stuckDetector') showToast(state.stuckDetector.enabled ? `Stuck detector on · ${state.stuckDetector.thresholdMin} min` : 'Stuck detector off');
27429:         if (feature === 'missionSpawn') showToast(state.missionSpawn.enabled ? 'New mission animation on' : 'New mission animation off');
27430:         if (feature === 'resourceGap') {
27431:             if (state.resourceGap.enabled) refreshPersonalVehicleData(false).then(() => { scheduleResourceGapRefresh(0); refreshVisibleMissionInspector(); });
27432:             showToast(state.resourceGap.enabled ? `Resource Gap on · ${state.resourceGap.radiusMi}mi` : 'Resource Gap off');
27433:         }
27434:         if (feature === 'payoutSound') showToast(state.payoutFlash.soundEnabled ? 'Theme audio on · hosted MP3 cues load only when played' : 'Theme audio off');
27435:         if (feature === 'payoutFlash') showToast(state.payoutFlash.enabled ? 'Emergency payout flash on' : 'Emergency payout flash off');
27436:         if (feature === 'autoNight') runAutoNight(true);
27437:     }
27438: 
27439:     function runAutoNight(force = false) {
27440:         if (!state.autoNight.enabled) return;
27441:         const bucket = isNightNow(state.autoNight.nightStart, state.autoNight.dayStart) ? 'night' : 'day';
27442:         if (!force && state.autoNight.lastBucket === bucket) return;
27443:         state.autoNight.lastBucket = bucket;
27444:         state.theme = bucket === 'night' ? normaliseTheme(state.autoNight.nightTheme) : normaliseTheme(state.autoNight.dayTheme);
27445:         saveState();
27446:         applyRootAttributes();
27447:         updateUI();
27448:     }
27449: 
27450:     function isNightNow(start, end) {
27451:         const now = new Date();
27452:         const current = now.getHours() * 60 + now.getMinutes();
27453:         const startMin = parseTime(start, 19 * 60);
27454:         const endMin = parseTime(end, 7 * 60);
27455:         if (startMin === endMin) return false;
27456:         if (startMin < endMin) return current >= startMin && current < endMin;
27457:         return current >= startMin || current < endMin;
27458:     }
27459: 
27460:     function parseTime(value, fallback) {
27461:         const match = String(value || '').match(/^(\d{1,2}):(\d{2})$/);
27462:         if (!match) return fallback;
27463:         return clamp(match[1], 0, 23, Math.floor(fallback / 60)) * 60 + clamp(match[2], 0, 59, fallback % 60);
27464:     }
27465: 
27466:     function shouldSuppressControl() {
27467:         if (state.cleanMode) return false;
27468:         if (document.body && document.body.classList.contains('modal-open')) return true;
27469: 
27470:         return SUPPRESSION_SELECTORS.some(selector => {
27471:             let nodes;
27472:             try { nodes = Array.from(document.querySelectorAll(selector)); } catch (err) { return false; }
27473:             return nodes.some(el => {
27474:                 if (!el || el.closest(`#${SCRIPT.controlId}`) || el.closest(`#${SCRIPT.panelId}`)) return false;
27475:                 if (!isVisible(el)) return false;
27476:                 const rect = el.getBoundingClientRect();
27477:                 return (rect.width * rect.height) > 1200;
27478:             });
27479:         });
27480:     }
27481: 
27482:     function refreshSuppression() {
27483:         const control = document.getElementById(SCRIPT.controlId);
27484:         if (!control) return;
27485:         control.classList.toggle('mcms-hidden-by-menu', shouldSuppressControl());
27486:     }
27487: 
27488:     function fitControlToMap() {
27489:         runtimeClearTimeout(fitTimer);
27490:         fitTimer = runtimeSetTimeout(() => {
27491:             const panel = document.getElementById(SCRIPT.panelId);
27492:             const mapEl = getLargestLeafletMap();
27493:             if (!mapEl) {
27494:                 if (!isTouchLayoutActive()) {
27495:                     observeDesktopPanelWorkspace(null);
27496:                     applyDesktopPanelSizing(panel, null);
27497:                 }
27498:                 return;
27499:             }
27500:             if (mobileModeActive) {
27501:                 clearDesktopPanelSizing(panel);
27502:                 applyMobileDockLayout(mapEl);
27503:             } else if (tabletModeActive) {
27504:                 clearDesktopPanelSizing(panel);
27505:                 applyTabletDockLayout(mapEl);
27506:             } else {
27507:                 clearTabletDockSizing();
27508:                 observeDesktopPanelWorkspace(mapEl);
27509:                 applyDesktopPanelSizing(panel, mapEl);
27510:             }
27511:             if (!panel) return;
27512:             const rect = mapEl.getBoundingClientRect();
27513:             panel.classList.toggle('mcms-map-small', rect.height < 560 || rect.width < 650);
27514:         }, 60);
27515:     }
27516: 
27517:     function setPanelCssPosition(left, top) {
27518:         const panel = document.getElementById(SCRIPT.panelId);
27519:         if (!panel) return;
27520:         if (isTouchLayoutActive()) { applyTabletPanelPosition(); return; }
27521:         clearTabletPanelSizing(panel);
27522:         panel.style.setProperty('position', 'fixed', 'important');
27523:         panel.style.setProperty('left', `${Math.round(left)}px`, 'important');
27524:         panel.style.setProperty('top', `${Math.round(top)}px`, 'important');
27525:         panel.style.setProperty('right', 'auto', 'important');
27526:         panel.style.setProperty('bottom', 'auto', 'important');
27527:         panel.style.setProperty('transform', 'none', 'important');
27528:     }
27529: 
27530:     function clampPanelPosition(left, top) {
27531:         const panel = document.getElementById(SCRIPT.panelId);
27532:         if (!panel) return { left: 12, top: 12 };
27533:         const mapEl = getLargestLeafletMap();
27534:         const bounds = applyDesktopPanelSizing(panel, mapEl) || resolveDesktopPanelBounds(null);
27535:         const panelWidth = Math.min(panel.offsetWidth || 318, Math.max(1, bounds.right - bounds.left));
27536:         const panelHeight = Math.min(panel.offsetHeight || 500, bounds.maxHeight);
27537:         return clampDesktopPanelPoint(left, top, panelWidth, panelHeight, bounds);
27538:     }
27539: 
27540:     function getDefaultPanelPosition() {
27541:         const control = document.getElementById(SCRIPT.controlId);
27542:         const panel = document.getElementById(SCRIPT.panelId);
27543:         const margin = 12;
27544:         if (!control || !panel) return { left: margin, top: margin };
27545: 
27546:         const controlRect = control.getBoundingClientRect();
27547:         const panelWidth = panel.offsetWidth || 318;
27548:         const viewportWidth = pageWindow.innerWidth || document.documentElement.clientWidth;
27549:         const spaceRight = viewportWidth - controlRect.right - margin;
27550:         const spaceLeft = controlRect.left - margin;
```

## `function handleAction(`

### Match 1 · canonical line 28625

```javascript
28595:         const entries = [];
28596:         for (const place of QUICK_PLACES) {
28597:             if (!state.quickPins[place.id]) continue;
28598:             entries.push({
28599:                 kind: 'quick',
28600:                 id: place.id,
28601:                 fullName: place.name,
28602:                 baseLabel: sanitiseBookmarkShortLabel(place.label) || makeSmartBookmarkLabel(place.name)
28603:             });
28604:         }
28605:         state.bookmarks.forEach((bookmark, index) => {
28606:             if (!bookmark || !bookmark.pinned) return;
28607:             entries.push({
28608:                 kind: 'bookmark',
28609:                 index,
28610:                 fullName: bookmark.name,
28611:                 baseLabel: bookmarkScreenLabel(bookmark)
28612:             });
28613:         });
28614: 
28615:         dock.innerHTML = resolveScreenPinLabels(entries).map(entry => {
28616:             const action = entry.kind === 'quick'
28617:                 ? `data-action="place-go" data-place="${escapeHtml(entry.id)}"`
28618:                 : `data-action="bookmark-go" data-slot="${entry.index}"`;
28619:             const className = entry.kind === 'quick' ? 'mcms-pin-quick' : 'mcms-pin-custom';
28620:             return `<button class="mcms-screen-pin-btn ${className}" type="button" ${action} data-full-label="${escapeHtml(entry.fullName)}" data-smart-label="${escapeHtml(entry.label)}" title="Jump to ${escapeHtml(entry.fullName)}" aria-label="Jump to ${escapeHtml(entry.fullName)}">${escapeHtml(entry.label)}</button>`;
28621:         }).join('');
28622:         if (isTouchLayoutActive()) fitControlToMap();
28623:     }
28624: 
28625:     function handleAction(button) {
28626:         const action = button.dataset.action;
28627:         if (action === 'place-go') {
28628:             const place = QUICK_PLACES.find(item => item.id === button.dataset.place);
28629:             if (place && setMapView(place.lat, place.lng, place.zoom)) showToast(place.name);
28630:             return;
28631:         }
28632:         if (action === 'quick-pin') { toggleQuickPin(button.dataset.place); return; }
28633:         if (action === 'bookmark-save') { saveBookmark(Number(button.dataset.slot)); return; }
28634:         if (action === 'bookmark-label') { editBookmarkLabel(Number(button.dataset.slot)); return; }
28635:         if (action === 'bookmark-go') { goBookmark(Number(button.dataset.slot)); return; }
28636:         if (action === 'bookmark-delete') { deleteBookmark(Number(button.dataset.slot)); return; }
28637:         if (action === 'bookmark-pin') { toggleBookmarkPin(Number(button.dataset.slot)); return; }
28638:         if (action === 'nudge-left') { nudgeControl(-4, 0); return; }
28639:         if (action === 'nudge-right') { nudgeControl(4, 0); return; }
28640:         if (action === 'nudge-up') { nudgeControl(0, -4); return; }
28641:         if (action === 'nudge-down') { nudgeControl(0, 4); return; }
28642:         if (action === 'nudge-reset') { resetNudge(); return; }
28643:         if (action === 'panel-left') { nudgePanel(-24, 0); return; }
28644:         if (action === 'panel-right') { nudgePanel(24, 0); return; }
28645:         if (action === 'panel-up') { nudgePanel(0, -24); return; }
28646:         if (action === 'panel-down') { nudgePanel(0, 24); return; }
28647:         if (action === 'open-help-center') { openHelpCenter(); return; }
28648:         if (action === 'toggle-economy') { setEconomyMode(!state.economyMode, true); return; }
28649:         if (action === 'open-critical-drawer') { toggleCriticalDrawer(); return; }
28650:         if (action === 'open-vehicle-status') { toggleVehicleCodeStatus(); return; }
28651:         if (action === 'fit-critical') { fitCriticalMissions(); return; }
28652:         if (action === 'scan-transport-sweep') { const queue = buildTransportSweepQueue(); showToast(queue.length ? `${queue.length} transport mission${queue.length === 1 ? '' : 's'} found` : 'No alliance patient transports found'); return; }
28653:         if (action === 'start-transport-sweep') { startTransportSweep(); return; }
28654:         if (action === 'stop-transport-sweep') { stopTransportSweep(); return; }
28655:         if (action === 'reset-session') { resetSessionPerformance(); return; }
28656:         if (action === 'clear-payout-history') { clearPayoutHistory(); return; }
28657:         if (action === 'critical-go') { focusMissionById(button.dataset.missionId, false); return; }
28658:         if (action === 'profile-save') { saveMapProfile(Number(button.dataset.slot)); return; }
28659:         if (action === 'profile-load') { loadMapProfile(Number(button.dataset.slot)); return; }
28660:         if (action === 'profile-delete') { deleteMapProfile(Number(button.dataset.slot)); return; }
28661:         if (action === 'export-config') { exportToolkitConfig(); return; }
28662:         if (action === 'import-config') { document.querySelector(`#${SCRIPT.panelId} [data-import-config-file]`)?.click?.(); return; }
28663:         if (action === 'reset-config') { resetToolkitConfiguration(); return; }
28664:         if (action === 'discord-test') { testDiscordWebhook(); return; }
28665:         if (action === 'discord-generate-post') { postDiscordFinancialReport(); return; }
28666:         if (action === 'discord-clear') { clearDiscordWebhook(); return; }
28667:         if (action === 'finance-archive-scan') { scanFinancialArchive(); return; }
28668:         if (action === 'finance-archive-cancel') { cancelFinancialArchiveScan(); return; }
28669:         if (action === 'finance-archive-export') { exportFinancialArchive(); return; }
28670:         if (action === 'finance-archive-import') { document.querySelector(`#${SCRIPT.panelId} [data-import-finance-file]`)?.click?.(); return; }
28671:         if (action === 'finance-archive-clear') { clearFinancialArchive(); return; }
28672:         if (action === 'finance-rules-refresh') { refreshFinancialIntelligenceFeeds(true).then(() => { renderFinanceVaultStatus(); showToast('GitHub financial intelligence refreshed'); }); return; }
28673:         if (action === 'test-payout-flash') {
28674:             const testAmount = Math.max(1000, Number(document.querySelector(`#${SCRIPT.panelId} [data-setting="payout-test-amount"]`)?.value) || state.payoutFlash.threshold);
28675:             const triggered = triggerPayoutFlash(testAmount, true, { source: 'personal', caption: 'Emergency Response Test' });
28676:             showToast(triggered ? 'Emergency flash test' : 'Emergency flash unavailable: map not detected');
28677:             return;
28678:         }
28679:         if (action === 'panel-reset') resetPanelPosition();
28680:     }
28681: 
28682:     function handleSettingChange(target) {
28683:         const setting = target.dataset.setting;
28684:         if (!setting) return;
28685: 
28686:         if (setting === 'mobile-mode' || setting === 'tablet-mode') {
28687:             const nextValue = ['auto', 'on', 'off'].includes(String(target.value)) ? String(target.value) : 'auto';
28688:             const previousLayout = activeDeviceLayout;
28689:             if (setting === 'mobile-mode') {
28690:                 state.mobileMode = nextValue;
28691:                 if (nextValue === 'on') state.tabletMode = 'off';
28692:             } else {
28693:                 state.tabletMode = nextValue;
28694:                 if (nextValue === 'on') state.mobileMode = 'off';
28695:             }
28696:             saveState();
28697:             applyRootAttributes();
28698:             refreshTabletModeUi();
28699:             if (previousLayout !== activeDeviceLayout && !isTouchLayoutActive()) {
28700:                 clearTabletPanelSizing();
28701:                 clearTabletDockSizing();
28702:             }
28703:             fitControlToMap();
28704:             positionPanelOverlay(true);
28705:             showToast(activeDeviceLayout === 'mobile' ? 'iOS Mobile Mode active' : activeDeviceLayout === 'tablet' ? 'Tablet Mode active' : 'Desktop layout active');
28706:             return;
28707:         }
28708: 
28709:         if (setting === 'major-incident-minimum') {
28710:             state.majorIncidentFeed.minimumCredits = MAJOR_INCIDENT_FEED_MINIMUM_OPTIONS.includes(Number(target.value)) ? Number(target.value) : 25000;
28711:             saveState();
28712:             updateUI();
28713:             refreshMissionSnapshots();
28714:             scheduleMajorIncidentFeedRender(0);
28715:             showToast(`Major Incident Feed: ${formatOperationalCompactCredits(state.majorIncidentFeed.minimumCredits)}+ credits`);
28716:             return;
28717:         }
28718: 
28719:         if (setting === 'coverage-radius') {
28720:             state.coverage.radiusMi = Number(target.value) || 10;
28721:             saveState();
28722:             updateUI();
28723:             scheduleCoverageRefresh();
28724:             return;
28725:         }
28726: 
28727:         if (setting === 'heatmap-source') state.heatmap.source = target.value === 'vehicles' ? 'vehicles' : 'stations';
28728:         if (setting === 'heatmap-service') state.heatmap.service = ['all', 'fire', 'ambulance', 'police', 'air', 'water'].includes(target.value) ? target.value : 'all';
28729:         if (setting === 'heatmap-radius') state.heatmap.radiusMi = Number(target.value) || 10;
28730:         if (setting === 'heatmap-opacity') state.heatmap.opacity = clamp(target.value, 0.12, 0.55, 0.30);
28731:         if (setting.startsWith('heatmap-')) {
28732:             saveState(); updateUI(); scheduleHeatmapRefresh(); return;
28733:         }
28734: 
28735: 
28736:         if (setting === 'transport-sweep-delay') {
28737:             state.transportSweep.delayMs = TRANSPORT_SWEEP_DELAY_OPTIONS.includes(Number(target.value)) ? Number(target.value) : 2000;
28738:             saveState(); updateUI();
28739:             showToast(`Transport Sweep delay: ${state.transportSweep.delayMs / 1000}s`);
28740:             return;
28741:         }
28742:         if (setting === 'transport-sweep-max') {
28743:             state.transportSweep.maxPerRun = Math.round(clamp(target.value, 1, TRANSPORT_SWEEP_MAX_REQUESTS, 25));
28744:             saveState(); updateUI();
28745:             showToast(`Transport Sweep maximum: ${state.transportSweep.maxPerRun}`);
28746:             return;
28747:         }
28748: 
28749:         if (setting === 'resource-gap-radius') {
28750:             state.resourceGap.radiusMi = RESOURCE_GAP_RADIUS_OPTIONS.includes(Number(target.value)) ? Number(target.value) : 25;
28751:             resourceGapAnalysisCache.clear();
28752:             saveState(); updateUI(); scheduleResourceGapRefresh(0); refreshVisibleMissionInspector();
28753:             showToast(`Resource Gap radius: ${state.resourceGap.radiusMi}mi`);
28754:             return;
28755:         }
28756: 
28757:         if (setting === 'stuck-threshold') {
28758:             state.stuckDetector.thresholdMin = Math.round(clamp(target.value, STUCK_MIN_MINUTES, STUCK_MAX_MINUTES, 20));
28759:             saveState();
28760:             updateUI();
28761:             scheduleStuckMissionRefresh(0);
28762:             showToast(`Stuck missions: ${state.stuckDetector.thresholdMin} minutes`);
28763:             return;
28764:         }
28765: 
28766:         if (setting === 'alliance-credit-minimum') {
28767:             state.allianceCreditMinimum = [0, 5000, 10000, 15000, 20000].includes(Number(target.value)) ? Number(target.value) : 0;
28768:             saveState();
28769:             updateUI();
28770:             scheduleAllianceCreditRefresh(0);
28771:             showToast(state.allianceCreditMinimum ? `Alliance credits: ${state.allianceCreditMinimum / 1000}K+` : 'Alliance credits: all values');
28772:             return;
28773:         }
28774: 
28775:         if (setting === 'discord-webhook') {
28776:             try {
28777:                 saveDiscordWebhookUrl(target.value);
28778:                 setDiscordStatus(target.value ? 'Webhook saved securely in Tampermonkey storage.' : 'Webhook removed.', 'good');
28779:             } catch (err) {
28780:                 setDiscordStatus(err?.message || 'Webhook URL is invalid.', 'bad');
28781:             }
28782:             return;
28783:         }
28784:         if (setting === 'discord-name') {
28785:             state.discordReport.webhookName = String(target.value || 'MissionChief Finance').trim().slice(0, 80) || 'MissionChief Finance';
28786:             saveState(); updateUI();
28787:             return;
28788:         }
28789:         if (setting === 'discord-top-categories') {
28790:             state.discordReport.topCategories = [3, 5, 8].includes(Number(target.value)) ? Number(target.value) : 5;
28791:             invalidateDiscordFinancialPreview();
28792:             saveState(); updateUI();
28793:             return;
28794:         }
28795:         if (setting === 'discord-period') {
28796:             state.discordReport.period = ['today', 'yesterday', 'last24', 'last7', 'last30', 'last90', 'last180', 'last365', 'allAvailable', 'session', 'sinceLast', 'custom'].includes(target.value) ? target.value : 'today';
28797:             invalidateDiscordFinancialPreview();
28798:             saveState(); updateUI();
28799:             return;
28800:         }
28801:         if (setting === 'discord-custom-start' || setting === 'discord-custom-end') {
28802:             const key = setting === 'discord-custom-start' ? 'customStart' : 'customEnd';
28803:             if (/^\d{4}-\d{2}-\d{2}$/u.test(String(target.value || ''))) state.discordReport[key] = String(target.value);
28804:             invalidateDiscordFinancialPreview();
28805:             saveState(); updateUI();
28806:             return;
28807:         }
28808:         if (setting === 'discord-comparison') {
28809:             state.discordReport.includeComparison = String(target.value) !== 'false';
28810:             invalidateDiscordFinancialPreview();
28811:             saveState(); updateUI();
28812:             return;
28813:         }
28814:         if (setting === 'discord-chart') {
28815:             state.discordReport.includeChart = String(target.value) !== 'false';
28816:             invalidateDiscordFinancialPreview();
28817:             saveState(); updateUI();
28818:             return;
28819:         }
28820: 
28821:         if (setting === 'discord-report-mode') {
28822:             state.discordReport.reportMode = ['executive', 'fullAudit'].includes(String(target.value)) ? String(target.value) : 'fullAudit';
28823:             invalidateDiscordFinancialPreview();
28824:             saveState(); updateUI();
28825:             return;
28826:         }
28827:         if (setting === 'discord-risk' || setting === 'discord-forecast') {
28828:             const key = setting === 'discord-risk' ? 'includeRisk' : 'includeForecast';
28829:             state.discordReport[key] = String(target.value) !== 'false';
28830:             invalidateDiscordFinancialPreview();
28831:             saveState(); updateUI();
28832:             return;
28833:         }
28834:         if (setting === 'finance-vault-enabled') {
28835:             state.financialVault.enabled = String(target.value) !== 'false';
28836:             saveState(); updateUI();
28837:             setFinanceVaultStatus(state.financialVault.enabled ? 'Local Financial Archive enabled.' : 'Local Financial Archive disabled; reports will scan MissionChief directly without retaining history.', 'neutral');
28838:             return;
28839:         }
28840:         if (setting === 'finance-vault-retention') {
28841:             state.financialVault.retentionDays = String(target.value) === 'all' ? 'all' : ([90, 180, 365, 730, 1825].includes(Number(target.value)) ? Number(target.value) : 'all');
28842:             saveState(); updateUI(); renderFinanceVaultStatus();
28843:             return;
28844:         }
28845:         if (setting === 'finance-rule-feed') {
```

## `function updateUI(`

### Match 1 · canonical line 28899

```javascript
28869:         }
28870:         if (setting === 'payout-duration') {
28871:             state.payoutFlash.durationMs = normalisePayoutFlashDuration(Number(target.value) * 1000);
28872:             saveState();
28873:             updateUI();
28874:             showToast(`Payout flash: ${state.payoutFlash.durationMs / 1000} seconds`);
28875:             return;
28876:         }
28877:         if (setting === 'payout-volume') {
28878:             state.payoutFlash.soundVolume = clamp(target.value, 0, 1, 0.35);
28879:             if (payoutMediaAudio && !payoutMediaAudio.paused) payoutMediaAudio.volume = state.payoutFlash.soundVolume;
28880:             saveState();
28881:             updateUI();
28882:             return;
28883:         }
28884:         if (setting === 'payout-test-amount') return;
28885: 
28886:         if (setting === 'auto-night-start') state.autoNight.nightStart = target.value || '19:00';
28887:         if (setting === 'auto-day-start') state.autoNight.dayStart = target.value || '07:00';
28888:         if (setting === 'auto-night-theme') state.autoNight.nightTheme = normaliseTheme(target.value);
28889:         if (setting === 'auto-day-theme') state.autoNight.dayTheme = normaliseTheme(target.value);
28890: 
28891:         if (setting.startsWith('auto-')) {
28892:             state.autoNight.lastBucket = '';
28893:             saveState();
28894:             runAutoNight(true);
28895:             updateUI();
28896:         }
28897:     }
28898: 
28899:     function updateUI() {
28900:         applyRootAttributes();
28901:         if (state.majorIncidentFeed.enabled && operationalStartupComplete) scheduleMajorIncidentFeedRender(40);
28902:         else if (!state.majorIncidentFeed.enabled) removeMajorIncidentFeed();
28903: 
28904:         const control = document.getElementById(SCRIPT.controlId);
28905:         const panel = document.getElementById(SCRIPT.panelId);
28906: 
28907:         if (control) {
28908:             for (const pos of Object.keys(POSITIONS)) control.classList.toggle(`mcms-pos-${pos}`, state.position === pos);
28909:             control.style.setProperty('--mcms-nudge-x', `${state.nudge.x}px`);
28910:             control.style.setProperty('--mcms-nudge-y', `${state.nudge.y}px`);
28911:             const controlToggleValues = {
28912:                 allianceMissions: state.visibility.allianceMissions,
28913:                 myMissions: state.visibility.myMissions,
28914:                 vehicles: state.visibility.vehicles,
28915:                 buildings: state.visibility.buildings,
28916:                 allianceCredits: state.allianceCredits,
28917:                 missionAge: state.missionAge,
28918:                 transportWatcher: state.transportWatcher,
28919:                 unitCommitment: state.unitCommitment,
28920:                 criticalView: criticalViewActive
28921:             };
28922:             control.querySelectorAll('[data-toggle]').forEach(btn => {
28923:                 const on = Boolean(controlToggleValues[btn.dataset.toggle]);
28924:                 btn.classList.toggle('mcms-on', on);
28925:                 btn.setAttribute('aria-pressed', String(on));
28926:                 btn.dataset.mcmsState = on ? 'on' : 'off';
28927:             });
28928: 
28929:             const vehicleStatusButton = control.querySelector('[data-action="open-vehicle-status"]');
28930:             if (vehicleStatusButton) {
28931:                 const open = Boolean(document.getElementById(SCRIPT.vehicleStatusId)?.classList?.contains('mcms-open'));
28932:                 vehicleStatusButton.classList.toggle('mcms-on', open);
28933:                 vehicleStatusButton.setAttribute('aria-pressed', String(open));
28934:                 vehicleStatusButton.dataset.mcmsState = open ? 'on' : 'off';
28935:             }
28936: 
28937:             const missionAgeWatchButton = control.querySelector('[data-action="open-critical-drawer"]');
28938:             if (missionAgeWatchButton) {
28939:                 const open = Boolean(document.getElementById(SCRIPT.criticalDrawerId)?.classList?.contains('mcms-open'));
28940:                 missionAgeWatchButton.classList.toggle('mcms-on', open);
28941:                 missionAgeWatchButton.setAttribute('aria-pressed', String(open));
28942:                 missionAgeWatchButton.dataset.mcmsState = open ? 'on' : 'off';
28943:             }
28944: 
28945:             const economyButton = control.querySelector('.mcms-economy-btn');
28946:             if (economyButton) {
28947:                 const on = Boolean(state.economyMode);
28948:                 const label = on ? 'Disable Economy Mode' : 'Enable Economy Mode';
28949:                 economyButton.classList.toggle('mcms-on', on);
28950:                 economyButton.setAttribute('aria-pressed', String(on));
28951:                 economyButton.setAttribute('aria-label', label);
28952:                 economyButton.title = label;
28953:                 economyButton.dataset.mcmsState = on ? 'on' : 'off';
28954:             }
28955: 
28956:             const dockToggleButton = control.querySelector('.mcms-dock-toggle-btn');
28957:             if (dockToggleButton) {
28958:                 const open = state.commandBarOpen !== false;
28959:                 const label = open ? 'Collapse command bar' : 'Expand command bar';
28960:                 dockToggleButton.classList.toggle('mcms-open', open);
28961:                 dockToggleButton.setAttribute('aria-expanded', String(open));
28962:                 dockToggleButton.setAttribute('aria-label', label);
28963:                 dockToggleButton.title = label;
28964:                 const icon = dockToggleButton.querySelector('.mcms-dock-toggle-icon');
28965:                 if (icon) icon.textContent = open ? '▴' : '▾';
28966:             }
28967:         }
28968: 
28969:         if (!panel) return;
28970: 
28971:         refreshTabletModeUi(panel);
28972:         panel.querySelectorAll('.mcms-tab-btn').forEach(btn => {
28973:             const active = btn.dataset.tab === state.activeTab;
28974:             btn.classList.toggle('mcms-active', active);
28975:             btn.setAttribute('aria-selected', String(active));
28976:             btn.tabIndex = active ? 0 : -1;
28977:         });
28978:         panel.querySelectorAll('.mcms-tab-panel').forEach(tabPanel => {
28979:             const active = tabPanel.dataset.panel === state.activeTab;
28980:             tabPanel.classList.toggle('mcms-active', active);
28981:             tabPanel.hidden = !active;
28982:         });
28983:         const panelOpen = panel.classList.contains('mcms-open');
28984:         panel.setAttribute('aria-hidden', String(!panelOpen));
28985:         control?.querySelector('.mcms-menu-btn')?.setAttribute('aria-expanded', String(panelOpen));
28986:         panel.querySelectorAll('.mcms-ui-theme-btn').forEach(btn => {
28987:             const active = btn.dataset.uiTheme === state.uiTheme;
28988:             btn.classList.toggle('mcms-active', active);
28989:             btn.setAttribute('aria-pressed', String(active));
28990:         });
28991:         panel.querySelectorAll('.mcms-theme-btn').forEach(btn => btn.classList.toggle('mcms-active', btn.dataset.theme === state.theme));
28992:         panel.querySelectorAll('.mcms-position-btn').forEach(btn => btn.classList.toggle('mcms-active', btn.dataset.position === state.position));
28993: 
28994:         const toggleValues = {
28995:             clean: state.cleanMode,
28996:             markerFocus: state.markerFocus,
28997:             missionPulse: state.missionPulse,
28998:             roadPriority: state.roadPriority,
28999:             coverage: state.coverage.enabled,
29000:             heatmap: state.heatmap.enabled,
29001:             shortcuts: state.shortcuts,
29002:             autoLoadAllVehicles: state.autoLoadAllVehicles,
29003:             allianceBuildingsMapBlocker: state.allianceBuildingsMap === false,
29004:             majorIncidentFeed: state.majorIncidentFeed.enabled,
29005:             missionLockAudio: state.missionLockAudio,
29006:             autoNight: state.autoNight.enabled,
29007:             payoutFlash: state.payoutFlash.enabled,
29008:             payoutSound: state.payoutFlash.soundEnabled,
29009:             missionInspector: state.missionInspector,
29010:             missionValue: state.missionValue,
29011:             stuckDetector: state.stuckDetector.enabled,
29012:             missionSpawn: state.missionSpawn.enabled,
29013:             resourceGap: state.resourceGap.enabled,
29014:             allianceMissions: state.visibility.allianceMissions,
29015:             myMissions: state.visibility.myMissions,
29016:             vehicles: state.visibility.vehicles,
29017:             buildings: state.visibility.buildings,
29018:             allianceCredits: state.allianceCredits,
29019:             missionAge: state.missionAge,
29020:             transportWatcher: state.transportWatcher,
29021:             unitCommitment: state.unitCommitment,
29022:             criticalView: criticalViewActive
29023:         };
29024: 
29025:         panel.querySelectorAll('[data-toggle]').forEach(btn => {
29026:             const key = btn.dataset.toggle;
29027:             const on = Boolean(toggleValues[key]);
29028:             btn.classList.toggle('mcms-on', on);
29029:             const pill = btn.querySelector('.mcms-pill');
29030:             if (pill) pill.textContent = key === 'coverage' ? (on ? `${state.coverage.radiusMi}mi` : 'OFF') : key === 'heatmap' ? (on ? `${state.heatmap.radiusMi}mi` : 'OFF') : (on ? 'ON' : 'OFF');
29031:         });
29032: 
29033:         const majorIncidentMinimum = panel.querySelector('[data-setting="major-incident-minimum"]');
29034:         if (majorIncidentMinimum) majorIncidentMinimum.value = String(state.majorIncidentFeed.minimumCredits);
29035:         const radius = panel.querySelector('[data-setting="coverage-radius"]');
29036:         if (radius) radius.value = String(state.coverage.radiusMi);
29037:         const heatmapSource = panel.querySelector('[data-setting="heatmap-source"]');
29038:         if (heatmapSource) heatmapSource.value = state.heatmap.source;
29039:         const heatmapService = panel.querySelector('[data-setting="heatmap-service"]');
29040:         if (heatmapService) heatmapService.value = state.heatmap.service;
29041:         const heatmapRadius = panel.querySelector('[data-setting="heatmap-radius"]');
29042:         if (heatmapRadius) heatmapRadius.value = String(state.heatmap.radiusMi);
29043:         const heatmapOpacity = panel.querySelector('[data-setting="heatmap-opacity"]');
29044:         if (heatmapOpacity) heatmapOpacity.value = String(state.heatmap.opacity);
29045:         const allianceCreditMinimum = panel.querySelector('[data-setting="alliance-credit-minimum"]');
29046:         if (allianceCreditMinimum) allianceCreditMinimum.value = String(state.allianceCreditMinimum);
29047:         const transportSweepDelay = panel.querySelector('[data-setting="transport-sweep-delay"]');
29048:         if (transportSweepDelay) transportSweepDelay.value = String(state.transportSweep.delayMs);
29049:         const transportSweepMax = panel.querySelector('[data-setting="transport-sweep-max"]');
29050:         if (transportSweepMax) transportSweepMax.value = String(state.transportSweep.maxPerRun);
29051:         if (panel.classList.contains('mcms-open') && state.activeTab === 'resources') renderTransportSweepPanel();
29052:         const payoutTemplate = panel.querySelector('[data-setting="payout-template"]');
29053:         if (payoutTemplate) payoutTemplate.value = state.payoutFlash.template;
29054:         const resourceGapRadius = panel.querySelector('[data-setting="resource-gap-radius"]'); if (resourceGapRadius) resourceGapRadius.value = String(state.resourceGap.radiusMi);
29055:         const stuckThreshold = panel.querySelector('[data-setting="stuck-threshold"]');
29056:         if (stuckThreshold) stuckThreshold.value = String(state.stuckDetector.thresholdMin);
29057:         const payoutThreshold = panel.querySelector('[data-setting="payout-threshold"]');
29058:         if (payoutThreshold) payoutThreshold.value = String(state.payoutFlash.threshold);
29059:         const payoutDuration = panel.querySelector('[data-setting="payout-duration"]');
29060:         if (payoutDuration) payoutDuration.value = String(state.payoutFlash.durationMs / 1000);
29061:         const payoutVolume = panel.querySelector('[data-setting="payout-volume"]');
29062:         if (payoutVolume) payoutVolume.value = String(state.payoutFlash.soundVolume);
29063:         const discordWebhook = panel.querySelector('[data-setting="discord-webhook"]');
29064:         if (discordWebhook && document.activeElement !== discordWebhook) discordWebhook.value = getDiscordWebhookUrl();
29065:         const discordName = panel.querySelector('[data-setting="discord-name"]');
29066:         if (discordName && document.activeElement !== discordName) discordName.value = state.discordReport.webhookName;
29067:         const discordTopCategories = panel.querySelector('[data-setting="discord-top-categories"]');
29068:         if (discordTopCategories) discordTopCategories.value = String(state.discordReport.topCategories);
29069:         const discordPeriod = panel.querySelector('[data-setting="discord-period"]');
29070:         if (discordPeriod) discordPeriod.value = state.discordReport.period;
29071:         const discordCustomStart = panel.querySelector('[data-setting="discord-custom-start"]');
29072:         if (discordCustomStart && document.activeElement !== discordCustomStart) discordCustomStart.value = state.discordReport.customStart;
29073:         const discordCustomEnd = panel.querySelector('[data-setting="discord-custom-end"]');
29074:         if (discordCustomEnd && document.activeElement !== discordCustomEnd) discordCustomEnd.value = state.discordReport.customEnd;
29075:         const discordComparison = panel.querySelector('[data-setting="discord-comparison"]');
29076:         if (discordComparison) discordComparison.value = String(state.discordReport.includeComparison);
29077:         const discordChart = panel.querySelector('[data-setting="discord-chart"]');
29078:         if (discordChart) discordChart.value = String(state.discordReport.includeChart);
29079:         const discordReportMode = panel.querySelector('[data-setting="discord-report-mode"]');
29080:         if (discordReportMode) discordReportMode.value = state.discordReport.reportMode;
29081:         const discordRisk = panel.querySelector('[data-setting="discord-risk"]');
29082:         if (discordRisk) discordRisk.value = String(state.discordReport.includeRisk);
29083:         const discordForecast = panel.querySelector('[data-setting="discord-forecast"]');
29084:         if (discordForecast) discordForecast.value = String(state.discordReport.includeForecast);
29085:         const financeVaultEnabled = panel.querySelector('[data-setting="finance-vault-enabled"]');
29086:         if (financeVaultEnabled) financeVaultEnabled.value = String(state.financialVault.enabled);
29087:         const financeVaultRetention = panel.querySelector('[data-setting="finance-vault-retention"]');
29088:         if (financeVaultRetention) financeVaultRetention.value = String(state.financialVault.retentionDays);
29089:         const financeRuleFeed = panel.querySelector('[data-setting="finance-rule-feed"]');
29090:         if (financeRuleFeed) financeRuleFeed.value = String(state.financialVault.ruleFeedEnabled);
29091:         setDiscordStatus(discordFinanceStatus, discordFinanceStatusTone);
29092:         if (panel.classList.contains('mcms-open') && state.activeTab === 'discord') renderFinanceVaultStatus();
29093:         const nightStart = panel.querySelector('[data-setting="auto-night-start"]');
29094:         if (nightStart) nightStart.value = state.autoNight.nightStart;
29095:         const dayStart = panel.querySelector('[data-setting="auto-day-start"]');
29096:         if (dayStart) dayStart.value = state.autoNight.dayStart;
29097:         const nightTheme = panel.querySelector('[data-setting="auto-night-theme"]');
29098:         if (nightTheme) nightTheme.value = state.autoNight.nightTheme;
29099:         const dayTheme = panel.querySelector('[data-setting="auto-day-theme"]');
29100:         if (dayTheme) dayTheme.value = state.autoNight.dayTheme;
29101:         const economyStatus = panel.querySelector('.mcms-economy-status');
29102:         if (economyStatus) economyStatus.textContent = state.economyMode
29103:             ? 'Economy Mode is ON: static visual effects, adaptive refresh intervals and off-screen vehicle/building layer culling are active.'
29104:             : 'Economy Mode is OFF. Use the leaf button beside the map-menu opener to reduce CPU, GPU and marker workload.';
29105:         const nudge = panel.querySelector('.mcms-nudge-value');
29106:         if (nudge) nudge.textContent = `X ${state.nudge.x} / Y ${state.nudge.y}`;
29107:         if (panel.classList.contains('mcms-open') && state.activeTab === 'settings') renderProfiles();
29108:         if ((panel.classList.contains('mcms-open') && state.activeTab === 'ops') || operationalUiIsVisible()) renderOperationalPanels();
29109:     }
29110: 
29111:     function ensureUi() {
29112:         const mapEl = getLargestLeafletMap();
29113:         if (settingsPanelActivated && !document.getElementById(SCRIPT.panelId)) createPanel();
29114:         if (mapEl) {
29115:             createControl(mapEl);
29116:             const map = findLeafletMapInstance(false);
29117:             if (state.economyMode && map) { applyLeafletEconomyPolicy(map); scheduleEconomyLayerSync(0); }
29118:             if (state.majorIncidentFeed.enabled && operationalStartupComplete) scheduleMajorIncidentFeedRender(0);
29119:             else if (!state.majorIncidentFeed.enabled) removeMajorIncidentFeed();
29120:             const payoutOverlay = document.getElementById(SCRIPT.payoutFlashId);
29121:             if (payoutOverlay?.classList.contains('mcms-payout-active')) positionPayoutFlashOverlay(payoutOverlay, mapEl);
29122:         }
29123:         return Boolean(mapEl && document.getElementById(SCRIPT.controlId));
29124:     }
29125: 
29126:     function mutationBelongsToToolkit(mutation) {
29127:         const target = mutation.target;
29128:         const toolkitTarget = Boolean(
29129:             target &&
29130:             target.nodeType === 1 &&
29131:             (
29132:                 target.id === SCRIPT.controlId ||
29133:                 target.id === SCRIPT.panelId ||
29134:                 target.id === SCRIPT.toastId ||
29135:                 target.id === SCRIPT.payoutFlashId ||
29136:                 target.id === SCRIPT.criticalDrawerId ||
29137:                 target.id === SCRIPT.vehicleStatusId ||
29138:                 target.id === SCRIPT.majorIncidentFeedId ||
29139:                 target.id === SCRIPT.missionInspectorId ||
```

## `function scanMissionValueWindows(`

### Match 1 · canonical line 21739

```javascript
21719:             mount.insertBefore(row, mount.firstChild || null);
21720:         }
21721: 
21722:         const fullLabel = `Mission Value · ${formatted}`;
21723:         const text = useToolbar ? presentation.text : fullLabel;
21724:         if (badge.textContent !== text) badge.textContent = text;
21725:         badge.title = `${fullLabel} · ${details.source}`;
21726:         badge.setAttribute('aria-label', fullLabel);
21727:         row.setAttribute('aria-label', fullLabel);
21728:         return row;
21729:     }
21730: 
21731:     function scheduleMissionValueScan(delay = 80) {
21732:         runtimeClearTimeout(missionValueScanTimer);
21733:         missionValueScanTimer = runtimeSetTimeout(() => {
21734:             missionValueScanTimer = null;
21735:             scanMissionValueWindows();
21736:         }, Math.max(0, Number(delay) || 0));
21737:     }
21738: 
21739:         function scanMissionValueWindows() {
21740:         if (!state.missionValue) {
21741:             clearMissionValueIndicators();
21742:             pruneMissionValueHostObservers(new Set());
21743:             return;
21744:         }
21745:         let needsRetry = false;
21746:         const activeRows = new Set();
21747:         const activeSpacers = new Set();
21748:         for (const candidate of missionValueWindowCandidates()) {
21749:             if (candidate.toolbarSpacer?.isConnected) activeSpacers.add(candidate.toolbarSpacer);
21750:             const renderedRow = syncMissionValueCandidate(candidate);
21751:             if (renderedRow) {
21752:                 activeRows.add(renderedRow);
21753:                 missionValueRetryState.delete(candidate.mount);
21754:                 continue;
21755:             }
21756:             const previous = missionValueRetryState.get(candidate.mount);
21757:             const attempts = previous?.missionId === candidate.missionId ? previous.attempts : 0;
21758:             if (attempts < 3) {
21759:                 missionValueRetryState.set(candidate.mount, { missionId: candidate.missionId, attempts: attempts + 1 });
21760:                 needsRetry = true;
21761:             }
21762:         }
21763:         for (const context of transportSweepDocumentContexts()) {
21764:             try {
21765:                 context.doc.querySelectorAll?.('.mcms-mission-value-row').forEach(row => {
21766:                     if (!activeRows.has(row)) row.remove();
21767:                 });
21768:             } catch (err) {}
21769:         }
21770:         pruneMissionValueHostObservers(activeSpacers);
21771:         if (needsRetry) runtimeSetTimeout(() => scheduleMissionValueScan(0), 650);
21772:     }
21773: 
21774:         function ensureMissionValueDocumentStyle(doc) {
21775:         if (!doc || doc === document) return;
21776:         const styleId = 'mcms-mission-value-document-style';
21777:         if (doc.getElementById?.(styleId)) return;
21778:         const style = doc.createElement?.('style');
21779:         if (!style) return;
21780:         style.id = styleId;
21781:         style.textContent = `
21782:             .mcms-mission-value-row{display:flex!important;align-items:center!important;justify-content:flex-end!important;min-width:0!important;box-sizing:border-box!important;position:relative!important;z-index:2!important;pointer-events:none!important}
21783:             #navbar-alarm-spacer>.mcms-mission-value-row,.mcms-mission-value-row[data-mcms-host="toolbar"]{flex:1 1 auto!important;width:100%!important;min-height:32px!important;margin:0!important;padding:0 3px 0 6px!important;clear:none!important;overflow:hidden!important}
21784:             .mcms-mission-value-row[data-mcms-host="fallback"]{width:100%!important;min-height:30px!important;margin:0 0 6px 0!important;padding:4px 8px!important;clear:both!important;overflow:hidden!important}
21785:             .mcms-mission-value-badge{display:inline-flex!important;align-items:center!important;justify-content:center!important;max-width:100%!important;min-width:0!important;min-height:24px!important;box-sizing:border-box!important;padding:4px 9px!important;border:1px solid rgba(235,190,64,.72)!important;border-radius:8px!important;background:linear-gradient(145deg,rgba(48,39,13,.96),rgba(19,21,24,.96))!important;color:#ffe59a!important;box-shadow:0 2px 8px rgba(0,0,0,.34)!important;font:900 11px/1.2 Arial,Helvetica,sans-serif!important;letter-spacing:.15px!important;text-align:right!important;white-space:nowrap!important;overflow:hidden!important;text-overflow:ellipsis!important;pointer-events:none!important}
21786:             .mcms-mission-value-row[data-mcms-mode="value"] .mcms-mission-value-badge{padding-left:7px!important;padding-right:7px!important}
21787:             @media(max-width:767px){.mcms-mission-value-row[data-mcms-host="fallback"]{padding:4px 6px!important}.mcms-mission-value-badge{font-size:10px!important}}
21788:         `;
21789:         (doc.head || doc.documentElement)?.appendChild(style);
21790:     }
21791: 
21792:     function clearMissionValueDocumentStyles() {
21793:         for (const context of transportSweepDocumentContexts()) {
21794:             if (context.doc === document) continue;
21795:             try { context.doc.getElementById?.('mcms-mission-value-document-style')?.remove(); } catch (err) {}
21796:         }
21797:     }
21798: 
21799:     function observeMissionValueFrame(frame) {
21800:         if (!frame || missionValueObservedFrames.has(frame)) return;
21801:         missionValueObservedFrames.add(frame);
21802:         const onLoad = () => scheduleMissionValueScan(40);
21803:         frame.addEventListener('load', onLoad);
21804:         runtimeOnCleanup(() => frame.removeEventListener('load', onLoad));
21805:     }
21806: 
21807:         function observeMissionValueDocument(doc) {
21808:         if (!doc) return;
21809:         ensureMissionValueDocumentStyle(doc);
21810:         if (missionValueObservedDocuments.has(doc)) return;
21811:         missionValueObservedDocuments.add(doc);
21812:         let frames = [];
21813:         try { frames = Array.from(doc.querySelectorAll('iframe, frame')); } catch (err) {}
21814:         frames.forEach(observeMissionValueFrame);
21815:         const root = doc.documentElement || doc.body;
21816:         if (!root) return;
21817:         const activitySelector = '#lightbox_box, #lightbox, .lightbox_content, .modal, [role="dialog"], .ui-dialog, iframe, frame, a[href*="/missions/"], form[action*="/missions/"], #navbar-alarm-spacer, #navbar-right-help-button, [id^="lssmv4-shareAlliancePost_alarm"], .navbar-header';
21818:         const observer = runtimeTrackObserver(new MutationObserver(mutations => {
21819:             const relevant = mutations.some(mutation => Array.from(mutation.addedNodes || []).concat(Array.from(mutation.removedNodes || [])).some(node => {
21820:                 if (node?.nodeType !== 1) return false;
21821:                 if (node.matches?.(activitySelector)) return true;
21822:                 return Boolean(node.querySelector?.(activitySelector));
21823:             }));
21824:             if (!relevant) return;
21825:             try { doc.querySelectorAll('iframe, frame').forEach(observeMissionValueFrame); } catch (err) {}
21826:             scheduleMissionValueScan(50);
21827:         }));
21828:         observer.observe(root, { childList: true, subtree: true });
21829:     }
21830: 
21831:     function installMissionValueWindows() {
21832:         if (!missionValueFeatureInstalled) {
21833:             missionValueFeatureInstalled = true;
21834:             runtimeOnCleanup(() => {
21835:                 runtimeClearTimeout(missionValueScanTimer);
21836:                 missionValueScanTimer = null;
21837:                 clearMissionValueIndicators();
21838:                 clearMissionValueDocumentStyles();
21839:             });
21840:         }
21841:         for (const context of transportSweepDocumentContexts()) observeMissionValueDocument(context.doc);
21842:         scheduleMissionValueScan(0);
21843:         runtimeSetTimeout(() => scheduleMissionValueScan(0), 180);
21844:         runtimeSetTimeout(() => scheduleMissionValueScan(0), 800);
21845:     }
21846: 
21847:     function criticalMissionValueForEntry(entry) {
21848:         return criticalMissionValueDetails(entry).value;
21849:     }
21850: 
21851:     function criticalValueEligible(entry) {
21852:         return selectedCriticalValueMode() === 'total' || Boolean(entry?.eligibleForCredits);
21853:     }
21854: 
21855:     function criticalValueGroup(entries, predicate = () => true) {
21856:         let total = 0;
21857:         let known = 0;
21858:         let unknown = 0;
21859:         let eligible = 0;
21860:         const seenMissionIds = new Set();
21861:         const sources = new Map();
21862:         for (const entry of entries) {
21863:             if (!predicate(entry) || !criticalValueEligible(entry)) continue;
21864:             const missionId = normaliseMissionId(entry?.missionId);
21865:             if (missionId !== null && seenMissionIds.has(missionId)) continue;
21866:             if (missionId !== null) seenMissionIds.add(missionId);
21867:             if (entry?.eligibleForCredits) eligible += 1;
21868:             const details = criticalMissionValueDetails(entry);
21869:             const value = details.value;
21870:             if (value === null || !Number.isFinite(Number(value))) {
21871:                 unknown += 1;
21872:                 continue;
21873:             }
21874:             total += Math.max(0, Number(value) || 0);
21875:             known += 1;
21876:             sources.set(details.source, (sources.get(details.source) || 0) + 1);
21877:         }
21878:         return { total: Math.round(total), known, unknown, eligible, count: seenMissionIds.size, sources };
21879:     }
21880: 
21881:     function criticalValueDisplay(group) {
21882:         if (!group?.known) return 'UNKNOWN';
21883:         return `≈${formatOperationalCompactCredits(group.total)} CR`;
21884:     }
21885: 
21886:     function criticalValueCoverage(group) {
21887:         return `${group.known.toLocaleString('en-GB')} / ${(group.known + group.unknown).toLocaleString('en-GB')} valued`;
21888:     }
21889: 
```

## `function observeMissionValueDocument(`

### Match 1 · canonical line 21807

```javascript
21787:             @media(max-width:767px){.mcms-mission-value-row[data-mcms-host="fallback"]{padding:4px 6px!important}.mcms-mission-value-badge{font-size:10px!important}}
21788:         `;
21789:         (doc.head || doc.documentElement)?.appendChild(style);
21790:     }
21791: 
21792:     function clearMissionValueDocumentStyles() {
21793:         for (const context of transportSweepDocumentContexts()) {
21794:             if (context.doc === document) continue;
21795:             try { context.doc.getElementById?.('mcms-mission-value-document-style')?.remove(); } catch (err) {}
21796:         }
21797:     }
21798: 
21799:     function observeMissionValueFrame(frame) {
21800:         if (!frame || missionValueObservedFrames.has(frame)) return;
21801:         missionValueObservedFrames.add(frame);
21802:         const onLoad = () => scheduleMissionValueScan(40);
21803:         frame.addEventListener('load', onLoad);
21804:         runtimeOnCleanup(() => frame.removeEventListener('load', onLoad));
21805:     }
21806: 
21807:         function observeMissionValueDocument(doc) {
21808:         if (!doc) return;
21809:         ensureMissionValueDocumentStyle(doc);
21810:         if (missionValueObservedDocuments.has(doc)) return;
21811:         missionValueObservedDocuments.add(doc);
21812:         let frames = [];
21813:         try { frames = Array.from(doc.querySelectorAll('iframe, frame')); } catch (err) {}
21814:         frames.forEach(observeMissionValueFrame);
21815:         const root = doc.documentElement || doc.body;
21816:         if (!root) return;
21817:         const activitySelector = '#lightbox_box, #lightbox, .lightbox_content, .modal, [role="dialog"], .ui-dialog, iframe, frame, a[href*="/missions/"], form[action*="/missions/"], #navbar-alarm-spacer, #navbar-right-help-button, [id^="lssmv4-shareAlliancePost_alarm"], .navbar-header';
21818:         const observer = runtimeTrackObserver(new MutationObserver(mutations => {
21819:             const relevant = mutations.some(mutation => Array.from(mutation.addedNodes || []).concat(Array.from(mutation.removedNodes || [])).some(node => {
21820:                 if (node?.nodeType !== 1) return false;
21821:                 if (node.matches?.(activitySelector)) return true;
21822:                 return Boolean(node.querySelector?.(activitySelector));
21823:             }));
21824:             if (!relevant) return;
21825:             try { doc.querySelectorAll('iframe, frame').forEach(observeMissionValueFrame); } catch (err) {}
21826:             scheduleMissionValueScan(50);
21827:         }));
21828:         observer.observe(root, { childList: true, subtree: true });
21829:     }
21830: 
21831:     function installMissionValueWindows() {
21832:         if (!missionValueFeatureInstalled) {
21833:             missionValueFeatureInstalled = true;
21834:             runtimeOnCleanup(() => {
21835:                 runtimeClearTimeout(missionValueScanTimer);
21836:                 missionValueScanTimer = null;
21837:                 clearMissionValueIndicators();
21838:                 clearMissionValueDocumentStyles();
21839:             });
21840:         }
21841:         for (const context of transportSweepDocumentContexts()) observeMissionValueDocument(context.doc);
21842:         scheduleMissionValueScan(0);
21843:         runtimeSetTimeout(() => scheduleMissionValueScan(0), 180);
21844:         runtimeSetTimeout(() => scheduleMissionValueScan(0), 800);
21845:     }
21846: 
21847:     function criticalMissionValueForEntry(entry) {
21848:         return criticalMissionValueDetails(entry).value;
21849:     }
21850: 
21851:     function criticalValueEligible(entry) {
21852:         return selectedCriticalValueMode() === 'total' || Boolean(entry?.eligibleForCredits);
21853:     }
21854: 
21855:     function criticalValueGroup(entries, predicate = () => true) {
21856:         let total = 0;
21857:         let known = 0;
21858:         let unknown = 0;
21859:         let eligible = 0;
21860:         const seenMissionIds = new Set();
21861:         const sources = new Map();
21862:         for (const entry of entries) {
21863:             if (!predicate(entry) || !criticalValueEligible(entry)) continue;
21864:             const missionId = normaliseMissionId(entry?.missionId);
21865:             if (missionId !== null && seenMissionIds.has(missionId)) continue;
21866:             if (missionId !== null) seenMissionIds.add(missionId);
21867:             if (entry?.eligibleForCredits) eligible += 1;
21868:             const details = criticalMissionValueDetails(entry);
21869:             const value = details.value;
21870:             if (value === null || !Number.isFinite(Number(value))) {
21871:                 unknown += 1;
21872:                 continue;
21873:             }
21874:             total += Math.max(0, Number(value) || 0);
21875:             known += 1;
21876:             sources.set(details.source, (sources.get(details.source) || 0) + 1);
21877:         }
21878:         return { total: Math.round(total), known, unknown, eligible, count: seenMissionIds.size, sources };
21879:     }
21880: 
21881:     function criticalValueDisplay(group) {
21882:         if (!group?.known) return 'UNKNOWN';
21883:         return `≈${formatOperationalCompactCredits(group.total)} CR`;
21884:     }
21885: 
21886:     function criticalValueCoverage(group) {
21887:         return `${group.known.toLocaleString('en-GB')} / ${(group.known + group.unknown).toLocaleString('en-GB')} valued`;
21888:     }
21889: 
21890:     function criticalValueTitle(label, group) {
21891:         const knownText = `${group.known.toLocaleString('en-GB')} valued mission${group.known === 1 ? '' : 's'}`;
21892:         const unknownText = group.unknown ? ` · ${group.unknown.toLocaleString('en-GB')} value${group.unknown === 1 ? '' : 's'} unavailable` : '';
21893:         return `${label}: approximately ${group.total.toLocaleString('en-GB')} credits from MissionChief average-credit data · ${knownText}${unknownText}`;
21894:     }
21895: 
21896:     function criticalValuesHtml(allEntries, visibleEntries) {
21897:         const scopedEntries = visibleEntries;
```

## `function connectMainMutationObserver(`

### Match 1 · canonical line 29401

```javascript
29381:             button.disabled = true;
29382:             button.textContent = 'Reloading…';
29383:             runtimeSetTimeout(() => location.reload(), 120);
29384:         }, true);
29385: 
29386:         runtimeOnCleanup(() => {
29387:             document.getElementById(ALLIANCE_BUILDINGS_MAP_NOTICE_ID)?.remove();
29388:             document.querySelectorAll('.mcms-alliance-buildings-map-column').forEach(element => element.classList.remove('mcms-alliance-buildings-map-column'));
29389:             document.querySelectorAll('.mcms-alliance-buildings-list-column').forEach(element => element.classList.remove('mcms-alliance-buildings-list-column'));
29390:             document.querySelectorAll('[data-mcms-alliance-map-column], [data-mcms-alliance-list-column]').forEach(element => {
29391:                 element.removeAttribute('data-mcms-alliance-map-column');
29392:                 element.removeAttribute('data-mcms-alliance-list-column');
29393:             });
29394:             document.documentElement?.removeAttribute('data-mcms-alliance-buildings-page');
29395:         });
29396: 
29397:         return initiallyInContext && !enabled;
29398:     }
29399: 
29400: 
29401:     function connectMainMutationObserver() {
29402:         if (!mainMutationObserver || runtime.destroyed || !document.body) return;
29403:         try { mainMutationObserver.disconnect(); } catch (err) {}
29404: 
29405:         const roots = new Set();
29406:         const mapElement = getLargestLeafletMap();
29407:         const mapRoot = mapElement?.closest?.('#map_outer') || mapElement?.parentElement || mapElement;
29408:         const missionRoot = document.querySelector('#missions, #mission_list, .missions-panel, .mission-list');
29409:         if (mapRoot?.isConnected) roots.add(mapRoot);
29410:         if (missionRoot?.isConnected) roots.add(missionRoot);
29411: 
29412:         if (!roots.size) {
29413:             mainMutationObserverFallbackActive = true;
29414:             mainMutationObserver.observe(document.body, { childList: true, subtree: true });
29415:             return;
29416:         }
29417: 
29418:         mainMutationObserverFallbackActive = false;
29419:         for (const root of roots) mainMutationObserver.observe(root, { childList: true, subtree: true });
29420:         mainMutationObserver.observe(document.body, { childList: true, subtree: false });
29421:     }
29422: 
29423:     async function runDeferredOperationalStartup() {
29424:         if (operationalStartupStarted || runtime.destroyed) return;
29425:         const operationalPerformanceStartedAt = startupClock();
29426:         if (document.hidden) {
29427:             runtimeSetTimeout(() => scheduleDeferredOperationalStartup(0), 1000);
29428:             return;
29429:         }
29430:         operationalStartupStarted = true;
29431: 
29432:         loadCachedFinancialRules();
29433:         loadCachedFinancialPolicy();
29434:         ensureFinanceVaultCredential(financePlayerIdentity());
29435:         scanInlineMissionMarkerData();
29436:         installMissionMarkerAddHook();
29437:         installRadioMessageHook();
29438:         if (state.missionValue) installMissionValueWindows();
29439: 
29440:         startupDataPassActive = true;
29441:         try {
29442:             if (vehicleDataNeeded()) await refreshPersonalVehicleData(true);
29443:         } finally {
29444:             startupDataPassActive = false;
29445:         }
29446: 
29447:         runtimeClearTimeout(missionSnapshotTimer);
29448:         missionSnapshotTimer = null;
29449:         if (missionSnapshotsNeeded()) refreshMissionSnapshots();
29450:         if (state.missionSpawn.enabled) primeMissionSpawnDetector();
29451:         if (state.stuckDetector.enabled) scheduleStuckMissionRefresh(180);
29452:         if (state.transportWatcher) scheduleTransportWatcherRefresh(220);
29453:         if (state.resourceGap.enabled) scheduleResourceGapRefresh(260);
29454:         if (state.unitCommitment) scheduleUnitCommitmentRefresh(300);
29455:         if (state.allianceCredits) scheduleAllianceCreditRefresh(320);
29456:         if (state.missionAge) scheduleMissionAgeRefresh(340);
29457: 
29458:         operationalStartupComplete = true;
29459:         scheduleOperationalPanelsRender(0);
29460:         if (state.majorIncidentFeed.enabled) scheduleMajorIncidentFeedRender(120);
29461:         scheduleEnabledMapRefreshes({ includeSnapshots: false, positionPanel: false, mapOnly: true });
29462:         recordStartupMetric('operationalStartupMs', operationalPerformanceStartedAt, { operationalStartupComplete: true });
29463: 
29464:     }
29465: 
29466:     function scheduleDeferredOperationalStartup(delay = STARTUP_OPERATIONAL_DELAY_MS) {
29467:         if (operationalStartupStarted || runtime.destroyed) return;
29468:         runtimeSetTimeout(() => runtimeRunWhenIdle(() => {
29469:             runDeferredOperationalStartup().catch(err => {
29470:                 operationalStartupComplete = true;
29471:                 startupDataPassActive = false;
29472:                 console.debug(`[${SCRIPT.name}] Deferred startup recovered after an operational initialisation error.`, err);
29473:                 connectMainMutationObserver();
29474:             });
29475:         }, STARTUP_IDLE_TIMEOUT_MS), Math.max(0, Number(delay) || 0));
29476:     }
29477: 
29478: 
29479:     const AUTO_LOAD_ALL_VEHICLES_SELECTOR = 'a.missing_vehicles_load[href*="/missing_vehicles"]';
29480:     const AUTO_LOAD_ALL_VEHICLES_MISSION_ROOT_SELECTOR = '#lightbox_box, #lightbox, .lightbox_content, .modal.show, .modal.in, .modal-content, [role="dialog"], .ui-dialog-content, .ui-dialog';
29481:     const AUTO_LOAD_ALL_VEHICLES_MAX_REQUESTS = 50;
29482:     const AUTO_LOAD_ALL_VEHICLES_SETTLE_MS = 180;
29483:     const AUTO_LOAD_ALL_VEHICLES_TIMEOUT_MS = 6000;
29484:     const AUTO_LOAD_ALL_VEHICLES_HIDDEN_RETRIES = 24;
29485:     let autoLoadAllVehiclesObserver = null;
29486:     let autoLoadAllVehiclesLinkObserver = null;
29487:     let autoLoadAllVehiclesRootObserver = null;
29488:     let autoLoadAllVehiclesScanTimer = null;
29489:     let autoLoadAllVehiclesReleaseTimer = null;
29490:     let autoLoadAllVehiclesMissionId = null;
29491:     let autoLoadAllVehiclesMissionRoot = null;
29492:     let autoLoadAllVehiclesActiveLink = null;
29493:     let autoLoadAllVehiclesActiveSignature = '';
29494:     let autoLoadAllVehiclesInFlight = false;
29495:     let autoLoadAllVehiclesRequestCount = 0;
29496:     let autoLoadAllVehiclesHiddenRetryCount = 0;
29497:     const autoLoadAllVehiclesRequestedPages = new Set();
29498: 
29499:     function autoLoadAllVehiclesLinkInfo(link) {
29500:         if (!link || link.nodeType !== 1 || !link.matches?.(AUTO_LOAD_ALL_VEHICLES_SELECTOR)) return null;
29501:         let url;
29502:         try { url = new URL(link.getAttribute('href') || link.href, location.href); } catch (err) { return null; }
29503:         if (url.origin !== location.origin) return null;
29504:         const match = url.pathname.match(/^\/missions\/(\d+)\/missing_vehicles\/?$/u);
29505:         if (!match) return null;
29506:         const rawOffset = url.searchParams.get('offset_page');
29507:         const offsetPage = Number.isFinite(Number(rawOffset)) ? Math.max(0, Number(rawOffset)) : 0;
29508:         return {
29509:             missionId: match[1],
29510:             offsetPage,
29511:             signature: `${match[1]}:${offsetPage}:${url.pathname}${url.search}`,
29512:             href: url.href
29513:         };
29514:     }
29515: 
29516:     function autoLoadAllVehiclesElementVisible(element) {
29517:         if (!element?.isConnected || element.hidden || element.getAttribute?.('aria-hidden') === 'true') return false;
29518:         if (element.matches?.(':disabled, .disabled, [aria-disabled="true"]')) return false;
29519:         try {
29520:             const style = pageWindow.getComputedStyle?.(element);
29521:             if (style?.display === 'none' || style?.visibility === 'hidden' || style?.visibility === 'collapse' || style?.pointerEvents === 'none' || Number(style?.opacity) === 0) return false;
29522:             const rect = element.getBoundingClientRect?.();
29523:             return !rect || (rect.width > 1 && rect.height > 1);
29524:         } catch (err) {
29525:             return true;
29526:         }
29527:     }
29528: 
29529:     function autoLoadAllVehiclesResolveMissionRoot(link) {
29530:         return link.closest?.(AUTO_LOAD_ALL_VEHICLES_MISSION_ROOT_SELECTOR) || link.parentElement || document.body;
29531:     }
29532: 
29533:     function autoLoadAllVehiclesCandidateLinks() {
29534:         if (!state.autoLoadAllVehicles) return [];
29535:         const queryRoot = autoLoadAllVehiclesMissionRoot?.isConnected && autoLoadAllVehiclesElementVisible(autoLoadAllVehiclesMissionRoot)
29536:             ? autoLoadAllVehiclesMissionRoot
29537:             : document;
29538:         return Array.from(queryRoot.querySelectorAll(AUTO_LOAD_ALL_VEHICLES_SELECTOR))
29539:             .reverse()
29540:             .map(link => ({ link, info: autoLoadAllVehiclesLinkInfo(link) }))
29541:             .filter(candidate => Boolean(candidate.info));
29542:     }
29543: 
29544:     function clearAutoLoadAllVehiclesReleaseTimer() {
29545:         runtimeClearTimeout(autoLoadAllVehiclesReleaseTimer);
29546:         autoLoadAllVehiclesReleaseTimer = null;
29547:     }
29548: 
29549:     function disconnectAutoLoadAllVehiclesLinkObserver() {
29550:         runtimeUntrackObserver(autoLoadAllVehiclesLinkObserver);
29551:         autoLoadAllVehiclesLinkObserver = null;
29552:     }
29553: 
29554:     function disconnectAutoLoadAllVehiclesRootObserver() {
29555:         runtimeUntrackObserver(autoLoadAllVehiclesRootObserver);
29556:         autoLoadAllVehiclesRootObserver = null;
29557:     }
29558: 
29559:     function releaseAutoLoadAllVehiclesRequest({ schedule = true } = {}) {
29560:         clearAutoLoadAllVehiclesReleaseTimer();
29561:         disconnectAutoLoadAllVehiclesLinkObserver();
29562:         autoLoadAllVehiclesInFlight = false;
29563:         autoLoadAllVehiclesActiveLink = null;
29564:         autoLoadAllVehiclesActiveSignature = '';
29565:         if (schedule && state.autoLoadAllVehicles) scheduleAutoLoadAllVehiclesScan(AUTO_LOAD_ALL_VEHICLES_SETTLE_MS);
29566:     }
29567: 
29568:     function resetAutoLoadAllVehiclesMission() {
29569:         releaseAutoLoadAllVehiclesRequest({ schedule: false });
29570:         disconnectAutoLoadAllVehiclesRootObserver();
29571:         autoLoadAllVehiclesMissionId = null;
29572:         autoLoadAllVehiclesMissionRoot = null;
29573:         autoLoadAllVehiclesRequestCount = 0;
29574:         autoLoadAllVehiclesHiddenRetryCount = 0;
29575:         autoLoadAllVehiclesRequestedPages.clear();
29576:     }
29577: 
29578:     function observeAutoLoadAllVehiclesRoot(root) {
29579:         disconnectAutoLoadAllVehiclesRootObserver();
29580:         if (!root || root === document.body) return;
29581:         const observer = runtimeTrackObserver(new MutationObserver(() => {
```

## `function scheduleDeferredOperationalStartup(`

### Match 1 · canonical line 29466

```javascript
29446: 
29447:         runtimeClearTimeout(missionSnapshotTimer);
29448:         missionSnapshotTimer = null;
29449:         if (missionSnapshotsNeeded()) refreshMissionSnapshots();
29450:         if (state.missionSpawn.enabled) primeMissionSpawnDetector();
29451:         if (state.stuckDetector.enabled) scheduleStuckMissionRefresh(180);
29452:         if (state.transportWatcher) scheduleTransportWatcherRefresh(220);
29453:         if (state.resourceGap.enabled) scheduleResourceGapRefresh(260);
29454:         if (state.unitCommitment) scheduleUnitCommitmentRefresh(300);
29455:         if (state.allianceCredits) scheduleAllianceCreditRefresh(320);
29456:         if (state.missionAge) scheduleMissionAgeRefresh(340);
29457: 
29458:         operationalStartupComplete = true;
29459:         scheduleOperationalPanelsRender(0);
29460:         if (state.majorIncidentFeed.enabled) scheduleMajorIncidentFeedRender(120);
29461:         scheduleEnabledMapRefreshes({ includeSnapshots: false, positionPanel: false, mapOnly: true });
29462:         recordStartupMetric('operationalStartupMs', operationalPerformanceStartedAt, { operationalStartupComplete: true });
29463: 
29464:     }
29465: 
29466:     function scheduleDeferredOperationalStartup(delay = STARTUP_OPERATIONAL_DELAY_MS) {
29467:         if (operationalStartupStarted || runtime.destroyed) return;
29468:         runtimeSetTimeout(() => runtimeRunWhenIdle(() => {
29469:             runDeferredOperationalStartup().catch(err => {
29470:                 operationalStartupComplete = true;
29471:                 startupDataPassActive = false;
29472:                 console.debug(`[${SCRIPT.name}] Deferred startup recovered after an operational initialisation error.`, err);
29473:                 connectMainMutationObserver();
29474:             });
29475:         }, STARTUP_IDLE_TIMEOUT_MS), Math.max(0, Number(delay) || 0));
29476:     }
29477: 
29478: 
29479:     const AUTO_LOAD_ALL_VEHICLES_SELECTOR = 'a.missing_vehicles_load[href*="/missing_vehicles"]';
29480:     const AUTO_LOAD_ALL_VEHICLES_MISSION_ROOT_SELECTOR = '#lightbox_box, #lightbox, .lightbox_content, .modal.show, .modal.in, .modal-content, [role="dialog"], .ui-dialog-content, .ui-dialog';
29481:     const AUTO_LOAD_ALL_VEHICLES_MAX_REQUESTS = 50;
29482:     const AUTO_LOAD_ALL_VEHICLES_SETTLE_MS = 180;
29483:     const AUTO_LOAD_ALL_VEHICLES_TIMEOUT_MS = 6000;
29484:     const AUTO_LOAD_ALL_VEHICLES_HIDDEN_RETRIES = 24;
29485:     let autoLoadAllVehiclesObserver = null;
29486:     let autoLoadAllVehiclesLinkObserver = null;
29487:     let autoLoadAllVehiclesRootObserver = null;
29488:     let autoLoadAllVehiclesScanTimer = null;
29489:     let autoLoadAllVehiclesReleaseTimer = null;
29490:     let autoLoadAllVehiclesMissionId = null;
29491:     let autoLoadAllVehiclesMissionRoot = null;
29492:     let autoLoadAllVehiclesActiveLink = null;
29493:     let autoLoadAllVehiclesActiveSignature = '';
29494:     let autoLoadAllVehiclesInFlight = false;
29495:     let autoLoadAllVehiclesRequestCount = 0;
29496:     let autoLoadAllVehiclesHiddenRetryCount = 0;
29497:     const autoLoadAllVehiclesRequestedPages = new Set();
29498: 
29499:     function autoLoadAllVehiclesLinkInfo(link) {
29500:         if (!link || link.nodeType !== 1 || !link.matches?.(AUTO_LOAD_ALL_VEHICLES_SELECTOR)) return null;
29501:         let url;
29502:         try { url = new URL(link.getAttribute('href') || link.href, location.href); } catch (err) { return null; }
29503:         if (url.origin !== location.origin) return null;
29504:         const match = url.pathname.match(/^\/missions\/(\d+)\/missing_vehicles\/?$/u);
29505:         if (!match) return null;
29506:         const rawOffset = url.searchParams.get('offset_page');
29507:         const offsetPage = Number.isFinite(Number(rawOffset)) ? Math.max(0, Number(rawOffset)) : 0;
29508:         return {
29509:             missionId: match[1],
29510:             offsetPage,
29511:             signature: `${match[1]}:${offsetPage}:${url.pathname}${url.search}`,
29512:             href: url.href
29513:         };
29514:     }
29515: 
29516:     function autoLoadAllVehiclesElementVisible(element) {
29517:         if (!element?.isConnected || element.hidden || element.getAttribute?.('aria-hidden') === 'true') return false;
29518:         if (element.matches?.(':disabled, .disabled, [aria-disabled="true"]')) return false;
29519:         try {
29520:             const style = pageWindow.getComputedStyle?.(element);
29521:             if (style?.display === 'none' || style?.visibility === 'hidden' || style?.visibility === 'collapse' || style?.pointerEvents === 'none' || Number(style?.opacity) === 0) return false;
29522:             const rect = element.getBoundingClientRect?.();
29523:             return !rect || (rect.width > 1 && rect.height > 1);
29524:         } catch (err) {
29525:             return true;
29526:         }
29527:     }
29528: 
29529:     function autoLoadAllVehiclesResolveMissionRoot(link) {
29530:         return link.closest?.(AUTO_LOAD_ALL_VEHICLES_MISSION_ROOT_SELECTOR) || link.parentElement || document.body;
29531:     }
29532: 
29533:     function autoLoadAllVehiclesCandidateLinks() {
29534:         if (!state.autoLoadAllVehicles) return [];
29535:         const queryRoot = autoLoadAllVehiclesMissionRoot?.isConnected && autoLoadAllVehiclesElementVisible(autoLoadAllVehiclesMissionRoot)
29536:             ? autoLoadAllVehiclesMissionRoot
29537:             : document;
29538:         return Array.from(queryRoot.querySelectorAll(AUTO_LOAD_ALL_VEHICLES_SELECTOR))
29539:             .reverse()
29540:             .map(link => ({ link, info: autoLoadAllVehiclesLinkInfo(link) }))
29541:             .filter(candidate => Boolean(candidate.info));
29542:     }
29543: 
29544:     function clearAutoLoadAllVehiclesReleaseTimer() {
29545:         runtimeClearTimeout(autoLoadAllVehiclesReleaseTimer);
29546:         autoLoadAllVehiclesReleaseTimer = null;
29547:     }
29548: 
29549:     function disconnectAutoLoadAllVehiclesLinkObserver() {
29550:         runtimeUntrackObserver(autoLoadAllVehiclesLinkObserver);
29551:         autoLoadAllVehiclesLinkObserver = null;
29552:     }
29553: 
29554:     function disconnectAutoLoadAllVehiclesRootObserver() {
29555:         runtimeUntrackObserver(autoLoadAllVehiclesRootObserver);
29556:         autoLoadAllVehiclesRootObserver = null;
29557:     }
29558: 
29559:     function releaseAutoLoadAllVehiclesRequest({ schedule = true } = {}) {
29560:         clearAutoLoadAllVehiclesReleaseTimer();
29561:         disconnectAutoLoadAllVehiclesLinkObserver();
29562:         autoLoadAllVehiclesInFlight = false;
29563:         autoLoadAllVehiclesActiveLink = null;
29564:         autoLoadAllVehiclesActiveSignature = '';
29565:         if (schedule && state.autoLoadAllVehicles) scheduleAutoLoadAllVehiclesScan(AUTO_LOAD_ALL_VEHICLES_SETTLE_MS);
29566:     }
29567: 
29568:     function resetAutoLoadAllVehiclesMission() {
29569:         releaseAutoLoadAllVehiclesRequest({ schedule: false });
29570:         disconnectAutoLoadAllVehiclesRootObserver();
29571:         autoLoadAllVehiclesMissionId = null;
29572:         autoLoadAllVehiclesMissionRoot = null;
29573:         autoLoadAllVehiclesRequestCount = 0;
29574:         autoLoadAllVehiclesHiddenRetryCount = 0;
29575:         autoLoadAllVehiclesRequestedPages.clear();
29576:     }
29577: 
29578:     function observeAutoLoadAllVehiclesRoot(root) {
29579:         disconnectAutoLoadAllVehiclesRootObserver();
29580:         if (!root || root === document.body) return;
29581:         const observer = runtimeTrackObserver(new MutationObserver(() => {
29582:             if (!state.autoLoadAllVehicles) return;
29583:             if (!root.isConnected || !autoLoadAllVehiclesElementVisible(root)) {
29584:                 resetAutoLoadAllVehiclesMission();
29585:                 return;
29586:             }
29587:             scheduleAutoLoadAllVehiclesScan(AUTO_LOAD_ALL_VEHICLES_SETTLE_MS);
29588:         }));
29589:         observer.observe(root, {
29590:             attributes: true,
29591:             attributeFilter: ['class', 'style', 'hidden', 'aria-hidden']
29592:         });
29593:         autoLoadAllVehiclesRootObserver = observer;
29594:     }
29595: 
29596:     function observeAutoLoadAllVehiclesLink(link) {
29597:         disconnectAutoLoadAllVehiclesLinkObserver();
29598:         if (!link) return;
29599:         const observer = runtimeTrackObserver(new MutationObserver(() => {
29600:             if (!state.autoLoadAllVehicles) return;
29601:             const info = autoLoadAllVehiclesLinkInfo(link);
29602:             const changed = Boolean(info && info.signature !== autoLoadAllVehiclesActiveSignature);
29603:             if (!link.isConnected || !info || !autoLoadAllVehiclesElementVisible(link) || changed) {
29604:                 releaseAutoLoadAllVehiclesRequest({ schedule: true });
29605:             }
29606:         }));
29607:         observer.observe(link, {
29608:             attributes: true,
29609:             attributeFilter: ['href', 'class', 'style', 'hidden', 'aria-hidden', 'aria-disabled']
29610:         });
29611:         autoLoadAllVehiclesLinkObserver = observer;
29612:     }
29613: 
29614:     function scheduleAutoLoadAllVehiclesScan(delay = 0) {
29615:         if (!state.autoLoadAllVehicles || runtime.destroyed) return;
29616:         runtimeClearTimeout(autoLoadAllVehiclesScanTimer);
29617:         autoLoadAllVehiclesScanTimer = runtimeSetTimeout(() => {
29618:             autoLoadAllVehiclesScanTimer = null;
29619:             scanAutoLoadAllVehicles();
29620:         }, Math.max(0, Number(delay) || 0));
29621:     }
29622: 
29623:     function scanAutoLoadAllVehicles() {
29624:         if (!state.autoLoadAllVehicles || runtime.destroyed || autoLoadAllVehiclesInFlight) return false;
29625:         const candidates = autoLoadAllVehiclesCandidateLinks();
29626:         if (!candidates.length) {
29627:             autoLoadAllVehiclesHiddenRetryCount = 0;
29628:             if (autoLoadAllVehiclesMissionRoot && (!autoLoadAllVehiclesMissionRoot.isConnected || !autoLoadAllVehiclesElementVisible(autoLoadAllVehiclesMissionRoot))) {
29629:                 resetAutoLoadAllVehiclesMission();
29630:             }
29631:             return false;
29632:         }
29633: 
29634:         const visibleCandidates = candidates.filter(candidate => autoLoadAllVehiclesElementVisible(candidate.link));
29635:         if (!visibleCandidates.length) {
29636:             if (autoLoadAllVehiclesHiddenRetryCount < AUTO_LOAD_ALL_VEHICLES_HIDDEN_RETRIES) {
29637:                 autoLoadAllVehiclesHiddenRetryCount += 1;
29638:                 scheduleAutoLoadAllVehiclesScan(AUTO_LOAD_ALL_VEHICLES_SETTLE_MS);
29639:             }
29640:             return false;
29641:         }
29642:         autoLoadAllVehiclesHiddenRetryCount = 0;
29643: 
29644:         const candidate = visibleCandidates.find(item => item.info.missionId !== autoLoadAllVehiclesMissionId || !autoLoadAllVehiclesRequestedPages.has(item.info.signature)) || visibleCandidates[0];
29645:         const { link, info } = candidate;
29646:         const missionRoot = autoLoadAllVehiclesResolveMissionRoot(link);
```

## `function startBootAttemptCoordinator(`

### Match 1 · canonical line 29735

```javascript
29715:         }
29716:         if (!autoLoadAllVehiclesObserver) {
29717:             const observer = runtimeTrackObserver(new MutationObserver(mutations => {
29718:                 if (!state.autoLoadAllVehicles) return;
29719:                 if (autoLoadAllVehiclesMissionRoot && !autoLoadAllVehiclesMissionRoot.isConnected) {
29720:                     resetAutoLoadAllVehiclesMission();
29721:                 }
29722:                 if (autoLoadAllVehiclesActiveLink && !autoLoadAllVehiclesActiveLink.isConnected) {
29723:                     releaseAutoLoadAllVehiclesRequest({ schedule: false });
29724:                 }
29725:                 if (mutations.some(autoLoadAllVehiclesMutationRelevant)) scheduleAutoLoadAllVehiclesScan(AUTO_LOAD_ALL_VEHICLES_SETTLE_MS);
29726:             }));
29727:             observer.observe(document.body, { childList: true, subtree: true });
29728:             autoLoadAllVehiclesObserver = observer;
29729:         }
29730:         scheduleAutoLoadAllVehiclesScan(0);
29731:         return true;
29732:     }
29733: 
29734: 
29735:     function startBootAttemptCoordinator(bootPerformanceStartedAt) {
29736:         let attempts = 0;
29737:         const runBootAttempt = () => {
29738:             attempts += 1;
29739:             installMissionMarkerAddHook();
29740:             installRadioMessageHook();
29741:             installCreditsUpdateHook();
29742:             observeCreditValue();
29743:             const ready = ensureUi();
29744:             const mapReady = Boolean(getLargestLeafletMap());
29745:             if (ready && (mapReady || attempts >= 12)) {
29746:                 recordStartupMetric('coreUiReadyMs', bootPerformanceStartedAt, { bootAttempts: attempts });
29747:                 scheduleMarkerStateSync(0, false);
29748:                 scheduleDeferredOperationalStartup();
29749:                 runtimeSetTimeout(() => runtimeRunWhenIdle(connectMainMutationObserver, STARTUP_OBSERVER_DELAY_MS), STARTUP_OBSERVER_DELAY_MS);
29750:                 return;
29751:             }
29752:             if (attempts >= 90 || runtime.destroyed) return;
29753:             const delay = attempts < 12 ? 350 : attempts < 30 ? 700 : 1400;
29754:             runtimeSetTimeout(runBootAttempt, delay);
29755:         };
29756:         runtimeSetTimeout(runBootAttempt, 250);
29757:     }
29758: 
29759:     function boot() {
29760:         if (runtime.destroyed || bootStarted) return;
29761:         bootStarted = true;
29762:         bootStartedAt = Date.now();
29763:         const bootPerformanceStartedAt = startupClock();
29764:         applyRootAttributes();
29765:         if (installAllianceBuildingsPageOptimisation()) return;
29766:         createCleanExit();
29767:         if (state.autoLoadAllVehicles) installAutoLoadAllVehicles();
29768:         installMissionMarkerAddHook();
29769:         installRadioMessageHook();
29770:         lastObservedCredits = readCurrentCreditTotal();
29771:         installCreditsUpdateHook();
29772:         observeCreditValue();
29773: 
29774:         startBootAttemptCoordinator(bootPerformanceStartedAt);
29775: 
29776:         const observer = runtimeTrackObserver(new MutationObserver(mutations => {
29777:             if (state.economyMode && economyMapMoving) {
29778:                 economyDeferredDomMutation = true;
29779:                 return;
29780:             }
29781:             let externalMutationFound = false;
29782:             let addedLeafletMarker = false;
29783:             let missionChanged = false;
29784:             let layoutChanged = false;
29785:             let toolkitUiRemoved = false;
29786:             for (const mutation of mutations) {
29787:                 if (mutationBelongsToToolkit(mutation)) continue;
29788:                 externalMutationFound = true;
29789:                 if (!addedLeafletMarker && mutationAddsLeafletMarkerIcon(mutation)) {
29790:                     addedLeafletMarker = true;
29791:                     missionChanged = true;
29792:                 }
29793:                 if (!missionChanged && mutationAffectsMissionData(mutation)) missionChanged = true;
29794:                 if (!layoutChanged && mutationAffectsMapLayout(mutation)) layoutChanged = true;
29795:                 if (!toolkitUiRemoved && mutationRemovesToolkitUi(mutation)) toolkitUiRemoved = true;
29796:                 if (addedLeafletMarker && missionChanged && layoutChanged && toolkitUiRemoved) break;
29797:             }
29798:             if (!externalMutationFound) return;
29799:             missionChanged ||= addedLeafletMarker;
29800:             if (!missionChanged && !layoutChanged && !toolkitUiRemoved) return;
29801: 
29802:             if (addedLeafletMarker) {
29803:                 invalidateMarkerRegistryCaches('all');
29804:                 scheduleMarkerStateSync(0, false);
29805:                 if (!state.visibility.buildings) scheduleMarkerStateSync(180, true);
29806:             }
29807:             if (layoutChanged) invalidateMapElementCache();
29808:             if (document.hidden || dragState || (state.economyMode && economyMapMoving)) return;
29809: 
29810:             runtimeClearTimeout(mutationTimer);
29811:             const startupSettling = bootStartedAt > 0 && Date.now() - bootStartedAt < STARTUP_SETTLE_WINDOW_MS;
29812:             const mutationDelay = startupSettling
29813:                 ? STARTUP_MUTATION_DEBOUNCE_MS
29814:                 : (state.economyMode ? Math.max(320, DOM_REFRESH_DEBOUNCE_MS) : DOM_REFRESH_DEBOUNCE_MS);
29815:             mutationTimer = runtimeSetTimeout(() => {
29816:                 if (dragState || document.hidden || runtime.destroyed || (state.economyMode && economyMapMoving)) return;
29817:                 const panelMissing = settingsPanelActivated && !document.getElementById(SCRIPT.panelId);
29818:                 const mapElement = getLargestLeafletMap();
29819:                 const controlMissing = Boolean(mapElement && !document.getElementById(SCRIPT.controlId));
29820:                 if (toolkitUiRemoved || panelMissing || controlMissing) ensureUi();
29821:                 if (mainMutationObserverFallbackActive && (mapElement || document.querySelector('#missions, #mission_list, .missions-panel, .mission-list'))) {
29822:                     connectMainMutationObserver();
29823:                 }
29824:                 if (layoutChanged) {
29825:                     refreshSuppression();
29826:                     fitControlToMap();
29827:                     schedulePanelPosition(true, 50);
29828:                     scheduleCriticalDrawerDock(60);
29829:                 }
29830:                 if (missionChanged) scheduleEnabledMapRefreshes({ includeSnapshots: missionSnapshotsNeeded(), positionPanel: false });
29831:             }, mutationDelay);
29832:         }));
29833:         mainMutationObserver = observer;
29834: 
29835:         runtimeListen(document, 'keydown', handleKeyboard);
29836:         runtimeListen(document, 'pointerover', handleMissionInspectorPointerOver, true);
29837:         runtimeListen(document, 'pointermove', handleMissionInspectorPointerMove, true);
29838:         runtimeListen(document, 'pointerout', handleMissionInspectorPointerOut, true);
29839:         runtimeListen(document, 'pointerdown', () => unlockPayoutAudio(), { once: true, capture: true });
29840:         runtimeListen(document, 'click', event => {
29841:             runtimeSetTimeout(refreshSuppression, 0);
29842:             if (suppressNextOutsideClick) {
29843:                 event.preventDefault();
29844:                 event.stopPropagation();
29845:                 suppressNextOutsideClick = false;
29846:                 return;
29847:             }
29848: 
29849:             const control = document.getElementById(SCRIPT.controlId);
29850:             const panel = document.getElementById(SCRIPT.panelId);
29851:             if (!panel || !panel.classList.contains('mcms-open')) return;
29852:             if (control && control.contains(event.target)) return;
29853:             if (panel.contains(event.target)) return;
29854:             closePanel();
29855:         }, true);
29856: 
29857:         runtimeListen(pageWindow, 'resize', () => {
29858:             invalidateMapElementCache();
29859:             applyRootAttributes();
29860:             refreshTabletModeUi();
29861:             scheduleTabletLayoutRefresh(20);
29862:             const payoutOverlay = document.getElementById(SCRIPT.payoutFlashId);
29863:             if (payoutOverlay?.classList.contains('mcms-payout-active')) positionPayoutFlashOverlay(payoutOverlay);
29864:             if (dragState) return;
29865:             refreshSuppression();
29866:             fitControlToMap();
29867:             schedulePanelPosition(true, 40);
29868:             scheduleCriticalDrawerDock(30);
29869:             scheduleEnabledMapRefreshes({ includeSnapshots: false, positionPanel: false, mapOnly: true });
29870:             scheduleMajorIncidentFeedLayout();
29871:         });
29872: 
29873:         runtimeListen(pageWindow, 'scroll', scheduleMajorIncidentFeedLayout, { passive: true });
29874:         runtimeListen(pageWindow, 'orientationchange', () => scheduleTabletLayoutRefresh(30));
29875:         if (pageWindow.visualViewport) {
29876:             runtimeListen(pageWindow.visualViewport, 'resize', () => scheduleTabletLayoutRefresh(20));
29877:             runtimeListen(pageWindow.visualViewport, 'scroll', () => {
29878:                 if (isTouchLayoutActive() && document.getElementById(SCRIPT.panelId)?.classList.contains('mcms-open')) scheduleTabletLayoutRefresh(20);
29879:             });
29880:         }
29881:         try {
29882:             const coarsePointerQuery = pageWindow.matchMedia?.('(any-pointer: coarse)');
29883:             if (coarsePointerQuery?.addEventListener) runtimeListen(coarsePointerQuery, 'change', () => scheduleTabletLayoutRefresh(20));
29884:         } catch (err) {}
29885: 
29886:         runtimeListen(pageWindow, 'focus', () => {
29887:             if (dragState) return;
29888:             refreshSuppression();
29889:             fitControlToMap();
29890:             schedulePanelPosition(true, 40);
29891:             installRadioMessageHook();
29892:             if (vehicleDataNeeded()) refreshPersonalVehicleData(false);
29893:             if (state.economyMode) scheduleEconomyLayerSync(0);
29894:             scheduleEnabledMapRefreshes({ includeSnapshots: missionSnapshotsNeeded(), positionPanel: false });
29895:             scheduleOperationalPanelsRender(500);
29896:             scheduleMajorIncidentFeedRender(80);
29897:         });
29898: 
29899:         const recoverUiAfterNavigation = event => {
29900:             runtimeSetTimeout(() => {
29901:                 if (runtime.destroyed || document.hidden) return;
29902:                 invalidateMapElementCache();
29903:                 ensureUi();
29904:                 connectMainMutationObserver();
29905:                 recoverMajorIncidentFeed(event?.type || 'navigation');
```

## `function boot(`

### Match 1 · canonical line 29759

```javascript
29739:             installMissionMarkerAddHook();
29740:             installRadioMessageHook();
29741:             installCreditsUpdateHook();
29742:             observeCreditValue();
29743:             const ready = ensureUi();
29744:             const mapReady = Boolean(getLargestLeafletMap());
29745:             if (ready && (mapReady || attempts >= 12)) {
29746:                 recordStartupMetric('coreUiReadyMs', bootPerformanceStartedAt, { bootAttempts: attempts });
29747:                 scheduleMarkerStateSync(0, false);
29748:                 scheduleDeferredOperationalStartup();
29749:                 runtimeSetTimeout(() => runtimeRunWhenIdle(connectMainMutationObserver, STARTUP_OBSERVER_DELAY_MS), STARTUP_OBSERVER_DELAY_MS);
29750:                 return;
29751:             }
29752:             if (attempts >= 90 || runtime.destroyed) return;
29753:             const delay = attempts < 12 ? 350 : attempts < 30 ? 700 : 1400;
29754:             runtimeSetTimeout(runBootAttempt, delay);
29755:         };
29756:         runtimeSetTimeout(runBootAttempt, 250);
29757:     }
29758: 
29759:     function boot() {
29760:         if (runtime.destroyed || bootStarted) return;
29761:         bootStarted = true;
29762:         bootStartedAt = Date.now();
29763:         const bootPerformanceStartedAt = startupClock();
29764:         applyRootAttributes();
29765:         if (installAllianceBuildingsPageOptimisation()) return;
29766:         createCleanExit();
29767:         if (state.autoLoadAllVehicles) installAutoLoadAllVehicles();
29768:         installMissionMarkerAddHook();
29769:         installRadioMessageHook();
29770:         lastObservedCredits = readCurrentCreditTotal();
29771:         installCreditsUpdateHook();
29772:         observeCreditValue();
29773: 
29774:         startBootAttemptCoordinator(bootPerformanceStartedAt);
29775: 
29776:         const observer = runtimeTrackObserver(new MutationObserver(mutations => {
29777:             if (state.economyMode && economyMapMoving) {
29778:                 economyDeferredDomMutation = true;
29779:                 return;
29780:             }
29781:             let externalMutationFound = false;
29782:             let addedLeafletMarker = false;
29783:             let missionChanged = false;
29784:             let layoutChanged = false;
29785:             let toolkitUiRemoved = false;
29786:             for (const mutation of mutations) {
29787:                 if (mutationBelongsToToolkit(mutation)) continue;
29788:                 externalMutationFound = true;
29789:                 if (!addedLeafletMarker && mutationAddsLeafletMarkerIcon(mutation)) {
29790:                     addedLeafletMarker = true;
29791:                     missionChanged = true;
29792:                 }
29793:                 if (!missionChanged && mutationAffectsMissionData(mutation)) missionChanged = true;
29794:                 if (!layoutChanged && mutationAffectsMapLayout(mutation)) layoutChanged = true;
29795:                 if (!toolkitUiRemoved && mutationRemovesToolkitUi(mutation)) toolkitUiRemoved = true;
29796:                 if (addedLeafletMarker && missionChanged && layoutChanged && toolkitUiRemoved) break;
29797:             }
29798:             if (!externalMutationFound) return;
29799:             missionChanged ||= addedLeafletMarker;
29800:             if (!missionChanged && !layoutChanged && !toolkitUiRemoved) return;
29801: 
29802:             if (addedLeafletMarker) {
29803:                 invalidateMarkerRegistryCaches('all');
29804:                 scheduleMarkerStateSync(0, false);
29805:                 if (!state.visibility.buildings) scheduleMarkerStateSync(180, true);
29806:             }
29807:             if (layoutChanged) invalidateMapElementCache();
29808:             if (document.hidden || dragState || (state.economyMode && economyMapMoving)) return;
29809: 
29810:             runtimeClearTimeout(mutationTimer);
29811:             const startupSettling = bootStartedAt > 0 && Date.now() - bootStartedAt < STARTUP_SETTLE_WINDOW_MS;
29812:             const mutationDelay = startupSettling
29813:                 ? STARTUP_MUTATION_DEBOUNCE_MS
29814:                 : (state.economyMode ? Math.max(320, DOM_REFRESH_DEBOUNCE_MS) : DOM_REFRESH_DEBOUNCE_MS);
29815:             mutationTimer = runtimeSetTimeout(() => {
29816:                 if (dragState || document.hidden || runtime.destroyed || (state.economyMode && economyMapMoving)) return;
29817:                 const panelMissing = settingsPanelActivated && !document.getElementById(SCRIPT.panelId);
29818:                 const mapElement = getLargestLeafletMap();
29819:                 const controlMissing = Boolean(mapElement && !document.getElementById(SCRIPT.controlId));
29820:                 if (toolkitUiRemoved || panelMissing || controlMissing) ensureUi();
29821:                 if (mainMutationObserverFallbackActive && (mapElement || document.querySelector('#missions, #mission_list, .missions-panel, .mission-list'))) {
29822:                     connectMainMutationObserver();
29823:                 }
29824:                 if (layoutChanged) {
29825:                     refreshSuppression();
29826:                     fitControlToMap();
29827:                     schedulePanelPosition(true, 50);
29828:                     scheduleCriticalDrawerDock(60);
29829:                 }
29830:                 if (missionChanged) scheduleEnabledMapRefreshes({ includeSnapshots: missionSnapshotsNeeded(), positionPanel: false });
29831:             }, mutationDelay);
29832:         }));
29833:         mainMutationObserver = observer;
29834: 
29835:         runtimeListen(document, 'keydown', handleKeyboard);
29836:         runtimeListen(document, 'pointerover', handleMissionInspectorPointerOver, true);
29837:         runtimeListen(document, 'pointermove', handleMissionInspectorPointerMove, true);
29838:         runtimeListen(document, 'pointerout', handleMissionInspectorPointerOut, true);
29839:         runtimeListen(document, 'pointerdown', () => unlockPayoutAudio(), { once: true, capture: true });
29840:         runtimeListen(document, 'click', event => {
29841:             runtimeSetTimeout(refreshSuppression, 0);
29842:             if (suppressNextOutsideClick) {
29843:                 event.preventDefault();
29844:                 event.stopPropagation();
29845:                 suppressNextOutsideClick = false;
29846:                 return;
29847:             }
29848: 
29849:             const control = document.getElementById(SCRIPT.controlId);
29850:             const panel = document.getElementById(SCRIPT.panelId);
29851:             if (!panel || !panel.classList.contains('mcms-open')) return;
29852:             if (control && control.contains(event.target)) return;
29853:             if (panel.contains(event.target)) return;
29854:             closePanel();
29855:         }, true);
29856: 
29857:         runtimeListen(pageWindow, 'resize', () => {
29858:             invalidateMapElementCache();
29859:             applyRootAttributes();
29860:             refreshTabletModeUi();
29861:             scheduleTabletLayoutRefresh(20);
29862:             const payoutOverlay = document.getElementById(SCRIPT.payoutFlashId);
29863:             if (payoutOverlay?.classList.contains('mcms-payout-active')) positionPayoutFlashOverlay(payoutOverlay);
29864:             if (dragState) return;
29865:             refreshSuppression();
29866:             fitControlToMap();
29867:             schedulePanelPosition(true, 40);
29868:             scheduleCriticalDrawerDock(30);
29869:             scheduleEnabledMapRefreshes({ includeSnapshots: false, positionPanel: false, mapOnly: true });
29870:             scheduleMajorIncidentFeedLayout();
29871:         });
29872: 
29873:         runtimeListen(pageWindow, 'scroll', scheduleMajorIncidentFeedLayout, { passive: true });
29874:         runtimeListen(pageWindow, 'orientationchange', () => scheduleTabletLayoutRefresh(30));
29875:         if (pageWindow.visualViewport) {
29876:             runtimeListen(pageWindow.visualViewport, 'resize', () => scheduleTabletLayoutRefresh(20));
29877:             runtimeListen(pageWindow.visualViewport, 'scroll', () => {
29878:                 if (isTouchLayoutActive() && document.getElementById(SCRIPT.panelId)?.classList.contains('mcms-open')) scheduleTabletLayoutRefresh(20);
29879:             });
29880:         }
29881:         try {
29882:             const coarsePointerQuery = pageWindow.matchMedia?.('(any-pointer: coarse)');
29883:             if (coarsePointerQuery?.addEventListener) runtimeListen(coarsePointerQuery, 'change', () => scheduleTabletLayoutRefresh(20));
29884:         } catch (err) {}
29885: 
29886:         runtimeListen(pageWindow, 'focus', () => {
29887:             if (dragState) return;
29888:             refreshSuppression();
29889:             fitControlToMap();
29890:             schedulePanelPosition(true, 40);
29891:             installRadioMessageHook();
29892:             if (vehicleDataNeeded()) refreshPersonalVehicleData(false);
29893:             if (state.economyMode) scheduleEconomyLayerSync(0);
29894:             scheduleEnabledMapRefreshes({ includeSnapshots: missionSnapshotsNeeded(), positionPanel: false });
29895:             scheduleOperationalPanelsRender(500);
29896:             scheduleMajorIncidentFeedRender(80);
29897:         });
29898: 
29899:         const recoverUiAfterNavigation = event => {
```

## `.mcms-mission-value-row {`

### Match 1 · canonical line 4210

```javascript
04180:             pointer-events: none !important;
04181:         }
04182:         @media (prefers-reduced-motion: reduce) {
04183:             #${SCRIPT.controlId} { transition: none !important; }
04184:         }
04185: 
04186:         /* v2.5.x mission intelligence and configuration tools */
04187:         #${SCRIPT.missionInspectorId} {
04188:             position: fixed !important; left: 0 !important; top: 0 !important; z-index: 2147483646 !important;
04189:             width: min(300px, calc(100vw - 24px)) !important; padding: 10px 11px !important;
04190:             border: 1px solid rgba(255,255,255,.18) !important; border-radius: 10px !important;
04191:             background: linear-gradient(180deg, rgba(14,19,27,.97), rgba(7,10,15,.96)) !important;
04192:             color: #eef4fb !important; box-shadow: 0 14px 34px rgba(0,0,0,.48), inset 0 1px 0 rgba(255,255,255,.06) !important;
04193:             font: 700 10px/1.35 Arial, Helvetica, sans-serif !important; pointer-events: none !important;
04194:             opacity: 0 !important; visibility: hidden !important; transform: translateY(4px) scale(.985) !important;
04195:             transition: opacity 110ms ease, transform 110ms ease, visibility 110ms step-end !important; backdrop-filter: blur(6px) !important;
04196:         }
04197:         #${SCRIPT.missionInspectorId}.mcms-open { opacity: 1 !important; visibility: visible !important; transform: translateY(0) scale(1) !important; transition: opacity 110ms ease, transform 110ms ease, visibility 0s step-start !important; }
04198:         #${SCRIPT.missionInspectorId} .mcms-inspector-head { display:flex !important; align-items:flex-start !important; justify-content:space-between !important; gap:8px !important; margin-bottom:7px !important; }
04199:         #${SCRIPT.missionInspectorId} .mcms-inspector-title { display:block !important; min-width:0 !important; color:#fff !important; font-size:12px !important; font-weight:950 !important; line-height:1.2 !important; overflow:hidden !important; text-overflow:ellipsis !important; }
04200:         #${SCRIPT.missionInspectorId} .mcms-inspector-type { flex:0 0 auto !important; padding:3px 5px !important; border-radius:5px !important; border:1px solid rgba(255,255,255,.16) !important; background:rgba(255,255,255,.06) !important; color:#b9c8d8 !important; font-size:7px !important; font-weight:950 !important; letter-spacing:.6px !important; }
04201:         #${SCRIPT.missionInspectorId} .mcms-inspector-type.mcms-alliance { color:#8df3ad !important; border-color:rgba(112,239,155,.38) !important; }
04202:         #${SCRIPT.missionInspectorId} .mcms-inspector-grid { display:grid !important; grid-template-columns:repeat(2,minmax(0,1fr)) !important; gap:5px !important; }
04203:         #${SCRIPT.missionInspectorId} .mcms-inspector-stat { min-width:0 !important; padding:6px 7px !important; border-radius:7px !important; background:rgba(255,255,255,.055) !important; border:1px solid rgba(255,255,255,.08) !important; }
04204:         #${SCRIPT.missionInspectorId} .mcms-inspector-stat span { display:block !important; color:#8393a5 !important; font-size:7px !important; font-weight:900 !important; letter-spacing:.4px !important; text-transform:uppercase !important; }
04205:         #${SCRIPT.missionInspectorId} .mcms-inspector-stat strong { display:block !important; margin-top:2px !important; color:#fff !important; font-size:11px !important; font-weight:950 !important; overflow:hidden !important; text-overflow:ellipsis !important; white-space:nowrap !important; }
04206:         #${SCRIPT.missionInspectorId} .mcms-inspector-alert { margin-top:6px !important; padding:6px 7px !important; border-radius:7px !important; border:1px solid rgba(255,181,71,.34) !important; background:rgba(255,143,31,.11) !important; color:#ffd29a !important; font-size:8px !important; font-weight:900 !important; line-height:1.35 !important; white-space:normal !important; overflow-wrap:anywhere !important; }
04207:         #${SCRIPT.missionInspectorId} .mcms-inspector-alert.mcms-stuck { border-color:rgba(255,74,64,.48) !important; background:rgba(255,44,36,.14) !important; color:#ffaaa4 !important; }
04208: 
04209: 
04210:         .mcms-mission-value-row {
04211:             display: flex !important;
04212:             align-items: center !important;
04213:             justify-content: flex-end !important;
04214:             min-width: 0 !important;
04215:             box-sizing: border-box !important;
04216:             position: relative !important;
04217:             z-index: 2 !important;
04218:             pointer-events: none !important;
04219:         }
04220:         #navbar-alarm-spacer > .mcms-mission-value-row,
04221:         .mcms-mission-value-row[data-mcms-host="toolbar"] {
04222:             flex: 1 1 auto !important;
04223:             width: 100% !important;
04224:             min-height: 32px !important;
04225:             margin: 0 !important;
04226:             padding: 0 3px 0 6px !important;
04227:             clear: none !important;
04228:             overflow: hidden !important;
04229:         }
04230:         .mcms-mission-value-row[data-mcms-host="fallback"] {
04231:             width: 100% !important;
04232:             min-height: 30px !important;
04233:             margin: 0 0 6px 0 !important;
04234:             padding: 4px 8px !important;
04235:             clear: both !important;
04236:             overflow: hidden !important;
04237:         }
04238:         .mcms-mission-value-badge {
04239:             display: inline-flex !important;
04240:             align-items: center !important;
04241:             justify-content: center !important;
04242:             max-width: 100% !important;
04243:             min-width: 0 !important;
04244:             min-height: 24px !important;
04245:             box-sizing: border-box !important;
04246:             padding: 4px 9px !important;
04247:             border: 1px solid rgba(235,190,64,.72) !important;
04248:             border-radius: 8px !important;
04249:             background: linear-gradient(145deg, rgba(48,39,13,.96), rgba(19,21,24,.96)) !important;
04250:             color: #ffe59a !important;
04251:             box-shadow: 0 2px 8px rgba(0,0,0,.34) !important;
04252:             font: 900 11px/1.2 Arial, Helvetica, sans-serif !important;
04253:             letter-spacing: .15px !important;
04254:             text-align: right !important;
04255:             white-space: nowrap !important;
04256:             overflow: hidden !important;
04257:             text-overflow: ellipsis !important;
04258:             pointer-events: none !important;
04259:         }
04260:         .mcms-mission-value-row[data-mcms-mode="value"] .mcms-mission-value-badge {
04261:             padding-left: 7px !important;
04262:             padding-right: 7px !important;
04263:         }
04264:         @media (max-width: 767px) {
04265:             .mcms-mission-value-row[data-mcms-host="fallback"] {
04266:                 padding: 4px 6px !important;
04267:             }
04268:             .mcms-mission-value-badge {
04269:                 font-size: 10px !important;
04270:             }
04271:         }
04272: 
04273:         .mcms-stuck-mission-icon { pointer-events:none !important; }
04274:         .mcms-stuck-mission-badge { display:inline-flex !important; align-items:center !important; justify-content:center !important; min-width:58px !important; height:17px !important; padding:0 6px !important; border-radius:6px !important; border:1px solid rgba(255,86,72,.72) !important; background:rgba(90,10,8,.88) !important; color:#ffd7d2 !important; font:950 8px/17px Arial,Helvetica,sans-serif !important; letter-spacing:.35px !important; text-shadow:0 1px 2px #000 !important; box-shadow:0 0 10px rgba(255,53,39,.32) !important; white-space:nowrap !important; }
04275:         .mcms-stuck-mission-badge.mcms-stuck-severe { background:rgba(130,7,4,.94) !important; border-color:#ff3d2e !important; color:#fff !important; animation:mcmsStuckPulse 1.3s ease-in-out infinite !important; }
04276:         @keyframes mcmsStuckPulse { 0%,100%{box-shadow:0 0 7px rgba(255,53,39,.28);transform:scale(1)} 50%{box-shadow:0 0 16px rgba(255,53,39,.70);transform:scale(1.035)} }
04277: 
04278:         .mcms-mission-spawn-ring { transform-box:fill-box !important; stroke:#67d9ff !important; stroke-width:3 !important; fill:rgba(48,183,255,.12) !important; transform-origin:center !important; animation:mcmsMissionSpawnRing 2.35s cubic-bezier(.12,.72,.18,1) both !important; pointer-events:none !important; }
04279:         .mcms-mission-spawn-label-icon { pointer-events:none !important; }
04280:         .mcms-mission-spawn-label { display:inline-flex !important; align-items:center !important; justify-content:center !important; min-width:86px !important; height:20px !important; padding:0 8px !important; border-radius:7px !important; border:1px solid rgba(98,219,255,.78) !important; background:rgba(4,22,34,.92) !important; color:#aeeeff !important; font:950 8px/20px Arial,Helvetica,sans-serif !important; letter-spacing:.65px !important; text-shadow:0 1px 2px #000 !important; box-shadow:0 0 16px rgba(67,198,255,.42) !important; animation:mcmsMissionSpawnLabel 2.35s ease-out both !important; white-space:nowrap !important; }
04281:         .leaflet-marker-icon.mcms-mission-spawn-focus { animation:mcmsMissionSpawnMarker 2.2s cubic-bezier(.16,.74,.18,1) both !important; }
04282:         @keyframes mcmsMissionSpawnRing { 0%{opacity:0;transform:scale(.25)} 12%{opacity:1;transform:scale(.55)} 75%{opacity:.50;transform:scale(3.2)} 100%{opacity:0;transform:scale(4.2)} }
04283:         @keyframes mcmsMissionSpawnLabel { 0%{opacity:0;transform:translateY(8px) scale(.9)} 14%,72%{opacity:1;transform:translateY(0) scale(1)} 100%{opacity:0;transform:translateY(-8px) scale(.96)} }
04284:         @keyframes mcmsMissionSpawnMarker { 0%{filter:brightness(1);transform:scale(1)} 12%{filter:brightness(1.55) drop-shadow(0 0 10px #53d9ff);transform:scale(1.22)} 34%{filter:brightness(1.15) drop-shadow(0 0 6px #53d9ff);transform:scale(.98)} 58%{filter:brightness(1.35) drop-shadow(0 0 8px #53d9ff);transform:scale(1.12)} 100%{filter:brightness(1);transform:scale(1)} }
04285: 
04286:         #${SCRIPT.panelId} .mcms-profile-list { display:grid !important; gap:6px !important; }
04287:         #${SCRIPT.panelId} .mcms-profile-row { display:grid !important; grid-template-columns:minmax(0,1fr) 36px 36px 25px !important; gap:5px !important; align-items:center !important; }
04288:         #${SCRIPT.panelId} .mcms-profile-main { min-width:0 !important; padding:6px 7px !important; border:1px solid rgba(255,255,255,.09) !important; border-radius:7px !important; background:rgba(255,255,255,.035) !important; }
04289:         #${SCRIPT.panelId} .mcms-profile-main strong,#${SCRIPT.panelId} .mcms-profile-main span { display:block !important; min-width:0 !important; overflow:hidden !important; white-space:nowrap !important; text-overflow:ellipsis !important; }
04290:         #${SCRIPT.panelId} .mcms-profile-main strong { color:#edf4fb !important; font-size:9px !important; }
04291:         #${SCRIPT.panelId} .mcms-profile-main span { color:#8393a5 !important; font-size:7px !important; margin-top:2px !important; }
04292:         #${SCRIPT.panelId} .mcms-config-actions { display:grid !important; grid-template-columns:repeat(3,minmax(0,1fr)) !important; gap:5px !important; }
04293:         #${SCRIPT.panelId} .mcms-config-actions .mcms-small-btn { min-width:0 !important; white-space:normal !important; text-overflow:clip !important; overflow-wrap:anywhere !important; }
04294:         html[data-mcms-mobile-active="true"] #${SCRIPT.panelId} .mcms-config-actions { grid-template-columns:repeat(2,minmax(0,1fr)) !important; gap:7px !important; }
04295:         html[data-mcms-mobile-active="true"] #${SCRIPT.panelId} .mcms-config-actions [data-action="reset-config"] { grid-column:1 / -1 !important; }
04296:         #${SCRIPT.panelId} .mcms-hidden-file { display:none !important; }
04297: 
04298: 
04299:         /* v3.7.0 complete interface themes */
04300:         #${SCRIPT.panelId} .mcms-ui-theme-grid {
04301:             display: grid !important;
04302:             grid-template-columns: repeat(2, minmax(0, 1fr)) !important;
04303:             gap: 7px !important;
04304:             margin-bottom: 7px !important;
04305:         }
04306:         #${SCRIPT.panelId} .mcms-ui-theme-btn {
04307:             position: relative !important;
04308:             display: grid !important;
04309:             grid-template-columns: 48px minmax(0, 1fr) !important;
04310:             align-items: center !important;
04311:             gap: 8px !important;
04312:             min-width: 0 !important;
04313:             height: 58px !important;
04314:             padding: 6px 8px !important;
04315:             border: 1px solid rgba(255,255,255,.14) !important;
04316:             border-radius: 10px !important;
04317:             background: rgba(255,255,255,.055) !important;
04318:             color: rgba(255,255,255,.82) !important;
04319:             cursor: pointer !important;
04320:             text-align: left !important;
04321:             overflow: hidden !important;
04322:             transition: transform 140ms ease, border-color 140ms ease, background 140ms ease !important;
04323:         }
04324:         #${SCRIPT.panelId} .mcms-ui-theme-btn:hover,
04325:         #${SCRIPT.panelId} .mcms-ui-theme-btn:focus-visible {
04326:             transform: translateY(-1px) !important;
04327:             border-color: rgba(124,194,255,.72) !important;
04328:             background: rgba(93,169,255,.12) !important;
04329:         }
04330:         #${SCRIPT.panelId} .mcms-ui-theme-btn.mcms-active {
```

## `<section class="mcms-tab-panel" data-panel="ops">`

### Match 1 · canonical line 28319

```javascript
28309:                     ${makeToggleButton('resourceGap', '⚠', 'Resource Gap', 'Show missing-resource badges and nearby available-unit estimates in Mission Inspector.')}
28310:                 </div>
28311:                 <div class="mcms-row"><span class="mcms-row-label">Nearby radius</span><select class="mcms-select" data-setting="resource-gap-radius"><option value="10">10 miles</option><option value="25">25 miles</option><option value="50">50 miles</option><option value="100">100 miles</option></select></div>
28312:                 <div class="mcms-status">Resource Gap uses MissionChief's missing-requirement text and performs best-effort matching against your currently available vehicle types. It never selects or dispatches units.</div>
28313:                 <div class="mcms-section-label">Vehicle loading</div>
28314:                 <div class="mcms-grid-2">
28315:                     ${makeToggleButton('autoLoadAllVehicles', '⇊', 'Auto-load all vehicles', 'Automatically activates MissionChief’s native Load more vehicles control inside an opened mission.')}
28316:                 </div>
28317:                 <div class="mcms-status">Transport Watcher and Unit Count remain under Tools as the canonical map-overlay controls for shortcuts 7 and 8.</div>
28318:             </section>
28319:             <section class="mcms-tab-panel" data-panel="ops">
28320:                 <div class="mcms-section-label">Mission Intelligence</div>
28321:                 <div class="mcms-grid-2">
28322:                     ${makeToggleButton('missionInspector', 'ⓘ', 'Inspector', 'Hover a mission marker for a live mission summary.')}
28323:                     ${makeToggleButton('missionValue', '£', 'Mission Value', 'Show a formatted mission value in opened MissionChief windows.')}
28324:                     ${makeToggleButton('stuckDetector', '⚠', 'Stuck Detect', 'Flag personal or joined missions that show no meaningful progress.')}
28325:                     ${makeToggleButton('missionSpawn', '◎', 'New Mission', 'Animate genuinely new mission spawns with a radar pulse.')}
28326:                     ${makeToggleButton('majorIncidentFeed', '▰', 'Incident Feed', 'Show the theme-aware major incident ticker in the top status bar. Hover pauses; click a mission to zoom.')}
28327:                     ${makeToggleButton('missionLockAudio', '⌁', 'Tracking Audio', 'Play a short synthesized tracking cue during mission zoom and target acquisition.')}
28328:                     <button class="mcms-toggle-btn mcms-action-btn" type="button" data-action="open-vehicle-status" title="Open or close a live table of personal vehicles grouped by MissionChief status code. Shortcut: V">
28329:                         <span class="mcms-iconbox">V</span>
28330:                         <span class="mcms-text"><span class="mcms-label">Vehicle Codes</span><span class="mcms-pill">VIEW</span></span>
28331:                     </button>
28332:                 </div>
28333:                 <div class="mcms-row"><span class="mcms-row-label">Stuck after</span><select class="mcms-select" data-setting="stuck-threshold"><option value="10">10 minutes</option><option value="15">15 minutes</option><option value="20">20 minutes</option><option value="30">30 minutes</option><option value="45">45 minutes</option><option value="60">60 minutes</option></select></div>
28334:                 <div class="mcms-status">Stuck detection resets its timer whenever missing requirements, patients, prisoners, progress value or your assigned-unit state changes.</div>
28335:                 <div class="mcms-section-label">Session Performance</div>
28336:                 <div data-ops-session></div>
28337:                 <div class="mcms-section-label">Mission Age Workflow</div>
28338:                 <div class="mcms-grid-2">
28339:                     <button class="mcms-small-btn" type="button" data-action="open-critical-drawer">Open Mission Drawer (W)</button>
28340:                     <button class="mcms-small-btn" type="button" data-action="fit-critical">Frame Aged</button>
28341:                 </div>
28342:                 <div class="mcms-status">Mission Age and Critical View remain under Tools as the canonical shortcut controls for 6 and 9. Ops provides the mission workflow and dashboard actions.</div>
28343:                 <div class="mcms-section-label">Mission Age Watch · 8H Amber · 16H Orange · 24H Red</div>
28344:                 <div class="mcms-ops-list" data-ops-critical-preview></div>
28345:                 <div class="mcms-section-label">Completion History</div>
28346:                 <div class="mcms-ops-list" data-ops-history></div>
28347:                 <div class="mcms-grid-2" style="margin-top:7px !important">
28348:                     <button class="mcms-small-btn" type="button" data-action="reset-session">Reset Session</button>
28349:                     <button class="mcms-small-btn" type="button" data-action="clear-payout-history">Clear History</button>
28350:                 </div>
28351:             </section>
28352:             <section class="mcms-tab-panel" data-panel="payouts">
28353:                 <div class="mcms-section-label">Emergency Payout Flash</div>
28354:                 <div class="mcms-grid-2">
28355:                     ${makeToggleButton('payoutFlash', '🚨', 'Payout Flash', 'Flash the map red and blue when a single credit gain reaches the configured threshold.')}
28356:                     ${makeToggleButton('payoutSound', '♪', 'Theme Audio', 'Play the selected template completion cue. Vice City, Bad Company, Scarface and Cyberpunk use hosted MP3 cashout sounds; other templates retain synthesized cues.')}
28357:                 </div>
28358:                 <div class="mcms-row"><span class="mcms-row-label">Banner style</span><select class="mcms-select" data-setting="payout-template">${buildPayoutTemplateOptions(state.payoutFlash.template)}</select></div>
28359:                 <div class="mcms-row"><span class="mcms-row-label">Minimum payout</span><input class="mcms-input" type="number" min="1000" step="1000" data-setting="payout-threshold"></div>
28360:                 <div class="mcms-row"><span class="mcms-row-label">Flash duration (sec)</span><input class="mcms-input" type="number" min="2" max="30" step="2" data-setting="payout-duration"></div>
28361:                 <div class="mcms-row"><span class="mcms-row-label">Sound volume</span><input class="mcms-input" type="range" min="0" max="1" step="0.05" data-setting="payout-volume"></div>
28362:                 <div class="mcms-row"><span class="mcms-row-label">Test payout tier</span><select class="mcms-select" data-setting="payout-test-amount"><option value="10000">10K Standard</option><option value="25000">25K Major</option><option value="50000">50K High Value</option><option value="100000">100K Elite</option></select></div>
28363:                 <button class="mcms-small-btn" style="width:100% !important;margin-bottom:8px !important" type="button" data-action="test-payout-flash">Test Emergency Flash</button>
28364:                 <div class="mcms-status">Vice City Inspired, Bad Company Inspired, Scarface Inspired and Cyberpunk Inspired use hosted cashout MP3s from your public GitHub asset repository. Other templates retain synthesized cues. Enable Theme Audio, set the volume, then use Test Emergency Flash.</div>
28365:             </section>
28366:             <section class="mcms-tab-panel" data-panel="discord">
28367:                 <div class="mcms-section-label">Discord Financial Command</div>
28368:                 <div class="mcms-row mcms-discord-wide"><span class="mcms-row-label">Webhook URL</span><input class="mcms-input" type="password" autocomplete="off" spellcheck="false" data-setting="discord-webhook" placeholder="https://discord.com/api/webhooks/..."></div>
28369:                 <div class="mcms-row mcms-discord-wide"><span class="mcms-row-label">Webhook name</span><input class="mcms-input" type="text" maxlength="80" data-setting="discord-name" value="MissionChief Finance"></div>
28370:                 <div class="mcms-row"><span class="mcms-row-label">Report format</span><select class="mcms-select" data-setting="discord-report-mode"><option value="fullAudit">Executive + Full Audit</option><option value="executive">Executive Brief Only</option></select></div>
28371:                 <div class="mcms-row"><span class="mcms-row-label">Report period</span><select class="mcms-select" data-setting="discord-period"><option value="today">Today</option><option value="yesterday">Yesterday</option><option value="last24">Last 24 Hours</option><option value="last7">Last 7 Days</option><option value="last30">Last 30 Days</option><option value="last90">Last 90 Days</option><option value="last180">Last 180 Days</option><option value="last365">Last 365 Days</option><option value="allAvailable">All Available History</option><option value="session">Current Session</option><option value="sinceLast">Since Last Report</option><option value="custom">Custom Dates</option></select></div>
28372:                 <div class="mcms-discord-date-grid">
28373:                     <div class="mcms-row"><span class="mcms-row-label">From</span><input class="mcms-input" type="date" data-setting="discord-custom-start"></div>
28374:                     <div class="mcms-row"><span class="mcms-row-label">To</span><input class="mcms-input" type="date" data-setting="discord-custom-end"></div>
28375:                 </div>
28376:                 <div class="mcms-row"><span class="mcms-row-label">Breakdown depth</span><select class="mcms-select" data-setting="discord-top-categories"><option value="3">Top 3</option><option value="5">Top 5</option><option value="8">Top 8</option></select></div>
28377:                 <div class="mcms-row"><span class="mcms-row-label">Previous-period comparison</span><select class="mcms-select" data-setting="discord-comparison"><option value="true">Included</option><option value="false">Disabled</option></select></div>
28378:                 <div class="mcms-row"><span class="mcms-row-label">Risk intelligence</span><select class="mcms-select" data-setting="discord-risk"><option value="true">Included</option><option value="false">Disabled</option></select></div>
28379:                 <div class="mcms-row"><span class="mcms-row-label">Forecast intelligence</span><select class="mcms-select" data-setting="discord-forecast"><option value="true">Included</option><option value="false">Disabled</option></select></div>
28380:                 <div class="mcms-row"><span class="mcms-row-label">Discord chart image</span><select class="mcms-select" data-setting="discord-chart"><option value="true">Attach chart</option><option value="false">Text only</option></select></div>
28381:                 <div class="mcms-grid-2">
28382:                     <button class="mcms-small-btn" type="button" data-action="discord-test">Test Connection</button>
28383:                     <button class="mcms-small-btn" type="button" data-action="discord-clear">Clear Webhook</button>
28384:                 </div>
28385:                 <button class="mcms-small-btn" style="width:100% !important;margin-top:7px !important" type="button" data-action="discord-generate-post">Generate & Post Audit</button>
28386:                 <div class="mcms-status mcms-discord-status" data-discord-status data-tone="neutral">Select a reporting period, then generate and post the financial intelligence report.</div>
28387: 
28388:                 <div class="mcms-section-label">Player-Linked Local Financial Archive</div>
28389:                 <div class="mcms-row"><span class="mcms-row-label">Local historical archive</span><select class="mcms-select" data-setting="finance-vault-enabled"><option value="true">Enabled</option><option value="false">Disabled</option></select></div>
28390:                 <div class="mcms-row"><span class="mcms-row-label">History retention</span><select class="mcms-select" data-setting="finance-vault-retention"><option value="all">All available</option><option value="1825">5 years</option><option value="730">2 years</option><option value="365">1 year</option><option value="180">180 days</option><option value="90">90 days</option></select></div>
28391:                 <div class="mcms-row"><span class="mcms-row-label">GitHub intelligence feeds</span><select class="mcms-select" data-setting="finance-rule-feed"><option value="true">Automatic rules + policy</option><option value="false">Built-in intelligence only</option></select></div>
28392:                 <div class="mcms-grid-2">
28393:                     <button class="mcms-small-btn" type="button" data-action="finance-archive-scan">Deep Scan All Available</button>
28394:                     <button class="mcms-small-btn" type="button" data-action="finance-archive-cancel">Stop Scan</button>
28395:                     <button class="mcms-small-btn" type="button" data-action="finance-archive-export">Export Archive</button>
28396:                     <button class="mcms-small-btn" type="button" data-action="finance-archive-import">Import Archive</button>
28397:                 </div>
28398:                 <button class="mcms-small-btn" style="width:100% !important;margin-top:7px !important" type="button" data-action="finance-rules-refresh">Refresh Financial Intelligence</button>
28399:                 <button class="mcms-small-btn" style="width:100% !important;margin-top:7px !important" type="button" data-action="finance-archive-clear">Clear Player Archive</button>
28400:                 <input class="mcms-hidden-file" type="file" accept="application/json,text/json,.json" data-import-finance-file>
28401:                 <div class="mcms-finance-vault-summary" data-finance-vault-summary></div>
28402:                 <div class="mcms-status mcms-discord-status" data-finance-vault-status data-tone="neutral">Local Financial Archive ready.</div>
28403:                 <div class="mcms-status mcms-discord-status" data-finance-rule-status data-tone="neutral">Built-in financial intelligence active.</div>
28404:                 <div class="mcms-status">GitHub hosts public transaction-classification rules and audit policy only. The Toolkit never uploads player ledger data, Discord webhooks or repository credentials. The local archive is indexed by MissionChief player ID/name and can be transferred between devices using Export Archive / Import Archive or the complete private Toolkit backup.</div>
28405:                 <div class="mcms-status mcms-finance-private-note">Private backup warning: Export All includes your Discord webhook and locally stored MissionChief financial history. Anyone holding the file may post through the webhook and inspect the exported game ledger.</div>
28406:             </section>
28407:             <section class="mcms-tab-panel" data-panel="places">
28408:                 <div class="mcms-section-label">Quick jumps + screen shortcuts</div>
28409:                 <div class="mcms-quick-list"></div>
28410:                 <div class="mcms-section-label">Custom bookmarks + screen shortcuts</div>
28411:                 <div class="mcms-bookmark-list"></div>
28412:                 <div class="mcms-section-label">Saved Map Profiles</div>
28413:                 <div class="mcms-profile-list" data-profile-list></div>
28414:                 <div class="mcms-status">Profiles store your map location, zoom, skin, visibility filters and operational overlays.</div>
28415:             </section>
28416:             <section class="mcms-tab-panel" data-panel="settings">
28417:                 <div class="mcms-section-label">Device layout</div>
28418:                 <div class="mcms-row"><span class="mcms-row-label">Mobile Mode · iOS Safari</span><select class="mcms-select" data-setting="mobile-mode"><option value="auto">Auto detect iPhone</option><option value="on">Always on</option><option value="off">Always off</option></select></div>
28419:                 <div class="mcms-row"><span class="mcms-row-label">Tablet Mode</span><select class="mcms-select" data-setting="tablet-mode"><option value="auto">Auto detect</option><option value="on">Always on</option><option value="off">Always off</option></select></div>
28420:                 <div class="mcms-status" data-device-layout-status>Detecting device layout…</div>
28421:                 <div class="mcms-status">Mobile Mode is tuned for iPhone Safari with Tampermonkey: a map-aware 5×2 command grid in portrait, a compact single-row dock where space allows, full-width safe-area bottom sheets, 16px form controls to prevent Safari input zoom, and Visual Viewport handling for the iOS keyboard. Tablet and desktop layouts remain separate and unchanged.</div>
28422:                 <div class="mcms-section-label">Dock position</div>
28423:                 <div class="mcms-position-grid">${positionButtons}</div>
28424:                 <div class="mcms-desktop-position-controls">
28425:                     <div class="mcms-section-label">Fine nudge</div>
28426:                     <div class="mcms-nudge-grid">
28427:                         <button class="mcms-small-btn" type="button" data-action="nudge-left">←</button>
28428:                         <button class="mcms-small-btn" type="button" data-action="nudge-up">↑</button>
28429:                         <button class="mcms-small-btn" type="button" data-action="nudge-down">↓</button>
```
