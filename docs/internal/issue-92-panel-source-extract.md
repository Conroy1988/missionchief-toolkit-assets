# Issue 92 focused panel source extract

## Complete command-panel markup

```text
27860:                     </span>
27861:                 </button>
27862:             `;
27863:         }).join('');
27864:         const uiThemeButtons = buildUiThemeButtons();
27865:         const coreThemeButtons = buildThemeButtons(CORE_THEME_ORDER);
27866:         const serviceThemeButtons = buildThemeButtons(SERVICE_THEME_ORDER);
27867: 
27868:         const positionButtons = Object.entries(POSITIONS).map(([key, pos]) => `<button class="mcms-position-btn" type="button" data-position="${key}" title="${pos.label}">${pos.short}</button>`).join('');
27869: 
27870:         panel.innerHTML = `
27871:             <div class="mcms-panel-sticky-stack">
27872:                 <div class="mcms-header">
27873:                     <div class="mcms-drag-handle" title="Hold left-click and drag this bar to move the menu">
27874:                         <span class="mcms-title">☰ DRAG MENU HERE</span>
27875:                         <span class="mcms-subtitle">Hold left-click on this title area. Position saves.</span>
27876:                     </div>
27877:                     <button class="mcms-reset-panel" type="button" data-action="panel-reset" title="Reset menu position">↺</button>
27878:                     <button class="mcms-help-button" type="button" data-action="open-help-center" title="Open searchable Help Centre" aria-label="Open searchable Help Centre">?</button>
27879:                     <button class="mcms-close" type="button" title="Close">×</button>
27880:                 </div>
27881:                 <div class="mcms-tabs">
27882:                     <button class="mcms-tab-btn" type="button" data-tab="skins">Skins</button>
27883:                     <button class="mcms-tab-btn" type="button" data-tab="tools">Tools</button>
27884:                     <button class="mcms-tab-btn" type="button" data-tab="resources">Resources</button>
27885:                     <button class="mcms-tab-btn" type="button" data-tab="ops">Ops</button>
27886:                     <button class="mcms-tab-btn" type="button" data-tab="payouts">Payouts</button>
27887:                     <button class="mcms-tab-btn" type="button" data-tab="discord">Discord</button>
27888:                     <button class="mcms-tab-btn" type="button" data-tab="places">Places</button>
27889:                     <button class="mcms-tab-btn" type="button" data-tab="settings">Settings</button>
27890:                 </div>
27891:             </div>
27892:             <section class="mcms-tab-panel" data-panel="skins">
27893:                 <div class="mcms-section-label">Interface theme</div>
27894:                 <div class="mcms-ui-theme-grid">${uiThemeButtons}</div>
27895:                 <div class="mcms-status mcms-ui-theme-status">Interface themes restyle the complete toolkit without changing your selected operational map skin.</div>
27896:                 <div class="mcms-section-label">Core skins</div>
27897:                 <div class="mcms-grid-2">${coreThemeButtons}</div>
27898:                 <div class="mcms-section-label">Emergency services</div>
27899:                 <div class="mcms-grid-2">${serviceThemeButtons}</div>
27900:                 <div class="mcms-status">Fire Command, Police Tactical, Medical Control and Coastal Command use lightweight local tile filters and remain compatible with map overlays.</div>
27901:             </section>
27902:             <section class="mcms-tab-panel" data-panel="tools">
27903:                 <div class="mcms-section-label">Map tools</div>
27904:                 <div class="mcms-grid-2">
27905:                     ${makeToggleButton('clean', '▢', 'Clean', 'Hide map controls for screenshots. Shortcut: C')}
27906:                     ${makeToggleButton('markerFocus', '◉', 'Focus', 'Dim detected buildings/vehicles and keep missions clearer. Shortcut: F')}
27907:                     ${makeToggleButton('missionPulse', '✦', 'Pulse', 'Pulse detected mission markers. Shortcut: P')}
27908:                     ${makeToggleButton('roadPriority', '═', 'Roads+', 'Increase road contrast. Shortcut: R')}
27909:                     ${makeToggleButton('coverage', '◎', 'Rings', 'Draw coverage rings around detected buildings/stations.')}
27910:                     ${makeToggleButton('heatmap', '▦', 'Heatmap', 'Show strong and weak operational coverage across the visible map.')}
27911:                 </div>
27912:                 <div class="mcms-row" style="margin-top:8px">
27913:                     <span class="mcms-row-label">Ring radius</span>
27914:                     <select class="mcms-select" data-setting="coverage-radius">
27915:                         <option value="5">5 miles</option><option value="10">10 miles</option><option value="25">25 miles</option><option value="50">50 miles</option>
27916:                     </select>
27917:                 </div>
27918:                 <div class="mcms-section-label">Coverage Heatmap</div>
27919:                 <div class="mcms-row"><span class="mcms-row-label">Coverage source</span><select class="mcms-select" data-setting="heatmap-source"><option value="stations">Personal stations</option><option value="vehicles">Current vehicles</option></select></div>
27920:                 <div class="mcms-row"><span class="mcms-row-label">Service</span><select class="mcms-select" data-setting="heatmap-service"><option value="all">All services</option><option value="fire">Fire & rescue</option><option value="ambulance">Ambulance</option><option value="police">Police</option><option value="air">Air assets</option><option value="water">Water/coastal</option></select></div>
27921:                 <div class="mcms-row"><span class="mcms-row-label">Planning radius</span><select class="mcms-select" data-setting="heatmap-radius"><option value="5">5 miles</option><option value="10">10 miles</option><option value="25">25 miles</option><option value="50">50 miles</option></select></div>
27922:                 <div class="mcms-row"><span class="mcms-row-label">Overlay strength</span><select class="mcms-select" data-setting="heatmap-opacity"><option value="0.18">Light</option><option value="0.30">Normal</option><option value="0.42">Strong</option></select></div>
27923:                 <div class="mcms-heat-legend"><span class="mcms-heat-key" style="background:#00c853">Strong</span><span class="mcms-heat-key" style="background:#64dd17">Good</span><span class="mcms-heat-key" style="background:#ffd600">Covered</span><span class="mcms-heat-key" style="background:#ff9100">Weak</span><span class="mcms-heat-key" style="background:#d50000">Gap</span></div>
27924:                 <div class="mcms-section-label">Map visibility · shortcuts 1–9 · dashboards V/W</div>
27925:                 <div class="mcms-grid-2">
27926:                     ${makeToggleButton('myMissions', '1', 'Personal Missions', 'Show/hide confidently detected personal missions. Shortcut: 1')}
27927:                     ${makeToggleButton('allianceMissions', '2', 'Alliance Missions', 'Show/hide confidently detected alliance missions. Shortcut: 2')}
27928:                     ${makeToggleButton('vehicles', '3', 'Vehicles', 'Show/hide confidently detected vehicles. Shortcut: 3')}
27929:                     ${makeToggleButton('buildings', '4', 'Buildings', 'Show/hide confidently detected buildings/stations. Shortcut: 4')}
27930:                     ${makeToggleButton('allianceCredits', '5', 'Ally Cred', 'Show/hide approximate credit values beside alliance mission markers. Shortcut: 5')}
27931:                     ${makeToggleButton('missionAge', '6', 'Miss Age', 'Show personal mission age with progressive 8H amber, 16H orange and 24H red severity. Shortcut: 6')}
27932:                     ${makeToggleButton('transportWatcher', '7', 'Transport Watcher', 'Show amber transport-required badges beside personal and alliance missions. Shortcut: 7')}
27933:                     ${makeToggleButton('unitCommitment', '8', 'Unit Count', 'Show your committed units beside personal and alliance missions. Shortcut: 8')}
27934:                     ${makeToggleButton('criticalView', '9', 'Critical View', 'Temporarily show only personal missions aged 8 hours or more. Shortcut: 9')}
27935:                 </div>
27936:                 <div class="mcms-row" style="margin-top:8px"><span class="mcms-row-label">Ally Credits filter</span><select class="mcms-select" data-setting="alliance-credit-minimum"><option value="0">All values</option><option value="5000">5K+</option><option value="10000">10K+</option><option value="15000">15K+</option><option value="20000">20K+</option></select></div>
27937:                 <div class="mcms-status">Ready.</div>
27938:             </section>
27939:             <section class="mcms-tab-panel" data-panel="resources">
27940:                 <div class="mcms-section-label">Co-admin Patient Transport Sweep</div>
27941:                 <div class="mcms-grid-2">
27942:                     <button class="mcms-small-btn" type="button" data-action="scan-transport-sweep">Scan Transports</button>
27943:                     <button class="mcms-small-btn" type="button" data-action="start-transport-sweep">Start Sweep</button>
27944:                     <button class="mcms-small-btn" type="button" data-action="stop-transport-sweep">Stop</button>
27945:                     ${makeToggleButton('transportWatcher', '7', 'Transport Watch', 'Show amber transport-required badges beside missions. Shortcut: 7')}
27946:                 </div>
27947:                 <div class="mcms-row"><span class="mcms-row-label">Delay between clears</span><select class="mcms-select" data-setting="transport-sweep-delay"><option value="1500">1.5 seconds</option><option value="2000">2 seconds</option><option value="2500">2.5 seconds</option><option value="3000">3 seconds</option><option value="4000">4 seconds</option><option value="5000">5 seconds</option></select></div>
27948:                 <div class="mcms-row"><span class="mcms-row-label">Maximum per run</span><input class="mcms-input" type="number" min="1" max="50" step="1" data-setting="transport-sweep-max"></div>
27949:                 <div data-transport-sweep></div>
27950:                 <div class="mcms-status">Manual start only. The sweep excludes your personal vehicle IDs, checks every non-personal FMS 5 patient vehicle in each affected alliance mission, and only clears a vehicle when MissionChief exposes the visible <b>Discharge patient</b> button. Prisoner transports are not included.</div>
27951:                 <div class="mcms-section-label">Resource Gap Finder</div>
27952:                 <div class="mcms-grid-2">
27953:                     ${makeToggleButton('resourceGap', '⚠', 'Resource Gap', 'Show missing-resource badges and nearby available-unit estimates in Mission Inspector.')}
27954:                 </div>
27955:                 <div class="mcms-row"><span class="mcms-row-label">Nearby radius</span><select class="mcms-select" data-setting="resource-gap-radius"><option value="10">10 miles</option><option value="25">25 miles</option><option value="50">50 miles</option><option value="100">100 miles</option></select></div>
27956:                 <div class="mcms-status">Resource Gap uses MissionChief's missing-requirement text and performs best-effort matching against your currently available vehicle types. It never selects or dispatches units.</div>
27957:             </section>
27958:             <section class="mcms-tab-panel" data-panel="ops">
27959:                 <div class="mcms-section-label">Mission Intelligence</div>
27960:                 <div class="mcms-grid-2">
27961:                     ${makeToggleButton('missionInspector', 'ⓘ', 'Inspector', 'Hover a mission marker for a live mission summary.')}
27962:                     ${makeToggleButton('missionValue', '£', 'Mission Value', 'Show a formatted mission value in opened MissionChief windows.')}
27963:                     ${makeToggleButton('stuckDetector', '⚠', 'Stuck Detect', 'Flag personal or joined missions that show no meaningful progress.')}
27964:                     ${makeToggleButton('missionSpawn', '◎', 'New Mission', 'Animate genuinely new mission spawns with a radar pulse.')}
27965:                     ${makeToggleButton('transportWatcher', '7', 'Transport Watch', 'Show amber transport-required badges beside missions. Shortcut: 7')}
27966:                     ${makeToggleButton('unitCommitment', '8', 'Unit Count', 'Show your own committed unit counts beside missions. Shortcut: 8')}
27967:                     <button class="mcms-toggle-btn mcms-action-btn" type="button" data-action="open-vehicle-status" title="Open or close a live table of personal vehicles grouped by MissionChief status code. Shortcut: V">
27968:                         <span class="mcms-iconbox">V</span>
27969:                         <span class="mcms-text"><span class="mcms-label">Vehicle Codes</span><span class="mcms-pill">VIEW</span></span>
27970:                     </button>
27971:                 </div>
27972:                 <div class="mcms-row"><span class="mcms-row-label">Stuck after</span><select class="mcms-select" data-setting="stuck-threshold"><option value="10">10 minutes</option><option value="15">15 minutes</option><option value="20">20 minutes</option><option value="30">30 minutes</option><option value="45">45 minutes</option><option value="60">60 minutes</option></select></div>
27973:                 <div class="mcms-status">Stuck detection resets its timer whenever missing requirements, patients, prisoners, progress value or your assigned-unit state changes.</div>
27974:                 <div class="mcms-section-label">Session Performance</div>
27975:                 <div data-ops-session></div>
27976:                 <div class="mcms-section-label">Mission Age Workflow</div>
27977:                 <div class="mcms-grid-2">
27978:                     <button class="mcms-small-btn" style="height:34px !important;line-height:34px !important" type="button" data-action="open-critical-drawer">Open Mission Drawer (W)</button>
27979:                     <button class="mcms-small-btn" style="height:34px !important;line-height:34px !important" type="button" data-action="fit-critical">Frame Aged</button>
27980:                     ${makeToggleButton('criticalView', '9', 'Critical View', 'Show only personal missions aged 8 hours or more. Shortcut: 9')}
27981:                     ${makeToggleButton('missionAge', '6', 'Mission Age', 'Show personal mission age with 8H amber, 16H orange and 24H red warning stages. Shortcut: 6')}
27982:                 </div>
27983:                 <div class="mcms-section-label">Mission Age Watch · 8H Amber · 16H Orange · 24H Red</div>
27984:                 <div class="mcms-ops-list" data-ops-critical-preview></div>
27985:                 <div class="mcms-section-label">Completion History</div>
27986:                 <div class="mcms-ops-list" data-ops-history></div>
27987:                 <div class="mcms-grid-2" style="margin-top:7px !important">
27988:                     <button class="mcms-small-btn" type="button" data-action="reset-session">Reset Session</button>
27989:                     <button class="mcms-small-btn" type="button" data-action="clear-payout-history">Clear History</button>
27990:                 </div>
27991:             </section>
27992:             <section class="mcms-tab-panel" data-panel="payouts">
27993:                 <div class="mcms-section-label">Emergency Payout Flash</div>
27994:                 <div class="mcms-grid-2">
27995:                     ${makeToggleButton('payoutFlash', '🚨', 'Payout Flash', 'Flash the map red and blue when a single credit gain reaches the configured threshold.')}
27996:                     ${makeToggleButton('payoutSound', '♪', 'Theme Audio', 'Play the selected template completion cue. Vice City, Bad Company, Scarface and Cyberpunk use hosted MP3 cashout sounds; other templates retain synthesized cues.')}
27997:                 </div>
27998:                 <div class="mcms-row"><span class="mcms-row-label">Banner style</span><select class="mcms-select" data-setting="payout-template">${buildPayoutTemplateOptions(state.payoutFlash.template)}</select></div>
27999:                 <div class="mcms-row"><span class="mcms-row-label">Minimum payout</span><input class="mcms-input" type="number" min="1000" step="1000" data-setting="payout-threshold"></div>
28000:                 <div class="mcms-row"><span class="mcms-row-label">Flash duration (sec)</span><input class="mcms-input" type="number" min="2" max="30" step="2" data-setting="payout-duration"></div>
28001:                 <div class="mcms-row"><span class="mcms-row-label">Sound volume</span><input class="mcms-input" type="range" min="0" max="1" step="0.05" data-setting="payout-volume"></div>
28002:                 <div class="mcms-row"><span class="mcms-row-label">Test payout tier</span><select class="mcms-select" data-setting="payout-test-amount"><option value="10000">10K Standard</option><option value="25000">25K Major</option><option value="50000">50K High Value</option><option value="100000">100K Elite</option></select></div>
28003:                 <button class="mcms-small-btn" style="width:100% !important;margin-bottom:8px !important" type="button" data-action="test-payout-flash">Test Emergency Flash</button>
28004:                 <div class="mcms-status">Vice City Inspired, Bad Company Inspired, Scarface Inspired and Cyberpunk Inspired use hosted cashout MP3s from your public GitHub asset repository. Other templates retain synthesized cues. Enable Theme Audio, set the volume, then use Test Emergency Flash.</div>
28005:             </section>
28006:             <section class="mcms-tab-panel" data-panel="discord">
28007:                 <div class="mcms-section-label">Discord Financial Command</div>
28008:                 <div class="mcms-row mcms-discord-wide"><span class="mcms-row-label">Webhook URL</span><input class="mcms-input" type="password" autocomplete="off" spellcheck="false" data-setting="discord-webhook" placeholder="https://discord.com/api/webhooks/..."></div>
28009:                 <div class="mcms-row mcms-discord-wide"><span class="mcms-row-label">Webhook name</span><input class="mcms-input" type="text" maxlength="80" data-setting="discord-name" value="MissionChief Finance"></div>
28010:                 <div class="mcms-row"><span class="mcms-row-label">Report format</span><select class="mcms-select" data-setting="discord-report-mode"><option value="fullAudit">Executive + Full Audit</option><option value="executive">Executive Brief Only</option></select></div>
28011:                 <div class="mcms-row"><span class="mcms-row-label">Report period</span><select class="mcms-select" data-setting="discord-period"><option value="today">Today</option><option value="yesterday">Yesterday</option><option value="last24">Last 24 Hours</option><option value="last7">Last 7 Days</option><option value="last30">Last 30 Days</option><option value="last90">Last 90 Days</option><option value="last180">Last 180 Days</option><option value="last365">Last 365 Days</option><option value="allAvailable">All Available History</option><option value="session">Current Session</option><option value="sinceLast">Since Last Report</option><option value="custom">Custom Dates</option></select></div>
28012:                 <div class="mcms-discord-date-grid">
28013:                     <div class="mcms-row"><span class="mcms-row-label">From</span><input class="mcms-input" type="date" data-setting="discord-custom-start"></div>
28014:                     <div class="mcms-row"><span class="mcms-row-label">To</span><input class="mcms-input" type="date" data-setting="discord-custom-end"></div>
28015:                 </div>
28016:                 <div class="mcms-row"><span class="mcms-row-label">Breakdown depth</span><select class="mcms-select" data-setting="discord-top-categories"><option value="3">Top 3</option><option value="5">Top 5</option><option value="8">Top 8</option></select></div>
28017:                 <div class="mcms-row"><span class="mcms-row-label">Previous-period comparison</span><select class="mcms-select" data-setting="discord-comparison"><option value="true">Included</option><option value="false">Disabled</option></select></div>
28018:                 <div class="mcms-row"><span class="mcms-row-label">Risk intelligence</span><select class="mcms-select" data-setting="discord-risk"><option value="true">Included</option><option value="false">Disabled</option></select></div>
28019:                 <div class="mcms-row"><span class="mcms-row-label">Forecast intelligence</span><select class="mcms-select" data-setting="discord-forecast"><option value="true">Included</option><option value="false">Disabled</option></select></div>
28020:                 <div class="mcms-row"><span class="mcms-row-label">Discord chart image</span><select class="mcms-select" data-setting="discord-chart"><option value="true">Attach chart</option><option value="false">Text only</option></select></div>
28021:                 <div class="mcms-grid-2">
28022:                     <button class="mcms-small-btn" type="button" data-action="discord-test">Test Connection</button>
28023:                     <button class="mcms-small-btn" type="button" data-action="discord-clear">Clear Webhook</button>
28024:                 </div>
28025:                 <button class="mcms-small-btn" style="width:100% !important;margin-top:7px !important" type="button" data-action="discord-generate-post">Generate and Post Supreme Audit</button>
28026:                 <div class="mcms-status mcms-discord-status" data-discord-status data-tone="neutral">Select a reporting period, then generate and post the financial intelligence report.</div>
28027: 
28028:                 <div class="mcms-section-label">Player-Linked Local Financial Archive</div>
28029:                 <div class="mcms-row"><span class="mcms-row-label">Local historical archive</span><select class="mcms-select" data-setting="finance-vault-enabled"><option value="true">Enabled</option><option value="false">Disabled</option></select></div>
28030:                 <div class="mcms-row"><span class="mcms-row-label">History retention</span><select class="mcms-select" data-setting="finance-vault-retention"><option value="all">All available</option><option value="1825">5 years</option><option value="730">2 years</option><option value="365">1 year</option><option value="180">180 days</option><option value="90">90 days</option></select></div>
28031:                 <div class="mcms-row"><span class="mcms-row-label">GitHub intelligence feeds</span><select class="mcms-select" data-setting="finance-rule-feed"><option value="true">Automatic rules + policy</option><option value="false">Built-in intelligence only</option></select></div>
28032:                 <div class="mcms-grid-2">
28033:                     <button class="mcms-small-btn" type="button" data-action="finance-archive-scan">Deep Scan All Available</button>
28034:                     <button class="mcms-small-btn" type="button" data-action="finance-archive-cancel">Stop Scan</button>
28035:                     <button class="mcms-small-btn" type="button" data-action="finance-archive-export">Export Archive</button>
28036:                     <button class="mcms-small-btn" type="button" data-action="finance-archive-import">Import Archive</button>
28037:                 </div>
28038:                 <button class="mcms-small-btn" style="width:100% !important;margin-top:7px !important" type="button" data-action="finance-rules-refresh">Refresh GitHub Financial Intelligence</button>
28039:                 <button class="mcms-small-btn" style="width:100% !important;margin-top:7px !important" type="button" data-action="finance-archive-clear">Clear This Player's Local Archive</button>
28040:                 <input class="mcms-hidden-file" type="file" accept="application/json,text/json,.json" data-import-finance-file>
28041:                 <div class="mcms-finance-vault-summary" data-finance-vault-summary></div>
28042:                 <div class="mcms-status mcms-discord-status" data-finance-vault-status data-tone="neutral">Local Financial Archive ready.</div>
28043:                 <div class="mcms-status mcms-discord-status" data-finance-rule-status data-tone="neutral">Built-in financial intelligence active.</div>
28044:                 <div class="mcms-status">GitHub hosts public transaction-classification rules and audit policy only. The Toolkit never uploads player ledger data, Discord webhooks or repository credentials. The local archive is indexed by MissionChief player ID/name and can be transferred between devices using Export Archive / Import Archive or the complete private Toolkit backup.</div>
28045:                 <div class="mcms-status mcms-finance-private-note">Private backup warning: Export All includes your Discord webhook and locally stored MissionChief financial history. Anyone holding the file may post through the webhook and inspect the exported game ledger.</div>
28046:             </section>
28047:             <section class="mcms-tab-panel" data-panel="places">
28048:                 <div class="mcms-section-label">Quick jumps + screen shortcuts</div>
28049:                 <div class="mcms-quick-list"></div>
28050:                 <div class="mcms-section-label">Custom bookmarks + screen shortcuts</div>
28051:                 <div class="mcms-bookmark-list"></div>
28052:             </section>
28053:             <section class="mcms-tab-panel" data-panel="settings">
28054:                 <div class="mcms-section-label">Device layout</div>
28055:                 <div class="mcms-row"><span class="mcms-row-label">Mobile Mode · iOS Safari</span><select class="mcms-select" data-setting="mobile-mode"><option value="auto">Auto detect iPhone</option><option value="on">Always on</option><option value="off">Always off</option></select></div>
28056:                 <div class="mcms-row"><span class="mcms-row-label">Tablet Mode</span><select class="mcms-select" data-setting="tablet-mode"><option value="auto">Auto detect</option><option value="on">Always on</option><option value="off">Always off</option></select></div>
28057:                 <div class="mcms-status" data-device-layout-status>Detecting device layout…</div>
28058:                 <div class="mcms-status">Mobile Mode is tuned for iPhone Safari with Tampermonkey: a map-aware 5×2 command grid in portrait, a compact single-row dock where space allows, full-width safe-area bottom sheets, 16px form controls to prevent Safari input zoom, and Visual Viewport handling for the iOS keyboard. Tablet and desktop layouts remain separate and unchanged.</div>
28059:                 <div class="mcms-section-label">Dock position</div>
28060:                 <div class="mcms-position-grid">${positionButtons}</div>
28061:                 <div class="mcms-desktop-position-controls">
28062:                     <div class="mcms-section-label">Fine nudge</div>
28063:                     <div class="mcms-nudge-grid">
28064:                         <button class="mcms-small-btn" type="button" data-action="nudge-left">←</button>
28065:                         <button class="mcms-small-btn" type="button" data-action="nudge-up">↑</button>
28066:                         <button class="mcms-small-btn" type="button" data-action="nudge-down">↓</button>
28067:                         <button class="mcms-small-btn" type="button" data-action="nudge-right">→</button>
28068:                         <button class="mcms-small-btn" type="button" data-action="nudge-reset">0</button>
28069:                     </div>
28070:                     <div class="mcms-status mcms-nudge-value">X 0 / Y 0</div>
28071:                     <div class="mcms-section-label">Menu panel</div>
28072:                     <div class="mcms-nudge-grid">
28073:                         <button class="mcms-small-btn" type="button" data-action="panel-left">←</button>
28074:                         <button class="mcms-small-btn" type="button" data-action="panel-up">↑</button>
28075:                         <button class="mcms-small-btn" type="button" data-action="panel-down">↓</button>
28076:                         <button class="mcms-small-btn" type="button" data-action="panel-right">→</button>
28077:                         <button class="mcms-small-btn" type="button" data-action="panel-reset">↺</button>
28078:                     </div>
28079:                 </div>
28080:                 <div class="mcms-section-label">Behaviour</div>
28081:                 <div class="mcms-grid-2">
28082:                     ${makeToggleButton('shortcuts', '⌨', 'Keys', 'Keyboard shortcuts on/off. Map tools: 1–9. Vehicle Codes: V. Mission Age Watch: W. Menu: M.')}
28083:                     ${makeToggleButton('autoLoadAllVehicles', '⇊', 'Auto-load all vehicles', 'Automatically presses MissionChief’s Load more vehicles control whenever an opened mission limits the vehicle list.')}
28084:                     ${makeToggleButton('autoNight', '◑', 'AutoNight', 'Automatically switch skins by time.')}
28085:                     ${makeToggleButton('allianceBuildingsMapBlocker', '▦', 'Map Blocker', 'Blocks the heavy map in the Alliance Buildings menu (Courses menu). ON means blocked. Reload required.')}
28086:                     ${makeToggleButton('majorIncidentFeed', '▰', 'Incident Feed', 'Theme-aware major incident ticker in the top status bar. Hover pauses; click a mission to zoom.')}
28087:                     ${makeToggleButton('missionLockAudio', '⌁', 'Tracking Audio', 'Plays a short synthesized digital tracking cue during mission zoom and target acquisition.')}
28088:                 </div>
28089:                 <div class="mcms-row"><span class="mcms-row-label">Major incident threshold</span><select class="mcms-select" data-setting="major-incident-minimum"><option value="10000">10,000+ credits</option><option value="25000">25,000+ credits</option><option value="50000">50,000+ credits</option><option value="100000">100,000+ credits</option></select></div>
28090:                 <div class="mcms-status">The Incident Feed shows qualifying personal and alliance missions in the top status bar. Exceptionally old, stuck or mass-casualty incidents can appear regardless of the credit threshold. Hover pauses the feed; click an item to zoom to it.</div>
28091:                 <div class="mcms-status"><strong>Map Blocker ON</strong> is the performance mode for the Alliance Buildings menu (Courses menu). It removes that page's map, expands the courses list to full width and prevents its heavy marker layer attaching.</div>
28092:                 <div class="mcms-section-label">Auto Night</div>
28093:                 <div class="mcms-row"><span class="mcms-row-label">Night starts</span><input class="mcms-input" type="time" data-setting="auto-night-start"></div>
28094:                 <div class="mcms-row"><span class="mcms-row-label">Day starts</span><input class="mcms-input" type="time" data-setting="auto-day-start"></div>
28095:                 <div class="mcms-row"><span class="mcms-row-label">Night skin</span><select class="mcms-select" data-setting="auto-night-theme">${buildThemeOptions(state.autoNight.nightTheme)}</select></div>
28096:                 <div class="mcms-row"><span class="mcms-row-label">Day skin</span><select class="mcms-select" data-setting="auto-day-theme">${buildThemeOptions(state.autoNight.dayTheme)}</select></div>
28097:                 <div class="mcms-section-label">Saved Map Profiles</div>
28098:                 <div class="mcms-profile-list" data-profile-list></div>
28099:                 <div class="mcms-status">Profiles save your map location, zoom, skin, visibility filters and operational overlays.</div>
28100:                 <div class="mcms-section-label">Economy Mode</div>
28101:                 <div class="mcms-status mcms-economy-status">Use the leaf button beside the map-menu opener. Economy Mode preserves every module while reducing animations, map-layer pressure and background refresh frequency.</div>
28102:                 <div class="mcms-section-label">Settings Backup</div>
28103:                 <div class="mcms-config-actions">
28104:                     <button class="mcms-small-btn" type="button" data-action="export-config" title="Export every toolkit setting, private integration, profile, bookmark and Financial Archive history" aria-label="Export all toolkit settings">Export All</button>
28105:                     <button class="mcms-small-btn" type="button" data-action="import-config" title="Import a current or legacy toolkit settings backup" aria-label="Import all toolkit settings">Import All</button>
28106:                     <button class="mcms-small-btn" type="button" data-action="reset-config">Reset</button>
28107:                 </div>
28108:                 <input class="mcms-hidden-file" type="file" accept="application/json,text/json,.json" data-import-config-file>
28109:                 <div class="mcms-status">Backups include every persistent toolkit preference, desktop/Tablet/iOS layout choice, profile, bookmark, saved Discord webhook and local Financial Archive history. A clear private-file warning is shown before export and import. Store the JSON securely. Current and legacy toolkit backup files are supported.</div>
28110:             </section>
28111:             <div class="mcms-footer">
28112:                 <span>Audited runtime: compact Smart Bookmark Labels, responsive modes and every interface theme remain fully preserved.</span>
28113:                 <span class="mcms-build">${SCRIPT.name} v${SCRIPT.version} · MIT · ${SCRIPT.author}</span>
28114:             </div>
28115:         `;
28116: 
28117:         const tabList = panel.querySelector('.mcms-tabs');
28118:         if (tabList) tabList.setAttribute('role', 'tablist');
28119:         panel.querySelectorAll('.mcms-tab-btn').forEach(button => {
28120:             const tab = button.dataset.tab;
28121:             button.id = `mcms-tab-${tab}`;
28122:             button.setAttribute('role', 'tab');
28123:             button.setAttribute('aria-controls', `mcms-tabpanel-${tab}`);
28124:             button.setAttribute('aria-selected', 'false');
28125:             button.tabIndex = -1;
28126:         });
28127:         panel.querySelectorAll('.mcms-tab-panel').forEach(tabPanel => {
28128:             const tab = tabPanel.dataset.panel;
28129:             tabPanel.id = `mcms-tabpanel-${tab}`;
28130:             tabPanel.setAttribute('role', 'tabpanel');
28131:             tabPanel.setAttribute('aria-labelledby', `mcms-tab-${tab}`);
28132:             tabPanel.hidden = true;
28133:         });
28134: 
28135:         panel.addEventListener('keydown', event => {
28136:             const current = closestEventTarget(event, '.mcms-tab-btn');
28137:             if (!current || !['ArrowLeft', 'ArrowRight', 'Home', 'End'].includes(event.key)) return;
28138:             const buttons = Array.from(panel.querySelectorAll('.mcms-tab-btn'));
28139:             const currentIndex = Math.max(0, buttons.indexOf(current));
28140:             const nextIndex = event.key === 'Home' ? 0
28141:                 : event.key === 'End' ? buttons.length - 1
28142:                 : (currentIndex + (event.key === 'ArrowRight' ? 1 : -1) + buttons.length) % buttons.length;
28143:             event.preventDefault();
28144:             const nextButton = buttons[nextIndex];
28145:             setActiveTab(nextButton.dataset.tab);
28146:             nextButton.focus({ preventScroll: true });
28147:         });
28148: 
28149:         panel.addEventListener('click', event => {
28150:             const closeButton = closestEventTarget(event, '.mcms-close');
28151:             const tabButton = closestEventTarget(event, '.mcms-tab-btn');
28152:             const uiThemeButton = closestEventTarget(event, '.mcms-ui-theme-btn');
28153:             const themeButton = closestEventTarget(event, '.mcms-theme-btn');
28154:             const toggleButton = closestEventTarget(event, '[data-toggle]');
28155:             const positionButton = closestEventTarget(event, '.mcms-position-btn');
28156:             const actionButton = closestEventTarget(event, '[data-action]');
28157:             if (closeButton) { closePanel({ restoreFocus: true }); return; }
28158:             if (tabButton) { setActiveTab(tabButton.dataset.tab); return; }
28159:             if (uiThemeButton) { applyUiTheme(uiThemeButton.dataset.uiTheme, true); return; }
28160:             if (themeButton) { applyTheme(themeButton.dataset.theme, true); return; }
28161:             if (toggleButton) { toggleFeature(toggleButton.dataset.toggle); return; }
28162:             if (positionButton) { applyPosition(positionButton.dataset.position, true); return; }
28163:             if (actionButton) {
28164:                 event.preventDefault();
28165:                 handleAction(actionButton);
28166:                 return;
28167:             }
28168:         });
28169: 
28170:         panel.addEventListener('change', event => handleSettingChange(event.target));
28171: 
28172:         const dragHandle = panel.querySelector('.mcms-drag-handle');
28173:         if (dragHandle) {
28174:             dragHandle.addEventListener('mousedown', startPanelDrag, true);
28175:             dragHandle.addEventListener('touchstart', startPanelDrag, { capture: true, passive: false });
28176:         }
28177: 
28178:         ['click', 'dblclick', 'mousedown', 'mouseup', 'mousemove', 'wheel', 'contextmenu', 'touchstart', 'touchmove', 'touchend'].forEach(eventName => {
28179:             panel.addEventListener(eventName, event => event.stopPropagation(), { passive: false });
28180:         });
28181: 
28182:         document.body.appendChild(panel);
28183:         const importInput = panel.querySelector('[data-import-config-file]');
28184:         if (importInput) {
28185:             importInput.addEventListener('change', () => {
28186:                 const file = importInput.files?.[0];
28187:                 if (file) importToolkitConfigFile(file);
28188:                 importInput.value = '';
28189:             });
28190:         }
28191:         const financeImportInput = panel.querySelector('[data-import-finance-file]');
28192:         if (financeImportInput) {
28193:             financeImportInput.addEventListener('change', () => {
28194:                 const file = financeImportInput.files?.[0];
28195:                 if (file) importFinancialArchiveFile(file);
28196:                 financeImportInput.value = '';
28197:             });
28198:         }
28199:         renderQuickPlaces();
28200:         renderBookmarks();
28201:         renderProfiles();
28202:         updateUI();
28203:         recordStartupMetric('settingsPanelBuildMs', panelStartedAt, { settingsPanelLazy: true });
28204:         return panel;
28205:     }
28206: 
28207:     function renderQuickPlaces() {
28208:         const list = document.querySelector(`#${SCRIPT.panelId} .mcms-quick-list`);
28209:         if (!list) return;
28210:         list.innerHTML = QUICK_PLACES.map(place => `
28211:             <div class="mcms-quick-row">
28212:                 <button class="mcms-place-main" type="button" data-action="place-go" data-place="${place.id}" title="Jump to ${escapeHtml(place.name)}">
28213:                     <span class="mcms-iconbox">⌖</span><span class="mcms-text"><span class="mcms-label">${escapeHtml(place.name)}</span><span class="mcms-pill">${place.label}</span></span>
28214:                 </button>
28215:                 <button class="mcms-pin-btn ${state.quickPins[place.id] ? 'mcms-on' : ''}" type="button" data-action="quick-pin" data-place="${place.id}" title="Pin as persistent screen shortcut">${state.quickPins[place.id] ? 'ON' : 'PIN'}</button>
28216:             </div>
28217:         `).join('');
28218:     }
28219: 
28220:     function renderBookmarks() {
28221:         const list = document.querySelector(`#${SCRIPT.panelId} .mcms-bookmark-list`);
28222:         if (!list) return;
28223:         list.innerHTML = state.bookmarks.map((bookmark, index) => {
28224:             if (!bookmark) {
28225:                 return `<div class="mcms-bookmark-row"><span class="mcms-bookmark-name">Slot ${index + 1} empty</span><span></span><span></span><button class="mcms-bookmark-btn" type="button" data-action="bookmark-save" data-slot="${index}">Save</button><span></span></div>`;
28226:             }
28227:             const screenLabel = bookmarkScreenLabel(bookmark);
28228:             const labelMode = bookmark.shortLabel ? 'CUSTOM' : 'AUTO';
28229:             const labelTitle = `${bookmark.name} · Screen label: ${screenLabel} (${labelMode.toLowerCase()})`;
28230:             return `
28231:                 <div class="mcms-bookmark-row">
28232:                     <button class="mcms-bookmark-name mcms-bookmark-name-btn" type="button" data-action="bookmark-label" data-slot="${index}" title="${escapeHtml(labelTitle)}" aria-label="Edit ${escapeHtml(bookmark.name)} name and short label">
28233:                         <span class="mcms-bookmark-name-main">${escapeHtml(bookmark.name)}</span>
28234:                         <span class="mcms-bookmark-short">${escapeHtml(screenLabel)} · ${labelMode}</span>
28235:                     </button>
28236:                     <button class="mcms-bookmark-btn" type="button" data-action="bookmark-go" data-slot="${index}">Go</button>
28237:                     <button class="mcms-pin-btn ${bookmark.pinned ? 'mcms-on' : ''}" type="button" data-action="bookmark-pin" data-slot="${index}" title="Pin as persistent screen shortcut">${bookmark.pinned ? 'ON' : 'PIN'}</button>
28238:                     <button class="mcms-bookmark-btn" type="button" data-action="bookmark-save" data-slot="${index}" title="Update this bookmark from the current map view">Save</button>
28239:                     <button class="mcms-bookmark-btn" type="button" data-action="bookmark-delete" data-slot="${index}">×</button>
28240:                 </div>`;
28241:         }).join('');
28242:     }
28243: 
28244:     function renderScreenPins() {
28245:         const dock = document.querySelector(`#${SCRIPT.controlId} .mcms-screen-pins`);
28246:         if (!dock) return;
28247:         const entries = [];
28248:         for (const place of QUICK_PLACES) {
28249:             if (!state.quickPins[place.id]) continue;
28250:             entries.push({
28251:                 kind: 'quick',
28252:                 id: place.id,
28253:                 fullName: place.name,
28254:                 baseLabel: sanitiseBookmarkShortLabel(place.label) || makeSmartBookmarkLabel(place.name)
28255:             });
28256:         }
28257:         state.bookmarks.forEach((bookmark, index) => {
28258:             if (!bookmark || !bookmark.pinned) return;
28259:             entries.push({
28260:                 kind: 'bookmark',
28261:                 index,
28262:                 fullName: bookmark.name,
28263:                 baseLabel: bookmarkScreenLabel(bookmark)
28264:             });
28265:         });
28266: 
28267:         dock.innerHTML = resolveScreenPinLabels(entries).map(entry => {
28268:             const action = entry.kind === 'quick'
28269:                 ? `data-action="place-go" data-place="${escapeHtml(entry.id)}"`
28270:                 : `data-action="bookmark-go" data-slot="${entry.index}"`;
28271:             const className = entry.kind === 'quick' ? 'mcms-pin-quick' : 'mcms-pin-custom';
28272:             return `<button class="mcms-screen-pin-btn ${className}" type="button" ${action} data-full-label="${escapeHtml(entry.fullName)}" data-smart-label="${escapeHtml(entry.label)}" title="Jump to ${escapeHtml(entry.fullName)}" aria-label="Jump to ${escapeHtml(entry.fullName)}">${escapeHtml(entry.label)}</button>`;
28273:         }).join('');
28274:         if (isTouchLayoutActive()) fitControlToMap();
28275:     }
28276: 
28277:     function handleAction(button) {
28278:         const action = button.dataset.action;
28279:         if (action === 'place-go') {
28280:             const place = QUICK_PLACES.find(item => item.id === button.dataset.place);
28281:             if (place && setMapView(place.lat, place.lng, place.zoom)) showToast(place.name);
28282:             return;
28283:         }
28284:         if (action === 'quick-pin') { toggleQuickPin(button.dataset.place); return; }
28285:         if (action === 'bookmark-save') { saveBookmark(Number(button.dataset.slot)); return; }
28286:         if (action === 'bookmark-label') { editBookmarkLabel(Number(button.dataset.slot)); return; }
28287:         if (action === 'bookmark-go') { goBookmark(Number(button.dataset.slot)); return; }
28288:         if (action === 'bookmark-delete') { deleteBookmark(Number(button.dataset.slot)); return; }
28289:         if (action === 'bookmark-pin') { toggleBookmarkPin(Number(button.dataset.slot)); return; }
28290:         if (action === 'nudge-left') { nudgeControl(-4, 0); return; }
28291:         if (action === 'nudge-right') { nudgeControl(4, 0); return; }
28292:         if (action === 'nudge-up') { nudgeControl(0, -4); return; }
28293:         if (action === 'nudge-down') { nudgeControl(0, 4); return; }
28294:         if (action === 'nudge-reset') { resetNudge(); return; }
28295:         if (action === 'panel-left') { nudgePanel(-24, 0); return; }
28296:         if (action === 'panel-right') { nudgePanel(24, 0); return; }
28297:         if (action === 'panel-up') { nudgePanel(0, -24); return; }
28298:         if (action === 'panel-down') { nudgePanel(0, 24); return; }
28299:         if (action === 'open-help-center') { openHelpCenter(); return; }
28300:         if (action === 'toggle-economy') { setEconomyMode(!state.economyMode, true); return; }
28301:         if (action === 'open-critical-drawer') { toggleCriticalDrawer(); return; }
28302:         if (action === 'open-vehicle-status') { toggleVehicleCodeStatus(); return; }
28303:         if (action === 'fit-critical') { fitCriticalMissions(); return; }
28304:         if (action === 'scan-transport-sweep') { const queue = buildTransportSweepQueue(); showToast(queue.length ? `${queue.length} transport mission${queue.length === 1 ? '' : 's'} found` : 'No alliance patient transports found'); return; }
28305:         if (action === 'start-transport-sweep') { startTransportSweep(); return; }
28306:         if (action === 'stop-transport-sweep') { stopTransportSweep(); return; }
28307:         if (action === 'reset-session') { resetSessionPerformance(); return; }
28308:         if (action === 'clear-payout-history') { clearPayoutHistory(); return; }
28309:         if (action === 'critical-go') { focusMissionById(button.dataset.missionId, false); return; }
28310:         if (action === 'profile-save') { saveMapProfile(Number(button.dataset.slot)); return; }
28311:         if (action === 'profile-load') { loadMapProfile(Number(button.dataset.slot)); return; }
28312:         if (action === 'profile-delete') { deleteMapProfile(Number(button.dataset.slot)); return; }
28313:         if (action === 'export-config') { exportToolkitConfig(); return; }
28314:         if (action === 'import-config') { document.querySelector(`#${SCRIPT.panelId} [data-import-config-file]`)?.click?.(); return; }
28315:         if (action === 'reset-config') { resetToolkitConfiguration(); return; }
28316:         if (action === 'discord-test') { testDiscordWebhook(); return; }
28317:         if (action === 'discord-generate-post') { postDiscordFinancialReport(); return; }
28318:         if (action === 'discord-clear') { clearDiscordWebhook(); return; }
28319:         if (action === 'finance-archive-scan') { scanFinancialArchive(); return; }
28320:         if (action === 'finance-archive-cancel') { cancelFinancialArchiveScan(); return; }
28321:         if (action === 'finance-archive-export') { exportFinancialArchive(); return; }
28322:         if (action === 'finance-archive-import') { document.querySelector(`#${SCRIPT.panelId} [data-import-finance-file]`)?.click?.(); return; }
28323:         if (action === 'finance-archive-clear') { clearFinancialArchive(); return; }
28324:         if (action === 'finance-rules-refresh') { refreshFinancialIntelligenceFeeds(true).then(() => { renderFinanceVaultStatus(); showToast('GitHub financial intelligence refreshed'); }); return; }
28325:         if (action === 'test-payout-flash') {
28326:             const testAmount = Math.max(1000, Number(document.querySelector(`#${SCRIPT.panelId} [data-setting="payout-test-amount"]`)?.value) || state.payoutFlash.threshold);
28327:             const triggered = triggerPayoutFlash(testAmount, true, { source: 'personal', caption: 'Emergency Response Test' });
28328:             showToast(triggered ? 'Emergency flash test' : 'Emergency flash unavailable: map not detected');
28329:             return;
28330:         }
28331:         if (action === 'panel-reset') resetPanelPosition();
28332:     }
28333: 
28334:     function handleSettingChange(target) {
28335:         const setting = target.dataset.setting;
28336:         if (!setting) return;
28337: 
28338:         if (setting === 'mobile-mode' || setting === 'tablet-mode') {
28339:             const nextValue = ['auto', 'on', 'off'].includes(String(target.value)) ? String(target.value) : 'auto';
28340:             const previousLayout = activeDeviceLayout;
28341:             if (setting === 'mobile-mode') {
28342:                 state.mobileMode = nextValue;
28343:                 if (nextValue === 'on') state.tabletMode = 'off';
28344:             } else {
28345:                 state.tabletMode = nextValue;
28346:                 if (nextValue === 'on') state.mobileMode = 'off';
28347:             }
28348:             saveState();
28349:             applyRootAttributes();
28350:             refreshTabletModeUi();
28351:             if (previousLayout !== activeDeviceLayout && !isTouchLayoutActive()) {
28352:                 clearTabletPanelSizing();
28353:                 clearTabletDockSizing();
28354:             }
28355:             fitControlToMap();
28356:             positionPanelOverlay(true);
28357:             showToast(activeDeviceLayout === 'mobile' ? 'iOS Mobile Mode active' : activeDeviceLayout === 'tablet' ? 'Tablet Mode active' : 'Desktop layout active');
28358:             return;
28359:         }
28360: 
28361:         if (setting === 'major-incident-minimum') {
28362:             state.majorIncidentFeed.minimumCredits = MAJOR_INCIDENT_FEED_MINIMUM_OPTIONS.includes(Number(target.value)) ? Number(target.value) : 25000;
28363:             saveState();
28364:             updateUI();
28365:             refreshMissionSnapshots();
28366:             scheduleMajorIncidentFeedRender(0);
28367:             showToast(`Major Incident Feed: ${formatOperationalCompactCredits(state.majorIncidentFeed.minimumCredits)}+ credits`);
28368:             return;
28369:         }
28370: 
28371:         if (setting === 'coverage-radius') {
28372:             state.coverage.radiusMi = Number(target.value) || 10;
28373:             saveState();
28374:             updateUI();
28375:             scheduleCoverageRefresh();
28376:             return;
28377:         }
28378: 
28379:         if (setting === 'heatmap-source') state.heatmap.source = target.value === 'vehicles' ? 'vehicles' : 'stations';
28380:         if (setting === 'heatmap-service') state.heatmap.service = ['all', 'fire', 'ambulance', 'police', 'air', 'water'].includes(target.value) ? target.value : 'all';
28381:         if (setting === 'heatmap-radius') state.heatmap.radiusMi = Number(target.value) || 10;
28382:         if (setting === 'heatmap-opacity') state.heatmap.opacity = clamp(target.value, 0.12, 0.55, 0.30);
28383:         if (setting.startsWith('heatmap-')) {
28384:             saveState(); updateUI(); scheduleHeatmapRefresh(); return;
28385:         }
28386: 
28387: 
28388:         if (setting === 'transport-sweep-delay') {
28389:             state.transportSweep.delayMs = TRANSPORT_SWEEP_DELAY_OPTIONS.includes(Number(target.value)) ? Number(target.value) : 2000;
28390:             saveState(); updateUI();
28391:             showToast(`Transport Sweep delay: ${state.transportSweep.delayMs / 1000}s`);
28392:             return;
28393:         }
28394:         if (setting === 'transport-sweep-max') {
28395:             state.transportSweep.maxPerRun = Math.round(clamp(target.value, 1, TRANSPORT_SWEEP_MAX_REQUESTS, 25));
28396:             saveState(); updateUI();
28397:             showToast(`Transport Sweep maximum: ${state.transportSweep.maxPerRun}`);
28398:             return;
28399:         }
28400: 
28401:         if (setting === 'resource-gap-radius') {
28402:             state.resourceGap.radiusMi = RESOURCE_GAP_RADIUS_OPTIONS.includes(Number(target.value)) ? Number(target.value) : 25;
28403:             resourceGapAnalysisCache.clear();
28404:             saveState(); updateUI(); scheduleResourceGapRefresh(0); refreshVisibleMissionInspector();
28405:             showToast(`Resource Gap radius: ${state.resourceGap.radiusMi}mi`);
28406:             return;
28407:         }
28408: 
28409:         if (setting === 'stuck-threshold') {
28410:             state.stuckDetector.thresholdMin = Math.round(clamp(target.value, STUCK_MIN_MINUTES, STUCK_MAX_MINUTES, 20));
28411:             saveState();
28412:             updateUI();
28413:             scheduleStuckMissionRefresh(0);
28414:             showToast(`Stuck missions: ${state.stuckDetector.thresholdMin} minutes`);
28415:             return;
28416:         }
28417: 
28418:         if (setting === 'alliance-credit-minimum') {
28419:             state.allianceCreditMinimum = [0, 5000, 10000, 15000, 20000].includes(Number(target.value)) ? Number(target.value) : 0;
28420:             saveState();
28421:             updateUI();
28422:             scheduleAllianceCreditRefresh(0);
28423:             showToast(state.allianceCreditMinimum ? `Alliance credits: ${state.allianceCreditMinimum / 1000}K+` : 'Alliance credits: all values');
28424:             return;
28425:         }
28426: 
28427:         if (setting === 'discord-webhook') {
28428:             try {
28429:                 saveDiscordWebhookUrl(target.value);
28430:                 setDiscordStatus(target.value ? 'Webhook saved securely in Tampermonkey storage.' : 'Webhook removed.', 'good');
28431:             } catch (err) {
28432:                 setDiscordStatus(err?.message || 'Webhook URL is invalid.', 'bad');
28433:             }
28434:             return;
28435:         }
28436:         if (setting === 'discord-name') {
28437:             state.discordReport.webhookName = String(target.value || 'MissionChief Finance').trim().slice(0, 80) || 'MissionChief Finance';
28438:             saveState(); updateUI();
28439:             return;
28440:         }
28441:         if (setting === 'discord-top-categories') {
28442:             state.discordReport.topCategories = [3, 5, 8].includes(Number(target.value)) ? Number(target.value) : 5;
28443:             invalidateDiscordFinancialPreview();
28444:             saveState(); updateUI();
28445:             return;
28446:         }
28447:         if (setting === 'discord-period') {
28448:             state.discordReport.period = ['today', 'yesterday', 'last24', 'last7', 'last30', 'last90', 'last180', 'last365', 'allAvailable', 'session', 'sinceLast', 'custom'].includes(target.value) ? target.value : 'today';
28449:             invalidateDiscordFinancialPreview();
28450:             saveState(); updateUI();
28451:             return;
28452:         }
28453:         if (setting === 'discord-custom-start' || setting === 'discord-custom-end') {
28454:             const key = setting === 'discord-custom-start' ? 'customStart' : 'customEnd';
28455:             if (/^\d{4}-\d{2}-\d{2}$/u.test(String(target.value || ''))) state.discordReport[key] = String(target.value);
28456:             invalidateDiscordFinancialPreview();
28457:             saveState(); updateUI();
28458:             return;
28459:         }
28460:         if (setting === 'discord-comparison') {
28461:             state.discordReport.includeComparison = String(target.value) !== 'false';
28462:             invalidateDiscordFinancialPreview();
28463:             saveState(); updateUI();
28464:             return;
28465:         }
28466:         if (setting === 'discord-chart') {
28467:             state.discordReport.includeChart = String(target.value) !== 'false';
28468:             invalidateDiscordFinancialPreview();
28469:             saveState(); updateUI();
28470:             return;
28471:         }
28472: 
28473:         if (setting === 'discord-report-mode') {
28474:             state.discordReport.reportMode = ['executive', 'fullAudit'].includes(String(target.value)) ? String(target.value) : 'fullAudit';
28475:             invalidateDiscordFinancialPreview();
28476:             saveState(); updateUI();
28477:             return;
28478:         }
28479:         if (setting === 'discord-risk' || setting === 'discord-forecast') {
28480:             const key = setting === 'discord-risk' ? 'includeRisk' : 'includeForecast';
```

## Navigation, control-grid and label-layout anchors

### Lines 1369-1385

```text
01369:     let helpGuideLoadPromise = null;
01370:     let helpCenterReturnFocus = null;
01371: 
01372:     function defaultState() {
01373:         return {
01374:             uiTheme: 'mapCommand',
01375:             theme: getLegacyTheme(),
01376:             position: getLegacyPosition(),
01377:             activeTab: 'skins',
01378:             cleanMode: false,
01379:             markerFocus: false,
01380:             missionPulse: false,
01381:             roadPriority: false,
01382:             compactDock: false,
01383:             commandBarOpen: true,
01384:             economyMode: false,
01385:             tabletMode: 'auto',
```

### Lines 1460-1477

```text
01460:         };
01461: 
01462:         while (merged.bookmarks.length < 5) merged.bookmarks.push(null);
01463:         while (merged.profiles.length < MAP_PROFILE_LIMIT) merged.profiles.push(null);
01464: 
01465:         merged.uiTheme = normaliseUiTheme(merged.uiTheme);
01466:         merged.theme = normaliseTheme(merged.theme);
01467:         merged.position = POSITIONS[merged.position] ? merged.position : 'bl';
01468:         if (merged.activeTab === 'fleet') merged.activeTab = 'resources';
01469:         merged.activeTab = ['skins', 'tools', 'resources', 'ops', 'payouts', 'discord', 'places', 'settings'].includes(merged.activeTab) ? merged.activeTab : 'skins';
01470:         delete merged.fleetFilter;
01471:         merged.nudge.x = clamp(merged.nudge.x, -220, 220, 0);
01472:         merged.nudge.y = clamp(merged.nudge.y, -220, 220, 0);
01473:         merged.coverage.radiusMi = Number(merged.coverage.radiusMi) || 10;
01474:         merged.heatmap.radiusMi = Number(merged.heatmap.radiusMi) || 10;
01475:         merged.heatmap.opacity = clamp(merged.heatmap.opacity, 0.12, 0.55, 0.30);
01476:         merged.allianceCreditMinimum = [0, 5000, 10000, 15000, 20000].includes(Number(merged.allianceCreditMinimum)) ? Number(merged.allianceCreditMinimum) : 0;
01477:         merged.commandBarOpen = merged.commandBarOpen !== false;
```

### Lines 2131-2165

```text
02131:             border:1px solid color-mix(in srgb,var(--mcms-lock-primary) 74%,transparent) !important;
02132:             border-left:3px solid var(--mcms-lock-accent) !important;
02133:             border-radius:3px !important;
02134:             background:var(--mcms-lock-surface) !important;
02135:             color:var(--mcms-lock-secondary) !important;
02136:             box-shadow:0 5px 14px rgba(0,0,0,.38),0 0 10px color-mix(in srgb,var(--mcms-lock-primary) 24%,transparent) !important;
02137:             transform:translateX(-50%) translateY(6px) !important;
02138:             opacity:0 !important;
02139:             white-space:nowrap !important;
02140:             overflow:hidden !important;
02141:             text-overflow:ellipsis !important;
02142:             animation:mcmsIntelLabel 1550ms ease 1450ms both !important;
02143:         }
02144:         .mcms-mission-lock-label strong {
02145:             display:block !important;
02146:             color:var(--mcms-lock-primary) !important;
02147:             font:950 8px/1 Arial,Helvetica,sans-serif !important;
02148:             letter-spacing:1px !important;
02149:             text-transform:uppercase !important;
02150:         }
02151:         .mcms-mission-lock-label small {
02152:             display:block !important;
02153:             margin-top:3px !important;
02154:             color:var(--mcms-lock-secondary) !important;
02155:             font:800 8px/1.1 Arial,Helvetica,sans-serif !important;
02156:             overflow:hidden !important;
02157:             text-overflow:ellipsis !important;
02158:         }
02159:         .leaflet-marker-icon.mcms-mission-lock-target {
02160:             animation:mcmsIntelMarkerPulse 2.65s ease-in-out 920ms both !important;
02161:             z-index:1500 !important;
02162:         }
02163: 
02164:         html[data-mcms-ui-theme="cyberpunk"] .mcms-mission-lock-travel-overlay,
02165:         html[data-mcms-ui-theme="cyberpunk"] .mcms-mission-lock-dom,
```

### Lines 2314-2343

```text
02314:             text-align: left !important; overflow: hidden !important;
02315:         }
02316:         #${SCRIPT.controlId} .mcms-float-key {
02317:             width: 17px !important; height: 17px !important; border-radius: 6px !important; background: rgba(255,255,255,.12) !important;
02318:             display: flex !important; align-items: center !important; justify-content: center !important; color: #fff !important;
02319:             font-size: 9px !important; line-height: 1 !important; font-weight: 900 !important;
02320:         }
02321:         #${SCRIPT.controlId} .mcms-float-label {
02322:             min-width: 0 !important; overflow: hidden !important; text-overflow: ellipsis !important; white-space: nowrap !important;
02323:             font-size: 8.5px !important; line-height: 1 !important; font-weight: 900 !important;
02324:         }
02325:         #${SCRIPT.controlId} .mcms-float-label-tablet,
02326:         #${SCRIPT.controlId} .mcms-float-label-mobile { display: none !important; }
02327:         #${SCRIPT.controlId} .mcms-float-btn.mcms-on { background: rgba(25,118,210,.78) !important; color: #fff !important; border-color: rgba(120,190,255,.8) !important; }
02328:         #${SCRIPT.controlId} .mcms-float-btn.mcms-on .mcms-float-key { background: rgba(255,255,255,.22) !important; }
02329:         #${SCRIPT.controlId} .mcms-screen-pins {
02330:             display: grid !important; grid-template-columns: repeat(2, minmax(0, 1fr)) !important; gap: 4px !important; margin-top: 6px !important;
02331:             width: 160px !important; max-height: 156px !important; overflow-y: auto !important; overflow-x: hidden !important; scrollbar-width: thin !important;
02332:         }
02333:         #${SCRIPT.controlId} .mcms-screen-pins:empty { display: none !important; }
02334:         #${SCRIPT.controlId} .mcms-screen-pin-btn {
02335:             height: 25px !important; min-width: 0 !important; padding: 0 6px !important; white-space: nowrap !important; overflow: hidden !important; text-overflow: ellipsis !important; color: #fff !important;
02336:         }
02337:         #${SCRIPT.controlId} .mcms-screen-pin-btn.mcms-pin-quick { background: rgba(16,78,138,.86) !important; border-color: rgba(86,169,255,.68) !important; }
02338:         #${SCRIPT.controlId} .mcms-screen-pin-btn.mcms-pin-custom { background: rgba(106,80,10,.88) !important; border-color: rgba(255,213,79,.70) !important; }
02339: 
02340:         #${SCRIPT.panelId} {
02341:             display: none !important;
02342:             position: fixed !important;
02343:             width: 318px !important;
```

### Lines 2380-2404

```text
02380:             flex: none !important;
02381:             position: sticky !important;
02382:             top: 0 !important;
02383:             z-index: 30 !important;
02384:             overflow: visible !important;
02385:             transform: none !important;
02386:         }
02387:         html[data-mcms-device-layout="desktop"] body #${SCRIPT.panelId} > .mcms-panel-sticky-stack .mcms-header,
02388:         html[data-mcms-device-layout="desktop"] body #${SCRIPT.panelId} > .mcms-panel-sticky-stack .mcms-tabs {
02389:             flex: none !important;
02390:         }
02391:         html[data-mcms-device-layout="desktop"] body #${SCRIPT.panelId} > .mcms-tab-panel {
02392:             grid-row: 2 !important;
02393:             min-height: 0 !important;
02394:             max-height: 100% !important;
02395:         }
02396:         html[data-mcms-device-layout="desktop"] body #${SCRIPT.panelId} > .mcms-tab-panel.mcms-active {
02397:             display: block !important;
02398:             height: 100% !important;
02399:             min-height: 0 !important;
02400:             overflow-y: auto !important;
02401:             overflow-x: hidden !important;
02402:             overscroll-behavior: contain !important;
02403:             scrollbar-width: thin !important;
02404:             padding-right: 2px !important;
```

### Lines 2410-2517

```text
02410:             margin: 0 0 8px 0 !important; padding: 0 0 7px 0 !important; border-bottom: 1px solid rgba(255,255,255,.12) !important; overflow: hidden !important;
02411:         }
02412:         #${SCRIPT.panelId} .mcms-drag-handle {
02413:             min-width: 0 !important; cursor: grab !important; touch-action: none !important; user-select: none !important;
02414:             border-radius: 9px !important; padding: 4px 6px !important; background: rgba(255,255,255,.055) !important; border: 1px solid rgba(255,255,255,.075) !important;
02415:         }
02416:         #${SCRIPT.panelId} .mcms-drag-handle:hover { background: rgba(255,255,255,.10) !important; }
02417:         #${SCRIPT.panelId}.mcms-dragging .mcms-drag-handle { cursor: grabbing !important; }
02418:         #${SCRIPT.panelId} .mcms-title { display: block !important; font-size: 13px !important; line-height: 1.1 !important; font-weight: 900 !important; color: #f2f6ff !important; white-space: nowrap !important; overflow: hidden !important; text-overflow: ellipsis !important; }
02419:         #${SCRIPT.panelId} .mcms-subtitle { display: block !important; margin-top: 2px !important; font-size: 9px !important; line-height: 1.15 !important; color: rgba(233,238,245,.64) !important; white-space: nowrap !important; overflow: hidden !important; text-overflow: ellipsis !important; }
02420:         #${SCRIPT.panelId} .mcms-close, #${SCRIPT.panelId} .mcms-reset-panel, #${SCRIPT.panelId} .mcms-help-button {
02421:             width: 24px !important; height: 24px !important; border: 0 !important; border-radius: 8px !important; background: rgba(255,255,255,.10) !important;
02422:             color: rgba(255,255,255,.88) !important; cursor: pointer !important; font-size: 15px !important; line-height: 24px !important; text-align: center !important; padding: 0 !important;
02423:         }
02424:         #${SCRIPT.panelId} .mcms-close:hover, #${SCRIPT.panelId} .mcms-reset-panel:hover, #${SCRIPT.panelId} .mcms-help-button:hover, #${SCRIPT.panelId} .mcms-help-button:focus-visible { background: rgba(58,174,232,.28) !important; color:#fff !important; }
02425:         #${SCRIPT.panelId} .mcms-tabs { display: grid !important; grid-template-columns: repeat(4, minmax(0,1fr)) !important; gap: 5px !important; margin-bottom: 8px !important; }
02426:         #${SCRIPT.panelId} .mcms-tab-btn { height: 26px !important; border: 1px solid rgba(255,255,255,.13) !important; border-radius: 8px !important; background: rgba(255,255,255,.06) !important; color: rgba(255,255,255,.78) !important; cursor: pointer !important; font-size: 9px !important; line-height: 1 !important; font-weight: 900 !important; padding: 0 !important; overflow: hidden !important; }
02427:         #${SCRIPT.panelId} .mcms-tab-btn.mcms-active, #${SCRIPT.panelId} .mcms-theme-btn.mcms-active, #${SCRIPT.panelId} .mcms-toggle-btn.mcms-on, #${SCRIPT.panelId} .mcms-position-btn.mcms-active, #${SCRIPT.panelId} .mcms-pin-btn.mcms-on { background: rgba(25,118,210,.42) !important; border-color: rgba(120,190,255,.78) !important; color: #fff !important; }
02428:         #${SCRIPT.panelId} .mcms-tab-panel { display: none !important; }
02429:         #${SCRIPT.panelId} .mcms-tab-panel.mcms-active { display: block !important; }
02430:         #${SCRIPT.panelId} .mcms-grid-2 { display: grid !important; grid-template-columns: repeat(2, minmax(0,1fr)) !important; gap: 7px !important; width: 100% !important; min-width: 0 !important; overflow: hidden !important; }
02431:         #${SCRIPT.panelId} .mcms-theme-btn, #${SCRIPT.panelId} .mcms-toggle-btn, #${SCRIPT.panelId} .mcms-place-main {
02432:             width: 100% !important; min-width: 0 !important; height: 42px !important; border: 1px solid rgba(255,255,255,.13) !important; border-radius: 10px !important;
02433:             background: rgba(255,255,255,.065) !important; color: #eef4ff !important; padding: 6px !important; cursor: pointer !important; text-align: left !important;
02434:             display: grid !important; grid-template-columns: 20px minmax(0,1fr) !important; align-items: center !important; gap: 6px !important; overflow: hidden !important;
02435:         }
02436:         #${SCRIPT.panelId} .mcms-theme-btn:hover, #${SCRIPT.panelId} .mcms-toggle-btn:hover, #${SCRIPT.panelId} .mcms-place-main:hover { background: rgba(255,255,255,.14) !important; border-color: rgba(255,255,255,.30) !important; }
02437:         #${SCRIPT.panelId} .mcms-iconbox { width: 20px !important; height: 20px !important; min-width: 20px !important; border-radius: 7px !important; background: rgba(255,255,255,.11) !important; display: flex !important; align-items: center !important; justify-content: center !important; color: rgba(255,255,255,.86) !important; font-size: 10px !important; line-height: 1 !important; font-weight: 900 !important; overflow: hidden !important; }
02438:         #${SCRIPT.panelId} .mcms-text { display: block !important; min-width: 0 !important; max-width: 100% !important; overflow: hidden !important; }
02439:         #${SCRIPT.panelId} .mcms-label { display: block !important; width: 100% !important; color: #f4f7ff !important; font-size: 10.5px !important; line-height: 1.05 !important; font-weight: 900 !important; white-space: nowrap !important; overflow: hidden !important; text-overflow: ellipsis !important; }
02440:         #${SCRIPT.panelId} .mcms-pill { display: inline-block !important; margin-top: 4px !important; max-width: 78px !important; padding: 1px 5px !important; border-radius: 999px !important; background: rgba(255,255,255,.13) !important; color: rgba(255,255,255,.82) !important; font-size: 7.5px !important; line-height: 1.05 !important; font-weight: 900 !important; white-space: nowrap !important; overflow: hidden !important; }
02441:         #${SCRIPT.panelId} .mcms-section-label { margin: 9px 0 6px 0 !important; color: rgba(233,238,245,.62) !important; font-size: 9px !important; line-height: 1 !important; font-weight: 900 !important; letter-spacing: .55px !important; text-transform: uppercase !important; }
02442:         #${SCRIPT.panelId} .mcms-row { display: grid !important; grid-template-columns: minmax(0,1fr) 100px !important; gap: 7px !important; align-items: center !important; margin-bottom: 7px !important; }
02443:         #${SCRIPT.panelId} .mcms-row-label { color: rgba(255,255,255,.82) !important; font-size: 10px !important; font-weight: 800 !important; overflow: hidden !important; text-overflow: ellipsis !important; white-space: nowrap !important; }
02444:         #${SCRIPT.panelId} .mcms-input, #${SCRIPT.panelId} .mcms-select { width: 100% !important; height: 27px !important; border: 1px solid rgba(255,255,255,.14) !important; border-radius: 8px !important; background: rgba(255,255,255,.08) !important; color: #fff !important; font-size: 10px !important; font-weight: 800 !important; padding: 0 7px !important; }
02445:         #${SCRIPT.panelId} .mcms-select option { color: #111 !important; }
02446:         #${SCRIPT.panelId} .mcms-position-grid, #${SCRIPT.panelId} .mcms-nudge-grid { display: grid !important; grid-template-columns: repeat(4, minmax(0,1fr)) !important; gap: 6px !important; width: 100% !important; }
02447:         #${SCRIPT.panelId} .mcms-nudge-grid { grid-template-columns: repeat(5, minmax(0,1fr)) !important; }
02448:         #${SCRIPT.panelId} .mcms-position-btn, #${SCRIPT.panelId} .mcms-small-btn, #${SCRIPT.panelId} .mcms-bookmark-btn, #${SCRIPT.panelId} .mcms-pin-btn { width: 100% !important; min-width: 0 !important; height: 28px !important; border: 1px solid rgba(255,255,255,.13) !important; border-radius: 9px !important; background: rgba(255,255,255,.065) !important; color: rgba(255,255,255,.84) !important; cursor: pointer !important; font-size: 9px !important; line-height: 28px !important; font-weight: 900 !important; text-align: center !important; padding: 0 !important; overflow: hidden !important; }
02449:         #${SCRIPT.panelId} .mcms-position-btn:hover, #${SCRIPT.panelId} .mcms-small-btn:hover, #${SCRIPT.panelId} .mcms-bookmark-btn:hover, #${SCRIPT.panelId} .mcms-pin-btn:hover { background: rgba(255,255,255,.14) !important; }
02450:         #${SCRIPT.panelId} .mcms-quick-row { display: grid !important; grid-template-columns: minmax(0,1fr) 44px !important; gap: 6px !important; margin-bottom: 6px !important; }
02451:         #${SCRIPT.panelId} .mcms-bookmark-row { display: grid !important; grid-template-columns: minmax(0,1fr) 32px 38px 34px 26px !important; gap: 5px !important; align-items: center !important; margin-bottom: 5px !important; }
02452:         #${SCRIPT.panelId} .mcms-bookmark-name { color: rgba(255,255,255,.86) !important; font-size: 10px !important; font-weight: 850 !important; white-space: nowrap !important; overflow: hidden !important; text-overflow: ellipsis !important; }
02453:         #${SCRIPT.panelId} .mcms-status { margin-top: 8px !important; padding: 7px !important; border-radius: 9px !important; border: 1px solid rgba(255,255,255,.12) !important; background: rgba(255,255,255,.055) !important; color: rgba(255,255,255,.68) !important; font-size: 9px !important; line-height: 1.25 !important; }
02454:         #${SCRIPT.panelId} .mcms-input, #${SCRIPT.panelId} .mcms-select { user-select: text !important; }
02455:         #${SCRIPT.panelId} .mcms-discord-wide { grid-template-columns: 92px minmax(0,1fr) !important; }
02456:         #${SCRIPT.panelId} .mcms-discord-preview { margin-top:8px !important; min-height:72px !important; }
02457:         #${SCRIPT.panelId} .mcms-discord-empty { padding:14px 10px !important; border:1px dashed rgba(88,166,255,.28) !important; border-radius:10px !important; background:linear-gradient(135deg,rgba(88,166,255,.06),rgba(124,77,255,.05)) !important; color:rgba(255,255,255,.58) !important; font-size:9px !important; line-height:1.35 !important; text-align:center !important; }
02458:         #${SCRIPT.panelId} .mcms-discord-card { padding:10px !important; border-radius:12px !important; border:1px solid rgba(255,255,255,.14) !important; background:linear-gradient(145deg,rgba(22,28,38,.96),rgba(11,15,22,.98)) !important; box-shadow:inset 0 1px rgba(255,255,255,.04),0 8px 18px rgba(0,0,0,.22) !important; }
02459:         #${SCRIPT.panelId} .mcms-discord-card[data-tone="positive"] { border-color:rgba(46,204,113,.48) !important; box-shadow:inset 3px 0 #2ecc71,0 8px 18px rgba(0,0,0,.22) !important; }
02460:         #${SCRIPT.panelId} .mcms-discord-card[data-tone="negative"] { border-color:rgba(231,76,60,.52) !important; box-shadow:inset 3px 0 #e74c3c,0 8px 18px rgba(0,0,0,.22) !important; }
02461:         #${SCRIPT.panelId} .mcms-discord-card[data-tone="neutral"] { border-color:rgba(241,196,15,.42) !important; box-shadow:inset 3px 0 #f1c40f,0 8px 18px rgba(0,0,0,.22) !important; }
02462:         #${SCRIPT.panelId} .mcms-discord-head { display:flex !important; justify-content:space-between !important; align-items:flex-start !important; gap:8px !important; margin-bottom:8px !important; }
02463:         #${SCRIPT.panelId} .mcms-discord-title { color:#fff !important; font-size:10px !important; font-weight:950 !important; letter-spacing:.35px !important; }
02464:         #${SCRIPT.panelId} .mcms-discord-date { margin-top:2px !important; color:rgba(255,255,255,.54) !important; font-size:8px !important; font-weight:800 !important; }
02465:         #${SCRIPT.panelId} .mcms-discord-result { padding:3px 6px !important; border-radius:999px !important; background:rgba(255,255,255,.08) !important; color:#fff !important; font-size:8px !important; font-weight:950 !important; white-space:nowrap !important; }
02466:         #${SCRIPT.panelId} .mcms-discord-stats { display:grid !important; grid-template-columns:repeat(3,minmax(0,1fr)) !important; gap:5px !important; }
02467:         #${SCRIPT.panelId} .mcms-discord-stat { min-width:0 !important; padding:7px 5px !important; border-radius:8px !important; background:rgba(255,255,255,.055) !important; text-align:center !important; }
02468:         #${SCRIPT.panelId} .mcms-discord-stat span { display:block !important; color:rgba(255,255,255,.52) !important; font-size:7px !important; font-weight:900 !important; text-transform:uppercase !important; letter-spacing:.5px !important; }
02469:         #${SCRIPT.panelId} .mcms-discord-stat strong { display:block !important; margin-top:3px !important; color:#fff !important; font-size:10px !important; font-weight:950 !important; white-space:nowrap !important; overflow:hidden !important; text-overflow:ellipsis !important; }
02470:         #${SCRIPT.panelId} .mcms-discord-breakdowns { display:grid !important; grid-template-columns:repeat(2,minmax(0,1fr)) !important; gap:6px !important; margin-top:7px !important; }
02471:         #${SCRIPT.panelId} .mcms-discord-breakdown { min-width:0 !important; padding:7px !important; border-radius:8px !important; background:rgba(255,255,255,.04) !important; }
02472:         #${SCRIPT.panelId} .mcms-discord-breakdown b { display:block !important; margin-bottom:4px !important; color:#bbdefb !important; font-size:7.5px !important; text-transform:uppercase !important; letter-spacing:.55px !important; }
02473:         #${SCRIPT.panelId} .mcms-discord-line { display:flex !important; justify-content:space-between !important; gap:5px !important; margin-top:3px !important; color:rgba(255,255,255,.68) !important; font-size:7.5px !important; }
02474:         #${SCRIPT.panelId} .mcms-discord-line span { min-width:0 !important; overflow:hidden !important; text-overflow:ellipsis !important; white-space:nowrap !important; }
02475:         #${SCRIPT.panelId} .mcms-discord-line strong { color:#fff !important; white-space:nowrap !important; }
02476:         #${SCRIPT.panelId} .mcms-discord-foot { margin-top:7px !important; padding-top:6px !important; border-top:1px solid rgba(255,255,255,.08) !important; color:rgba(255,255,255,.48) !important; font-size:7.5px !important; line-height:1.3 !important; }
02477:         #${SCRIPT.panelId} .mcms-discord-status[data-tone="good"] { border-color:rgba(46,204,113,.38) !important; color:#9be8b8 !important; }
02478:         #${SCRIPT.panelId} .mcms-discord-status[data-tone="bad"] { border-color:rgba(231,76,60,.42) !important; color:#ffaaa1 !important; }
02479:         #${SCRIPT.panelId} .mcms-discord-status[data-tone="busy"] { border-color:rgba(52,152,219,.42) !important; color:#9bd5ff !important; }
02480:         #${SCRIPT.panelId} .mcms-discord-mini-stats { display:grid !important; grid-template-columns:repeat(4,minmax(0,1fr)) !important; gap:4px !important; margin-top:6px !important; }
02481:         #${SCRIPT.panelId} .mcms-discord-mini-stats span { min-width:0 !important; padding:5px 4px !important; border-radius:7px !important; background:rgba(88,166,255,.07) !important; color:rgba(255,255,255,.52) !important; font-size:6.8px !important; font-weight:850 !important; text-align:center !important; text-transform:uppercase !important; letter-spacing:.3px !important; }
02482:         #${SCRIPT.panelId} .mcms-discord-mini-stats b { display:block !important; margin-top:2px !important; color:#fff !important; font-size:7.8px !important; overflow:hidden !important; text-overflow:ellipsis !important; white-space:nowrap !important; }
02483:         #${SCRIPT.panelId} .mcms-discord-chart { display:block !important; width:100% !important; margin-top:8px !important; border-radius:9px !important; border:1px solid rgba(255,255,255,.11) !important; background:#0b1018 !important; }
02484:         #${SCRIPT.panelId} .mcms-discord-date-grid { display:grid !important; grid-template-columns:repeat(2,minmax(0,1fr)) !important; gap:5px !important; }
02485:         #${SCRIPT.panelId} .mcms-discord-date-grid .mcms-row { grid-template-columns:56px minmax(0,1fr) !important; }
02486:         #${SCRIPT.panelId} .mcms-finance-vault-summary { display:grid !important; grid-template-columns:repeat(4,minmax(0,1fr)) !important; gap:5px !important; margin:7px 0 !important; }
02487:         #${SCRIPT.panelId} .mcms-finance-vault-summary span { min-width:0 !important; padding:7px 5px !important; border:1px solid rgba(88,166,255,.18) !important; border-radius:8px !important; background:rgba(88,166,255,.055) !important; color:rgba(255,255,255,.54) !important; font-size:6.8px !important; font-weight:850 !important; text-align:center !important; text-transform:uppercase !important; letter-spacing:.3px !important; }
02488:         #${SCRIPT.panelId} .mcms-finance-vault-summary b { display:block !important; margin-bottom:2px !important; color:#fff !important; font-size:8px !important; overflow:hidden !important; text-overflow:ellipsis !important; white-space:nowrap !important; }
02489:         #${SCRIPT.panelId} .mcms-finance-vault-summary small { grid-column:1/-1 !important; padding:5px 7px !important; border-radius:7px !important; background:rgba(255,255,255,.035) !important; color:rgba(255,255,255,.48) !important; font-size:7.2px !important; line-height:1.35 !important; text-align:center !important; }
02490:         #${SCRIPT.panelId} .mcms-finance-private-note { border-color:rgba(241,196,15,.34) !important; color:#f5d984 !important; }
02491:         #${SCRIPT.panelId} .mcms-sweep-card { margin-top:8px !important; padding:8px !important; border-radius:9px !important; border:1px solid rgba(255,183,72,.28) !important; background:rgba(88,46,4,.13) !important; }
02492:         #${SCRIPT.panelId} .mcms-sweep-head { display:flex !important; justify-content:space-between !important; align-items:center !important; gap:8px !important; color:#ffe0a3 !important; font-size:9px !important; font-weight:950 !important; }
02493:         #${SCRIPT.panelId} .mcms-sweep-state { padding:2px 6px !important; border-radius:999px !important; background:rgba(255,255,255,.10) !important; color:rgba(255,255,255,.78) !important; font-size:7px !important; letter-spacing:.35px !important; }
02494:         #${SCRIPT.panelId} .mcms-sweep-state.mcms-running { background:rgba(255,145,24,.28) !important; color:#fff1cf !important; }
02495:         #${SCRIPT.panelId} .mcms-sweep-stats { display:grid !important; grid-template-columns:repeat(4,minmax(0,1fr)) !important; gap:4px !important; margin-top:7px !important; }
02496:         #${SCRIPT.panelId} .mcms-sweep-stat { min-width:0 !important; padding:5px 3px !important; border-radius:7px !important; background:rgba(255,255,255,.055) !important; text-align:center !important; }
02497:         #${SCRIPT.panelId} .mcms-sweep-stat b { display:block !important; color:#fff !important; font-size:11px !important; line-height:1 !important; }
02498:         #${SCRIPT.panelId} .mcms-sweep-stat span { display:block !important; margin-top:3px !important; color:rgba(255,255,255,.50) !important; font-size:6.5px !important; font-weight:900 !important; text-transform:uppercase !important; }
02499:         #${SCRIPT.panelId} .mcms-sweep-queue { display:grid !important; gap:4px !important; max-height:128px !important; overflow-y:auto !important; margin-top:7px !important; padding-right:2px !important; overscroll-behavior:contain !important; scrollbar-width:thin !important; }
02500:         #${SCRIPT.panelId} .mcms-sweep-entry { display:grid !important; grid-template-columns:minmax(0,1fr) auto !important; gap:6px !important; padding:6px !important; border-radius:7px !important; border:1px solid rgba(255,255,255,.08) !important; background:rgba(255,255,255,.04) !important; }
02501:         #${SCRIPT.panelId} .mcms-sweep-entry.mcms-current { border-color:rgba(255,177,57,.62) !important; background:rgba(255,145,24,.11) !important; }
02502:         #${SCRIPT.panelId} .mcms-sweep-title { min-width:0 !important; color:#f7f8fb !important; font-size:8.5px !important; font-weight:900 !important; white-space:nowrap !important; overflow:hidden !important; text-overflow:ellipsis !important; }
02503:         #${SCRIPT.panelId} .mcms-sweep-meta { display:block !important; margin-top:2px !important; color:rgba(255,255,255,.52) !important; font-size:7px !important; font-weight:800 !important; }
02504:         #${SCRIPT.panelId} .mcms-sweep-count { color:#ffc86b !important; font-size:9px !important; font-weight:950 !important; white-space:nowrap !important; }
02505:         #${SCRIPT.panelId} .mcms-sweep-log { max-height:72px !important; overflow-y:auto !important; margin-top:7px !important; padding:6px !important; border-radius:7px !important; background:rgba(0,0,0,.18) !important; color:rgba(255,255,255,.64) !important; font:700 7px/1.35 Arial,Helvetica,sans-serif !important; white-space:normal !important; }
02506:         #${SCRIPT.panelId} .mcms-heat-legend { display: grid !important; grid-template-columns: repeat(5,minmax(0,1fr)) !important; gap: 3px !important; margin-top: 7px !important; }
02507:         #${SCRIPT.panelId} .mcms-heat-key { padding: 4px 2px !important; border-radius: 6px !important; color: #fff !important; font-size: 7px !important; font-weight: 900 !important; text-align: center !important; text-shadow: 0 1px 2px #000 !important; }
02508:         #${SCRIPT.panelId} .mcms-footer { margin: 9px 0 0 0 !important; padding: 7px 0 0 0 !important; border-top: 1px solid rgba(255,255,255,.10) !important; color: rgba(233,238,245,.58) !important; font-size: 9px !important; line-height: 1.25 !important; overflow: hidden !important; }
02509:         #${SCRIPT.panelId} .mcms-build { display: block !important; margin-top: 4px !important; white-space: nowrap !important; overflow: hidden !important; text-overflow: ellipsis !important; }
02510: 
02511:         .mcms-mission-float-pane,
02512:         .mcms-mission-float-pane * {
02513:             pointer-events: none !important;
02514:             touch-action: none !important;
02515:         }
02516:         .mcms-alliance-credit-icon,
02517:         .mcms-mission-age-icon,
```

### Lines 2525-2541

```text
02525:         .mcms-alliance-credit-badge,
02526:         .mcms-mission-age-badge,
02527:         .mcms-unit-commitment-badge,
02528:         .mcms-transport-watcher-badge,
02529:         .mcms-resource-gap-badge {
02530:             position: absolute !important; left: 0 !important; top: 0 !important;
02531:             transform: translate(-50%, -50%) !important;
02532:             display: inline-flex !important; align-items: center !important; justify-content: center !important;
02533:             white-space: nowrap !important; pointer-events: none !important; touch-action: none !important;
02534:             backdrop-filter: blur(3px) !important;
02535:             -webkit-backdrop-filter: blur(3px) !important;
02536:             text-shadow: 0 1px 2px rgba(0,0,0,.80) !important;
02537:         }
02538:         .mcms-alliance-credit-badge {
02539:             min-width: 48px !important; height: 22px !important; padding: 0 7px !important; border-radius: 8px !important;
02540:             border: 1px solid rgba(255,213,79,.46) !important; background: rgba(10,14,20,.46) !important;
02541:             color: #ffe082 !important; box-shadow: 0 2px 7px rgba(0,0,0,.18) !important;
```

### Lines 2610-2645

```text
02610:             box-shadow: 0 0 0 2px rgba(0,0,0,.38), 0 2px 8px rgba(255,112,20,.27) !important;
02611:             font: 950 8.5px/1 Arial,Helvetica,sans-serif !important; letter-spacing:.1px !important;
02612:         }
02613:         .mcms-resource-gap-badge.mcms-gap-uncovered { border-color:#ff574d !important; color:#fff !important; background:rgba(91,11,7,.94) !important; box-shadow:0 0 0 2px rgba(0,0,0,.42),0 0 11px rgba(255,45,35,.46) !important; }
02614: 
02615:         #${SCRIPT.missionInspectorId} .mcms-inspector-gap { margin-top:6px !important; padding:7px !important; border-radius:7px !important; border:1px solid rgba(255,152,52,.38) !important; background:rgba(77,31,4,.18) !important; }
02616:         #${SCRIPT.missionInspectorId} .mcms-inspector-gap-title { display:flex !important; align-items:center !important; justify-content:space-between !important; gap:8px !important; color:#ffd29a !important; font-size:8px !important; font-weight:950 !important; letter-spacing:.4px !important; }
02617:         #${SCRIPT.missionInspectorId} .mcms-inspector-gap-row { display:grid !important; grid-template-columns:minmax(0,1fr) auto !important; gap:7px !important; margin-top:4px !important; color:#e8edf4 !important; font-size:8px !important; line-height:1.3 !important; }
02618:         #${SCRIPT.missionInspectorId} .mcms-inspector-gap-row span:last-child { color:#9fb0c2 !important; text-align:right !important; white-space:nowrap !important; }
02619: 
02620:         #${SCRIPT.panelId} .mcms-ops-session-grid {
02621:             display: grid !important; grid-template-columns: repeat(2,minmax(0,1fr)) !important; gap: 6px !important;
02622:         }
02623:         #${SCRIPT.panelId} .mcms-ops-stat {
02624:             min-width: 0 !important; padding: 8px !important; border-radius: 9px !important;
02625:             border: 1px solid rgba(255,255,255,.11) !important; background: rgba(255,255,255,.055) !important;
02626:         }
02627:         #${SCRIPT.panelId} .mcms-ops-stat-label { display:block !important; color:rgba(255,255,255,.56) !important; font-size:7.5px !important; font-weight:900 !important; text-transform:uppercase !important; letter-spacing:.45px !important; }
02628:         #${SCRIPT.panelId} .mcms-ops-stat-value { display:block !important; margin-top:4px !important; color:#fff !important; font-size:13px !important; line-height:1 !important; font-weight:950 !important; overflow:hidden !important; text-overflow:ellipsis !important; white-space:nowrap !important; }
02629:         #${SCRIPT.panelId} .mcms-ops-list { display:grid !important; gap:5px !important; }
02630:         #${SCRIPT.panelId} .mcms-ops-entry {
02631:             display:grid !important; grid-template-columns:minmax(0,1fr) auto !important; gap:7px !important; align-items:center !important;
02632:             padding:7px !important; border-radius:8px !important; border:1px solid rgba(255,255,255,.10) !important; background:rgba(255,255,255,.045) !important;
02633:         }
02634:         #${SCRIPT.panelId} .mcms-ops-entry-main { min-width:0 !important; }
02635:         #${SCRIPT.panelId} .mcms-ops-entry-title { display:block !important; color:#f5f7ff !important; font-size:9.5px !important; font-weight:900 !important; white-space:nowrap !important; overflow:hidden !important; text-overflow:ellipsis !important; }
02636:         #${SCRIPT.panelId} .mcms-ops-entry-meta { display:block !important; margin-top:3px !important; color:rgba(255,255,255,.58) !important; font-size:7.5px !important; font-weight:800 !important; white-space:nowrap !important; overflow:hidden !important; text-overflow:ellipsis !important; }
02637:         #${SCRIPT.panelId} .mcms-ops-entry-value { color:#ffe082 !important; font-size:10px !important; font-weight:950 !important; white-space:nowrap !important; }
02638:         #${SCRIPT.panelId} .mcms-history-latest { display:grid !important; gap:5px !important; }
02639:         #${SCRIPT.panelId} .mcms-history-older {
02640:             margin-top:2px !important; border:1px solid rgba(255,255,255,.11) !important; border-radius:8px !important;
02641:             background:rgba(255,255,255,.035) !important; overflow:hidden !important;
02642:         }
02643:         #${SCRIPT.panelId} .mcms-history-older > summary {
02644:             display:block !important; padding:7px 9px !important; cursor:pointer !important; list-style:none !important;
02645:             color:rgba(255,255,255,.68) !important; font-size:8px !important; font-weight:900 !important; letter-spacing:.35px !important; text-transform:uppercase !important;
```

### Lines 2669-2689

```text
02669:         #${SCRIPT.criticalDrawerId} .mcms-drawer-subtitle { display:block !important; margin-top:2px !important; color:rgba(255,255,255,.58) !important; font-size:8px !important; font-weight:800 !important; }
02670:         #${SCRIPT.criticalDrawerId} .mcms-drawer-close { width:28px !important; height:28px !important; border:0 !important; border-radius:8px !important; background:rgba(255,255,255,.10) !important; color:#fff !important; cursor:pointer !important; font-weight:900 !important; }
02671:         #${SCRIPT.criticalDrawerId} .mcms-drawer-list { display:grid !important; gap:6px !important; margin-top:8px !important; }
02672:         #${SCRIPT.criticalDrawerId} .mcms-critical-row { width:100% !important; display:grid !important; grid-template-columns:86px minmax(0,1fr) auto !important; gap:7px !important; align-items:center !important; padding:8px !important; border-radius:9px !important; border:1px solid rgba(255,255,255,.11) !important; background:rgba(255,255,255,.05) !important; color:#fff !important; cursor:pointer !important; text-align:left !important; }
02673:         #${SCRIPT.criticalDrawerId} .mcms-critical-row:hover { background:rgba(255,255,255,.11) !important; }
02674:         #${SCRIPT.criticalDrawerId} .mcms-critical-row.mcms-age-aged { border-color:rgba(255,183,77,.34) !important; }
02675:         #${SCRIPT.criticalDrawerId} .mcms-critical-row.mcms-age-high { border-color:rgba(255,112,67,.48) !important; background:rgba(68,24,8,.18) !important; }
02676:         #${SCRIPT.criticalDrawerId} .mcms-critical-row.mcms-age-critical { border-color:rgba(255,82,82,.62) !important; background:rgba(88,12,12,.32) !important; }
02677:         #${SCRIPT.criticalDrawerId} .mcms-critical-age-band { color:#ffb74d !important; font-size:8px !important; font-weight:950 !important; letter-spacing:.45px !important; white-space:nowrap !important; text-transform:uppercase !important; }
02678:         #${SCRIPT.criticalDrawerId} .mcms-critical-row.mcms-age-critical .mcms-critical-age-band { color:#ff6b6b !important; }
02679:         #${SCRIPT.criticalDrawerId} .mcms-critical-name { display:block !important; min-width:0 !important; color:#fff !important; font-size:9.5px !important; font-weight:900 !important; white-space:nowrap !important; overflow:hidden !important; text-overflow:ellipsis !important; }
02680:         #${SCRIPT.criticalDrawerId} .mcms-critical-meta { display:block !important; margin-top:3px !important; color:rgba(255,255,255,.58) !important; font-size:7.5px !important; font-weight:800 !important; }
02681:         #${SCRIPT.criticalDrawerId} .mcms-critical-age { color:#bbdefb !important; font-size:8.5px !important; font-weight:950 !important; white-space:nowrap !important; }
02682: 
02683:         #${SCRIPT.payoutFlashId} {
02684:             position: absolute !important; inset: 0 !important; width: 100% !important; height: 100% !important;
02685:             z-index: 625 !important; overflow: hidden !important;
02686:             pointer-events: none !important; opacity: 0 !important;
02687:             isolation: isolate !important;
02688:         }
02689:         #${SCRIPT.payoutFlashId}.mcms-payout-active { opacity: 1 !important; }
```

### Lines 2734-2750

```text
02734:         }
02735:         #${SCRIPT.payoutFlashId}.mcms-payout-active .mcms-payout-banner {
02736:             animation: mcmsPayoutBanner var(--mcms-payout-duration, 3000ms) cubic-bezier(.16,.78,.24,1) both !important;
02737:         }
02738:         #${SCRIPT.payoutFlashId} .mcms-payout-title {
02739:             display: block !important; color: var(--mcms-payout-accent, #f4c84f) !important;
02740:             font-family: Impact, Haettenschweiler, "Arial Narrow Bold", "Arial Black", sans-serif !important;
02741:             font-size: clamp(34px, 5.4vw, 64px) !important; line-height: .92 !important; font-weight: 900 !important;
02742:             letter-spacing: 1.9px !important; text-transform: uppercase !important; white-space: nowrap !important;
02743:             text-shadow: 0 3px 0 rgba(0,0,0,.78), 0 5px 18px rgba(0,0,0,.74), 0 0 18px var(--mcms-payout-glow, rgba(244,200,79,.16)) !important;
02744:             transform: scaleX(.94) !important;
02745:         }
02746:         #${SCRIPT.payoutFlashId} .mcms-payout-divider {
02747:             display: block !important; width: min(390px, 78%) !important; height: 1px !important;
02748:             margin: 11px auto 9px !important;
02749:             background: linear-gradient(90deg, transparent, var(--mcms-payout-accent, #f4c84f) 24%, rgba(255,255,255,.90) 50%, var(--mcms-payout-accent, #f4c84f) 76%, transparent) !important;
02750:             box-shadow: 0 0 8px rgba(244,200,79,.24) !important;
```

### Lines 2767-2783

```text
02767:             display:inline-block !important; margin-bottom:7px !important; padding:3px 8px !important; border-radius:999px !important;
02768:             border:1px solid var(--mcms-payout-accent-soft, rgba(247,205,83,.42)) !important; background:rgba(0,0,0,.28) !important;
02769:             color:var(--mcms-payout-accent, #f4c84f) !important; font-size:7.5px !important; line-height:1 !important; font-weight:950 !important;
02770:             letter-spacing:1.6px !important; text-transform:uppercase !important;
02771:         }
02772:         #${SCRIPT.payoutFlashId} .mcms-payout-mission {
02773:             display:block !important; margin-top:8px !important; color:#fff !important;
02774:             font-size:clamp(12px,2vw,18px) !important; line-height:1.05 !important; font-weight:950 !important;
02775:             white-space:nowrap !important; overflow:hidden !important; text-overflow:ellipsis !important;
02776:             text-shadow:0 2px 8px rgba(0,0,0,.85) !important;
02777:         }
02778:         #${SCRIPT.payoutFlashId} .mcms-payout-mission:empty { display:none !important; }
02779:         #${SCRIPT.payoutFlashId} .mcms-payout-source {
02780:             display:block !important; margin-top:5px !important; color:var(--mcms-payout-accent, #f4c84f) !important;
02781:             font-size:8px !important; line-height:1 !important; font-weight:950 !important; letter-spacing:2px !important; text-transform:uppercase !important;
02782:         }
02783:         #${SCRIPT.payoutFlashId} .mcms-payout-kicker {
```

### Lines 2785-2801

```text
02785:             font-family: "Arial Narrow", Arial, Helvetica, sans-serif !important;
02786:             font-size: 10px !important; line-height: 1 !important; font-weight: 900 !important;
02787:             letter-spacing: 3px !important; text-transform: uppercase !important;
02788:         }
02789:         #${SCRIPT.payoutFlashId} .mcms-payout-amount {
02790:             display: block !important; margin-top: 7px !important; color: #fff !important;
02791:             font-family: "Arial Black", "Arial Narrow Bold", Arial, Helvetica, sans-serif !important;
02792:             font-size: clamp(20px, 3vw, 32px) !important; line-height: 1 !important; font-weight: 950 !important;
02793:             letter-spacing: 1.5px !important; white-space: nowrap !important;
02794:             text-shadow: 0 2px 0 rgba(0,0,0,.74), 0 5px 15px rgba(0,0,0,.68) !important;
02795:         }
02796: 
02797:         #${SCRIPT.payoutFlashId} .mcms-payout-vc-sunset,
02798:         #${SCRIPT.payoutFlashId} .mcms-payout-vc-grid {
02799:             position: absolute !important; inset: 0 !important; opacity: 0;
02800:             pointer-events: none !important; will-change: opacity, transform !important;
02801:         }
```

### Lines 2987-3020

```text
02987:             color: #f1f0e8 !important;
02988:             font-family: Impact, Haettenschweiler, "Arial Narrow Bold", "Arial Black", sans-serif !important;
02989:             font-size: clamp(31px, 5.05vw, 58px) !important;
02990:             font-weight: 900 !important;
02991:             letter-spacing: clamp(.8px, .24vw, 2.6px) !important;
02992:             word-spacing: -1px !important;
02993:             line-height: .88 !important;
02994:             text-transform: uppercase !important;
02995:             white-space: nowrap !important;
02996:             transform: skewX(-5deg) scaleX(.89) !important;
02997:             transform-origin: 50% 50% !important;
02998:             text-shadow:
02999:                 2px 2px 0 rgba(2,3,2,.98),
03000:                 5px 5px 0 rgba(2,3,2,.96),
03001:                 8px 8px 0 rgba(255,116,13,.34),
03002:                 -1px -1px 0 rgba(255,255,255,.18),
03003:                 0 0 24px rgba(255,126,17,.15) !important;
03004:         }
03005:         #${SCRIPT.payoutFlashId}[data-template="badCompany"] .mcms-payout-title.mcms-payout-title-long {
03006:             font-size: clamp(27px, 4.25vw, 49px) !important;
03007:             letter-spacing: clamp(.3px, .16vw, 1.5px) !important;
03008:             transform: skewX(-5deg) scaleX(.84) !important;
03009:         }
03010:         #${SCRIPT.payoutFlashId}[data-template="badCompany"] .mcms-payout-title.mcms-payout-title-very-long {
03011:             font-size: clamp(23px, 3.65vw, 42px) !important;
03012:             white-space: normal !important;
03013:             text-wrap: balance !important;
03014:             line-height: .94 !important;
03015:             transform: skewX(-4deg) scaleX(.88) !important;
03016:         }
03017:         #${SCRIPT.payoutFlashId}[data-template="badCompany"] .mcms-payout-divider {
03018:             height: 3px !important; width: min(500px, 76%) !important; margin: 14px auto 10px !important;
03019:             background:
03020:                 linear-gradient(90deg, transparent, #ff8e19 14%, #f4f1e4 45%, #747f68 75%, transparent) !important;
```

### Lines 3057-3073

```text
03057:             }
03058:             #${SCRIPT.payoutFlashId}[data-template="badCompany"] .mcms-payout-title {
03059:                 font-size: clamp(25px, 8vw, 39px) !important;
03060:                 letter-spacing: .5px !important;
03061:                 transform: skewX(-4deg) scaleX(.84) !important;
03062:             }
03063:             #${SCRIPT.payoutFlashId}[data-template="badCompany"] .mcms-payout-title.mcms-payout-title-long {
03064:                 font-size: clamp(21px, 6.8vw, 33px) !important;
03065:                 white-space: normal !important;
03066:                 text-wrap: balance !important;
03067:             }
03068:         }
03069:         #${SCRIPT.payoutFlashId} .mcms-payout-theme-fx,
03070:         #${SCRIPT.payoutFlashId} .mcms-payout-theme-particles {
03071:             position:absolute !important; inset:0 !important; opacity:0;
03072:             pointer-events:none !important; overflow:hidden !important;
03073:             will-change:opacity, transform, background-position, filter !important;
```

### Lines 3618-3634

```text
03618:             #${SCRIPT.payoutFlashId}[data-template="gta5"] .mcms-payout-banner,
03619:             #${SCRIPT.payoutFlashId}[data-template="cyberpunk"] .mcms-payout-banner,
03620:             #${SCRIPT.payoutFlashId}[data-template="factorio"] .mcms-payout-banner,
03621:             #${SCRIPT.payoutFlashId}[data-template="galactic"] .mcms-payout-banner {padding-left:18px !important;padding-right:18px !important;}
03622:         }
03623: 
03624:         /* Shared title fitting for every template. */
03625:         #${SCRIPT.payoutFlashId} .mcms-payout-title.mcms-payout-title-long { font-size:clamp(28px,4.35vw,51px) !important; letter-spacing:.6px !important; transform:scaleX(.90) !important; }
03626:         #${SCRIPT.payoutFlashId} .mcms-payout-title.mcms-payout-title-very-long { font-size:clamp(23px,3.55vw,42px) !important; line-height:.95 !important; white-space:normal !important; text-wrap:balance !important; transform:scaleX(.92) !important; }
03627:         #${SCRIPT.payoutFlashId}[data-template="viceCity"] .mcms-payout-title.mcms-payout-title-long { font-size:clamp(34px,5.5vw,62px) !important; transform:rotate(-2deg) skewX(-5deg) scaleX(.92) !important; }
03628:         #${SCRIPT.payoutFlashId}[data-template="viceCity"] .mcms-payout-title.mcms-payout-title-very-long { font-size:clamp(29px,4.6vw,52px) !important; line-height:.93 !important; transform:rotate(-1deg) skewX(-4deg) scaleX(.94) !important; }
03629:         #${SCRIPT.payoutFlashId}[data-template="darkFantasy"] .mcms-payout-title.mcms-payout-title-long,
03630:         #${SCRIPT.payoutFlashId}[data-template="underworld"] .mcms-payout-title.mcms-payout-title-long { transform:none !important; }
03631:         #${SCRIPT.payoutFlashId}[data-template="darkFantasy"] .mcms-payout-title.mcms-payout-title-very-long,
03632:         #${SCRIPT.payoutFlashId}[data-template="underworld"] .mcms-payout-title.mcms-payout-title-very-long { transform:none !important; }
03633:         @media (max-width:620px) {
03634:             #${SCRIPT.payoutFlashId}[data-template="cyberpunk"] .mcms-payout-banner,
```

### Lines 3773-3790

```text
03773:             background: rgba(23,198,126,.95) !important; border-color: rgba(194,255,226,.72) !important;
03774:             box-shadow: 0 0 9px rgba(67,239,166,.55) !important;
03775:         }
03776:         html[data-mcms-tablet-active="true"] #${SCRIPT.controlId} .mcms-float-label-desktop { display: none !important; }
03777:         html[data-mcms-tablet-active="true"] #${SCRIPT.controlId} .mcms-float-label-tablet {
03778:             position: relative !important; z-index: 2 !important;
03779:             display: flex !important; align-items: center !important; justify-content: flex-start !important;
03780:             min-width: 0 !important; min-height: 2.05em !important; max-height: 2.05em !important;
03781:             overflow: hidden !important; text-overflow: clip !important; white-space: normal !important;
03782:             overflow-wrap: normal !important; word-break: normal !important; hyphens: none !important;
03783:             font-size: clamp(9px,1.1vw,10.25px) !important; line-height: 1.03 !important; letter-spacing: -.08px !important;
03784:             font-weight: 900 !important; text-align: left !important; padding-right: 4px !important; text-shadow: 0 1px 2px rgba(0,0,0,.72) !important;
03785:         }
03786:         html[data-mcms-tablet-active="true"] #${SCRIPT.controlId} .mcms-screen-pins {
03787:             grid-area: pins !important;
03788:             display: grid !important;
03789:             grid-template-columns: repeat(var(--mcms-tablet-pin-columns, 4), minmax(0,1fr)) !important;
03790:             gap: 7px !important;
```

### Lines 3821-3858

```text
03821:         html[data-mcms-tablet-active="true"] #${SCRIPT.panelId} .mcms-title { font-size: 14px !important; letter-spacing: .45px !important; }
03822:         html[data-mcms-tablet-active="true"] #${SCRIPT.panelId} .mcms-subtitle { margin-top: 4px !important; font-size: 10.5px !important; }
03823:         html[data-mcms-tablet-active="true"] #${SCRIPT.panelId} .mcms-reset-panel { display: none !important; }
03824:         html[data-mcms-tablet-active="true"] #${SCRIPT.panelId} .mcms-close,
03825:         html[data-mcms-tablet-active="true"] #${SCRIPT.panelId} .mcms-help-button {
03826:             width: 44px !important; height: 44px !important; border-radius: 11px !important; font-size: 20px !important; line-height: 44px !important;
03827:         }
03828:         html[data-mcms-tablet-active="true"] #${SCRIPT.panelId} .mcms-close { font-size:24px !important; }
03829:         html[data-mcms-tablet-active="true"] #${SCRIPT.panelId} .mcms-tabs {
03830:             position: sticky !important; top: 42px !important; z-index: 7 !important;
03831:             grid-template-columns: repeat(4, minmax(0,1fr)) !important; gap: 8px !important;
03832:             margin: 0 -4px 12px !important; padding: 8px 4px !important; background: rgba(8,12,18,.985) !important;
03833:         }
03834:         html[data-mcms-tablet-active="true"] #${SCRIPT.panelId} .mcms-tab-btn {
03835:             height: 44px !important; border-radius: 11px !important; font-size: 11.5px !important; padding: 0 6px !important;
03836:         }
03837:         html[data-mcms-tablet-active="true"] #${SCRIPT.panelId} .mcms-grid-2 { gap: 9px !important; }
03838:         html[data-mcms-tablet-active="true"] #${SCRIPT.panelId} .mcms-grid-2 [data-toggle="criticalView"] { grid-column: auto !important; }
03839:         html[data-mcms-tablet-active="true"] #${SCRIPT.panelId} .mcms-theme-btn,
03840:         html[data-mcms-tablet-active="true"] #${SCRIPT.panelId} .mcms-toggle-btn,
03841:         html[data-mcms-tablet-active="true"] #${SCRIPT.panelId} .mcms-place-main {
03842:             min-height: 58px !important; height: auto !important; padding: 9px !important;
03843:             grid-template-columns: 30px minmax(0,1fr) !important; gap: 9px !important; border-radius: 12px !important;
03844:         }
03845:         html[data-mcms-tablet-active="true"] #${SCRIPT.panelId} .mcms-iconbox {
03846:             width: 30px !important; height: 30px !important; min-width: 30px !important; border-radius: 9px !important; font-size: 13px !important;
03847:         }
03848:         html[data-mcms-tablet-active="true"] #${SCRIPT.panelId} .mcms-label { font-size: 12.5px !important; line-height: 1.15 !important; }
03849:         html[data-mcms-tablet-active="true"] #${SCRIPT.panelId} .mcms-pill { margin-top: 5px !important; max-width: 120px !important; padding: 3px 7px !important; font-size: 9px !important; }
03850:         html[data-mcms-tablet-active="true"] #${SCRIPT.panelId} .mcms-section-label { margin: 14px 0 8px !important; font-size: 10.5px !important; letter-spacing: .8px !important; }
03851:         html[data-mcms-tablet-active="true"] #${SCRIPT.panelId} .mcms-row {
03852:             grid-template-columns: minmax(0,1fr) minmax(170px, 42%) !important; gap: 10px !important; margin-bottom: 10px !important;
03853:         }
03854:         html[data-mcms-tablet-active="true"] #${SCRIPT.panelId} .mcms-discord-wide { grid-template-columns: 120px minmax(0,1fr) !important; }
03855:         html[data-mcms-tablet-active="true"] #${SCRIPT.panelId} .mcms-row-label { font-size: 12px !important; }
03856:         html[data-mcms-tablet-active="true"] #${SCRIPT.panelId} .mcms-input,
03857:         html[data-mcms-tablet-active="true"] #${SCRIPT.panelId} .mcms-select {
03858:             height: 44px !important; border-radius: 10px !important; padding: 0 11px !important; font-size: 13px !important;
```

### Lines 3911-3927

```text
03911:             max-width: min(420px, calc(100vw - 24px)) !important; padding: 10px 13px !important; font-size: 12px !important;
03912:         }
03913: 
03914:         @media (max-width: 560px) {
03915:             html[data-mcms-tablet-active="true"] #${SCRIPT.panelId} .mcms-grid-2 { grid-template-columns: 1fr !important; }
03916:             html[data-mcms-tablet-active="true"] #${SCRIPT.panelId} .mcms-grid-2 [data-toggle="criticalView"] { grid-column: auto !important; }
03917:             html[data-mcms-tablet-active="true"] #${SCRIPT.panelId} .mcms-row,
03918:             html[data-mcms-tablet-active="true"] #${SCRIPT.panelId} .mcms-discord-wide { grid-template-columns: 1fr !important; }
03919:             html[data-mcms-tablet-active="true"] #${SCRIPT.panelId} .mcms-row-label { white-space: normal !important; }
03920:         }
03921: 
03922: 
03923:         /* v3.3.1 iOS Safari Mobile Mode: map-aware command grid, safe-area bottom sheet,
03924:            Visual Viewport keyboard support and compact high-contrast touch controls. */
03925:         html[data-mcms-mobile-active="true"] #${SCRIPT.controlId},
03926:         html[data-mcms-mobile-active="true"] #${SCRIPT.panelId},
03927:         html[data-mcms-mobile-active="true"] #${SCRIPT.criticalDrawerId},
```

### Lines 4001-4017

```text
04001:         }
04002:         html[data-mcms-mobile-active="true"] #${SCRIPT.controlId} .mcms-float-btn.mcms-on .mcms-float-key {
04003:             background:rgba(23,198,126,.96) !important; border-color:rgba(194,255,226,.75) !important; box-shadow:0 0 7px rgba(67,239,166,.58) !important;
04004:         }
04005:         html[data-mcms-mobile-active="true"] #${SCRIPT.controlId} .mcms-float-label-desktop,
04006:         html[data-mcms-mobile-active="true"] #${SCRIPT.controlId} .mcms-float-label-tablet { display:none !important; }
04007:         html[data-mcms-mobile-active="true"] #${SCRIPT.controlId} .mcms-float-label-mobile {
04008:             position:relative !important; z-index:2 !important; display:flex !important; align-items:center !important; justify-content:flex-start !important;
04009:             min-width:0 !important; overflow:hidden !important; white-space:nowrap !important; text-overflow:ellipsis !important;
04010:             font-size:clamp(7.5px,2.15vw,9px) !important; line-height:1 !important; font-weight:950 !important; letter-spacing:-.15px !important;
04011:             text-align:left !important; text-shadow:0 1px 2px rgba(0,0,0,.78) !important;
04012:         }
04013:         html[data-mcms-mobile-active="true"] #${SCRIPT.controlId} .mcms-screen-pins {
04014:             grid-area:auto !important; grid-column:1 / -1 !important; display:grid !important;
04015:             grid-template-columns:repeat(var(--mcms-mobile-pin-columns,4),minmax(0,1fr)) !important;
04016:             grid-auto-flow:row !important; justify-self:stretch !important; align-self:stretch !important;
04017:             justify-items:stretch !important; align-items:stretch !important;
```

### Lines 4022-4085

```text
04022:         html[data-mcms-mobile-active="true"] #${SCRIPT.controlId} .mcms-screen-pins:empty { display:none !important; }
04023:         html[data-mcms-mobile-active="true"] #${SCRIPT.controlId} .mcms-screen-pin-btn {
04024:             -webkit-appearance:none !important; appearance:none !important;
04025:             display:flex !important; align-items:center !important; justify-content:center !important;
04026:             justify-self:stretch !important; align-self:stretch !important; box-sizing:border-box !important;
04027:             width:100% !important; max-width:none !important; min-width:0 !important;
04028:             height:var(--mcms-mobile-pin-height,34px) !important; padding:0 7px !important;
04029:             border-radius:9px !important; font-size:clamp(8.5px,2.25vw,10px) !important; line-height:1.05 !important;
04030:             letter-spacing:-.08px !important; text-align:center !important; overflow:hidden !important; text-overflow:ellipsis !important;
04031:             white-space:nowrap !important; backdrop-filter:none !important; -webkit-backdrop-filter:none !important; pointer-events:auto !important;
04032:         }
04033:         html[data-mcms-mobile-active="true"] #${SCRIPT.panelId} {
04034:             width:calc(100% - 8px) !important; max-width:calc(100% - 8px) !important;
04035:             border-radius:16px 16px 11px 11px !important; border-color:rgba(112,204,255,.46) !important;
04036:             padding:8px 8px calc(8px + env(safe-area-inset-bottom)) !important;
04037:             overflow-x:hidden !important; overflow-y:auto !important; overscroll-behavior:contain !important;
04038:             -webkit-overflow-scrolling:touch !important; touch-action:pan-y !important;
04039:             background:linear-gradient(180deg,rgba(9,14,21,.99),rgba(4,7,11,.99)) !important;
04040:             box-shadow:0 -12px 38px rgba(0,0,0,.58),inset 0 1px rgba(255,255,255,.06) !important;
04041:             backdrop-filter:none !important; -webkit-backdrop-filter:none !important;
04042:         }
04043:         html[data-mcms-mobile-active="true"] #${SCRIPT.panelId}::-webkit-scrollbar,
04044:         html[data-mcms-mobile-active="true"] #${SCRIPT.panelId} .mcms-tabs::-webkit-scrollbar { display:none !important; width:0 !important; height:0 !important; }
04045:         html[data-mcms-mobile-active="true"] #${SCRIPT.panelId},
04046:         html[data-mcms-mobile-active="true"] #${SCRIPT.panelId} .mcms-tabs { scrollbar-width:none !important; }
04047:         html[data-mcms-mobile-active="true"] #${SCRIPT.panelId} .mcms-header {
04048:             position:sticky !important; top:-8px !important; z-index:8 !important; min-height:48px !important; margin:-8px -8px 7px !important;
04049:             grid-template-columns:minmax(0,1fr) 44px 44px !important; gap:6px !important;
04050:             padding:8px 8px 6px !important; border-radius:16px 16px 0 0 !important; background:rgba(7,11,17,.985) !important;
04051:             border-bottom:1px solid rgba(255,255,255,.10) !important;
04052:         }
04053:         html[data-mcms-mobile-active="true"] #${SCRIPT.panelId} .mcms-drag-handle { cursor:default !important; touch-action:pan-y !important; }
04054:         html[data-mcms-mobile-active="true"] #${SCRIPT.panelId} .mcms-title { font-size:12px !important; letter-spacing:.35px !important; }
04055:         html[data-mcms-mobile-active="true"] #${SCRIPT.panelId} .mcms-subtitle { margin-top:3px !important; font-size:9px !important; }
04056:         html[data-mcms-mobile-active="true"] #${SCRIPT.panelId} .mcms-reset-panel { display:none !important; }
04057:         html[data-mcms-mobile-active="true"] #${SCRIPT.panelId} .mcms-close,
04058:         html[data-mcms-mobile-active="true"] #${SCRIPT.panelId} .mcms-help-button { width:44px !important; height:44px !important; border-radius:12px !important; font-size:20px !important; line-height:42px !important; }
04059:         html[data-mcms-mobile-active="true"] #${SCRIPT.panelId} .mcms-tabs {
04060:             position:sticky !important; top:40px !important; z-index:7 !important; display:flex !important; gap:5px !important;
04061:             margin:0 -2px 7px !important; padding:2px 2px 6px !important; overflow-x:auto !important; overflow-y:hidden !important;
04062:             overscroll-behavior-x:contain !important; -webkit-overflow-scrolling:touch !important; background:rgba(6,10,15,.96) !important;
04063:         }
04064:         html[data-mcms-mobile-active="true"] #${SCRIPT.panelId} .mcms-tab-btn {
04065:             flex:0 0 auto !important; min-width:74px !important; height:40px !important; padding:0 10px !important; border-radius:10px !important;
04066:             font-size:10px !important; line-height:1 !important;
04067:         }
04068:         html[data-mcms-mobile-active="true"] #${SCRIPT.panelId} .mcms-grid-2 { gap:6px !important; }
04069:         html[data-mcms-mobile-active="true"] #${SCRIPT.panelId} .mcms-theme-btn,
04070:         html[data-mcms-mobile-active="true"] #${SCRIPT.panelId} .mcms-toggle-btn,
04071:         html[data-mcms-mobile-active="true"] #${SCRIPT.panelId} .mcms-place-main { min-height:48px !important; height:auto !important; padding:7px !important; border-radius:11px !important; }
04072:         html[data-mcms-mobile-active="true"] #${SCRIPT.panelId} .mcms-iconbox { width:22px !important; height:22px !important; min-width:22px !important; }
04073:         html[data-mcms-mobile-active="true"] #${SCRIPT.panelId} .mcms-label { font-size:11px !important; }
04074:         html[data-mcms-mobile-active="true"] #${SCRIPT.panelId} .mcms-pill { margin-top:4px !important; max-width:110px !important; font-size:8px !important; }
04075:         html[data-mcms-mobile-active="true"] #${SCRIPT.panelId} .mcms-section-label { margin:12px 0 7px !important; font-size:9.5px !important; }
04076:         html[data-mcms-mobile-active="true"] #${SCRIPT.panelId} .mcms-row { grid-template-columns:minmax(0,1fr) minmax(132px,44%) !important; gap:7px !important; margin-bottom:7px !important; }
04077:         html[data-mcms-mobile-active="true"] #${SCRIPT.panelId} .mcms-row-label { font-size:10.5px !important; white-space:normal !important; }
04078:         html[data-mcms-mobile-active="true"] #${SCRIPT.panelId} .mcms-input,
04079:         html[data-mcms-mobile-active="true"] #${SCRIPT.panelId} .mcms-select {
04080:             min-height:44px !important; height:44px !important; border-radius:10px !important; padding:0 9px !important;
04081:             font-size:16px !important; line-height:1.2 !important;
04082:         }
04083:         html[data-mcms-mobile-active="true"] #${SCRIPT.panelId} input[type="range"].mcms-input { min-height:44px !important; }
04084:         html[data-mcms-mobile-active="true"] #${SCRIPT.panelId} .mcms-position-btn,
04085:         html[data-mcms-mobile-active="true"] #${SCRIPT.panelId} .mcms-small-btn,
```

### Lines 4124-4141

```text
04124:             html[data-mcms-mobile-active="true"] #${SCRIPT.panelId} .mcms-row { grid-template-columns:1fr !important; }
04125:             html[data-mcms-mobile-active="true"] #${SCRIPT.panelId} .mcms-row-label { margin-bottom:-2px !important; }
04126:             html[data-mcms-mobile-active="true"] #${SCRIPT.panelId} .mcms-bookmark-row { grid-template-columns:minmax(0,1fr) repeat(4,40px) !important; }
04127:         }
04128:         @media (orientation: landscape) and (max-height: 500px) {
04129:             html[data-mcms-mobile-active="true"] #${SCRIPT.panelId} { border-radius:12px !important; padding-top:6px !important; }
04130:             html[data-mcms-mobile-active="true"] #${SCRIPT.panelId} .mcms-header { min-height:42px !important; padding-top:5px !important; }
04131:             html[data-mcms-mobile-active="true"] #${SCRIPT.panelId} .mcms-subtitle { display:none !important; }
04132:             html[data-mcms-mobile-active="true"] #${SCRIPT.panelId} .mcms-tabs { top:34px !important; }
04133:             html[data-mcms-mobile-active="true"] #${SCRIPT.panelId} .mcms-tab-btn { height:36px !important; }
04134:         }
04135: 
04136:         /* v3.4.2: collapse after the exit animation and override later tablet/mobile layout rules. */
04137:         #${SCRIPT.controlId} {
04138:             transition: width 180ms cubic-bezier(.2,.78,.22,1), max-width 180ms cubic-bezier(.2,.78,.22,1) !important;
04139:         }
04140:         html[data-mcms-command-bar-open="false"] #${SCRIPT.controlId} .mcms-floating-filter,
04141:         html[data-mcms-command-bar-open="false"] #${SCRIPT.controlId} .mcms-screen-pins {
```

### Lines 4154-4177

```text
04154:             background: linear-gradient(180deg, rgba(14,19,27,.97), rgba(7,10,15,.96)) !important;
04155:             color: #eef4fb !important; box-shadow: 0 14px 34px rgba(0,0,0,.48), inset 0 1px 0 rgba(255,255,255,.06) !important;
04156:             font: 700 10px/1.35 Arial, Helvetica, sans-serif !important; pointer-events: none !important;
04157:             opacity: 0 !important; visibility: hidden !important; transform: translateY(4px) scale(.985) !important;
04158:             transition: opacity 110ms ease, transform 110ms ease, visibility 110ms step-end !important; backdrop-filter: blur(6px) !important;
04159:         }
04160:         #${SCRIPT.missionInspectorId}.mcms-open { opacity: 1 !important; visibility: visible !important; transform: translateY(0) scale(1) !important; transition: opacity 110ms ease, transform 110ms ease, visibility 0s step-start !important; }
04161:         #${SCRIPT.missionInspectorId} .mcms-inspector-head { display:flex !important; align-items:flex-start !important; justify-content:space-between !important; gap:8px !important; margin-bottom:7px !important; }
04162:         #${SCRIPT.missionInspectorId} .mcms-inspector-title { display:block !important; min-width:0 !important; color:#fff !important; font-size:12px !important; font-weight:950 !important; line-height:1.2 !important; overflow:hidden !important; text-overflow:ellipsis !important; }
04163:         #${SCRIPT.missionInspectorId} .mcms-inspector-type { flex:0 0 auto !important; padding:3px 5px !important; border-radius:5px !important; border:1px solid rgba(255,255,255,.16) !important; background:rgba(255,255,255,.06) !important; color:#b9c8d8 !important; font-size:7px !important; font-weight:950 !important; letter-spacing:.6px !important; }
04164:         #${SCRIPT.missionInspectorId} .mcms-inspector-type.mcms-alliance { color:#8df3ad !important; border-color:rgba(112,239,155,.38) !important; }
04165:         #${SCRIPT.missionInspectorId} .mcms-inspector-grid { display:grid !important; grid-template-columns:repeat(2,minmax(0,1fr)) !important; gap:5px !important; }
04166:         #${SCRIPT.missionInspectorId} .mcms-inspector-stat { min-width:0 !important; padding:6px 7px !important; border-radius:7px !important; background:rgba(255,255,255,.055) !important; border:1px solid rgba(255,255,255,.08) !important; }
04167:         #${SCRIPT.missionInspectorId} .mcms-inspector-stat span { display:block !important; color:#8393a5 !important; font-size:7px !important; font-weight:900 !important; letter-spacing:.4px !important; text-transform:uppercase !important; }
04168:         #${SCRIPT.missionInspectorId} .mcms-inspector-stat strong { display:block !important; margin-top:2px !important; color:#fff !important; font-size:11px !important; font-weight:950 !important; overflow:hidden !important; text-overflow:ellipsis !important; white-space:nowrap !important; }
04169:         #${SCRIPT.missionInspectorId} .mcms-inspector-alert { margin-top:6px !important; padding:6px 7px !important; border-radius:7px !important; border:1px solid rgba(255,181,71,.34) !important; background:rgba(255,143,31,.11) !important; color:#ffd29a !important; font-size:8px !important; font-weight:900 !important; line-height:1.35 !important; white-space:normal !important; overflow-wrap:anywhere !important; }
04170:         #${SCRIPT.missionInspectorId} .mcms-inspector-alert.mcms-stuck { border-color:rgba(255,74,64,.48) !important; background:rgba(255,44,36,.14) !important; color:#ffaaa4 !important; }
04171: 
04172: 
04173:         .mcms-mission-value-row {
04174:             display: flex !important;
04175:             align-items: center !important;
04176:             justify-content: flex-end !important;
04177:             width: 100% !important;
```

### Lines 4195-4241

```text
04195:             border: 1px solid rgba(235,190,64,.72) !important;
04196:             border-radius: 8px !important;
04197:             background: linear-gradient(145deg, rgba(48,39,13,.96), rgba(19,21,24,.96)) !important;
04198:             color: #ffe59a !important;
04199:             box-shadow: 0 2px 8px rgba(0,0,0,.34) !important;
04200:             font: 900 11px/1.25 Arial, Helvetica, sans-serif !important;
04201:             letter-spacing: .15px !important;
04202:             text-align: right !important;
04203:             white-space: nowrap !important;
04204:             overflow: hidden !important;
04205:             text-overflow: ellipsis !important;
04206:             pointer-events: none !important;
04207:         }
04208:         @media (max-width: 520px) {
04209:             .mcms-mission-value-row { padding-right: 40px !important; }
04210:             .mcms-mission-value-badge { max-width: 100% !important; font-size: 10px !important; }
04211:         }
04212: 
04213:         .mcms-stuck-mission-icon { pointer-events:none !important; }
04214:         .mcms-stuck-mission-badge { display:inline-flex !important; align-items:center !important; justify-content:center !important; min-width:58px !important; height:17px !important; padding:0 6px !important; border-radius:6px !important; border:1px solid rgba(255,86,72,.72) !important; background:rgba(90,10,8,.88) !important; color:#ffd7d2 !important; font:950 8px/17px Arial,Helvetica,sans-serif !important; letter-spacing:.35px !important; text-shadow:0 1px 2px #000 !important; box-shadow:0 0 10px rgba(255,53,39,.32) !important; white-space:nowrap !important; }
04215:         .mcms-stuck-mission-badge.mcms-stuck-severe { background:rgba(130,7,4,.94) !important; border-color:#ff3d2e !important; color:#fff !important; animation:mcmsStuckPulse 1.3s ease-in-out infinite !important; }
04216:         @keyframes mcmsStuckPulse { 0%,100%{box-shadow:0 0 7px rgba(255,53,39,.28);transform:scale(1)} 50%{box-shadow:0 0 16px rgba(255,53,39,.70);transform:scale(1.035)} }
04217: 
04218:         .mcms-mission-spawn-ring { transform-box:fill-box !important; stroke:#67d9ff !important; stroke-width:3 !important; fill:rgba(48,183,255,.12) !important; transform-origin:center !important; animation:mcmsMissionSpawnRing 2.35s cubic-bezier(.12,.72,.18,1) both !important; pointer-events:none !important; }
04219:         .mcms-mission-spawn-label-icon { pointer-events:none !important; }
04220:         .mcms-mission-spawn-label { display:inline-flex !important; align-items:center !important; justify-content:center !important; min-width:86px !important; height:20px !important; padding:0 8px !important; border-radius:7px !important; border:1px solid rgba(98,219,255,.78) !important; background:rgba(4,22,34,.92) !important; color:#aeeeff !important; font:950 8px/20px Arial,Helvetica,sans-serif !important; letter-spacing:.65px !important; text-shadow:0 1px 2px #000 !important; box-shadow:0 0 16px rgba(67,198,255,.42) !important; animation:mcmsMissionSpawnLabel 2.35s ease-out both !important; white-space:nowrap !important; }
04221:         .leaflet-marker-icon.mcms-mission-spawn-focus { animation:mcmsMissionSpawnMarker 2.2s cubic-bezier(.16,.74,.18,1) both !important; }
04222:         @keyframes mcmsMissionSpawnRing { 0%{opacity:0;transform:scale(.25)} 12%{opacity:1;transform:scale(.55)} 75%{opacity:.50;transform:scale(3.2)} 100%{opacity:0;transform:scale(4.2)} }
04223:         @keyframes mcmsMissionSpawnLabel { 0%{opacity:0;transform:translateY(8px) scale(.9)} 14%,72%{opacity:1;transform:translateY(0) scale(1)} 100%{opacity:0;transform:translateY(-8px) scale(.96)} }
04224:         @keyframes mcmsMissionSpawnMarker { 0%{filter:brightness(1);transform:scale(1)} 12%{filter:brightness(1.55) drop-shadow(0 0 10px #53d9ff);transform:scale(1.22)} 34%{filter:brightness(1.15) drop-shadow(0 0 6px #53d9ff);transform:scale(.98)} 58%{filter:brightness(1.35) drop-shadow(0 0 8px #53d9ff);transform:scale(1.12)} 100%{filter:brightness(1);transform:scale(1)} }
04225: 
04226:         #${SCRIPT.panelId} .mcms-profile-list { display:grid !important; gap:6px !important; }
04227:         #${SCRIPT.panelId} .mcms-profile-row { display:grid !important; grid-template-columns:minmax(0,1fr) 36px 36px 25px !important; gap:5px !important; align-items:center !important; }
04228:         #${SCRIPT.panelId} .mcms-profile-main { min-width:0 !important; padding:6px 7px !important; border:1px solid rgba(255,255,255,.09) !important; border-radius:7px !important; background:rgba(255,255,255,.035) !important; }
04229:         #${SCRIPT.panelId} .mcms-profile-main strong,#${SCRIPT.panelId} .mcms-profile-main span { display:block !important; min-width:0 !important; overflow:hidden !important; white-space:nowrap !important; text-overflow:ellipsis !important; }
04230:         #${SCRIPT.panelId} .mcms-profile-main strong { color:#edf4fb !important; font-size:9px !important; }
04231:         #${SCRIPT.panelId} .mcms-profile-main span { color:#8393a5 !important; font-size:7px !important; margin-top:2px !important; }
04232:         #${SCRIPT.panelId} .mcms-config-actions { display:grid !important; grid-template-columns:repeat(3,minmax(0,1fr)) !important; gap:5px !important; }
04233:         #${SCRIPT.panelId} .mcms-config-actions .mcms-small-btn { min-width:0 !important; white-space:nowrap !important; text-overflow:ellipsis !important; }
04234:         html[data-mcms-mobile-active="true"] #${SCRIPT.panelId} .mcms-config-actions { grid-template-columns:repeat(2,minmax(0,1fr)) !important; gap:7px !important; }
04235:         html[data-mcms-mobile-active="true"] #${SCRIPT.panelId} .mcms-config-actions [data-action="reset-config"] { grid-column:1 / -1 !important; }
04236:         #${SCRIPT.panelId} .mcms-hidden-file { display:none !important; }
04237: 
04238: 
04239:         /* v3.7.0 complete interface themes */
04240:         #${SCRIPT.panelId} .mcms-ui-theme-grid {
04241:             display: grid !important;
```

### Lines 4395-4411

```text
04395:             box-shadow: inset 0 1px rgba(255,255,255,.20), 0 0 3px currentColor !important;
04396:         }
04397:         #${SCRIPT.panelId} .mcms-ui-theme-preview-factorio span:nth-child(1) { height: 45% !important; background: #d57b2b !important; color: #d57b2b !important; }
04398:         #${SCRIPT.panelId} .mcms-ui-theme-preview-factorio span:nth-child(2) { height: 78% !important; background: #9fc55a !important; color: #9fc55a !important; }
04399:         #${SCRIPT.panelId} .mcms-ui-theme-preview-factorio span:nth-child(3) { height: 60% !important; background: #e9c16e !important; color: #e9c16e !important; }
04400:         #${SCRIPT.panelId} .mcms-ui-theme-btn[data-ui-theme="factorio"] { grid-column: auto !important; }
04401:         #${SCRIPT.panelId} .mcms-ui-theme-copy { min-width: 0 !important; }
04402:         #${SCRIPT.panelId} .mcms-ui-theme-copy strong,
04403:         #${SCRIPT.panelId} .mcms-ui-theme-copy small { display: block !important; overflow: hidden !important; text-overflow: ellipsis !important; white-space: nowrap !important; }
04404:         #${SCRIPT.panelId} .mcms-ui-theme-copy strong { color: inherit !important; font-size: 10px !important; font-weight: 950 !important; }
04405:         #${SCRIPT.panelId} .mcms-ui-theme-copy small { margin-top: 4px !important; color: rgba(255,255,255,.48) !important; font-size: 7px !important; font-weight: 900 !important; letter-spacing: .7px !important; }
04406: 
04407:         html[data-mcms-tablet-active="true"] #${SCRIPT.panelId} .mcms-ui-theme-btn { height: 72px !important; grid-template-columns: 58px minmax(0,1fr) !important; padding: 8px 10px !important; }
04408:         html[data-mcms-tablet-active="true"] #${SCRIPT.panelId} .mcms-ui-theme-preview { width: 58px !important; height: 44px !important; }
04409:         html[data-mcms-tablet-active="true"] #${SCRIPT.panelId} .mcms-ui-theme-copy strong { font-size: 13px !important; }
04410:         html[data-mcms-tablet-active="true"] #${SCRIPT.panelId} .mcms-ui-theme-copy small { font-size: 8.5px !important; }
04411:         html[data-mcms-mobile-active="true"] #${SCRIPT.panelId} .mcms-ui-theme-grid { gap: 6px !important; }
```

### Lines 4576-4633

```text
04576:             color: var(--mcms-cp-yellow) !important;
04577:             clip-path: polygon(0 0, calc(100% - 6px) 0, 100% 6px, 100% 100%, 0 100%) !important;
04578:         }
04579:         html[data-mcms-ui-theme="cyberpunk"] #${SCRIPT.panelId} .mcms-reset-panel:hover,
04580:         html[data-mcms-ui-theme="cyberpunk"] #${SCRIPT.panelId} .mcms-close:hover {
04581:             background: var(--mcms-cp-red) !important;
04582:             color: #fff !important;
04583:         }
04584:         html[data-mcms-ui-theme="cyberpunk"] #${SCRIPT.panelId} .mcms-tabs {
04585:             gap: 4px !important;
04586:             border-bottom: 1px solid rgba(0,240,255,.20) !important;
04587:             padding-bottom: 7px !important;
04588:         }
04589:         html[data-mcms-ui-theme="cyberpunk"] #${SCRIPT.panelId} .mcms-tab-btn {
04590:             position: relative !important;
04591:             border: 1px solid rgba(0,240,255,.34) !important;
04592:             border-radius: 0 !important;
04593:             background: rgba(0,240,255,.045) !important;
04594:             color: #9fdce0 !important;
04595:             letter-spacing: .55px !important;
04596:             clip-path: polygon(0 0, calc(100% - 5px) 0, 100% 5px, 100% 100%, 0 100%) !important;
04597:         }
04598:         html[data-mcms-ui-theme="cyberpunk"] #${SCRIPT.panelId} .mcms-tab-btn:hover {
04599:             border-color: var(--mcms-cp-cyan) !important;
04600:             color: #fff !important;
04601:             background: rgba(0,240,255,.12) !important;
04602:         }
04603:         html[data-mcms-ui-theme="cyberpunk"] #${SCRIPT.panelId} .mcms-tab-btn.mcms-active {
04604:             border-color: var(--mcms-cp-yellow) !important;
04605:             background: var(--mcms-cp-yellow) !important;
04606:             color: var(--mcms-cp-ink) !important;
04607:             box-shadow: inset 0 -3px 0 var(--mcms-cp-red), 0 0 10px rgba(252,238,10,.20) !important;
04608:         }
04609:         html[data-mcms-ui-theme="cyberpunk"] #${SCRIPT.panelId} .mcms-tab-panel.mcms-active {
04610:             animation: mcmsCyberTabIn 150ms steps(3,end) both !important;
04611:         }
04612:         html[data-mcms-ui-theme="cyberpunk"] #${SCRIPT.panelId} .mcms-section-label {
04613:             position: relative !important;
04614:             margin-top: 11px !important;
04615:             padding: 5px 7px 5px 16px !important;
04616:             border: 0 !important;
04617:             border-bottom: 1px solid rgba(0,240,255,.34) !important;
04618:             background: linear-gradient(90deg, rgba(252,238,10,.14), transparent 70%) !important;
04619:             color: var(--mcms-cp-yellow) !important;
04620:             font-size: 9px !important;
04621:             font-weight: 1000 !important;
04622:             letter-spacing: 1px !important;
04623:             text-transform: uppercase !important;
04624:         }
04625:         html[data-mcms-ui-theme="cyberpunk"] #${SCRIPT.panelId} .mcms-section-label::before {
04626:             content: '' !important;
04627:             position: absolute !important;
04628:             left: 4px !important;
04629:             top: 7px !important;
04630:             width: 6px !important;
04631:             height: 6px !important;
04632:             background: var(--mcms-cp-cyan) !important;
04633:             box-shadow: 0 0 7px rgba(0,240,255,.72) !important;
```

### Lines 5186-5247

```text
05186:         html[data-mcms-ui-theme="fallout4"] #${SCRIPT.panelId} .mcms-close:focus-visible {
05187:             border-color: var(--mcms-fo-red) !important;
05188:             background: var(--mcms-fo-red) !important;
05189:             color: var(--mcms-fo-ink) !important;
05190:             text-shadow: none !important;
05191:         }
05192: 
05193:         /* Tabs and section navigation. */
05194:         html[data-mcms-ui-theme="fallout4"] #${SCRIPT.panelId} .mcms-tabs {
05195:             gap: 4px !important;
05196:             padding: 0 1px 7px 1px !important;
05197:             border-bottom: 1px solid rgba(185,255,114,.24) !important;
05198:         }
05199:         html[data-mcms-ui-theme="fallout4"] #${SCRIPT.panelId} .mcms-tab-btn {
05200:             border: 1px solid #405b38 !important;
05201:             border-radius: 3px !important;
05202:             background: linear-gradient(180deg, #162318, #0a130c) !important;
05203:             color: #cfe8bc !important;
05204:             letter-spacing: .25px !important;
05205:             box-shadow: inset 0 1px rgba(222,255,201,.045) !important;
05206:             text-shadow: 0 0 4px rgba(185,255,114,.16) !important;
05207:         }
05208:         html[data-mcms-ui-theme="fallout4"] #${SCRIPT.panelId} .mcms-tab-btn:hover,
05209:         html[data-mcms-ui-theme="fallout4"] #${SCRIPT.panelId} .mcms-tab-btn:focus-visible {
05210:             border-color: var(--mcms-fo-green-mid) !important;
05211:             background: #243a22 !important;
05212:             color: #f0ffe4 !important;
05213:         }
05214:         html[data-mcms-ui-theme="fallout4"] #${SCRIPT.panelId} .mcms-tab-btn.mcms-active {
05215:             border-color: var(--mcms-fo-green-strong) !important;
05216:             background: var(--mcms-fo-green-strong) !important;
05217:             color: var(--mcms-fo-ink) !important;
05218:             text-shadow: none !important;
05219:             box-shadow: inset 0 -3px 0 #4f7b3c, 0 0 10px rgba(185,255,114,.18) !important;
05220:         }
05221:         html[data-mcms-ui-theme="fallout4"] #${SCRIPT.panelId} .mcms-tab-panel.mcms-active {
05222:             animation: mcmsFalloutDataIn 190ms steps(4,end) both !important;
05223:         }
05224:         html[data-mcms-ui-theme="fallout4"] #${SCRIPT.panelId} .mcms-section-label {
05225:             position: relative !important;
05226:             margin: 11px 0 6px 0 !important;
05227:             padding: 5px 8px 5px 18px !important;
05228:             border: 1px solid rgba(118,171,82,.34) !important;
05229:             border-left: 4px solid var(--mcms-fo-green-mid) !important;
05230:             border-radius: 3px !important;
05231:             background: linear-gradient(90deg, rgba(82,130,65,.24), rgba(12,23,14,.28) 72%) !important;
05232:             color: var(--mcms-fo-green-strong) !important;
05233:             font-size: 9px !important;
05234:             font-weight: 950 !important;
05235:             letter-spacing: .7px !important;
05236:             text-transform: uppercase !important;
05237:             text-shadow: 0 0 5px rgba(185,255,114,.25) !important;
05238:         }
05239:         html[data-mcms-ui-theme="fallout4"] #${SCRIPT.panelId} .mcms-section-label::before {
05240:             content: '▸' !important;
05241:             position: absolute !important;
05242:             left: 6px !important;
05243:             top: 4px !important;
05244:             color: var(--mcms-fo-amber) !important;
05245:             text-shadow: 0 0 4px rgba(255,211,106,.32) !important;
05246:         }
05247: 
```

### Lines 5674-5690

```text
05674:         @keyframes mcmsFalloutSweep {
05675:             0% { transform: translateX(0); opacity: 0; }
05676:             8% { opacity: 1; }
05677:             62% { opacity: .85; }
05678:             72%, 100% { transform: translateX(560%); opacity: 0; }
05679:         }
05680:         @media (prefers-reduced-motion: reduce) {
05681:             html[data-mcms-ui-theme="fallout4"] #${SCRIPT.panelId}.mcms-open,
05682:             html[data-mcms-ui-theme="fallout4"] #${SCRIPT.panelId} .mcms-tab-panel.mcms-active,
05683:             html[data-mcms-ui-theme="fallout4"] #${SCRIPT.panelId} .mcms-header::after,
05684:             html[data-mcms-ui-theme="fallout4"] #${SCRIPT.controlId} .mcms-float-btn.mcms-on {
05685:                 animation: none !important;
05686:             }
05687:             html[data-mcms-ui-theme="fallout4"] #${SCRIPT.controlId} .mcms-float-btn,
05688:             html[data-mcms-ui-theme="fallout4"] #${SCRIPT.controlId} .mcms-screen-pin-btn,
05689:             html[data-mcms-ui-theme="fallout4"] #${SCRIPT.panelId} button {
05690:                 transition: none !important;
```

### Lines 5908-5969

```text
05908:         html[data-mcms-ui-theme="umbrella"] #${SCRIPT.panelId} .mcms-close:focus-visible {
05909:             border-color: var(--mcms-um-red-hot) !important;
05910:             background: var(--mcms-um-red-hot) !important;
05911:             color: var(--mcms-um-ink) !important;
05912:             text-shadow: none !important;
05913:         }
05914: 
05915:         /* Tabs and section navigation. */
05916:         html[data-mcms-ui-theme="umbrella"] #${SCRIPT.panelId} .mcms-tabs {
05917:             gap: 4px !important;
05918:             padding: 0 1px 7px 1px !important;
05919:             border-bottom: 1px solid rgba(216,25,63,.24) !important;
05920:         }
05921:         html[data-mcms-ui-theme="umbrella"] #${SCRIPT.panelId} .mcms-tab-btn {
05922:             border: 1px solid #424852 !important;
05923:             border-radius: 3px !important;
05924:             background: linear-gradient(180deg, #191d24, #0e1117) !important;
05925:             color: #dfe3e8 !important;
05926:             letter-spacing: .25px !important;
05927:             box-shadow: inset 0 1px rgba(255,255,255,.045) !important;
05928:             text-shadow: 0 0 4px rgba(216,25,63,.16) !important;
05929:         }
05930:         html[data-mcms-ui-theme="umbrella"] #${SCRIPT.panelId} .mcms-tab-btn:hover,
05931:         html[data-mcms-ui-theme="umbrella"] #${SCRIPT.panelId} .mcms-tab-btn:focus-visible {
05932:             border-color: var(--mcms-um-red) !important;
05933:             background: #2b3039 !important;
05934:             color: #ffffff !important;
05935:         }
05936:         html[data-mcms-ui-theme="umbrella"] #${SCRIPT.panelId} .mcms-tab-btn.mcms-active {
05937:             border-color: var(--mcms-um-white-strong) !important;
05938:             background: var(--mcms-um-white-strong) !important;
05939:             color: var(--mcms-um-ink) !important;
05940:             text-shadow: none !important;
05941:             box-shadow: inset 0 -3px 0 #760e25, 0 0 10px rgba(216,25,63,.18) !important;
05942:         }
05943:         html[data-mcms-ui-theme="umbrella"] #${SCRIPT.panelId} .mcms-tab-panel.mcms-active {
05944:             animation: mcmsUmbrellaDataIn 190ms steps(4,end) both !important;
05945:         }
05946:         html[data-mcms-ui-theme="umbrella"] #${SCRIPT.panelId} .mcms-section-label {
05947:             position: relative !important;
05948:             margin: 11px 0 6px 0 !important;
05949:             padding: 5px 8px 5px 18px !important;
05950:             border: 1px solid rgba(118,171,82,.34) !important;
05951:             border-left: 4px solid var(--mcms-um-red) !important;
05952:             border-radius: 3px !important;
05953:             background: linear-gradient(90deg, rgba(82,130,65,.24), rgba(12,23,14,.28) 72%) !important;
05954:             color: var(--mcms-um-white-strong) !important;
05955:             font-size: 9px !important;
05956:             font-weight: 950 !important;
05957:             letter-spacing: .7px !important;
05958:             text-transform: uppercase !important;
05959:             text-shadow: 0 0 5px rgba(216,25,63,.25) !important;
05960:         }
05961:         html[data-mcms-ui-theme="umbrella"] #${SCRIPT.panelId} .mcms-section-label::before {
05962:             content: '▸' !important;
05963:             position: absolute !important;
05964:             left: 6px !important;
05965:             top: 4px !important;
05966:             color: var(--mcms-um-amber) !important;
05967:             text-shadow: 0 0 4px rgba(255,211,106,.32) !important;
05968:         }
05969: 
```

### Lines 6396-6412

```text
06396:         @keyframes mcmsUmbrellaSweep {
06397:             0% { transform: translateX(0); opacity: 0; }
06398:             8% { opacity: 1; }
06399:             62% { opacity: .85; }
06400:             72%, 100% { transform: translateX(560%); opacity: 0; }
06401:         }
06402:         @media (prefers-reduced-motion: reduce) {
06403:             html[data-mcms-ui-theme="umbrella"] #${SCRIPT.panelId}.mcms-open,
06404:             html[data-mcms-ui-theme="umbrella"] #${SCRIPT.panelId} .mcms-tab-panel.mcms-active,
06405:             html[data-mcms-ui-theme="umbrella"] #${SCRIPT.panelId} .mcms-header::after,
06406:             html[data-mcms-ui-theme="umbrella"] #${SCRIPT.controlId} .mcms-float-btn.mcms-on {
06407:                 animation: none !important;
06408:             }
06409:             html[data-mcms-ui-theme="umbrella"] #${SCRIPT.controlId} .mcms-float-btn,
06410:             html[data-mcms-ui-theme="umbrella"] #${SCRIPT.controlId} .mcms-screen-pin-btn,
06411:             html[data-mcms-ui-theme="umbrella"] #${SCRIPT.panelId} button {
06412:                 transition: none !important;
```

### Lines 6535-6593

```text
06535:             font-weight: 950 !important;
06536:             letter-spacing: 1.2px !important;
06537:             text-shadow: 2px 0 0 rgba(216,25,63,.55) !important;
06538:         }
06539:         html[data-mcms-ui-theme="umbrella"] #${SCRIPT.panelId} .mcms-subtitle {
06540:             color: #d3d8df !important;
06541:             text-shadow: none !important;
06542:         }
06543:         html[data-mcms-ui-theme="umbrella"] #${SCRIPT.panelId} .mcms-tabs {
06544:             gap: 3px !important;
06545:             border-bottom: 1px solid #646b75 !important;
06546:         }
06547:         html[data-mcms-ui-theme="umbrella"] #${SCRIPT.panelId} .mcms-tab-btn {
06548:             border-radius: 1px !important;
06549:             border-color: #555c66 !important;
06550:             background: linear-gradient(180deg, #252932, #11141a) !important;
06551:             color: #e8ebef !important;
06552:             text-shadow: none !important;
06553:             clip-path: polygon(0 0, calc(100% - 5px) 0, 100% 5px, 100% 100%, 0 100%) !important;
06554:         }
06555:         html[data-mcms-ui-theme="umbrella"] #${SCRIPT.panelId} .mcms-tab-btn:hover,
06556:         html[data-mcms-ui-theme="umbrella"] #${SCRIPT.panelId} .mcms-tab-btn:focus-visible {
06557:             border-color: #ffffff !important;
06558:             background: #363b45 !important;
06559:             color: #ffffff !important;
06560:         }
06561:         html[data-mcms-ui-theme="umbrella"] #${SCRIPT.panelId} .mcms-tab-btn.mcms-active {
06562:             border-color: #8e0c28 !important;
06563:             background: linear-gradient(180deg, #d81d43, #a10d2d) !important;
06564:             color: #ffffff !important;
06565:             box-shadow: inset 0 -3px 0 #ffffff, 0 0 9px rgba(216,25,63,.20) !important;
06566:         }
06567:         html[data-mcms-ui-theme="umbrella"] #${SCRIPT.panelId} .mcms-tab-panel.mcms-active {
06568:             animation: mcmsUmbrellaRecordIn 180ms ease-out both !important;
06569:         }
06570:         html[data-mcms-ui-theme="umbrella"] #${SCRIPT.panelId} .mcms-section-label {
06571:             min-height: 24px !important;
06572:             padding: 5px 8px 5px 23px !important;
06573:             border: 1px solid #aeb4bd !important;
06574:             border-left: 6px solid #c8102e !important;
06575:             border-radius: 1px !important;
06576:             background:
06577:                 repeating-linear-gradient(135deg, rgba(0,0,0,.035) 0 4px, transparent 4px 8px),
06578:                 linear-gradient(180deg, #f4f6f8, #dfe3e8) !important;
06579:             color: #11141a !important;
06580:             letter-spacing: .85px !important;
06581:             text-shadow: none !important;
06582:             box-shadow: inset 0 -1px rgba(0,0,0,.10) !important;
06583:             clip-path: polygon(0 0, calc(100% - 8px) 0, 100% 8px, 100% 100%, 0 100%) !important;
06584:         }
06585:         html[data-mcms-ui-theme="umbrella"] #${SCRIPT.panelId} .mcms-section-label::before {
06586:             content: '☣' !important;
06587:             left: 7px !important;
06588:             color: #a60d2c !important;
06589:             font-size: 11px !important;
06590:             text-shadow: none !important;
06591:         }
06592: 
06593:         html[data-mcms-ui-theme="umbrella"] #${SCRIPT.panelId} .mcms-theme-btn,
```

### Lines 6849-6865

```text
06849:         @keyframes mcmsUmbrellaScan {
06850:             0% { transform: translateX(0); opacity: 0; }
06851:             8% { opacity: 1; }
06852:             58% { opacity: .88; }
06853:             70%, 100% { transform: translateX(760%); opacity: 0; }
06854:         }
06855:         @media (prefers-reduced-motion: reduce) {
06856:             html[data-mcms-ui-theme="umbrella"] #${SCRIPT.panelId}.mcms-open,
06857:             html[data-mcms-ui-theme="umbrella"] #${SCRIPT.panelId} .mcms-tab-panel.mcms-active,
06858:             html[data-mcms-ui-theme="umbrella"] #${SCRIPT.panelId} .mcms-header::after,
06859:             html[data-mcms-ui-theme="umbrella"] #${SCRIPT.controlId} .mcms-float-btn.mcms-on {
06860:                 animation: none !important;
06861:             }
06862:             html[data-mcms-ui-theme="umbrella"] #${SCRIPT.controlId} .mcms-float-btn,
06863:             html[data-mcms-ui-theme="umbrella"] #${SCRIPT.controlId} .mcms-screen-pin-btn,
06864:             html[data-mcms-ui-theme="umbrella"] #${SCRIPT.panelId} button {
06865:                 transition: none !important;
```

### Lines 6885-6901

```text
06885:         @keyframes mcmsCyberScan {
06886:             0% { transform: translateX(-110%); opacity: 0; }
06887:             8% { opacity: 1; }
06888:             42% { opacity: 1; }
06889:             50%, 100% { transform: translateX(390%); opacity: 0; }
06890:         }
06891:         @media (prefers-reduced-motion: reduce) {
06892:             html[data-mcms-ui-theme="cyberpunk"] #${SCRIPT.panelId}.mcms-open,
06893:             html[data-mcms-ui-theme="cyberpunk"] #${SCRIPT.panelId} .mcms-tab-panel.mcms-active,
06894:             html[data-mcms-ui-theme="cyberpunk"] #${SCRIPT.panelId} .mcms-header::after,
06895:             html[data-mcms-ui-theme="cyberpunk"] #${SCRIPT.controlId} .mcms-float-btn.mcms-on {
06896:                 animation: none !important;
06897:             }
06898:             html[data-mcms-ui-theme="cyberpunk"] #${SCRIPT.controlId} .mcms-float-btn,
06899:             html[data-mcms-ui-theme="cyberpunk"] #${SCRIPT.controlId} .mcms-screen-pin-btn,
06900:             html[data-mcms-ui-theme="cyberpunk"] #${SCRIPT.panelId} button {
06901:                 transition: none !important;
```

### Lines 7104-7166

```text
07104:         html[data-mcms-ui-theme="factorio"] #${SCRIPT.panelId} .mcms-reset-panel:focus-visible,
07105:         html[data-mcms-ui-theme="factorio"] #${SCRIPT.panelId} .mcms-close:focus-visible {
07106:             border-color: #ec9743 !important;
07107:             background: #df842f !important;
07108:             color: var(--mcms-fac-ink) !important;
07109:             text-shadow: none !important;
07110:         }
07111: 
07112:         html[data-mcms-ui-theme="factorio"] #${SCRIPT.panelId} .mcms-tabs {
07113:             gap: 3px !important;
07114:             padding: 4px !important;
07115:             border-bottom: 1px solid #4d5048 !important;
07116:             background: #181a17 !important;
07117:         }
07118:         html[data-mcms-ui-theme="factorio"] #${SCRIPT.panelId} .mcms-tab-btn {
07119:             border: 1px solid #494c45 !important;
07120:             border-radius: 2px !important;
07121:             background: linear-gradient(180deg, #343731, #222420) !important;
07122:             color: #d5c49d !important;
07123:             box-shadow: inset 0 1px rgba(255,255,255,.05) !important;
07124:         }
07125:         html[data-mcms-ui-theme="factorio"] #${SCRIPT.panelId} .mcms-tab-btn:hover,
07126:         html[data-mcms-ui-theme="factorio"] #${SCRIPT.panelId} .mcms-tab-btn:focus-visible {
07127:             border-color: #bd6b2a !important;
07128:             color: #f4d7a1 !important;
07129:             background: linear-gradient(180deg, #47453e, #2b2923) !important;
07130:         }
07131:         html[data-mcms-ui-theme="factorio"] #${SCRIPT.panelId} .mcms-tab-btn.mcms-active {
07132:             border-color: #f0aa5a !important;
07133:             background: linear-gradient(180deg, #f0a04b, #cb6d28) !important;
07134:             color: var(--mcms-fac-ink) !important;
07135:             box-shadow: inset 0 1px rgba(255,255,255,.28), inset 0 -4px 8px rgba(96,40,9,.18) !important;
07136:             text-shadow: none !important;
07137:         }
07138:         html[data-mcms-ui-theme="factorio"] #${SCRIPT.panelId} .mcms-tab-panel.mcms-active {
07139:             animation: mcmsFactorioRecordIn 190ms ease-out both !important;
07140:         }
07141:         html[data-mcms-ui-theme="factorio"] #${SCRIPT.panelId} .mcms-section-label {
07142:             position: relative !important;
07143:             min-height: 25px !important;
07144:             padding: 7px 10px 6px 28px !important;
07145:             border: 1px solid #5b5e56 !important;
07146:             border-left: 5px solid #d97b2c !important;
07147:             border-radius: 2px !important;
07148:             background:
07149:                 repeating-linear-gradient(135deg, rgba(230,139,45,.16) 0 5px, transparent 5px 10px),
07150:                 linear-gradient(180deg, #3c3f39, #252723) !important;
07151:             color: #f0d8aa !important;
07152:             font-size: 8px !important;
07153:             font-weight: 950 !important;
07154:             letter-spacing: .8px !important;
07155:             text-transform: uppercase !important;
07156:             box-shadow: inset 0 1px rgba(255,255,255,.06) !important;
07157:         }
07158:         html[data-mcms-ui-theme="factorio"] #${SCRIPT.panelId} .mcms-section-label::before {
07159:             content: "⚙" !important;
07160:             position: absolute !important;
07161:             left: 8px !important;
07162:             top: 50% !important;
07163:             transform: translateY(-50%) !important;
07164:             color: #f1a14d !important;
07165:             font-size: 11px !important;
07166:         }
```

### Lines 7467-7483

```text
07467:             0%, 100% { filter: brightness(1); }
07468:             46% { filter: brightness(1); }
07469:             48% { filter: brightness(1.10); }
07470:             50% { filter: brightness(.97); }
07471:             52% { filter: brightness(1.05); }
07472:         }
07473:         @media (prefers-reduced-motion: reduce) {
07474:             html[data-mcms-ui-theme="factorio"] #${SCRIPT.panelId}.mcms-open,
07475:             html[data-mcms-ui-theme="factorio"] #${SCRIPT.panelId} .mcms-tab-panel.mcms-active,
07476:             html[data-mcms-ui-theme="factorio"] #${SCRIPT.panelId} .mcms-header::after,
07477:             html[data-mcms-ui-theme="factorio"] #${SCRIPT.controlId} .mcms-float-btn.mcms-on {
07478:                 animation: none !important;
07479:             }
07480:             html[data-mcms-ui-theme="factorio"] #${SCRIPT.controlId} .mcms-float-btn,
07481:             html[data-mcms-ui-theme="factorio"] #${SCRIPT.controlId} .mcms-screen-pin-btn,
07482:             html[data-mcms-ui-theme="factorio"] #${SCRIPT.panelId} button {
07483:                 transition: none !important;
```

### Lines 7989-8006

```text
07989:         }
07990:         #${SCRIPT.vehicleStatusId} .mcms-vcs-status {
07991:             min-width:0 !important;
07992:             overflow:hidden !important;
07993:             color:var(--mcms-vcs-text) !important;
07994:             font-size:10.5px !important;
07995:             font-weight:850 !important;
07996:             line-height:1.25 !important;
07997:             text-overflow:ellipsis !important;
07998:             white-space:nowrap !important;
07999:         }
08000:         #${SCRIPT.vehicleStatusId} .mcms-vcs-count {
08001:             color:var(--mcms-vcs-text) !important;
08002:             font-size:12px !important;
08003:             font-weight:950 !important;
08004:             font-variant-numeric:tabular-nums !important;
08005:         }
08006:         #${SCRIPT.vehicleStatusId} .mcms-vcs-total-row {
```

### Lines 8068-8084

```text
08068:         html[data-mcms-mobile-active="true"] #${SCRIPT.vehicleStatusId} .mcms-vcs-title { font-size:15px !important; }
08069:         html[data-mcms-mobile-active="true"] #${SCRIPT.vehicleStatusId} .mcms-vcs-subtitle { font-size:9px !important; }
08070:         html[data-mcms-mobile-active="true"] #${SCRIPT.vehicleStatusId} .mcms-vcs-refresh,
08071:         html[data-mcms-mobile-active="true"] #${SCRIPT.vehicleStatusId} .mcms-vcs-close { width:42px !important; height:42px !important; font-size:21px !important; }
08072:         html[data-mcms-mobile-active="true"] #${SCRIPT.vehicleStatusId} .mcms-vcs-meta { align-items:flex-start !important; flex-direction:column !important; gap:2px !important; font-size:8.5px !important; }
08073:         html[data-mcms-mobile-active="true"] #${SCRIPT.vehicleStatusId} .mcms-vcs-table-row { grid-template-columns:48px minmax(0,1fr) 66px !important; gap:6px !important; min-height:45px !important; padding:7px 7px !important; }
08074:         html[data-mcms-mobile-active="true"] #${SCRIPT.vehicleStatusId} .mcms-vcs-table-head { min-height:30px !important; font-size:7.5px !important; letter-spacing:.32px !important; }
08075:         html[data-mcms-mobile-active="true"] #${SCRIPT.vehicleStatusId} .mcms-vcs-code { width:34px !important; height:27px !important; font-size:12px !important; }
08076:         html[data-mcms-mobile-active="true"] #${SCRIPT.vehicleStatusId} .mcms-vcs-status { font-size:10px !important; white-space:normal !important; overflow:visible !important; text-overflow:clip !important; }
08077:         html[data-mcms-mobile-active="true"] #${SCRIPT.vehicleStatusId} .mcms-vcs-count { font-size:12px !important; }
08078:         html[data-mcms-mobile-active="true"] #${SCRIPT.vehicleStatusId} .mcms-vcs-footnote { font-size:7.5px !important; }
08079: 
08080:         /* Cyberpunk command terminal. */
08081:         html[data-mcms-ui-theme="cyberpunk"] #${SCRIPT.vehicleStatusId} {
08082:             --mcms-vcs-bg:linear-gradient(145deg,rgba(7,10,13,.99),rgba(15,18,20,.99));
08083:             --mcms-vcs-panel:rgba(255,231,0,.035);
08084:             --mcms-vcs-line:rgba(255,231,0,.28);
```

### Lines 8284-8300

```text
08284:             display:block !important;
08285:             margin-top:3px !important;
08286:             color:inherit !important;
08287:             font-size:7.4px !important;
08288:             line-height:1.1 !important;
08289:             font-weight:850 !important;
08290:             letter-spacing:.2px !important;
08291:             opacity:.74 !important;
08292:             white-space:nowrap !important;
08293:         }
08294:         #${SCRIPT.criticalDrawerId} .mcms-critical-age-filters {
08295:             display:grid !important;
08296:             grid-template-columns:auto repeat(4,minmax(34px,1fr)) !important;
08297:             align-items:stretch !important;
08298:             gap:3px !important;
08299:             max-width:278px !important;
08300:             margin-top:5px !important;
```

### Lines 8326-8342

```text
08326:             cursor:pointer !important;
08327:             transition:transform 120ms ease,filter 120ms ease,box-shadow 120ms ease,background 120ms ease !important;
08328:         }
08329:         #${SCRIPT.criticalDrawerId} .mcms-critical-age-filter span {
08330:             font-size:7.3px !important;
08331:             line-height:1 !important;
08332:             font-weight:950 !important;
08333:             letter-spacing:.18px !important;
08334:             white-space:nowrap !important;
08335:         }
08336:         #${SCRIPT.criticalDrawerId} .mcms-critical-age-filter strong {
08337:             font-size:8.5px !important;
08338:             line-height:1 !important;
08339:             font-weight:950 !important;
08340:         }
08341:         #${SCRIPT.criticalDrawerId} .mcms-critical-age-filter i {
08342:             position:absolute !important;
```

### Lines 8430-8448

```text
08430:             transition:transform 130ms ease,filter 130ms ease,box-shadow 130ms ease,background 130ms ease !important;
08431:         }
08432:         #${SCRIPT.criticalDrawerId} .mcms-critical-type-filter span {
08433:             overflow:hidden !important;
08434:             font-size:7.2px !important;
08435:             line-height:1 !important;
08436:             font-weight:950 !important;
08437:             letter-spacing:.25px !important;
08438:             text-overflow:ellipsis !important;
08439:             text-transform:uppercase !important;
08440:             white-space:nowrap !important;
08441:         }
08442:         #${SCRIPT.criticalDrawerId} .mcms-critical-type-filter strong {
08443:             font-size:11px !important;
08444:             line-height:1 !important;
08445:             font-weight:950 !important;
08446:         }
08447:         #${SCRIPT.criticalDrawerId} .mcms-critical-type-filter i {
08448:             position:absolute !important;
```

### Lines 8595-8612

```text
08595:         #${SCRIPT.criticalDrawerId} .mcms-critical-value-card strong {
08596:             display:block !important;
08597:             margin-top:3px !important;
08598:             overflow:hidden !important;
08599:             color:#f5fbff !important;
08600:             font-size:10px !important;
08601:             line-height:1 !important;
08602:             font-weight:950 !important;
08603:             text-overflow:ellipsis !important;
08604:             white-space:nowrap !important;
08605:         }
08606:         #${SCRIPT.criticalDrawerId} .mcms-value-no-scene { border-color:rgba(255,72,72,.48) !important; color:#ffaaaa !important; }
08607:         #${SCRIPT.criticalDrawerId} .mcms-value-assistance { border-color:rgba(255,143,45,.52) !important; color:#ffc17c !important; }
08608:         #${SCRIPT.criticalDrawerId} .mcms-value-all { border-color:rgba(98,181,255,.48) !important; color:#a9dcff !important; }
08609: 
08610:         #${SCRIPT.criticalDrawerId} button.mcms-critical-summary-card {
08611:             position:relative !important;
08612:             appearance:none !important;
```

### Lines 8681-8697

```text
08681:             padding:2px 6px !important;
08682:             border:1px solid currentColor !important;
08683:             border-radius:999px !important;
08684:             font-size:6px !important;
08685:             line-height:1 !important;
08686:             font-weight:950 !important;
08687:             letter-spacing:.32px !important;
08688:             text-transform:uppercase !important;
08689:             white-space:nowrap !important;
08690:         }
08691:         #${SCRIPT.criticalDrawerId} .mcms-critical-top-actions {
08692:             display:flex !important;
08693:             align-items:center !important;
08694:             justify-content:flex-end !important;
08695:             gap:4px !important;
08696:             min-width:0 !important;
08697:         }
```

### Lines 8746-8764

```text
08746:             font-size:10px !important;
08747:             line-height:1 !important;
08748:         }
08749:         #${SCRIPT.criticalDrawerId} .mcms-critical-name {
08750:             display:block !important;
08751:             margin-top:4px !important;
08752:             font-size:12px !important;
08753:             line-height:1.18 !important;
08754:             white-space:normal !important;
08755:             overflow:visible !important;
08756:             text-overflow:clip !important;
08757:         }
08758:         #${SCRIPT.criticalDrawerId} .mcms-critical-titleline {
08759:             display:flex !important;
08760:             align-items:center !important;
08761:             justify-content:space-between !important;
08762:             gap:6px !important;
08763:             margin-top:4px !important;
08764:             min-width:0 !important;
```

### Lines 8777-8793

```text
08777:             min-height:22px !important;
08778:             padding:3px 7px !important;
08779:             border:1px solid rgba(112,210,255,.82) !important;
08780:             border-radius:999px !important;
08781:             background:linear-gradient(135deg,rgba(12,72,105,.92),rgba(5,38,62,.92)) !important;
08782:             color:#c9efff !important;
08783:             box-shadow:inset 0 0 0 1px rgba(255,255,255,.06),0 0 10px rgba(75,190,255,.16) !important;
08784:             text-shadow:none !important;
08785:             white-space:nowrap !important;
08786:         }
08787:         #${SCRIPT.criticalDrawerId} .mcms-critical-patients .mcms-patient-icon {
08788:             color:#79d9ff !important;
08789:             font:950 10px/1 Arial,sans-serif !important;
08790:         }
08791:         #${SCRIPT.criticalDrawerId} .mcms-critical-patients strong {
08792:             color:#fff !important;
08793:             font:950 10px/1 Arial,sans-serif !important;
```

### Lines 8833-8849

```text
08833:         }
08834:         #${SCRIPT.criticalDrawerId} .mcms-critical-state-copy small {
08835:             display:block !important;
08836:             margin-top:2px !important;
08837:             font-size:8px !important;
08838:             line-height:1.17 !important;
08839:             font-weight:750 !important;
08840:             opacity:.9 !important;
08841:             white-space:normal !important;
08842:         }
08843:         #${SCRIPT.criticalDrawerId} .mcms-critical-unit-grid {
08844:             display:grid !important;
08845:             grid-template-columns:repeat(2,minmax(0,1fr)) !important;
08846:             gap:4px !important;
08847:             margin-top:0 !important;
08848:         }
08849:         #${SCRIPT.criticalDrawerId} .mcms-critical-unit-chip {
```

### Lines 9077-9093

```text
09077:             max-width:calc(100vw - 8px) !important;
09078:             max-height:min(86dvh,calc(100dvh - env(safe-area-inset-top) - 8px)) !important;
09079:             padding:8px 7px calc(8px + env(safe-area-inset-bottom)) !important;
09080:         }
09081:         html[data-mcms-mobile-active="true"] #${SCRIPT.criticalDrawerId} .mcms-drawer-title { font-size:13px !important; }
09082:         html[data-mcms-mobile-active="true"] #${SCRIPT.criticalDrawerId} .mcms-drawer-subtitle { font-size:7.7px !important; }
09083:         html[data-mcms-mobile-active="true"] #${SCRIPT.criticalDrawerId} .mcms-drawer-refresh,
09084:         html[data-mcms-mobile-active="true"] #${SCRIPT.criticalDrawerId} .mcms-drawer-close { width:38px !important; height:38px !important; font-size:19px !important; }
09085:         html[data-mcms-mobile-active="true"] #${SCRIPT.criticalDrawerId} .mcms-critical-refreshed { font-size:7.5px !important; white-space:normal !important; }
09086:         html[data-mcms-mobile-active="true"] #${SCRIPT.criticalDrawerId} .mcms-critical-topline { align-items:flex-start !important; }
09087:         html[data-mcms-mobile-active="true"] #${SCRIPT.criticalDrawerId} .mcms-critical-top-actions { gap:3px !important; flex-wrap:wrap !important; }
09088:         html[data-mcms-mobile-active="true"] #${SCRIPT.criticalDrawerId} .mcms-critical-zoom,
09089:         html[data-mcms-mobile-active="true"] #${SCRIPT.criticalDrawerId} .mcms-critical-open { min-width:50px !important; height:30px !important; padding:0 6px !important; font-size:8px !important; }
09090:         html[data-mcms-mobile-active="true"] #${SCRIPT.criticalDrawerId} .mcms-critical-values-grid { grid-template-columns:1fr !important; }
09091:         html[data-mcms-mobile-active="true"] #${SCRIPT.criticalDrawerId} .mcms-critical-value-card {
09092:             display:grid !important;
09093:             grid-template-columns:minmax(0,1fr) auto !important;
```

### Lines 9186-9212

```text
09186:             text-align:center !important;
09187:             cursor:help !important;
09188:         }
09189:         #${SCRIPT.criticalDrawerId} .mcms-critical-value-card span {
09190:             display:block !important;
09191:             font-size:5.7px !important;
09192:             line-height:1 !important;
09193:             letter-spacing:.17px !important;
09194:             white-space:nowrap !important;
09195:         }
09196:         #${SCRIPT.criticalDrawerId} .mcms-critical-value-card strong {
09197:             display:block !important;
09198:             max-width:100% !important;
09199:             margin:1px 0 0 !important;
09200:             overflow:hidden !important;
09201:             font-size:9.2px !important;
09202:             line-height:1 !important;
09203:             text-overflow:ellipsis !important;
09204:             white-space:nowrap !important;
09205:         }
09206:         #${SCRIPT.criticalDrawerId} .mcms-critical-values-clear {
09207:             align-self:stretch !important;
09208:             min-width:35px !important;
09209:             min-height:25px !important;
09210:             padding:0 5px !important;
09211:             border:1px solid rgba(255,255,255,.32) !important;
09212:             border-radius:5px !important;
```

### Lines 9444-9460

```text
09444:             padding:0 10px;
09445:             border-right:1px solid rgba(126,202,255,.34);
09446:             background:linear-gradient(180deg,#24628e,#173e5b);
09447:             color:#fff;
09448:             font-size:9px;
09449:             font-weight:900;
09450:             letter-spacing:.75px;
09451:             text-transform:uppercase;
09452:             white-space:nowrap;
09453:         }
09454:         #${SCRIPT.majorIncidentFeedId} .mcms-incident-feed-label::before {
09455:             content:"●";
09456:             color:#ff4655;
09457:             font-size:9px;
09458:             text-shadow:0 0 7px rgba(255,70,85,.9);
09459:         }
09460:         #${SCRIPT.majorIncidentFeedId} .mcms-incident-feed-viewport {
```

### Lines 9512-9528

```text
09512:             height:100%;
09513:             margin:0;
09514:             padding:0 14px;
09515:             border:0;
09516:             border-right:1px solid rgba(164,205,232,.17);
09517:             background:transparent;
09518:             color:inherit;
09519:             font:inherit;
09520:             white-space:nowrap;
09521:             cursor:pointer;
09522:             transition:background .16s ease,filter .16s ease;
09523:         }
09524:         #${SCRIPT.majorIncidentFeedId} .mcms-incident-feed-item:hover,
09525:         #${SCRIPT.majorIncidentFeedId} .mcms-incident-feed-item:focus-visible {
09526:             background:rgba(255,255,255,.09);
09527:             outline:2px solid #fff;
09528:             outline-offset:-2px;
```

### Lines 9749-9765

```text
09749:             min-height:22px !important;
09750:             padding:2px 6px !important;
09751:             border:1px solid rgba(93,238,147,.72) !important;
09752:             border-radius:999px !important;
09753:             background:rgba(4,60,30,.86) !important;
09754:             color:#cdf9dc !important;
09755:             font:950 7.4px/1 Arial,sans-serif !important;
09756:             letter-spacing:.2px !important;
09757:             white-space:nowrap !important;
09758:             box-shadow:inset 0 0 0 1px rgba(255,255,255,.04),0 0 8px rgba(55,222,125,.14) !important;
09759:         }
09760:         html[data-mcms-ui-theme] #${SCRIPT.criticalDrawerId} .mcms-critical-row.mcms-critical-state-enroute {
09761:             border-color:rgba(72,188,255,.90) !important;
09762:             background:linear-gradient(135deg,rgba(4,55,88,.82),rgba(7,31,52,.74)) !important;
09763:             box-shadow:inset 4px 0 0 #48bcff,0 0 12px rgba(72,188,255,.18) !important;
09764:         }
09765:         html[data-mcms-ui-theme] #${SCRIPT.criticalDrawerId} .mcms-critical-row.mcms-critical-has-enroute:not(.mcms-critical-state-enroute):not(.mcms-critical-state-clearing) {
```

### Lines 9934-9950

```text
09934:             border:1px solid rgba(255,255,255,.22) !important;
09935:             border-radius:999px !important;
09936:             background:rgba(4,12,20,.72) !important;
09937:             color:#edf7ff !important;
09938:             font:900 5.8px/1 Arial,sans-serif !important;
09939:             letter-spacing:.18px !important;
09940:             text-transform:uppercase !important;
09941:             text-shadow:none !important;
09942:             white-space:nowrap !important;
09943:         }
09944:         #${SCRIPT.criticalDrawerId} .mcms-critical-city { color:#f5f7fa !important; }
09945:         #${SCRIPT.criticalDrawerId} .mcms-critical-postcode { border-color:rgba(88,194,255,.64) !important; color:#9fddff !important; }
09946:         #${SCRIPT.criticalDrawerId} .mcms-critical-distance { border-color:rgba(106,224,196,.55) !important; color:#aef3df !important; }
09947:         html[data-mcms-tablet-active="true"] #${SCRIPT.criticalDrawerId} .mcms-drawer-expand {
09948:             min-width:74px !important;
09949:             height:44px !important;
09950:             border-radius:10px !important;
```

### Lines 10010-10026

```text
10010:             padding:2px 6px !important;
10011:             border:1px solid rgba(255,99,190,.92) !important;
10012:             border-radius:999px !important;
10013:             background:linear-gradient(135deg,rgba(112,12,75,.94),rgba(65,8,51,.94)) !important;
10014:             color:#ffd4ef !important;
10015:             font:950 5.8px/1 Arial,sans-serif !important;
10016:             letter-spacing:.24px !important;
10017:             text-transform:uppercase !important;
10018:             white-space:nowrap !important;
10019:             box-shadow:0 0 10px rgba(255,56,172,.20) !important;
10020:             animation:mcms-special-event-pulse 2.4s ease-in-out infinite !important;
10021:         }
10022:         #${SCRIPT.criticalDrawerId} .mcms-critical-special-event > span { color:#fff2a6 !important; font-size:7px !important; }
10023:         #${SCRIPT.criticalDrawerId} .mcms-critical-row.mcms-critical-developer-event { border-top-color:rgba(255,82,184,.82) !important; }
10024:         @keyframes mcms-special-event-pulse {
10025:             0%,100% { filter:brightness(.96); box-shadow:0 0 7px rgba(255,56,172,.13); }
10026:             50% { filter:brightness(1.12); box-shadow:0 0 14px rgba(255,56,172,.30); }
```

### Lines 10063-10080

```text
10063:             height:auto !important;
10064:             min-height:max-content !important;
10065:             max-height:none !important;
10066:             contain:none !important;
10067:         }
10068:         #${SCRIPT.criticalDrawerId}.mcms-critical-expanded .mcms-critical-name,
10069:         #${SCRIPT.criticalDrawerId}.mcms-critical-expanded .mcms-critical-state-copy small {
10070:             overflow:visible !important;
10071:             white-space:normal !important;
10072:             text-overflow:clip !important;
10073:         }
10074:         #${SCRIPT.criticalDrawerId}.mcms-critical-expanded .mcms-critical-lowerline {
10075:             grid-template-columns:minmax(0,1fr) 126px !important;
10076:         }
10077:         html[data-mcms-mobile-active="true"] #${SCRIPT.criticalDrawerId} .mcms-critical-type-filters {
10078:             grid-template-columns:repeat(2,minmax(0,1fr)) !important;
10079:         }
10080:         html[data-mcms-mobile-active="true"] #${SCRIPT.criticalDrawerId} .mcms-critical-type-label { grid-column:1 / -1 !important; }
```

### Lines 10260-10307

```text
10260:             border-color:#d44349 !important;
10261:             background:#7e1119 !important;
10262:             color:#fff !important;
10263:         }
10264:         html[data-mcms-ui-theme="bond007"] #${SCRIPT.panelId} .mcms-reset-panel:hover {
10265:             border-color:#d5b85f !important;
10266:             color:#f0d47f !important;
10267:         }
10268:         html[data-mcms-ui-theme="bond007"] #${SCRIPT.panelId} .mcms-tabs {
10269:             gap:4px !important;
10270:             border-bottom:1px solid rgba(255,255,255,.055) !important;
10271:             padding-bottom:6px !important;
10272:         }
10273:         html[data-mcms-ui-theme="bond007"] #${SCRIPT.panelId} .mcms-tab-btn {
10274:             border:1px solid #44494f !important;
10275:             border-radius:1px !important;
10276:             background:linear-gradient(180deg,#282b30,#121417) !important;
10277:             color:#c8c9c7 !important;
10278:             letter-spacing:.35px !important;
10279:         }
10280:         html[data-mcms-ui-theme="bond007"] #${SCRIPT.panelId} .mcms-tab-btn:hover {
10281:             border-color:#a98e48 !important;
10282:             color:#f0d47e !important;
10283:         }
10284:         html[data-mcms-ui-theme="bond007"] #${SCRIPT.panelId} .mcms-tab-btn.mcms-active {
10285:             border-color:#e3c875 !important;
10286:             background:linear-gradient(180deg,#e9dfc5,#c8b98e) !important;
10287:             color:#111214 !important;
10288:             box-shadow:0 0 11px rgba(210,181,95,.18) !important;
10289:         }
10290:         html[data-mcms-ui-theme="bond007"] #${SCRIPT.panelId} .mcms-section-label {
10291:             position:relative !important;
10292:             padding:5px 7px 5px 21px !important;
10293:             border-left:2px solid #a71924 !important;
10294:             border-bottom:1px solid rgba(200,170,91,.28) !important;
10295:             background:linear-gradient(90deg,rgba(200,170,91,.09),transparent 72%) !important;
10296:             color:#e2c778 !important;
10297:             letter-spacing:1px !important;
10298:         }
10299:         html[data-mcms-ui-theme="bond007"] #${SCRIPT.panelId} .mcms-section-label::before {
10300:             content:"◉" !important;
10301:             position:absolute !important;
10302:             left:7px !important;
10303:             top:50% !important;
10304:             transform:translateY(-50%) !important;
10305:             color:#b61d27 !important;
10306:             font-size:8px !important;
10307:         }
```

### Lines 10805-10853

```text
10805:             position:relative !important;
10806:             z-index:3 !important;
10807:             min-width:0 !important;
10808:             max-width:100% !important;
10809:         }
10810:         #${SCRIPT.payoutFlashId} .mcms-payout-title {
10811:             width:100% !important;
10812:             max-width:100% !important;
10813:             white-space:normal !important;
10814:             overflow-wrap:anywhere !important;
10815:             word-break:normal !important;
10816:             text-wrap:balance !important;
10817:             hyphens:none !important;
10818:         }
10819:         #${SCRIPT.payoutFlashId} .mcms-payout-title.mcms-payout-title-long {
10820:             font-size:clamp(26px,4.15vw,49px) !important;
10821:             line-height:.94 !important;
10822:             letter-spacing:.45px !important;
10823:         }
10824:         #${SCRIPT.payoutFlashId} .mcms-payout-title.mcms-payout-title-very-long {
10825:             font-size:clamp(21px,3.35vw,39px) !important;
10826:             line-height:.97 !important;
10827:             letter-spacing:.2px !important;
10828:         }
10829:         #${SCRIPT.payoutFlashId} .mcms-payout-mission {
10830:             width:100% !important;
10831:             max-width:100% !important;
10832:             white-space:normal !important;
10833:             overflow:visible !important;
10834:             text-overflow:clip !important;
10835:             overflow-wrap:anywhere !important;
10836:             line-height:1.15 !important;
10837:             text-wrap:balance !important;
10838:         }
10839:         #${SCRIPT.payoutFlashId} .mcms-payout-source,
10840:         #${SCRIPT.payoutFlashId} .mcms-payout-kicker,
10841:         #${SCRIPT.payoutFlashId} .mcms-payout-amount,
10842:         #${SCRIPT.payoutFlashId} .mcms-payout-tier {
10843:             max-width:100% !important;
10844:             white-space:normal !important;
10845:             overflow-wrap:anywhere !important;
10846:             line-height:1.12 !important;
10847:         }
10848:         #${SCRIPT.payoutFlashId} .mcms-payout-amount {
10849:             width:100% !important;
10850:             text-align:center !important;
10851:         }
10852:         #${SCRIPT.payoutFlashId}.mcms-payout-fit-compact .mcms-payout-banner {
10853:             padding:20px 22px 18px !important;
```

### Lines 10914-10931

```text
10914:             #${SCRIPT.payoutFlashId} .mcms-payout-kicker {
10915:                 font-size:7px !important;
10916:                 letter-spacing:.75px !important;
10917:             }
10918:             #${SCRIPT.payoutFlashId} .mcms-payout-banner::before,
10919:             #${SCRIPT.payoutFlashId} .mcms-payout-banner::after {
10920:                 max-width:calc(100% - 24px) !important;
10921:                 overflow:hidden !important;
10922:                 text-overflow:ellipsis !important;
10923:                 white-space:nowrap !important;
10924:             }
10925:             #${SCRIPT.payoutFlashId}[data-template="jamesBond"] .mcms-payout-banner {
10926:                 background-size:82px auto,auto !important;
10927:                 background-position:right 10px top 15px,center !important;
10928:             }
10929:             #${SCRIPT.payoutFlashId}[data-template="jamesBond"] .mcms-payout-title {
10930:                 padding-inline:0 !important;
10931:                 padding-top:24px !important;
```

### Lines 11011-11027

```text
11011:             border:1px solid rgba(255,255,255,.18) !important;
11012:             border-radius:6px !important;
11013:             background:rgba(255,255,255,.055) !important;
11014:             color:#eaf4fb !important;
11015:             cursor:pointer !important;
11016:         }
11017:         #${SCRIPT.criticalDrawerId} .mcms-critical-category-filter span,
11018:         #${SCRIPT.criticalDrawerId} .mcms-critical-category-filter strong { font-weight:950 !important; }
11019:         #${SCRIPT.criticalDrawerId} .mcms-critical-category-filter span { overflow:hidden !important; font-size:7px !important; text-overflow:ellipsis !important; text-transform:uppercase !important; white-space:nowrap !important; }
11020:         #${SCRIPT.criticalDrawerId} .mcms-critical-category-filter strong { font-size:10px !important; }
11021:         #${SCRIPT.criticalDrawerId} .mcms-critical-category-filter i { position:absolute !important; top:2px !important; right:3px !important; font:900 4.6px/1 Arial,sans-serif !important; opacity:.5 !important; }
11022:         #${SCRIPT.criticalDrawerId} .mcms-critical-category-filter.mcms-filter-active { transform:translateY(-1px) !important; box-shadow:inset 0 0 0 2px currentColor,0 0 12px rgba(0,0,0,.32) !important; }
11023:         #${SCRIPT.criticalDrawerId} .mcms-critical-category-filter.mcms-filter-active i { padding:2px 3px !important; border-radius:3px !important; background:currentColor !important; color:#10151b !important; opacity:1 !important; }
11024:         #${SCRIPT.criticalDrawerId} .mcms-ownership-all { color:#dbe8f1 !important; border-color:rgba(219,232,241,.55) !important; }
11025:         #${SCRIPT.criticalDrawerId} .mcms-ownership-personal { color:#ffe084 !important; border-color:rgba(255,205,78,.72) !important; background:rgba(66,48,4,.42) !important; }
11026:         #${SCRIPT.criticalDrawerId} .mcms-ownership-alliance { color:#8ed1ff !important; border-color:rgba(79,174,255,.82) !important; background:rgba(4,38,68,.50) !important; }
11027:         #${SCRIPT.criticalDrawerId} .mcms-category-all { color:#dbe8f1 !important; }
```

### Lines 11035-11076

```text
11035:             grid-template-columns:auto repeat(3,minmax(50px,1fr)) !important;
11036:             grid-auto-rows:minmax(21px,auto) !important;
11037:         }
11038:         #${SCRIPT.criticalDrawerId} .mcms-critical-sort-button span {
11039:             display:block !important;
11040:             width:100% !important;
11041:             min-width:0 !important;
11042:             overflow:hidden !important;
11043:             text-overflow:ellipsis !important;
11044:             white-space:nowrap !important;
11045:             text-align:center !important;
11046:         }
11047:         #${SCRIPT.criticalDrawerId} .mcms-critical-origin-control {
11048:             grid-column:1 / 4 !important;
11049:             display:grid !important;
11050:             grid-template-columns:auto minmax(0,1fr) !important;
11051:             align-items:center !important;
11052:             gap:4px !important;
11053:             min-width:0 !important;
11054:             padding:2px 4px !important;
11055:             border:1px solid rgba(82,178,240,.42) !important;
11056:             border-radius:5px !important;
11057:             background:rgba(4,27,43,.62) !important;
11058:         }
11059:         #${SCRIPT.criticalDrawerId} .mcms-critical-origin-control span { color:#8fd4ff !important; font:950 5px/1 Arial,sans-serif !important; letter-spacing:.3px !important; }
11060:         #${SCRIPT.criticalDrawerId} .mcms-critical-origin-control select { min-width:0 !important; width:100% !important; height:19px !important; padding:0 3px !important; border:0 !important; background:#111820 !important; color:#eef8ff !important; font:850 6.6px/1 Arial,sans-serif !important; }
11061:         #${SCRIPT.criticalDrawerId} .mcms-critical-lock-origin { grid-column:4 / 5 !important; min-width:48px !important; padding:3px 5px !important; border:1px solid rgba(82,178,240,.55) !important; border-radius:5px !important; background:rgba(7,46,72,.74) !important; color:#a8ddff !important; font:950 5.8px/1 Arial,sans-serif !important; cursor:pointer !important; white-space:nowrap !important; }
11062: 
11063:         #${SCRIPT.criticalDrawerId} .mcms-critical-values { grid-template-columns:auto auto minmax(0,1fr) auto auto !important; }
11064:         #${SCRIPT.criticalDrawerId} .mcms-critical-value-mode { display:flex !important; gap:2px !important; }
11065:         #${SCRIPT.criticalDrawerId} .mcms-critical-value-mode button { min-width:38px !important; padding:3px 5px !important; border:1px solid rgba(255,255,255,.25) !important; border-radius:4px !important; background:rgba(255,255,255,.06) !important; color:#dceaf3 !important; font:950 5.8px/1 Arial,sans-serif !important; cursor:pointer !important; }
11066:         #${SCRIPT.criticalDrawerId} .mcms-critical-value-mode button.mcms-filter-active { border-color:#f0d47d !important; background:#f0d47d !important; color:#171717 !important; box-shadow:0 0 7px rgba(240,212,125,.35) !important; }
11067:         #${SCRIPT.criticalDrawerId} .mcms-critical-value-card small { display:block !important; margin-top:1px !important; font-size:4.8px !important; line-height:1 !important; opacity:.7 !important; }
11068:         #${SCRIPT.criticalDrawerId} .mcms-critical-showing { color:#b9cbd8 !important; font:900 5px/1 Arial,sans-serif !important; letter-spacing:.25px !important; white-space:nowrap !important; }
11069: 
11070:         #${SCRIPT.criticalDrawerId} .mcms-critical-summary { grid-template-columns:repeat(4,minmax(0,1fr)) !important; }
11071:         #${SCRIPT.criticalDrawerId} .mcms-summary-on-scene { border-color:rgba(61,209,126,.68) !important; color:#9ef0bd !important; }
11072:         #${SCRIPT.criticalDrawerId} .mcms-summary-my-units { border-color:rgba(232,214,154,.62) !important; color:#f3e4ad !important; }
11073:         #${SCRIPT.criticalDrawerId} .mcms-summary-syncing { border-color:rgba(151,176,194,.62) !important; color:#c9d8e2 !important; background:repeating-linear-gradient(135deg,rgba(95,116,132,.14) 0 7px,rgba(95,116,132,.04) 7px 14px) !important; }
11074:         #${SCRIPT.criticalDrawerId} .mcms-critical-summary-card small { display:block !important; margin-top:2px !important; font-size:5px !important; opacity:.76 !important; text-transform:uppercase !important; }
11075: 
11076:         #${SCRIPT.criticalDrawerId} .mcms-critical-category-badge,
```

### Lines 11080-11096

```text
11080:             align-items:center !important;
11081:             min-height:15px !important;
11082:             padding:2px 5px !important;
11083:             border:1px solid currentColor !important;
11084:             border-radius:999px !important;
11085:             font:950 5.7px/1 Arial,sans-serif !important;
11086:             letter-spacing:.22px !important;
11087:             text-transform:uppercase !important;
11088:             white-space:nowrap !important;
11089:         }
11090:         #${SCRIPT.criticalDrawerId} .mcms-critical-category-badge.mcms-category-standard { color:#bac8d2 !important; background:rgba(74,88,99,.42) !important; }
11091:         #${SCRIPT.criticalDrawerId} .mcms-critical-category-badge.mcms-category-event { color:#e5b5ff !important; background:rgba(76,25,104,.64) !important; }
11092:         #${SCRIPT.criticalDrawerId} .mcms-critical-category-badge.mcms-category-special { color:#ff9fe8 !important; background:rgba(110,12,83,.72) !important; }
11093:         #${SCRIPT.criticalDrawerId} .mcms-critical-eligibility.mcms-eligible { color:#93efb4 !important; background:rgba(5,89,43,.72) !important; }
11094:         #${SCRIPT.criticalDrawerId} .mcms-critical-eligibility.mcms-not-eligible { color:#ffd47b !important; background:rgba(91,57,2,.74) !important; }
11095:         #${SCRIPT.criticalDrawerId} .mcms-critical-data-badge.mcms-data-sync { color:#d8e6ee !important; background:rgba(68,88,102,.82) !important; animation:mcmsCriticalSyncPulse 1.4s ease-in-out infinite !important; }
11096:         #${SCRIPT.criticalDrawerId} .mcms-critical-data-badge.mcms-data-unknown { color:#d5dce1 !important; background:rgba(63,68,73,.72) !important; }
```

### Lines 11179-11196

```text
11179:         #${SCRIPT.criticalDrawerId} .mcms-critical-view-trigger strong {
11180:             grid-area:summary !important;
11181:             display:block !important;
11182:             min-width:0 !important;
11183:             overflow:hidden !important;
11184:             color:#f4f8fb !important;
11185:             font:950 7.5px/1.1 Arial,sans-serif !important;
11186:             letter-spacing:.18px !important;
11187:             text-overflow:ellipsis !important;
11188:             white-space:nowrap !important;
11189:         }
11190:         #${SCRIPT.criticalDrawerId} .mcms-critical-view-chevron {
11191:             grid-area:chevron !important;
11192:             display:grid !important;
11193:             place-items:center !important;
11194:             width:23px !important;
11195:             height:23px !important;
11196:             border:1px solid rgba(143,212,255,.46) !important;
```

### Lines 11367-11434

```text
11367:                 repeating-linear-gradient(90deg,rgba(216,25,63,.025) 0 1px,transparent 1px 16px),
11368:                 linear-gradient(180deg,#262a31,#14171d) !important;
11369:         }
11370:         html[data-mcms-ui-theme="umbrella"] #${SCRIPT.panelId} .mcms-header::before {
11371:             left:138px !important;
11372:             right:auto !important;
11373:             max-width:calc(100% - 246px) !important;
11374:             overflow:hidden !important;
11375:             text-overflow:ellipsis !important;
11376:             white-space:nowrap !important;
11377:         }
11378: 
11379:         html[data-mcms-ui-theme="umbrella"] #${SCRIPT.panelId} .mcms-section-label {
11380:             position:relative !important;
11381:             padding-right:29px !important;
11382:             overflow:hidden !important;
11383:         }
11384:         html[data-mcms-ui-theme="umbrella"] #${SCRIPT.panelId} .mcms-section-label::after {
11385:             content:"" !important;
11386:             position:absolute !important;
11387:             right:6px !important;
11388:             top:50% !important;
11389:             width:19px !important;
11390:             height:19px !important;
11391:             transform:translateY(-50%) !important;
11392:             background:url("${THEME_ASSETS.umbrellaContainmentBadge}") center/contain no-repeat !important;
11393:             opacity:.72 !important;
11394:             pointer-events:none !important;
11395:             filter:drop-shadow(0 0 4px rgba(216,25,63,.28)) !important;
11396:         }
11397: 
11398:         html[data-mcms-ui-theme="umbrella"] #${SCRIPT.panelId} .mcms-tab-panel[data-panel="resources"],
11399:         html[data-mcms-ui-theme="umbrella"] #${SCRIPT.panelId} .mcms-tab-panel[data-panel="ops"] {
11400:             position:relative !important;
11401:             isolation:isolate !important;
11402:         }
11403:         html[data-mcms-ui-theme="umbrella"] #${SCRIPT.panelId} .mcms-tab-panel[data-panel="resources"]::after,
11404:         html[data-mcms-ui-theme="umbrella"] #${SCRIPT.panelId} .mcms-tab-panel[data-panel="ops"]::after {
11405:             content:"" !important;
11406:             position:absolute !important;
11407:             right:-7px !important;
11408:             bottom:8px !important;
11409:             width:118px !important;
11410:             height:190px !important;
11411:             background:url("${THEME_ASSETS.umbrellaSpecimenVial}") center bottom/contain no-repeat !important;
11412:             opacity:.075 !important;
11413:             pointer-events:none !important;
11414:             z-index:0 !important;
11415:             filter:grayscale(.12) drop-shadow(0 8px 10px rgba(0,0,0,.35)) !important;
11416:         }
11417:         html[data-mcms-ui-theme="umbrella"] #${SCRIPT.panelId} .mcms-tab-panel[data-panel="ops"]::after {
11418:             right:4px !important;
11419:             bottom:12px !important;
11420:             width:178px !important;
11421:             height:110px !important;
11422:             background-image:url("${THEME_ASSETS.umbrellaSurveillanceTerminal}") !important;
11423:             opacity:.065 !important;
11424:         }
11425:         html[data-mcms-ui-theme="umbrella"] #${SCRIPT.panelId} .mcms-tab-panel[data-panel="resources"] > *,
11426:         html[data-mcms-ui-theme="umbrella"] #${SCRIPT.panelId} .mcms-tab-panel[data-panel="ops"] > * {
11427:             position:relative !important;
11428:             z-index:1 !important;
11429:         }
11430: 
11431:         html[data-mcms-ui-theme="umbrella"] #${SCRIPT.criticalDrawerId} .mcms-drawer-head,
11432:         html[data-mcms-ui-theme="umbrella"] #${SCRIPT.vehicleStatusId} .mcms-vcs-head {
11433:             position:relative !important;
11434:             overflow:hidden !important;
```

### Lines 11547-11564

```text
11547:         }
11548:         #${SCRIPT.payoutFlashId}[data-template="biohazard"] .mcms-payout-banner::before {
11549:             content:"UMBRELLA CONTAINMENT // BSL-4 SECURE NODE" !important;
11550:             left:24px !important;
11551:             right:24px !important;
11552:             top:11px !important;
11553:             max-width:calc(100% - 48px) !important;
11554:             overflow:hidden !important;
11555:             text-overflow:ellipsis !important;
11556:             white-space:nowrap !important;
11557:             color:rgba(255,123,142,.78) !important;
11558:             font:950 7px/1 Consolas,monospace !important;
11559:             letter-spacing:1.15px !important;
11560:             text-align:center !important;
11561:             z-index:2 !important;
11562:         }
11563:         #${SCRIPT.payoutFlashId}[data-template="biohazard"] .mcms-payout-banner::after {
11564:             content:"" !important;
```

### Lines 11658-11675

```text
11658: 
11659:         @media (max-width:760px) {
11660:             html[data-mcms-ui-theme="umbrella"] #${SCRIPT.panelId} .mcms-header {
11661:                 background:
11662:                     repeating-linear-gradient(90deg,rgba(216,25,63,.025) 0 1px,transparent 1px 16px),
11663:                     linear-gradient(180deg,#262a31,#14171d) !important;
11664:             }
11665:             html[data-mcms-ui-theme="umbrella"] #${SCRIPT.panelId} .mcms-header::before { display:none !important; }
11666:             html[data-mcms-ui-theme="umbrella"] #${SCRIPT.panelId} .mcms-tab-panel[data-panel="resources"]::after,
11667:             html[data-mcms-ui-theme="umbrella"] #${SCRIPT.panelId} .mcms-tab-panel[data-panel="ops"]::after { opacity:.045 !important; }
11668:             #${SCRIPT.payoutFlashId}[data-template="biohazard"] .mcms-payout-banner { padding:30px 18px 21px !important; }
11669:             #${SCRIPT.payoutFlashId}[data-template="biohazard"] .mcms-payout-title { padding-inline:0 !important; font-size:clamp(24px,7.4vw,40px) !important; letter-spacing:.65px !important; }
11670:             #${SCRIPT.payoutFlashId}[data-template="biohazard"] .mcms-payout-title.mcms-payout-title-long { font-size:clamp(21px,6.5vw,34px) !important; }
11671:             #${SCRIPT.payoutFlashId}[data-template="biohazard"] .mcms-payout-title.mcms-payout-title-very-long { font-size:clamp(18px,5.6vw,29px) !important; }
11672:             #${SCRIPT.payoutFlashId}[data-template="biohazard"] .mcms-payout-mission { font-size:clamp(10px,3.3vw,14px) !important; }
11673:             #${SCRIPT.payoutFlashId}[data-template="biohazard"] .mcms-payout-kicker { font-size:7px !important; letter-spacing:1px !important; }
11674:             #${SCRIPT.payoutFlashId}[data-template="biohazard"] .mcms-payout-banner::after { opacity:.06 !important; background-size:88px auto,62px auto !important; }
11675:             #${SCRIPT.payoutFlashId}[data-template="biohazard"] .mcms-payout-banner::before { left:16px !important; right:16px !important; max-width:calc(100% - 32px) !important; font-size:6px !important; letter-spacing:.65px !important; }
```

### Lines 11745-11778

```text
11745:         }
11746:         #${SCRIPT.helpCenterId} .mcms-help-brand { min-width:0 !important; display:flex !important; align-items:center !important; gap:10px !important; }
11747:         #${SCRIPT.helpCenterId} .mcms-help-brand-icon {
11748:             width:36px !important; height:36px !important; flex:0 0 36px !important; display:grid !important; place-items:center !important;
11749:             border:1px solid #4aa7cf !important; border-radius:11px !important; background:#0b2c3d !important; color:#bfeeff !important;
11750:             font-size:20px !important; font-weight:1000 !important; box-shadow:0 0 14px rgba(79,195,247,.14) !important;
11751:         }
11752:         #${SCRIPT.helpCenterId} .mcms-help-brand-copy { min-width:0 !important; }
11753:         #${SCRIPT.helpCenterId} .mcms-help-brand-copy strong { display:block !important; overflow:hidden !important; text-overflow:ellipsis !important; white-space:nowrap !important; font-size:13px !important; font-weight:950 !important; }
11754:         #${SCRIPT.helpCenterId} .mcms-help-brand-copy small { display:block !important; margin-top:2px !important; color:#8eabb9 !important; font-size:9px !important; font-weight:750 !important; }
11755:         #${SCRIPT.helpCenterId} .mcms-help-actions { display:flex !important; gap:6px !important; }
11756:         #${SCRIPT.helpCenterId} .mcms-help-action {
11757:             min-width:38px !important; height:38px !important; padding:0 10px !important; border:1px solid #31596d !important; border-radius:10px !important;
11758:             background:#0c202b !important; color:#dff5ff !important; cursor:pointer !important; font-size:12px !important; font-weight:900 !important;
11759:         }
11760:         #${SCRIPT.helpCenterId} .mcms-help-action:hover,
11761:         #${SCRIPT.helpCenterId} .mcms-help-action:focus-visible { border-color:#62cfff !important; background:#15435a !important; outline:none !important; }
11762:         #${SCRIPT.helpCenterId} .mcms-help-close { font-size:20px !important; }
11763:         #${SCRIPT.helpCenterId} .mcms-help-address {
11764:             min-height:35px !important; display:grid !important; grid-template-columns:auto minmax(0,1fr) auto !important; gap:8px !important; align-items:center !important;
11765:             padding:5px 12px !important; border-bottom:1px solid rgba(67,121,146,.22) !important; background:#07131b !important;
11766:             color:#88a9b9 !important; font-size:9px !important;
11767:         }
11768:         #${SCRIPT.helpCenterId} .mcms-help-address-lock { color:#69d99b !important; }
11769:         #${SCRIPT.helpCenterId} .mcms-help-address-text { overflow:hidden !important; text-overflow:ellipsis !important; white-space:nowrap !important; }
11770:         #${SCRIPT.helpCenterId} .mcms-help-status { color:#b8d7e6 !important; font-weight:850 !important; white-space:nowrap !important; }
11771:         #${SCRIPT.helpCenterId} .mcms-help-progress { height:2px !important; background:transparent !important; overflow:hidden !important; }
11772:         #${SCRIPT.helpCenterId}.mcms-loading .mcms-help-progress::before {
11773:             content:'' !important; display:block !important; width:34% !important; height:100% !important; background:linear-gradient(90deg,transparent,#4fc3f7,#a8e7ff,transparent) !important;
11774:             animation:mcmsHelpProgress 1.05s ease-in-out infinite !important;
11775:         }
11776:         @keyframes mcmsHelpProgress { from { transform:translateX(-120%) } to { transform:translateX(400%) } }
11777:         #${SCRIPT.helpCenterId} .mcms-help-content { position:relative !important; flex:1 1 auto !important; min-height:0 !important; background:#071018 !important; }
11778:         #${SCRIPT.helpCenterId} .mcms-help-frame { width:100% !important; height:100% !important; display:block !important; border:0 !important; background:#071018 !important; }
```

### Lines 11832-11848

```text
11832:         html[data-mcms-tablet-active="true"] #${SCRIPT.panelId} .mcms-panel-sticky-stack .mcms-header {
11833:             position:relative !important;
11834:             top:auto !important;
11835:             z-index:2 !important;
11836:             margin:0 -12px !important;
11837:             padding:10px 12px 9px !important;
11838:             border-bottom:1px solid rgba(255,255,255,.12) !important;
11839:         }
11840:         html[data-mcms-tablet-active="true"] #${SCRIPT.panelId} .mcms-panel-sticky-stack .mcms-tabs {
11841:             position:relative !important;
11842:             top:auto !important;
11843:             z-index:1 !important;
11844:             margin:0 -4px !important;
11845:             padding:8px 4px 10px !important;
11846:         }
11847: 
11848: 
```

### Lines 11977-11993

```text
11977:             animation:none !important; transition:none !important; filter:none !important;
11978:             backdrop-filter:none !important; -webkit-backdrop-filter:none !important;
11979:             box-shadow:none !important; text-shadow:none !important; will-change:auto !important;
11980:         }
11981:         html[data-mcms-economy="true"] #${SCRIPT.controlId} .mcms-economy-btn,
11982:         html[data-mcms-economy="true"] #${SCRIPT.controlId} .mcms-shell {
11983:             background-image:none !important; backdrop-filter:none !important; -webkit-backdrop-filter:none !important;
11984:         }
11985:         html[data-mcms-economy="true"] #${SCRIPT.panelId} .mcms-tab-panel.mcms-active,
11986:         html[data-mcms-economy="true"] #${SCRIPT.panelId} .mcms-section,
11987:         html[data-mcms-economy="true"] #${SCRIPT.vehicleStatusId} .mcms-vehicle-status-body {
11988:             contain:layout paint style !important;
11989:         }
11990:         html[data-mcms-economy="true"] .leaflet-container *,
11991:         html[data-mcms-economy="true"] #mission_list *,
11992:         html[data-mcms-economy="true"] #radio_messages *,
11993:         html[data-mcms-economy="true"] #radio_messages_important * {
```

### Lines 12025-12041

```text
12025: 
12026:         /* v4.8.0 full quality audit: sizing, readability, responsive flow and focus integrity. */
12027:         #${SCRIPT.controlId} *, #${SCRIPT.panelId} *, #${SCRIPT.criticalDrawerId} *, #${SCRIPT.vehicleStatusId} *,
12028:         #${SCRIPT.majorIncidentFeedId} *, #${SCRIPT.missionInspectorId} *, #${SCRIPT.helpCenterId} * { box-sizing:border-box !important; }
12029:         #${SCRIPT.panelId} :is(.mcms-grid-2,.mcms-row,.mcms-ui-theme-grid,.mcms-profile-row,.mcms-bookmark-row,.mcms-quick-row,.mcms-finance-vault-summary) > *,
12030:         #${SCRIPT.criticalDrawerId} :is(.mcms-critical-values-grid,.mcms-critical-type-filters,.mcms-critical-category-filters,.mcms-critical-summary,.mcms-critical-unit-grid) > * { min-width:0 !important; max-width:100% !important; }
12031:         #${SCRIPT.panelId} :is(.mcms-status,.mcms-footer,.mcms-subtitle,.mcms-row-label,.mcms-profile-main,.mcms-bookmark-name,.mcms-ui-theme-copy,.mcms-text),
12032:         #${SCRIPT.criticalDrawerId} :is(.mcms-critical-state-copy,.mcms-critical-location,.mcms-critical-meta,.mcms-critical-list-footer),
12033:         #${SCRIPT.vehicleStatusId} :is(.mcms-vehicle-status-title,.mcms-vehicle-status-body) { overflow-wrap:anywhere !important; word-break:normal !important; }
12034:         #${SCRIPT.panelId}, #${SCRIPT.criticalDrawerId}, #${SCRIPT.vehicleStatusId}, #${SCRIPT.helpCenterId} { overscroll-behavior:contain !important; scrollbar-gutter:stable both-edges; }
12035:         #${SCRIPT.controlId} :is(button,[tabindex]), #${SCRIPT.panelId} :is(button,input,select,[tabindex]),
12036:         #${SCRIPT.criticalDrawerId} :is(button,input,select,[tabindex]), #${SCRIPT.vehicleStatusId} :is(button,input,select,[tabindex]),
12037:         #${SCRIPT.helpCenterId} :is(button,input,select,a,[tabindex]) { outline:none !important; }
12038:         #${SCRIPT.controlId} :is(button,[tabindex]):focus-visible, #${SCRIPT.panelId} :is(button,input,select,[tabindex]):focus-visible,
12039:         #${SCRIPT.criticalDrawerId} :is(button,input,select,[tabindex]):focus-visible, #${SCRIPT.vehicleStatusId} :is(button,input,select,[tabindex]):focus-visible,
12040:         #${SCRIPT.helpCenterId} :is(button,input,select,a,[tabindex]):focus-visible { outline:3px solid #8cddff !important; outline-offset:2px !important; }
12041:         #${SCRIPT.panelId} :is(button,input,select):disabled, #${SCRIPT.criticalDrawerId} :is(button,input,select):disabled,
```

### Lines 12043-12106

```text
12043: 
12044:         html:not([data-mcms-tablet-active="true"]):not([data-mcms-mobile-active="true"]) #${SCRIPT.panelId} {
12045:             width:min(360px,calc(100vw - 24px)) !important; max-width:calc(100vw - 24px) !important;
12046:         }
12047:         html:not([data-mcms-tablet-active="true"]):not([data-mcms-mobile-active="true"]) #${SCRIPT.panelId} .mcms-header {
12048:             grid-template-columns:minmax(0,1fr) 32px 32px 32px !important; gap:6px !important; min-height:48px !important;
12049:         }
12050:         html:not([data-mcms-tablet-active="true"]):not([data-mcms-mobile-active="true"]) #${SCRIPT.panelId} :is(.mcms-reset-panel,.mcms-help-button,.mcms-close) { width:32px !important; height:32px !important; min-width:32px !important; }
12051:         #${SCRIPT.panelId} .mcms-title { min-width:0 !important; white-space:normal !important; font-size:11px !important; line-height:1.15 !important; }
12052:         #${SCRIPT.panelId} .mcms-subtitle { white-space:normal !important; font-size:9px !important; line-height:1.25 !important; }
12053:         #${SCRIPT.panelId} .mcms-tabs { min-width:0 !important; }
12054:         #${SCRIPT.panelId} .mcms-tab-btn { min-width:0 !important; overflow:hidden !important; text-overflow:ellipsis !important; font-size:9px !important; }
12055:         #${SCRIPT.panelId} .mcms-tab-panel[hidden] { display:none !important; }
12056:         #${SCRIPT.panelId} .mcms-section-label { font-size:9.5px !important; line-height:1.25 !important; }
12057:         #${SCRIPT.panelId} .mcms-status { font-size:9.5px !important; line-height:1.42 !important; }
12058:         #${SCRIPT.panelId} .mcms-row-label { font-size:10px !important; line-height:1.3 !important; }
12059:         #${SCRIPT.panelId} :is(.mcms-label,.mcms-bookmark-name,.mcms-profile-main strong,.mcms-ui-theme-copy strong) { font-size:10.5px !important; line-height:1.2 !important; }
12060:         #${SCRIPT.panelId} :is(.mcms-pill,.mcms-heat-key,.mcms-ui-theme-copy small,.mcms-profile-main span,.mcms-build) { font-size:8.5px !important; line-height:1.25 !important; }
12061:         #${SCRIPT.panelId} :is(.mcms-input,.mcms-select,.mcms-small-btn,.mcms-position-btn,.mcms-bookmark-btn,.mcms-pin-btn) { min-height:32px !important; }
12062:         #${SCRIPT.panelId} .mcms-footer { gap:4px !important; font-size:9px !important; line-height:1.35 !important; }
12063:         #${SCRIPT.panelId} .mcms-discord-wide { grid-template-columns:minmax(96px,35%) minmax(0,1fr) !important; }
12064:         #${SCRIPT.panelId} .mcms-finance-vault-summary { grid-template-columns:repeat(2,minmax(0,1fr)) !important; gap:7px !important; }
12065: 
12066:         html:not([data-mcms-mobile-active="true"]) #${SCRIPT.criticalDrawerId} { width:min(480px,calc(100vw - 28px)) !important; max-width:calc(100vw - 28px) !important; }
12067:         #${SCRIPT.criticalDrawerId} .mcms-critical-values-grid { grid-template-columns:repeat(3,minmax(0,1fr)) !important; gap:6px !important; }
12068:         #${SCRIPT.criticalDrawerId} .mcms-critical-category-filters { grid-template-columns:repeat(2,minmax(0,1fr)) !important; gap:6px !important; }
12069:         #${SCRIPT.criticalDrawerId} .mcms-critical-summary { grid-template-columns:repeat(2,minmax(0,1fr)) !important; gap:6px !important; }
12070:         #${SCRIPT.criticalDrawerId} :is(.mcms-critical-values-label,.mcms-critical-type-label,.mcms-critical-category-label,.mcms-critical-sort-label,.mcms-critical-age-label) { font-size:8.5px !important; line-height:1.25 !important; white-space:normal !important; }
12071:         #${SCRIPT.criticalDrawerId} :is(.mcms-critical-value-card,.mcms-critical-type-filter,.mcms-critical-category-filter,.mcms-critical-summary-card) { min-width:0 !important; overflow:hidden !important; }
12072:         #${SCRIPT.criticalDrawerId} .mcms-critical-value-card strong { font-size:11px !important; line-height:1.1 !important; }
12073:         #${SCRIPT.criticalDrawerId} :is(.mcms-critical-value-mode,.mcms-critical-unit-extra,.mcms-critical-refreshed,.mcms-critical-showing) { font-size:8px !important; line-height:1.3 !important; }
12074:         #${SCRIPT.criticalDrawerId} :is(.mcms-critical-category-filter,.mcms-critical-type-filter) span {
12075:             min-width:0 !important; overflow:visible !important; text-overflow:clip !important; white-space:normal !important;
12076:             font-size:8.5px !important; line-height:1.1 !important;
12077:         }
12078:         #${SCRIPT.criticalDrawerId} :is(.mcms-critical-category-filter,.mcms-critical-type-filter) strong { font-size:11px !important; }
12079:         #${SCRIPT.criticalDrawerId} :is(.mcms-critical-category-filter,.mcms-critical-type-filter) i { font-size:5.5px !important; line-height:1 !important; }
12080:         #${SCRIPT.criticalDrawerId} .mcms-critical-category-filter { min-height:34px !important; padding:6px 8px !important; }
12081:         #${SCRIPT.criticalDrawerId} .mcms-critical-type-filter { min-height:34px !important; }
12082:         #${SCRIPT.criticalDrawerId} .mcms-critical-name { white-space:normal !important; overflow:hidden !important; display:-webkit-box !important; -webkit-line-clamp:2 !important; -webkit-box-orient:vertical !important; line-height:1.2 !important; }
12083:         #${SCRIPT.criticalDrawerId} .mcms-critical-state-copy { min-width:0 !important; white-space:normal !important; }
12084:         #${SCRIPT.criticalDrawerId} .mcms-critical-card { contain:layout style !important; }
12085:         #${SCRIPT.vehicleStatusId} .mcms-vehicle-status-title { font-size:12px !important; line-height:1.2 !important; }
12086:         #${SCRIPT.vehicleStatusId} .mcms-vehicle-status-body { font-size:10px !important; line-height:1.35 !important; }
12087:         #${SCRIPT.majorIncidentFeedId} :is(.mcms-major-feed-track,.mcms-major-feed-item,.mcms-major-feed-copy) { min-width:0 !important; }
12088:         #${SCRIPT.majorIncidentFeedId} .mcms-major-feed-copy { overflow:hidden !important; text-overflow:ellipsis !important; white-space:nowrap !important; }
12089: 
12090:         html[data-mcms-tablet-active="true"] #${SCRIPT.panelId} :is(.mcms-pill,.mcms-heat-key,.mcms-ui-theme-copy small,.mcms-profile-main span,.mcms-build) { font-size:9.5px !important; }
12091:         html[data-mcms-tablet-active="true"] #${SCRIPT.panelId} :is(.mcms-status,.mcms-row-label) { font-size:11px !important; }
12092:         html[data-mcms-tablet-active="true"] #${SCRIPT.criticalDrawerId} :is(.mcms-critical-values-label,.mcms-critical-type-label,.mcms-critical-category-label,.mcms-critical-value-mode,.mcms-critical-unit-extra) { font-size:8.5px !important; }
12093: 
12094:         html[data-mcms-mobile-active="true"] #${SCRIPT.panelId} .mcms-tabs {
12095:             top:40px !important; display:grid !important; grid-template-columns:repeat(4,minmax(0,1fr)) !important;
12096:             gap:5px !important; overflow:visible !important; padding:3px 2px 7px !important;
12097:         }
12098:         html[data-mcms-mobile-active="true"] #${SCRIPT.panelId} .mcms-tab-btn { width:100% !important; min-width:0 !important; height:38px !important; padding:0 4px !important; font-size:9.5px !important; }
12099:         html[data-mcms-mobile-active="true"] #${SCRIPT.panelId} .mcms-panel-sticky-stack { position:sticky !important; top:-8px !important; z-index:9 !important; background:rgba(6,10,15,.985) !important; }
12100:         html[data-mcms-mobile-active="true"] #${SCRIPT.panelId} .mcms-header { position:relative !important; top:auto !important; margin:-8px -8px 5px !important; }
12101:         html[data-mcms-mobile-active="true"] #${SCRIPT.panelId} :is(.mcms-pill,.mcms-heat-key,.mcms-ui-theme-copy small,.mcms-profile-main span,.mcms-build) { font-size:9px !important; }
12102:         html[data-mcms-mobile-active="true"] #${SCRIPT.panelId} :is(.mcms-status,.mcms-row-label) { font-size:10px !important; }
12103:         html[data-mcms-mobile-active="true"] #${SCRIPT.panelId} .mcms-grid-2 { align-items:stretch !important; }
12104:         html[data-mcms-mobile-active="true"] #${SCRIPT.panelId} .mcms-theme-btn,
12105:         html[data-mcms-mobile-active="true"] #${SCRIPT.panelId} .mcms-toggle-btn,
12106:         html[data-mcms-mobile-active="true"] #${SCRIPT.panelId} .mcms-ui-theme-btn { min-width:0 !important; overflow:hidden !important; }
```

### Lines 12110-12146

```text
12110:         }
12111:         html[data-mcms-mobile-active="true"] #${SCRIPT.toastId}.mcms-flash { transform:translateY(0) !important; }
12112:         html[data-mcms-mobile-active="true"] #${SCRIPT.criticalDrawerId} .mcms-critical-values-grid,
12113:         html[data-mcms-mobile-active="true"] #${SCRIPT.criticalDrawerId} .mcms-critical-category-filters,
12114:         html[data-mcms-mobile-active="true"] #${SCRIPT.criticalDrawerId} .mcms-critical-summary { grid-template-columns:repeat(2,minmax(0,1fr)) !important; }
12115:         html[data-mcms-mobile-active="true"] #${SCRIPT.criticalDrawerId} :is(.mcms-critical-values-label,.mcms-critical-type-label,.mcms-critical-category-label,.mcms-critical-value-mode,.mcms-critical-unit-extra,.mcms-critical-refreshed,.mcms-critical-showing) { font-size:8.5px !important; }
12116:         html[data-mcms-mobile-active="true"] #${SCRIPT.criticalDrawerId} :is(button,.mcms-critical-filter,.mcms-critical-type-filter,.mcms-critical-category-filter,.mcms-critical-summary-card) { min-height:38px !important; }
12117:         @media (max-width:380px) {
12118:             html[data-mcms-mobile-active="true"] #${SCRIPT.panelId} .mcms-tabs { grid-template-columns:repeat(2,minmax(0,1fr)) !important; }
12119:             html[data-mcms-mobile-active="true"] #${SCRIPT.criticalDrawerId} .mcms-critical-values-grid,
12120:             html[data-mcms-mobile-active="true"] #${SCRIPT.criticalDrawerId} .mcms-critical-category-filters,
12121:             html[data-mcms-mobile-active="true"] #${SCRIPT.criticalDrawerId} .mcms-critical-summary { grid-template-columns:1fr !important; }
12122:         }
12123:         html[data-mcms-ui-theme] #${SCRIPT.panelId} .mcms-panel-sticky-stack,
12124:         html[data-mcms-ui-theme] #${SCRIPT.panelId} .mcms-tab-panel { width:100% !important; max-width:100% !important; overflow-x:hidden !important; }
12125:         html[data-mcms-ui-theme] #${SCRIPT.panelId} :is(.mcms-help-button,.mcms-close,.mcms-reset-panel) {
12126:             display:grid !important; place-items:center !important; line-height:1 !important; padding:0 !important;
12127:         }
12128:         html[data-mcms-ui-theme] #${SCRIPT.panelId} .mcms-section-label { font-size:9.5px !important; line-height:1.25 !important; }
12129:         html[data-mcms-ui-theme] #${SCRIPT.panelId} .mcms-ops-stat-label { font-size:9px !important; line-height:1.2 !important; }
12130:         html[data-mcms-ui-theme] #${SCRIPT.panelId} .mcms-sweep-state { font-size:8.5px !important; line-height:1.1 !important; }
12131:         html[data-mcms-ui-theme] #${SCRIPT.panelId} .mcms-sweep-log,
12132:         html[data-mcms-ui-theme] #${SCRIPT.panelId} .mcms-empty-state { font-size:9px !important; line-height:1.35 !important; }
12133:         html[data-mcms-ui-theme] #${SCRIPT.panelId} .mcms-alliance-text { font-size:9px !important; }
12134:         html[data-mcms-ui-theme] #${SCRIPT.panelId} .mcms-finance-vault-summary span { font-size:9px !important; line-height:1.2 !important; }
12135:         html[data-mcms-ui-theme] #${SCRIPT.panelId} .mcms-finance-vault-summary b { font-size:10px !important; line-height:1.2 !important; white-space:normal !important; }
12136:         html[data-mcms-ui-theme] #${SCRIPT.panelId} .mcms-finance-vault-summary small { font-size:9px !important; line-height:1.4 !important; }
12137:         html[data-mcms-tablet-active="true"][data-mcms-ui-theme] #${SCRIPT.panelId} .mcms-section-label,
12138:         html[data-mcms-mobile-active="true"][data-mcms-ui-theme] #${SCRIPT.panelId} .mcms-section-label { font-size:10px !important; }
12139:         html[data-mcms-tablet-active="true"][data-mcms-ui-theme] #${SCRIPT.panelId} :is(.mcms-ops-stat-label,.mcms-sweep-state,.mcms-alliance-text),
12140:         html[data-mcms-mobile-active="true"][data-mcms-ui-theme] #${SCRIPT.panelId} :is(.mcms-ops-stat-label,.mcms-sweep-state,.mcms-alliance-text) { font-size:9.5px !important; }
12141:         html[data-mcms-mobile-active="true"] #${SCRIPT.toastId} { top:calc(max(10px,env(safe-area-inset-top)) + 58px) !important; }
12142: 
12143: 
12144:         /* v4.8.1: preserve MissionChief's native interaction layer above Toolkit drawers.
12145:            Bootstrap dropdowns can be trapped inside the navbar stacking context even
12146:            when their own z-index is high. Elevating the native navigation context and
```

### Lines 12211-12233

```text
12211:             letter-spacing:.42px !important;
12212:             text-transform:uppercase !important;
12213:         }
12214:         #${SCRIPT.criticalDrawerId} .mcms-critical-filter-overview-copy strong {
12215:             min-width:0 !important;
12216:             overflow:hidden !important;
12217:             color:#f0f8fc !important;
12218:             font:900 7.4px/1.15 Arial,sans-serif !important;
12219:             text-overflow:ellipsis !important;
12220:             white-space:nowrap !important;
12221:         }
12222:         #${SCRIPT.criticalDrawerId} .mcms-critical-filter-overview-count {
12223:             color:#b9cbd6 !important;
12224:             font:900 6.1px/1 Arial,sans-serif !important;
12225:             white-space:nowrap !important;
12226:         }
12227:         #${SCRIPT.criticalDrawerId} .mcms-critical-filter-overview button {
12228:             min-height:23px !important;
12229:             padding:3px 8px !important;
12230:             border:1px solid rgba(255,111,111,.62) !important;
12231:             border-radius:5px !important;
12232:             background:rgba(89,18,23,.78) !important;
12233:             color:#ffd5d5 !important;
```

### Lines 12272-12290

```text
12272:             background:rgba(255,255,255,.055) !important;
12273:             color:#e8f2f8 !important;
12274:             cursor:pointer !important;
12275:         }
12276:         #${SCRIPT.criticalDrawerId} .mcms-critical-quick-view span {
12277:             min-width:0 !important;
12278:             overflow:hidden !important;
12279:             font:950 6.4px/1.08 Arial,sans-serif !important;
12280:             text-overflow:ellipsis !important;
12281:             text-transform:uppercase !important;
12282:             white-space:nowrap !important;
12283:         }
12284:         #${SCRIPT.criticalDrawerId} .mcms-critical-quick-view strong { font:950 9px/1 Arial,sans-serif !important; }
12285:         #${SCRIPT.criticalDrawerId} .mcms-critical-quick-view i {
12286:             position:absolute !important;
12287:             top:2px !important;
12288:             right:3px !important;
12289:             color:currentColor !important;
12290:             font:950 6px/1 Arial,sans-serif !important;
```

### Lines 12334-12351

```text
12334:         }
12335:         #${SCRIPT.criticalDrawerId} .mcms-critical-advanced-toggle > span { display:grid !important; min-width:0 !important; gap:2px !important; }
12336:         #${SCRIPT.criticalDrawerId} .mcms-critical-advanced-toggle strong { font:950 6.5px/1 Arial,sans-serif !important; letter-spacing:.35px !important; }
12337:         #${SCRIPT.criticalDrawerId} .mcms-critical-advanced-toggle small {
12338:             min-width:0 !important;
12339:             overflow:hidden !important;
12340:             color:#91a5b1 !important;
12341:             font:850 5.7px/1.1 Arial,sans-serif !important;
12342:             text-overflow:ellipsis !important;
12343:             white-space:nowrap !important;
12344:         }
12345:         #${SCRIPT.criticalDrawerId} .mcms-critical-advanced-toggle i { font:950 12px/1 Arial,sans-serif !important; transition:transform 140ms ease !important; }
12346:         #${SCRIPT.criticalDrawerId} .mcms-critical-advanced-shell.mcms-open .mcms-critical-advanced-toggle {
12347:             border-color:rgba(87,190,244,.66) !important;
12348:             background:rgba(8,48,70,.68) !important;
12349:         }
12350:         #${SCRIPT.criticalDrawerId} .mcms-critical-advanced-shell.mcms-open .mcms-critical-advanced-toggle i { transform:rotate(180deg) !important; }
12351:         #${SCRIPT.criticalDrawerId} .mcms-critical-advanced-panel {
```

### Lines 12535-12618

```text
12535:             background:transparent !important;
12536:         }
12537:         html[data-mcms-ui-theme="bond007"] #${SCRIPT.panelId} .mcms-title {
12538:             max-width:100% !important;
12539:             overflow:visible !important;
12540:             color:#fff9ea !important;
12541:             font:700 clamp(15px,1.5vw,21px)/1.04 Georgia,"Times New Roman",serif !important;
12542:             letter-spacing:.45px !important;
12543:             white-space:normal !important;
12544:             overflow-wrap:anywhere !important;
12545:         }
12546:         html[data-mcms-ui-theme="bond007"] #${SCRIPT.panelId} .mcms-subtitle {
12547:             max-width:100% !important;
12548:             overflow:visible !important;
12549:             color:#c2c5c7 !important;
12550:             font-size:9px !important;
12551:             line-height:1.15 !important;
12552:             white-space:normal !important;
12553:             overflow-wrap:anywhere !important;
12554:         }
12555: 
12556:         html[data-mcms-ui-theme="bond007"] #${SCRIPT.panelId} .mcms-tabs {
12557:             position:relative !important;
12558:             gap:3px !important;
12559:             padding:5px !important;
12560:             border-bottom:1px solid rgba(214,182,95,.45) !important;
12561:             background:rgba(5,6,8,.88) !important;
12562:         }
12563:         html[data-mcms-ui-theme="bond007"] #${SCRIPT.panelId} .mcms-tabs::after {
12564:             content:"" !important;
12565:             position:absolute !important;
12566:             left:8px !important;
12567:             right:8px !important;
12568:             bottom:-1px !important;
12569:             height:6px !important;
12570:             background:url("${THEME_ASSETS.bond007GoldDivider}") center/100% 100% no-repeat !important;
12571:             opacity:.65 !important;
12572:             pointer-events:none !important;
12573:         }
12574:         html[data-mcms-ui-theme="bond007"] #${SCRIPT.panelId} .mcms-tab-btn {
12575:             min-width:0 !important;
12576:             min-height:40px !important;
12577:             padding:7px 8px !important;
12578:             border:1px solid #494f55 !important;
12579:             border-radius:1px !important;
12580:             background:linear-gradient(180deg,#25292e,#101215) !important;
12581:             color:#dcd7ca !important;
12582:             font-size:10px !important;
12583:             line-height:1.05 !important;
12584:             letter-spacing:.4px !important;
12585:             white-space:normal !important;
12586:             overflow-wrap:anywhere !important;
12587:         }
12588:         html[data-mcms-ui-theme="bond007"] #${SCRIPT.panelId} .mcms-tab-btn.mcms-active {
12589:             border-color:#f0d480 !important;
12590:             border-top:3px solid #a71924 !important;
12591:             background:linear-gradient(180deg,#f2ead5,#c9bb92) !important;
12592:             color:#111214 !important;
12593:             box-shadow:inset 0 0 0 1px rgba(255,255,255,.55),0 0 11px rgba(214,182,95,.22) !important;
12594:         }
12595: 
12596:         html[data-mcms-ui-theme="bond007"] #${SCRIPT.panelId} .mcms-section-label {
12597:             min-height:30px !important;
12598:             padding:8px 12px 8px 38px !important;
12599:             border:1px solid rgba(214,182,95,.55) !important;
12600:             border-left:4px solid #a71924 !important;
12601:             border-radius:1px !important;
12602:             background:
12603:                 url("${THEME_ASSETS.bond007CommandSeal}") 9px center/20px auto no-repeat,
12604:                 linear-gradient(90deg,rgba(244,239,223,.97),rgba(210,201,178,.94)) !important;
12605:             color:#15171a !important;
12606:             font:950 9px/1.15 Arial,sans-serif !important;
12607:             letter-spacing:.75px !important;
12608:             white-space:normal !important;
12609:         }
12610:         html[data-mcms-ui-theme="bond007"] #${SCRIPT.panelId} .mcms-section-label::before { display:none !important; }
12611: 
12612:         html[data-mcms-ui-theme="bond007"] #${SCRIPT.panelId} .mcms-theme-btn,
12613:         html[data-mcms-ui-theme="bond007"] #${SCRIPT.panelId} .mcms-toggle-btn,
12614:         html[data-mcms-ui-theme="bond007"] #${SCRIPT.panelId} .mcms-place-main,
12615:         html[data-mcms-ui-theme="bond007"] #${SCRIPT.panelId} .mcms-position-btn,
12616:         html[data-mcms-ui-theme="bond007"] #${SCRIPT.panelId} .mcms-small-btn,
12617:         html[data-mcms-ui-theme="bond007"] #${SCRIPT.panelId} .mcms-bookmark-btn,
12618:         html[data-mcms-ui-theme="bond007"] #${SCRIPT.panelId} .mcms-pin-btn,
```

### Lines 12770-12802

```text
12770:             left:12px !important;
12771:             right:auto !important;
12772:             bottom:3px !important;
12773:             max-width:calc(100% - 150px) !important;
12774:             overflow:hidden !important;
12775:             color:#d8b45f !important;
12776:             font:900 5.5px/1 Consolas,monospace !important;
12777:             letter-spacing:.75px !important;
12778:             text-overflow:ellipsis !important;
12779:             white-space:nowrap !important;
12780:             opacity:.84 !important;
12781:             pointer-events:none !important;
12782:         }
12783: 
12784:         html[data-mcms-ui-theme="bond007"] #${SCRIPT.criticalDrawerId} .mcms-drawer-title,
12785:         html[data-mcms-ui-theme="bond007"] #${SCRIPT.missionInspectorId} .mcms-inspector-title,
12786:         html[data-mcms-ui-theme="bond007"] #${SCRIPT.vehicleStatusId} .mcms-vehicle-status-title {
12787:             min-width:0 !important;
12788:             overflow:hidden !important;
12789:             color:#fff8e8 !important;
12790:             font-family:Georgia,"Times New Roman",serif !important;
12791:             font-size:clamp(15px,1.4vw,20px) !important;
12792:             line-height:1.05 !important;
12793:             text-overflow:ellipsis !important;
12794:             white-space:nowrap !important;
12795:         }
12796:         html[data-mcms-ui-theme="bond007"] #${SCRIPT.criticalDrawerId} .mcms-critical-filter-deck,
12797:         html[data-mcms-ui-theme="bond007"] #${SCRIPT.criticalDrawerId} .mcms-critical-view-menu,
12798:         html[data-mcms-ui-theme="bond007"] #${SCRIPT.criticalDrawerId} .mcms-critical-advanced-panel {
12799:             border-color:rgba(214,182,95,.35) !important;
12800:             background:rgba(7,9,11,.88) !important;
12801:             box-shadow:inset 3px 0 rgba(167,25,36,.55) !important;
12802:         }
```

### Lines 12833-12849

```text
12833:             border-right:1px solid #d8b45f !important;
12834:             background:
12835:                 url("${THEME_ASSETS.bond007CommandSeal}") 9px center/46px auto no-repeat,
12836:                 linear-gradient(90deg,#f3ecda,#c9bb92) !important;
12837:             color:#111214 !important;
12838:             font-size:0 !important;
12839:             line-height:1 !important;
12840:             letter-spacing:.65px !important;
12841:             white-space:nowrap !important;
12842:         }
12843:         html[data-mcms-ui-theme="bond007"] #${SCRIPT.majorIncidentFeedId} .mcms-incident-feed-label::before {
12844:             display:none !important;
12845:         }
12846:         html[data-mcms-ui-theme="bond007"] #${SCRIPT.majorIncidentFeedId} .mcms-incident-feed-label::after {
12847:             content:"MI6 INCIDENT WIRE" !important;
12848:             position:static !important;
12849:             color:#111214 !important;
```

### Lines 12905-12922

```text
12905:             content:"TOP SECRET // SECTION 00 FINANCIAL AUTHORISATION" !important;
12906:             left:35px !important;
12907:             right:190px !important;
12908:             top:17px !important;
12909:             overflow:hidden !important;
12910:             color:#8f171f !important;
12911:             font:950 8px/1 Consolas,monospace !important;
12912:             letter-spacing:1.15px !important;
12913:             text-overflow:ellipsis !important;
12914:             white-space:nowrap !important;
12915:         }
12916:         #${SCRIPT.payoutFlashId}[data-template="jamesBond"] .mcms-payout-banner::after {
12917:             content:"FILE 00-7 // LONDON" !important;
12918:             right:28px !important;
12919:             bottom:13px !important;
12920:             color:rgba(17,18,20,.55) !important;
12921:             font:950 7px/1 Consolas,monospace !important;
12922:             letter-spacing:1.3px !important;
```

### Lines 13023-13044

```text
13023:             display:none !important;
13024:         }
13025:         html[data-mcms-mobile-active="true"][data-mcms-ui-theme="bond007"] #${SCRIPT.panelId} .mcms-drag-handle {
13026:             min-height:56px !important;
13027:             padding:8px 12px 14px !important;
13028:         }
13029:         html[data-mcms-mobile-active="true"][data-mcms-ui-theme="bond007"] #${SCRIPT.panelId} .mcms-title {
13030:             font-size:15px !important;
13031:             white-space:normal !important;
13032:             line-height:1.02 !important;
13033:         }
13034:         html[data-mcms-mobile-active="true"][data-mcms-ui-theme="bond007"] #${SCRIPT.panelId} .mcms-subtitle {
13035:             font-size:8px !important;
13036:             white-space:normal !important;
13037:         }
13038:         html[data-mcms-mobile-active="true"][data-mcms-ui-theme="bond007"] #${SCRIPT.panelId} .mcms-ui-theme-btn {
13039:             min-height:70px !important;
13040:         }
13041:         html[data-mcms-mobile-active="true"][data-mcms-ui-theme="bond007"] #${SCRIPT.panelId} .mcms-toggle-btn {
13042:             min-height:54px !important;
13043:         }
13044:         html[data-mcms-mobile-active="true"][data-mcms-ui-theme="bond007"] #${SCRIPT.panelId} .mcms-header::after {
```

### Lines 13156-13192

```text
13156:         html[data-mcms-ui-theme="bond007"] #${SCRIPT.missionInspectorId} .mcms-inspector-head > *,
13157:         html[data-mcms-ui-theme="bond007"] #${SCRIPT.vehicleStatusId} .mcms-vehicle-status-head > * {
13158:             min-width:0 !important;
13159:         }
13160:         html[data-mcms-ui-theme="bond007"] #${SCRIPT.panelId} .mcms-theme-btn strong,
13161:         html[data-mcms-ui-theme="bond007"] #${SCRIPT.panelId} .mcms-toggle-btn strong,
13162:         html[data-mcms-ui-theme="bond007"] #${SCRIPT.panelId} .mcms-ui-theme-btn strong,
13163:         html[data-mcms-ui-theme="bond007"] #${SCRIPT.panelId} .mcms-place-main strong,
13164:         html[data-mcms-ui-theme="bond007"] #${SCRIPT.panelId} .mcms-section-label,
13165:         html[data-mcms-ui-theme="bond007"] #${SCRIPT.criticalDrawerId} button,
13166:         html[data-mcms-ui-theme="bond007"] #${SCRIPT.missionInspectorId} button,
13167:         html[data-mcms-ui-theme="bond007"] #${SCRIPT.vehicleStatusId} button {
13168:             overflow-wrap:anywhere !important;
13169:             word-break:normal !important;
13170:         }
13171:         html[data-mcms-ui-theme="bond007"] #${SCRIPT.criticalDrawerId} .mcms-drawer-title,
13172:         html[data-mcms-ui-theme="bond007"] #${SCRIPT.missionInspectorId} .mcms-inspector-title,
13173:         html[data-mcms-ui-theme="bond007"] #${SCRIPT.vehicleStatusId} .mcms-vehicle-status-title {
13174:             max-width:100% !important;
13175:         }
13176:         #${SCRIPT.payoutFlashId}[data-template="jamesBond"] .mcms-payout-banner > * {
13177:             min-width:0 !important;
13178:             max-width:100% !important;
13179:         }
13180:         #${SCRIPT.payoutFlashId}[data-template="jamesBond"] .mcms-payout-title,
13181:         #${SCRIPT.payoutFlashId}[data-template="jamesBond"] .mcms-payout-mission,
13182:         #${SCRIPT.payoutFlashId}[data-template="jamesBond"] .mcms-payout-amount {
13183:             overflow-wrap:anywhere !important;
13184:             word-break:normal !important;
13185:         }
13186:         @media (max-width:430px) {
13187:             #${SCRIPT.payoutFlashId}[data-template="jamesBond"] .mcms-payout-banner {
13188:                 padding-inline:14px !important;
13189:             }
13190:             #${SCRIPT.payoutFlashId}[data-template="jamesBond"] .mcms-payout-banner::before {
13191:                 right:88px !important;
13192:                 letter-spacing:.45px !important;
```

### Lines 13425-13443

```text
13425:             min-width:52px !important;
13426:             max-width:112px !important;
13427:             height:29px !important;
13428:             padding:0 10px !important;
13429:             font-size:9px !important;
13430:             line-height:1 !important;
13431:             letter-spacing:.18px !important;
13432:             text-align:center !important;
13433:             white-space:nowrap !important;
13434:             overflow:hidden !important;
13435:             text-overflow:ellipsis !important;
13436:         }
13437:         #${SCRIPT.panelId} .mcms-bookmark-name-btn {
13438:             appearance:none !important;
13439:             -webkit-appearance:none !important;
13440:             display:flex !important;
13441:             flex-direction:column !important;
13442:             align-items:flex-start !important;
13443:             justify-content:center !important;
```

### Lines 13446-13482

```text
13446:             min-height:30px !important;
13447:             padding:0 2px !important;
13448:             border:0 !important;
13449:             background:transparent !important;
13450:             color:inherit !important;
13451:             line-height:1.05 !important;
13452:             text-align:left !important;
13453:             cursor:pointer !important;
13454:             white-space:normal !important;
13455:             overflow:hidden !important;
13456:         }
13457:         #${SCRIPT.panelId} .mcms-bookmark-name-main {
13458:             display:block !important;
13459:             width:100% !important;
13460:             overflow:hidden !important;
13461:             text-overflow:ellipsis !important;
13462:             white-space:nowrap !important;
13463:         }
13464:         #${SCRIPT.panelId} .mcms-bookmark-short {
13465:             display:block !important;
13466:             max-width:100% !important;
13467:             color:rgba(255,255,255,.55) !important;
13468:             font-size:7px !important;
13469:             line-height:1 !important;
13470:             font-weight:900 !important;
13471:             letter-spacing:.35px !important;
13472:             white-space:nowrap !important;
13473:             overflow:hidden !important;
13474:             text-overflow:ellipsis !important;
13475:         }
13476:         #${SCRIPT.panelId} .mcms-bookmark-name-btn:hover .mcms-bookmark-name-main,
13477:         #${SCRIPT.panelId} .mcms-bookmark-name-btn:focus-visible .mcms-bookmark-name-main {
13478:             text-decoration:underline !important;
13479:         }
13480:         html[data-mcms-tablet-active="true"] #${SCRIPT.controlId} .mcms-screen-pins {
13481:             display:flex !important;
13482:             flex-wrap:wrap !important;
```

### Lines 13715-13758

```text
13715:             font-weight:900 !important;
13716:             letter-spacing:.75px !important;
13717:             text-shadow:0 2px 2px #000,0 0 12px rgba(255,215,79,.28) !important;
13718:         }
13719:         html[data-mcms-ui-theme="hyrule"] #${SCRIPT.panelId} .mcms-subtitle,
13720:         html[data-mcms-ui-theme="hyrule"] #${SCRIPT.criticalDrawerId} .mcms-drawer-subtitle {
13721:             color:rgba(196,255,240,.72) !important;
13722:         }
13723:         html[data-mcms-ui-theme="hyrule"] #${SCRIPT.panelId} .mcms-tabs {
13724:             border-bottom:1px solid rgba(232,193,72,.44) !important;
13725:             background:linear-gradient(180deg,rgba(19,55,42,.82),rgba(5,24,29,.82)) !important;
13726:         }
13727:         html[data-mcms-ui-theme="hyrule"] #${SCRIPT.panelId} .mcms-tab-btn {
13728:             border-color:transparent !important;
13729:             color:rgba(239,227,184,.70) !important;
13730:             background:transparent !important;
13731:             font-family:Georgia,"Palatino Linotype",serif !important;
13732:             letter-spacing:.25px !important;
13733:         }
13734:         html[data-mcms-ui-theme="hyrule"] #${SCRIPT.panelId} .mcms-tab-btn:hover {
13735:             color:#fff3ad !important;
13736:             background:rgba(63,177,139,.12) !important;
13737:         }
13738:         html[data-mcms-ui-theme="hyrule"] #${SCRIPT.panelId} .mcms-tab-btn.mcms-active {
13739:             color:#fff3a1 !important;
13740:             background:linear-gradient(180deg,rgba(86,207,163,.19),rgba(14,62,57,.34)) !important;
13741:             box-shadow:inset 0 -2px #4bf0dd,0 2px 10px rgba(47,226,216,.15) !important;
13742:         }
13743:         html[data-mcms-ui-theme="hyrule"] #${SCRIPT.panelId} .mcms-section-label {
13744:             color:#ffe887 !important;
13745:             border-color:rgba(232,191,68,.44) !important;
13746:             background:
13747:                 linear-gradient(90deg,rgba(111,74,25,.45),rgba(26,78,57,.28),transparent) !important;
13748:             text-shadow:0 1px 2px #000 !important;
13749:         }
13750:         html[data-mcms-ui-theme="hyrule"] #${SCRIPT.panelId} .mcms-section-label::before { color:#62f4dd !important; }
13751:         html[data-mcms-ui-theme="hyrule"] #${SCRIPT.panelId} .mcms-theme-btn,
13752:         html[data-mcms-ui-theme="hyrule"] #${SCRIPT.panelId} .mcms-toggle-btn,
13753:         html[data-mcms-ui-theme="hyrule"] #${SCRIPT.panelId} .mcms-place-main,
13754:         html[data-mcms-ui-theme="hyrule"] #${SCRIPT.panelId} .mcms-position-btn,
13755:         html[data-mcms-ui-theme="hyrule"] #${SCRIPT.panelId} .mcms-small-btn,
13756:         html[data-mcms-ui-theme="hyrule"] #${SCRIPT.panelId} .mcms-bookmark-btn,
13757:         html[data-mcms-ui-theme="hyrule"] #${SCRIPT.panelId} .mcms-pin-btn,
13758:         html[data-mcms-ui-theme="hyrule"] #${SCRIPT.panelId} .mcms-ui-theme-btn,
```

### Lines 14456-14472

```text
14456:     function refreshTabletModeUi(panel = document.getElementById(SCRIPT.panelId)) {
14457:         if (!panel) return;
14458:         panel.classList.toggle('mcms-tablet-active', tabletModeActive);
14459:         panel.classList.toggle('mcms-mobile-active', mobileModeActive);
14460:         const tabletSelect = panel.querySelector('[data-setting="tablet-mode"]');
14461:         const mobileSelect = panel.querySelector('[data-setting="mobile-mode"]');
14462:         if (tabletSelect && document.activeElement !== tabletSelect) tabletSelect.value = state.tabletMode;
14463:         if (mobileSelect && document.activeElement !== mobileSelect) mobileSelect.value = state.mobileMode;
14464:         const status = panel.querySelector('[data-device-layout-status], [data-tablet-status]');
14465:         if (status) status.textContent = tabletModeStatusText();
14466:         const dragHandle = panel.querySelector('.mcms-drag-handle');
14467:         const title = panel.querySelector('.mcms-title');
14468:         const subtitle = panel.querySelector('.mcms-subtitle');
14469:         const touchLayout = isTouchLayoutActive();
14470:         const layoutName = mobileModeActive ? 'MOBILE COMMAND PANEL' : tabletModeActive ? 'TABLET COMMAND PANEL' : '☰ DRAG MENU HERE';
14471:         const layoutHelp = mobileModeActive
14472:             ? 'iPhone Safari layout · swipe vertically · close with ×'
```

### Lines 20306-20322

```text
20306:             const missionId = missionIdFromMarker(marker);
20307:             if (missionId !== null && isAllianceMissionLayer(marker, missionId) && missionHasPersonalUnit(marker, missionId)) count += 1;
20308:         }
20309:         return count;
20310:     }
20311: 
20312:     function operationalUiIsVisible() {
20313:         const panel = document.getElementById(SCRIPT.panelId);
20314:         const opsPanelVisible = Boolean(panel?.classList?.contains('mcms-open') && state.activeTab === 'ops');
20315:         const drawerVisible = Boolean(document.getElementById(SCRIPT.criticalDrawerId)?.classList?.contains('mcms-open'));
20316:         const vehicleStatusVisible = Boolean(document.getElementById(SCRIPT.vehicleStatusId)?.classList?.contains('mcms-open'));
20317:         return opsPanelVisible || drawerVisible || vehicleStatusVisible;
20318:     }
20319: 
20320:     function scheduleOperationalPanelsRender(delay = 500, force = false) {
20321:         runtimeClearTimeout(opsRefreshTimer);
20322:         if (!force && !operationalUiIsVisible()) return;
```

### Lines 20325-20341

```text
20325:         const wait = Math.max(Number(delay) || 0, elapsed < minimumGap ? minimumGap - elapsed : 0);
20326:         opsRefreshTimer = runtimeSetTimeout(() => renderOperationalPanels(force), wait);
20327:     }
20328: 
20329:     function renderOperationalPanels(force = false, criticalRenderOptions = null) {
20330:         runtimeClearTimeout(opsRefreshTimer);
20331:         opsRefreshTimer = null;
20332:         const panel = document.getElementById(SCRIPT.panelId);
20333:         const opsPanelVisible = Boolean(panel?.classList?.contains('mcms-open') && state.activeTab === 'ops');
20334:         const criticalDrawerVisible = Boolean(document.getElementById(SCRIPT.criticalDrawerId)?.classList?.contains('mcms-open'));
20335:         const vehicleStatusVisible = Boolean(document.getElementById(SCRIPT.vehicleStatusId)?.classList?.contains('mcms-open'));
20336:         if (!force && !opsPanelVisible && !criticalDrawerVisible && !vehicleStatusVisible) return;
20337:         operationalPanelsLastRender = Date.now();
20338: 
20339:         if (vehicleStatusVisible) renderVehicleCodeStatus();
20340:         if (!opsPanelVisible && !criticalDrawerVisible) return;
20341: 
```

### Lines 21498-21515

```text
21498:             }
21499:             .mcms-mission-value-badge {
21500:                 display:inline-flex !important;align-items:center !important;justify-content:center !important;
21501:                 max-width:min(100%,260px) !important;min-height:25px !important;box-sizing:border-box !important;
21502:                 padding:4px 10px !important;border:1px solid rgba(235,190,64,.72) !important;border-radius:8px !important;
21503:                 background:linear-gradient(145deg,rgba(48,39,13,.96),rgba(19,21,24,.96)) !important;
21504:                 color:#ffe59a !important;box-shadow:0 2px 8px rgba(0,0,0,.34) !important;
21505:                 font:900 11px/1.25 Arial,Helvetica,sans-serif !important;letter-spacing:.15px !important;
21506:                 text-align:right !important;white-space:nowrap !important;overflow:hidden !important;
21507:                 text-overflow:ellipsis !important;pointer-events:none !important;
21508:             }
21509:             @media (max-width:520px) {
21510:                 .mcms-mission-value-row { padding-right:40px !important; }
21511:                 .mcms-mission-value-badge { max-width:100% !important;font-size:10px !important; }
21512:             }
21513:         `;
21514:         (doc.head || doc.documentElement)?.appendChild(style);
21515:     }
```

### Lines 26833-26851

```text
26833:     function applyTheme(themeKey, persist = true) {
26834:         state.theme = normaliseTheme(themeKey);
26835:         if (persist) saveState();
26836:         applyRootAttributes();
26837:         updateUI();
26838:         showToast(THEMES[state.theme].full);
26839:     }
26840: 
26841:     function setActiveTab(tab) {
26842:         if (!['skins', 'tools', 'resources', 'ops', 'payouts', 'discord', 'places', 'settings'].includes(tab)) return;
26843:         state.activeTab = tab;
26844:         saveState();
26845:         updateUI();
26846:         if (!dragState) positionPanelOverlay(true);
26847:         if (tab === 'ops') refreshPersonalVehicleData(false).finally(() => scheduleOperationalPanelsRender(0, true));
26848:     }
26849: 
26850:     function applyPosition(position, persist = true) {
26851:         state.position = POSITIONS[position] ? position : 'bl';
```

### Lines 27874-27910

```text
27874:                         <span class="mcms-title">☰ DRAG MENU HERE</span>
27875:                         <span class="mcms-subtitle">Hold left-click on this title area. Position saves.</span>
27876:                     </div>
27877:                     <button class="mcms-reset-panel" type="button" data-action="panel-reset" title="Reset menu position">↺</button>
27878:                     <button class="mcms-help-button" type="button" data-action="open-help-center" title="Open searchable Help Centre" aria-label="Open searchable Help Centre">?</button>
27879:                     <button class="mcms-close" type="button" title="Close">×</button>
27880:                 </div>
27881:                 <div class="mcms-tabs">
27882:                     <button class="mcms-tab-btn" type="button" data-tab="skins">Skins</button>
27883:                     <button class="mcms-tab-btn" type="button" data-tab="tools">Tools</button>
27884:                     <button class="mcms-tab-btn" type="button" data-tab="resources">Resources</button>
27885:                     <button class="mcms-tab-btn" type="button" data-tab="ops">Ops</button>
27886:                     <button class="mcms-tab-btn" type="button" data-tab="payouts">Payouts</button>
27887:                     <button class="mcms-tab-btn" type="button" data-tab="discord">Discord</button>
27888:                     <button class="mcms-tab-btn" type="button" data-tab="places">Places</button>
27889:                     <button class="mcms-tab-btn" type="button" data-tab="settings">Settings</button>
27890:                 </div>
27891:             </div>
27892:             <section class="mcms-tab-panel" data-panel="skins">
27893:                 <div class="mcms-section-label">Interface theme</div>
27894:                 <div class="mcms-ui-theme-grid">${uiThemeButtons}</div>
27895:                 <div class="mcms-status mcms-ui-theme-status">Interface themes restyle the complete toolkit without changing your selected operational map skin.</div>
27896:                 <div class="mcms-section-label">Core skins</div>
27897:                 <div class="mcms-grid-2">${coreThemeButtons}</div>
27898:                 <div class="mcms-section-label">Emergency services</div>
27899:                 <div class="mcms-grid-2">${serviceThemeButtons}</div>
27900:                 <div class="mcms-status">Fire Command, Police Tactical, Medical Control and Coastal Command use lightweight local tile filters and remain compatible with map overlays.</div>
27901:             </section>
27902:             <section class="mcms-tab-panel" data-panel="tools">
27903:                 <div class="mcms-section-label">Map tools</div>
27904:                 <div class="mcms-grid-2">
27905:                     ${makeToggleButton('clean', '▢', 'Clean', 'Hide map controls for screenshots. Shortcut: C')}
27906:                     ${makeToggleButton('markerFocus', '◉', 'Focus', 'Dim detected buildings/vehicles and keep missions clearer. Shortcut: F')}
27907:                     ${makeToggleButton('missionPulse', '✦', 'Pulse', 'Pulse detected mission markers. Shortcut: P')}
27908:                     ${makeToggleButton('roadPriority', '═', 'Roads+', 'Increase road contrast. Shortcut: R')}
27909:                     ${makeToggleButton('coverage', '◎', 'Rings', 'Draw coverage rings around detected buildings/stations.')}
27910:                     ${makeToggleButton('heatmap', '▦', 'Heatmap', 'Show strong and weak operational coverage across the visible map.')}
```

### Lines 27931-27947

```text
27931:                     ${makeToggleButton('missionAge', '6', 'Miss Age', 'Show personal mission age with progressive 8H amber, 16H orange and 24H red severity. Shortcut: 6')}
27932:                     ${makeToggleButton('transportWatcher', '7', 'Transport Watcher', 'Show amber transport-required badges beside personal and alliance missions. Shortcut: 7')}
27933:                     ${makeToggleButton('unitCommitment', '8', 'Unit Count', 'Show your committed units beside personal and alliance missions. Shortcut: 8')}
27934:                     ${makeToggleButton('criticalView', '9', 'Critical View', 'Temporarily show only personal missions aged 8 hours or more. Shortcut: 9')}
27935:                 </div>
27936:                 <div class="mcms-row" style="margin-top:8px"><span class="mcms-row-label">Ally Credits filter</span><select class="mcms-select" data-setting="alliance-credit-minimum"><option value="0">All values</option><option value="5000">5K+</option><option value="10000">10K+</option><option value="15000">15K+</option><option value="20000">20K+</option></select></div>
27937:                 <div class="mcms-status">Ready.</div>
27938:             </section>
27939:             <section class="mcms-tab-panel" data-panel="resources">
27940:                 <div class="mcms-section-label">Co-admin Patient Transport Sweep</div>
27941:                 <div class="mcms-grid-2">
27942:                     <button class="mcms-small-btn" type="button" data-action="scan-transport-sweep">Scan Transports</button>
27943:                     <button class="mcms-small-btn" type="button" data-action="start-transport-sweep">Start Sweep</button>
27944:                     <button class="mcms-small-btn" type="button" data-action="stop-transport-sweep">Stop</button>
27945:                     ${makeToggleButton('transportWatcher', '7', 'Transport Watch', 'Show amber transport-required badges beside missions. Shortcut: 7')}
27946:                 </div>
27947:                 <div class="mcms-row"><span class="mcms-row-label">Delay between clears</span><select class="mcms-select" data-setting="transport-sweep-delay"><option value="1500">1.5 seconds</option><option value="2000">2 seconds</option><option value="2500">2.5 seconds</option><option value="3000">3 seconds</option><option value="4000">4 seconds</option><option value="5000">5 seconds</option></select></div>
```

### Lines 27950-27966

```text
27950:                 <div class="mcms-status">Manual start only. The sweep excludes your personal vehicle IDs, checks every non-personal FMS 5 patient vehicle in each affected alliance mission, and only clears a vehicle when MissionChief exposes the visible <b>Discharge patient</b> button. Prisoner transports are not included.</div>
27951:                 <div class="mcms-section-label">Resource Gap Finder</div>
27952:                 <div class="mcms-grid-2">
27953:                     ${makeToggleButton('resourceGap', '⚠', 'Resource Gap', 'Show missing-resource badges and nearby available-unit estimates in Mission Inspector.')}
27954:                 </div>
27955:                 <div class="mcms-row"><span class="mcms-row-label">Nearby radius</span><select class="mcms-select" data-setting="resource-gap-radius"><option value="10">10 miles</option><option value="25">25 miles</option><option value="50">50 miles</option><option value="100">100 miles</option></select></div>
27956:                 <div class="mcms-status">Resource Gap uses MissionChief's missing-requirement text and performs best-effort matching against your currently available vehicle types. It never selects or dispatches units.</div>
27957:             </section>
27958:             <section class="mcms-tab-panel" data-panel="ops">
27959:                 <div class="mcms-section-label">Mission Intelligence</div>
27960:                 <div class="mcms-grid-2">
27961:                     ${makeToggleButton('missionInspector', 'ⓘ', 'Inspector', 'Hover a mission marker for a live mission summary.')}
27962:                     ${makeToggleButton('missionValue', '£', 'Mission Value', 'Show a formatted mission value in opened MissionChief windows.')}
27963:                     ${makeToggleButton('stuckDetector', '⚠', 'Stuck Detect', 'Flag personal or joined missions that show no meaningful progress.')}
27964:                     ${makeToggleButton('missionSpawn', '◎', 'New Mission', 'Animate genuinely new mission spawns with a radar pulse.')}
27965:                     ${makeToggleButton('transportWatcher', '7', 'Transport Watch', 'Show amber transport-required badges beside missions. Shortcut: 7')}
27966:                     ${makeToggleButton('unitCommitment', '8', 'Unit Count', 'Show your own committed unit counts beside missions. Shortcut: 8')}
```

### Lines 27984-28014

```text
27984:                 <div class="mcms-ops-list" data-ops-critical-preview></div>
27985:                 <div class="mcms-section-label">Completion History</div>
27986:                 <div class="mcms-ops-list" data-ops-history></div>
27987:                 <div class="mcms-grid-2" style="margin-top:7px !important">
27988:                     <button class="mcms-small-btn" type="button" data-action="reset-session">Reset Session</button>
27989:                     <button class="mcms-small-btn" type="button" data-action="clear-payout-history">Clear History</button>
27990:                 </div>
27991:             </section>
27992:             <section class="mcms-tab-panel" data-panel="payouts">
27993:                 <div class="mcms-section-label">Emergency Payout Flash</div>
27994:                 <div class="mcms-grid-2">
27995:                     ${makeToggleButton('payoutFlash', '🚨', 'Payout Flash', 'Flash the map red and blue when a single credit gain reaches the configured threshold.')}
27996:                     ${makeToggleButton('payoutSound', '♪', 'Theme Audio', 'Play the selected template completion cue. Vice City, Bad Company, Scarface and Cyberpunk use hosted MP3 cashout sounds; other templates retain synthesized cues.')}
27997:                 </div>
27998:                 <div class="mcms-row"><span class="mcms-row-label">Banner style</span><select class="mcms-select" data-setting="payout-template">${buildPayoutTemplateOptions(state.payoutFlash.template)}</select></div>
27999:                 <div class="mcms-row"><span class="mcms-row-label">Minimum payout</span><input class="mcms-input" type="number" min="1000" step="1000" data-setting="payout-threshold"></div>
28000:                 <div class="mcms-row"><span class="mcms-row-label">Flash duration (sec)</span><input class="mcms-input" type="number" min="2" max="30" step="2" data-setting="payout-duration"></div>
28001:                 <div class="mcms-row"><span class="mcms-row-label">Sound volume</span><input class="mcms-input" type="range" min="0" max="1" step="0.05" data-setting="payout-volume"></div>
28002:                 <div class="mcms-row"><span class="mcms-row-label">Test payout tier</span><select class="mcms-select" data-setting="payout-test-amount"><option value="10000">10K Standard</option><option value="25000">25K Major</option><option value="50000">50K High Value</option><option value="100000">100K Elite</option></select></div>
28003:                 <button class="mcms-small-btn" style="width:100% !important;margin-bottom:8px !important" type="button" data-action="test-payout-flash">Test Emergency Flash</button>
28004:                 <div class="mcms-status">Vice City Inspired, Bad Company Inspired, Scarface Inspired and Cyberpunk Inspired use hosted cashout MP3s from your public GitHub asset repository. Other templates retain synthesized cues. Enable Theme Audio, set the volume, then use Test Emergency Flash.</div>
28005:             </section>
28006:             <section class="mcms-tab-panel" data-panel="discord">
28007:                 <div class="mcms-section-label">Discord Financial Command</div>
28008:                 <div class="mcms-row mcms-discord-wide"><span class="mcms-row-label">Webhook URL</span><input class="mcms-input" type="password" autocomplete="off" spellcheck="false" data-setting="discord-webhook" placeholder="https://discord.com/api/webhooks/..."></div>
28009:                 <div class="mcms-row mcms-discord-wide"><span class="mcms-row-label">Webhook name</span><input class="mcms-input" type="text" maxlength="80" data-setting="discord-name" value="MissionChief Finance"></div>
28010:                 <div class="mcms-row"><span class="mcms-row-label">Report format</span><select class="mcms-select" data-setting="discord-report-mode"><option value="fullAudit">Executive + Full Audit</option><option value="executive">Executive Brief Only</option></select></div>
28011:                 <div class="mcms-row"><span class="mcms-row-label">Report period</span><select class="mcms-select" data-setting="discord-period"><option value="today">Today</option><option value="yesterday">Yesterday</option><option value="last24">Last 24 Hours</option><option value="last7">Last 7 Days</option><option value="last30">Last 30 Days</option><option value="last90">Last 90 Days</option><option value="last180">Last 180 Days</option><option value="last365">Last 365 Days</option><option value="allAvailable">All Available History</option><option value="session">Current Session</option><option value="sinceLast">Since Last Report</option><option value="custom">Custom Dates</option></select></div>
28012:                 <div class="mcms-discord-date-grid">
28013:                     <div class="mcms-row"><span class="mcms-row-label">From</span><input class="mcms-input" type="date" data-setting="discord-custom-start"></div>
28014:                     <div class="mcms-row"><span class="mcms-row-label">To</span><input class="mcms-input" type="date" data-setting="discord-custom-end"></div>
```

### Lines 28039-28061

```text
28039:                 <button class="mcms-small-btn" style="width:100% !important;margin-top:7px !important" type="button" data-action="finance-archive-clear">Clear This Player's Local Archive</button>
28040:                 <input class="mcms-hidden-file" type="file" accept="application/json,text/json,.json" data-import-finance-file>
28041:                 <div class="mcms-finance-vault-summary" data-finance-vault-summary></div>
28042:                 <div class="mcms-status mcms-discord-status" data-finance-vault-status data-tone="neutral">Local Financial Archive ready.</div>
28043:                 <div class="mcms-status mcms-discord-status" data-finance-rule-status data-tone="neutral">Built-in financial intelligence active.</div>
28044:                 <div class="mcms-status">GitHub hosts public transaction-classification rules and audit policy only. The Toolkit never uploads player ledger data, Discord webhooks or repository credentials. The local archive is indexed by MissionChief player ID/name and can be transferred between devices using Export Archive / Import Archive or the complete private Toolkit backup.</div>
28045:                 <div class="mcms-status mcms-finance-private-note">Private backup warning: Export All includes your Discord webhook and locally stored MissionChief financial history. Anyone holding the file may post through the webhook and inspect the exported game ledger.</div>
28046:             </section>
28047:             <section class="mcms-tab-panel" data-panel="places">
28048:                 <div class="mcms-section-label">Quick jumps + screen shortcuts</div>
28049:                 <div class="mcms-quick-list"></div>
28050:                 <div class="mcms-section-label">Custom bookmarks + screen shortcuts</div>
28051:                 <div class="mcms-bookmark-list"></div>
28052:             </section>
28053:             <section class="mcms-tab-panel" data-panel="settings">
28054:                 <div class="mcms-section-label">Device layout</div>
28055:                 <div class="mcms-row"><span class="mcms-row-label">Mobile Mode · iOS Safari</span><select class="mcms-select" data-setting="mobile-mode"><option value="auto">Auto detect iPhone</option><option value="on">Always on</option><option value="off">Always off</option></select></div>
28056:                 <div class="mcms-row"><span class="mcms-row-label">Tablet Mode</span><select class="mcms-select" data-setting="tablet-mode"><option value="auto">Auto detect</option><option value="on">Always on</option><option value="off">Always off</option></select></div>
28057:                 <div class="mcms-status" data-device-layout-status>Detecting device layout…</div>
28058:                 <div class="mcms-status">Mobile Mode is tuned for iPhone Safari with Tampermonkey: a map-aware 5×2 command grid in portrait, a compact single-row dock where space allows, full-width safe-area bottom sheets, 16px form controls to prevent Safari input zoom, and Visual Viewport handling for the iOS keyboard. Tablet and desktop layouts remain separate and unchanged.</div>
28059:                 <div class="mcms-section-label">Dock position</div>
28060:                 <div class="mcms-position-grid">${positionButtons}</div>
28061:                 <div class="mcms-desktop-position-controls">
```

### Lines 28109-28166

```text
28109:                 <div class="mcms-status">Backups include every persistent toolkit preference, desktop/Tablet/iOS layout choice, profile, bookmark, saved Discord webhook and local Financial Archive history. A clear private-file warning is shown before export and import. Store the JSON securely. Current and legacy toolkit backup files are supported.</div>
28110:             </section>
28111:             <div class="mcms-footer">
28112:                 <span>Audited runtime: compact Smart Bookmark Labels, responsive modes and every interface theme remain fully preserved.</span>
28113:                 <span class="mcms-build">${SCRIPT.name} v${SCRIPT.version} · MIT · ${SCRIPT.author}</span>
28114:             </div>
28115:         `;
28116: 
28117:         const tabList = panel.querySelector('.mcms-tabs');
28118:         if (tabList) tabList.setAttribute('role', 'tablist');
28119:         panel.querySelectorAll('.mcms-tab-btn').forEach(button => {
28120:             const tab = button.dataset.tab;
28121:             button.id = `mcms-tab-${tab}`;
28122:             button.setAttribute('role', 'tab');
28123:             button.setAttribute('aria-controls', `mcms-tabpanel-${tab}`);
28124:             button.setAttribute('aria-selected', 'false');
28125:             button.tabIndex = -1;
28126:         });
28127:         panel.querySelectorAll('.mcms-tab-panel').forEach(tabPanel => {
28128:             const tab = tabPanel.dataset.panel;
28129:             tabPanel.id = `mcms-tabpanel-${tab}`;
28130:             tabPanel.setAttribute('role', 'tabpanel');
28131:             tabPanel.setAttribute('aria-labelledby', `mcms-tab-${tab}`);
28132:             tabPanel.hidden = true;
28133:         });
28134: 
28135:         panel.addEventListener('keydown', event => {
28136:             const current = closestEventTarget(event, '.mcms-tab-btn');
28137:             if (!current || !['ArrowLeft', 'ArrowRight', 'Home', 'End'].includes(event.key)) return;
28138:             const buttons = Array.from(panel.querySelectorAll('.mcms-tab-btn'));
28139:             const currentIndex = Math.max(0, buttons.indexOf(current));
28140:             const nextIndex = event.key === 'Home' ? 0
28141:                 : event.key === 'End' ? buttons.length - 1
28142:                 : (currentIndex + (event.key === 'ArrowRight' ? 1 : -1) + buttons.length) % buttons.length;
28143:             event.preventDefault();
28144:             const nextButton = buttons[nextIndex];
28145:             setActiveTab(nextButton.dataset.tab);
28146:             nextButton.focus({ preventScroll: true });
28147:         });
28148: 
28149:         panel.addEventListener('click', event => {
28150:             const closeButton = closestEventTarget(event, '.mcms-close');
28151:             const tabButton = closestEventTarget(event, '.mcms-tab-btn');
28152:             const uiThemeButton = closestEventTarget(event, '.mcms-ui-theme-btn');
28153:             const themeButton = closestEventTarget(event, '.mcms-theme-btn');
28154:             const toggleButton = closestEventTarget(event, '[data-toggle]');
28155:             const positionButton = closestEventTarget(event, '.mcms-position-btn');
28156:             const actionButton = closestEventTarget(event, '[data-action]');
28157:             if (closeButton) { closePanel({ restoreFocus: true }); return; }
28158:             if (tabButton) { setActiveTab(tabButton.dataset.tab); return; }
28159:             if (uiThemeButton) { applyUiTheme(uiThemeButton.dataset.uiTheme, true); return; }
28160:             if (themeButton) { applyTheme(themeButton.dataset.theme, true); return; }
28161:             if (toggleButton) { toggleFeature(toggleButton.dataset.toggle); return; }
28162:             if (positionButton) { applyPosition(positionButton.dataset.position, true); return; }
28163:             if (actionButton) {
28164:                 event.preventDefault();
28165:                 handleAction(actionButton);
28166:                 return;
```

### Lines 28616-28639

```text
28616:                 const icon = dockToggleButton.querySelector('.mcms-dock-toggle-icon');
28617:                 if (icon) icon.textContent = open ? '▴' : '▾';
28618:             }
28619:         }
28620: 
28621:         if (!panel) return;
28622: 
28623:         refreshTabletModeUi(panel);
28624:         panel.querySelectorAll('.mcms-tab-btn').forEach(btn => {
28625:             const active = btn.dataset.tab === state.activeTab;
28626:             btn.classList.toggle('mcms-active', active);
28627:             btn.setAttribute('aria-selected', String(active));
28628:             btn.tabIndex = active ? 0 : -1;
28629:         });
28630:         panel.querySelectorAll('.mcms-tab-panel').forEach(tabPanel => {
28631:             const active = tabPanel.dataset.panel === state.activeTab;
28632:             tabPanel.classList.toggle('mcms-active', active);
28633:             tabPanel.hidden = !active;
28634:         });
28635:         const panelOpen = panel.classList.contains('mcms-open');
28636:         panel.setAttribute('aria-hidden', String(!panelOpen));
28637:         control?.querySelector('.mcms-menu-btn')?.setAttribute('aria-expanded', String(panelOpen));
28638:         panel.querySelectorAll('.mcms-ui-theme-btn').forEach(btn => {
28639:             const active = btn.dataset.uiTheme === state.uiTheme;
```

### Lines 28695-28711

```text
28695:         const heatmapOpacity = panel.querySelector('[data-setting="heatmap-opacity"]');
28696:         if (heatmapOpacity) heatmapOpacity.value = String(state.heatmap.opacity);
28697:         const allianceCreditMinimum = panel.querySelector('[data-setting="alliance-credit-minimum"]');
28698:         if (allianceCreditMinimum) allianceCreditMinimum.value = String(state.allianceCreditMinimum);
28699:         const transportSweepDelay = panel.querySelector('[data-setting="transport-sweep-delay"]');
28700:         if (transportSweepDelay) transportSweepDelay.value = String(state.transportSweep.delayMs);
28701:         const transportSweepMax = panel.querySelector('[data-setting="transport-sweep-max"]');
28702:         if (transportSweepMax) transportSweepMax.value = String(state.transportSweep.maxPerRun);
28703:         if (panel.classList.contains('mcms-open') && state.activeTab === 'resources') renderTransportSweepPanel();
28704:         const payoutTemplate = panel.querySelector('[data-setting="payout-template"]');
28705:         if (payoutTemplate) payoutTemplate.value = state.payoutFlash.template;
28706:         const resourceGapRadius = panel.querySelector('[data-setting="resource-gap-radius"]'); if (resourceGapRadius) resourceGapRadius.value = String(state.resourceGap.radiusMi);
28707:         const stuckThreshold = panel.querySelector('[data-setting="stuck-threshold"]');
28708:         if (stuckThreshold) stuckThreshold.value = String(state.stuckDetector.thresholdMin);
28709:         const payoutThreshold = panel.querySelector('[data-setting="payout-threshold"]');
28710:         if (payoutThreshold) payoutThreshold.value = String(state.payoutFlash.threshold);
28711:         const payoutDuration = panel.querySelector('[data-setting="payout-duration"]');
```

### Lines 28736-28768

```text
28736:         if (discordForecast) discordForecast.value = String(state.discordReport.includeForecast);
28737:         const financeVaultEnabled = panel.querySelector('[data-setting="finance-vault-enabled"]');
28738:         if (financeVaultEnabled) financeVaultEnabled.value = String(state.financialVault.enabled);
28739:         const financeVaultRetention = panel.querySelector('[data-setting="finance-vault-retention"]');
28740:         if (financeVaultRetention) financeVaultRetention.value = String(state.financialVault.retentionDays);
28741:         const financeRuleFeed = panel.querySelector('[data-setting="finance-rule-feed"]');
28742:         if (financeRuleFeed) financeRuleFeed.value = String(state.financialVault.ruleFeedEnabled);
28743:         setDiscordStatus(discordFinanceStatus, discordFinanceStatusTone);
28744:         if (panel.classList.contains('mcms-open') && state.activeTab === 'discord') renderFinanceVaultStatus();
28745:         const nightStart = panel.querySelector('[data-setting="auto-night-start"]');
28746:         if (nightStart) nightStart.value = state.autoNight.nightStart;
28747:         const dayStart = panel.querySelector('[data-setting="auto-day-start"]');
28748:         if (dayStart) dayStart.value = state.autoNight.dayStart;
28749:         const nightTheme = panel.querySelector('[data-setting="auto-night-theme"]');
28750:         if (nightTheme) nightTheme.value = state.autoNight.nightTheme;
28751:         const dayTheme = panel.querySelector('[data-setting="auto-day-theme"]');
28752:         if (dayTheme) dayTheme.value = state.autoNight.dayTheme;
28753:         const economyStatus = panel.querySelector('.mcms-economy-status');
28754:         if (economyStatus) economyStatus.textContent = state.economyMode
28755:             ? 'Economy Mode is ON: static visual effects, adaptive refresh intervals and off-screen vehicle/building layer culling are active.'
28756:             : 'Economy Mode is OFF. Use the leaf button beside the map-menu opener to reduce CPU, GPU and marker workload.';
28757:         const nudge = panel.querySelector('.mcms-nudge-value');
28758:         if (nudge) nudge.textContent = `X ${state.nudge.x} / Y ${state.nudge.y}`;
28759:         if (panel.classList.contains('mcms-open') && state.activeTab === 'settings') renderProfiles();
28760:         if ((panel.classList.contains('mcms-open') && state.activeTab === 'ops') || operationalUiIsVisible()) renderOperationalPanels();
28761:     }
28762: 
28763:     function ensureUi() {
28764:         const mapEl = getLargestLeafletMap();
28765:         if (settingsPanelActivated && !document.getElementById(SCRIPT.panelId)) createPanel();
28766:         if (mapEl) {
28767:             createControl(mapEl);
28768:             const map = findLeafletMapInstance(false);
```

