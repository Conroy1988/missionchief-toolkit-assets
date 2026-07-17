# Issue 92 navigation diagnostic

Canonical source lines: 29733

## Skins

Occurrences: 1

### Lines 27872-27892
```text
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
```

## Tools

Occurrences: 1

### Lines 27873-27893
```text
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
```

## Resources

Occurrences: 1

### Lines 27874-27894
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
```

## Ops

Occurrences: 2

### Lines 20391-20411
```text
20391:                     html = `
20392:                         <div class="mcms-history-latest">${latest.map(historyEntryHtml).join('')}</div>
20393:                         ${older.length ? `<details class="mcms-history-older" data-ops-history-older>
20394:                             <summary>Earlier payouts (${older.length})</summary>
20395:                             <div class="mcms-history-scroll">${older.map(historyEntryHtml).join('')}</div>
20396:                         </details>` : ''}`;
20397:                 }
20398:                 setInnerHtmlIfChanged(history, html, `history:${payoutHistory.map(entry => entry.id).join('|')}`);
20399:             }
20400:         }
20401:         // Keep Mission Age Watch independent from the personal-only Ops preview.
20402:         // The drawer rebuilds its full Personal/Event/Alliance dataset only when open.
20403:         if (criticalDrawerVisible) renderCriticalDrawer(null, criticalRenderOptions || {});
20404:     }
20405: 
20406:     function vehicleCodeStatusSnapshot() {
20407:         const counts = new Map();
20408:         const seen = new Set();
20409:         let total = 0;
20410: 
20411:         for (const vehicle of getPersonalVehicleRecords()) {
```

### Lines 27875-27895
```text
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
```

## Payouts

Occurrences: 16

### Lines 18981-19001
```text
18981:     }
18982: 
18983:     function savePayoutHistory() {
18984:         try { localStorage.setItem(SCRIPT.payoutHistoryState, JSON.stringify(payoutHistory.slice(0, PAYOUT_HISTORY_LIMIT))); }
18985:         catch (err) {}
18986:     }
18987: 
18988:     function defaultSessionPerformance() {
18989:         return {
18990:             startedAt: Date.now(), creditsEarned: 0, payoutCount: 0, qualifyingCount: 0,
18991:             largestPayout: 0, personalPayouts: 0, alliancePayouts: 0, unknownPayouts: 0
18992:         };
18993:     }
18994: 
18995:     function loadSessionPerformance() {
18996:         try {
18997:             const parsed = JSON.parse(sessionStorage.getItem(SCRIPT.sessionPerformanceState) || 'null');
18998:             if (!parsed || typeof parsed !== 'object') return defaultSessionPerformance();
18999:             return { ...defaultSessionPerformance(), ...parsed };
19000:         } catch (err) { return defaultSessionPerformance(); }
19001:     }
```

### Lines 19850-19870
```text
19850:             source: ['personal', 'alliance'].includes(context?.source) ? context.source : 'unknown', tier
19851:         };
19852:         payoutHistory.unshift(entry);
19853:         if (payoutHistory.length > PAYOUT_HISTORY_LIMIT) payoutHistory.length = PAYOUT_HISTORY_LIMIT;
19854:         savePayoutHistory();
19855: 
19856:         sessionPerformance.creditsEarned = Math.max(0, Number(sessionPerformance.creditsEarned) || 0) + value;
19857:         sessionPerformance.payoutCount = Math.max(0, Number(sessionPerformance.payoutCount) || 0) + 1;
19858:         if (value >= 10000) sessionPerformance.qualifyingCount = Math.max(0, Number(sessionPerformance.qualifyingCount) || 0) + 1;
19859:         sessionPerformance.largestPayout = Math.max(Number(sessionPerformance.largestPayout) || 0, value);
19860:         if (entry.source === 'personal') sessionPerformance.personalPayouts = Math.max(0, Number(sessionPerformance.personalPayouts) || 0) + 1;
19861:         else if (entry.source === 'alliance') sessionPerformance.alliancePayouts = Math.max(0, Number(sessionPerformance.alliancePayouts) || 0) + 1;
19862:         else sessionPerformance.unknownPayouts = Math.max(0, Number(sessionPerformance.unknownPayouts) || 0) + 1;
19863:         saveSessionPerformance();
19864:         renderOperationalPanels();
19865:     }
19866: 
19867:     function formatOperationalCompactCredits(value) {
19868:         const amount = Math.max(0, Number(value) || 0);
19869:         if (amount >= 1000000) return `${(amount / 1000000).toFixed(amount >= 10000000 ? 0 : 1)}M`;
19870:         if (amount >= 1000) return `${(amount / 1000).toFixed(amount >= 100000 ? 0 : 1)}K`;
```

### Lines 19851-19871
```text
19851:         };
19852:         payoutHistory.unshift(entry);
19853:         if (payoutHistory.length > PAYOUT_HISTORY_LIMIT) payoutHistory.length = PAYOUT_HISTORY_LIMIT;
19854:         savePayoutHistory();
19855: 
19856:         sessionPerformance.creditsEarned = Math.max(0, Number(sessionPerformance.creditsEarned) || 0) + value;
19857:         sessionPerformance.payoutCount = Math.max(0, Number(sessionPerformance.payoutCount) || 0) + 1;
19858:         if (value >= 10000) sessionPerformance.qualifyingCount = Math.max(0, Number(sessionPerformance.qualifyingCount) || 0) + 1;
19859:         sessionPerformance.largestPayout = Math.max(Number(sessionPerformance.largestPayout) || 0, value);
19860:         if (entry.source === 'personal') sessionPerformance.personalPayouts = Math.max(0, Number(sessionPerformance.personalPayouts) || 0) + 1;
19861:         else if (entry.source === 'alliance') sessionPerformance.alliancePayouts = Math.max(0, Number(sessionPerformance.alliancePayouts) || 0) + 1;
19862:         else sessionPerformance.unknownPayouts = Math.max(0, Number(sessionPerformance.unknownPayouts) || 0) + 1;
19863:         saveSessionPerformance();
19864:         renderOperationalPanels();
19865:     }
19866: 
19867:     function formatOperationalCompactCredits(value) {
19868:         const amount = Math.max(0, Number(value) || 0);
19869:         if (amount >= 1000000) return `${(amount / 1000000).toFixed(amount >= 10000000 ? 0 : 1)}M`;
19870:         if (amount >= 1000) return `${(amount / 1000).toFixed(amount >= 100000 ? 0 : 1)}K`;
19871:         return Math.round(amount).toLocaleString();
```

### Lines 19852-19872
```text
19852:         payoutHistory.unshift(entry);
19853:         if (payoutHistory.length > PAYOUT_HISTORY_LIMIT) payoutHistory.length = PAYOUT_HISTORY_LIMIT;
19854:         savePayoutHistory();
19855: 
19856:         sessionPerformance.creditsEarned = Math.max(0, Number(sessionPerformance.creditsEarned) || 0) + value;
19857:         sessionPerformance.payoutCount = Math.max(0, Number(sessionPerformance.payoutCount) || 0) + 1;
19858:         if (value >= 10000) sessionPerformance.qualifyingCount = Math.max(0, Number(sessionPerformance.qualifyingCount) || 0) + 1;
19859:         sessionPerformance.largestPayout = Math.max(Number(sessionPerformance.largestPayout) || 0, value);
19860:         if (entry.source === 'personal') sessionPerformance.personalPayouts = Math.max(0, Number(sessionPerformance.personalPayouts) || 0) + 1;
19861:         else if (entry.source === 'alliance') sessionPerformance.alliancePayouts = Math.max(0, Number(sessionPerformance.alliancePayouts) || 0) + 1;
19862:         else sessionPerformance.unknownPayouts = Math.max(0, Number(sessionPerformance.unknownPayouts) || 0) + 1;
19863:         saveSessionPerformance();
19864:         renderOperationalPanels();
19865:     }
19866: 
19867:     function formatOperationalCompactCredits(value) {
19868:         const amount = Math.max(0, Number(value) || 0);
19869:         if (amount >= 1000000) return `${(amount / 1000000).toFixed(amount >= 10000000 ? 0 : 1)}M`;
19870:         if (amount >= 1000) return `${(amount / 1000).toFixed(amount >= 100000 ? 0 : 1)}K`;
19871:         return Math.round(amount).toLocaleString();
19872:     }
```

### Lines 25873-25893
```text
25873:         if (finite.length < 2) return 0;
25874:         const average = finite.reduce((sum, value) => sum + value, 0) / finite.length;
25875:         return Math.sqrt(finite.reduce((sum, value) => sum + Math.pow(value - average, 2), 0) / finite.length);
25876:     }
25877: 
25878:     function summariseFinancialTransactions(transactions, period) {
25879:         const incomeCategoryMap = new Map();
25880:         const spendingCategoryMap = new Map();
25881:         const operatingExpenseCategoryMap = new Map();
25882:         const capitalCategoryMap = new Map();
25883:         const topPayouts = [];
25884:         const missionPayoutValues = [];
25885:         const unclassifiedEntries = [];
25886:         let income = 0;
25887:         let spending = 0;
25888:         let operatingIncome = 0;
25889:         let otherIncome = 0;
25890:         let operatingExpense = 0;
25891:         let capitalInvestment = 0;
25892:         let incomeCount = 0;
25893:         let spendingCount = 0;
```

### Lines 25905-25925
```text
25905:         let unclassifiedCount = 0;
25906:         let hasMissionPayout = false;
25907: 
25908:         const addCategory = (map, category, amount) => {
25909:             const existing = map.get(category.key) || { key: category.key, label: category.label, accountingGroup: category.accountingGroup, total: 0, count: 0 };
25910:             existing.total += Math.abs(amount);
25911:             existing.count += 1;
25912:             map.set(category.key, existing);
25913:         };
25914:         const addTopPayout = entry => {
25915:             topPayouts.push(entry);
25916:             topPayouts.sort((a, b) => b.amount - a.amount);
25917:             if (topPayouts.length > 8) topPayouts.length = 8;
25918:         };
25919: 
25920:         const classifiedTransactions = [];
25921:         for (const sourceEntry of transactions) {
25922:             const amount = Number(sourceEntry.amount) || 0;
25923:             if (!amount) continue;
25924:             const category = classifyFinancialTransaction(sourceEntry);
25925:             const entry = { ...sourceEntry, classification: category };
```

### Lines 25906-25926
```text
25906:         let hasMissionPayout = false;
25907: 
25908:         const addCategory = (map, category, amount) => {
25909:             const existing = map.get(category.key) || { key: category.key, label: category.label, accountingGroup: category.accountingGroup, total: 0, count: 0 };
25910:             existing.total += Math.abs(amount);
25911:             existing.count += 1;
25912:             map.set(category.key, existing);
25913:         };
25914:         const addTopPayout = entry => {
25915:             topPayouts.push(entry);
25916:             topPayouts.sort((a, b) => b.amount - a.amount);
25917:             if (topPayouts.length > 8) topPayouts.length = 8;
25918:         };
25919: 
25920:         const classifiedTransactions = [];
25921:         for (const sourceEntry of transactions) {
25922:             const amount = Number(sourceEntry.amount) || 0;
25923:             if (!amount) continue;
25924:             const category = classifyFinancialTransaction(sourceEntry);
25925:             const entry = { ...sourceEntry, classification: category };
25926:             classifiedTransactions.push(entry);
```

### Lines 25907-25927
```text
25907: 
25908:         const addCategory = (map, category, amount) => {
25909:             const existing = map.get(category.key) || { key: category.key, label: category.label, accountingGroup: category.accountingGroup, total: 0, count: 0 };
25910:             existing.total += Math.abs(amount);
25911:             existing.count += 1;
25912:             map.set(category.key, existing);
25913:         };
25914:         const addTopPayout = entry => {
25915:             topPayouts.push(entry);
25916:             topPayouts.sort((a, b) => b.amount - a.amount);
25917:             if (topPayouts.length > 8) topPayouts.length = 8;
25918:         };
25919: 
25920:         const classifiedTransactions = [];
25921:         for (const sourceEntry of transactions) {
25922:             const amount = Number(sourceEntry.amount) || 0;
25923:             if (!amount) continue;
25924:             const category = classifyFinancialTransaction(sourceEntry);
25925:             const entry = { ...sourceEntry, classification: category };
25926:             classifiedTransactions.push(entry);
25927:             const weight = Math.max(1, Math.abs(amount));
```

### Lines 25962-25982
```text
25962:                     capitalInvestment += absolute;
25963:                     addCategory(capitalCategoryMap, category, amount);
25964:                 } else {
25965:                     operatingExpense += absolute;
25966:                     addCategory(operatingExpenseCategoryMap, category, amount);
25967:                 }
25968:             }
25969:         }
25970: 
25971:         if (!hasMissionPayout) {
25972:             topPayouts.length = 0;
25973:             largestReward = 0;
25974:             smallestReward = Infinity;
25975:             for (const entry of classifiedTransactions) {
25976:                 if (entry.amount <= 0) continue;
25977:                 largestReward = Math.max(largestReward, entry.amount);
25978:                 smallestReward = Math.min(smallestReward, entry.amount);
25979:                 addTopPayout(entry);
25980:             }
25981:         }
25982: 
```

### Lines 26034-26054
```text
26034:             calendarDays: Math.round(calendarDays * 1000) / 1000,
26035:             classificationConfidence,
26036:             unclassifiedAmount,
26037:             unclassifiedCount,
26038:             unclassifiedEntries,
26039:             operatingMarginPercent,
26040:             capitalInvestmentRatioPercent,
26041:             incomeConcentrationPercent,
26042:             incomeVolatilityPercent,
26043:             topIncomeCategory,
26044:             topPayouts,
26045:             buckets
26046:         };
26047:     }
26048: 
26049:     function percentageChange(current, previous) {
26050:         const currentValue = Number(current) || 0;
26051:         const previousValue = Number(previous) || 0;
26052:         if (!previousValue) return currentValue ? null : 0;
26053:         return ((currentValue - previousValue) / Math.abs(previousValue)) * 100;
26054:     }
```

### Lines 26369-26389
```text
26369:         const text = String(value || '');
26370:         return text.length <= maximum ? text : `${text.slice(0, Math.max(0, maximum - 1))}…`;
26371:     }
26372: 
26373:     function buildDiscordCategoryBreakdown(entries, prefix, limit) {
26374:         const rows = entries.slice(0, limit);
26375:         if (!rows.length) return 'No entries recorded.';
26376:         return truncateDiscord(rows.map(entry => `• **${escapeDiscordMarkdown(entry.label)}** — ${prefix}${entry.total.toLocaleString('en-GB')} Credits · ${entry.count.toLocaleString('en-GB')} entr${entry.count === 1 ? 'y' : 'ies'}`).join('\n'));
26377:     }
26378: 
26379:     function buildDiscordTopPayouts(report, limit = 5) {
26380:         if (!report.topPayouts.length) return 'No positive payouts recorded.';
26381:         return truncateDiscord(report.topPayouts.slice(0, limit).map((entry, index) => `${index + 1}. **${escapeDiscordMarkdown(entry.description)}** — +${entry.amount.toLocaleString('en-GB')} Credits`).join('\n'));
26382:     }
26383: 
26384:     function buildDiscordComparisonField(report) {
26385:         if (!report.comparison || !report.previous) return 'Comparison disabled.';
26386:         return [
26387:             `Income: **${formatPercentageChange(report.comparison.incomeChange)}**`,
26388:             `Operating result: **${formatPercentageChange(report.comparison.operatingResultChange)}**`,
26389:             `Capital deployed: **${formatPercentageChange(report.comparison.capitalInvestmentChange)}**`,
```

### Lines 26370-26390
```text
26370:         return text.length <= maximum ? text : `${text.slice(0, Math.max(0, maximum - 1))}…`;
26371:     }
26372: 
26373:     function buildDiscordCategoryBreakdown(entries, prefix, limit) {
26374:         const rows = entries.slice(0, limit);
26375:         if (!rows.length) return 'No entries recorded.';
26376:         return truncateDiscord(rows.map(entry => `• **${escapeDiscordMarkdown(entry.label)}** — ${prefix}${entry.total.toLocaleString('en-GB')} Credits · ${entry.count.toLocaleString('en-GB')} entr${entry.count === 1 ? 'y' : 'ies'}`).join('\n'));
26377:     }
26378: 
26379:     function buildDiscordTopPayouts(report, limit = 5) {
26380:         if (!report.topPayouts.length) return 'No positive payouts recorded.';
26381:         return truncateDiscord(report.topPayouts.slice(0, limit).map((entry, index) => `${index + 1}. **${escapeDiscordMarkdown(entry.description)}** — +${entry.amount.toLocaleString('en-GB')} Credits`).join('\n'));
26382:     }
26383: 
26384:     function buildDiscordComparisonField(report) {
26385:         if (!report.comparison || !report.previous) return 'Comparison disabled.';
26386:         return [
26387:             `Income: **${formatPercentageChange(report.comparison.incomeChange)}**`,
26388:             `Operating result: **${formatPercentageChange(report.comparison.operatingResultChange)}**`,
26389:             `Capital deployed: **${formatPercentageChange(report.comparison.capitalInvestmentChange)}**`,
26390:             `Active-hour velocity: **${formatPercentageChange(report.comparison.activeVelocityChange)}**`,
```

### Lines 26371-26391
```text
26371:     }
26372: 
26373:     function buildDiscordCategoryBreakdown(entries, prefix, limit) {
26374:         const rows = entries.slice(0, limit);
26375:         if (!rows.length) return 'No entries recorded.';
26376:         return truncateDiscord(rows.map(entry => `• **${escapeDiscordMarkdown(entry.label)}** — ${prefix}${entry.total.toLocaleString('en-GB')} Credits · ${entry.count.toLocaleString('en-GB')} entr${entry.count === 1 ? 'y' : 'ies'}`).join('\n'));
26377:     }
26378: 
26379:     function buildDiscordTopPayouts(report, limit = 5) {
26380:         if (!report.topPayouts.length) return 'No positive payouts recorded.';
26381:         return truncateDiscord(report.topPayouts.slice(0, limit).map((entry, index) => `${index + 1}. **${escapeDiscordMarkdown(entry.description)}** — +${entry.amount.toLocaleString('en-GB')} Credits`).join('\n'));
26382:     }
26383: 
26384:     function buildDiscordComparisonField(report) {
26385:         if (!report.comparison || !report.previous) return 'Comparison disabled.';
26386:         return [
26387:             `Income: **${formatPercentageChange(report.comparison.incomeChange)}**`,
26388:             `Operating result: **${formatPercentageChange(report.comparison.operatingResultChange)}**`,
26389:             `Capital deployed: **${formatPercentageChange(report.comparison.capitalInvestmentChange)}**`,
26390:             `Active-hour velocity: **${formatPercentageChange(report.comparison.activeVelocityChange)}**`,
26391:             `Mission count: **${report.comparison.missionChange > 0 ? '+' : ''}${report.comparison.missionChange.toLocaleString('en-GB')}**`,
```

### Lines 26440-26460
```text
26440: 
26441:     function discordEmbedCharacterCount(embed) {
26442:         let total = String(embed?.title || '').length + String(embed?.description || '').length + String(embed?.footer?.text || '').length + String(embed?.author?.name || '').length;
26443:         for (const field of embed?.fields || []) total += String(field.name || '').length + String(field.value || '').length;
26444:         return total;
26445:     }
26446: 
26447:     function fitDiscordEmbedsToBudget(embeds, maximum = 5900) {
26448:         const result = embeds.map(embed => ({ ...embed, fields: (embed.fields || []).map(field => ({ ...field })) }));
26449:         const count = () => result.reduce((sum, embed) => sum + discordEmbedCharacterCount(embed), 0);
26450:         const optionalNames = ['🏆 Highest Payouts', '📊 Previous Period', '🔭 Forecast', '🗄️ Archive Coverage'];
26451:         while (count() > maximum && optionalNames.length) {
26452:             const name = optionalNames.shift();
26453:             for (const embed of result) {
26454:                 const index = embed.fields.findIndex(field => field.name === name);
26455:                 if (index >= 0) { embed.fields.splice(index, 1); break; }
26456:             }
26457:         }
26458:         for (const embed of result) {
26459:             embed.description = truncateDiscord(embed.description || '', 3800);
26460:             embed.fields = embed.fields.slice(0, 25).map(field => ({ ...field, name: truncateDiscord(field.name, 256), value: truncateDiscord(field.value, 1000) }));
```

### Lines 26516-26536
```text
26516:         };
26517:         if (withAttachment) executive.image = { url: `attachment://${FINANCE_CHART_FILENAME}` };
26518: 
26519:         const audit = {
26520:             title: '🧠 Audit Intelligence & Capital Strategy',
26521:             color: 0x3498db,
26522:             fields: [
26523:                 { name: '🟢 Income Classification', value: buildDiscordCategoryBreakdown(report.incomeCategories, '+', topLimit), inline: false },
26524:                 { name: '🧾 Operating Expenditure', value: buildDiscordCategoryBreakdown(report.operatingExpenseCategories, '-', topLimit), inline: true },
26525:                 { name: '🏗️ Capital Deployment', value: buildDiscordCategoryBreakdown(report.capitalCategories, '-', topLimit), inline: true },
26526:                 { name: '🏆 Highest Payouts', value: buildDiscordTopPayouts(report, Math.min(5, topLimit)), inline: false },
26527:                 { name: '🔭 Forecast', value: truncateDiscord(buildDiscordForecastField(report)), inline: true },
26528:                 { name: '🗄️ Archive Coverage', value: truncateDiscord(buildDiscordDataQualityField(report)), inline: false }
26529:             ],
26530:             footer: { text: 'Operating performance is separated from capital investment. Forecasts are indicative, not guaranteed.' }
26531:         };
26532: 
26533:         const embeds = fitDiscordEmbedsToBudget(state.discordReport.reportMode === 'executive' ? [executive] : [executive, audit]);
26534:         const payload = {
26535:             username: state.discordReport.webhookName || 'MissionChief Finance',
26536:             allowed_mentions: { parse: [] },
```

### Lines 27876-27896
```text
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
```

## Discord

Occurrences: 151

### Lines 7766-7786
```text
07766:         html[data-mcms-ui-theme] #${SCRIPT.criticalDrawerId} .mcms-critical-row.mcms-age-high .mcms-critical-age-band {
07767:             color: #ffb16f !important;
07768:         }
07769:         html[data-mcms-ui-theme] #${SCRIPT.criticalDrawerId} .mcms-critical-row.mcms-age-critical .mcms-critical-age-band {
07770:             color: #ff8585 !important;
07771:         }
07772:         html[data-mcms-ui-theme] #${SCRIPT.criticalDrawerId} .mcms-critical-age {
07773:             color: #bbdefb !important;
07774:         }
07775: 
07776:         /* Discord reporting: positive green, negative red, neutral amber, busy blue. */
07777:         html[data-mcms-ui-theme] #${SCRIPT.panelId} .mcms-discord-card[data-tone="positive"] {
07778:             border-color: rgba(46,204,113,.68) !important;
07779:             box-shadow: inset 4px 0 #2ecc71, 0 8px 18px rgba(0,0,0,.22) !important;
07780:         }
07781:         html[data-mcms-ui-theme] #${SCRIPT.panelId} .mcms-discord-card[data-tone="negative"] {
07782:             border-color: rgba(231,76,60,.72) !important;
07783:             box-shadow: inset 4px 0 #e74c3c, 0 8px 18px rgba(0,0,0,.22) !important;
07784:         }
07785:         html[data-mcms-ui-theme] #${SCRIPT.panelId} .mcms-discord-card[data-tone="neutral"] {
07786:             border-color: rgba(241,196,15,.66) !important;
```

### Lines 22981-23001
```text
22981:         renderProfiles();
22982:         showToast('Profile deleted');
22983:     }
22984: 
22985:     function settingsBackupFilename(date = new Date()) {
22986:         const pad = value => String(value).padStart(2, '0');
22987:         return `MC Map Command PRIVATE Backup ${date.getFullYear()}-${pad(date.getMonth() + 1)}-${pad(date.getDate())} ${pad(date.getHours())}-${pad(date.getMinutes())}-${pad(date.getSeconds())}.json`;
22988:     }
22989: 
22990:     function buildToolkitSettingsBackup(exportedAt = new Date()) {
22991:         const discordWebhook = getDiscordWebhookUrl();
22992:         const financeIdentity = financeVaultCredential();
22993:         const financialArchiveStore = loadFinanceVaultStore();
22994:         return {
22995:             format: 'MissionChief Map Command Toolkit Private Settings Backup',
22996:             schema: 4,
22997:             version: SCRIPT.version,
22998:             exportedAt: exportedAt.toISOString(),
22999:             state: clonePlainData(state),
23000:             integrations: {
23001:                 discordWebhook,
```

### Lines 22997-23017
```text
22997:             version: SCRIPT.version,
22998:             exportedAt: exportedAt.toISOString(),
22999:             state: clonePlainData(state),
23000:             integrations: {
23001:                 discordWebhook,
23002:                 financialArchiveIdentity: clonePlainData(financeIdentity)
23003:             },
23004:             financialArchiveStore: clonePlainData(financialArchiveStore),
23005:             containsPrivateCredentials: Boolean(discordWebhook),
23006:             containsFinancialHistory: Boolean(financialArchiveStore?.profiles && Object.keys(financialArchiveStore.profiles).length),
23007:             privateCredentialNotice: 'This private backup may contain your Discord webhook token and locally stored MissionChief financial history. Anyone holding it may be able to post through the webhook and inspect the exported game ledger.'
23008:         };
23009:     }
23010: 
23011:     function downloadToolkitSettingsBlob(blob, filename) {
23012:         const urlApi = pageWindow.URL || globalThis.URL;
23013:         const url = urlApi.createObjectURL(blob);
23014:         const link = document.createElement('a');
23015:         link.href = url;
23016:         link.download = filename;
23017:         link.style.display = 'none';
```

### Lines 23017-23037
```text
23017:         link.style.display = 'none';
23018:         document.body.appendChild(link);
23019:         link.click();
23020:         link.remove();
23021:         runtimeSetTimeout(() => urlApi.revokeObjectURL(url), 2500);
23022:     }
23023: 
23024:     async function exportToolkitConfig() {
23025:         try {
23026:             const privateItems = [];
23027:             if (getDiscordWebhookUrl()) privateItems.push('your Discord webhook URL and token');
23028:             if (loadFinanceVaultStore()?.profiles && Object.keys(loadFinanceVaultStore().profiles).length) privateItems.push('your locally stored MissionChief financial history');
23029:             if (privateItems.length) {
23030:                 const accepted = pageWindow.confirm(`PRIVATE BACKUP WARNING
23031: 
23032: This export contains ${privateItems.join(', ')}. Anyone with the file may be able to post to your Discord channel or inspect the exported game ledger.
23033: 
23034: Store it privately and never upload it to a public website or support ticket.
23035: 
23036: Create the private backup now?`);
23037:                 if (!accepted) {
```

### Lines 23022-23042
```text
23022:     }
23023: 
23024:     async function exportToolkitConfig() {
23025:         try {
23026:             const privateItems = [];
23027:             if (getDiscordWebhookUrl()) privateItems.push('your Discord webhook URL and token');
23028:             if (loadFinanceVaultStore()?.profiles && Object.keys(loadFinanceVaultStore().profiles).length) privateItems.push('your locally stored MissionChief financial history');
23029:             if (privateItems.length) {
23030:                 const accepted = pageWindow.confirm(`PRIVATE BACKUP WARNING
23031: 
23032: This export contains ${privateItems.join(', ')}. Anyone with the file may be able to post to your Discord channel or inspect the exported game ledger.
23033: 
23034: Store it privately and never upload it to a public website or support ticket.
23035: 
23036: Create the private backup now?`);
23037:                 if (!accepted) {
23038:                     showToast('Private settings export cancelled');
23039:                     return;
23040:                 }
23041:             }
23042:             const exportedAt = new Date();
```

### Lines 23087-23107
```text
23087:         const candidates = [
23088:             parsed?.state,
23089:             parsed?.settings?.state,
23090:             parsed?.configuration?.state,
23091:             parsed?.configuration,
23092:             parsed
23093:         ];
23094:         return candidates.find(looksLikeToolkitState) || null;
23095:     }
23096: 
23097:     function extractImportedDiscordWebhook(parsed) {
23098:         const containers = [
23099:             parsed?.integrations,
23100:             parsed?.settings?.integrations,
23101:             parsed?.configuration?.integrations
23102:         ];
23103:         for (const container of containers) {
23104:             if (!container || typeof container !== 'object') continue;
23105:             if (Object.prototype.hasOwnProperty.call(container, 'discordWebhook')) {
23106:                 return { present: true, value: String(container.discordWebhook || '') };
23107:             }
```

### Lines 23166-23186
```text
23166:                 name: financeNormaliseText(rawVault?.player?.name).slice(0, 120)
23167:             };
23168:             const key = player.id || player.name ? financePlayerProfileKey(player) : String(rawKey || '').slice(0, 180);
23169:             if (!key) continue;
23170:             profiles[key] = normaliseFinanceVault(rawVault, player, credential.deviceId);
23171:         }
23172:         return { schema: FINANCE_VAULT_SCHEMA, profiles };
23173:     }
23174: 
23175:     function describePrivateImport(parsed) {
23176:         const importedWebhook = extractImportedDiscordWebhook(parsed);
23177:         const importedCredential = extractImportedFinancialVaultCredential(parsed);
23178:         const importedStore = extractImportedFinancialVaultStore(parsed);
23179:         const privateItems = [];
23180:         if (importedWebhook.present && String(importedWebhook.value || '').trim()) privateItems.push('a Discord webhook URL and token');
23181:         if (importedStore.present && Object.keys(importedStore.value?.profiles || {}).length) privateItems.push('stored MissionChief financial ledger history');
23182:         return { importedWebhook, importedCredential, importedStore, privateItems };
23183:     }
23184: 
23185:     function applyImportedToolkitSettings(parsed) {
23186:         const importedState = extractImportedToolkitState(parsed);
```

### Lines 23170-23190
```text
23170:             profiles[key] = normaliseFinanceVault(rawVault, player, credential.deviceId);
23171:         }
23172:         return { schema: FINANCE_VAULT_SCHEMA, profiles };
23173:     }
23174: 
23175:     function describePrivateImport(parsed) {
23176:         const importedWebhook = extractImportedDiscordWebhook(parsed);
23177:         const importedCredential = extractImportedFinancialVaultCredential(parsed);
23178:         const importedStore = extractImportedFinancialVaultStore(parsed);
23179:         const privateItems = [];
23180:         if (importedWebhook.present && String(importedWebhook.value || '').trim()) privateItems.push('a Discord webhook URL and token');
23181:         if (importedStore.present && Object.keys(importedStore.value?.profiles || {}).length) privateItems.push('stored MissionChief financial ledger history');
23182:         return { importedWebhook, importedCredential, importedStore, privateItems };
23183:     }
23184: 
23185:     function applyImportedToolkitSettings(parsed) {
23186:         const importedState = extractImportedToolkitState(parsed);
23187:         if (!importedState) throw new Error('The file does not contain MissionChief Map Command settings.');
23188: 
23189:         const { importedWebhook, importedCredential, importedStore } = describePrivateImport(parsed);
23190:         const normalisedWebhook = importedWebhook.present ? normaliseDiscordWebhookUrl(importedWebhook.value) : '';
```

### Lines 23180-23200
```text
23180:         if (importedWebhook.present && String(importedWebhook.value || '').trim()) privateItems.push('a Discord webhook URL and token');
23181:         if (importedStore.present && Object.keys(importedStore.value?.profiles || {}).length) privateItems.push('stored MissionChief financial ledger history');
23182:         return { importedWebhook, importedCredential, importedStore, privateItems };
23183:     }
23184: 
23185:     function applyImportedToolkitSettings(parsed) {
23186:         const importedState = extractImportedToolkitState(parsed);
23187:         if (!importedState) throw new Error('The file does not contain MissionChief Map Command settings.');
23188: 
23189:         const { importedWebhook, importedCredential, importedStore } = describePrivateImport(parsed);
23190:         const normalisedWebhook = importedWebhook.present ? normaliseDiscordWebhookUrl(importedWebhook.value) : '';
23191:         const normalisedCredential = importedCredential.present ? normaliseImportedFinanceVaultCredential(importedCredential.value) : null;
23192:         const normalisedVaultStore = importedStore.present ? normaliseImportedFinanceVaultStore(importedStore.value) : null;
23193:         const previousStateRaw = localStorage.getItem(SCRIPT.storageState);
23194:         const previousWebhook = getDiscordWebhookUrl();
23195:         const previousCredentialRaw = gmGetValueSafe(SCRIPT.financeVaultCredentialState, null);
23196:         const previousVaultRaw = gmGetValueSafe(SCRIPT.financeVaultState, null);
23197: 
23198:         try {
23199:             localStorage.setItem(SCRIPT.storageState, JSON.stringify(importedState));
23200:             state = loadState();
```

### Lines 23184-23204
```text
23184: 
23185:     function applyImportedToolkitSettings(parsed) {
23186:         const importedState = extractImportedToolkitState(parsed);
23187:         if (!importedState) throw new Error('The file does not contain MissionChief Map Command settings.');
23188: 
23189:         const { importedWebhook, importedCredential, importedStore } = describePrivateImport(parsed);
23190:         const normalisedWebhook = importedWebhook.present ? normaliseDiscordWebhookUrl(importedWebhook.value) : '';
23191:         const normalisedCredential = importedCredential.present ? normaliseImportedFinanceVaultCredential(importedCredential.value) : null;
23192:         const normalisedVaultStore = importedStore.present ? normaliseImportedFinanceVaultStore(importedStore.value) : null;
23193:         const previousStateRaw = localStorage.getItem(SCRIPT.storageState);
23194:         const previousWebhook = getDiscordWebhookUrl();
23195:         const previousCredentialRaw = gmGetValueSafe(SCRIPT.financeVaultCredentialState, null);
23196:         const previousVaultRaw = gmGetValueSafe(SCRIPT.financeVaultState, null);
23197: 
23198:         try {
23199:             localStorage.setItem(SCRIPT.storageState, JSON.stringify(importedState));
23200:             state = loadState();
23201:             saveState();
23202:             if (importedWebhook.present) saveDiscordWebhookUrl(normalisedWebhook);
23203:             if (normalisedCredential) saveFinanceVaultCredential(normalisedCredential);
23204:             if (normalisedVaultStore) saveFinanceVaultStore(normalisedVaultStore);
```

### Lines 23192-23212
```text
23192:         const normalisedVaultStore = importedStore.present ? normaliseImportedFinanceVaultStore(importedStore.value) : null;
23193:         const previousStateRaw = localStorage.getItem(SCRIPT.storageState);
23194:         const previousWebhook = getDiscordWebhookUrl();
23195:         const previousCredentialRaw = gmGetValueSafe(SCRIPT.financeVaultCredentialState, null);
23196:         const previousVaultRaw = gmGetValueSafe(SCRIPT.financeVaultState, null);
23197: 
23198:         try {
23199:             localStorage.setItem(SCRIPT.storageState, JSON.stringify(importedState));
23200:             state = loadState();
23201:             saveState();
23202:             if (importedWebhook.present) saveDiscordWebhookUrl(normalisedWebhook);
23203:             if (normalisedCredential) saveFinanceVaultCredential(normalisedCredential);
23204:             if (normalisedVaultStore) saveFinanceVaultStore(normalisedVaultStore);
23205:             invalidateFinanceVaultMemory();
23206:             loadCachedFinancialRules();
23207:             loadCachedFinancialPolicy();
23208:             applyLoadedConfiguration();
23209:         } catch (err) {
23210:             try {
23211:                 if (previousStateRaw === null) localStorage.removeItem(SCRIPT.storageState);
23212:                 else localStorage.setItem(SCRIPT.storageState, previousStateRaw);
```

### Lines 23204-23224
```text
23204:             if (normalisedVaultStore) saveFinanceVaultStore(normalisedVaultStore);
23205:             invalidateFinanceVaultMemory();
23206:             loadCachedFinancialRules();
23207:             loadCachedFinancialPolicy();
23208:             applyLoadedConfiguration();
23209:         } catch (err) {
23210:             try {
23211:                 if (previousStateRaw === null) localStorage.removeItem(SCRIPT.storageState);
23212:                 else localStorage.setItem(SCRIPT.storageState, previousStateRaw);
23213:                 state = loadState();
23214:                 saveDiscordWebhookUrl(previousWebhook);
23215:                 if (previousCredentialRaw === null) gmDeleteValueSafe(SCRIPT.financeVaultCredentialState);
23216:                 else gmSetValueSafe(SCRIPT.financeVaultCredentialState, previousCredentialRaw);
23217:                 if (previousVaultRaw === null) gmDeleteValueSafe(SCRIPT.financeVaultState);
23218:                 else gmSetValueSafe(SCRIPT.financeVaultState, previousVaultRaw);
23219:                 invalidateFinanceVaultMemory();
23220:                 applyLoadedConfiguration();
23221:             } catch (rollbackError) {}
23222:             throw err;
23223:         }
23224: 
```

### Lines 23234-23254
```text
23234:         if (Number(file.size) > 150 * 1024 * 1024) {
23235:             showToast('Import failed: settings file is too large');
23236:             return;
23237:         }
23238:         const reader = new FileReader();
23239:         reader.onload = () => {
23240:             try {
23241:                 const parsed = JSON.parse(String(reader.result || ''));
23242:                 const privateImport = describePrivateImport(parsed);
23243:                 if (privateImport.privateItems.length) {
23244:                     const accepted = pageWindow.confirm(`PRIVATE BACKUP IMPORT WARNING\n\nThis file contains ${privateImport.privateItems.join(', ')}. Importing it can replace your saved Discord connection, Financial Archive identity or local financial history.\n\nOnly continue if you trust where this backup came from.\n\nImport this private backup now?`);
23245:                     if (!accepted) {
23246:                         showToast('Private settings import cancelled');
23247:                         return;
23248:                     }
23249:                 }
23250:                 const imported = applyImportedToolkitSettings(parsed);
23251:                 const additions = [imported.webhook && 'webhook', imported.credential && 'archive identity', imported.vaultHistory && 'financial history'].filter(Boolean);
23252:                 showToast(additions.length ? `All toolkit settings imported · ${additions.join(', ')}` : 'Toolkit settings imported · existing private integrations kept');
23253:             } catch (err) {
23254:                 showToast(`Import failed: ${err?.message || 'invalid settings file'}`);
```

### Lines 24305-24325
```text
24305:         }
24306: 
24307:         observedCreditsElement = element;
24308:         processCreditTotal(element.textContent);
24309:         creditsValueObserver = runtimeTrackObserver(new MutationObserver(() => processCreditTotal(element.textContent)));
24310:         creditsValueObserver.observe(element, { childList: true, subtree: true, characterData: true });
24311:         return true;
24312:     }
24313: 
24314: 
24315:     // --- Discord Financial Command + local archive --------------------------------------------
24316:     const DISCORD_WEBHOOK_HOSTS = new Set(['discord.com', 'ptb.discord.com', 'canary.discord.com', 'discordapp.com', 'ptb.discordapp.com', 'canary.discordapp.com']);
24317:     const DISCORD_REQUEST_TIMEOUT_MS = 30000;
24318:     const DISCORD_MAX_FIELD_LENGTH = 1024;
24319:     const FINANCE_MAX_LEDGER_PAGES = 5000;
24320:     const FINANCE_FETCH_YIELD_EVERY = 5;
24321:     const FINANCE_SESSION_STARTED_AT = Date.now();
24322:     const FINANCE_PERIOD_IDS = new Set(['today', 'yesterday', 'last24', 'last7', 'last30', 'last90', 'last180', 'last365', 'allAvailable', 'session', 'sinceLast', 'custom']);
24323:     const FINANCE_CHART_FILENAME = 'missionchief-financial-report.png';
24324:     let discordFinanceChartUrl = '';
24325: 
```

### Lines 24936-24956
```text
24936:     }
24937: 
24938:     function buildFinancialArchiveExport(exportedAt = new Date()) {
24939:         return {
24940:             format: 'MissionChief Map Command Financial Archive',
24941:             schema: 2,
24942:             toolkitVersion: SCRIPT.version,
24943:             exportedAt: exportedAt.toISOString(),
24944:             identity: clonePlainData(financeVaultCredential()),
24945:             store: clonePlainData(loadFinanceVaultStore()),
24946:             notice: 'Contains locally stored MissionChief game-financial history. It does not contain the Discord webhook.'
24947:         };
24948:     }
24949: 
24950:     async function exportFinancialArchive() {
24951:         const store = loadFinanceVaultStore();
24952:         if (!Object.keys(store.profiles || {}).length) {
24953:             showToast('No local financial history to export');
24954:             return;
24955:         }
24956:         const accepted = pageWindow.confirm('FINANCIAL ARCHIVE EXPORT\n\nThis file contains your locally stored MissionChief game-financial history. It does not contain your Discord webhook.\n\nCreate the archive file now?');
```

### Lines 24946-24966
```text
24946:             notice: 'Contains locally stored MissionChief game-financial history. It does not contain the Discord webhook.'
24947:         };
24948:     }
24949: 
24950:     async function exportFinancialArchive() {
24951:         const store = loadFinanceVaultStore();
24952:         if (!Object.keys(store.profiles || {}).length) {
24953:             showToast('No local financial history to export');
24954:             return;
24955:         }
24956:         const accepted = pageWindow.confirm('FINANCIAL ARCHIVE EXPORT\n\nThis file contains your locally stored MissionChief game-financial history. It does not contain your Discord webhook.\n\nCreate the archive file now?');
24957:         if (!accepted) return;
24958:         const exportedAt = new Date();
24959:         const json = JSON.stringify(buildFinancialArchiveExport(exportedAt), null, 2);
24960:         const BlobConstructor = pageWindow.Blob || globalThis.Blob;
24961:         downloadToolkitSettingsBlob(new BlobConstructor([json], { type: 'application/json' }), financialArchiveFilename(exportedAt));
24962:         showToast('Financial archive exported');
24963:     }
24964: 
24965:     function mergeFinanceVaultStores(existingStore, importedStore) {
24966:         const result = { schema: FINANCE_VAULT_SCHEMA, profiles: { ...(existingStore?.profiles || {}) } };
```

### Lines 25012-25032
```text
25012:             try {
25013:                 const parsed = JSON.parse(String(reader.result || ''));
25014:                 const importedStore = parsed?.store || parsed?.financialArchiveStore || parsed?.financialVaultStore;
25015:                 if (!importedStore?.profiles || typeof importedStore.profiles !== 'object') throw new Error('No Financial Archive history was found.');
25016:                 if (!pageWindow.confirm('FINANCIAL ARCHIVE IMPORT\n\nThe imported ledger will be merged with the local archive by player ID/name and transaction fingerprint. Existing entries will not be discarded.\n\nContinue?')) return;
25017:                 const merged = mergeFinanceVaultStores(loadFinanceVaultStore(), importedStore);
25018:                 saveFinanceVaultStore(merged);
25019:                 const importedIdentity = parsed?.identity || parsed?.integrations?.financialArchiveIdentity;
25020:                 if (importedIdentity && typeof importedIdentity === 'object') saveFinanceVaultCredential(normaliseImportedFinanceVaultCredential(importedIdentity));
25021:                 renderFinanceVaultStatus();
25022:                 invalidateDiscordFinancialPreview();
25023:                 showToast('Financial archive imported and merged');
25024:             } catch (err) {
25025:                 showToast(`Archive import failed: ${err?.message || 'invalid file'}`);
25026:             }
25027:         };
25028:         reader.onerror = () => showToast('Archive import failed: file could not be read');
25029:         reader.readAsText(file);
25030:     }
25031: 
25032:     function clearFinancialArchive() {
```

### Lines 25033-25053
```text
25033:         const player = financePlayerIdentity({ userId: currentUserIdCached(), userName: financeVaultCredential().playerName });
25034:         const key = financePlayerProfileKey(player);
25035:         const store = loadFinanceVaultStore();
25036:         if (!store.profiles[key]) {
25037:             showToast('No local archive exists for this player');
25038:             return;
25039:         }
25040:         if (!pageWindow.confirm(`Clear the locally stored Financial Archive for ${player.name || `player ${player.id || ''}`}?\n\nThis does not clear MissionChief's own ledger and cannot be undone unless you have an exported backup.`)) return;
25041:         delete store.profiles[key];
25042:         saveFinanceVaultStore(store);
25043:         invalidateDiscordFinancialPreview();
25044:         renderFinanceVaultStatus();
25045:         showToast('Local financial archive cleared');
25046:     }
25047: 
25048:     function cancelFinancialArchiveScan() {
25049:         if (!financeArchiveScanBusy) {
25050:             showToast('No deep financial scan is running');
25051:             return;
25052:         }
25053:         financeArchiveScanCancelled = true;
```

### Lines 25100-25120
```text
25100:     function gmDeleteValueSafe(key) {
25101:         try {
25102:             if (typeof GM_deleteValue === 'function') {
25103:                 GM_deleteValue(key);
25104:                 return true;
25105:             }
25106:         } catch (err) {}
25107:         return false;
25108:     }
25109: 
25110:     function getDiscordWebhookUrl() {
25111:         return String(gmGetValueSafe(SCRIPT.discordWebhookState, '') || '').trim();
25112:     }
25113: 
25114:     function getLastDiscordReportAt() {
25115:         const value = Number(gmGetValueSafe(SCRIPT.discordLastReportState, 0));
25116:         return Number.isFinite(value) && value > 0 ? value : 0;
25117:     }
25118: 
25119:     function normaliseDiscordWebhookUrl(rawValue) {
25120:         const raw = String(rawValue || '').trim();
```

### Lines 25104-25124
```text
25104:                 return true;
25105:             }
25106:         } catch (err) {}
25107:         return false;
25108:     }
25109: 
25110:     function getDiscordWebhookUrl() {
25111:         return String(gmGetValueSafe(SCRIPT.discordWebhookState, '') || '').trim();
25112:     }
25113: 
25114:     function getLastDiscordReportAt() {
25115:         const value = Number(gmGetValueSafe(SCRIPT.discordLastReportState, 0));
25116:         return Number.isFinite(value) && value > 0 ? value : 0;
25117:     }
25118: 
25119:     function normaliseDiscordWebhookUrl(rawValue) {
25120:         const raw = String(rawValue || '').trim();
25121:         if (!raw) return '';
25122:         let parsed;
25123:         try { parsed = new URL(raw); } catch (err) { throw new Error('The Discord webhook URL is not valid.'); }
25124:         if (parsed.protocol !== 'https:' || !DISCORD_WEBHOOK_HOSTS.has(parsed.hostname.toLowerCase())) {
```

## Places

Occurrences: 5

### Lines 18950-18970
```text
18950:         renderBookmarks();
18951:         renderScreenPins();
18952:         updateUI();
18953:         showToast(bookmark.pinned ? 'Shortcut pinned' : 'Shortcut unpinned');
18954:     }
18955: 
18956:     function toggleQuickPin(id) {
18957:         if (!(id in state.quickPins)) return;
18958:         state.quickPins[id] = !state.quickPins[id];
18959:         saveState();
18960:         renderQuickPlaces();
18961:         renderScreenPins();
18962:         updateUI();
18963:         showToast(state.quickPins[id] ? 'Shortcut pinned' : 'Shortcut unpinned');
18964:     }
18965: 
18966:     function loadPayoutHistory() {
18967:         try {
18968:             const parsed = JSON.parse(localStorage.getItem(SCRIPT.payoutHistoryState) || '[]');
18969:             if (!Array.isArray(parsed)) return [];
18970:             return parsed.filter(item => item && Number.isFinite(Number(item.amount)) && Number.isFinite(Number(item.timestamp)))
```

### Lines 22928-22948
```text
22928:         vehicleStatus?.classList.remove('mcms-open');
22929:         vehicleStatus?.setAttribute('aria-hidden', 'true');
22930:         hideMissionInspector();
22931:         missionSpawnArmed = false;
22932:         runtimeClearTimeout(missionSpawnPrimeTimer);
22933:         knownMissionIds.clear();
22934:         if (state.missionSpawn.enabled) primeMissionSpawnDetector();
22935:         if (state.autoLoadAllVehicles) installAutoLoadAllVehicles();
22936:         else stopAutoLoadAllVehicles();
22937:         applyRootAttributes();
22938:         renderQuickPlaces();
22939:         renderBookmarks();
22940:         renderProfiles();
22941:         renderScreenPins();
22942:         updateUI();
22943:         synchroniseVehicleMarkerClasses();
22944:         synchronisePersonalBuildingVisibility();
22945:         reconcileFeatureRefreshes({ includeSnapshots: missionSnapshotsNeeded(), positionPanel: true });
22946:     }
22947: 
22948:     function loadMapProfile(slot) {
```

### Lines 27878-27898
```text
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
```

### Lines 28189-28209
```text
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
```

### Lines 28197-28217
```text
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
```

## Settings

Occurrences: 11

### Lines 22980-23000
```text
22980:         saveState();
22981:         renderProfiles();
22982:         showToast('Profile deleted');
22983:     }
22984: 
22985:     function settingsBackupFilename(date = new Date()) {
22986:         const pad = value => String(value).padStart(2, '0');
22987:         return `MC Map Command PRIVATE Backup ${date.getFullYear()}-${pad(date.getMonth() + 1)}-${pad(date.getDate())} ${pad(date.getHours())}-${pad(date.getMinutes())}-${pad(date.getSeconds())}.json`;
22988:     }
22989: 
22990:     function buildToolkitSettingsBackup(exportedAt = new Date()) {
22991:         const discordWebhook = getDiscordWebhookUrl();
22992:         const financeIdentity = financeVaultCredential();
22993:         const financialArchiveStore = loadFinanceVaultStore();
22994:         return {
22995:             format: 'MissionChief Map Command Toolkit Private Settings Backup',
22996:             schema: 4,
22997:             version: SCRIPT.version,
22998:             exportedAt: exportedAt.toISOString(),
22999:             state: clonePlainData(state),
23000:             integrations: {
```

### Lines 22985-23005
```text
22985:     function settingsBackupFilename(date = new Date()) {
22986:         const pad = value => String(value).padStart(2, '0');
22987:         return `MC Map Command PRIVATE Backup ${date.getFullYear()}-${pad(date.getMonth() + 1)}-${pad(date.getDate())} ${pad(date.getHours())}-${pad(date.getMinutes())}-${pad(date.getSeconds())}.json`;
22988:     }
22989: 
22990:     function buildToolkitSettingsBackup(exportedAt = new Date()) {
22991:         const discordWebhook = getDiscordWebhookUrl();
22992:         const financeIdentity = financeVaultCredential();
22993:         const financialArchiveStore = loadFinanceVaultStore();
22994:         return {
22995:             format: 'MissionChief Map Command Toolkit Private Settings Backup',
22996:             schema: 4,
22997:             version: SCRIPT.version,
22998:             exportedAt: exportedAt.toISOString(),
22999:             state: clonePlainData(state),
23000:             integrations: {
23001:                 discordWebhook,
23002:                 financialArchiveIdentity: clonePlainData(financeIdentity)
23003:             },
23004:             financialArchiveStore: clonePlainData(financialArchiveStore),
23005:             containsPrivateCredentials: Boolean(discordWebhook),
```

### Lines 23001-23021
```text
23001:                 discordWebhook,
23002:                 financialArchiveIdentity: clonePlainData(financeIdentity)
23003:             },
23004:             financialArchiveStore: clonePlainData(financialArchiveStore),
23005:             containsPrivateCredentials: Boolean(discordWebhook),
23006:             containsFinancialHistory: Boolean(financialArchiveStore?.profiles && Object.keys(financialArchiveStore.profiles).length),
23007:             privateCredentialNotice: 'This private backup may contain your Discord webhook token and locally stored MissionChief financial history. Anyone holding it may be able to post through the webhook and inspect the exported game ledger.'
23008:         };
23009:     }
23010: 
23011:     function downloadToolkitSettingsBlob(blob, filename) {
23012:         const urlApi = pageWindow.URL || globalThis.URL;
23013:         const url = urlApi.createObjectURL(blob);
23014:         const link = document.createElement('a');
23015:         link.href = url;
23016:         link.download = filename;
23017:         link.style.display = 'none';
23018:         document.body.appendChild(link);
23019:         link.click();
23020:         link.remove();
23021:         runtimeSetTimeout(() => urlApi.revokeObjectURL(url), 2500);
```

### Lines 23034-23054
```text
23034: Store it privately and never upload it to a public website or support ticket.
23035: 
23036: Create the private backup now?`);
23037:                 if (!accepted) {
23038:                     showToast('Private settings export cancelled');
23039:                     return;
23040:                 }
23041:             }
23042:             const exportedAt = new Date();
23043:             const filename = settingsBackupFilename(exportedAt);
23044:             const json = JSON.stringify(buildToolkitSettingsBackup(exportedAt), null, 2);
23045:             const BlobConstructor = pageWindow.Blob || globalThis.Blob;
23046:             const FileConstructor = pageWindow.File || globalThis.File;
23047:             const blob = new BlobConstructor([json], { type: 'application/json' });
23048:             const shareNavigator = pageWindow.navigator || globalThis.navigator;
23049: 
23050:             if (activeDeviceLayout === 'mobile' && typeof FileConstructor === 'function' && typeof shareNavigator?.share === 'function') {
23051:                 const file = new FileConstructor([json], filename, { type: 'application/json' });
23052:                 let canShareFile = false;
23053:                 try {
23054:                     canShareFile = typeof shareNavigator.canShare !== 'function' || shareNavigator.canShare({ files: [file] });
```

### Lines 23056-23076
```text
23056:                 if (canShareFile) {
23057:                     try {
23058:                         await shareNavigator.share({
23059:                             files: [file],
23060:                             title: 'MC Map Command private settings backup'
23061:                         });
23062:                         showToast('All toolkit settings exported');
23063:                         return;
23064:                     } catch (err) {
23065:                         if (err?.name === 'AbortError') {
23066:                             showToast('Settings export cancelled');
23067:                             return;
23068:                         }
23069:                     }
23070:                 }
23071:             }
23072: 
23073:             downloadToolkitSettingsBlob(blob, filename);
23074:             showToast('All toolkit settings exported');
23075:         } catch (err) {
23076:             showToast('Export failed: settings file could not be created');
```

### Lines 23063-23083
```text
23063:                         return;
23064:                     } catch (err) {
23065:                         if (err?.name === 'AbortError') {
23066:                             showToast('Settings export cancelled');
23067:                             return;
23068:                         }
23069:                     }
23070:                 }
23071:             }
23072: 
23073:             downloadToolkitSettingsBlob(blob, filename);
23074:             showToast('All toolkit settings exported');
23075:         } catch (err) {
23076:             showToast('Export failed: settings file could not be created');
23077:         }
23078:     }
23079: 
23080:     function looksLikeToolkitState(value) {
23081:         if (!value || typeof value !== 'object' || Array.isArray(value)) return false;
23082:         return ['theme', 'position', 'visibility', 'bookmarks', 'profiles', 'payoutFlash', 'tabletMode', 'mobileMode']
23083:             .some(key => Object.prototype.hasOwnProperty.call(value, key));
```

### Lines 23175-23195
```text
23175:     function describePrivateImport(parsed) {
23176:         const importedWebhook = extractImportedDiscordWebhook(parsed);
23177:         const importedCredential = extractImportedFinancialVaultCredential(parsed);
23178:         const importedStore = extractImportedFinancialVaultStore(parsed);
23179:         const privateItems = [];
23180:         if (importedWebhook.present && String(importedWebhook.value || '').trim()) privateItems.push('a Discord webhook URL and token');
23181:         if (importedStore.present && Object.keys(importedStore.value?.profiles || {}).length) privateItems.push('stored MissionChief financial ledger history');
23182:         return { importedWebhook, importedCredential, importedStore, privateItems };
23183:     }
23184: 
23185:     function applyImportedToolkitSettings(parsed) {
23186:         const importedState = extractImportedToolkitState(parsed);
23187:         if (!importedState) throw new Error('The file does not contain MissionChief Map Command settings.');
23188: 
23189:         const { importedWebhook, importedCredential, importedStore } = describePrivateImport(parsed);
23190:         const normalisedWebhook = importedWebhook.present ? normaliseDiscordWebhookUrl(importedWebhook.value) : '';
23191:         const normalisedCredential = importedCredential.present ? normaliseImportedFinanceVaultCredential(importedCredential.value) : null;
23192:         const normalisedVaultStore = importedStore.present ? normaliseImportedFinanceVaultStore(importedStore.value) : null;
23193:         const previousStateRaw = localStorage.getItem(SCRIPT.storageState);
23194:         const previousWebhook = getDiscordWebhookUrl();
23195:         const previousCredentialRaw = gmGetValueSafe(SCRIPT.financeVaultCredentialState, null);
```

### Lines 23240-23260
```text
23240:             try {
23241:                 const parsed = JSON.parse(String(reader.result || ''));
23242:                 const privateImport = describePrivateImport(parsed);
23243:                 if (privateImport.privateItems.length) {
23244:                     const accepted = pageWindow.confirm(`PRIVATE BACKUP IMPORT WARNING\n\nThis file contains ${privateImport.privateItems.join(', ')}. Importing it can replace your saved Discord connection, Financial Archive identity or local financial history.\n\nOnly continue if you trust where this backup came from.\n\nImport this private backup now?`);
23245:                     if (!accepted) {
23246:                         showToast('Private settings import cancelled');
23247:                         return;
23248:                     }
23249:                 }
23250:                 const imported = applyImportedToolkitSettings(parsed);
23251:                 const additions = [imported.webhook && 'webhook', imported.credential && 'archive identity', imported.vaultHistory && 'financial history'].filter(Boolean);
23252:                 showToast(additions.length ? `All toolkit settings imported · ${additions.join(', ')}` : 'Toolkit settings imported · existing private integrations kept');
23253:             } catch (err) {
23254:                 showToast(`Import failed: ${err?.message || 'invalid settings file'}`);
23255:             }
23256:         };
23257:         reader.onerror = () => showToast('Import failed: file could not be read');
23258:         reader.readAsText(file);
23259:     }
23260: 
```

### Lines 24951-24971
```text
24951:         const store = loadFinanceVaultStore();
24952:         if (!Object.keys(store.profiles || {}).length) {
24953:             showToast('No local financial history to export');
24954:             return;
24955:         }
24956:         const accepted = pageWindow.confirm('FINANCIAL ARCHIVE EXPORT\n\nThis file contains your locally stored MissionChief game-financial history. It does not contain your Discord webhook.\n\nCreate the archive file now?');
24957:         if (!accepted) return;
24958:         const exportedAt = new Date();
24959:         const json = JSON.stringify(buildFinancialArchiveExport(exportedAt), null, 2);
24960:         const BlobConstructor = pageWindow.Blob || globalThis.Blob;
24961:         downloadToolkitSettingsBlob(new BlobConstructor([json], { type: 'application/json' }), financialArchiveFilename(exportedAt));
24962:         showToast('Financial archive exported');
24963:     }
24964: 
24965:     function mergeFinanceVaultStores(existingStore, importedStore) {
24966:         const result = { schema: FINANCE_VAULT_SCHEMA, profiles: { ...(existingStore?.profiles || {}) } };
24967:         for (const [rawKey, rawVault] of Object.entries(importedStore?.profiles || {}).slice(0, 100)) {
24968:             if (!rawVault || typeof rawVault !== 'object') continue;
24969:             const player = {
24970:                 id: rawVault?.player?.id === undefined || rawVault?.player?.id === null || rawVault?.player?.id === '' ? null : String(rawVault.player.id).slice(0, 64),
24971:                 name: financeNormaliseText(rawVault?.player?.name).slice(0, 120)
```

### Lines 27879-27899
```text
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
```

### Lines 28092-28112
```text
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
```

## Navigation and responsive-layout anchors

### Lines 1372-1382
```text
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
```

### Lines 1463-1473
```text
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
```

### Lines 1464-1474
```text
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
```

### Lines 2134-2144
```text
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
```

### Lines 2136-2146
```text
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
```

### Lines 2152-2162
```text
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
```

### Lines 2203-2213
```text
02203:         @keyframes mcmsIntelLabel { 0%{opacity:0;transform:translateX(-50%) translateY(6px)} 18%,76%{opacity:1;transform:translateX(-50%) translateY(0)} 100%{opacity:0;transform:translateX(-50%) translateY(-2px)} }
02204:         @keyframes mcmsIntelMarkerPulse { 0%,20%,100%{filter:brightness(1)} 38%{filter:drop-shadow(0 0 7px var(--mcms-lock-secondary,#fff)) drop-shadow(0 0 15px var(--mcms-lock-primary,#67d9ff)) brightness(1.45)} 58%{filter:drop-shadow(0 0 5px var(--mcms-lock-primary,#67d9ff)) brightness(1.16)} 74%{filter:drop-shadow(0 0 9px var(--mcms-lock-primary,#67d9ff)) brightness(1.3)} }
02205: 
02206: 
02207: 
02208:         @media (prefers-reduced-motion:reduce) {
02209:             .mcms-mission-lock-travel-overlay,
02210:             .mcms-mission-lock-travel-overlay::before,
02211:             .mcms-mission-lock-travel-overlay::after,
02212:             .mcms-mission-lock-beam,
02213:             .mcms-mission-lock-reticle,
```

### Lines 2296-2306
```text
02296: 
02297:         html[data-mcms-command-bar-open="false"] #${SCRIPT.controlId} .mcms-floating-filter,
02298:         html[data-mcms-command-bar-open="false"] #${SCRIPT.controlId} .mcms-screen-pins { display: none !important; }
02299: 
02300:         #${SCRIPT.controlId} .mcms-floating-filter {
02301:             display: grid !important; grid-template-columns: repeat(2, 82px) !important; gap: 4px !important; margin-top: 6px !important; width: 168px !important;
02302:         }
02303:         #${SCRIPT.panelId} .mcms-grid-2 [data-toggle="criticalView"] {
02304:             grid-column: 1 / -1 !important;
02305:         }
02306:         #${SCRIPT.controlId} .mcms-float-btn, #${SCRIPT.controlId} .mcms-screen-pin-btn {
```

### Lines 2308-2318
```text
02308:             cursor: pointer !important; font-size: 8.5px !important; line-height: 1 !important; font-weight: 900 !important;
02309:             box-shadow: 0 3px 10px rgba(0,0,0,.25) !important; backdrop-filter: blur(6px) !important;
02310:         }
02311:         #${SCRIPT.controlId} .mcms-float-btn {
02312:             height: 29px !important; background: rgba(10,14,20,.78) !important; padding: 0 5px !important;
02313:             display: grid !important; grid-template-columns: 17px minmax(0,1fr) !important; align-items: center !important; gap: 5px !important;
02314:             text-align: left !important; overflow: hidden !important;
02315:         }
02316:         #${SCRIPT.controlId} .mcms-float-key {
02317:             width: 17px !important; height: 17px !important; border-radius: 6px !important; background: rgba(255,255,255,.12) !important;
02318:             display: flex !important; align-items: center !important; justify-content: center !important; color: #fff !important;
```

### Lines 2317-2327
```text
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
```

### Lines 2325-2335
```text
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
```

### Lines 2330-2340
```text
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
```

### Lines 2383-2393
```text
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
```

### Lines 2386-2396
```text
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
```

### Lines 2391-2401
```text
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
```

### Lines 2404-2414
```text
02404:             padding-right: 2px !important;
02405:         }
02406:         #${SCRIPT.panelId}.mcms-dragging { opacity: .96 !important; cursor: grabbing !important; }
02407: 
02408:         #${SCRIPT.panelId} .mcms-header {
02409:             display: grid !important; grid-template-columns: minmax(0, 1fr) 24px 24px 24px !important; align-items: center !important; gap: 7px !important;
02410:             margin: 0 0 8px 0 !important; padding: 0 0 7px 0 !important; border-bottom: 1px solid rgba(255,255,255,.12) !important; overflow: hidden !important;
02411:         }
02412:         #${SCRIPT.panelId} .mcms-drag-handle {
02413:             min-width: 0 !important; cursor: grab !important; touch-action: none !important; user-select: none !important;
02414:             border-radius: 9px !important; padding: 4px 6px !important; background: rgba(255,255,255,.055) !important; border: 1px solid rgba(255,255,255,.075) !important;
```

### Lines 2413-2423
```text
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
```

### Lines 2414-2424
```text
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
```

### Lines 2420-2430
```text
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
```

### Lines 2421-2431
```text
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
```

### Lines 2422-2432
```text
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
```

### Lines 2423-2433
```text
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
```

### Lines 2424-2434
```text
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
```

### Lines 2425-2435
```text
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
```

### Lines 2429-2439
```text
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
```

### Lines 2434-2444
```text
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
```

### Lines 2435-2445
```text
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
```

### Lines 2436-2446
```text
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
```

### Lines 2437-2447
```text
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
```

### Lines 2438-2448
```text
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
```

### Lines 2441-2451
```text
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
```

### Lines 2442-2452
```text
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
```

### Lines 2445-2455
```text
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
```

### Lines 2446-2456
```text
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
```

### Lines 2447-2457
```text
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
```

### Lines 2450-2460
```text
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
```

### Lines 2460-2470
```text
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
```

### Lines 2461-2471
```text
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
```

### Lines 2464-2474
```text
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
```

### Lines 2465-2475
```text
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
```

### Lines 2469-2479
```text
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
```

### Lines 2470-2480
```text
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
```

### Lines 2475-2485
```text
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
```

### Lines 2477-2487
```text
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
```

### Lines 2479-2489
```text
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
```

### Lines 2480-2490
```text
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
```

### Lines 2481-2491
```text
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
```

### Lines 2483-2493
```text
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
```

### Lines 2490-2500
```text
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
```

### Lines 2495-2505
```text
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
```

### Lines 2497-2507
```text
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
```

### Lines 2499-2509
```text
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
```

### Lines 2500-2510
```text
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
```

### Lines 2501-2511
```text
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
```

### Lines 2504-2514
```text
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
```

### Lines 2528-2538
```text
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
```

### Lines 2600-2610
```text
02600:         .mcms-transport-watcher-badge.mcms-transport-patient { border-color: rgba(255,194,71,.96) !important; color:#fff1c7 !important; }
02601:         .mcms-transport-watcher-badge.mcms-transport-prisoner { border-color: rgba(255,139,53,.98) !important; color:#ffd0a5 !important; background:linear-gradient(145deg,rgba(91,35,4,.97),rgba(28,12,4,.97)) !important; }
02602:         .mcms-transport-watcher-count { position:absolute !important; right:-7px !important; top:-7px !important; min-width:15px !important; height:15px !important; padding:0 3px !important; border-radius:999px !important; border:1px solid rgba(255,255,255,.86) !important; background:#e67600 !important; color:#fff !important; font:950 8px/13px Arial,Helvetica,sans-serif !important; text-align:center !important; box-shadow:0 1px 4px rgba(0,0,0,.65) !important; }
02603:         .mcms-transport-watcher-badge.mcms-transport-side-left .mcms-transport-watcher-count { left:-7px !important; right:auto !important; }
02604:         @keyframes mcmsTransportWatcherPulse { 0%,100%{transform:translate(-50%,-50%) scale(1);box-shadow:0 0 0 2px rgba(0,0,0,.48),0 0 8px rgba(255,145,24,.38)} 50%{transform:translate(-50%,-50%) scale(1.08);box-shadow:0 0 0 2px rgba(0,0,0,.55),0 0 16px rgba(255,145,24,.82)} }
02605:         @media (prefers-reduced-motion: reduce) { .mcms-transport-watcher-badge { animation:none !important; } }
02606: 
02607:         .mcms-resource-gap-badge {
02608:             min-width: 31px !important; height: 19px !important; padding: 0 6px !important; border-radius: 7px !important;
02609:             border: 1px solid rgba(255,146,49,.88) !important; background: rgba(48,20,3,.91) !important; color: #ffd29a !important;
02610:             box-shadow: 0 0 0 2px rgba(0,0,0,.38), 0 2px 8px rgba(255,112,20,.27) !important;
```

### Lines 2612-2622
```text
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
```

### Lines 2613-2623
```text
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
```

### Lines 2616-2626
```text
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
```

### Lines 2623-2633
```text
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
```

### Lines 2626-2636
```text
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
```

### Lines 2630-2640
```text
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
```

### Lines 2631-2641
```text
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
```

### Lines 2632-2642
```text
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
```

### Lines 2662-2672
```text
02662:             backdrop-filter:blur(10px) !important; -webkit-backdrop-filter:blur(10px) !important;
02663:             font-family:Arial,Helvetica,sans-serif !important;
02664:         }
02665:         #${SCRIPT.criticalDrawerId}.mcms-open { display:block !important; }
02666:         #${SCRIPT.criticalDrawerId}, #${SCRIPT.criticalDrawerId} * { box-sizing:border-box !important; }
02667:         #${SCRIPT.criticalDrawerId} .mcms-drawer-head { display:grid !important; grid-template-columns:minmax(0,1fr) 28px !important; gap:8px !important; align-items:center !important; padding-bottom:8px !important; border-bottom:1px solid rgba(255,255,255,.12) !important; }
02668:         #${SCRIPT.criticalDrawerId} .mcms-drawer-title { font-size:13px !important; font-weight:950 !important; letter-spacing:.3px !important; }
02669:         #${SCRIPT.criticalDrawerId} .mcms-drawer-subtitle { display:block !important; margin-top:2px !important; color:rgba(255,255,255,.58) !important; font-size:8px !important; font-weight:800 !important; }
02670:         #${SCRIPT.criticalDrawerId} .mcms-drawer-close { width:28px !important; height:28px !important; border:0 !important; border-radius:8px !important; background:rgba(255,255,255,.10) !important; color:#fff !important; cursor:pointer !important; font-weight:900 !important; }
02671:         #${SCRIPT.criticalDrawerId} .mcms-drawer-list { display:grid !important; gap:6px !important; margin-top:8px !important; }
02672:         #${SCRIPT.criticalDrawerId} .mcms-critical-row { width:100% !important; display:grid !important; grid-template-columns:86px minmax(0,1fr) auto !important; gap:7px !important; align-items:center !important; padding:8px !important; border-radius:9px !important; border:1px solid rgba(255,255,255,.11) !important; background:rgba(255,255,255,.05) !important; color:#fff !important; cursor:pointer !important; text-align:left !important; }
```

### Lines 2667-2677
```text
02667:         #${SCRIPT.criticalDrawerId} .mcms-drawer-head { display:grid !important; grid-template-columns:minmax(0,1fr) 28px !important; gap:8px !important; align-items:center !important; padding-bottom:8px !important; border-bottom:1px solid rgba(255,255,255,.12) !important; }
02668:         #${SCRIPT.criticalDrawerId} .mcms-drawer-title { font-size:13px !important; font-weight:950 !important; letter-spacing:.3px !important; }
02669:         #${SCRIPT.criticalDrawerId} .mcms-drawer-subtitle { display:block !important; margin-top:2px !important; color:rgba(255,255,255,.58) !important; font-size:8px !important; font-weight:800 !important; }
02670:         #${SCRIPT.criticalDrawerId} .mcms-drawer-close { width:28px !important; height:28px !important; border:0 !important; border-radius:8px !important; background:rgba(255,255,255,.10) !important; color:#fff !important; cursor:pointer !important; font-weight:900 !important; }
02671:         #${SCRIPT.criticalDrawerId} .mcms-drawer-list { display:grid !important; gap:6px !important; margin-top:8px !important; }
02672:         #${SCRIPT.criticalDrawerId} .mcms-critical-row { width:100% !important; display:grid !important; grid-template-columns:86px minmax(0,1fr) auto !important; gap:7px !important; align-items:center !important; padding:8px !important; border-radius:9px !important; border:1px solid rgba(255,255,255,.11) !important; background:rgba(255,255,255,.05) !important; color:#fff !important; cursor:pointer !important; text-align:left !important; }
02673:         #${SCRIPT.criticalDrawerId} .mcms-critical-row:hover { background:rgba(255,255,255,.11) !important; }
02674:         #${SCRIPT.criticalDrawerId} .mcms-critical-row.mcms-age-aged { border-color:rgba(255,183,77,.34) !important; }
02675:         #${SCRIPT.criticalDrawerId} .mcms-critical-row.mcms-age-high { border-color:rgba(255,112,67,.48) !important; background:rgba(68,24,8,.18) !important; }
02676:         #${SCRIPT.criticalDrawerId} .mcms-critical-row.mcms-age-critical { border-color:rgba(255,82,82,.62) !important; background:rgba(88,12,12,.32) !important; }
02677:         #${SCRIPT.criticalDrawerId} .mcms-critical-age-band { color:#ffb74d !important; font-size:8px !important; font-weight:950 !important; letter-spacing:.45px !important; white-space:nowrap !important; text-transform:uppercase !important; }
```

### Lines 2672-2682
```text
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
```

### Lines 2674-2684
```text
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
```

### Lines 2676-2686
```text
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
```

### Lines 2737-2747
```text
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
```

### Lines 2770-2780
```text
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
```

### Lines 2788-2798
```text
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
```

### Lines 2990-3000
```text
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
```

### Lines 3007-3017
```text
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
```

### Lines 3048-3058
```text
03048:             font-family: Impact, Haettenschweiler, "Arial Narrow Bold", sans-serif !important;
03049:             font-size: clamp(23px, 3.25vw, 35px) !important;
03050:             letter-spacing: 2px !important;
03051:             text-shadow: 2px 2px 0 #11140e, 0 0 14px rgba(255,126,17,.36), 0 0 28px rgba(255,78,4,.12) !important;
03052:         }
03053:         @media (max-width: 620px) {
03054:             #${SCRIPT.payoutFlashId}[data-template="badCompany"] .mcms-payout-banner {
03055:                 width: calc(100% - 16px) !important;
03056:                 padding: 21px 16px 19px !important;
03057:             }
03058:             #${SCRIPT.payoutFlashId}[data-template="badCompany"] .mcms-payout-title {
```

### Lines 3060-3070
```text
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
```

### Lines 3202-3212
```text
03202:             border-radius:0 !important;
03203:             background:#f5e8be !important;
03204:             box-shadow:0 0 5px #fff7d7,0 0 12px rgba(218,176,79,.78) !important;
03205:             transform:rotate(45deg);
03206:         }
03207:         @media (max-width:620px) {
03208:             #${SCRIPT.payoutFlashId}[data-template="scarface"] .mcms-payout-banner {
03209:                 width:calc(100% - 16px) !important; padding:25px 19px 21px !important;
03210:                 background:linear-gradient(90deg,rgba(5,5,5,.985) 0 76%,rgba(234,228,215,.97) 76% 100%) !important;
03211:             }
03212:             #${SCRIPT.payoutFlashId}[data-template="scarface"] .mcms-payout-title {
```

### Lines 3610-3620
```text
03610:             border-radius: 1px !important;
03611:             background: #ffb24d !important;
03612:             box-shadow: 0 0 5px #ff7a22, 0 0 10px rgba(255,123,35,.62) !important;
03613:         }
03614: 
03615:         @media (max-width:620px) {
03616:             #${SCRIPT.payoutFlashId}[data-template]:not([data-template="wasteland"]) .mcms-payout-banner::before,
03617:             #${SCRIPT.payoutFlashId}[data-template]:not([data-template="wasteland"]) .mcms-payout-banner::after {font-size:6px !important;letter-spacing:.8px !important;}
03618:             #${SCRIPT.payoutFlashId}[data-template="gta5"] .mcms-payout-banner,
03619:             #${SCRIPT.payoutFlashId}[data-template="cyberpunk"] .mcms-payout-banner,
03620:             #${SCRIPT.payoutFlashId}[data-template="factorio"] .mcms-payout-banner,
```

### Lines 3621-3631
```text
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
```

### Lines 3628-3638
```text
03628:         #${SCRIPT.payoutFlashId}[data-template="viceCity"] .mcms-payout-title.mcms-payout-title-very-long { font-size:clamp(29px,4.6vw,52px) !important; line-height:.93 !important; transform:rotate(-1deg) skewX(-4deg) scaleX(.94) !important; }
03629:         #${SCRIPT.payoutFlashId}[data-template="darkFantasy"] .mcms-payout-title.mcms-payout-title-long,
03630:         #${SCRIPT.payoutFlashId}[data-template="underworld"] .mcms-payout-title.mcms-payout-title-long { transform:none !important; }
03631:         #${SCRIPT.payoutFlashId}[data-template="darkFantasy"] .mcms-payout-title.mcms-payout-title-very-long,
03632:         #${SCRIPT.payoutFlashId}[data-template="underworld"] .mcms-payout-title.mcms-payout-title-very-long { transform:none !important; }
03633:         @media (max-width:620px) {
03634:             #${SCRIPT.payoutFlashId}[data-template="cyberpunk"] .mcms-payout-banner,
03635:             #${SCRIPT.payoutFlashId}[data-template="hellfire"] .mcms-payout-banner,
03636:             #${SCRIPT.payoutFlashId}[data-template="wasteland"] .mcms-payout-banner,
03637:             #${SCRIPT.payoutFlashId}[data-template="galactic"] .mcms-payout-banner,
03638:             #${SCRIPT.payoutFlashId}[data-template="darkFantasy"] .mcms-payout-banner,
```

### Lines 3653-3663
```text
03653:             0% { opacity: 0; transform: translate(-50%, -44%) scale(1.08); filter: blur(8px); }
03654:             5% { opacity: 1; transform: translate(-50%, -50%) scale(1); filter: blur(0); }
03655:             94% { opacity: 1; transform: translate(-50%, -50%) scale(1); filter: blur(0); }
03656:             100% { opacity: 0; transform: translate(-50%, -56%) scale(.985); filter: blur(2px); }
03657:         }
03658:         @media (prefers-reduced-motion: reduce) {
03659:             #${SCRIPT.payoutFlashId}.mcms-payout-active .mcms-payout-light {
03660:                 animation: none !important; opacity: .24 !important;
03661:             }
03662:             #${SCRIPT.payoutFlashId}.mcms-payout-active .mcms-payout-banner {
03663:                 animation: mcmsPayoutBannerReduced var(--mcms-payout-duration, 3000ms) ease-out both !important;
```

### Lines 3670-3680
```text
03670: 
03671:         #${SCRIPT.toastId} { position: fixed !important; left: 12px !important; bottom: 14px !important; z-index: 982 !important; max-width: 280px !important; padding: 6px 9px !important; border-radius: 9px !important; border: 1px solid rgba(255,255,255,.14) !important; background: rgba(10,14,20,.92) !important; color: #fff !important; font: 900 10px/1.15 Arial, Helvetica, sans-serif !important; opacity: 0 !important; transform: translateY(4px) !important; pointer-events: none !important; transition: opacity 140ms ease, transform 140ms ease !important; box-shadow: 0 5px 14px rgba(0,0,0,.28) !important; }
03672:         #${SCRIPT.toastId}.mcms-flash { opacity: 1 !important; transform: translateY(0) !important; }
03673:         #${SCRIPT.panelId}.mcms-map-small { width: 292px !important; }
03674:         #${SCRIPT.panelId}.mcms-map-small .mcms-grid-2 { gap: 6px !important; }
03675:         #${SCRIPT.panelId}.mcms-map-small .mcms-theme-btn, #${SCRIPT.panelId}.mcms-map-small .mcms-toggle-btn, #${SCRIPT.panelId}.mcms-map-small .mcms-place-main { height: 40px !important; padding: 5px !important; grid-template-columns: 18px minmax(0,1fr) !important; gap: 5px !important; }
03676:         #${SCRIPT.panelId}.mcms-map-small .mcms-iconbox { width: 18px !important; height: 18px !important; min-width: 18px !important; font-size: 9px !important; }
03677:         #${SCRIPT.panelId}.mcms-map-small .mcms-label { font-size: 10px !important; }
03678:         #${SCRIPT.panelId}.mcms-map-small .mcms-footer { display: none !important; }
03679: 
03680: 
```

### Lines 3678-3688
```text
03678:         #${SCRIPT.panelId}.mcms-map-small .mcms-footer { display: none !important; }
03679: 
03680: 
03681:         /* v3.3.0 Tablet Mode: map-aware responsive dock, unmistakable enabled states, fitted labels and bottom-sheet panel,
03682:            low-overhead rendering and safe-area aware spacing. */
03683:         html[data-mcms-tablet-active="true"] #${SCRIPT.controlId},
03684:         html[data-mcms-tablet-active="true"] #${SCRIPT.panelId},
03685:         html[data-mcms-tablet-active="true"] #${SCRIPT.criticalDrawerId} {
03686:             -webkit-tap-highlight-color: transparent !important;
03687:         }
03688:         html[data-mcms-tablet-active="true"] #${SCRIPT.controlId} button,
```

### Lines 3679-3689
```text
03679: 
03680: 
03681:         /* v3.3.0 Tablet Mode: map-aware responsive dock, unmistakable enabled states, fitted labels and bottom-sheet panel,
03682:            low-overhead rendering and safe-area aware spacing. */
03683:         html[data-mcms-tablet-active="true"] #${SCRIPT.controlId},
03684:         html[data-mcms-tablet-active="true"] #${SCRIPT.panelId},
03685:         html[data-mcms-tablet-active="true"] #${SCRIPT.criticalDrawerId} {
03686:             -webkit-tap-highlight-color: transparent !important;
03687:         }
03688:         html[data-mcms-tablet-active="true"] #${SCRIPT.controlId} button,
03689:         html[data-mcms-tablet-active="true"] #${SCRIPT.panelId} button,
```

### Lines 3680-3690
```text
03680: 
03681:         /* v3.3.0 Tablet Mode: map-aware responsive dock, unmistakable enabled states, fitted labels and bottom-sheet panel,
03682:            low-overhead rendering and safe-area aware spacing. */
03683:         html[data-mcms-tablet-active="true"] #${SCRIPT.controlId},
03684:         html[data-mcms-tablet-active="true"] #${SCRIPT.panelId},
03685:         html[data-mcms-tablet-active="true"] #${SCRIPT.criticalDrawerId} {
03686:             -webkit-tap-highlight-color: transparent !important;
03687:         }
03688:         html[data-mcms-tablet-active="true"] #${SCRIPT.controlId} button,
03689:         html[data-mcms-tablet-active="true"] #${SCRIPT.panelId} button,
03690:         html[data-mcms-tablet-active="true"] #${SCRIPT.panelId} input,
```

### Lines 3683-3693
```text
03683:         html[data-mcms-tablet-active="true"] #${SCRIPT.controlId},
03684:         html[data-mcms-tablet-active="true"] #${SCRIPT.panelId},
03685:         html[data-mcms-tablet-active="true"] #${SCRIPT.criticalDrawerId} {
03686:             -webkit-tap-highlight-color: transparent !important;
03687:         }
03688:         html[data-mcms-tablet-active="true"] #${SCRIPT.controlId} button,
03689:         html[data-mcms-tablet-active="true"] #${SCRIPT.panelId} button,
03690:         html[data-mcms-tablet-active="true"] #${SCRIPT.panelId} input,
03691:         html[data-mcms-tablet-active="true"] #${SCRIPT.panelId} select,
03692:         html[data-mcms-tablet-active="true"] #${SCRIPT.criticalDrawerId} button {
03693:             touch-action: manipulation !important;
```

### Lines 3684-3694
```text
03684:         html[data-mcms-tablet-active="true"] #${SCRIPT.panelId},
03685:         html[data-mcms-tablet-active="true"] #${SCRIPT.criticalDrawerId} {
03686:             -webkit-tap-highlight-color: transparent !important;
03687:         }
03688:         html[data-mcms-tablet-active="true"] #${SCRIPT.controlId} button,
03689:         html[data-mcms-tablet-active="true"] #${SCRIPT.panelId} button,
03690:         html[data-mcms-tablet-active="true"] #${SCRIPT.panelId} input,
03691:         html[data-mcms-tablet-active="true"] #${SCRIPT.panelId} select,
03692:         html[data-mcms-tablet-active="true"] #${SCRIPT.criticalDrawerId} button {
03693:             touch-action: manipulation !important;
03694:         }
```

### Lines 3685-3695
```text
03685:         html[data-mcms-tablet-active="true"] #${SCRIPT.criticalDrawerId} {
03686:             -webkit-tap-highlight-color: transparent !important;
03687:         }
03688:         html[data-mcms-tablet-active="true"] #${SCRIPT.controlId} button,
03689:         html[data-mcms-tablet-active="true"] #${SCRIPT.panelId} button,
03690:         html[data-mcms-tablet-active="true"] #${SCRIPT.panelId} input,
03691:         html[data-mcms-tablet-active="true"] #${SCRIPT.panelId} select,
03692:         html[data-mcms-tablet-active="true"] #${SCRIPT.criticalDrawerId} button {
03693:             touch-action: manipulation !important;
03694:         }
03695:         html[data-mcms-tablet-active="true"] #${SCRIPT.controlId} {
```

### Lines 3686-3696
```text
03686:             -webkit-tap-highlight-color: transparent !important;
03687:         }
03688:         html[data-mcms-tablet-active="true"] #${SCRIPT.controlId} button,
03689:         html[data-mcms-tablet-active="true"] #${SCRIPT.panelId} button,
03690:         html[data-mcms-tablet-active="true"] #${SCRIPT.panelId} input,
03691:         html[data-mcms-tablet-active="true"] #${SCRIPT.panelId} select,
03692:         html[data-mcms-tablet-active="true"] #${SCRIPT.criticalDrawerId} button {
03693:             touch-action: manipulation !important;
03694:         }
03695:         html[data-mcms-tablet-active="true"] #${SCRIPT.controlId} {
03696:             width: var(--mcms-tablet-dock-width, min(920px, calc(100% - 20px))) !important;
```

### Lines 3687-3697
```text
03687:         }
03688:         html[data-mcms-tablet-active="true"] #${SCRIPT.controlId} button,
03689:         html[data-mcms-tablet-active="true"] #${SCRIPT.panelId} button,
03690:         html[data-mcms-tablet-active="true"] #${SCRIPT.panelId} input,
03691:         html[data-mcms-tablet-active="true"] #${SCRIPT.panelId} select,
03692:         html[data-mcms-tablet-active="true"] #${SCRIPT.criticalDrawerId} button {
03693:             touch-action: manipulation !important;
03694:         }
03695:         html[data-mcms-tablet-active="true"] #${SCRIPT.controlId} {
03696:             width: var(--mcms-tablet-dock-width, min(920px, calc(100% - 20px))) !important;
03697:             max-width: var(--mcms-tablet-dock-width, min(920px, calc(100% - 20px))) !important;
```

### Lines 3690-3700
```text
03690:         html[data-mcms-tablet-active="true"] #${SCRIPT.panelId} input,
03691:         html[data-mcms-tablet-active="true"] #${SCRIPT.panelId} select,
03692:         html[data-mcms-tablet-active="true"] #${SCRIPT.criticalDrawerId} button {
03693:             touch-action: manipulation !important;
03694:         }
03695:         html[data-mcms-tablet-active="true"] #${SCRIPT.controlId} {
03696:             width: var(--mcms-tablet-dock-width, min(920px, calc(100% - 20px))) !important;
03697:             max-width: var(--mcms-tablet-dock-width, min(920px, calc(100% - 20px))) !important;
03698:             display: grid !important;
03699:             grid-template-columns: 52px minmax(0,1fr) !important;
03700:             grid-template-areas: "menu filters" ". pins" !important;
```

### Lines 3691-3701
```text
03691:         html[data-mcms-tablet-active="true"] #${SCRIPT.panelId} select,
03692:         html[data-mcms-tablet-active="true"] #${SCRIPT.criticalDrawerId} button {
03693:             touch-action: manipulation !important;
03694:         }
03695:         html[data-mcms-tablet-active="true"] #${SCRIPT.controlId} {
03696:             width: var(--mcms-tablet-dock-width, min(920px, calc(100% - 20px))) !important;
03697:             max-width: var(--mcms-tablet-dock-width, min(920px, calc(100% - 20px))) !important;
03698:             display: grid !important;
03699:             grid-template-columns: 52px minmax(0,1fr) !important;
03700:             grid-template-areas: "menu filters" ". pins" !important;
03701:             align-items: start !important;
```

### Lines 3692-3702
```text
03692:         html[data-mcms-tablet-active="true"] #${SCRIPT.criticalDrawerId} button {
03693:             touch-action: manipulation !important;
03694:         }
03695:         html[data-mcms-tablet-active="true"] #${SCRIPT.controlId} {
03696:             width: var(--mcms-tablet-dock-width, min(920px, calc(100% - 20px))) !important;
03697:             max-width: var(--mcms-tablet-dock-width, min(920px, calc(100% - 20px))) !important;
03698:             display: grid !important;
03699:             grid-template-columns: 52px minmax(0,1fr) !important;
03700:             grid-template-areas: "menu filters" ". pins" !important;
03701:             align-items: start !important;
03702:             column-gap: 7px !important;
```

### Lines 3694-3704
```text
03694:         }
03695:         html[data-mcms-tablet-active="true"] #${SCRIPT.controlId} {
03696:             width: var(--mcms-tablet-dock-width, min(920px, calc(100% - 20px))) !important;
03697:             max-width: var(--mcms-tablet-dock-width, min(920px, calc(100% - 20px))) !important;
03698:             display: grid !important;
03699:             grid-template-columns: 52px minmax(0,1fr) !important;
03700:             grid-template-areas: "menu filters" ". pins" !important;
03701:             align-items: start !important;
03702:             column-gap: 7px !important;
03703:             row-gap: 7px !important;
03704:             font-size: 12px !important;
```

### Lines 3702-3712
```text
03702:             column-gap: 7px !important;
03703:             row-gap: 7px !important;
03704:             font-size: 12px !important;
03705:             pointer-events: none !important;
03706:         }
03707:         html[data-mcms-tablet-active="true"] #${SCRIPT.controlId}.mcms-pos-tl { left: max(10px, env(safe-area-inset-left)) !important; top: max(10px, env(safe-area-inset-top)) !important; }
03708:         html[data-mcms-tablet-active="true"] #${SCRIPT.controlId}.mcms-pos-tr { right: max(10px, env(safe-area-inset-right)) !important; top: max(10px, env(safe-area-inset-top)) !important; }
03709:         html[data-mcms-tablet-active="true"] #${SCRIPT.controlId}.mcms-pos-bl { left: max(10px, env(safe-area-inset-left)) !important; bottom: max(10px, env(safe-area-inset-bottom)) !important; }
03710:         html[data-mcms-tablet-active="true"] #${SCRIPT.controlId}.mcms-pos-br { right: max(10px, env(safe-area-inset-right)) !important; bottom: max(10px, env(safe-area-inset-bottom)) !important; }
03711:         html[data-mcms-tablet-active="true"] #${SCRIPT.controlId} .mcms-shell {
03712:             grid-area: menu !important;
```

### Lines 3703-3713
```text
03703:             row-gap: 7px !important;
03704:             font-size: 12px !important;
03705:             pointer-events: none !important;
03706:         }
03707:         html[data-mcms-tablet-active="true"] #${SCRIPT.controlId}.mcms-pos-tl { left: max(10px, env(safe-area-inset-left)) !important; top: max(10px, env(safe-area-inset-top)) !important; }
03708:         html[data-mcms-tablet-active="true"] #${SCRIPT.controlId}.mcms-pos-tr { right: max(10px, env(safe-area-inset-right)) !important; top: max(10px, env(safe-area-inset-top)) !important; }
03709:         html[data-mcms-tablet-active="true"] #${SCRIPT.controlId}.mcms-pos-bl { left: max(10px, env(safe-area-inset-left)) !important; bottom: max(10px, env(safe-area-inset-bottom)) !important; }
03710:         html[data-mcms-tablet-active="true"] #${SCRIPT.controlId}.mcms-pos-br { right: max(10px, env(safe-area-inset-right)) !important; bottom: max(10px, env(safe-area-inset-bottom)) !important; }
03711:         html[data-mcms-tablet-active="true"] #${SCRIPT.controlId} .mcms-shell {
03712:             grid-area: menu !important;
03713:             width: 52px !important; height: 48px !important; border-radius: 13px !important;
```

### Lines 3704-3714
```text
03704:             font-size: 12px !important;
03705:             pointer-events: none !important;
03706:         }
03707:         html[data-mcms-tablet-active="true"] #${SCRIPT.controlId}.mcms-pos-tl { left: max(10px, env(safe-area-inset-left)) !important; top: max(10px, env(safe-area-inset-top)) !important; }
03708:         html[data-mcms-tablet-active="true"] #${SCRIPT.controlId}.mcms-pos-tr { right: max(10px, env(safe-area-inset-right)) !important; top: max(10px, env(safe-area-inset-top)) !important; }
03709:         html[data-mcms-tablet-active="true"] #${SCRIPT.controlId}.mcms-pos-bl { left: max(10px, env(safe-area-inset-left)) !important; bottom: max(10px, env(safe-area-inset-bottom)) !important; }
03710:         html[data-mcms-tablet-active="true"] #${SCRIPT.controlId}.mcms-pos-br { right: max(10px, env(safe-area-inset-right)) !important; bottom: max(10px, env(safe-area-inset-bottom)) !important; }
03711:         html[data-mcms-tablet-active="true"] #${SCRIPT.controlId} .mcms-shell {
03712:             grid-area: menu !important;
03713:             width: 52px !important; height: 48px !important; border-radius: 13px !important;
03714:             background: rgba(8,12,18,.96) !important; backdrop-filter: none !important;
```

### Lines 3705-3715
```text
03705:             pointer-events: none !important;
03706:         }
03707:         html[data-mcms-tablet-active="true"] #${SCRIPT.controlId}.mcms-pos-tl { left: max(10px, env(safe-area-inset-left)) !important; top: max(10px, env(safe-area-inset-top)) !important; }
03708:         html[data-mcms-tablet-active="true"] #${SCRIPT.controlId}.mcms-pos-tr { right: max(10px, env(safe-area-inset-right)) !important; top: max(10px, env(safe-area-inset-top)) !important; }
03709:         html[data-mcms-tablet-active="true"] #${SCRIPT.controlId}.mcms-pos-bl { left: max(10px, env(safe-area-inset-left)) !important; bottom: max(10px, env(safe-area-inset-bottom)) !important; }
03710:         html[data-mcms-tablet-active="true"] #${SCRIPT.controlId}.mcms-pos-br { right: max(10px, env(safe-area-inset-right)) !important; bottom: max(10px, env(safe-area-inset-bottom)) !important; }
03711:         html[data-mcms-tablet-active="true"] #${SCRIPT.controlId} .mcms-shell {
03712:             grid-area: menu !important;
03713:             width: 52px !important; height: 48px !important; border-radius: 13px !important;
03714:             background: rgba(8,12,18,.96) !important; backdrop-filter: none !important;
03715:             pointer-events: auto !important;
```

### Lines 3706-3716
```text
03706:         }
03707:         html[data-mcms-tablet-active="true"] #${SCRIPT.controlId}.mcms-pos-tl { left: max(10px, env(safe-area-inset-left)) !important; top: max(10px, env(safe-area-inset-top)) !important; }
03708:         html[data-mcms-tablet-active="true"] #${SCRIPT.controlId}.mcms-pos-tr { right: max(10px, env(safe-area-inset-right)) !important; top: max(10px, env(safe-area-inset-top)) !important; }
03709:         html[data-mcms-tablet-active="true"] #${SCRIPT.controlId}.mcms-pos-bl { left: max(10px, env(safe-area-inset-left)) !important; bottom: max(10px, env(safe-area-inset-bottom)) !important; }
03710:         html[data-mcms-tablet-active="true"] #${SCRIPT.controlId}.mcms-pos-br { right: max(10px, env(safe-area-inset-right)) !important; bottom: max(10px, env(safe-area-inset-bottom)) !important; }
03711:         html[data-mcms-tablet-active="true"] #${SCRIPT.controlId} .mcms-shell {
03712:             grid-area: menu !important;
03713:             width: 52px !important; height: 48px !important; border-radius: 13px !important;
03714:             background: rgba(8,12,18,.96) !important; backdrop-filter: none !important;
03715:             pointer-events: auto !important;
03716:         }
```

### Lines 3712-3722
```text
03712:             grid-area: menu !important;
03713:             width: 52px !important; height: 48px !important; border-radius: 13px !important;
03714:             background: rgba(8,12,18,.96) !important; backdrop-filter: none !important;
03715:             pointer-events: auto !important;
03716:         }
03717:         html[data-mcms-tablet-active="true"] #${SCRIPT.controlId} .mcms-menu-btn { font-size: 22px !important; }
03718:         html[data-mcms-tablet-active="true"] #${SCRIPT.controlId} .mcms-dock-toggle-btn { height: 16px !important; flex-basis: 16px !important; font-size: 12px !important; }
03719:         html[data-mcms-command-bar-open="false"][data-mcms-tablet-active="true"] #${SCRIPT.controlId} {
03720:             width: 52px !important; max-width: 52px !important; grid-template-columns: 52px !important; grid-template-areas: "menu" !important;
03721:         }
03722:         html[data-mcms-tablet-active="true"] #${SCRIPT.controlId} .mcms-floating-filter {
```

### Lines 3713-3723
```text
03713:             width: 52px !important; height: 48px !important; border-radius: 13px !important;
03714:             background: rgba(8,12,18,.96) !important; backdrop-filter: none !important;
03715:             pointer-events: auto !important;
03716:         }
03717:         html[data-mcms-tablet-active="true"] #${SCRIPT.controlId} .mcms-menu-btn { font-size: 22px !important; }
03718:         html[data-mcms-tablet-active="true"] #${SCRIPT.controlId} .mcms-dock-toggle-btn { height: 16px !important; flex-basis: 16px !important; font-size: 12px !important; }
03719:         html[data-mcms-command-bar-open="false"][data-mcms-tablet-active="true"] #${SCRIPT.controlId} {
03720:             width: 52px !important; max-width: 52px !important; grid-template-columns: 52px !important; grid-template-areas: "menu" !important;
03721:         }
03722:         html[data-mcms-tablet-active="true"] #${SCRIPT.controlId} .mcms-floating-filter {
03723:             grid-area: filters !important;
```

### Lines 3714-3724
```text
03714:             background: rgba(8,12,18,.96) !important; backdrop-filter: none !important;
03715:             pointer-events: auto !important;
03716:         }
03717:         html[data-mcms-tablet-active="true"] #${SCRIPT.controlId} .mcms-menu-btn { font-size: 22px !important; }
03718:         html[data-mcms-tablet-active="true"] #${SCRIPT.controlId} .mcms-dock-toggle-btn { height: 16px !important; flex-basis: 16px !important; font-size: 12px !important; }
03719:         html[data-mcms-command-bar-open="false"][data-mcms-tablet-active="true"] #${SCRIPT.controlId} {
03720:             width: 52px !important; max-width: 52px !important; grid-template-columns: 52px !important; grid-template-areas: "menu" !important;
03721:         }
03722:         html[data-mcms-tablet-active="true"] #${SCRIPT.controlId} .mcms-floating-filter {
03723:             grid-area: filters !important;
03724:             display: grid !important;
```

### Lines 3715-3725
```text
03715:             pointer-events: auto !important;
03716:         }
03717:         html[data-mcms-tablet-active="true"] #${SCRIPT.controlId} .mcms-menu-btn { font-size: 22px !important; }
03718:         html[data-mcms-tablet-active="true"] #${SCRIPT.controlId} .mcms-dock-toggle-btn { height: 16px !important; flex-basis: 16px !important; font-size: 12px !important; }
03719:         html[data-mcms-command-bar-open="false"][data-mcms-tablet-active="true"] #${SCRIPT.controlId} {
03720:             width: 52px !important; max-width: 52px !important; grid-template-columns: 52px !important; grid-template-areas: "menu" !important;
03721:         }
03722:         html[data-mcms-tablet-active="true"] #${SCRIPT.controlId} .mcms-floating-filter {
03723:             grid-area: filters !important;
03724:             display: grid !important;
03725:             grid-template-columns: repeat(var(--mcms-tablet-filter-columns, 6), minmax(0,1fr)) !important;
```

### Lines 3717-3727
```text
03717:         html[data-mcms-tablet-active="true"] #${SCRIPT.controlId} .mcms-menu-btn { font-size: 22px !important; }
03718:         html[data-mcms-tablet-active="true"] #${SCRIPT.controlId} .mcms-dock-toggle-btn { height: 16px !important; flex-basis: 16px !important; font-size: 12px !important; }
03719:         html[data-mcms-command-bar-open="false"][data-mcms-tablet-active="true"] #${SCRIPT.controlId} {
03720:             width: 52px !important; max-width: 52px !important; grid-template-columns: 52px !important; grid-template-areas: "menu" !important;
03721:         }
03722:         html[data-mcms-tablet-active="true"] #${SCRIPT.controlId} .mcms-floating-filter {
03723:             grid-area: filters !important;
03724:             display: grid !important;
03725:             grid-template-columns: repeat(var(--mcms-tablet-filter-columns, 6), minmax(0,1fr)) !important;
03726:             gap: 7px !important;
03727:             width: 100% !important; max-width: none !important; margin-top: 0 !important;
```

### Lines 3720-3730
```text
03720:             width: 52px !important; max-width: 52px !important; grid-template-columns: 52px !important; grid-template-areas: "menu" !important;
03721:         }
03722:         html[data-mcms-tablet-active="true"] #${SCRIPT.controlId} .mcms-floating-filter {
03723:             grid-area: filters !important;
03724:             display: grid !important;
03725:             grid-template-columns: repeat(var(--mcms-tablet-filter-columns, 6), minmax(0,1fr)) !important;
03726:             gap: 7px !important;
03727:             width: 100% !important; max-width: none !important; margin-top: 0 !important;
03728:             overflow: visible !important; padding: 0 !important;
03729:             scrollbar-width: none !important; overscroll-behavior: auto !important;
03730:             -webkit-overflow-scrolling: auto !important; touch-action: manipulation !important;
```

### Lines 3728-3738
```text
03728:             overflow: visible !important; padding: 0 !important;
03729:             scrollbar-width: none !important; overscroll-behavior: auto !important;
03730:             -webkit-overflow-scrolling: auto !important; touch-action: manipulation !important;
03731:             pointer-events: none !important;
03732:         }
03733:         html[data-mcms-tablet-active="true"] #${SCRIPT.controlId} .mcms-floating-filter [data-toggle="criticalView"] { grid-column: auto !important; }
03734:         html[data-mcms-tablet-active="true"] #${SCRIPT.controlId} .mcms-float-btn {
03735:             position: relative !important; isolation: isolate !important; box-sizing: border-box !important;
03736:             flex: 0 1 auto !important; width: auto !important; min-width: 0 !important;
03737:             height: var(--mcms-tablet-filter-height, 48px) !important;
03738:             grid-template-columns: 21px minmax(0,1fr) !important; gap: 5px !important; padding: 0 6px !important;
```

### Lines 3729-3739
```text
03729:             scrollbar-width: none !important; overscroll-behavior: auto !important;
03730:             -webkit-overflow-scrolling: auto !important; touch-action: manipulation !important;
03731:             pointer-events: none !important;
03732:         }
03733:         html[data-mcms-tablet-active="true"] #${SCRIPT.controlId} .mcms-floating-filter [data-toggle="criticalView"] { grid-column: auto !important; }
03734:         html[data-mcms-tablet-active="true"] #${SCRIPT.controlId} .mcms-float-btn {
03735:             position: relative !important; isolation: isolate !important; box-sizing: border-box !important;
03736:             flex: 0 1 auto !important; width: auto !important; min-width: 0 !important;
03737:             height: var(--mcms-tablet-filter-height, 48px) !important;
03738:             grid-template-columns: 21px minmax(0,1fr) !important; gap: 5px !important; padding: 0 6px !important;
03739:             border-radius: 11px !important; border-width: 1px !important;
```

### Lines 3732-3742
```text
03732:         }
03733:         html[data-mcms-tablet-active="true"] #${SCRIPT.controlId} .mcms-floating-filter [data-toggle="criticalView"] { grid-column: auto !important; }
03734:         html[data-mcms-tablet-active="true"] #${SCRIPT.controlId} .mcms-float-btn {
03735:             position: relative !important; isolation: isolate !important; box-sizing: border-box !important;
03736:             flex: 0 1 auto !important; width: auto !important; min-width: 0 !important;
03737:             height: var(--mcms-tablet-filter-height, 48px) !important;
03738:             grid-template-columns: 21px minmax(0,1fr) !important; gap: 5px !important; padding: 0 6px !important;
03739:             border-radius: 11px !important; border-width: 1px !important;
03740:             background: linear-gradient(180deg,rgba(14,20,28,.97),rgba(7,11,17,.97)) !important;
03741:             color: rgba(255,255,255,.78) !important; backdrop-filter: none !important;
03742:             box-shadow: 0 4px 12px rgba(0,0,0,.34), inset 0 1px 0 rgba(255,255,255,.04) !important;
```

### Lines 3733-3743
```text
03733:         html[data-mcms-tablet-active="true"] #${SCRIPT.controlId} .mcms-floating-filter [data-toggle="criticalView"] { grid-column: auto !important; }
03734:         html[data-mcms-tablet-active="true"] #${SCRIPT.controlId} .mcms-float-btn {
03735:             position: relative !important; isolation: isolate !important; box-sizing: border-box !important;
03736:             flex: 0 1 auto !important; width: auto !important; min-width: 0 !important;
03737:             height: var(--mcms-tablet-filter-height, 48px) !important;
03738:             grid-template-columns: 21px minmax(0,1fr) !important; gap: 5px !important; padding: 0 6px !important;
03739:             border-radius: 11px !important; border-width: 1px !important;
03740:             background: linear-gradient(180deg,rgba(14,20,28,.97),rgba(7,11,17,.97)) !important;
03741:             color: rgba(255,255,255,.78) !important; backdrop-filter: none !important;
03742:             box-shadow: 0 4px 12px rgba(0,0,0,.34), inset 0 1px 0 rgba(255,255,255,.04) !important;
03743:             scroll-snap-align: none !important; pointer-events: auto !important;
```

### Lines 3741-3751
```text
03741:             color: rgba(255,255,255,.78) !important; backdrop-filter: none !important;
03742:             box-shadow: 0 4px 12px rgba(0,0,0,.34), inset 0 1px 0 rgba(255,255,255,.04) !important;
03743:             scroll-snap-align: none !important; pointer-events: auto !important;
03744:             transition: background 120ms ease,border-color 120ms ease,box-shadow 120ms ease,color 120ms ease,opacity 120ms ease,transform 120ms ease !important;
03745:         }
03746:         html[data-mcms-tablet-active="true"] #${SCRIPT.controlId} .mcms-float-btn:not(.mcms-on) {
03747:             opacity: .76 !important; border-color: rgba(255,255,255,.20) !important;
03748:         }
03749:         html[data-mcms-tablet-active="true"] #${SCRIPT.controlId} .mcms-float-btn.mcms-on {
03750:             opacity: 1 !important;
03751:             background: linear-gradient(145deg,rgba(8,101,73,.98),rgba(10,72,94,.98) 58%,rgba(14,49,82,.98)) !important;
```

### Lines 3744-3754
```text
03744:             transition: background 120ms ease,border-color 120ms ease,box-shadow 120ms ease,color 120ms ease,opacity 120ms ease,transform 120ms ease !important;
03745:         }
03746:         html[data-mcms-tablet-active="true"] #${SCRIPT.controlId} .mcms-float-btn:not(.mcms-on) {
03747:             opacity: .76 !important; border-color: rgba(255,255,255,.20) !important;
03748:         }
03749:         html[data-mcms-tablet-active="true"] #${SCRIPT.controlId} .mcms-float-btn.mcms-on {
03750:             opacity: 1 !important;
03751:             background: linear-gradient(145deg,rgba(8,101,73,.98),rgba(10,72,94,.98) 58%,rgba(14,49,82,.98)) !important;
03752:             border-color: #63f2b1 !important; color: #fff !important;
03753:             box-shadow: 0 0 0 1px rgba(99,242,177,.22),0 0 16px rgba(34,211,153,.38),0 5px 14px rgba(0,0,0,.38),inset 0 1px 0 rgba(255,255,255,.18) !important;
03754:             transform: translateY(-1px) !important;
```

### Lines 3751-3761
```text
03751:             background: linear-gradient(145deg,rgba(8,101,73,.98),rgba(10,72,94,.98) 58%,rgba(14,49,82,.98)) !important;
03752:             border-color: #63f2b1 !important; color: #fff !important;
03753:             box-shadow: 0 0 0 1px rgba(99,242,177,.22),0 0 16px rgba(34,211,153,.38),0 5px 14px rgba(0,0,0,.38),inset 0 1px 0 rgba(255,255,255,.18) !important;
03754:             transform: translateY(-1px) !important;
03755:         }
03756:         html[data-mcms-tablet-active="true"] #${SCRIPT.controlId} .mcms-float-btn.mcms-on::before {
03757:             content: "" !important; position: absolute !important; z-index: 1 !important; pointer-events: none !important;
03758:             left: 5px !important; right: 5px !important; bottom: 3px !important; height: 3px !important;
03759:             border-radius: 999px !important; background: linear-gradient(90deg,transparent,#72ffc0 18%,#61dfff 82%,transparent) !important;
03760:             box-shadow: 0 0 8px rgba(99,242,177,.85) !important;
03761:         }
```

### Lines 3757-3767
```text
03757:             content: "" !important; position: absolute !important; z-index: 1 !important; pointer-events: none !important;
03758:             left: 5px !important; right: 5px !important; bottom: 3px !important; height: 3px !important;
03759:             border-radius: 999px !important; background: linear-gradient(90deg,transparent,#72ffc0 18%,#61dfff 82%,transparent) !important;
03760:             box-shadow: 0 0 8px rgba(99,242,177,.85) !important;
03761:         }
03762:         html[data-mcms-tablet-active="true"] #${SCRIPT.controlId} .mcms-float-btn.mcms-on::after {
03763:             content: "" !important; position: absolute !important; z-index: 3 !important; pointer-events: none !important; top: 5px !important; right: 5px !important;
03764:             width: 5px !important; height: 5px !important; border-radius: 50% !important;
03765:             background: #76ffc1 !important; box-shadow: 0 0 0 2px rgba(5,35,29,.72),0 0 8px rgba(118,255,193,.95) !important;
03766:         }
03767:         html[data-mcms-tablet-active="true"] #${SCRIPT.controlId} .mcms-float-key {
```

### Lines 3762-3772
```text
03762:         html[data-mcms-tablet-active="true"] #${SCRIPT.controlId} .mcms-float-btn.mcms-on::after {
03763:             content: "" !important; position: absolute !important; z-index: 3 !important; pointer-events: none !important; top: 5px !important; right: 5px !important;
03764:             width: 5px !important; height: 5px !important; border-radius: 50% !important;
03765:             background: #76ffc1 !important; box-shadow: 0 0 0 2px rgba(5,35,29,.72),0 0 8px rgba(118,255,193,.95) !important;
03766:         }
03767:         html[data-mcms-tablet-active="true"] #${SCRIPT.controlId} .mcms-float-key {
03768:             position: relative !important; z-index: 2 !important;
03769:             width: 21px !important; height: 21px !important; border-radius: 7px !important; font-size: 10px !important;
03770:             background: rgba(255,255,255,.11) !important; border: 1px solid rgba(255,255,255,.10) !important;
03771:         }
03772:         html[data-mcms-tablet-active="true"] #${SCRIPT.controlId} .mcms-float-btn.mcms-on .mcms-float-key {
```

### Lines 3767-3777
```text
03767:         html[data-mcms-tablet-active="true"] #${SCRIPT.controlId} .mcms-float-key {
03768:             position: relative !important; z-index: 2 !important;
03769:             width: 21px !important; height: 21px !important; border-radius: 7px !important; font-size: 10px !important;
03770:             background: rgba(255,255,255,.11) !important; border: 1px solid rgba(255,255,255,.10) !important;
03771:         }
03772:         html[data-mcms-tablet-active="true"] #${SCRIPT.controlId} .mcms-float-btn.mcms-on .mcms-float-key {
03773:             background: rgba(23,198,126,.95) !important; border-color: rgba(194,255,226,.72) !important;
03774:             box-shadow: 0 0 9px rgba(67,239,166,.55) !important;
03775:         }
03776:         html[data-mcms-tablet-active="true"] #${SCRIPT.controlId} .mcms-float-label-desktop { display: none !important; }
03777:         html[data-mcms-tablet-active="true"] #${SCRIPT.controlId} .mcms-float-label-tablet {
```

### Lines 3771-3781
```text
03771:         }
03772:         html[data-mcms-tablet-active="true"] #${SCRIPT.controlId} .mcms-float-btn.mcms-on .mcms-float-key {
03773:             background: rgba(23,198,126,.95) !important; border-color: rgba(194,255,226,.72) !important;
03774:             box-shadow: 0 0 9px rgba(67,239,166,.55) !important;
03775:         }
03776:         html[data-mcms-tablet-active="true"] #${SCRIPT.controlId} .mcms-float-label-desktop { display: none !important; }
03777:         html[data-mcms-tablet-active="true"] #${SCRIPT.controlId} .mcms-float-label-tablet {
03778:             position: relative !important; z-index: 2 !important;
03779:             display: flex !important; align-items: center !important; justify-content: flex-start !important;
03780:             min-width: 0 !important; min-height: 2.05em !important; max-height: 2.05em !important;
03781:             overflow: hidden !important; text-overflow: clip !important; white-space: normal !important;
```

### Lines 3772-3782
```text
03772:         html[data-mcms-tablet-active="true"] #${SCRIPT.controlId} .mcms-float-btn.mcms-on .mcms-float-key {
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
```

### Lines 3776-3786
```text
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
```

### Lines 3777-3787
```text
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
```

### Lines 3781-3791
```text
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
03791:             width: 100% !important; max-width: none !important; max-height: none !important; margin-top: 0 !important;
```

### Lines 3784-3794
```text
03784:             font-weight: 900 !important; text-align: left !important; padding-right: 4px !important; text-shadow: 0 1px 2px rgba(0,0,0,.72) !important;
03785:         }
03786:         html[data-mcms-tablet-active="true"] #${SCRIPT.controlId} .mcms-screen-pins {
03787:             grid-area: pins !important;
03788:             display: grid !important;
03789:             grid-template-columns: repeat(var(--mcms-tablet-pin-columns, 4), minmax(0,1fr)) !important;
03790:             gap: 7px !important;
03791:             width: 100% !important; max-width: none !important; max-height: none !important; margin-top: 0 !important;
03792:             overflow: visible !important; padding: 0 !important;
03793:             overscroll-behavior: auto !important; -webkit-overflow-scrolling: auto !important; touch-action: manipulation !important;
03794:             pointer-events: none !important;
```

### Lines 3791-3801
```text
03791:             width: 100% !important; max-width: none !important; max-height: none !important; margin-top: 0 !important;
03792:             overflow: visible !important; padding: 0 !important;
03793:             overscroll-behavior: auto !important; -webkit-overflow-scrolling: auto !important; touch-action: manipulation !important;
03794:             pointer-events: none !important;
03795:         }
03796:         html[data-mcms-tablet-active="true"] #${SCRIPT.controlId} .mcms-screen-pins:empty { display: none !important; }
03797:         html[data-mcms-tablet-active="true"] #${SCRIPT.controlId} .mcms-screen-pin-btn {
03798:             flex: 0 1 auto !important; width: auto !important; min-width: 0 !important;
03799:             height: var(--mcms-tablet-pin-height, 42px) !important; padding: 0 12px !important;
03800:             border-radius: 10px !important; font-size: 10.5px !important; backdrop-filter: none !important;
03801:             pointer-events: auto !important;
```

### Lines 3792-3802
```text
03792:             overflow: visible !important; padding: 0 !important;
03793:             overscroll-behavior: auto !important; -webkit-overflow-scrolling: auto !important; touch-action: manipulation !important;
03794:             pointer-events: none !important;
03795:         }
03796:         html[data-mcms-tablet-active="true"] #${SCRIPT.controlId} .mcms-screen-pins:empty { display: none !important; }
03797:         html[data-mcms-tablet-active="true"] #${SCRIPT.controlId} .mcms-screen-pin-btn {
03798:             flex: 0 1 auto !important; width: auto !important; min-width: 0 !important;
03799:             height: var(--mcms-tablet-pin-height, 42px) !important; padding: 0 12px !important;
03800:             border-radius: 10px !important; font-size: 10.5px !important; backdrop-filter: none !important;
03801:             pointer-events: auto !important;
03802:         }
```

### Lines 3794-3804
```text
03794:             pointer-events: none !important;
03795:         }
03796:         html[data-mcms-tablet-active="true"] #${SCRIPT.controlId} .mcms-screen-pins:empty { display: none !important; }
03797:         html[data-mcms-tablet-active="true"] #${SCRIPT.controlId} .mcms-screen-pin-btn {
03798:             flex: 0 1 auto !important; width: auto !important; min-width: 0 !important;
03799:             height: var(--mcms-tablet-pin-height, 42px) !important; padding: 0 12px !important;
03800:             border-radius: 10px !important; font-size: 10.5px !important; backdrop-filter: none !important;
03801:             pointer-events: auto !important;
03802:         }
03803: 
03804:         html[data-mcms-tablet-active="true"] #${SCRIPT.panelId} {
```

### Lines 3799-3809
```text
03799:             height: var(--mcms-tablet-pin-height, 42px) !important; padding: 0 12px !important;
03800:             border-radius: 10px !important; font-size: 10.5px !important; backdrop-filter: none !important;
03801:             pointer-events: auto !important;
03802:         }
03803: 
03804:         html[data-mcms-tablet-active="true"] #${SCRIPT.panelId} {
03805:             padding: 12px !important; border-radius: 18px !important;
03806:             background: rgba(8,12,18,.985) !important; backdrop-filter: none !important; -webkit-backdrop-filter: none !important;
03807:             box-shadow: 0 12px 30px rgba(0,0,0,.52) !important;
03808:             overflow-y: auto !important; overflow-x: hidden !important; overscroll-behavior: contain !important;
03809:             -webkit-overflow-scrolling: touch !important; touch-action: pan-y !important;
```

### Lines 3807-3817
```text
03807:             box-shadow: 0 12px 30px rgba(0,0,0,.52) !important;
03808:             overflow-y: auto !important; overflow-x: hidden !important; overscroll-behavior: contain !important;
03809:             -webkit-overflow-scrolling: touch !important; touch-action: pan-y !important;
03810:             font-size: 13px !important; line-height: 1.25 !important;
03811:         }
03812:         html[data-mcms-tablet-active="true"] #${SCRIPT.panelId} .mcms-header {
03813:             position: sticky !important; top: -12px !important; z-index: 8 !important;
03814:             grid-template-columns: minmax(0,1fr) 44px 44px !important; gap: 9px !important;
03815:             min-height: 54px !important; margin: -12px -12px 10px !important; padding: 10px 12px 9px !important;
03816:             background: rgba(8,12,18,.995) !important; border-bottom: 1px solid rgba(255,255,255,.16) !important;
03817:         }
```

### Lines 3809-3819
```text
03809:             -webkit-overflow-scrolling: touch !important; touch-action: pan-y !important;
03810:             font-size: 13px !important; line-height: 1.25 !important;
03811:         }
03812:         html[data-mcms-tablet-active="true"] #${SCRIPT.panelId} .mcms-header {
03813:             position: sticky !important; top: -12px !important; z-index: 8 !important;
03814:             grid-template-columns: minmax(0,1fr) 44px 44px !important; gap: 9px !important;
03815:             min-height: 54px !important; margin: -12px -12px 10px !important; padding: 10px 12px 9px !important;
03816:             background: rgba(8,12,18,.995) !important; border-bottom: 1px solid rgba(255,255,255,.16) !important;
03817:         }
03818:         html[data-mcms-tablet-active="true"] #${SCRIPT.panelId} .mcms-drag-handle {
03819:             cursor: default !important; touch-action: pan-y !important; padding: 2px 0 !important;
```

### Lines 3813-3823
```text
03813:             position: sticky !important; top: -12px !important; z-index: 8 !important;
03814:             grid-template-columns: minmax(0,1fr) 44px 44px !important; gap: 9px !important;
03815:             min-height: 54px !important; margin: -12px -12px 10px !important; padding: 10px 12px 9px !important;
03816:             background: rgba(8,12,18,.995) !important; border-bottom: 1px solid rgba(255,255,255,.16) !important;
03817:         }
03818:         html[data-mcms-tablet-active="true"] #${SCRIPT.panelId} .mcms-drag-handle {
03819:             cursor: default !important; touch-action: pan-y !important; padding: 2px 0 !important;
03820:         }
03821:         html[data-mcms-tablet-active="true"] #${SCRIPT.panelId} .mcms-title { font-size: 14px !important; letter-spacing: .45px !important; }
03822:         html[data-mcms-tablet-active="true"] #${SCRIPT.panelId} .mcms-subtitle { margin-top: 4px !important; font-size: 10.5px !important; }
03823:         html[data-mcms-tablet-active="true"] #${SCRIPT.panelId} .mcms-reset-panel { display: none !important; }
```

### Lines 3816-3826
```text
03816:             background: rgba(8,12,18,.995) !important; border-bottom: 1px solid rgba(255,255,255,.16) !important;
03817:         }
03818:         html[data-mcms-tablet-active="true"] #${SCRIPT.panelId} .mcms-drag-handle {
03819:             cursor: default !important; touch-action: pan-y !important; padding: 2px 0 !important;
03820:         }
03821:         html[data-mcms-tablet-active="true"] #${SCRIPT.panelId} .mcms-title { font-size: 14px !important; letter-spacing: .45px !important; }
03822:         html[data-mcms-tablet-active="true"] #${SCRIPT.panelId} .mcms-subtitle { margin-top: 4px !important; font-size: 10.5px !important; }
03823:         html[data-mcms-tablet-active="true"] #${SCRIPT.panelId} .mcms-reset-panel { display: none !important; }
03824:         html[data-mcms-tablet-active="true"] #${SCRIPT.panelId} .mcms-close,
03825:         html[data-mcms-tablet-active="true"] #${SCRIPT.panelId} .mcms-help-button {
03826:             width: 44px !important; height: 44px !important; border-radius: 11px !important; font-size: 20px !important; line-height: 44px !important;
```

### Lines 3817-3827
```text
03817:         }
03818:         html[data-mcms-tablet-active="true"] #${SCRIPT.panelId} .mcms-drag-handle {
03819:             cursor: default !important; touch-action: pan-y !important; padding: 2px 0 !important;
03820:         }
03821:         html[data-mcms-tablet-active="true"] #${SCRIPT.panelId} .mcms-title { font-size: 14px !important; letter-spacing: .45px !important; }
03822:         html[data-mcms-tablet-active="true"] #${SCRIPT.panelId} .mcms-subtitle { margin-top: 4px !important; font-size: 10.5px !important; }
03823:         html[data-mcms-tablet-active="true"] #${SCRIPT.panelId} .mcms-reset-panel { display: none !important; }
03824:         html[data-mcms-tablet-active="true"] #${SCRIPT.panelId} .mcms-close,
03825:         html[data-mcms-tablet-active="true"] #${SCRIPT.panelId} .mcms-help-button {
03826:             width: 44px !important; height: 44px !important; border-radius: 11px !important; font-size: 20px !important; line-height: 44px !important;
03827:         }
```

### Lines 3818-3828
```text
03818:         html[data-mcms-tablet-active="true"] #${SCRIPT.panelId} .mcms-drag-handle {
03819:             cursor: default !important; touch-action: pan-y !important; padding: 2px 0 !important;
03820:         }
03821:         html[data-mcms-tablet-active="true"] #${SCRIPT.panelId} .mcms-title { font-size: 14px !important; letter-spacing: .45px !important; }
03822:         html[data-mcms-tablet-active="true"] #${SCRIPT.panelId} .mcms-subtitle { margin-top: 4px !important; font-size: 10.5px !important; }
03823:         html[data-mcms-tablet-active="true"] #${SCRIPT.panelId} .mcms-reset-panel { display: none !important; }
03824:         html[data-mcms-tablet-active="true"] #${SCRIPT.panelId} .mcms-close,
03825:         html[data-mcms-tablet-active="true"] #${SCRIPT.panelId} .mcms-help-button {
03826:             width: 44px !important; height: 44px !important; border-radius: 11px !important; font-size: 20px !important; line-height: 44px !important;
03827:         }
03828:         html[data-mcms-tablet-active="true"] #${SCRIPT.panelId} .mcms-close { font-size:24px !important; }
```

### Lines 3819-3829
```text
03819:             cursor: default !important; touch-action: pan-y !important; padding: 2px 0 !important;
03820:         }
03821:         html[data-mcms-tablet-active="true"] #${SCRIPT.panelId} .mcms-title { font-size: 14px !important; letter-spacing: .45px !important; }
03822:         html[data-mcms-tablet-active="true"] #${SCRIPT.panelId} .mcms-subtitle { margin-top: 4px !important; font-size: 10.5px !important; }
03823:         html[data-mcms-tablet-active="true"] #${SCRIPT.panelId} .mcms-reset-panel { display: none !important; }
03824:         html[data-mcms-tablet-active="true"] #${SCRIPT.panelId} .mcms-close,
03825:         html[data-mcms-tablet-active="true"] #${SCRIPT.panelId} .mcms-help-button {
03826:             width: 44px !important; height: 44px !important; border-radius: 11px !important; font-size: 20px !important; line-height: 44px !important;
03827:         }
03828:         html[data-mcms-tablet-active="true"] #${SCRIPT.panelId} .mcms-close { font-size:24px !important; }
03829:         html[data-mcms-tablet-active="true"] #${SCRIPT.panelId} .mcms-tabs {
```

### Lines 3820-3830
```text
03820:         }
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
```

### Lines 3823-3833
```text
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
```

### Lines 3824-3834
```text
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
```

### Lines 3826-3836
```text
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
```

### Lines 3829-3839
```text
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
```

### Lines 3832-3842
```text
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
```

### Lines 3833-3843
```text
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
```

### Lines 3834-3844
```text
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
```

### Lines 3835-3845
```text
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
```

### Lines 3836-3846
```text
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
```

### Lines 3838-3848
```text
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
```

### Lines 3840-3850
```text
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
```

### Lines 3843-3853
```text
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
```

### Lines 3844-3854
```text
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
```

### Lines 3845-3855
```text
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
```

### Lines 3846-3856
```text
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
```

### Lines 3847-3857
```text
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
```

### Lines 3849-3859
```text
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
03859:         }
```

### Lines 3850-3860
```text
03850:         html[data-mcms-tablet-active="true"] #${SCRIPT.panelId} .mcms-section-label { margin: 14px 0 8px !important; font-size: 10.5px !important; letter-spacing: .8px !important; }
03851:         html[data-mcms-tablet-active="true"] #${SCRIPT.panelId} .mcms-row {
03852:             grid-template-columns: minmax(0,1fr) minmax(170px, 42%) !important; gap: 10px !important; margin-bottom: 10px !important;
03853:         }
03854:         html[data-mcms-tablet-active="true"] #${SCRIPT.panelId} .mcms-discord-wide { grid-template-columns: 120px minmax(0,1fr) !important; }
03855:         html[data-mcms-tablet-active="true"] #${SCRIPT.panelId} .mcms-row-label { font-size: 12px !important; }
03856:         html[data-mcms-tablet-active="true"] #${SCRIPT.panelId} .mcms-input,
03857:         html[data-mcms-tablet-active="true"] #${SCRIPT.panelId} .mcms-select {
03858:             height: 44px !important; border-radius: 10px !important; padding: 0 11px !important; font-size: 13px !important;
03859:         }
03860:         html[data-mcms-tablet-active="true"] #${SCRIPT.panelId} .mcms-position-grid,
```

### Lines 3851-3861
```text
03851:         html[data-mcms-tablet-active="true"] #${SCRIPT.panelId} .mcms-row {
03852:             grid-template-columns: minmax(0,1fr) minmax(170px, 42%) !important; gap: 10px !important; margin-bottom: 10px !important;
03853:         }
03854:         html[data-mcms-tablet-active="true"] #${SCRIPT.panelId} .mcms-discord-wide { grid-template-columns: 120px minmax(0,1fr) !important; }
03855:         html[data-mcms-tablet-active="true"] #${SCRIPT.panelId} .mcms-row-label { font-size: 12px !important; }
03856:         html[data-mcms-tablet-active="true"] #${SCRIPT.panelId} .mcms-input,
03857:         html[data-mcms-tablet-active="true"] #${SCRIPT.panelId} .mcms-select {
03858:             height: 44px !important; border-radius: 10px !important; padding: 0 11px !important; font-size: 13px !important;
03859:         }
03860:         html[data-mcms-tablet-active="true"] #${SCRIPT.panelId} .mcms-position-grid,
03861:         html[data-mcms-tablet-active="true"] #${SCRIPT.panelId} .mcms-nudge-grid { gap: 8px !important; }
```

### Lines 3852-3862
```text
03852:             grid-template-columns: minmax(0,1fr) minmax(170px, 42%) !important; gap: 10px !important; margin-bottom: 10px !important;
03853:         }
03854:         html[data-mcms-tablet-active="true"] #${SCRIPT.panelId} .mcms-discord-wide { grid-template-columns: 120px minmax(0,1fr) !important; }
03855:         html[data-mcms-tablet-active="true"] #${SCRIPT.panelId} .mcms-row-label { font-size: 12px !important; }
03856:         html[data-mcms-tablet-active="true"] #${SCRIPT.panelId} .mcms-input,
03857:         html[data-mcms-tablet-active="true"] #${SCRIPT.panelId} .mcms-select {
03858:             height: 44px !important; border-radius: 10px !important; padding: 0 11px !important; font-size: 13px !important;
03859:         }
03860:         html[data-mcms-tablet-active="true"] #${SCRIPT.panelId} .mcms-position-grid,
03861:         html[data-mcms-tablet-active="true"] #${SCRIPT.panelId} .mcms-nudge-grid { gap: 8px !important; }
03862:         html[data-mcms-tablet-active="true"] #${SCRIPT.panelId} .mcms-position-btn,
```

### Lines 3855-3865
```text
03855:         html[data-mcms-tablet-active="true"] #${SCRIPT.panelId} .mcms-row-label { font-size: 12px !important; }
03856:         html[data-mcms-tablet-active="true"] #${SCRIPT.panelId} .mcms-input,
03857:         html[data-mcms-tablet-active="true"] #${SCRIPT.panelId} .mcms-select {
03858:             height: 44px !important; border-radius: 10px !important; padding: 0 11px !important; font-size: 13px !important;
03859:         }
03860:         html[data-mcms-tablet-active="true"] #${SCRIPT.panelId} .mcms-position-grid,
03861:         html[data-mcms-tablet-active="true"] #${SCRIPT.panelId} .mcms-nudge-grid { gap: 8px !important; }
03862:         html[data-mcms-tablet-active="true"] #${SCRIPT.panelId} .mcms-position-btn,
03863:         html[data-mcms-tablet-active="true"] #${SCRIPT.panelId} .mcms-small-btn,
03864:         html[data-mcms-tablet-active="true"] #${SCRIPT.panelId} .mcms-bookmark-btn,
03865:         html[data-mcms-tablet-active="true"] #${SCRIPT.panelId} .mcms-pin-btn {
```

### Lines 3856-3866
```text
03856:         html[data-mcms-tablet-active="true"] #${SCRIPT.panelId} .mcms-input,
03857:         html[data-mcms-tablet-active="true"] #${SCRIPT.panelId} .mcms-select {
03858:             height: 44px !important; border-radius: 10px !important; padding: 0 11px !important; font-size: 13px !important;
03859:         }
03860:         html[data-mcms-tablet-active="true"] #${SCRIPT.panelId} .mcms-position-grid,
03861:         html[data-mcms-tablet-active="true"] #${SCRIPT.panelId} .mcms-nudge-grid { gap: 8px !important; }
03862:         html[data-mcms-tablet-active="true"] #${SCRIPT.panelId} .mcms-position-btn,
03863:         html[data-mcms-tablet-active="true"] #${SCRIPT.panelId} .mcms-small-btn,
03864:         html[data-mcms-tablet-active="true"] #${SCRIPT.panelId} .mcms-bookmark-btn,
03865:         html[data-mcms-tablet-active="true"] #${SCRIPT.panelId} .mcms-pin-btn {
03866:             min-height: 44px !important; height: 44px !important; border-radius: 10px !important;
```

### Lines 3857-3867
```text
03857:         html[data-mcms-tablet-active="true"] #${SCRIPT.panelId} .mcms-select {
03858:             height: 44px !important; border-radius: 10px !important; padding: 0 11px !important; font-size: 13px !important;
03859:         }
03860:         html[data-mcms-tablet-active="true"] #${SCRIPT.panelId} .mcms-position-grid,
03861:         html[data-mcms-tablet-active="true"] #${SCRIPT.panelId} .mcms-nudge-grid { gap: 8px !important; }
03862:         html[data-mcms-tablet-active="true"] #${SCRIPT.panelId} .mcms-position-btn,
03863:         html[data-mcms-tablet-active="true"] #${SCRIPT.panelId} .mcms-small-btn,
03864:         html[data-mcms-tablet-active="true"] #${SCRIPT.panelId} .mcms-bookmark-btn,
03865:         html[data-mcms-tablet-active="true"] #${SCRIPT.panelId} .mcms-pin-btn {
03866:             min-height: 44px !important; height: 44px !important; border-radius: 10px !important;
03867:             font-size: 11.5px !important; line-height: 44px !important; padding: 0 8px !important;
```

### Lines 3858-3868
```text
03858:             height: 44px !important; border-radius: 10px !important; padding: 0 11px !important; font-size: 13px !important;
03859:         }
03860:         html[data-mcms-tablet-active="true"] #${SCRIPT.panelId} .mcms-position-grid,
03861:         html[data-mcms-tablet-active="true"] #${SCRIPT.panelId} .mcms-nudge-grid { gap: 8px !important; }
03862:         html[data-mcms-tablet-active="true"] #${SCRIPT.panelId} .mcms-position-btn,
03863:         html[data-mcms-tablet-active="true"] #${SCRIPT.panelId} .mcms-small-btn,
03864:         html[data-mcms-tablet-active="true"] #${SCRIPT.panelId} .mcms-bookmark-btn,
03865:         html[data-mcms-tablet-active="true"] #${SCRIPT.panelId} .mcms-pin-btn {
03866:             min-height: 44px !important; height: 44px !important; border-radius: 10px !important;
03867:             font-size: 11.5px !important; line-height: 44px !important; padding: 0 8px !important;
03868:         }
```

### Lines 3859-3869
```text
03859:         }
03860:         html[data-mcms-tablet-active="true"] #${SCRIPT.panelId} .mcms-position-grid,
03861:         html[data-mcms-tablet-active="true"] #${SCRIPT.panelId} .mcms-nudge-grid { gap: 8px !important; }
03862:         html[data-mcms-tablet-active="true"] #${SCRIPT.panelId} .mcms-position-btn,
03863:         html[data-mcms-tablet-active="true"] #${SCRIPT.panelId} .mcms-small-btn,
03864:         html[data-mcms-tablet-active="true"] #${SCRIPT.panelId} .mcms-bookmark-btn,
03865:         html[data-mcms-tablet-active="true"] #${SCRIPT.panelId} .mcms-pin-btn {
03866:             min-height: 44px !important; height: 44px !important; border-radius: 10px !important;
03867:             font-size: 11.5px !important; line-height: 44px !important; padding: 0 8px !important;
03868:         }
03869:         html[data-mcms-tablet-active="true"] #${SCRIPT.panelId} .mcms-quick-row { grid-template-columns: minmax(0,1fr) 64px !important; gap: 8px !important; margin-bottom: 8px !important; }
```

### Lines 3860-3870
```text
03860:         html[data-mcms-tablet-active="true"] #${SCRIPT.panelId} .mcms-position-grid,
03861:         html[data-mcms-tablet-active="true"] #${SCRIPT.panelId} .mcms-nudge-grid { gap: 8px !important; }
03862:         html[data-mcms-tablet-active="true"] #${SCRIPT.panelId} .mcms-position-btn,
03863:         html[data-mcms-tablet-active="true"] #${SCRIPT.panelId} .mcms-small-btn,
03864:         html[data-mcms-tablet-active="true"] #${SCRIPT.panelId} .mcms-bookmark-btn,
03865:         html[data-mcms-tablet-active="true"] #${SCRIPT.panelId} .mcms-pin-btn {
03866:             min-height: 44px !important; height: 44px !important; border-radius: 10px !important;
03867:             font-size: 11.5px !important; line-height: 44px !important; padding: 0 8px !important;
03868:         }
03869:         html[data-mcms-tablet-active="true"] #${SCRIPT.panelId} .mcms-quick-row { grid-template-columns: minmax(0,1fr) 64px !important; gap: 8px !important; margin-bottom: 8px !important; }
03870:         html[data-mcms-tablet-active="true"] #${SCRIPT.panelId} .mcms-bookmark-row {
```

### Lines 3864-3874
```text
03864:         html[data-mcms-tablet-active="true"] #${SCRIPT.panelId} .mcms-bookmark-btn,
03865:         html[data-mcms-tablet-active="true"] #${SCRIPT.panelId} .mcms-pin-btn {
03866:             min-height: 44px !important; height: 44px !important; border-radius: 10px !important;
03867:             font-size: 11.5px !important; line-height: 44px !important; padding: 0 8px !important;
03868:         }
03869:         html[data-mcms-tablet-active="true"] #${SCRIPT.panelId} .mcms-quick-row { grid-template-columns: minmax(0,1fr) 64px !important; gap: 8px !important; margin-bottom: 8px !important; }
03870:         html[data-mcms-tablet-active="true"] #${SCRIPT.panelId} .mcms-bookmark-row {
03871:             grid-template-columns: minmax(0,1fr) 54px 54px 54px 46px !important; gap: 7px !important; margin-bottom: 8px !important;
03872:         }
03873:         html[data-mcms-tablet-active="true"] #${SCRIPT.panelId} .mcms-bookmark-name { font-size: 12px !important; }
03874:         html[data-mcms-tablet-active="true"] #${SCRIPT.panelId} .mcms-status {
```

### Lines 3865-3875
```text
03865:         html[data-mcms-tablet-active="true"] #${SCRIPT.panelId} .mcms-pin-btn {
03866:             min-height: 44px !important; height: 44px !important; border-radius: 10px !important;
03867:             font-size: 11.5px !important; line-height: 44px !important; padding: 0 8px !important;
03868:         }
03869:         html[data-mcms-tablet-active="true"] #${SCRIPT.panelId} .mcms-quick-row { grid-template-columns: minmax(0,1fr) 64px !important; gap: 8px !important; margin-bottom: 8px !important; }
03870:         html[data-mcms-tablet-active="true"] #${SCRIPT.panelId} .mcms-bookmark-row {
03871:             grid-template-columns: minmax(0,1fr) 54px 54px 54px 46px !important; gap: 7px !important; margin-bottom: 8px !important;
03872:         }
03873:         html[data-mcms-tablet-active="true"] #${SCRIPT.panelId} .mcms-bookmark-name { font-size: 12px !important; }
03874:         html[data-mcms-tablet-active="true"] #${SCRIPT.panelId} .mcms-status {
03875:             margin-top: 10px !important; padding: 10px 11px !important; border-radius: 11px !important; font-size: 11px !important; line-height: 1.4 !important;
```

### Lines 3866-3876
```text
03866:             min-height: 44px !important; height: 44px !important; border-radius: 10px !important;
03867:             font-size: 11.5px !important; line-height: 44px !important; padding: 0 8px !important;
03868:         }
03869:         html[data-mcms-tablet-active="true"] #${SCRIPT.panelId} .mcms-quick-row { grid-template-columns: minmax(0,1fr) 64px !important; gap: 8px !important; margin-bottom: 8px !important; }
03870:         html[data-mcms-tablet-active="true"] #${SCRIPT.panelId} .mcms-bookmark-row {
03871:             grid-template-columns: minmax(0,1fr) 54px 54px 54px 46px !important; gap: 7px !important; margin-bottom: 8px !important;
03872:         }
03873:         html[data-mcms-tablet-active="true"] #${SCRIPT.panelId} .mcms-bookmark-name { font-size: 12px !important; }
03874:         html[data-mcms-tablet-active="true"] #${SCRIPT.panelId} .mcms-status {
03875:             margin-top: 10px !important; padding: 10px 11px !important; border-radius: 11px !important; font-size: 11px !important; line-height: 1.4 !important;
03876:         }
```

### Lines 3868-3878
```text
03868:         }
03869:         html[data-mcms-tablet-active="true"] #${SCRIPT.panelId} .mcms-quick-row { grid-template-columns: minmax(0,1fr) 64px !important; gap: 8px !important; margin-bottom: 8px !important; }
03870:         html[data-mcms-tablet-active="true"] #${SCRIPT.panelId} .mcms-bookmark-row {
03871:             grid-template-columns: minmax(0,1fr) 54px 54px 54px 46px !important; gap: 7px !important; margin-bottom: 8px !important;
03872:         }
03873:         html[data-mcms-tablet-active="true"] #${SCRIPT.panelId} .mcms-bookmark-name { font-size: 12px !important; }
03874:         html[data-mcms-tablet-active="true"] #${SCRIPT.panelId} .mcms-status {
03875:             margin-top: 10px !important; padding: 10px 11px !important; border-radius: 11px !important; font-size: 11px !important; line-height: 1.4 !important;
03876:         }
03877:         html[data-mcms-tablet-active="true"] #${SCRIPT.panelId} .mcms-profile-row {
03878:             grid-template-columns: minmax(0,1fr) 54px 54px 44px !important; gap: 7px !important;
```

### Lines 3869-3879
```text
03869:         html[data-mcms-tablet-active="true"] #${SCRIPT.panelId} .mcms-quick-row { grid-template-columns: minmax(0,1fr) 64px !important; gap: 8px !important; margin-bottom: 8px !important; }
03870:         html[data-mcms-tablet-active="true"] #${SCRIPT.panelId} .mcms-bookmark-row {
03871:             grid-template-columns: minmax(0,1fr) 54px 54px 54px 46px !important; gap: 7px !important; margin-bottom: 8px !important;
03872:         }
03873:         html[data-mcms-tablet-active="true"] #${SCRIPT.panelId} .mcms-bookmark-name { font-size: 12px !important; }
03874:         html[data-mcms-tablet-active="true"] #${SCRIPT.panelId} .mcms-status {
03875:             margin-top: 10px !important; padding: 10px 11px !important; border-radius: 11px !important; font-size: 11px !important; line-height: 1.4 !important;
03876:         }
03877:         html[data-mcms-tablet-active="true"] #${SCRIPT.panelId} .mcms-profile-row {
03878:             grid-template-columns: minmax(0,1fr) 54px 54px 44px !important; gap: 7px !important;
03879:         }
```

### Lines 3872-3882
```text
03872:         }
03873:         html[data-mcms-tablet-active="true"] #${SCRIPT.panelId} .mcms-bookmark-name { font-size: 12px !important; }
03874:         html[data-mcms-tablet-active="true"] #${SCRIPT.panelId} .mcms-status {
03875:             margin-top: 10px !important; padding: 10px 11px !important; border-radius: 11px !important; font-size: 11px !important; line-height: 1.4 !important;
03876:         }
03877:         html[data-mcms-tablet-active="true"] #${SCRIPT.panelId} .mcms-profile-row {
03878:             grid-template-columns: minmax(0,1fr) 54px 54px 44px !important; gap: 7px !important;
03879:         }
03880:         html[data-mcms-tablet-active="true"] #${SCRIPT.panelId} .mcms-profile-main { min-height: 52px !important; padding: 9px 10px !important; border-radius: 10px !important; }
03881:         html[data-mcms-tablet-active="true"] #${SCRIPT.panelId} .mcms-profile-main strong { font-size: 11.5px !important; }
03882:         html[data-mcms-tablet-active="true"] #${SCRIPT.panelId} .mcms-profile-main span { font-size: 9.5px !important; }
```

### Lines 3873-3883
```text
03873:         html[data-mcms-tablet-active="true"] #${SCRIPT.panelId} .mcms-bookmark-name { font-size: 12px !important; }
03874:         html[data-mcms-tablet-active="true"] #${SCRIPT.panelId} .mcms-status {
03875:             margin-top: 10px !important; padding: 10px 11px !important; border-radius: 11px !important; font-size: 11px !important; line-height: 1.4 !important;
03876:         }
03877:         html[data-mcms-tablet-active="true"] #${SCRIPT.panelId} .mcms-profile-row {
03878:             grid-template-columns: minmax(0,1fr) 54px 54px 44px !important; gap: 7px !important;
03879:         }
03880:         html[data-mcms-tablet-active="true"] #${SCRIPT.panelId} .mcms-profile-main { min-height: 52px !important; padding: 9px 10px !important; border-radius: 10px !important; }
03881:         html[data-mcms-tablet-active="true"] #${SCRIPT.panelId} .mcms-profile-main strong { font-size: 11.5px !important; }
03882:         html[data-mcms-tablet-active="true"] #${SCRIPT.panelId} .mcms-profile-main span { font-size: 9.5px !important; }
03883:         html[data-mcms-tablet-active="true"] #${SCRIPT.panelId} .mcms-config-actions { gap: 8px !important; }
```

### Lines 3875-3885
```text
03875:             margin-top: 10px !important; padding: 10px 11px !important; border-radius: 11px !important; font-size: 11px !important; line-height: 1.4 !important;
03876:         }
03877:         html[data-mcms-tablet-active="true"] #${SCRIPT.panelId} .mcms-profile-row {
03878:             grid-template-columns: minmax(0,1fr) 54px 54px 44px !important; gap: 7px !important;
03879:         }
03880:         html[data-mcms-tablet-active="true"] #${SCRIPT.panelId} .mcms-profile-main { min-height: 52px !important; padding: 9px 10px !important; border-radius: 10px !important; }
03881:         html[data-mcms-tablet-active="true"] #${SCRIPT.panelId} .mcms-profile-main strong { font-size: 11.5px !important; }
03882:         html[data-mcms-tablet-active="true"] #${SCRIPT.panelId} .mcms-profile-main span { font-size: 9.5px !important; }
03883:         html[data-mcms-tablet-active="true"] #${SCRIPT.panelId} .mcms-config-actions { gap: 8px !important; }
03884:         html[data-mcms-tablet-active="true"] #${SCRIPT.panelId} .mcms-footer { margin-top: 14px !important; padding-top: 11px !important; font-size: 9.5px !important; }
03885:         html[data-mcms-tablet-active="true"] #${SCRIPT.panelId} .mcms-desktop-position-controls { display: none !important; }
```

### Lines 3876-3886
```text
03876:         }
03877:         html[data-mcms-tablet-active="true"] #${SCRIPT.panelId} .mcms-profile-row {
03878:             grid-template-columns: minmax(0,1fr) 54px 54px 44px !important; gap: 7px !important;
03879:         }
03880:         html[data-mcms-tablet-active="true"] #${SCRIPT.panelId} .mcms-profile-main { min-height: 52px !important; padding: 9px 10px !important; border-radius: 10px !important; }
03881:         html[data-mcms-tablet-active="true"] #${SCRIPT.panelId} .mcms-profile-main strong { font-size: 11.5px !important; }
03882:         html[data-mcms-tablet-active="true"] #${SCRIPT.panelId} .mcms-profile-main span { font-size: 9.5px !important; }
03883:         html[data-mcms-tablet-active="true"] #${SCRIPT.panelId} .mcms-config-actions { gap: 8px !important; }
03884:         html[data-mcms-tablet-active="true"] #${SCRIPT.panelId} .mcms-footer { margin-top: 14px !important; padding-top: 11px !important; font-size: 9.5px !important; }
03885:         html[data-mcms-tablet-active="true"] #${SCRIPT.panelId} .mcms-desktop-position-controls { display: none !important; }
03886:         html[data-mcms-tablet-active="true"] #${SCRIPT.panelId}.mcms-map-small { width: auto !important; }
```

### Lines 3877-3887
```text
03877:         html[data-mcms-tablet-active="true"] #${SCRIPT.panelId} .mcms-profile-row {
03878:             grid-template-columns: minmax(0,1fr) 54px 54px 44px !important; gap: 7px !important;
03879:         }
03880:         html[data-mcms-tablet-active="true"] #${SCRIPT.panelId} .mcms-profile-main { min-height: 52px !important; padding: 9px 10px !important; border-radius: 10px !important; }
03881:         html[data-mcms-tablet-active="true"] #${SCRIPT.panelId} .mcms-profile-main strong { font-size: 11.5px !important; }
03882:         html[data-mcms-tablet-active="true"] #${SCRIPT.panelId} .mcms-profile-main span { font-size: 9.5px !important; }
03883:         html[data-mcms-tablet-active="true"] #${SCRIPT.panelId} .mcms-config-actions { gap: 8px !important; }
03884:         html[data-mcms-tablet-active="true"] #${SCRIPT.panelId} .mcms-footer { margin-top: 14px !important; padding-top: 11px !important; font-size: 9.5px !important; }
03885:         html[data-mcms-tablet-active="true"] #${SCRIPT.panelId} .mcms-desktop-position-controls { display: none !important; }
03886:         html[data-mcms-tablet-active="true"] #${SCRIPT.panelId}.mcms-map-small { width: auto !important; }
03887:         html[data-mcms-tablet-active="true"] #${SCRIPT.panelId}.mcms-map-small .mcms-footer { display: block !important; }
```

### Lines 3878-3888
```text
03878:             grid-template-columns: minmax(0,1fr) 54px 54px 44px !important; gap: 7px !important;
03879:         }
03880:         html[data-mcms-tablet-active="true"] #${SCRIPT.panelId} .mcms-profile-main { min-height: 52px !important; padding: 9px 10px !important; border-radius: 10px !important; }
03881:         html[data-mcms-tablet-active="true"] #${SCRIPT.panelId} .mcms-profile-main strong { font-size: 11.5px !important; }
03882:         html[data-mcms-tablet-active="true"] #${SCRIPT.panelId} .mcms-profile-main span { font-size: 9.5px !important; }
03883:         html[data-mcms-tablet-active="true"] #${SCRIPT.panelId} .mcms-config-actions { gap: 8px !important; }
03884:         html[data-mcms-tablet-active="true"] #${SCRIPT.panelId} .mcms-footer { margin-top: 14px !important; padding-top: 11px !important; font-size: 9.5px !important; }
03885:         html[data-mcms-tablet-active="true"] #${SCRIPT.panelId} .mcms-desktop-position-controls { display: none !important; }
03886:         html[data-mcms-tablet-active="true"] #${SCRIPT.panelId}.mcms-map-small { width: auto !important; }
03887:         html[data-mcms-tablet-active="true"] #${SCRIPT.panelId}.mcms-map-small .mcms-footer { display: block !important; }
03888: 
```

### Lines 3879-3889
```text
03879:         }
03880:         html[data-mcms-tablet-active="true"] #${SCRIPT.panelId} .mcms-profile-main { min-height: 52px !important; padding: 9px 10px !important; border-radius: 10px !important; }
03881:         html[data-mcms-tablet-active="true"] #${SCRIPT.panelId} .mcms-profile-main strong { font-size: 11.5px !important; }
03882:         html[data-mcms-tablet-active="true"] #${SCRIPT.panelId} .mcms-profile-main span { font-size: 9.5px !important; }
03883:         html[data-mcms-tablet-active="true"] #${SCRIPT.panelId} .mcms-config-actions { gap: 8px !important; }
03884:         html[data-mcms-tablet-active="true"] #${SCRIPT.panelId} .mcms-footer { margin-top: 14px !important; padding-top: 11px !important; font-size: 9.5px !important; }
03885:         html[data-mcms-tablet-active="true"] #${SCRIPT.panelId} .mcms-desktop-position-controls { display: none !important; }
03886:         html[data-mcms-tablet-active="true"] #${SCRIPT.panelId}.mcms-map-small { width: auto !important; }
03887:         html[data-mcms-tablet-active="true"] #${SCRIPT.panelId}.mcms-map-small .mcms-footer { display: block !important; }
03888: 
03889:         html[data-mcms-tablet-active="true"] #${SCRIPT.criticalDrawerId} {
```

### Lines 3880-3890
```text
03880:         html[data-mcms-tablet-active="true"] #${SCRIPT.panelId} .mcms-profile-main { min-height: 52px !important; padding: 9px 10px !important; border-radius: 10px !important; }
03881:         html[data-mcms-tablet-active="true"] #${SCRIPT.panelId} .mcms-profile-main strong { font-size: 11.5px !important; }
03882:         html[data-mcms-tablet-active="true"] #${SCRIPT.panelId} .mcms-profile-main span { font-size: 9.5px !important; }
03883:         html[data-mcms-tablet-active="true"] #${SCRIPT.panelId} .mcms-config-actions { gap: 8px !important; }
03884:         html[data-mcms-tablet-active="true"] #${SCRIPT.panelId} .mcms-footer { margin-top: 14px !important; padding-top: 11px !important; font-size: 9.5px !important; }
03885:         html[data-mcms-tablet-active="true"] #${SCRIPT.panelId} .mcms-desktop-position-controls { display: none !important; }
03886:         html[data-mcms-tablet-active="true"] #${SCRIPT.panelId}.mcms-map-small { width: auto !important; }
03887:         html[data-mcms-tablet-active="true"] #${SCRIPT.panelId}.mcms-map-small .mcms-footer { display: block !important; }
03888: 
03889:         html[data-mcms-tablet-active="true"] #${SCRIPT.criticalDrawerId} {
03890:             left: 50% !important; right: auto !important; top: auto !important; bottom: max(8px, env(safe-area-inset-bottom)) !important;
```

### Lines 3881-3891
```text
03881:         html[data-mcms-tablet-active="true"] #${SCRIPT.panelId} .mcms-profile-main strong { font-size: 11.5px !important; }
03882:         html[data-mcms-tablet-active="true"] #${SCRIPT.panelId} .mcms-profile-main span { font-size: 9.5px !important; }
03883:         html[data-mcms-tablet-active="true"] #${SCRIPT.panelId} .mcms-config-actions { gap: 8px !important; }
03884:         html[data-mcms-tablet-active="true"] #${SCRIPT.panelId} .mcms-footer { margin-top: 14px !important; padding-top: 11px !important; font-size: 9.5px !important; }
03885:         html[data-mcms-tablet-active="true"] #${SCRIPT.panelId} .mcms-desktop-position-controls { display: none !important; }
03886:         html[data-mcms-tablet-active="true"] #${SCRIPT.panelId}.mcms-map-small { width: auto !important; }
03887:         html[data-mcms-tablet-active="true"] #${SCRIPT.panelId}.mcms-map-small .mcms-footer { display: block !important; }
03888: 
03889:         html[data-mcms-tablet-active="true"] #${SCRIPT.criticalDrawerId} {
03890:             left: 50% !important; right: auto !important; top: auto !important; bottom: max(8px, env(safe-area-inset-bottom)) !important;
03891:             width: min(700px, calc(100vw - 16px)) !important; max-width: calc(100vw - 16px) !important; max-height: 78dvh !important;
```

### Lines 3882-3892
```text
03882:         html[data-mcms-tablet-active="true"] #${SCRIPT.panelId} .mcms-profile-main span { font-size: 9.5px !important; }
03883:         html[data-mcms-tablet-active="true"] #${SCRIPT.panelId} .mcms-config-actions { gap: 8px !important; }
03884:         html[data-mcms-tablet-active="true"] #${SCRIPT.panelId} .mcms-footer { margin-top: 14px !important; padding-top: 11px !important; font-size: 9.5px !important; }
03885:         html[data-mcms-tablet-active="true"] #${SCRIPT.panelId} .mcms-desktop-position-controls { display: none !important; }
03886:         html[data-mcms-tablet-active="true"] #${SCRIPT.panelId}.mcms-map-small { width: auto !important; }
03887:         html[data-mcms-tablet-active="true"] #${SCRIPT.panelId}.mcms-map-small .mcms-footer { display: block !important; }
03888: 
03889:         html[data-mcms-tablet-active="true"] #${SCRIPT.criticalDrawerId} {
03890:             left: 50% !important; right: auto !important; top: auto !important; bottom: max(8px, env(safe-area-inset-bottom)) !important;
03891:             width: min(700px, calc(100vw - 16px)) !important; max-width: calc(100vw - 16px) !important; max-height: 78dvh !important;
03892:             transform: translateX(-50%) !important; padding: 12px !important; border-radius: 18px !important;
```

### Lines 3884-3894
```text
03884:         html[data-mcms-tablet-active="true"] #${SCRIPT.panelId} .mcms-footer { margin-top: 14px !important; padding-top: 11px !important; font-size: 9.5px !important; }
03885:         html[data-mcms-tablet-active="true"] #${SCRIPT.panelId} .mcms-desktop-position-controls { display: none !important; }
03886:         html[data-mcms-tablet-active="true"] #${SCRIPT.panelId}.mcms-map-small { width: auto !important; }
03887:         html[data-mcms-tablet-active="true"] #${SCRIPT.panelId}.mcms-map-small .mcms-footer { display: block !important; }
03888: 
03889:         html[data-mcms-tablet-active="true"] #${SCRIPT.criticalDrawerId} {
03890:             left: 50% !important; right: auto !important; top: auto !important; bottom: max(8px, env(safe-area-inset-bottom)) !important;
03891:             width: min(700px, calc(100vw - 16px)) !important; max-width: calc(100vw - 16px) !important; max-height: 78dvh !important;
03892:             transform: translateX(-50%) !important; padding: 12px !important; border-radius: 18px !important;
03893:             background: rgba(8,12,18,.985) !important; backdrop-filter: none !important; -webkit-backdrop-filter: none !important;
03894:             overscroll-behavior: contain !important; -webkit-overflow-scrolling: touch !important;
```

### Lines 3891-3901
```text
03891:             width: min(700px, calc(100vw - 16px)) !important; max-width: calc(100vw - 16px) !important; max-height: 78dvh !important;
03892:             transform: translateX(-50%) !important; padding: 12px !important; border-radius: 18px !important;
03893:             background: rgba(8,12,18,.985) !important; backdrop-filter: none !important; -webkit-backdrop-filter: none !important;
03894:             overscroll-behavior: contain !important; -webkit-overflow-scrolling: touch !important;
03895:         }
03896:         html[data-mcms-tablet-active="true"] #${SCRIPT.criticalDrawerId} .mcms-drawer-head { grid-template-columns: minmax(0,1fr) 44px !important; min-height: 52px !important; }
03897:         html[data-mcms-tablet-active="true"] #${SCRIPT.criticalDrawerId} .mcms-drawer-title { font-size: 15px !important; }
03898:         html[data-mcms-tablet-active="true"] #${SCRIPT.criticalDrawerId} .mcms-drawer-subtitle { font-size: 10px !important; }
03899:         html[data-mcms-tablet-active="true"] #${SCRIPT.criticalDrawerId} .mcms-drawer-close { width: 44px !important; height: 44px !important; border-radius: 11px !important; font-size: 20px !important; }
03900:         html[data-mcms-tablet-active="true"] #${SCRIPT.criticalDrawerId} .mcms-critical-row { min-height: 56px !important; grid-template-columns: 112px minmax(0,1fr) auto !important; gap: 10px !important; padding: 10px !important; border-radius: 11px !important; }
03901:         html[data-mcms-tablet-active="true"] #${SCRIPT.criticalDrawerId} .mcms-critical-name { font-size: 12px !important; }
```

### Lines 3892-3902
```text
03892:             transform: translateX(-50%) !important; padding: 12px !important; border-radius: 18px !important;
03893:             background: rgba(8,12,18,.985) !important; backdrop-filter: none !important; -webkit-backdrop-filter: none !important;
03894:             overscroll-behavior: contain !important; -webkit-overflow-scrolling: touch !important;
03895:         }
03896:         html[data-mcms-tablet-active="true"] #${SCRIPT.criticalDrawerId} .mcms-drawer-head { grid-template-columns: minmax(0,1fr) 44px !important; min-height: 52px !important; }
03897:         html[data-mcms-tablet-active="true"] #${SCRIPT.criticalDrawerId} .mcms-drawer-title { font-size: 15px !important; }
03898:         html[data-mcms-tablet-active="true"] #${SCRIPT.criticalDrawerId} .mcms-drawer-subtitle { font-size: 10px !important; }
03899:         html[data-mcms-tablet-active="true"] #${SCRIPT.criticalDrawerId} .mcms-drawer-close { width: 44px !important; height: 44px !important; border-radius: 11px !important; font-size: 20px !important; }
03900:         html[data-mcms-tablet-active="true"] #${SCRIPT.criticalDrawerId} .mcms-critical-row { min-height: 56px !important; grid-template-columns: 112px minmax(0,1fr) auto !important; gap: 10px !important; padding: 10px !important; border-radius: 11px !important; }
03901:         html[data-mcms-tablet-active="true"] #${SCRIPT.criticalDrawerId} .mcms-critical-name { font-size: 12px !important; }
03902:         html[data-mcms-tablet-active="true"] #${SCRIPT.criticalDrawerId} .mcms-critical-meta,
```

### Lines 3893-3903
```text
03893:             background: rgba(8,12,18,.985) !important; backdrop-filter: none !important; -webkit-backdrop-filter: none !important;
03894:             overscroll-behavior: contain !important; -webkit-overflow-scrolling: touch !important;
03895:         }
03896:         html[data-mcms-tablet-active="true"] #${SCRIPT.criticalDrawerId} .mcms-drawer-head { grid-template-columns: minmax(0,1fr) 44px !important; min-height: 52px !important; }
03897:         html[data-mcms-tablet-active="true"] #${SCRIPT.criticalDrawerId} .mcms-drawer-title { font-size: 15px !important; }
03898:         html[data-mcms-tablet-active="true"] #${SCRIPT.criticalDrawerId} .mcms-drawer-subtitle { font-size: 10px !important; }
03899:         html[data-mcms-tablet-active="true"] #${SCRIPT.criticalDrawerId} .mcms-drawer-close { width: 44px !important; height: 44px !important; border-radius: 11px !important; font-size: 20px !important; }
03900:         html[data-mcms-tablet-active="true"] #${SCRIPT.criticalDrawerId} .mcms-critical-row { min-height: 56px !important; grid-template-columns: 112px minmax(0,1fr) auto !important; gap: 10px !important; padding: 10px !important; border-radius: 11px !important; }
03901:         html[data-mcms-tablet-active="true"] #${SCRIPT.criticalDrawerId} .mcms-critical-name { font-size: 12px !important; }
03902:         html[data-mcms-tablet-active="true"] #${SCRIPT.criticalDrawerId} .mcms-critical-meta,
03903:         html[data-mcms-tablet-active="true"] #${SCRIPT.criticalDrawerId} .mcms-critical-age-band { font-size: 9.5px !important; }
```

### Lines 3894-3904
```text
03894:             overscroll-behavior: contain !important; -webkit-overflow-scrolling: touch !important;
03895:         }
03896:         html[data-mcms-tablet-active="true"] #${SCRIPT.criticalDrawerId} .mcms-drawer-head { grid-template-columns: minmax(0,1fr) 44px !important; min-height: 52px !important; }
03897:         html[data-mcms-tablet-active="true"] #${SCRIPT.criticalDrawerId} .mcms-drawer-title { font-size: 15px !important; }
03898:         html[data-mcms-tablet-active="true"] #${SCRIPT.criticalDrawerId} .mcms-drawer-subtitle { font-size: 10px !important; }
03899:         html[data-mcms-tablet-active="true"] #${SCRIPT.criticalDrawerId} .mcms-drawer-close { width: 44px !important; height: 44px !important; border-radius: 11px !important; font-size: 20px !important; }
03900:         html[data-mcms-tablet-active="true"] #${SCRIPT.criticalDrawerId} .mcms-critical-row { min-height: 56px !important; grid-template-columns: 112px minmax(0,1fr) auto !important; gap: 10px !important; padding: 10px !important; border-radius: 11px !important; }
03901:         html[data-mcms-tablet-active="true"] #${SCRIPT.criticalDrawerId} .mcms-critical-name { font-size: 12px !important; }
03902:         html[data-mcms-tablet-active="true"] #${SCRIPT.criticalDrawerId} .mcms-critical-meta,
03903:         html[data-mcms-tablet-active="true"] #${SCRIPT.criticalDrawerId} .mcms-critical-age-band { font-size: 9.5px !important; }
03904:         html[data-mcms-tablet-active="true"] #${SCRIPT.criticalDrawerId} .mcms-critical-age { font-size: 11px !important; }
```

### Lines 3895-3905
```text
03895:         }
03896:         html[data-mcms-tablet-active="true"] #${SCRIPT.criticalDrawerId} .mcms-drawer-head { grid-template-columns: minmax(0,1fr) 44px !important; min-height: 52px !important; }
03897:         html[data-mcms-tablet-active="true"] #${SCRIPT.criticalDrawerId} .mcms-drawer-title { font-size: 15px !important; }
03898:         html[data-mcms-tablet-active="true"] #${SCRIPT.criticalDrawerId} .mcms-drawer-subtitle { font-size: 10px !important; }
03899:         html[data-mcms-tablet-active="true"] #${SCRIPT.criticalDrawerId} .mcms-drawer-close { width: 44px !important; height: 44px !important; border-radius: 11px !important; font-size: 20px !important; }
03900:         html[data-mcms-tablet-active="true"] #${SCRIPT.criticalDrawerId} .mcms-critical-row { min-height: 56px !important; grid-template-columns: 112px minmax(0,1fr) auto !important; gap: 10px !important; padding: 10px !important; border-radius: 11px !important; }
03901:         html[data-mcms-tablet-active="true"] #${SCRIPT.criticalDrawerId} .mcms-critical-name { font-size: 12px !important; }
03902:         html[data-mcms-tablet-active="true"] #${SCRIPT.criticalDrawerId} .mcms-critical-meta,
03903:         html[data-mcms-tablet-active="true"] #${SCRIPT.criticalDrawerId} .mcms-critical-age-band { font-size: 9.5px !important; }
03904:         html[data-mcms-tablet-active="true"] #${SCRIPT.criticalDrawerId} .mcms-critical-age { font-size: 11px !important; }
03905: 
```

### Lines 3896-3906
```text
03896:         html[data-mcms-tablet-active="true"] #${SCRIPT.criticalDrawerId} .mcms-drawer-head { grid-template-columns: minmax(0,1fr) 44px !important; min-height: 52px !important; }
03897:         html[data-mcms-tablet-active="true"] #${SCRIPT.criticalDrawerId} .mcms-drawer-title { font-size: 15px !important; }
03898:         html[data-mcms-tablet-active="true"] #${SCRIPT.criticalDrawerId} .mcms-drawer-subtitle { font-size: 10px !important; }
03899:         html[data-mcms-tablet-active="true"] #${SCRIPT.criticalDrawerId} .mcms-drawer-close { width: 44px !important; height: 44px !important; border-radius: 11px !important; font-size: 20px !important; }
03900:         html[data-mcms-tablet-active="true"] #${SCRIPT.criticalDrawerId} .mcms-critical-row { min-height: 56px !important; grid-template-columns: 112px minmax(0,1fr) auto !important; gap: 10px !important; padding: 10px !important; border-radius: 11px !important; }
03901:         html[data-mcms-tablet-active="true"] #${SCRIPT.criticalDrawerId} .mcms-critical-name { font-size: 12px !important; }
03902:         html[data-mcms-tablet-active="true"] #${SCRIPT.criticalDrawerId} .mcms-critical-meta,
03903:         html[data-mcms-tablet-active="true"] #${SCRIPT.criticalDrawerId} .mcms-critical-age-band { font-size: 9.5px !important; }
03904:         html[data-mcms-tablet-active="true"] #${SCRIPT.criticalDrawerId} .mcms-critical-age { font-size: 11px !important; }
03905: 
03906:         html[data-mcms-tablet-active="true"] #${SCRIPT.missionInspectorId} {
```

### Lines 3897-3907
```text
03897:         html[data-mcms-tablet-active="true"] #${SCRIPT.criticalDrawerId} .mcms-drawer-title { font-size: 15px !important; }
03898:         html[data-mcms-tablet-active="true"] #${SCRIPT.criticalDrawerId} .mcms-drawer-subtitle { font-size: 10px !important; }
03899:         html[data-mcms-tablet-active="true"] #${SCRIPT.criticalDrawerId} .mcms-drawer-close { width: 44px !important; height: 44px !important; border-radius: 11px !important; font-size: 20px !important; }
03900:         html[data-mcms-tablet-active="true"] #${SCRIPT.criticalDrawerId} .mcms-critical-row { min-height: 56px !important; grid-template-columns: 112px minmax(0,1fr) auto !important; gap: 10px !important; padding: 10px !important; border-radius: 11px !important; }
03901:         html[data-mcms-tablet-active="true"] #${SCRIPT.criticalDrawerId} .mcms-critical-name { font-size: 12px !important; }
03902:         html[data-mcms-tablet-active="true"] #${SCRIPT.criticalDrawerId} .mcms-critical-meta,
03903:         html[data-mcms-tablet-active="true"] #${SCRIPT.criticalDrawerId} .mcms-critical-age-band { font-size: 9.5px !important; }
03904:         html[data-mcms-tablet-active="true"] #${SCRIPT.criticalDrawerId} .mcms-critical-age { font-size: 11px !important; }
03905: 
03906:         html[data-mcms-tablet-active="true"] #${SCRIPT.missionInspectorId} {
03907:             width: min(420px, calc(100vw - 20px)) !important; padding: 12px 13px !important;
```

### Lines 3898-3908
```text
03898:         html[data-mcms-tablet-active="true"] #${SCRIPT.criticalDrawerId} .mcms-drawer-subtitle { font-size: 10px !important; }
03899:         html[data-mcms-tablet-active="true"] #${SCRIPT.criticalDrawerId} .mcms-drawer-close { width: 44px !important; height: 44px !important; border-radius: 11px !important; font-size: 20px !important; }
03900:         html[data-mcms-tablet-active="true"] #${SCRIPT.criticalDrawerId} .mcms-critical-row { min-height: 56px !important; grid-template-columns: 112px minmax(0,1fr) auto !important; gap: 10px !important; padding: 10px !important; border-radius: 11px !important; }
03901:         html[data-mcms-tablet-active="true"] #${SCRIPT.criticalDrawerId} .mcms-critical-name { font-size: 12px !important; }
03902:         html[data-mcms-tablet-active="true"] #${SCRIPT.criticalDrawerId} .mcms-critical-meta,
03903:         html[data-mcms-tablet-active="true"] #${SCRIPT.criticalDrawerId} .mcms-critical-age-band { font-size: 9.5px !important; }
03904:         html[data-mcms-tablet-active="true"] #${SCRIPT.criticalDrawerId} .mcms-critical-age { font-size: 11px !important; }
03905: 
03906:         html[data-mcms-tablet-active="true"] #${SCRIPT.missionInspectorId} {
03907:             width: min(420px, calc(100vw - 20px)) !important; padding: 12px 13px !important;
03908:             font-size: 12px !important; backdrop-filter: none !important; -webkit-backdrop-filter: none !important;
```

### Lines 3899-3909
```text
03899:         html[data-mcms-tablet-active="true"] #${SCRIPT.criticalDrawerId} .mcms-drawer-close { width: 44px !important; height: 44px !important; border-radius: 11px !important; font-size: 20px !important; }
03900:         html[data-mcms-tablet-active="true"] #${SCRIPT.criticalDrawerId} .mcms-critical-row { min-height: 56px !important; grid-template-columns: 112px minmax(0,1fr) auto !important; gap: 10px !important; padding: 10px !important; border-radius: 11px !important; }
03901:         html[data-mcms-tablet-active="true"] #${SCRIPT.criticalDrawerId} .mcms-critical-name { font-size: 12px !important; }
03902:         html[data-mcms-tablet-active="true"] #${SCRIPT.criticalDrawerId} .mcms-critical-meta,
03903:         html[data-mcms-tablet-active="true"] #${SCRIPT.criticalDrawerId} .mcms-critical-age-band { font-size: 9.5px !important; }
03904:         html[data-mcms-tablet-active="true"] #${SCRIPT.criticalDrawerId} .mcms-critical-age { font-size: 11px !important; }
03905: 
03906:         html[data-mcms-tablet-active="true"] #${SCRIPT.missionInspectorId} {
03907:             width: min(420px, calc(100vw - 20px)) !important; padding: 12px 13px !important;
03908:             font-size: 12px !important; backdrop-filter: none !important; -webkit-backdrop-filter: none !important;
03909:         }
```

### Lines 3901-3911
```text
03901:         html[data-mcms-tablet-active="true"] #${SCRIPT.criticalDrawerId} .mcms-critical-name { font-size: 12px !important; }
03902:         html[data-mcms-tablet-active="true"] #${SCRIPT.criticalDrawerId} .mcms-critical-meta,
03903:         html[data-mcms-tablet-active="true"] #${SCRIPT.criticalDrawerId} .mcms-critical-age-band { font-size: 9.5px !important; }
03904:         html[data-mcms-tablet-active="true"] #${SCRIPT.criticalDrawerId} .mcms-critical-age { font-size: 11px !important; }
03905: 
03906:         html[data-mcms-tablet-active="true"] #${SCRIPT.missionInspectorId} {
03907:             width: min(420px, calc(100vw - 20px)) !important; padding: 12px 13px !important;
03908:             font-size: 12px !important; backdrop-filter: none !important; -webkit-backdrop-filter: none !important;
03909:         }
03910:         html[data-mcms-tablet-active="true"] #${SCRIPT.toastId} {
03911:             max-width: min(420px, calc(100vw - 24px)) !important; padding: 10px 13px !important; font-size: 12px !important;
```

### Lines 3905-3915
```text
03905: 
03906:         html[data-mcms-tablet-active="true"] #${SCRIPT.missionInspectorId} {
03907:             width: min(420px, calc(100vw - 20px)) !important; padding: 12px 13px !important;
03908:             font-size: 12px !important; backdrop-filter: none !important; -webkit-backdrop-filter: none !important;
03909:         }
03910:         html[data-mcms-tablet-active="true"] #${SCRIPT.toastId} {
03911:             max-width: min(420px, calc(100vw - 24px)) !important; padding: 10px 13px !important; font-size: 12px !important;
03912:         }
03913: 
03914:         @media (max-width: 560px) {
03915:             html[data-mcms-tablet-active="true"] #${SCRIPT.panelId} .mcms-grid-2 { grid-template-columns: 1fr !important; }
```

### Lines 3909-3919
```text
03909:         }
03910:         html[data-mcms-tablet-active="true"] #${SCRIPT.toastId} {
03911:             max-width: min(420px, calc(100vw - 24px)) !important; padding: 10px 13px !important; font-size: 12px !important;
03912:         }
03913: 
03914:         @media (max-width: 560px) {
03915:             html[data-mcms-tablet-active="true"] #${SCRIPT.panelId} .mcms-grid-2 { grid-template-columns: 1fr !important; }
03916:             html[data-mcms-tablet-active="true"] #${SCRIPT.panelId} .mcms-grid-2 [data-toggle="criticalView"] { grid-column: auto !important; }
03917:             html[data-mcms-tablet-active="true"] #${SCRIPT.panelId} .mcms-row,
03918:             html[data-mcms-tablet-active="true"] #${SCRIPT.panelId} .mcms-discord-wide { grid-template-columns: 1fr !important; }
03919:             html[data-mcms-tablet-active="true"] #${SCRIPT.panelId} .mcms-row-label { white-space: normal !important; }
```

### Lines 3910-3920
```text
03910:         html[data-mcms-tablet-active="true"] #${SCRIPT.toastId} {
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
```

### Lines 3911-3921
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
```

### Lines 3912-3922
```text
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
```

### Lines 3913-3923
```text
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
```

### Lines 3914-3924
```text
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
```

### Lines 3937-3947
```text
03937:         }
03938:         html[data-mcms-mobile-active="true"] #${SCRIPT.controlId} {
03939:             width: var(--mcms-mobile-dock-width, calc(100% - 10px)) !important;
03940:             max-width: var(--mcms-mobile-dock-width, calc(100% - 10px)) !important;
03941:             display: grid !important;
03942:             grid-template-columns: repeat(var(--mcms-mobile-columns, 5), minmax(0,1fr)) !important;
03943:             grid-auto-flow: row !important;
03944:             align-items: stretch !important;
03945:             gap: 4px !important;
03946:             margin: 0 !important;
03947:             font-size: 10px !important;
```

### Lines 3959-3969
```text
03959:             backdrop-filter: none !important; -webkit-backdrop-filter: none !important; pointer-events: auto !important;
03960:         }
03961:         html[data-mcms-mobile-active="true"] #${SCRIPT.controlId} .mcms-menu-btn { font-size: 19px !important; }
03962:         html[data-mcms-mobile-active="true"] #${SCRIPT.controlId} .mcms-dock-toggle-btn { height: 14px !important; flex-basis: 14px !important; font-size: 10px !important; }
03963:         html[data-mcms-command-bar-open="false"][data-mcms-mobile-active="true"] #${SCRIPT.controlId} {
03964:             width: 50px !important; max-width: 50px !important; grid-template-columns: 50px !important;
03965:         }
03966:         html[data-mcms-mobile-active="true"] #${SCRIPT.controlId} .mcms-floating-filter {
03967:             display: contents !important; grid-area: auto !important; width: auto !important; max-width: none !important;
03968:             overflow: visible !important; padding: 0 !important; margin: 0 !important; pointer-events: none !important;
03969:         }
```

### Lines 3969-3979
```text
03969:         }
03970:         html[data-mcms-mobile-active="true"] #${SCRIPT.controlId} .mcms-floating-filter [data-toggle="criticalView"] { grid-column: auto !important; }
03971:         html[data-mcms-mobile-active="true"] #${SCRIPT.controlId} .mcms-float-btn {
03972:             position: relative !important; isolation: isolate !important; width: auto !important; min-width: 0 !important;
03973:             height: var(--mcms-mobile-filter-height,44px) !important; display: grid !important;
03974:             grid-template-columns: 17px minmax(0,1fr) !important; gap: 3px !important; padding: 0 4px !important;
03975:             border-radius: 10px !important; border: 1px solid rgba(255,255,255,.18) !important;
03976:             background: linear-gradient(180deg,rgba(13,19,27,.98),rgba(6,9,14,.98)) !important;
03977:             color: rgba(255,255,255,.78) !important; box-shadow: 0 3px 10px rgba(0,0,0,.38),inset 0 1px rgba(255,255,255,.04) !important;
03978:             backdrop-filter: none !important; -webkit-backdrop-filter: none !important; pointer-events: auto !important;
03979:             transition: background 110ms ease,border-color 110ms ease,box-shadow 110ms ease,color 110ms ease,opacity 110ms ease,transform 110ms ease !important;
```

### Lines 4004-4014
```text
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
```

### Lines 4010-4020
```text
04010:             font-size:clamp(7.5px,2.15vw,9px) !important; line-height:1 !important; font-weight:950 !important; letter-spacing:-.15px !important;
04011:             text-align:left !important; text-shadow:0 1px 2px rgba(0,0,0,.78) !important;
04012:         }
04013:         html[data-mcms-mobile-active="true"] #${SCRIPT.controlId} .mcms-screen-pins {
04014:             grid-area:auto !important; grid-column:1 / -1 !important; display:grid !important;
04015:             grid-template-columns:repeat(var(--mcms-mobile-pin-columns,4),minmax(0,1fr)) !important;
04016:             grid-auto-flow:row !important; justify-self:stretch !important; align-self:stretch !important;
04017:             justify-items:stretch !important; align-items:stretch !important;
04018:             gap:4px !important; width:100% !important; min-width:0 !important; max-width:none !important; max-height:none !important;
04019:             box-sizing:border-box !important; margin:0 !important; padding:0 !important;
04020:             overflow:visible !important; pointer-events:none !important;
```

### Lines 4025-4035
```text
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
```

### Lines 4026-4036
```text
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
```

### Lines 4039-4049
```text
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
```

### Lines 4041-4051
```text
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
```

### Lines 4044-4054
```text
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
```

### Lines 4054-4064
```text
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
```

### Lines 4059-4069
```text
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
```

### Lines 4070-4080
```text
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
```

### Lines 4071-4081
```text
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
```

### Lines 4072-4082
```text
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
```

### Lines 4085-4095
```text
04085:         html[data-mcms-mobile-active="true"] #${SCRIPT.panelId} .mcms-small-btn,
04086:         html[data-mcms-mobile-active="true"] #${SCRIPT.panelId} .mcms-bookmark-btn,
04087:         html[data-mcms-mobile-active="true"] #${SCRIPT.panelId} .mcms-pin-btn { min-height:44px !important; height:44px !important; line-height:42px !important; border-radius:10px !important; font-size:10px !important; }
04088:         html[data-mcms-mobile-active="true"] #${SCRIPT.panelId} .mcms-position-grid,
04089:         html[data-mcms-mobile-active="true"] #${SCRIPT.panelId} .mcms-nudge-grid { gap:6px !important; }
04090:         html[data-mcms-mobile-active="true"] #${SCRIPT.panelId} .mcms-quick-row { grid-template-columns:minmax(0,1fr) 58px !important; gap:6px !important; }
04091:         html[data-mcms-mobile-active="true"] #${SCRIPT.panelId} .mcms-bookmark-row { grid-template-columns:minmax(0,1fr) 44px 50px 44px 40px !important; gap:4px !important; }
04092:         html[data-mcms-mobile-active="true"] #${SCRIPT.panelId} .mcms-bookmark-name { font-size:10.5px !important; }
04093:         html[data-mcms-mobile-active="true"] #${SCRIPT.panelId} .mcms-status { font-size:9.5px !important; line-height:1.35 !important; }
04094:         html[data-mcms-mobile-active="true"] #${SCRIPT.panelId} .mcms-discord-wide { grid-template-columns:1fr !important; }
04095:         html[data-mcms-mobile-active="true"] #${SCRIPT.panelId} .mcms-discord-date-grid { grid-template-columns:1fr !important; }
```

### Lines 4086-4096
```text
04086:         html[data-mcms-mobile-active="true"] #${SCRIPT.panelId} .mcms-bookmark-btn,
04087:         html[data-mcms-mobile-active="true"] #${SCRIPT.panelId} .mcms-pin-btn { min-height:44px !important; height:44px !important; line-height:42px !important; border-radius:10px !important; font-size:10px !important; }
04088:         html[data-mcms-mobile-active="true"] #${SCRIPT.panelId} .mcms-position-grid,
04089:         html[data-mcms-mobile-active="true"] #${SCRIPT.panelId} .mcms-nudge-grid { gap:6px !important; }
04090:         html[data-mcms-mobile-active="true"] #${SCRIPT.panelId} .mcms-quick-row { grid-template-columns:minmax(0,1fr) 58px !important; gap:6px !important; }
04091:         html[data-mcms-mobile-active="true"] #${SCRIPT.panelId} .mcms-bookmark-row { grid-template-columns:minmax(0,1fr) 44px 50px 44px 40px !important; gap:4px !important; }
04092:         html[data-mcms-mobile-active="true"] #${SCRIPT.panelId} .mcms-bookmark-name { font-size:10.5px !important; }
04093:         html[data-mcms-mobile-active="true"] #${SCRIPT.panelId} .mcms-status { font-size:9.5px !important; line-height:1.35 !important; }
04094:         html[data-mcms-mobile-active="true"] #${SCRIPT.panelId} .mcms-discord-wide { grid-template-columns:1fr !important; }
04095:         html[data-mcms-mobile-active="true"] #${SCRIPT.panelId} .mcms-discord-date-grid { grid-template-columns:1fr !important; }
04096:         html[data-mcms-mobile-active="true"] #${SCRIPT.panelId} .mcms-finance-vault-summary { grid-template-columns:repeat(2,minmax(0,1fr)) !important; }
```

### Lines 4089-4099
```text
04089:         html[data-mcms-mobile-active="true"] #${SCRIPT.panelId} .mcms-nudge-grid { gap:6px !important; }
04090:         html[data-mcms-mobile-active="true"] #${SCRIPT.panelId} .mcms-quick-row { grid-template-columns:minmax(0,1fr) 58px !important; gap:6px !important; }
04091:         html[data-mcms-mobile-active="true"] #${SCRIPT.panelId} .mcms-bookmark-row { grid-template-columns:minmax(0,1fr) 44px 50px 44px 40px !important; gap:4px !important; }
04092:         html[data-mcms-mobile-active="true"] #${SCRIPT.panelId} .mcms-bookmark-name { font-size:10.5px !important; }
04093:         html[data-mcms-mobile-active="true"] #${SCRIPT.panelId} .mcms-status { font-size:9.5px !important; line-height:1.35 !important; }
04094:         html[data-mcms-mobile-active="true"] #${SCRIPT.panelId} .mcms-discord-wide { grid-template-columns:1fr !important; }
04095:         html[data-mcms-mobile-active="true"] #${SCRIPT.panelId} .mcms-discord-date-grid { grid-template-columns:1fr !important; }
04096:         html[data-mcms-mobile-active="true"] #${SCRIPT.panelId} .mcms-finance-vault-summary { grid-template-columns:repeat(2,minmax(0,1fr)) !important; }
04097:         html[data-mcms-mobile-active="true"] #${SCRIPT.panelId} .mcms-profile-row { grid-template-columns:minmax(0,1fr) 44px 44px 40px !important; gap:4px !important; }
04098:         html[data-mcms-mobile-active="true"] #${SCRIPT.panelId} .mcms-profile-main { min-height:44px !important; }
04099:         html[data-mcms-mobile-active="true"] #${SCRIPT.panelId} .mcms-desktop-position-controls { display:none !important; }
```

### Lines 4090-4100
```text
04090:         html[data-mcms-mobile-active="true"] #${SCRIPT.panelId} .mcms-quick-row { grid-template-columns:minmax(0,1fr) 58px !important; gap:6px !important; }
04091:         html[data-mcms-mobile-active="true"] #${SCRIPT.panelId} .mcms-bookmark-row { grid-template-columns:minmax(0,1fr) 44px 50px 44px 40px !important; gap:4px !important; }
04092:         html[data-mcms-mobile-active="true"] #${SCRIPT.panelId} .mcms-bookmark-name { font-size:10.5px !important; }
04093:         html[data-mcms-mobile-active="true"] #${SCRIPT.panelId} .mcms-status { font-size:9.5px !important; line-height:1.35 !important; }
04094:         html[data-mcms-mobile-active="true"] #${SCRIPT.panelId} .mcms-discord-wide { grid-template-columns:1fr !important; }
04095:         html[data-mcms-mobile-active="true"] #${SCRIPT.panelId} .mcms-discord-date-grid { grid-template-columns:1fr !important; }
04096:         html[data-mcms-mobile-active="true"] #${SCRIPT.panelId} .mcms-finance-vault-summary { grid-template-columns:repeat(2,minmax(0,1fr)) !important; }
04097:         html[data-mcms-mobile-active="true"] #${SCRIPT.panelId} .mcms-profile-row { grid-template-columns:minmax(0,1fr) 44px 44px 40px !important; gap:4px !important; }
04098:         html[data-mcms-mobile-active="true"] #${SCRIPT.panelId} .mcms-profile-main { min-height:44px !important; }
04099:         html[data-mcms-mobile-active="true"] #${SCRIPT.panelId} .mcms-desktop-position-controls { display:none !important; }
04100:         html[data-mcms-mobile-active="true"] #${SCRIPT.panelId} .mcms-footer { display:none !important; }
```

### Lines 4091-4101
```text
04091:         html[data-mcms-mobile-active="true"] #${SCRIPT.panelId} .mcms-bookmark-row { grid-template-columns:minmax(0,1fr) 44px 50px 44px 40px !important; gap:4px !important; }
04092:         html[data-mcms-mobile-active="true"] #${SCRIPT.panelId} .mcms-bookmark-name { font-size:10.5px !important; }
04093:         html[data-mcms-mobile-active="true"] #${SCRIPT.panelId} .mcms-status { font-size:9.5px !important; line-height:1.35 !important; }
04094:         html[data-mcms-mobile-active="true"] #${SCRIPT.panelId} .mcms-discord-wide { grid-template-columns:1fr !important; }
04095:         html[data-mcms-mobile-active="true"] #${SCRIPT.panelId} .mcms-discord-date-grid { grid-template-columns:1fr !important; }
04096:         html[data-mcms-mobile-active="true"] #${SCRIPT.panelId} .mcms-finance-vault-summary { grid-template-columns:repeat(2,minmax(0,1fr)) !important; }
04097:         html[data-mcms-mobile-active="true"] #${SCRIPT.panelId} .mcms-profile-row { grid-template-columns:minmax(0,1fr) 44px 44px 40px !important; gap:4px !important; }
04098:         html[data-mcms-mobile-active="true"] #${SCRIPT.panelId} .mcms-profile-main { min-height:44px !important; }
04099:         html[data-mcms-mobile-active="true"] #${SCRIPT.panelId} .mcms-desktop-position-controls { display:none !important; }
04100:         html[data-mcms-mobile-active="true"] #${SCRIPT.panelId} .mcms-footer { display:none !important; }
04101:         html[data-mcms-mobile-active="true"] #${SCRIPT.criticalDrawerId} {
```

### Lines 4092-4102
```text
04092:         html[data-mcms-mobile-active="true"] #${SCRIPT.panelId} .mcms-bookmark-name { font-size:10.5px !important; }
04093:         html[data-mcms-mobile-active="true"] #${SCRIPT.panelId} .mcms-status { font-size:9.5px !important; line-height:1.35 !important; }
04094:         html[data-mcms-mobile-active="true"] #${SCRIPT.panelId} .mcms-discord-wide { grid-template-columns:1fr !important; }
04095:         html[data-mcms-mobile-active="true"] #${SCRIPT.panelId} .mcms-discord-date-grid { grid-template-columns:1fr !important; }
04096:         html[data-mcms-mobile-active="true"] #${SCRIPT.panelId} .mcms-finance-vault-summary { grid-template-columns:repeat(2,minmax(0,1fr)) !important; }
04097:         html[data-mcms-mobile-active="true"] #${SCRIPT.panelId} .mcms-profile-row { grid-template-columns:minmax(0,1fr) 44px 44px 40px !important; gap:4px !important; }
04098:         html[data-mcms-mobile-active="true"] #${SCRIPT.panelId} .mcms-profile-main { min-height:44px !important; }
04099:         html[data-mcms-mobile-active="true"] #${SCRIPT.panelId} .mcms-desktop-position-controls { display:none !important; }
04100:         html[data-mcms-mobile-active="true"] #${SCRIPT.panelId} .mcms-footer { display:none !important; }
04101:         html[data-mcms-mobile-active="true"] #${SCRIPT.criticalDrawerId} {
04102:             left:max(4px,env(safe-area-inset-left)) !important; right:max(4px,env(safe-area-inset-right)) !important;
```

### Lines 4117-4127
```text
04117:         html[data-mcms-mobile-active="true"] .mcms-unit-commitment-badge,
04118:         html[data-mcms-mobile-active="true"] .mcms-transport-watcher-badge,
04119:         html[data-mcms-mobile-active="true"] .mcms-resource-gap-badge {
04120:             backdrop-filter:none !important; -webkit-backdrop-filter:none !important;
04121:         }
04122:         @media (max-width: 430px) {
04123:             html[data-mcms-mobile-active="true"] #${SCRIPT.panelId} .mcms-grid-2 { grid-template-columns:repeat(2,minmax(0,1fr)) !important; }
04124:             html[data-mcms-mobile-active="true"] #${SCRIPT.panelId} .mcms-row { grid-template-columns:1fr !important; }
04125:             html[data-mcms-mobile-active="true"] #${SCRIPT.panelId} .mcms-row-label { margin-bottom:-2px !important; }
04126:             html[data-mcms-mobile-active="true"] #${SCRIPT.panelId} .mcms-bookmark-row { grid-template-columns:minmax(0,1fr) repeat(4,40px) !important; }
04127:         }
```

### Lines 4118-4128
```text
04118:         html[data-mcms-mobile-active="true"] .mcms-transport-watcher-badge,
04119:         html[data-mcms-mobile-active="true"] .mcms-resource-gap-badge {
04120:             backdrop-filter:none !important; -webkit-backdrop-filter:none !important;
04121:         }
04122:         @media (max-width: 430px) {
04123:             html[data-mcms-mobile-active="true"] #${SCRIPT.panelId} .mcms-grid-2 { grid-template-columns:repeat(2,minmax(0,1fr)) !important; }
04124:             html[data-mcms-mobile-active="true"] #${SCRIPT.panelId} .mcms-row { grid-template-columns:1fr !important; }
04125:             html[data-mcms-mobile-active="true"] #${SCRIPT.panelId} .mcms-row-label { margin-bottom:-2px !important; }
04126:             html[data-mcms-mobile-active="true"] #${SCRIPT.panelId} .mcms-bookmark-row { grid-template-columns:minmax(0,1fr) repeat(4,40px) !important; }
04127:         }
04128:         @media (orientation: landscape) and (max-height: 500px) {
```

### Lines 4119-4129
```text
04119:         html[data-mcms-mobile-active="true"] .mcms-resource-gap-badge {
04120:             backdrop-filter:none !important; -webkit-backdrop-filter:none !important;
04121:         }
04122:         @media (max-width: 430px) {
04123:             html[data-mcms-mobile-active="true"] #${SCRIPT.panelId} .mcms-grid-2 { grid-template-columns:repeat(2,minmax(0,1fr)) !important; }
04124:             html[data-mcms-mobile-active="true"] #${SCRIPT.panelId} .mcms-row { grid-template-columns:1fr !important; }
04125:             html[data-mcms-mobile-active="true"] #${SCRIPT.panelId} .mcms-row-label { margin-bottom:-2px !important; }
04126:             html[data-mcms-mobile-active="true"] #${SCRIPT.panelId} .mcms-bookmark-row { grid-template-columns:minmax(0,1fr) repeat(4,40px) !important; }
04127:         }
04128:         @media (orientation: landscape) and (max-height: 500px) {
04129:             html[data-mcms-mobile-active="true"] #${SCRIPT.panelId} { border-radius:12px !important; padding-top:6px !important; }
```

### Lines 4121-4131
```text
04121:         }
04122:         @media (max-width: 430px) {
04123:             html[data-mcms-mobile-active="true"] #${SCRIPT.panelId} .mcms-grid-2 { grid-template-columns:repeat(2,minmax(0,1fr)) !important; }
04124:             html[data-mcms-mobile-active="true"] #${SCRIPT.panelId} .mcms-row { grid-template-columns:1fr !important; }
04125:             html[data-mcms-mobile-active="true"] #${SCRIPT.panelId} .mcms-row-label { margin-bottom:-2px !important; }
04126:             html[data-mcms-mobile-active="true"] #${SCRIPT.panelId} .mcms-bookmark-row { grid-template-columns:minmax(0,1fr) repeat(4,40px) !important; }
04127:         }
04128:         @media (orientation: landscape) and (max-height: 500px) {
04129:             html[data-mcms-mobile-active="true"] #${SCRIPT.panelId} { border-radius:12px !important; padding-top:6px !important; }
04130:             html[data-mcms-mobile-active="true"] #${SCRIPT.panelId} .mcms-header { min-height:42px !important; padding-top:5px !important; }
04131:             html[data-mcms-mobile-active="true"] #${SCRIPT.panelId} .mcms-subtitle { display:none !important; }
```

### Lines 4123-4133
```text
04123:             html[data-mcms-mobile-active="true"] #${SCRIPT.panelId} .mcms-grid-2 { grid-template-columns:repeat(2,minmax(0,1fr)) !important; }
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
```

### Lines 4127-4137
```text
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
```

### Lines 4128-4138
```text
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
```

### Lines 4140-4150
```text
04140:         html[data-mcms-command-bar-open="false"] #${SCRIPT.controlId} .mcms-floating-filter,
04141:         html[data-mcms-command-bar-open="false"] #${SCRIPT.controlId} .mcms-screen-pins {
04142:             display: none !important;
04143:             pointer-events: none !important;
04144:         }
04145:         @media (prefers-reduced-motion: reduce) {
04146:             #${SCRIPT.controlId} { transition: none !important; }
04147:         }
04148: 
04149:         /* v2.5.x mission intelligence and configuration tools */
04150:         #${SCRIPT.missionInspectorId} {
```

### Lines 4157-4167
```text
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
```

### Lines 4160-4170
```text
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
```

### Lines 4163-4173
```text
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
```

### Lines 4164-4174
```text
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
```

### Lines 4198-4208
```text
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
```

### Lines 4200-4210
```text
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
```

### Lines 4203-4213
```text
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
```

### Lines 4209-4219
```text
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
```

### Lines 4215-4225
```text
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
```

### Lines 4222-4232
```text
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
```

### Lines 4224-4234
```text
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
```

### Lines 4227-4237
```text
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
```

### Lines 4228-4238
```text
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
```

### Lines 4229-4239
```text
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
```

### Lines 4237-4247
```text
04237: 
04238: 
04239:         /* v3.7.0 complete interface themes */
04240:         #${SCRIPT.panelId} .mcms-ui-theme-grid {
04241:             display: grid !important;
04242:             grid-template-columns: repeat(2, minmax(0, 1fr)) !important;
04243:             gap: 7px !important;
04244:             margin-bottom: 7px !important;
04245:         }
04246:         #${SCRIPT.panelId} .mcms-ui-theme-btn {
04247:             position: relative !important;
```

### Lines 4244-4254
```text
04244:             margin-bottom: 7px !important;
04245:         }
04246:         #${SCRIPT.panelId} .mcms-ui-theme-btn {
04247:             position: relative !important;
04248:             display: grid !important;
04249:             grid-template-columns: 48px minmax(0, 1fr) !important;
04250:             align-items: center !important;
04251:             gap: 8px !important;
04252:             min-width: 0 !important;
04253:             height: 58px !important;
04254:             padding: 6px 8px !important;
```

### Lines 4273-4283
```text
04273:             box-shadow: inset 0 0 0 1px rgba(145,210,255,.14), 0 5px 14px rgba(0,0,0,.18) !important;
04274:             color: #fff !important;
04275:         }
04276:         #${SCRIPT.panelId} .mcms-ui-theme-preview {
04277:             display: grid !important;
04278:             grid-template-columns: repeat(3, 1fr) !important;
04279:             align-items: end !important;
04280:             gap: 3px !important;
04281:             width: 48px !important;
04282:             height: 36px !important;
04283:             padding: 5px !important;
```

### Lines 4398-4408
```text
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
```

### Lines 4402-4412
```text
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
04412:         html[data-mcms-mobile-active="true"] #${SCRIPT.panelId} .mcms-ui-theme-btn { height: 62px !important; grid-template-columns: 46px minmax(0,1fr) !important; padding: 6px !important; }
```

### Lines 4403-4413
```text
04403:         #${SCRIPT.panelId} .mcms-ui-theme-copy small { display: block !important; overflow: hidden !important; text-overflow: ellipsis !important; white-space: nowrap !important; }
04404:         #${SCRIPT.panelId} .mcms-ui-theme-copy strong { color: inherit !important; font-size: 10px !important; font-weight: 950 !important; }
04405:         #${SCRIPT.panelId} .mcms-ui-theme-copy small { margin-top: 4px !important; color: rgba(255,255,255,.48) !important; font-size: 7px !important; font-weight: 900 !important; letter-spacing: .7px !important; }
04406: 
04407:         html[data-mcms-tablet-active="true"] #${SCRIPT.panelId} .mcms-ui-theme-btn { height: 72px !important; grid-template-columns: 58px minmax(0,1fr) !important; padding: 8px 10px !important; }
04408:         html[data-mcms-tablet-active="true"] #${SCRIPT.panelId} .mcms-ui-theme-preview { width: 58px !important; height: 44px !important; }
04409:         html[data-mcms-tablet-active="true"] #${SCRIPT.panelId} .mcms-ui-theme-copy strong { font-size: 13px !important; }
04410:         html[data-mcms-tablet-active="true"] #${SCRIPT.panelId} .mcms-ui-theme-copy small { font-size: 8.5px !important; }
04411:         html[data-mcms-mobile-active="true"] #${SCRIPT.panelId} .mcms-ui-theme-grid { gap: 6px !important; }
04412:         html[data-mcms-mobile-active="true"] #${SCRIPT.panelId} .mcms-ui-theme-btn { height: 62px !important; grid-template-columns: 46px minmax(0,1fr) !important; padding: 6px !important; }
04413:         html[data-mcms-mobile-active="true"] #${SCRIPT.panelId} .mcms-ui-theme-preview { width: 46px !important; height: 38px !important; }
```

### Lines 4404-4414
```text
04404:         #${SCRIPT.panelId} .mcms-ui-theme-copy strong { color: inherit !important; font-size: 10px !important; font-weight: 950 !important; }
04405:         #${SCRIPT.panelId} .mcms-ui-theme-copy small { margin-top: 4px !important; color: rgba(255,255,255,.48) !important; font-size: 7px !important; font-weight: 900 !important; letter-spacing: .7px !important; }
04406: 
04407:         html[data-mcms-tablet-active="true"] #${SCRIPT.panelId} .mcms-ui-theme-btn { height: 72px !important; grid-template-columns: 58px minmax(0,1fr) !important; padding: 8px 10px !important; }
04408:         html[data-mcms-tablet-active="true"] #${SCRIPT.panelId} .mcms-ui-theme-preview { width: 58px !important; height: 44px !important; }
04409:         html[data-mcms-tablet-active="true"] #${SCRIPT.panelId} .mcms-ui-theme-copy strong { font-size: 13px !important; }
04410:         html[data-mcms-tablet-active="true"] #${SCRIPT.panelId} .mcms-ui-theme-copy small { font-size: 8.5px !important; }
04411:         html[data-mcms-mobile-active="true"] #${SCRIPT.panelId} .mcms-ui-theme-grid { gap: 6px !important; }
04412:         html[data-mcms-mobile-active="true"] #${SCRIPT.panelId} .mcms-ui-theme-btn { height: 62px !important; grid-template-columns: 46px minmax(0,1fr) !important; padding: 6px !important; }
04413:         html[data-mcms-mobile-active="true"] #${SCRIPT.panelId} .mcms-ui-theme-preview { width: 46px !important; height: 38px !important; }
04414: 
```

### Lines 4405-4415
```text
04405:         #${SCRIPT.panelId} .mcms-ui-theme-copy small { margin-top: 4px !important; color: rgba(255,255,255,.48) !important; font-size: 7px !important; font-weight: 900 !important; letter-spacing: .7px !important; }
04406: 
04407:         html[data-mcms-tablet-active="true"] #${SCRIPT.panelId} .mcms-ui-theme-btn { height: 72px !important; grid-template-columns: 58px minmax(0,1fr) !important; padding: 8px 10px !important; }
04408:         html[data-mcms-tablet-active="true"] #${SCRIPT.panelId} .mcms-ui-theme-preview { width: 58px !important; height: 44px !important; }
04409:         html[data-mcms-tablet-active="true"] #${SCRIPT.panelId} .mcms-ui-theme-copy strong { font-size: 13px !important; }
04410:         html[data-mcms-tablet-active="true"] #${SCRIPT.panelId} .mcms-ui-theme-copy small { font-size: 8.5px !important; }
04411:         html[data-mcms-mobile-active="true"] #${SCRIPT.panelId} .mcms-ui-theme-grid { gap: 6px !important; }
04412:         html[data-mcms-mobile-active="true"] #${SCRIPT.panelId} .mcms-ui-theme-btn { height: 62px !important; grid-template-columns: 46px minmax(0,1fr) !important; padding: 6px !important; }
04413:         html[data-mcms-mobile-active="true"] #${SCRIPT.panelId} .mcms-ui-theme-preview { width: 46px !important; height: 38px !important; }
04414: 
04415:         html[data-mcms-ui-theme="cyberpunk"] {
```

### Lines 4407-4417
```text
04407:         html[data-mcms-tablet-active="true"] #${SCRIPT.panelId} .mcms-ui-theme-btn { height: 72px !important; grid-template-columns: 58px minmax(0,1fr) !important; padding: 8px 10px !important; }
04408:         html[data-mcms-tablet-active="true"] #${SCRIPT.panelId} .mcms-ui-theme-preview { width: 58px !important; height: 44px !important; }
04409:         html[data-mcms-tablet-active="true"] #${SCRIPT.panelId} .mcms-ui-theme-copy strong { font-size: 13px !important; }
04410:         html[data-mcms-tablet-active="true"] #${SCRIPT.panelId} .mcms-ui-theme-copy small { font-size: 8.5px !important; }
04411:         html[data-mcms-mobile-active="true"] #${SCRIPT.panelId} .mcms-ui-theme-grid { gap: 6px !important; }
04412:         html[data-mcms-mobile-active="true"] #${SCRIPT.panelId} .mcms-ui-theme-btn { height: 62px !important; grid-template-columns: 46px minmax(0,1fr) !important; padding: 6px !important; }
04413:         html[data-mcms-mobile-active="true"] #${SCRIPT.panelId} .mcms-ui-theme-preview { width: 46px !important; height: 38px !important; }
04414: 
04415:         html[data-mcms-ui-theme="cyberpunk"] {
04416:             --mcms-cp-yellow: #fcee0a;
04417:             --mcms-cp-cyan: #00f0ff;
```

### Lines 4579-4589
```text
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
```

### Lines 4584-4594
```text
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
```

### Lines 4593-4603
```text
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
```

### Lines 4598-4608
```text
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
```

### Lines 4604-4614
```text
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
```

### Lines 4607-4617
```text
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
```

### Lines 4620-4630
```text
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
```

### Lines 4953-4963
```text
04953:             color: #9dafb5 !important;
04954:             text-shadow: none !important;
04955:         }
04956: 
04957:         /* Device-specific small copy receives a minimum readable size. */
04958:         html[data-mcms-tablet-active="true"][data-mcms-ui-theme="cyberpunk"] #${SCRIPT.panelId} .mcms-ui-theme-copy small,
04959:         html[data-mcms-tablet-active="true"][data-mcms-ui-theme="cyberpunk"] #${SCRIPT.panelId} .mcms-profile-main span,
04960:         html[data-mcms-tablet-active="true"][data-mcms-ui-theme="cyberpunk"] #${SCRIPT.panelId} .mcms-ops-stat-label,
04961:         html[data-mcms-tablet-active="true"][data-mcms-ui-theme="cyberpunk"] #${SCRIPT.panelId} .mcms-ops-entry-meta {
04962:             font-size: 9px !important;
04963:         }
```

### Lines 4954-4964
```text
04954:             text-shadow: none !important;
04955:         }
04956: 
04957:         /* Device-specific small copy receives a minimum readable size. */
04958:         html[data-mcms-tablet-active="true"][data-mcms-ui-theme="cyberpunk"] #${SCRIPT.panelId} .mcms-ui-theme-copy small,
04959:         html[data-mcms-tablet-active="true"][data-mcms-ui-theme="cyberpunk"] #${SCRIPT.panelId} .mcms-profile-main span,
04960:         html[data-mcms-tablet-active="true"][data-mcms-ui-theme="cyberpunk"] #${SCRIPT.panelId} .mcms-ops-stat-label,
04961:         html[data-mcms-tablet-active="true"][data-mcms-ui-theme="cyberpunk"] #${SCRIPT.panelId} .mcms-ops-entry-meta {
04962:             font-size: 9px !important;
04963:         }
04964:         html[data-mcms-mobile-active="true"][data-mcms-ui-theme="cyberpunk"] #${SCRIPT.panelId} .mcms-ui-theme-copy small,
```

### Lines 4955-4965
```text
04955:         }
04956: 
04957:         /* Device-specific small copy receives a minimum readable size. */
04958:         html[data-mcms-tablet-active="true"][data-mcms-ui-theme="cyberpunk"] #${SCRIPT.panelId} .mcms-ui-theme-copy small,
04959:         html[data-mcms-tablet-active="true"][data-mcms-ui-theme="cyberpunk"] #${SCRIPT.panelId} .mcms-profile-main span,
04960:         html[data-mcms-tablet-active="true"][data-mcms-ui-theme="cyberpunk"] #${SCRIPT.panelId} .mcms-ops-stat-label,
04961:         html[data-mcms-tablet-active="true"][data-mcms-ui-theme="cyberpunk"] #${SCRIPT.panelId} .mcms-ops-entry-meta {
04962:             font-size: 9px !important;
04963:         }
04964:         html[data-mcms-mobile-active="true"][data-mcms-ui-theme="cyberpunk"] #${SCRIPT.panelId} .mcms-ui-theme-copy small,
04965:         html[data-mcms-mobile-active="true"][data-mcms-ui-theme="cyberpunk"] #${SCRIPT.panelId} .mcms-profile-main span,
```

### Lines 4956-4966
```text
04956: 
04957:         /* Device-specific small copy receives a minimum readable size. */
04958:         html[data-mcms-tablet-active="true"][data-mcms-ui-theme="cyberpunk"] #${SCRIPT.panelId} .mcms-ui-theme-copy small,
04959:         html[data-mcms-tablet-active="true"][data-mcms-ui-theme="cyberpunk"] #${SCRIPT.panelId} .mcms-profile-main span,
04960:         html[data-mcms-tablet-active="true"][data-mcms-ui-theme="cyberpunk"] #${SCRIPT.panelId} .mcms-ops-stat-label,
04961:         html[data-mcms-tablet-active="true"][data-mcms-ui-theme="cyberpunk"] #${SCRIPT.panelId} .mcms-ops-entry-meta {
04962:             font-size: 9px !important;
04963:         }
04964:         html[data-mcms-mobile-active="true"][data-mcms-ui-theme="cyberpunk"] #${SCRIPT.panelId} .mcms-ui-theme-copy small,
04965:         html[data-mcms-mobile-active="true"][data-mcms-ui-theme="cyberpunk"] #${SCRIPT.panelId} .mcms-profile-main span,
04966:         html[data-mcms-mobile-active="true"][data-mcms-ui-theme="cyberpunk"] #${SCRIPT.panelId} .mcms-ops-stat-label,
```

### Lines 5189-5199
```text
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
```

### Lines 5194-5204
```text
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
```

### Lines 5203-5213
```text
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
```

### Lines 5204-5214
```text
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
```

### Lines 5209-5219
```text
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
```

### Lines 5216-5226
```text
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
```

### Lines 5219-5229
```text
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
```

### Lines 5234-5244
```text
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
```

### Lines 5638-5648
```text
05638:             color: #a9b7a1 !important;
05639:             text-shadow: none !important;
05640:         }
05641: 
05642:         /* Device-specific readability without changing established layouts. */
05643:         html[data-mcms-tablet-active="true"][data-mcms-ui-theme="fallout4"] #${SCRIPT.panelId} .mcms-ui-theme-copy small,
05644:         html[data-mcms-tablet-active="true"][data-mcms-ui-theme="fallout4"] #${SCRIPT.panelId} .mcms-profile-main span,
05645:         html[data-mcms-tablet-active="true"][data-mcms-ui-theme="fallout4"] #${SCRIPT.panelId} .mcms-ops-stat-label,
05646:         html[data-mcms-tablet-active="true"][data-mcms-ui-theme="fallout4"] #${SCRIPT.panelId} .mcms-ops-entry-meta {
05647:             font-size: 9px !important;
05648:         }
```

### Lines 5639-5649
```text
05639:             text-shadow: none !important;
05640:         }
05641: 
05642:         /* Device-specific readability without changing established layouts. */
05643:         html[data-mcms-tablet-active="true"][data-mcms-ui-theme="fallout4"] #${SCRIPT.panelId} .mcms-ui-theme-copy small,
05644:         html[data-mcms-tablet-active="true"][data-mcms-ui-theme="fallout4"] #${SCRIPT.panelId} .mcms-profile-main span,
05645:         html[data-mcms-tablet-active="true"][data-mcms-ui-theme="fallout4"] #${SCRIPT.panelId} .mcms-ops-stat-label,
05646:         html[data-mcms-tablet-active="true"][data-mcms-ui-theme="fallout4"] #${SCRIPT.panelId} .mcms-ops-entry-meta {
05647:             font-size: 9px !important;
05648:         }
05649:         html[data-mcms-mobile-active="true"][data-mcms-ui-theme="fallout4"] #${SCRIPT.panelId} .mcms-ui-theme-copy small,
```

### Lines 5640-5650
```text
05640:         }
05641: 
05642:         /* Device-specific readability without changing established layouts. */
05643:         html[data-mcms-tablet-active="true"][data-mcms-ui-theme="fallout4"] #${SCRIPT.panelId} .mcms-ui-theme-copy small,
05644:         html[data-mcms-tablet-active="true"][data-mcms-ui-theme="fallout4"] #${SCRIPT.panelId} .mcms-profile-main span,
05645:         html[data-mcms-tablet-active="true"][data-mcms-ui-theme="fallout4"] #${SCRIPT.panelId} .mcms-ops-stat-label,
05646:         html[data-mcms-tablet-active="true"][data-mcms-ui-theme="fallout4"] #${SCRIPT.panelId} .mcms-ops-entry-meta {
05647:             font-size: 9px !important;
05648:         }
05649:         html[data-mcms-mobile-active="true"][data-mcms-ui-theme="fallout4"] #${SCRIPT.panelId} .mcms-ui-theme-copy small,
05650:         html[data-mcms-mobile-active="true"][data-mcms-ui-theme="fallout4"] #${SCRIPT.panelId} .mcms-profile-main span,
```

### Lines 5641-5651
```text
05641: 
05642:         /* Device-specific readability without changing established layouts. */
05643:         html[data-mcms-tablet-active="true"][data-mcms-ui-theme="fallout4"] #${SCRIPT.panelId} .mcms-ui-theme-copy small,
05644:         html[data-mcms-tablet-active="true"][data-mcms-ui-theme="fallout4"] #${SCRIPT.panelId} .mcms-profile-main span,
05645:         html[data-mcms-tablet-active="true"][data-mcms-ui-theme="fallout4"] #${SCRIPT.panelId} .mcms-ops-stat-label,
05646:         html[data-mcms-tablet-active="true"][data-mcms-ui-theme="fallout4"] #${SCRIPT.panelId} .mcms-ops-entry-meta {
05647:             font-size: 9px !important;
05648:         }
05649:         html[data-mcms-mobile-active="true"][data-mcms-ui-theme="fallout4"] #${SCRIPT.panelId} .mcms-ui-theme-copy small,
05650:         html[data-mcms-mobile-active="true"][data-mcms-ui-theme="fallout4"] #${SCRIPT.panelId} .mcms-profile-main span,
05651:         html[data-mcms-mobile-active="true"][data-mcms-ui-theme="fallout4"] #${SCRIPT.panelId} .mcms-ops-stat-label,
```

### Lines 5675-5685
```text
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
```

### Lines 5677-5687
```text
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
```

### Lines 5911-5921
```text
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
```

### Lines 5916-5926
```text
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
```

### Lines 5925-5935
```text
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
```

### Lines 5926-5936
```text
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
```

### Lines 5931-5941
```text
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
```

### Lines 5938-5948
```text
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
```

### Lines 5941-5951
```text
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
```

### Lines 5956-5966
```text
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
```

### Lines 6360-6370
```text
06360:             color: #b7bdc6 !important;
06361:             text-shadow: none !important;
06362:         }
06363: 
06364:         /* Device-specific readability without changing established layouts. */
06365:         html[data-mcms-tablet-active="true"][data-mcms-ui-theme="umbrella"] #${SCRIPT.panelId} .mcms-ui-theme-copy small,
06366:         html[data-mcms-tablet-active="true"][data-mcms-ui-theme="umbrella"] #${SCRIPT.panelId} .mcms-profile-main span,
06367:         html[data-mcms-tablet-active="true"][data-mcms-ui-theme="umbrella"] #${SCRIPT.panelId} .mcms-ops-stat-label,
06368:         html[data-mcms-tablet-active="true"][data-mcms-ui-theme="umbrella"] #${SCRIPT.panelId} .mcms-ops-entry-meta {
06369:             font-size: 9px !important;
06370:         }
```

### Lines 6361-6371
```text
06361:             text-shadow: none !important;
06362:         }
06363: 
06364:         /* Device-specific readability without changing established layouts. */
06365:         html[data-mcms-tablet-active="true"][data-mcms-ui-theme="umbrella"] #${SCRIPT.panelId} .mcms-ui-theme-copy small,
06366:         html[data-mcms-tablet-active="true"][data-mcms-ui-theme="umbrella"] #${SCRIPT.panelId} .mcms-profile-main span,
06367:         html[data-mcms-tablet-active="true"][data-mcms-ui-theme="umbrella"] #${SCRIPT.panelId} .mcms-ops-stat-label,
06368:         html[data-mcms-tablet-active="true"][data-mcms-ui-theme="umbrella"] #${SCRIPT.panelId} .mcms-ops-entry-meta {
06369:             font-size: 9px !important;
06370:         }
06371:         html[data-mcms-mobile-active="true"][data-mcms-ui-theme="umbrella"] #${SCRIPT.panelId} .mcms-ui-theme-copy small,
```

### Lines 6362-6372
```text
06362:         }
06363: 
06364:         /* Device-specific readability without changing established layouts. */
06365:         html[data-mcms-tablet-active="true"][data-mcms-ui-theme="umbrella"] #${SCRIPT.panelId} .mcms-ui-theme-copy small,
06366:         html[data-mcms-tablet-active="true"][data-mcms-ui-theme="umbrella"] #${SCRIPT.panelId} .mcms-profile-main span,
06367:         html[data-mcms-tablet-active="true"][data-mcms-ui-theme="umbrella"] #${SCRIPT.panelId} .mcms-ops-stat-label,
06368:         html[data-mcms-tablet-active="true"][data-mcms-ui-theme="umbrella"] #${SCRIPT.panelId} .mcms-ops-entry-meta {
06369:             font-size: 9px !important;
06370:         }
06371:         html[data-mcms-mobile-active="true"][data-mcms-ui-theme="umbrella"] #${SCRIPT.panelId} .mcms-ui-theme-copy small,
06372:         html[data-mcms-mobile-active="true"][data-mcms-ui-theme="umbrella"] #${SCRIPT.panelId} .mcms-profile-main span,
```

### Lines 6363-6373
```text
06363: 
06364:         /* Device-specific readability without changing established layouts. */
06365:         html[data-mcms-tablet-active="true"][data-mcms-ui-theme="umbrella"] #${SCRIPT.panelId} .mcms-ui-theme-copy small,
06366:         html[data-mcms-tablet-active="true"][data-mcms-ui-theme="umbrella"] #${SCRIPT.panelId} .mcms-profile-main span,
06367:         html[data-mcms-tablet-active="true"][data-mcms-ui-theme="umbrella"] #${SCRIPT.panelId} .mcms-ops-stat-label,
06368:         html[data-mcms-tablet-active="true"][data-mcms-ui-theme="umbrella"] #${SCRIPT.panelId} .mcms-ops-entry-meta {
06369:             font-size: 9px !important;
06370:         }
06371:         html[data-mcms-mobile-active="true"][data-mcms-ui-theme="umbrella"] #${SCRIPT.panelId} .mcms-ui-theme-copy small,
06372:         html[data-mcms-mobile-active="true"][data-mcms-ui-theme="umbrella"] #${SCRIPT.panelId} .mcms-profile-main span,
06373:         html[data-mcms-mobile-active="true"][data-mcms-ui-theme="umbrella"] #${SCRIPT.panelId} .mcms-ops-stat-label,
```

### Lines 6397-6407
```text
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
```

### Lines 6399-6409
```text
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
```

### Lines 6538-6548
```text
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
```

### Lines 6542-6552
```text
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
```

### Lines 6550-6560
```text
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
```

### Lines 6551-6561
```text
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
```

### Lines 6556-6566
```text
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
```

### Lines 6562-6572
```text
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
```

### Lines 6565-6575
```text
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
```

### Lines 6580-6590
```text
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
```

### Lines 6814-6824
```text
06814:         html[data-mcms-ui-theme="umbrella"] #${SCRIPT.panelId} button:disabled * {
06815:             color: #b8bec7 !important;
06816:             text-shadow: none !important;
06817:         }
06818: 
06819:         html[data-mcms-tablet-active="true"][data-mcms-ui-theme="umbrella"] #${SCRIPT.panelId} .mcms-ui-theme-copy small,
06820:         html[data-mcms-tablet-active="true"][data-mcms-ui-theme="umbrella"] #${SCRIPT.panelId} .mcms-profile-main span,
06821:         html[data-mcms-tablet-active="true"][data-mcms-ui-theme="umbrella"] #${SCRIPT.panelId} .mcms-ops-stat-label,
06822:         html[data-mcms-tablet-active="true"][data-mcms-ui-theme="umbrella"] #${SCRIPT.panelId} .mcms-ops-entry-meta {
06823:             font-size: 9px !important;
06824:         }
```

### Lines 6815-6825
```text
06815:             color: #b8bec7 !important;
06816:             text-shadow: none !important;
06817:         }
06818: 
06819:         html[data-mcms-tablet-active="true"][data-mcms-ui-theme="umbrella"] #${SCRIPT.panelId} .mcms-ui-theme-copy small,
06820:         html[data-mcms-tablet-active="true"][data-mcms-ui-theme="umbrella"] #${SCRIPT.panelId} .mcms-profile-main span,
06821:         html[data-mcms-tablet-active="true"][data-mcms-ui-theme="umbrella"] #${SCRIPT.panelId} .mcms-ops-stat-label,
06822:         html[data-mcms-tablet-active="true"][data-mcms-ui-theme="umbrella"] #${SCRIPT.panelId} .mcms-ops-entry-meta {
06823:             font-size: 9px !important;
06824:         }
06825:         html[data-mcms-mobile-active="true"][data-mcms-ui-theme="umbrella"] #${SCRIPT.panelId} .mcms-ui-theme-copy small,
```

### Lines 6816-6826
```text
06816:             text-shadow: none !important;
06817:         }
06818: 
06819:         html[data-mcms-tablet-active="true"][data-mcms-ui-theme="umbrella"] #${SCRIPT.panelId} .mcms-ui-theme-copy small,
06820:         html[data-mcms-tablet-active="true"][data-mcms-ui-theme="umbrella"] #${SCRIPT.panelId} .mcms-profile-main span,
06821:         html[data-mcms-tablet-active="true"][data-mcms-ui-theme="umbrella"] #${SCRIPT.panelId} .mcms-ops-stat-label,
06822:         html[data-mcms-tablet-active="true"][data-mcms-ui-theme="umbrella"] #${SCRIPT.panelId} .mcms-ops-entry-meta {
06823:             font-size: 9px !important;
06824:         }
06825:         html[data-mcms-mobile-active="true"][data-mcms-ui-theme="umbrella"] #${SCRIPT.panelId} .mcms-ui-theme-copy small,
06826:         html[data-mcms-mobile-active="true"][data-mcms-ui-theme="umbrella"] #${SCRIPT.panelId} .mcms-profile-main span,
```

### Lines 6817-6827
```text
06817:         }
06818: 
06819:         html[data-mcms-tablet-active="true"][data-mcms-ui-theme="umbrella"] #${SCRIPT.panelId} .mcms-ui-theme-copy small,
06820:         html[data-mcms-tablet-active="true"][data-mcms-ui-theme="umbrella"] #${SCRIPT.panelId} .mcms-profile-main span,
06821:         html[data-mcms-tablet-active="true"][data-mcms-ui-theme="umbrella"] #${SCRIPT.panelId} .mcms-ops-stat-label,
06822:         html[data-mcms-tablet-active="true"][data-mcms-ui-theme="umbrella"] #${SCRIPT.panelId} .mcms-ops-entry-meta {
06823:             font-size: 9px !important;
06824:         }
06825:         html[data-mcms-mobile-active="true"][data-mcms-ui-theme="umbrella"] #${SCRIPT.panelId} .mcms-ui-theme-copy small,
06826:         html[data-mcms-mobile-active="true"][data-mcms-ui-theme="umbrella"] #${SCRIPT.panelId} .mcms-profile-main span,
06827:         html[data-mcms-mobile-active="true"][data-mcms-ui-theme="umbrella"] #${SCRIPT.panelId} .mcms-ops-stat-label,
```

### Lines 6850-6860
```text
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
```

### Lines 6852-6862
```text
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
```

### Lines 6886-6896
```text
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
```

### Lines 6888-6898
```text
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
```

### Lines 7107-7117
```text
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
```

### Lines 7113-7123
```text
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
```

### Lines 7120-7130
```text
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
```

### Lines 7121-7131
```text
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
```

### Lines 7126-7136
```text
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
```

### Lines 7133-7143
```text
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
```

### Lines 7136-7146
```text
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
```

### Lines 7153-7163
```text
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
```

### Lines 7432-7442
```text
07432:         html[data-mcms-ui-theme="factorio"] #${SCRIPT.panelId} button:disabled * {
07433:             color: #a9a187 !important;
07434:             text-shadow: none !important;
07435:         }
07436: 
07437:         html[data-mcms-tablet-active="true"][data-mcms-ui-theme="factorio"] #${SCRIPT.panelId} .mcms-ui-theme-copy small,
07438:         html[data-mcms-tablet-active="true"][data-mcms-ui-theme="factorio"] #${SCRIPT.panelId} .mcms-profile-main span,
07439:         html[data-mcms-tablet-active="true"][data-mcms-ui-theme="factorio"] #${SCRIPT.panelId} .mcms-ops-stat-label,
07440:         html[data-mcms-tablet-active="true"][data-mcms-ui-theme="factorio"] #${SCRIPT.panelId} .mcms-ops-entry-meta {
07441:             font-size: 9px !important;
07442:         }
```

### Lines 7433-7443
```text
07433:             color: #a9a187 !important;
07434:             text-shadow: none !important;
07435:         }
07436: 
07437:         html[data-mcms-tablet-active="true"][data-mcms-ui-theme="factorio"] #${SCRIPT.panelId} .mcms-ui-theme-copy small,
07438:         html[data-mcms-tablet-active="true"][data-mcms-ui-theme="factorio"] #${SCRIPT.panelId} .mcms-profile-main span,
07439:         html[data-mcms-tablet-active="true"][data-mcms-ui-theme="factorio"] #${SCRIPT.panelId} .mcms-ops-stat-label,
07440:         html[data-mcms-tablet-active="true"][data-mcms-ui-theme="factorio"] #${SCRIPT.panelId} .mcms-ops-entry-meta {
07441:             font-size: 9px !important;
07442:         }
07443:         html[data-mcms-mobile-active="true"][data-mcms-ui-theme="factorio"] #${SCRIPT.panelId} .mcms-ui-theme-copy small,
```

### Lines 7434-7444
```text
07434:             text-shadow: none !important;
07435:         }
07436: 
07437:         html[data-mcms-tablet-active="true"][data-mcms-ui-theme="factorio"] #${SCRIPT.panelId} .mcms-ui-theme-copy small,
07438:         html[data-mcms-tablet-active="true"][data-mcms-ui-theme="factorio"] #${SCRIPT.panelId} .mcms-profile-main span,
07439:         html[data-mcms-tablet-active="true"][data-mcms-ui-theme="factorio"] #${SCRIPT.panelId} .mcms-ops-stat-label,
07440:         html[data-mcms-tablet-active="true"][data-mcms-ui-theme="factorio"] #${SCRIPT.panelId} .mcms-ops-entry-meta {
07441:             font-size: 9px !important;
07442:         }
07443:         html[data-mcms-mobile-active="true"][data-mcms-ui-theme="factorio"] #${SCRIPT.panelId} .mcms-ui-theme-copy small,
07444:         html[data-mcms-mobile-active="true"][data-mcms-ui-theme="factorio"] #${SCRIPT.panelId} .mcms-profile-main span,
```

### Lines 7435-7445
```text
07435:         }
07436: 
07437:         html[data-mcms-tablet-active="true"][data-mcms-ui-theme="factorio"] #${SCRIPT.panelId} .mcms-ui-theme-copy small,
07438:         html[data-mcms-tablet-active="true"][data-mcms-ui-theme="factorio"] #${SCRIPT.panelId} .mcms-profile-main span,
07439:         html[data-mcms-tablet-active="true"][data-mcms-ui-theme="factorio"] #${SCRIPT.panelId} .mcms-ops-stat-label,
07440:         html[data-mcms-tablet-active="true"][data-mcms-ui-theme="factorio"] #${SCRIPT.panelId} .mcms-ops-entry-meta {
07441:             font-size: 9px !important;
07442:         }
07443:         html[data-mcms-mobile-active="true"][data-mcms-ui-theme="factorio"] #${SCRIPT.panelId} .mcms-ui-theme-copy small,
07444:         html[data-mcms-mobile-active="true"][data-mcms-ui-theme="factorio"] #${SCRIPT.panelId} .mcms-profile-main span,
07445:         html[data-mcms-mobile-active="true"][data-mcms-ui-theme="factorio"] #${SCRIPT.panelId} .mcms-ops-stat-label,
```

### Lines 7468-7478
```text
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
```

### Lines 7470-7480
```text
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
```

### Lines 7529-7539
```text
07529:         html[data-mcms-ui-theme="umbrella"] #${SCRIPT.panelId} .mcms-sweep-card .mcms-sweep-stat b {
07530:             color: #11141a !important;
07531:             opacity: 1 !important;
07532:             text-shadow: none !important;
07533:         }
07534:         html[data-mcms-tablet-active="true"][data-mcms-ui-theme="umbrella"] #${SCRIPT.missionInspectorId} .mcms-inspector-stat span {
07535:             font-size: 9px !important;
07536:         }
07537:         html[data-mcms-tablet-active="true"][data-mcms-ui-theme="umbrella"] #${SCRIPT.missionInspectorId} .mcms-inspector-stat strong {
07538:             font-size: 13px !important;
07539:         }
```

### Lines 7532-7542
```text
07532:             text-shadow: none !important;
07533:         }
07534:         html[data-mcms-tablet-active="true"][data-mcms-ui-theme="umbrella"] #${SCRIPT.missionInspectorId} .mcms-inspector-stat span {
07535:             font-size: 9px !important;
07536:         }
07537:         html[data-mcms-tablet-active="true"][data-mcms-ui-theme="umbrella"] #${SCRIPT.missionInspectorId} .mcms-inspector-stat strong {
07538:             font-size: 13px !important;
07539:         }
07540:         html[data-mcms-mobile-active="true"][data-mcms-ui-theme="umbrella"] #${SCRIPT.missionInspectorId} .mcms-inspector-stat span {
07541:             font-size: 8px !important;
07542:         }
```

### Lines 7871-7881
```text
07871:             from { opacity:0; transform:translateY(-8px) scale(.985); }
07872:             to { opacity:1; transform:translateY(0) scale(1); }
07873:         }
07874:         #${SCRIPT.vehicleStatusId} .mcms-vcs-head {
07875:             display:grid !important;
07876:             grid-template-columns:minmax(0,1fr) auto !important;
07877:             gap:10px !important;
07878:             align-items:center !important;
07879:             padding-bottom:10px !important;
07880:             border-bottom:1px solid var(--mcms-vcs-line) !important;
07881:         }
```

### Lines 7942-7952
```text
07942:             border-radius:10px !important;
07943:             background:rgba(0,0,0,.13) !important;
07944:         }
07945:         #${SCRIPT.vehicleStatusId} .mcms-vcs-table-row {
07946:             display:grid !important;
07947:             grid-template-columns:64px minmax(0,1fr) 88px !important;
07948:             gap:9px !important;
07949:             align-items:center !important;
07950:             min-width:0 !important;
07951:             min-height:39px !important;
07952:             padding:6px 9px !important;
```

### Lines 7992-8002
```text
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
```

### Lines 7993-8003
```text
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
```

### Lines 8025-8035
```text
08025:         }
08026:         #${SCRIPT.vehicleStatusId} .mcms-vcs-footnote code { color:var(--mcms-vcs-text) !important; font-size:inherit !important; }
08027:         #${SCRIPT.vehicleStatusId} .mcms-vcs-unknown .mcms-vcs-status { color:#ffb6b0 !important; }
08028: 
08029:         /* Tablet: touch-sized controls and a readable, bounded fleet table. */
08030:         html[data-mcms-tablet-active="true"] #${SCRIPT.vehicleStatusId} {
08031:             top:max(12px,env(safe-area-inset-top)) !important;
08032:             right:12px !important;
08033:             width:min(680px,calc(100vw - 24px)) !important;
08034:             max-height:calc(100vh - 24px - env(safe-area-inset-bottom)) !important;
08035:             padding:15px !important;
```

### Lines 8033-8043
```text
08033:             width:min(680px,calc(100vw - 24px)) !important;
08034:             max-height:calc(100vh - 24px - env(safe-area-inset-bottom)) !important;
08035:             padding:15px !important;
08036:             border-radius:15px !important;
08037:         }
08038:         html[data-mcms-tablet-active="true"] #${SCRIPT.vehicleStatusId} .mcms-vcs-title { font-size:17px !important; }
08039:         html[data-mcms-tablet-active="true"] #${SCRIPT.vehicleStatusId} .mcms-vcs-subtitle,
08040:         html[data-mcms-tablet-active="true"] #${SCRIPT.vehicleStatusId} .mcms-vcs-meta { font-size:10px !important; }
08041:         html[data-mcms-tablet-active="true"] #${SCRIPT.vehicleStatusId} .mcms-vcs-refresh,
08042:         html[data-mcms-tablet-active="true"] #${SCRIPT.vehicleStatusId} .mcms-vcs-close { width:44px !important; height:44px !important; border-radius:11px !important; font-size:22px !important; }
08043:         html[data-mcms-tablet-active="true"] #${SCRIPT.vehicleStatusId} .mcms-vcs-table-row { grid-template-columns:78px minmax(0,1fr) 104px !important; min-height:52px !important; padding:8px 12px !important; }
```

### Lines 8034-8044
```text
08034:             max-height:calc(100vh - 24px - env(safe-area-inset-bottom)) !important;
08035:             padding:15px !important;
08036:             border-radius:15px !important;
08037:         }
08038:         html[data-mcms-tablet-active="true"] #${SCRIPT.vehicleStatusId} .mcms-vcs-title { font-size:17px !important; }
08039:         html[data-mcms-tablet-active="true"] #${SCRIPT.vehicleStatusId} .mcms-vcs-subtitle,
08040:         html[data-mcms-tablet-active="true"] #${SCRIPT.vehicleStatusId} .mcms-vcs-meta { font-size:10px !important; }
08041:         html[data-mcms-tablet-active="true"] #${SCRIPT.vehicleStatusId} .mcms-vcs-refresh,
08042:         html[data-mcms-tablet-active="true"] #${SCRIPT.vehicleStatusId} .mcms-vcs-close { width:44px !important; height:44px !important; border-radius:11px !important; font-size:22px !important; }
08043:         html[data-mcms-tablet-active="true"] #${SCRIPT.vehicleStatusId} .mcms-vcs-table-row { grid-template-columns:78px minmax(0,1fr) 104px !important; min-height:52px !important; padding:8px 12px !important; }
08044:         html[data-mcms-tablet-active="true"] #${SCRIPT.vehicleStatusId} .mcms-vcs-code { width:48px !important; height:34px !important; font-size:15px !important; }
```

### Lines 8035-8045
```text
08035:             padding:15px !important;
08036:             border-radius:15px !important;
08037:         }
08038:         html[data-mcms-tablet-active="true"] #${SCRIPT.vehicleStatusId} .mcms-vcs-title { font-size:17px !important; }
08039:         html[data-mcms-tablet-active="true"] #${SCRIPT.vehicleStatusId} .mcms-vcs-subtitle,
08040:         html[data-mcms-tablet-active="true"] #${SCRIPT.vehicleStatusId} .mcms-vcs-meta { font-size:10px !important; }
08041:         html[data-mcms-tablet-active="true"] #${SCRIPT.vehicleStatusId} .mcms-vcs-refresh,
08042:         html[data-mcms-tablet-active="true"] #${SCRIPT.vehicleStatusId} .mcms-vcs-close { width:44px !important; height:44px !important; border-radius:11px !important; font-size:22px !important; }
08043:         html[data-mcms-tablet-active="true"] #${SCRIPT.vehicleStatusId} .mcms-vcs-table-row { grid-template-columns:78px minmax(0,1fr) 104px !important; min-height:52px !important; padding:8px 12px !important; }
08044:         html[data-mcms-tablet-active="true"] #${SCRIPT.vehicleStatusId} .mcms-vcs-code { width:48px !important; height:34px !important; font-size:15px !important; }
08045:         html[data-mcms-tablet-active="true"] #${SCRIPT.vehicleStatusId} .mcms-vcs-status { font-size:13px !important; }
```

### Lines 8036-8046
```text
08036:             border-radius:15px !important;
08037:         }
08038:         html[data-mcms-tablet-active="true"] #${SCRIPT.vehicleStatusId} .mcms-vcs-title { font-size:17px !important; }
08039:         html[data-mcms-tablet-active="true"] #${SCRIPT.vehicleStatusId} .mcms-vcs-subtitle,
08040:         html[data-mcms-tablet-active="true"] #${SCRIPT.vehicleStatusId} .mcms-vcs-meta { font-size:10px !important; }
08041:         html[data-mcms-tablet-active="true"] #${SCRIPT.vehicleStatusId} .mcms-vcs-refresh,
08042:         html[data-mcms-tablet-active="true"] #${SCRIPT.vehicleStatusId} .mcms-vcs-close { width:44px !important; height:44px !important; border-radius:11px !important; font-size:22px !important; }
08043:         html[data-mcms-tablet-active="true"] #${SCRIPT.vehicleStatusId} .mcms-vcs-table-row { grid-template-columns:78px minmax(0,1fr) 104px !important; min-height:52px !important; padding:8px 12px !important; }
08044:         html[data-mcms-tablet-active="true"] #${SCRIPT.vehicleStatusId} .mcms-vcs-code { width:48px !important; height:34px !important; font-size:15px !important; }
08045:         html[data-mcms-tablet-active="true"] #${SCRIPT.vehicleStatusId} .mcms-vcs-status { font-size:13px !important; }
08046:         html[data-mcms-tablet-active="true"] #${SCRIPT.vehicleStatusId} .mcms-vcs-count { font-size:15px !important; }
```

### Lines 8037-8047
```text
08037:         }
08038:         html[data-mcms-tablet-active="true"] #${SCRIPT.vehicleStatusId} .mcms-vcs-title { font-size:17px !important; }
08039:         html[data-mcms-tablet-active="true"] #${SCRIPT.vehicleStatusId} .mcms-vcs-subtitle,
08040:         html[data-mcms-tablet-active="true"] #${SCRIPT.vehicleStatusId} .mcms-vcs-meta { font-size:10px !important; }
08041:         html[data-mcms-tablet-active="true"] #${SCRIPT.vehicleStatusId} .mcms-vcs-refresh,
08042:         html[data-mcms-tablet-active="true"] #${SCRIPT.vehicleStatusId} .mcms-vcs-close { width:44px !important; height:44px !important; border-radius:11px !important; font-size:22px !important; }
08043:         html[data-mcms-tablet-active="true"] #${SCRIPT.vehicleStatusId} .mcms-vcs-table-row { grid-template-columns:78px minmax(0,1fr) 104px !important; min-height:52px !important; padding:8px 12px !important; }
08044:         html[data-mcms-tablet-active="true"] #${SCRIPT.vehicleStatusId} .mcms-vcs-code { width:48px !important; height:34px !important; font-size:15px !important; }
08045:         html[data-mcms-tablet-active="true"] #${SCRIPT.vehicleStatusId} .mcms-vcs-status { font-size:13px !important; }
08046:         html[data-mcms-tablet-active="true"] #${SCRIPT.vehicleStatusId} .mcms-vcs-count { font-size:15px !important; }
08047:         html[data-mcms-tablet-active="true"] #${SCRIPT.vehicleStatusId} .mcms-vcs-table-head,
```

### Lines 8038-8048
```text
08038:         html[data-mcms-tablet-active="true"] #${SCRIPT.vehicleStatusId} .mcms-vcs-title { font-size:17px !important; }
08039:         html[data-mcms-tablet-active="true"] #${SCRIPT.vehicleStatusId} .mcms-vcs-subtitle,
08040:         html[data-mcms-tablet-active="true"] #${SCRIPT.vehicleStatusId} .mcms-vcs-meta { font-size:10px !important; }
08041:         html[data-mcms-tablet-active="true"] #${SCRIPT.vehicleStatusId} .mcms-vcs-refresh,
08042:         html[data-mcms-tablet-active="true"] #${SCRIPT.vehicleStatusId} .mcms-vcs-close { width:44px !important; height:44px !important; border-radius:11px !important; font-size:22px !important; }
08043:         html[data-mcms-tablet-active="true"] #${SCRIPT.vehicleStatusId} .mcms-vcs-table-row { grid-template-columns:78px minmax(0,1fr) 104px !important; min-height:52px !important; padding:8px 12px !important; }
08044:         html[data-mcms-tablet-active="true"] #${SCRIPT.vehicleStatusId} .mcms-vcs-code { width:48px !important; height:34px !important; font-size:15px !important; }
08045:         html[data-mcms-tablet-active="true"] #${SCRIPT.vehicleStatusId} .mcms-vcs-status { font-size:13px !important; }
08046:         html[data-mcms-tablet-active="true"] #${SCRIPT.vehicleStatusId} .mcms-vcs-count { font-size:15px !important; }
08047:         html[data-mcms-tablet-active="true"] #${SCRIPT.vehicleStatusId} .mcms-vcs-table-head,
08048:         html[data-mcms-tablet-active="true"] #${SCRIPT.vehicleStatusId} .mcms-vcs-footnote { font-size:9.5px !important; }
```

### Lines 8039-8049
```text
08039:         html[data-mcms-tablet-active="true"] #${SCRIPT.vehicleStatusId} .mcms-vcs-subtitle,
08040:         html[data-mcms-tablet-active="true"] #${SCRIPT.vehicleStatusId} .mcms-vcs-meta { font-size:10px !important; }
08041:         html[data-mcms-tablet-active="true"] #${SCRIPT.vehicleStatusId} .mcms-vcs-refresh,
08042:         html[data-mcms-tablet-active="true"] #${SCRIPT.vehicleStatusId} .mcms-vcs-close { width:44px !important; height:44px !important; border-radius:11px !important; font-size:22px !important; }
08043:         html[data-mcms-tablet-active="true"] #${SCRIPT.vehicleStatusId} .mcms-vcs-table-row { grid-template-columns:78px minmax(0,1fr) 104px !important; min-height:52px !important; padding:8px 12px !important; }
08044:         html[data-mcms-tablet-active="true"] #${SCRIPT.vehicleStatusId} .mcms-vcs-code { width:48px !important; height:34px !important; font-size:15px !important; }
08045:         html[data-mcms-tablet-active="true"] #${SCRIPT.vehicleStatusId} .mcms-vcs-status { font-size:13px !important; }
08046:         html[data-mcms-tablet-active="true"] #${SCRIPT.vehicleStatusId} .mcms-vcs-count { font-size:15px !important; }
08047:         html[data-mcms-tablet-active="true"] #${SCRIPT.vehicleStatusId} .mcms-vcs-table-head,
08048:         html[data-mcms-tablet-active="true"] #${SCRIPT.vehicleStatusId} .mcms-vcs-footnote { font-size:9.5px !important; }
08049: 
```

### Lines 8040-8050
```text
08040:         html[data-mcms-tablet-active="true"] #${SCRIPT.vehicleStatusId} .mcms-vcs-meta { font-size:10px !important; }
08041:         html[data-mcms-tablet-active="true"] #${SCRIPT.vehicleStatusId} .mcms-vcs-refresh,
08042:         html[data-mcms-tablet-active="true"] #${SCRIPT.vehicleStatusId} .mcms-vcs-close { width:44px !important; height:44px !important; border-radius:11px !important; font-size:22px !important; }
08043:         html[data-mcms-tablet-active="true"] #${SCRIPT.vehicleStatusId} .mcms-vcs-table-row { grid-template-columns:78px minmax(0,1fr) 104px !important; min-height:52px !important; padding:8px 12px !important; }
08044:         html[data-mcms-tablet-active="true"] #${SCRIPT.vehicleStatusId} .mcms-vcs-code { width:48px !important; height:34px !important; font-size:15px !important; }
08045:         html[data-mcms-tablet-active="true"] #${SCRIPT.vehicleStatusId} .mcms-vcs-status { font-size:13px !important; }
08046:         html[data-mcms-tablet-active="true"] #${SCRIPT.vehicleStatusId} .mcms-vcs-count { font-size:15px !important; }
08047:         html[data-mcms-tablet-active="true"] #${SCRIPT.vehicleStatusId} .mcms-vcs-table-head,
08048:         html[data-mcms-tablet-active="true"] #${SCRIPT.vehicleStatusId} .mcms-vcs-footnote { font-size:9.5px !important; }
08049: 
08050:         /* iOS Mobile: full-width bottom sheet; no horizontal scroll. */
```

### Lines 8041-8051
```text
08041:         html[data-mcms-tablet-active="true"] #${SCRIPT.vehicleStatusId} .mcms-vcs-refresh,
08042:         html[data-mcms-tablet-active="true"] #${SCRIPT.vehicleStatusId} .mcms-vcs-close { width:44px !important; height:44px !important; border-radius:11px !important; font-size:22px !important; }
08043:         html[data-mcms-tablet-active="true"] #${SCRIPT.vehicleStatusId} .mcms-vcs-table-row { grid-template-columns:78px minmax(0,1fr) 104px !important; min-height:52px !important; padding:8px 12px !important; }
08044:         html[data-mcms-tablet-active="true"] #${SCRIPT.vehicleStatusId} .mcms-vcs-code { width:48px !important; height:34px !important; font-size:15px !important; }
08045:         html[data-mcms-tablet-active="true"] #${SCRIPT.vehicleStatusId} .mcms-vcs-status { font-size:13px !important; }
08046:         html[data-mcms-tablet-active="true"] #${SCRIPT.vehicleStatusId} .mcms-vcs-count { font-size:15px !important; }
08047:         html[data-mcms-tablet-active="true"] #${SCRIPT.vehicleStatusId} .mcms-vcs-table-head,
08048:         html[data-mcms-tablet-active="true"] #${SCRIPT.vehicleStatusId} .mcms-vcs-footnote { font-size:9.5px !important; }
08049: 
08050:         /* iOS Mobile: full-width bottom sheet; no horizontal scroll. */
08051:         html[data-mcms-mobile-active="true"] #${SCRIPT.vehicleStatusId} {
```

### Lines 8042-8052
```text
08042:         html[data-mcms-tablet-active="true"] #${SCRIPT.vehicleStatusId} .mcms-vcs-close { width:44px !important; height:44px !important; border-radius:11px !important; font-size:22px !important; }
08043:         html[data-mcms-tablet-active="true"] #${SCRIPT.vehicleStatusId} .mcms-vcs-table-row { grid-template-columns:78px minmax(0,1fr) 104px !important; min-height:52px !important; padding:8px 12px !important; }
08044:         html[data-mcms-tablet-active="true"] #${SCRIPT.vehicleStatusId} .mcms-vcs-code { width:48px !important; height:34px !important; font-size:15px !important; }
08045:         html[data-mcms-tablet-active="true"] #${SCRIPT.vehicleStatusId} .mcms-vcs-status { font-size:13px !important; }
08046:         html[data-mcms-tablet-active="true"] #${SCRIPT.vehicleStatusId} .mcms-vcs-count { font-size:15px !important; }
08047:         html[data-mcms-tablet-active="true"] #${SCRIPT.vehicleStatusId} .mcms-vcs-table-head,
08048:         html[data-mcms-tablet-active="true"] #${SCRIPT.vehicleStatusId} .mcms-vcs-footnote { font-size:9.5px !important; }
08049: 
08050:         /* iOS Mobile: full-width bottom sheet; no horizontal scroll. */
08051:         html[data-mcms-mobile-active="true"] #${SCRIPT.vehicleStatusId} {
08052:             top:auto !important;
```

### Lines 8043-8053
```text
08043:         html[data-mcms-tablet-active="true"] #${SCRIPT.vehicleStatusId} .mcms-vcs-table-row { grid-template-columns:78px minmax(0,1fr) 104px !important; min-height:52px !important; padding:8px 12px !important; }
08044:         html[data-mcms-tablet-active="true"] #${SCRIPT.vehicleStatusId} .mcms-vcs-code { width:48px !important; height:34px !important; font-size:15px !important; }
08045:         html[data-mcms-tablet-active="true"] #${SCRIPT.vehicleStatusId} .mcms-vcs-status { font-size:13px !important; }
08046:         html[data-mcms-tablet-active="true"] #${SCRIPT.vehicleStatusId} .mcms-vcs-count { font-size:15px !important; }
08047:         html[data-mcms-tablet-active="true"] #${SCRIPT.vehicleStatusId} .mcms-vcs-table-head,
08048:         html[data-mcms-tablet-active="true"] #${SCRIPT.vehicleStatusId} .mcms-vcs-footnote { font-size:9.5px !important; }
08049: 
08050:         /* iOS Mobile: full-width bottom sheet; no horizontal scroll. */
08051:         html[data-mcms-mobile-active="true"] #${SCRIPT.vehicleStatusId} {
08052:             top:auto !important;
08053:             right:0 !important;
```

### Lines 8068-8078
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
```

### Lines 8071-8081
```text
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
```

### Lines 8169-8179
```text
08169:         #${SCRIPT.vehicleStatusId} .mcms-vcs-subtitle { margin-top:2px !important; font-size:8px !important; }
08170:         #${SCRIPT.vehicleStatusId} .mcms-vcs-refresh,
08171:         #${SCRIPT.vehicleStatusId} .mcms-vcs-close { width:29px !important; height:29px !important; font-size:16px !important; }
08172:         #${SCRIPT.vehicleStatusId} .mcms-vcs-meta { padding:6px 2px !important; font-size:7.7px !important; }
08173:         #${SCRIPT.vehicleStatusId} .mcms-vcs-table-row {
08174:             grid-template-columns:54px minmax(0,1fr) 76px !important;
08175:             gap:7px !important;
08176:             min-height:34px !important;
08177:             padding:4px 8px !important;
08178:         }
08179:         #${SCRIPT.vehicleStatusId} .mcms-vcs-table-head { min-height:28px !important; font-size:7.6px !important; }
```

### Lines 8182-8192
```text
08182:         #${SCRIPT.vehicleStatusId} .mcms-vcs-count { font-size:11.5px !important; }
08183:         #${SCRIPT.vehicleStatusId} .mcms-vcs-total-row { min-height:36px !important; font-size:9.4px !important; }
08184:         #${SCRIPT.vehicleStatusId} .mcms-vcs-total-row strong:last-child { font-size:12px !important; }
08185:         #${SCRIPT.vehicleStatusId} .mcms-vcs-footnote { margin-top:6px !important; padding:6px 7px !important; font-size:7.2px !important; }
08186: 
08187:         html[data-mcms-tablet-active="true"] #${SCRIPT.vehicleStatusId} {
08188:             top:max(10px,env(safe-area-inset-top)) !important;
08189:             right:10px !important;
08190:             width:min(560px,calc(100vw - 20px)) !important;
08191:             max-height:calc(100vh - 20px - env(safe-area-inset-bottom)) !important;
08192:             padding:12px !important;
```

### Lines 8190-8200
```text
08190:             width:min(560px,calc(100vw - 20px)) !important;
08191:             max-height:calc(100vh - 20px - env(safe-area-inset-bottom)) !important;
08192:             padding:12px !important;
08193:             border-radius:13px !important;
08194:         }
08195:         html[data-mcms-tablet-active="true"] #${SCRIPT.vehicleStatusId} .mcms-vcs-title { font-size:15px !important; }
08196:         html[data-mcms-tablet-active="true"] #${SCRIPT.vehicleStatusId} .mcms-vcs-subtitle,
08197:         html[data-mcms-tablet-active="true"] #${SCRIPT.vehicleStatusId} .mcms-vcs-meta { font-size:9px !important; }
08198:         html[data-mcms-tablet-active="true"] #${SCRIPT.vehicleStatusId} .mcms-vcs-refresh,
08199:         html[data-mcms-tablet-active="true"] #${SCRIPT.vehicleStatusId} .mcms-vcs-close { width:40px !important; height:40px !important; border-radius:10px !important; font-size:20px !important; }
08200:         html[data-mcms-tablet-active="true"] #${SCRIPT.vehicleStatusId} .mcms-vcs-table-row {
```

### Lines 8191-8201
```text
08191:             max-height:calc(100vh - 20px - env(safe-area-inset-bottom)) !important;
08192:             padding:12px !important;
08193:             border-radius:13px !important;
08194:         }
08195:         html[data-mcms-tablet-active="true"] #${SCRIPT.vehicleStatusId} .mcms-vcs-title { font-size:15px !important; }
08196:         html[data-mcms-tablet-active="true"] #${SCRIPT.vehicleStatusId} .mcms-vcs-subtitle,
08197:         html[data-mcms-tablet-active="true"] #${SCRIPT.vehicleStatusId} .mcms-vcs-meta { font-size:9px !important; }
08198:         html[data-mcms-tablet-active="true"] #${SCRIPT.vehicleStatusId} .mcms-vcs-refresh,
08199:         html[data-mcms-tablet-active="true"] #${SCRIPT.vehicleStatusId} .mcms-vcs-close { width:40px !important; height:40px !important; border-radius:10px !important; font-size:20px !important; }
08200:         html[data-mcms-tablet-active="true"] #${SCRIPT.vehicleStatusId} .mcms-vcs-table-row {
08201:             grid-template-columns:62px minmax(0,1fr) 82px !important;
```

### Lines 8192-8202
```text
08192:             padding:12px !important;
08193:             border-radius:13px !important;
08194:         }
08195:         html[data-mcms-tablet-active="true"] #${SCRIPT.vehicleStatusId} .mcms-vcs-title { font-size:15px !important; }
08196:         html[data-mcms-tablet-active="true"] #${SCRIPT.vehicleStatusId} .mcms-vcs-subtitle,
08197:         html[data-mcms-tablet-active="true"] #${SCRIPT.vehicleStatusId} .mcms-vcs-meta { font-size:9px !important; }
08198:         html[data-mcms-tablet-active="true"] #${SCRIPT.vehicleStatusId} .mcms-vcs-refresh,
08199:         html[data-mcms-tablet-active="true"] #${SCRIPT.vehicleStatusId} .mcms-vcs-close { width:40px !important; height:40px !important; border-radius:10px !important; font-size:20px !important; }
08200:         html[data-mcms-tablet-active="true"] #${SCRIPT.vehicleStatusId} .mcms-vcs-table-row {
08201:             grid-template-columns:62px minmax(0,1fr) 82px !important;
08202:             gap:8px !important;
```

### Lines 8193-8203
```text
08193:             border-radius:13px !important;
08194:         }
08195:         html[data-mcms-tablet-active="true"] #${SCRIPT.vehicleStatusId} .mcms-vcs-title { font-size:15px !important; }
08196:         html[data-mcms-tablet-active="true"] #${SCRIPT.vehicleStatusId} .mcms-vcs-subtitle,
08197:         html[data-mcms-tablet-active="true"] #${SCRIPT.vehicleStatusId} .mcms-vcs-meta { font-size:9px !important; }
08198:         html[data-mcms-tablet-active="true"] #${SCRIPT.vehicleStatusId} .mcms-vcs-refresh,
08199:         html[data-mcms-tablet-active="true"] #${SCRIPT.vehicleStatusId} .mcms-vcs-close { width:40px !important; height:40px !important; border-radius:10px !important; font-size:20px !important; }
08200:         html[data-mcms-tablet-active="true"] #${SCRIPT.vehicleStatusId} .mcms-vcs-table-row {
08201:             grid-template-columns:62px minmax(0,1fr) 82px !important;
08202:             gap:8px !important;
08203:             min-height:42px !important;
```

### Lines 8194-8204
```text
08194:         }
08195:         html[data-mcms-tablet-active="true"] #${SCRIPT.vehicleStatusId} .mcms-vcs-title { font-size:15px !important; }
08196:         html[data-mcms-tablet-active="true"] #${SCRIPT.vehicleStatusId} .mcms-vcs-subtitle,
08197:         html[data-mcms-tablet-active="true"] #${SCRIPT.vehicleStatusId} .mcms-vcs-meta { font-size:9px !important; }
08198:         html[data-mcms-tablet-active="true"] #${SCRIPT.vehicleStatusId} .mcms-vcs-refresh,
08199:         html[data-mcms-tablet-active="true"] #${SCRIPT.vehicleStatusId} .mcms-vcs-close { width:40px !important; height:40px !important; border-radius:10px !important; font-size:20px !important; }
08200:         html[data-mcms-tablet-active="true"] #${SCRIPT.vehicleStatusId} .mcms-vcs-table-row {
08201:             grid-template-columns:62px minmax(0,1fr) 82px !important;
08202:             gap:8px !important;
08203:             min-height:42px !important;
08204:             padding:5px 9px !important;
```

### Lines 8195-8205
```text
08195:         html[data-mcms-tablet-active="true"] #${SCRIPT.vehicleStatusId} .mcms-vcs-title { font-size:15px !important; }
08196:         html[data-mcms-tablet-active="true"] #${SCRIPT.vehicleStatusId} .mcms-vcs-subtitle,
08197:         html[data-mcms-tablet-active="true"] #${SCRIPT.vehicleStatusId} .mcms-vcs-meta { font-size:9px !important; }
08198:         html[data-mcms-tablet-active="true"] #${SCRIPT.vehicleStatusId} .mcms-vcs-refresh,
08199:         html[data-mcms-tablet-active="true"] #${SCRIPT.vehicleStatusId} .mcms-vcs-close { width:40px !important; height:40px !important; border-radius:10px !important; font-size:20px !important; }
08200:         html[data-mcms-tablet-active="true"] #${SCRIPT.vehicleStatusId} .mcms-vcs-table-row {
08201:             grid-template-columns:62px minmax(0,1fr) 82px !important;
08202:             gap:8px !important;
08203:             min-height:42px !important;
08204:             padding:5px 9px !important;
08205:         }
```

### Lines 8196-8206
```text
08196:         html[data-mcms-tablet-active="true"] #${SCRIPT.vehicleStatusId} .mcms-vcs-subtitle,
08197:         html[data-mcms-tablet-active="true"] #${SCRIPT.vehicleStatusId} .mcms-vcs-meta { font-size:9px !important; }
08198:         html[data-mcms-tablet-active="true"] #${SCRIPT.vehicleStatusId} .mcms-vcs-refresh,
08199:         html[data-mcms-tablet-active="true"] #${SCRIPT.vehicleStatusId} .mcms-vcs-close { width:40px !important; height:40px !important; border-radius:10px !important; font-size:20px !important; }
08200:         html[data-mcms-tablet-active="true"] #${SCRIPT.vehicleStatusId} .mcms-vcs-table-row {
08201:             grid-template-columns:62px minmax(0,1fr) 82px !important;
08202:             gap:8px !important;
08203:             min-height:42px !important;
08204:             padding:5px 9px !important;
08205:         }
08206:         html[data-mcms-tablet-active="true"] #${SCRIPT.vehicleStatusId} .mcms-vcs-table-head { min-height:29px !important; font-size:8.3px !important; }
```

### Lines 8201-8211
```text
08201:             grid-template-columns:62px minmax(0,1fr) 82px !important;
08202:             gap:8px !important;
08203:             min-height:42px !important;
08204:             padding:5px 9px !important;
08205:         }
08206:         html[data-mcms-tablet-active="true"] #${SCRIPT.vehicleStatusId} .mcms-vcs-table-head { min-height:29px !important; font-size:8.3px !important; }
08207:         html[data-mcms-tablet-active="true"] #${SCRIPT.vehicleStatusId} .mcms-vcs-code { width:42px !important; height:29px !important; font-size:13px !important; }
08208:         html[data-mcms-tablet-active="true"] #${SCRIPT.vehicleStatusId} .mcms-vcs-status { font-size:11.5px !important; }
08209:         html[data-mcms-tablet-active="true"] #${SCRIPT.vehicleStatusId} .mcms-vcs-count { font-size:13px !important; }
08210:         html[data-mcms-tablet-active="true"] #${SCRIPT.vehicleStatusId} .mcms-vcs-total-row { min-height:40px !important; }
08211:         html[data-mcms-tablet-active="true"] #${SCRIPT.vehicleStatusId} .mcms-vcs-footnote { font-size:8.2px !important; }
```

### Lines 8202-8212
```text
08202:             gap:8px !important;
08203:             min-height:42px !important;
08204:             padding:5px 9px !important;
08205:         }
08206:         html[data-mcms-tablet-active="true"] #${SCRIPT.vehicleStatusId} .mcms-vcs-table-head { min-height:29px !important; font-size:8.3px !important; }
08207:         html[data-mcms-tablet-active="true"] #${SCRIPT.vehicleStatusId} .mcms-vcs-code { width:42px !important; height:29px !important; font-size:13px !important; }
08208:         html[data-mcms-tablet-active="true"] #${SCRIPT.vehicleStatusId} .mcms-vcs-status { font-size:11.5px !important; }
08209:         html[data-mcms-tablet-active="true"] #${SCRIPT.vehicleStatusId} .mcms-vcs-count { font-size:13px !important; }
08210:         html[data-mcms-tablet-active="true"] #${SCRIPT.vehicleStatusId} .mcms-vcs-total-row { min-height:40px !important; }
08211:         html[data-mcms-tablet-active="true"] #${SCRIPT.vehicleStatusId} .mcms-vcs-footnote { font-size:8.2px !important; }
08212: 
```

### Lines 8203-8213
```text
08203:             min-height:42px !important;
08204:             padding:5px 9px !important;
08205:         }
08206:         html[data-mcms-tablet-active="true"] #${SCRIPT.vehicleStatusId} .mcms-vcs-table-head { min-height:29px !important; font-size:8.3px !important; }
08207:         html[data-mcms-tablet-active="true"] #${SCRIPT.vehicleStatusId} .mcms-vcs-code { width:42px !important; height:29px !important; font-size:13px !important; }
08208:         html[data-mcms-tablet-active="true"] #${SCRIPT.vehicleStatusId} .mcms-vcs-status { font-size:11.5px !important; }
08209:         html[data-mcms-tablet-active="true"] #${SCRIPT.vehicleStatusId} .mcms-vcs-count { font-size:13px !important; }
08210:         html[data-mcms-tablet-active="true"] #${SCRIPT.vehicleStatusId} .mcms-vcs-total-row { min-height:40px !important; }
08211:         html[data-mcms-tablet-active="true"] #${SCRIPT.vehicleStatusId} .mcms-vcs-footnote { font-size:8.2px !important; }
08212: 
08213:         html[data-mcms-mobile-active="true"] #${SCRIPT.vehicleStatusId} {
```

### Lines 8204-8214
```text
08204:             padding:5px 9px !important;
08205:         }
08206:         html[data-mcms-tablet-active="true"] #${SCRIPT.vehicleStatusId} .mcms-vcs-table-head { min-height:29px !important; font-size:8.3px !important; }
08207:         html[data-mcms-tablet-active="true"] #${SCRIPT.vehicleStatusId} .mcms-vcs-code { width:42px !important; height:29px !important; font-size:13px !important; }
08208:         html[data-mcms-tablet-active="true"] #${SCRIPT.vehicleStatusId} .mcms-vcs-status { font-size:11.5px !important; }
08209:         html[data-mcms-tablet-active="true"] #${SCRIPT.vehicleStatusId} .mcms-vcs-count { font-size:13px !important; }
08210:         html[data-mcms-tablet-active="true"] #${SCRIPT.vehicleStatusId} .mcms-vcs-total-row { min-height:40px !important; }
08211:         html[data-mcms-tablet-active="true"] #${SCRIPT.vehicleStatusId} .mcms-vcs-footnote { font-size:8.2px !important; }
08212: 
08213:         html[data-mcms-mobile-active="true"] #${SCRIPT.vehicleStatusId} {
08214:             max-height:min(84vh,calc(100dvh - env(safe-area-inset-top) - 8px)) !important;
```

### Lines 8205-8215
```text
08205:         }
08206:         html[data-mcms-tablet-active="true"] #${SCRIPT.vehicleStatusId} .mcms-vcs-table-head { min-height:29px !important; font-size:8.3px !important; }
08207:         html[data-mcms-tablet-active="true"] #${SCRIPT.vehicleStatusId} .mcms-vcs-code { width:42px !important; height:29px !important; font-size:13px !important; }
08208:         html[data-mcms-tablet-active="true"] #${SCRIPT.vehicleStatusId} .mcms-vcs-status { font-size:11.5px !important; }
08209:         html[data-mcms-tablet-active="true"] #${SCRIPT.vehicleStatusId} .mcms-vcs-count { font-size:13px !important; }
08210:         html[data-mcms-tablet-active="true"] #${SCRIPT.vehicleStatusId} .mcms-vcs-total-row { min-height:40px !important; }
08211:         html[data-mcms-tablet-active="true"] #${SCRIPT.vehicleStatusId} .mcms-vcs-footnote { font-size:8.2px !important; }
08212: 
08213:         html[data-mcms-mobile-active="true"] #${SCRIPT.vehicleStatusId} {
08214:             max-height:min(84vh,calc(100dvh - env(safe-area-inset-top) - 8px)) !important;
08215:             padding:10px 8px calc(10px + env(safe-area-inset-bottom)) !important;
```

### Lines 8206-8216
```text
08206:         html[data-mcms-tablet-active="true"] #${SCRIPT.vehicleStatusId} .mcms-vcs-table-head { min-height:29px !important; font-size:8.3px !important; }
08207:         html[data-mcms-tablet-active="true"] #${SCRIPT.vehicleStatusId} .mcms-vcs-code { width:42px !important; height:29px !important; font-size:13px !important; }
08208:         html[data-mcms-tablet-active="true"] #${SCRIPT.vehicleStatusId} .mcms-vcs-status { font-size:11.5px !important; }
08209:         html[data-mcms-tablet-active="true"] #${SCRIPT.vehicleStatusId} .mcms-vcs-count { font-size:13px !important; }
08210:         html[data-mcms-tablet-active="true"] #${SCRIPT.vehicleStatusId} .mcms-vcs-total-row { min-height:40px !important; }
08211:         html[data-mcms-tablet-active="true"] #${SCRIPT.vehicleStatusId} .mcms-vcs-footnote { font-size:8.2px !important; }
08212: 
08213:         html[data-mcms-mobile-active="true"] #${SCRIPT.vehicleStatusId} {
08214:             max-height:min(84vh,calc(100dvh - env(safe-area-inset-top) - 8px)) !important;
08215:             padding:10px 8px calc(10px + env(safe-area-inset-bottom)) !important;
08216:         }
```

### Lines 8219-8229
```text
08219:         html[data-mcms-mobile-active="true"] #${SCRIPT.vehicleStatusId} .mcms-vcs-refresh,
08220:         html[data-mcms-mobile-active="true"] #${SCRIPT.vehicleStatusId} .mcms-vcs-close { width:40px !important; height:40px !important; font-size:20px !important; }
08221:         html[data-mcms-mobile-active="true"] #${SCRIPT.vehicleStatusId} .mcms-vcs-meta {
08222:             align-items:center !important;
08223:             flex-direction:row !important;
08224:             flex-wrap:wrap !important;
08225:             gap:3px 8px !important;
08226:             font-size:8px !important;
08227:         }
08228:         html[data-mcms-mobile-active="true"] #${SCRIPT.vehicleStatusId} .mcms-vcs-table-row {
08229:             grid-template-columns:44px minmax(0,1fr) 58px !important;
```

### Lines 8224-8234
```text
08224:             flex-wrap:wrap !important;
08225:             gap:3px 8px !important;
08226:             font-size:8px !important;
08227:         }
08228:         html[data-mcms-mobile-active="true"] #${SCRIPT.vehicleStatusId} .mcms-vcs-table-row {
08229:             grid-template-columns:44px minmax(0,1fr) 58px !important;
08230:             gap:5px !important;
08231:             min-height:39px !important;
08232:             padding:5px 6px !important;
08233:         }
08234:         html[data-mcms-mobile-active="true"] #${SCRIPT.vehicleStatusId} .mcms-vcs-table-head { min-height:28px !important; font-size:7.3px !important; }
```

### Lines 8236-8246
```text
08236:         html[data-mcms-mobile-active="true"] #${SCRIPT.vehicleStatusId} .mcms-vcs-status { font-size:9.6px !important; }
08237:         html[data-mcms-mobile-active="true"] #${SCRIPT.vehicleStatusId} .mcms-vcs-count { font-size:11.5px !important; }
08238:         html[data-mcms-mobile-active="true"] #${SCRIPT.vehicleStatusId} .mcms-vcs-total-row { min-height:37px !important; }
08239:         html[data-mcms-mobile-active="true"] #${SCRIPT.vehicleStatusId} .mcms-vcs-footnote { font-size:7.2px !important; }
08240: 
08241:         @media (prefers-reduced-motion:reduce) {
08242:             #${SCRIPT.vehicleStatusId}.mcms-open,
08243:             #${SCRIPT.vehicleStatusId}.mcms-vcs-loading .mcms-vcs-refresh { animation:none !important; }
08244:         }
08245: 
08246:         /* ============================================================
```

### Lines 8261-8271
```text
08261:         @keyframes mcms-critical-drawer-enter {
08262:             from { opacity:0; transform:translateY(-8px) scale(.985); }
08263:             to { opacity:1; transform:translateY(0) scale(1); }
08264:         }
08265:         #${SCRIPT.criticalDrawerId} .mcms-drawer-head {
08266:             grid-template-columns:minmax(0,1fr) auto !important;
08267:             gap:8px !important;
08268:             min-height:36px !important;
08269:             padding-bottom:7px !important;
08270:         }
08271:         #${SCRIPT.criticalDrawerId} .mcms-drawer-heading { min-width:0 !important; }
```

### Lines 8287-8297
```text
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
```

### Lines 8291-8301
```text
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
08301:         }
```

### Lines 8310-8320
```text
08310:             text-transform:uppercase !important;
08311:         }
08312:         #${SCRIPT.criticalDrawerId} .mcms-critical-age-filter {
08313:             position:relative !important;
08314:             display:grid !important;
08315:             grid-template-columns:minmax(0,1fr) auto !important;
08316:             align-items:center !important;
08317:             min-width:0 !important;
08318:             min-height:24px !important;
08319:             gap:3px !important;
08320:             padding:3px 5px !important;
```

### Lines 8329-8339
```text
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
```

### Lines 8393-8403
```text
08393:         #${SCRIPT.criticalDrawerId} .mcms-drawer-refresh:disabled { cursor:wait !important; opacity:.62 !important; }
08394:         @keyframes mcms-critical-refresh-spin { to { transform:rotate(360deg); } }
08395: 
08396:         #${SCRIPT.criticalDrawerId} .mcms-critical-type-filters {
08397:             display:grid !important;
08398:             grid-template-columns:auto repeat(3,minmax(0,1fr)) !important;
08399:             align-items:stretch !important;
08400:             gap:4px !important;
08401:             margin-top:5px !important;
08402:         }
08403:         #${SCRIPT.criticalDrawerId} .mcms-critical-type-label {
```

### Lines 8413-8423
```text
08413:             text-transform:uppercase !important;
08414:         }
08415:         #${SCRIPT.criticalDrawerId} .mcms-critical-type-filter {
08416:             position:relative !important;
08417:             display:grid !important;
08418:             grid-template-columns:minmax(0,1fr) auto !important;
08419:             align-items:center !important;
08420:             min-width:0 !important;
08421:             min-height:27px !important;
08422:             gap:5px !important;
08423:             padding:4px 7px !important;
```

### Lines 8433-8443
```text
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
```

### Lines 8435-8445
```text
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
```

### Lines 8475-8485
```text
08475:         #${SCRIPT.criticalDrawerId} .mcms-type-event { border-color:rgba(202,126,255,.78) !important; color:#e5b5ff !important; background:rgba(54,17,78,.48) !important; }
08476:         #${SCRIPT.criticalDrawerId} .mcms-type-alliance { border-color:rgba(79,174,255,.82) !important; color:#8ed1ff !important; background:rgba(4,38,68,.50) !important; }
08477: 
08478:         #${SCRIPT.criticalDrawerId} .mcms-critical-summary {
08479:             display:grid !important;
08480:             grid-template-columns:repeat(5,minmax(0,1fr)) !important;
08481:             gap:4px !important;
08482:             margin-top:6px !important;
08483:         }
08484:         #${SCRIPT.criticalDrawerId} .mcms-critical-summary-card {
08485:             min-width:0 !important;
```

### Lines 8570-8580
```text
08570:             outline:2px solid currentColor !important;
08571:             outline-offset:1px !important;
08572:         }
08573:         #${SCRIPT.criticalDrawerId} .mcms-critical-values-grid {
08574:             display:grid !important;
08575:             grid-template-columns:repeat(3,minmax(0,1fr)) !important;
08576:             gap:4px !important;
08577:         }
08578:         #${SCRIPT.criticalDrawerId} .mcms-critical-value-card {
08579:             min-width:0 !important;
08580:             padding:5px 4px !important;
```

### Lines 8598-8608
```text
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
```

### Lines 8599-8609
```text
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
```

### Lines 8670-8680
```text
08670:         #${SCRIPT.criticalDrawerId} .mcms-critical-top-identifiers {
08671:             display:flex !important;
08672:             min-width:0 !important;
08673:             align-items:center !important;
08674:             gap:5px !important;
08675:             flex-wrap:wrap !important;
08676:         }
08677:         #${SCRIPT.criticalDrawerId} .mcms-critical-type-badge {
08678:             display:inline-flex !important;
08679:             min-height:17px !important;
08680:             align-items:center !important;
```

### Lines 8684-8694
```text
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
```

### Lines 8749-8759
```text
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
```

### Lines 8751-8761
```text
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
```

### Lines 8780-8790
```text
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
```

### Lines 8797-8807
```text
08797:             font:900 6.4px/1 Arial,sans-serif !important;
08798:             letter-spacing:.45px !important;
08799:         }
08800:         #${SCRIPT.criticalDrawerId} .mcms-critical-lowerline {
08801:             display:grid !important;
08802:             grid-template-columns:minmax(0,1fr) 118px !important;
08803:             gap:5px !important;
08804:             align-items:stretch !important;
08805:             margin-top:5px !important;
08806:         }
08807:         #${SCRIPT.criticalDrawerId} .mcms-critical-state {
```

### Lines 8805-8815
```text
08805:             margin-top:5px !important;
08806:         }
08807:         #${SCRIPT.criticalDrawerId} .mcms-critical-state {
08808:             position:relative !important;
08809:             display:grid !important;
08810:             grid-template-columns:18px minmax(0,1fr) !important;
08811:             gap:6px !important;
08812:             align-items:center !important;
08813:             margin-top:0 !important;
08814:             padding:5px 6px !important;
08815:             border:1px solid rgba(255,255,255,.16) !important;
```

### Lines 8836-8846
```text
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
```

### Lines 8840-8850
```text
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
08850:             display:flex !important;
```

### Lines 9042-9052
```text
09042:             50% { filter:brightness(1.09); box-shadow:inset 0 0 0 1px rgba(126,255,176,.18),0 0 14px rgba(55,222,125,.19); }
09043:         }
09044:         html[data-mcms-ui-theme] #${SCRIPT.criticalDrawerId} .mcms-unit-scene { border-color:rgba(59,211,123,.48) !important; color:#a6efc3 !important; }
09045:         html[data-mcms-ui-theme] #${SCRIPT.criticalDrawerId} .mcms-unit-way { border-color:rgba(72,188,255,.48) !important; color:#a9e2ff !important; }
09046: 
09047:         html[data-mcms-tablet-active="true"] #${SCRIPT.criticalDrawerId} {
09048:             width:min(510px,calc(100vw - 18px)) !important;
09049:             max-width:calc(100vw - 18px) !important;
09050:             max-height:80dvh !important;
09051:             padding:10px !important;
09052:         }
```

### Lines 9048-9058
```text
09048:             width:min(510px,calc(100vw - 18px)) !important;
09049:             max-width:calc(100vw - 18px) !important;
09050:             max-height:80dvh !important;
09051:             padding:10px !important;
09052:         }
09053:         html[data-mcms-tablet-active="true"] #${SCRIPT.criticalDrawerId} .mcms-drawer-head { grid-template-columns:minmax(0,1fr) auto !important; min-height:42px !important; }
09054:         html[data-mcms-tablet-active="true"] #${SCRIPT.criticalDrawerId} .mcms-drawer-refresh,
09055:         html[data-mcms-tablet-active="true"] #${SCRIPT.criticalDrawerId} .mcms-drawer-close { width:38px !important; height:38px !important; font-size:19px !important; }
09056:         html[data-mcms-tablet-active="true"] #${SCRIPT.criticalDrawerId} .mcms-critical-refreshed { font-size:8.4px !important; }
09057:         html[data-mcms-tablet-active="true"] #${SCRIPT.criticalDrawerId} .mcms-critical-zoom,
09058:         html[data-mcms-tablet-active="true"] #${SCRIPT.criticalDrawerId} .mcms-critical-open { min-width:64px !important; height:32px !important; padding:0 8px !important; font-size:9px !important; }
```

### Lines 9049-9059
```text
09049:             max-width:calc(100vw - 18px) !important;
09050:             max-height:80dvh !important;
09051:             padding:10px !important;
09052:         }
09053:         html[data-mcms-tablet-active="true"] #${SCRIPT.criticalDrawerId} .mcms-drawer-head { grid-template-columns:minmax(0,1fr) auto !important; min-height:42px !important; }
09054:         html[data-mcms-tablet-active="true"] #${SCRIPT.criticalDrawerId} .mcms-drawer-refresh,
09055:         html[data-mcms-tablet-active="true"] #${SCRIPT.criticalDrawerId} .mcms-drawer-close { width:38px !important; height:38px !important; font-size:19px !important; }
09056:         html[data-mcms-tablet-active="true"] #${SCRIPT.criticalDrawerId} .mcms-critical-refreshed { font-size:8.4px !important; }
09057:         html[data-mcms-tablet-active="true"] #${SCRIPT.criticalDrawerId} .mcms-critical-zoom,
09058:         html[data-mcms-tablet-active="true"] #${SCRIPT.criticalDrawerId} .mcms-critical-open { min-width:64px !important; height:32px !important; padding:0 8px !important; font-size:9px !important; }
09059:         html[data-mcms-tablet-active="true"] #${SCRIPT.criticalDrawerId} .mcms-critical-values { padding:7px !important; }
```

### Lines 9050-9060
```text
09050:             max-height:80dvh !important;
09051:             padding:10px !important;
09052:         }
09053:         html[data-mcms-tablet-active="true"] #${SCRIPT.criticalDrawerId} .mcms-drawer-head { grid-template-columns:minmax(0,1fr) auto !important; min-height:42px !important; }
09054:         html[data-mcms-tablet-active="true"] #${SCRIPT.criticalDrawerId} .mcms-drawer-refresh,
09055:         html[data-mcms-tablet-active="true"] #${SCRIPT.criticalDrawerId} .mcms-drawer-close { width:38px !important; height:38px !important; font-size:19px !important; }
09056:         html[data-mcms-tablet-active="true"] #${SCRIPT.criticalDrawerId} .mcms-critical-refreshed { font-size:8.4px !important; }
09057:         html[data-mcms-tablet-active="true"] #${SCRIPT.criticalDrawerId} .mcms-critical-zoom,
09058:         html[data-mcms-tablet-active="true"] #${SCRIPT.criticalDrawerId} .mcms-critical-open { min-width:64px !important; height:32px !important; padding:0 8px !important; font-size:9px !important; }
09059:         html[data-mcms-tablet-active="true"] #${SCRIPT.criticalDrawerId} .mcms-critical-values { padding:7px !important; }
09060:         html[data-mcms-tablet-active="true"] #${SCRIPT.criticalDrawerId} .mcms-critical-value-card strong { font-size:11px !important; }
```

### Lines 9051-9061
```text
09051:             padding:10px !important;
09052:         }
09053:         html[data-mcms-tablet-active="true"] #${SCRIPT.criticalDrawerId} .mcms-drawer-head { grid-template-columns:minmax(0,1fr) auto !important; min-height:42px !important; }
09054:         html[data-mcms-tablet-active="true"] #${SCRIPT.criticalDrawerId} .mcms-drawer-refresh,
09055:         html[data-mcms-tablet-active="true"] #${SCRIPT.criticalDrawerId} .mcms-drawer-close { width:38px !important; height:38px !important; font-size:19px !important; }
09056:         html[data-mcms-tablet-active="true"] #${SCRIPT.criticalDrawerId} .mcms-critical-refreshed { font-size:8.4px !important; }
09057:         html[data-mcms-tablet-active="true"] #${SCRIPT.criticalDrawerId} .mcms-critical-zoom,
09058:         html[data-mcms-tablet-active="true"] #${SCRIPT.criticalDrawerId} .mcms-critical-open { min-width:64px !important; height:32px !important; padding:0 8px !important; font-size:9px !important; }
09059:         html[data-mcms-tablet-active="true"] #${SCRIPT.criticalDrawerId} .mcms-critical-values { padding:7px !important; }
09060:         html[data-mcms-tablet-active="true"] #${SCRIPT.criticalDrawerId} .mcms-critical-value-card strong { font-size:11px !important; }
09061:         html[data-mcms-tablet-active="true"] #${SCRIPT.criticalDrawerId} .mcms-critical-summary-card { padding:6px !important; }
```

### Lines 9052-9062
```text
09052:         }
09053:         html[data-mcms-tablet-active="true"] #${SCRIPT.criticalDrawerId} .mcms-drawer-head { grid-template-columns:minmax(0,1fr) auto !important; min-height:42px !important; }
09054:         html[data-mcms-tablet-active="true"] #${SCRIPT.criticalDrawerId} .mcms-drawer-refresh,
09055:         html[data-mcms-tablet-active="true"] #${SCRIPT.criticalDrawerId} .mcms-drawer-close { width:38px !important; height:38px !important; font-size:19px !important; }
09056:         html[data-mcms-tablet-active="true"] #${SCRIPT.criticalDrawerId} .mcms-critical-refreshed { font-size:8.4px !important; }
09057:         html[data-mcms-tablet-active="true"] #${SCRIPT.criticalDrawerId} .mcms-critical-zoom,
09058:         html[data-mcms-tablet-active="true"] #${SCRIPT.criticalDrawerId} .mcms-critical-open { min-width:64px !important; height:32px !important; padding:0 8px !important; font-size:9px !important; }
09059:         html[data-mcms-tablet-active="true"] #${SCRIPT.criticalDrawerId} .mcms-critical-values { padding:7px !important; }
09060:         html[data-mcms-tablet-active="true"] #${SCRIPT.criticalDrawerId} .mcms-critical-value-card strong { font-size:11px !important; }
09061:         html[data-mcms-tablet-active="true"] #${SCRIPT.criticalDrawerId} .mcms-critical-summary-card { padding:6px !important; }
09062:         html[data-mcms-tablet-active="true"] #${SCRIPT.criticalDrawerId} .mcms-critical-summary-card span { font-size:7.3px !important; }
```

### Lines 9053-9063
```text
09053:         html[data-mcms-tablet-active="true"] #${SCRIPT.criticalDrawerId} .mcms-drawer-head { grid-template-columns:minmax(0,1fr) auto !important; min-height:42px !important; }
09054:         html[data-mcms-tablet-active="true"] #${SCRIPT.criticalDrawerId} .mcms-drawer-refresh,
09055:         html[data-mcms-tablet-active="true"] #${SCRIPT.criticalDrawerId} .mcms-drawer-close { width:38px !important; height:38px !important; font-size:19px !important; }
09056:         html[data-mcms-tablet-active="true"] #${SCRIPT.criticalDrawerId} .mcms-critical-refreshed { font-size:8.4px !important; }
09057:         html[data-mcms-tablet-active="true"] #${SCRIPT.criticalDrawerId} .mcms-critical-zoom,
09058:         html[data-mcms-tablet-active="true"] #${SCRIPT.criticalDrawerId} .mcms-critical-open { min-width:64px !important; height:32px !important; padding:0 8px !important; font-size:9px !important; }
09059:         html[data-mcms-tablet-active="true"] #${SCRIPT.criticalDrawerId} .mcms-critical-values { padding:7px !important; }
09060:         html[data-mcms-tablet-active="true"] #${SCRIPT.criticalDrawerId} .mcms-critical-value-card strong { font-size:11px !important; }
09061:         html[data-mcms-tablet-active="true"] #${SCRIPT.criticalDrawerId} .mcms-critical-summary-card { padding:6px !important; }
09062:         html[data-mcms-tablet-active="true"] #${SCRIPT.criticalDrawerId} .mcms-critical-summary-card span { font-size:7.3px !important; }
09063:         html[data-mcms-tablet-active="true"] #${SCRIPT.criticalDrawerId} .mcms-critical-summary-card strong { font-size:14px !important; }
```

### Lines 9054-9064
```text
09054:         html[data-mcms-tablet-active="true"] #${SCRIPT.criticalDrawerId} .mcms-drawer-refresh,
09055:         html[data-mcms-tablet-active="true"] #${SCRIPT.criticalDrawerId} .mcms-drawer-close { width:38px !important; height:38px !important; font-size:19px !important; }
09056:         html[data-mcms-tablet-active="true"] #${SCRIPT.criticalDrawerId} .mcms-critical-refreshed { font-size:8.4px !important; }
09057:         html[data-mcms-tablet-active="true"] #${SCRIPT.criticalDrawerId} .mcms-critical-zoom,
09058:         html[data-mcms-tablet-active="true"] #${SCRIPT.criticalDrawerId} .mcms-critical-open { min-width:64px !important; height:32px !important; padding:0 8px !important; font-size:9px !important; }
09059:         html[data-mcms-tablet-active="true"] #${SCRIPT.criticalDrawerId} .mcms-critical-values { padding:7px !important; }
09060:         html[data-mcms-tablet-active="true"] #${SCRIPT.criticalDrawerId} .mcms-critical-value-card strong { font-size:11px !important; }
09061:         html[data-mcms-tablet-active="true"] #${SCRIPT.criticalDrawerId} .mcms-critical-summary-card { padding:6px !important; }
09062:         html[data-mcms-tablet-active="true"] #${SCRIPT.criticalDrawerId} .mcms-critical-summary-card span { font-size:7.3px !important; }
09063:         html[data-mcms-tablet-active="true"] #${SCRIPT.criticalDrawerId} .mcms-critical-summary-card strong { font-size:14px !important; }
09064:         html[data-mcms-tablet-active="true"] #${SCRIPT.criticalDrawerId} .mcms-critical-patients { min-height:24px !important; padding:4px 8px !important; }
```

### Lines 9055-9065
```text
09055:         html[data-mcms-tablet-active="true"] #${SCRIPT.criticalDrawerId} .mcms-drawer-close { width:38px !important; height:38px !important; font-size:19px !important; }
09056:         html[data-mcms-tablet-active="true"] #${SCRIPT.criticalDrawerId} .mcms-critical-refreshed { font-size:8.4px !important; }
09057:         html[data-mcms-tablet-active="true"] #${SCRIPT.criticalDrawerId} .mcms-critical-zoom,
09058:         html[data-mcms-tablet-active="true"] #${SCRIPT.criticalDrawerId} .mcms-critical-open { min-width:64px !important; height:32px !important; padding:0 8px !important; font-size:9px !important; }
09059:         html[data-mcms-tablet-active="true"] #${SCRIPT.criticalDrawerId} .mcms-critical-values { padding:7px !important; }
09060:         html[data-mcms-tablet-active="true"] #${SCRIPT.criticalDrawerId} .mcms-critical-value-card strong { font-size:11px !important; }
09061:         html[data-mcms-tablet-active="true"] #${SCRIPT.criticalDrawerId} .mcms-critical-summary-card { padding:6px !important; }
09062:         html[data-mcms-tablet-active="true"] #${SCRIPT.criticalDrawerId} .mcms-critical-summary-card span { font-size:7.3px !important; }
09063:         html[data-mcms-tablet-active="true"] #${SCRIPT.criticalDrawerId} .mcms-critical-summary-card strong { font-size:14px !important; }
09064:         html[data-mcms-tablet-active="true"] #${SCRIPT.criticalDrawerId} .mcms-critical-patients { min-height:24px !important; padding:4px 8px !important; }
09065:         html[data-mcms-mobile-active="true"] #${SCRIPT.criticalDrawerId} .mcms-critical-titleline { align-items:flex-start !important; }
```

### Lines 9056-9066
```text
09056:         html[data-mcms-tablet-active="true"] #${SCRIPT.criticalDrawerId} .mcms-critical-refreshed { font-size:8.4px !important; }
09057:         html[data-mcms-tablet-active="true"] #${SCRIPT.criticalDrawerId} .mcms-critical-zoom,
09058:         html[data-mcms-tablet-active="true"] #${SCRIPT.criticalDrawerId} .mcms-critical-open { min-width:64px !important; height:32px !important; padding:0 8px !important; font-size:9px !important; }
09059:         html[data-mcms-tablet-active="true"] #${SCRIPT.criticalDrawerId} .mcms-critical-values { padding:7px !important; }
09060:         html[data-mcms-tablet-active="true"] #${SCRIPT.criticalDrawerId} .mcms-critical-value-card strong { font-size:11px !important; }
09061:         html[data-mcms-tablet-active="true"] #${SCRIPT.criticalDrawerId} .mcms-critical-summary-card { padding:6px !important; }
09062:         html[data-mcms-tablet-active="true"] #${SCRIPT.criticalDrawerId} .mcms-critical-summary-card span { font-size:7.3px !important; }
09063:         html[data-mcms-tablet-active="true"] #${SCRIPT.criticalDrawerId} .mcms-critical-summary-card strong { font-size:14px !important; }
09064:         html[data-mcms-tablet-active="true"] #${SCRIPT.criticalDrawerId} .mcms-critical-patients { min-height:24px !important; padding:4px 8px !important; }
09065:         html[data-mcms-mobile-active="true"] #${SCRIPT.criticalDrawerId} .mcms-critical-titleline { align-items:flex-start !important; }
09066:         html[data-mcms-mobile-active="true"] #${SCRIPT.criticalDrawerId} .mcms-critical-patients { min-height:20px !important; padding:3px 6px !important; }
```

### Lines 9057-9067
```text
09057:         html[data-mcms-tablet-active="true"] #${SCRIPT.criticalDrawerId} .mcms-critical-zoom,
09058:         html[data-mcms-tablet-active="true"] #${SCRIPT.criticalDrawerId} .mcms-critical-open { min-width:64px !important; height:32px !important; padding:0 8px !important; font-size:9px !important; }
09059:         html[data-mcms-tablet-active="true"] #${SCRIPT.criticalDrawerId} .mcms-critical-values { padding:7px !important; }
09060:         html[data-mcms-tablet-active="true"] #${SCRIPT.criticalDrawerId} .mcms-critical-value-card strong { font-size:11px !important; }
09061:         html[data-mcms-tablet-active="true"] #${SCRIPT.criticalDrawerId} .mcms-critical-summary-card { padding:6px !important; }
09062:         html[data-mcms-tablet-active="true"] #${SCRIPT.criticalDrawerId} .mcms-critical-summary-card span { font-size:7.3px !important; }
09063:         html[data-mcms-tablet-active="true"] #${SCRIPT.criticalDrawerId} .mcms-critical-summary-card strong { font-size:14px !important; }
09064:         html[data-mcms-tablet-active="true"] #${SCRIPT.criticalDrawerId} .mcms-critical-patients { min-height:24px !important; padding:4px 8px !important; }
09065:         html[data-mcms-mobile-active="true"] #${SCRIPT.criticalDrawerId} .mcms-critical-titleline { align-items:flex-start !important; }
09066:         html[data-mcms-mobile-active="true"] #${SCRIPT.criticalDrawerId} .mcms-critical-patients { min-height:20px !important; padding:3px 6px !important; }
09067:         html[data-mcms-tablet-active="true"] #${SCRIPT.criticalDrawerId} .mcms-critical-row { padding:9px !important; }
```

### Lines 9058-9068
```text
09058:         html[data-mcms-tablet-active="true"] #${SCRIPT.criticalDrawerId} .mcms-critical-open { min-width:64px !important; height:32px !important; padding:0 8px !important; font-size:9px !important; }
09059:         html[data-mcms-tablet-active="true"] #${SCRIPT.criticalDrawerId} .mcms-critical-values { padding:7px !important; }
09060:         html[data-mcms-tablet-active="true"] #${SCRIPT.criticalDrawerId} .mcms-critical-value-card strong { font-size:11px !important; }
09061:         html[data-mcms-tablet-active="true"] #${SCRIPT.criticalDrawerId} .mcms-critical-summary-card { padding:6px !important; }
09062:         html[data-mcms-tablet-active="true"] #${SCRIPT.criticalDrawerId} .mcms-critical-summary-card span { font-size:7.3px !important; }
09063:         html[data-mcms-tablet-active="true"] #${SCRIPT.criticalDrawerId} .mcms-critical-summary-card strong { font-size:14px !important; }
09064:         html[data-mcms-tablet-active="true"] #${SCRIPT.criticalDrawerId} .mcms-critical-patients { min-height:24px !important; padding:4px 8px !important; }
09065:         html[data-mcms-mobile-active="true"] #${SCRIPT.criticalDrawerId} .mcms-critical-titleline { align-items:flex-start !important; }
09066:         html[data-mcms-mobile-active="true"] #${SCRIPT.criticalDrawerId} .mcms-critical-patients { min-height:20px !important; padding:3px 6px !important; }
09067:         html[data-mcms-tablet-active="true"] #${SCRIPT.criticalDrawerId} .mcms-critical-row { padding:9px !important; }
09068:         html[data-mcms-tablet-active="true"] #${SCRIPT.criticalDrawerId} .mcms-critical-name { font-size:12.8px !important; }
```

### Lines 9059-9069
```text
09059:         html[data-mcms-tablet-active="true"] #${SCRIPT.criticalDrawerId} .mcms-critical-values { padding:7px !important; }
09060:         html[data-mcms-tablet-active="true"] #${SCRIPT.criticalDrawerId} .mcms-critical-value-card strong { font-size:11px !important; }
09061:         html[data-mcms-tablet-active="true"] #${SCRIPT.criticalDrawerId} .mcms-critical-summary-card { padding:6px !important; }
09062:         html[data-mcms-tablet-active="true"] #${SCRIPT.criticalDrawerId} .mcms-critical-summary-card span { font-size:7.3px !important; }
09063:         html[data-mcms-tablet-active="true"] #${SCRIPT.criticalDrawerId} .mcms-critical-summary-card strong { font-size:14px !important; }
09064:         html[data-mcms-tablet-active="true"] #${SCRIPT.criticalDrawerId} .mcms-critical-patients { min-height:24px !important; padding:4px 8px !important; }
09065:         html[data-mcms-mobile-active="true"] #${SCRIPT.criticalDrawerId} .mcms-critical-titleline { align-items:flex-start !important; }
09066:         html[data-mcms-mobile-active="true"] #${SCRIPT.criticalDrawerId} .mcms-critical-patients { min-height:20px !important; padding:3px 6px !important; }
09067:         html[data-mcms-tablet-active="true"] #${SCRIPT.criticalDrawerId} .mcms-critical-row { padding:9px !important; }
09068:         html[data-mcms-tablet-active="true"] #${SCRIPT.criticalDrawerId} .mcms-critical-name { font-size:12.8px !important; }
09069:         html[data-mcms-tablet-active="true"] #${SCRIPT.criticalDrawerId} .mcms-critical-lowerline { grid-template-columns:minmax(0,1fr) 136px !important; gap:6px !important; }
```

### Lines 9062-9072
```text
09062:         html[data-mcms-tablet-active="true"] #${SCRIPT.criticalDrawerId} .mcms-critical-summary-card span { font-size:7.3px !important; }
09063:         html[data-mcms-tablet-active="true"] #${SCRIPT.criticalDrawerId} .mcms-critical-summary-card strong { font-size:14px !important; }
09064:         html[data-mcms-tablet-active="true"] #${SCRIPT.criticalDrawerId} .mcms-critical-patients { min-height:24px !important; padding:4px 8px !important; }
09065:         html[data-mcms-mobile-active="true"] #${SCRIPT.criticalDrawerId} .mcms-critical-titleline { align-items:flex-start !important; }
09066:         html[data-mcms-mobile-active="true"] #${SCRIPT.criticalDrawerId} .mcms-critical-patients { min-height:20px !important; padding:3px 6px !important; }
09067:         html[data-mcms-tablet-active="true"] #${SCRIPT.criticalDrawerId} .mcms-critical-row { padding:9px !important; }
09068:         html[data-mcms-tablet-active="true"] #${SCRIPT.criticalDrawerId} .mcms-critical-name { font-size:12.8px !important; }
09069:         html[data-mcms-tablet-active="true"] #${SCRIPT.criticalDrawerId} .mcms-critical-lowerline { grid-template-columns:minmax(0,1fr) 136px !important; gap:6px !important; }
09070:         html[data-mcms-tablet-active="true"] #${SCRIPT.criticalDrawerId} .mcms-critical-state-copy strong { font-size:9.7px !important; }
09071:         html[data-mcms-tablet-active="true"] #${SCRIPT.criticalDrawerId} .mcms-critical-state-copy small { font-size:8.7px !important; }
09072:         html[data-mcms-tablet-active="true"] #${SCRIPT.criticalDrawerId} .mcms-critical-unit-chip strong { font-size:14px !important; }
```

### Lines 9063-9073
```text
09063:         html[data-mcms-tablet-active="true"] #${SCRIPT.criticalDrawerId} .mcms-critical-summary-card strong { font-size:14px !important; }
09064:         html[data-mcms-tablet-active="true"] #${SCRIPT.criticalDrawerId} .mcms-critical-patients { min-height:24px !important; padding:4px 8px !important; }
09065:         html[data-mcms-mobile-active="true"] #${SCRIPT.criticalDrawerId} .mcms-critical-titleline { align-items:flex-start !important; }
09066:         html[data-mcms-mobile-active="true"] #${SCRIPT.criticalDrawerId} .mcms-critical-patients { min-height:20px !important; padding:3px 6px !important; }
09067:         html[data-mcms-tablet-active="true"] #${SCRIPT.criticalDrawerId} .mcms-critical-row { padding:9px !important; }
09068:         html[data-mcms-tablet-active="true"] #${SCRIPT.criticalDrawerId} .mcms-critical-name { font-size:12.8px !important; }
09069:         html[data-mcms-tablet-active="true"] #${SCRIPT.criticalDrawerId} .mcms-critical-lowerline { grid-template-columns:minmax(0,1fr) 136px !important; gap:6px !important; }
09070:         html[data-mcms-tablet-active="true"] #${SCRIPT.criticalDrawerId} .mcms-critical-state-copy strong { font-size:9.7px !important; }
09071:         html[data-mcms-tablet-active="true"] #${SCRIPT.criticalDrawerId} .mcms-critical-state-copy small { font-size:8.7px !important; }
09072:         html[data-mcms-tablet-active="true"] #${SCRIPT.criticalDrawerId} .mcms-critical-unit-chip strong { font-size:14px !important; }
09073:         html[data-mcms-tablet-active="true"] #${SCRIPT.criticalDrawerId} .mcms-critical-unit-chip small { font-size:7.4px !important; }
```

### Lines 9064-9074
```text
09064:         html[data-mcms-tablet-active="true"] #${SCRIPT.criticalDrawerId} .mcms-critical-patients { min-height:24px !important; padding:4px 8px !important; }
09065:         html[data-mcms-mobile-active="true"] #${SCRIPT.criticalDrawerId} .mcms-critical-titleline { align-items:flex-start !important; }
09066:         html[data-mcms-mobile-active="true"] #${SCRIPT.criticalDrawerId} .mcms-critical-patients { min-height:20px !important; padding:3px 6px !important; }
09067:         html[data-mcms-tablet-active="true"] #${SCRIPT.criticalDrawerId} .mcms-critical-row { padding:9px !important; }
09068:         html[data-mcms-tablet-active="true"] #${SCRIPT.criticalDrawerId} .mcms-critical-name { font-size:12.8px !important; }
09069:         html[data-mcms-tablet-active="true"] #${SCRIPT.criticalDrawerId} .mcms-critical-lowerline { grid-template-columns:minmax(0,1fr) 136px !important; gap:6px !important; }
09070:         html[data-mcms-tablet-active="true"] #${SCRIPT.criticalDrawerId} .mcms-critical-state-copy strong { font-size:9.7px !important; }
09071:         html[data-mcms-tablet-active="true"] #${SCRIPT.criticalDrawerId} .mcms-critical-state-copy small { font-size:8.7px !important; }
09072:         html[data-mcms-tablet-active="true"] #${SCRIPT.criticalDrawerId} .mcms-critical-unit-chip strong { font-size:14px !important; }
09073:         html[data-mcms-tablet-active="true"] #${SCRIPT.criticalDrawerId} .mcms-critical-unit-chip small { font-size:7.4px !important; }
09074: 
```

### Lines 9065-9075
```text
09065:         html[data-mcms-mobile-active="true"] #${SCRIPT.criticalDrawerId} .mcms-critical-titleline { align-items:flex-start !important; }
09066:         html[data-mcms-mobile-active="true"] #${SCRIPT.criticalDrawerId} .mcms-critical-patients { min-height:20px !important; padding:3px 6px !important; }
09067:         html[data-mcms-tablet-active="true"] #${SCRIPT.criticalDrawerId} .mcms-critical-row { padding:9px !important; }
09068:         html[data-mcms-tablet-active="true"] #${SCRIPT.criticalDrawerId} .mcms-critical-name { font-size:12.8px !important; }
09069:         html[data-mcms-tablet-active="true"] #${SCRIPT.criticalDrawerId} .mcms-critical-lowerline { grid-template-columns:minmax(0,1fr) 136px !important; gap:6px !important; }
09070:         html[data-mcms-tablet-active="true"] #${SCRIPT.criticalDrawerId} .mcms-critical-state-copy strong { font-size:9.7px !important; }
09071:         html[data-mcms-tablet-active="true"] #${SCRIPT.criticalDrawerId} .mcms-critical-state-copy small { font-size:8.7px !important; }
09072:         html[data-mcms-tablet-active="true"] #${SCRIPT.criticalDrawerId} .mcms-critical-unit-chip strong { font-size:14px !important; }
09073:         html[data-mcms-tablet-active="true"] #${SCRIPT.criticalDrawerId} .mcms-critical-unit-chip small { font-size:7.4px !important; }
09074: 
09075:         html[data-mcms-mobile-active="true"] #${SCRIPT.criticalDrawerId} {
```

### Lines 9066-9076
```text
09066:         html[data-mcms-mobile-active="true"] #${SCRIPT.criticalDrawerId} .mcms-critical-patients { min-height:20px !important; padding:3px 6px !important; }
09067:         html[data-mcms-tablet-active="true"] #${SCRIPT.criticalDrawerId} .mcms-critical-row { padding:9px !important; }
09068:         html[data-mcms-tablet-active="true"] #${SCRIPT.criticalDrawerId} .mcms-critical-name { font-size:12.8px !important; }
09069:         html[data-mcms-tablet-active="true"] #${SCRIPT.criticalDrawerId} .mcms-critical-lowerline { grid-template-columns:minmax(0,1fr) 136px !important; gap:6px !important; }
09070:         html[data-mcms-tablet-active="true"] #${SCRIPT.criticalDrawerId} .mcms-critical-state-copy strong { font-size:9.7px !important; }
09071:         html[data-mcms-tablet-active="true"] #${SCRIPT.criticalDrawerId} .mcms-critical-state-copy small { font-size:8.7px !important; }
09072:         html[data-mcms-tablet-active="true"] #${SCRIPT.criticalDrawerId} .mcms-critical-unit-chip strong { font-size:14px !important; }
09073:         html[data-mcms-tablet-active="true"] #${SCRIPT.criticalDrawerId} .mcms-critical-unit-chip small { font-size:7.4px !important; }
09074: 
09075:         html[data-mcms-mobile-active="true"] #${SCRIPT.criticalDrawerId} {
09076:             width:calc(100vw - 8px) !important;
```

### Lines 9067-9077
```text
09067:         html[data-mcms-tablet-active="true"] #${SCRIPT.criticalDrawerId} .mcms-critical-row { padding:9px !important; }
09068:         html[data-mcms-tablet-active="true"] #${SCRIPT.criticalDrawerId} .mcms-critical-name { font-size:12.8px !important; }
09069:         html[data-mcms-tablet-active="true"] #${SCRIPT.criticalDrawerId} .mcms-critical-lowerline { grid-template-columns:minmax(0,1fr) 136px !important; gap:6px !important; }
09070:         html[data-mcms-tablet-active="true"] #${SCRIPT.criticalDrawerId} .mcms-critical-state-copy strong { font-size:9.7px !important; }
09071:         html[data-mcms-tablet-active="true"] #${SCRIPT.criticalDrawerId} .mcms-critical-state-copy small { font-size:8.7px !important; }
09072:         html[data-mcms-tablet-active="true"] #${SCRIPT.criticalDrawerId} .mcms-critical-unit-chip strong { font-size:14px !important; }
09073:         html[data-mcms-tablet-active="true"] #${SCRIPT.criticalDrawerId} .mcms-critical-unit-chip small { font-size:7.4px !important; }
09074: 
09075:         html[data-mcms-mobile-active="true"] #${SCRIPT.criticalDrawerId} {
09076:             width:calc(100vw - 8px) !important;
09077:             max-width:calc(100vw - 8px) !important;
```

### Lines 9068-9078
```text
09068:         html[data-mcms-tablet-active="true"] #${SCRIPT.criticalDrawerId} .mcms-critical-name { font-size:12.8px !important; }
09069:         html[data-mcms-tablet-active="true"] #${SCRIPT.criticalDrawerId} .mcms-critical-lowerline { grid-template-columns:minmax(0,1fr) 136px !important; gap:6px !important; }
09070:         html[data-mcms-tablet-active="true"] #${SCRIPT.criticalDrawerId} .mcms-critical-state-copy strong { font-size:9.7px !important; }
09071:         html[data-mcms-tablet-active="true"] #${SCRIPT.criticalDrawerId} .mcms-critical-state-copy small { font-size:8.7px !important; }
09072:         html[data-mcms-tablet-active="true"] #${SCRIPT.criticalDrawerId} .mcms-critical-unit-chip strong { font-size:14px !important; }
09073:         html[data-mcms-tablet-active="true"] #${SCRIPT.criticalDrawerId} .mcms-critical-unit-chip small { font-size:7.4px !important; }
09074: 
09075:         html[data-mcms-mobile-active="true"] #${SCRIPT.criticalDrawerId} {
09076:             width:calc(100vw - 8px) !important;
09077:             max-width:calc(100vw - 8px) !important;
09078:             max-height:min(86dvh,calc(100dvh - env(safe-area-inset-top) - 8px)) !important;
```

### Lines 9080-9090
```text
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
```

### Lines 9082-9092
```text
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
```

### Lines 9085-9095
```text
09085:         html[data-mcms-mobile-active="true"] #${SCRIPT.criticalDrawerId} .mcms-critical-refreshed { font-size:7.5px !important; white-space:normal !important; }
09086:         html[data-mcms-mobile-active="true"] #${SCRIPT.criticalDrawerId} .mcms-critical-topline { align-items:flex-start !important; }
09087:         html[data-mcms-mobile-active="true"] #${SCRIPT.criticalDrawerId} .mcms-critical-top-actions { gap:3px !important; flex-wrap:wrap !important; }
09088:         html[data-mcms-mobile-active="true"] #${SCRIPT.criticalDrawerId} .mcms-critical-zoom,
09089:         html[data-mcms-mobile-active="true"] #${SCRIPT.criticalDrawerId} .mcms-critical-open { min-width:50px !important; height:30px !important; padding:0 6px !important; font-size:8px !important; }
09090:         html[data-mcms-mobile-active="true"] #${SCRIPT.criticalDrawerId} .mcms-critical-values-grid { grid-template-columns:1fr !important; }
09091:         html[data-mcms-mobile-active="true"] #${SCRIPT.criticalDrawerId} .mcms-critical-value-card {
09092:             display:grid !important;
09093:             grid-template-columns:minmax(0,1fr) auto !important;
09094:             align-items:center !important;
09095:             gap:8px !important;
```

### Lines 9088-9098
```text
09088:         html[data-mcms-mobile-active="true"] #${SCRIPT.criticalDrawerId} .mcms-critical-zoom,
09089:         html[data-mcms-mobile-active="true"] #${SCRIPT.criticalDrawerId} .mcms-critical-open { min-width:50px !important; height:30px !important; padding:0 6px !important; font-size:8px !important; }
09090:         html[data-mcms-mobile-active="true"] #${SCRIPT.criticalDrawerId} .mcms-critical-values-grid { grid-template-columns:1fr !important; }
09091:         html[data-mcms-mobile-active="true"] #${SCRIPT.criticalDrawerId} .mcms-critical-value-card {
09092:             display:grid !important;
09093:             grid-template-columns:minmax(0,1fr) auto !important;
09094:             align-items:center !important;
09095:             gap:8px !important;
09096:             padding:5px 7px !important;
09097:             text-align:left !important;
09098:         }
```

### Lines 9095-9105
```text
09095:             gap:8px !important;
09096:             padding:5px 7px !important;
09097:             text-align:left !important;
09098:         }
09099:         html[data-mcms-mobile-active="true"] #${SCRIPT.criticalDrawerId} .mcms-critical-value-card strong { margin-top:0 !important; font-size:10.5px !important; }
09100:         html[data-mcms-tablet-active="true"] #${SCRIPT.criticalDrawerId} .mcms-critical-age-filters { max-width:330px !important; grid-template-columns:auto repeat(4,minmax(42px,1fr)) !important; }
09101:         html[data-mcms-tablet-active="true"] #${SCRIPT.criticalDrawerId} .mcms-critical-age-filter { min-height:29px !important; padding:4px 7px !important; }
09102:         html[data-mcms-tablet-active="true"] #${SCRIPT.criticalDrawerId} .mcms-critical-age-filter span { font-size:8px !important; }
09103:         html[data-mcms-tablet-active="true"] #${SCRIPT.criticalDrawerId} .mcms-critical-type-filter { min-height:31px !important; padding:5px 8px !important; }
09104:         html[data-mcms-tablet-active="true"] #${SCRIPT.criticalDrawerId} .mcms-critical-type-filter span { font-size:7.8px !important; }
09105:         html[data-mcms-tablet-active="true"] #${SCRIPT.criticalDrawerId} .mcms-critical-type-filter strong { font-size:12px !important; }
```

### Lines 9096-9106
```text
09096:             padding:5px 7px !important;
09097:             text-align:left !important;
09098:         }
09099:         html[data-mcms-mobile-active="true"] #${SCRIPT.criticalDrawerId} .mcms-critical-value-card strong { margin-top:0 !important; font-size:10.5px !important; }
09100:         html[data-mcms-tablet-active="true"] #${SCRIPT.criticalDrawerId} .mcms-critical-age-filters { max-width:330px !important; grid-template-columns:auto repeat(4,minmax(42px,1fr)) !important; }
09101:         html[data-mcms-tablet-active="true"] #${SCRIPT.criticalDrawerId} .mcms-critical-age-filter { min-height:29px !important; padding:4px 7px !important; }
09102:         html[data-mcms-tablet-active="true"] #${SCRIPT.criticalDrawerId} .mcms-critical-age-filter span { font-size:8px !important; }
09103:         html[data-mcms-tablet-active="true"] #${SCRIPT.criticalDrawerId} .mcms-critical-type-filter { min-height:31px !important; padding:5px 8px !important; }
09104:         html[data-mcms-tablet-active="true"] #${SCRIPT.criticalDrawerId} .mcms-critical-type-filter span { font-size:7.8px !important; }
09105:         html[data-mcms-tablet-active="true"] #${SCRIPT.criticalDrawerId} .mcms-critical-type-filter strong { font-size:12px !important; }
09106:         html[data-mcms-mobile-active="true"] #${SCRIPT.criticalDrawerId} .mcms-critical-age-filters { max-width:none !important; grid-template-columns:repeat(4,minmax(0,1fr)) !important; gap:3px !important; }
```

### Lines 9097-9107
```text
09097:             text-align:left !important;
09098:         }
09099:         html[data-mcms-mobile-active="true"] #${SCRIPT.criticalDrawerId} .mcms-critical-value-card strong { margin-top:0 !important; font-size:10.5px !important; }
09100:         html[data-mcms-tablet-active="true"] #${SCRIPT.criticalDrawerId} .mcms-critical-age-filters { max-width:330px !important; grid-template-columns:auto repeat(4,minmax(42px,1fr)) !important; }
09101:         html[data-mcms-tablet-active="true"] #${SCRIPT.criticalDrawerId} .mcms-critical-age-filter { min-height:29px !important; padding:4px 7px !important; }
09102:         html[data-mcms-tablet-active="true"] #${SCRIPT.criticalDrawerId} .mcms-critical-age-filter span { font-size:8px !important; }
09103:         html[data-mcms-tablet-active="true"] #${SCRIPT.criticalDrawerId} .mcms-critical-type-filter { min-height:31px !important; padding:5px 8px !important; }
09104:         html[data-mcms-tablet-active="true"] #${SCRIPT.criticalDrawerId} .mcms-critical-type-filter span { font-size:7.8px !important; }
09105:         html[data-mcms-tablet-active="true"] #${SCRIPT.criticalDrawerId} .mcms-critical-type-filter strong { font-size:12px !important; }
09106:         html[data-mcms-mobile-active="true"] #${SCRIPT.criticalDrawerId} .mcms-critical-age-filters { max-width:none !important; grid-template-columns:repeat(4,minmax(0,1fr)) !important; gap:3px !important; }
09107:         html[data-mcms-mobile-active="true"] #${SCRIPT.criticalDrawerId} .mcms-critical-age-label { grid-column:1 / -1 !important; min-height:12px !important; }
```

### Lines 9098-9108
```text
09098:         }
09099:         html[data-mcms-mobile-active="true"] #${SCRIPT.criticalDrawerId} .mcms-critical-value-card strong { margin-top:0 !important; font-size:10.5px !important; }
09100:         html[data-mcms-tablet-active="true"] #${SCRIPT.criticalDrawerId} .mcms-critical-age-filters { max-width:330px !important; grid-template-columns:auto repeat(4,minmax(42px,1fr)) !important; }
09101:         html[data-mcms-tablet-active="true"] #${SCRIPT.criticalDrawerId} .mcms-critical-age-filter { min-height:29px !important; padding:4px 7px !important; }
09102:         html[data-mcms-tablet-active="true"] #${SCRIPT.criticalDrawerId} .mcms-critical-age-filter span { font-size:8px !important; }
09103:         html[data-mcms-tablet-active="true"] #${SCRIPT.criticalDrawerId} .mcms-critical-type-filter { min-height:31px !important; padding:5px 8px !important; }
09104:         html[data-mcms-tablet-active="true"] #${SCRIPT.criticalDrawerId} .mcms-critical-type-filter span { font-size:7.8px !important; }
09105:         html[data-mcms-tablet-active="true"] #${SCRIPT.criticalDrawerId} .mcms-critical-type-filter strong { font-size:12px !important; }
09106:         html[data-mcms-mobile-active="true"] #${SCRIPT.criticalDrawerId} .mcms-critical-age-filters { max-width:none !important; grid-template-columns:repeat(4,minmax(0,1fr)) !important; gap:3px !important; }
09107:         html[data-mcms-mobile-active="true"] #${SCRIPT.criticalDrawerId} .mcms-critical-age-label { grid-column:1 / -1 !important; min-height:12px !important; }
09108:         html[data-mcms-mobile-active="true"] #${SCRIPT.criticalDrawerId} .mcms-critical-age-filter { min-height:28px !important; padding:4px 5px !important; }
```

### Lines 9099-9109
```text
09099:         html[data-mcms-mobile-active="true"] #${SCRIPT.criticalDrawerId} .mcms-critical-value-card strong { margin-top:0 !important; font-size:10.5px !important; }
09100:         html[data-mcms-tablet-active="true"] #${SCRIPT.criticalDrawerId} .mcms-critical-age-filters { max-width:330px !important; grid-template-columns:auto repeat(4,minmax(42px,1fr)) !important; }
09101:         html[data-mcms-tablet-active="true"] #${SCRIPT.criticalDrawerId} .mcms-critical-age-filter { min-height:29px !important; padding:4px 7px !important; }
09102:         html[data-mcms-tablet-active="true"] #${SCRIPT.criticalDrawerId} .mcms-critical-age-filter span { font-size:8px !important; }
09103:         html[data-mcms-tablet-active="true"] #${SCRIPT.criticalDrawerId} .mcms-critical-type-filter { min-height:31px !important; padding:5px 8px !important; }
09104:         html[data-mcms-tablet-active="true"] #${SCRIPT.criticalDrawerId} .mcms-critical-type-filter span { font-size:7.8px !important; }
09105:         html[data-mcms-tablet-active="true"] #${SCRIPT.criticalDrawerId} .mcms-critical-type-filter strong { font-size:12px !important; }
09106:         html[data-mcms-mobile-active="true"] #${SCRIPT.criticalDrawerId} .mcms-critical-age-filters { max-width:none !important; grid-template-columns:repeat(4,minmax(0,1fr)) !important; gap:3px !important; }
09107:         html[data-mcms-mobile-active="true"] #${SCRIPT.criticalDrawerId} .mcms-critical-age-label { grid-column:1 / -1 !important; min-height:12px !important; }
09108:         html[data-mcms-mobile-active="true"] #${SCRIPT.criticalDrawerId} .mcms-critical-age-filter { min-height:28px !important; padding:4px 5px !important; }
09109:         html[data-mcms-mobile-active="true"] #${SCRIPT.criticalDrawerId} .mcms-critical-age-filter span { font-size:7.4px !important; }
```

### Lines 9100-9110
```text
09100:         html[data-mcms-tablet-active="true"] #${SCRIPT.criticalDrawerId} .mcms-critical-age-filters { max-width:330px !important; grid-template-columns:auto repeat(4,minmax(42px,1fr)) !important; }
09101:         html[data-mcms-tablet-active="true"] #${SCRIPT.criticalDrawerId} .mcms-critical-age-filter { min-height:29px !important; padding:4px 7px !important; }
09102:         html[data-mcms-tablet-active="true"] #${SCRIPT.criticalDrawerId} .mcms-critical-age-filter span { font-size:8px !important; }
09103:         html[data-mcms-tablet-active="true"] #${SCRIPT.criticalDrawerId} .mcms-critical-type-filter { min-height:31px !important; padding:5px 8px !important; }
09104:         html[data-mcms-tablet-active="true"] #${SCRIPT.criticalDrawerId} .mcms-critical-type-filter span { font-size:7.8px !important; }
09105:         html[data-mcms-tablet-active="true"] #${SCRIPT.criticalDrawerId} .mcms-critical-type-filter strong { font-size:12px !important; }
09106:         html[data-mcms-mobile-active="true"] #${SCRIPT.criticalDrawerId} .mcms-critical-age-filters { max-width:none !important; grid-template-columns:repeat(4,minmax(0,1fr)) !important; gap:3px !important; }
09107:         html[data-mcms-mobile-active="true"] #${SCRIPT.criticalDrawerId} .mcms-critical-age-label { grid-column:1 / -1 !important; min-height:12px !important; }
09108:         html[data-mcms-mobile-active="true"] #${SCRIPT.criticalDrawerId} .mcms-critical-age-filter { min-height:28px !important; padding:4px 5px !important; }
09109:         html[data-mcms-mobile-active="true"] #${SCRIPT.criticalDrawerId} .mcms-critical-age-filter span { font-size:7.4px !important; }
09110:         html[data-mcms-mobile-active="true"] #${SCRIPT.criticalDrawerId} .mcms-critical-type-filters { grid-template-columns:repeat(3,minmax(0,1fr)) !important; gap:3px !important; }
```

### Lines 9101-9111
```text
09101:         html[data-mcms-tablet-active="true"] #${SCRIPT.criticalDrawerId} .mcms-critical-age-filter { min-height:29px !important; padding:4px 7px !important; }
09102:         html[data-mcms-tablet-active="true"] #${SCRIPT.criticalDrawerId} .mcms-critical-age-filter span { font-size:8px !important; }
09103:         html[data-mcms-tablet-active="true"] #${SCRIPT.criticalDrawerId} .mcms-critical-type-filter { min-height:31px !important; padding:5px 8px !important; }
09104:         html[data-mcms-tablet-active="true"] #${SCRIPT.criticalDrawerId} .mcms-critical-type-filter span { font-size:7.8px !important; }
09105:         html[data-mcms-tablet-active="true"] #${SCRIPT.criticalDrawerId} .mcms-critical-type-filter strong { font-size:12px !important; }
09106:         html[data-mcms-mobile-active="true"] #${SCRIPT.criticalDrawerId} .mcms-critical-age-filters { max-width:none !important; grid-template-columns:repeat(4,minmax(0,1fr)) !important; gap:3px !important; }
09107:         html[data-mcms-mobile-active="true"] #${SCRIPT.criticalDrawerId} .mcms-critical-age-label { grid-column:1 / -1 !important; min-height:12px !important; }
09108:         html[data-mcms-mobile-active="true"] #${SCRIPT.criticalDrawerId} .mcms-critical-age-filter { min-height:28px !important; padding:4px 5px !important; }
09109:         html[data-mcms-mobile-active="true"] #${SCRIPT.criticalDrawerId} .mcms-critical-age-filter span { font-size:7.4px !important; }
09110:         html[data-mcms-mobile-active="true"] #${SCRIPT.criticalDrawerId} .mcms-critical-type-filters { grid-template-columns:repeat(3,minmax(0,1fr)) !important; gap:3px !important; }
09111:         html[data-mcms-mobile-active="true"] #${SCRIPT.criticalDrawerId} .mcms-critical-type-label { grid-column:1 / -1 !important; min-height:14px !important; }
```

### Lines 9105-9115
```text
09105:         html[data-mcms-tablet-active="true"] #${SCRIPT.criticalDrawerId} .mcms-critical-type-filter strong { font-size:12px !important; }
09106:         html[data-mcms-mobile-active="true"] #${SCRIPT.criticalDrawerId} .mcms-critical-age-filters { max-width:none !important; grid-template-columns:repeat(4,minmax(0,1fr)) !important; gap:3px !important; }
09107:         html[data-mcms-mobile-active="true"] #${SCRIPT.criticalDrawerId} .mcms-critical-age-label { grid-column:1 / -1 !important; min-height:12px !important; }
09108:         html[data-mcms-mobile-active="true"] #${SCRIPT.criticalDrawerId} .mcms-critical-age-filter { min-height:28px !important; padding:4px 5px !important; }
09109:         html[data-mcms-mobile-active="true"] #${SCRIPT.criticalDrawerId} .mcms-critical-age-filter span { font-size:7.4px !important; }
09110:         html[data-mcms-mobile-active="true"] #${SCRIPT.criticalDrawerId} .mcms-critical-type-filters { grid-template-columns:repeat(3,minmax(0,1fr)) !important; gap:3px !important; }
09111:         html[data-mcms-mobile-active="true"] #${SCRIPT.criticalDrawerId} .mcms-critical-type-label { grid-column:1 / -1 !important; min-height:14px !important; }
09112:         html[data-mcms-mobile-active="true"] #${SCRIPT.criticalDrawerId} .mcms-critical-type-filter { min-height:29px !important; padding:4px 5px !important; }
09113:         html[data-mcms-mobile-active="true"] #${SCRIPT.criticalDrawerId} .mcms-critical-type-filter span { font-size:6.8px !important; }
09114:         html[data-mcms-mobile-active="true"] #${SCRIPT.criticalDrawerId} .mcms-critical-summary { grid-template-columns:repeat(2,minmax(0,1fr)) !important; }
09115:         html[data-mcms-mobile-active="true"] #${SCRIPT.criticalDrawerId} .mcms-critical-summary-card span { font-size:7px !important; }
```

### Lines 9109-9119
```text
09109:         html[data-mcms-mobile-active="true"] #${SCRIPT.criticalDrawerId} .mcms-critical-age-filter span { font-size:7.4px !important; }
09110:         html[data-mcms-mobile-active="true"] #${SCRIPT.criticalDrawerId} .mcms-critical-type-filters { grid-template-columns:repeat(3,minmax(0,1fr)) !important; gap:3px !important; }
09111:         html[data-mcms-mobile-active="true"] #${SCRIPT.criticalDrawerId} .mcms-critical-type-label { grid-column:1 / -1 !important; min-height:14px !important; }
09112:         html[data-mcms-mobile-active="true"] #${SCRIPT.criticalDrawerId} .mcms-critical-type-filter { min-height:29px !important; padding:4px 5px !important; }
09113:         html[data-mcms-mobile-active="true"] #${SCRIPT.criticalDrawerId} .mcms-critical-type-filter span { font-size:6.8px !important; }
09114:         html[data-mcms-mobile-active="true"] #${SCRIPT.criticalDrawerId} .mcms-critical-summary { grid-template-columns:repeat(2,minmax(0,1fr)) !important; }
09115:         html[data-mcms-mobile-active="true"] #${SCRIPT.criticalDrawerId} .mcms-critical-summary-card span { font-size:7px !important; }
09116:         html[data-mcms-mobile-active="true"] #${SCRIPT.criticalDrawerId} .mcms-summary-clearing { grid-column:1 / -1 !important; }
09117:         html[data-mcms-mobile-active="true"] #${SCRIPT.criticalDrawerId} .mcms-critical-row { padding:8px !important; }
09118:         html[data-mcms-mobile-active="true"] #${SCRIPT.criticalDrawerId} .mcms-critical-name { font-size:11.5px !important; }
09119:         html[data-mcms-mobile-active="true"] #${SCRIPT.criticalDrawerId} .mcms-critical-lowerline { grid-template-columns:minmax(0,1fr) 106px !important; gap:4px !important; }
```

### Lines 9114-9124
```text
09114:         html[data-mcms-mobile-active="true"] #${SCRIPT.criticalDrawerId} .mcms-critical-summary { grid-template-columns:repeat(2,minmax(0,1fr)) !important; }
09115:         html[data-mcms-mobile-active="true"] #${SCRIPT.criticalDrawerId} .mcms-critical-summary-card span { font-size:7px !important; }
09116:         html[data-mcms-mobile-active="true"] #${SCRIPT.criticalDrawerId} .mcms-summary-clearing { grid-column:1 / -1 !important; }
09117:         html[data-mcms-mobile-active="true"] #${SCRIPT.criticalDrawerId} .mcms-critical-row { padding:8px !important; }
09118:         html[data-mcms-mobile-active="true"] #${SCRIPT.criticalDrawerId} .mcms-critical-name { font-size:11.5px !important; }
09119:         html[data-mcms-mobile-active="true"] #${SCRIPT.criticalDrawerId} .mcms-critical-lowerline { grid-template-columns:minmax(0,1fr) 106px !important; gap:4px !important; }
09120:         html[data-mcms-mobile-active="true"] #${SCRIPT.criticalDrawerId} .mcms-critical-state-copy strong { font-size:8.5px !important; }
09121:         html[data-mcms-mobile-active="true"] #${SCRIPT.criticalDrawerId} .mcms-critical-state-copy small { font-size:7.5px !important; }
09122: 
09123:         /* v3.16.1: compact Mission Value rail inside the Mission Age Watch header. */
09124:         #${SCRIPT.criticalDrawerId} .mcms-drawer-head {
```

### Lines 9120-9130
```text
09120:         html[data-mcms-mobile-active="true"] #${SCRIPT.criticalDrawerId} .mcms-critical-state-copy strong { font-size:8.5px !important; }
09121:         html[data-mcms-mobile-active="true"] #${SCRIPT.criticalDrawerId} .mcms-critical-state-copy small { font-size:7.5px !important; }
09122: 
09123:         /* v3.16.1: compact Mission Value rail inside the Mission Age Watch header. */
09124:         #${SCRIPT.criticalDrawerId} .mcms-drawer-head {
09125:             grid-template-columns:minmax(0,1fr) auto !important;
09126:             grid-template-rows:auto auto !important;
09127:             column-gap:8px !important;
09128:             row-gap:3px !important;
09129:         }
09130:         #${SCRIPT.criticalDrawerId} .mcms-drawer-heading { grid-column:1 !important; grid-row:1 !important; }
```

### Lines 9131-9141
```text
09131:         #${SCRIPT.criticalDrawerId} .mcms-drawer-actions { grid-column:2 !important; grid-row:1 !important; }
09132:         #${SCRIPT.criticalDrawerId} .mcms-critical-values {
09133:             grid-column:1 / -1 !important;
09134:             grid-row:2 !important;
09135:             display:grid !important;
09136:             grid-template-columns:auto minmax(0,1fr) auto !important;
09137:             align-items:stretch !important;
09138:             gap:4px !important;
09139:             margin:1px 0 0 !important;
09140:             padding:5px 0 0 !important;
09141:             border:0 !important;
```

### Lines 9166-9176
```text
09166:             text-transform:uppercase !important;
09167:         }
09168:         #${SCRIPT.criticalDrawerId} .mcms-critical-values-label span { margin-top:2px !important; color:#8fb6ce !important; }
09169:         #${SCRIPT.criticalDrawerId} .mcms-critical-values-grid {
09170:             display:grid !important;
09171:             grid-template-columns:repeat(3,minmax(0,1fr)) !important;
09172:             gap:3px !important;
09173:             min-width:0 !important;
09174:         }
09175:         #${SCRIPT.criticalDrawerId} .mcms-critical-value-card {
09176:             display:flex !important;
```

### Lines 9189-9199
```text
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
```

### Lines 9198-9208
```text
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
```

### Lines 9199-9209
```text
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
```

### Lines 9223-9233
```text
09223:             outline:2px solid currentColor !important;
09224:             outline-offset:1px !important;
09225:         }
09226:         #${SCRIPT.criticalDrawerId} .mcms-critical-summary { margin-top:5px !important; }
09227: 
09228:         html[data-mcms-tablet-active="true"] #${SCRIPT.criticalDrawerId} .mcms-critical-values {
09229:             padding:5px 0 0 !important;
09230:         }
09231:         html[data-mcms-tablet-active="true"] #${SCRIPT.criticalDrawerId} .mcms-critical-value-card {
09232:             min-height:28px !important;
09233:             padding:3px 5px !important;
```

### Lines 9226-9236
```text
09226:         #${SCRIPT.criticalDrawerId} .mcms-critical-summary { margin-top:5px !important; }
09227: 
09228:         html[data-mcms-tablet-active="true"] #${SCRIPT.criticalDrawerId} .mcms-critical-values {
09229:             padding:5px 0 0 !important;
09230:         }
09231:         html[data-mcms-tablet-active="true"] #${SCRIPT.criticalDrawerId} .mcms-critical-value-card {
09232:             min-height:28px !important;
09233:             padding:3px 5px !important;
09234:         }
09235:         html[data-mcms-tablet-active="true"] #${SCRIPT.criticalDrawerId} .mcms-critical-value-card span { font-size:6.3px !important; }
09236:         html[data-mcms-tablet-active="true"] #${SCRIPT.criticalDrawerId} .mcms-critical-value-card strong { font-size:10.2px !important; }
```

### Lines 9230-9240
```text
09230:         }
09231:         html[data-mcms-tablet-active="true"] #${SCRIPT.criticalDrawerId} .mcms-critical-value-card {
09232:             min-height:28px !important;
09233:             padding:3px 5px !important;
09234:         }
09235:         html[data-mcms-tablet-active="true"] #${SCRIPT.criticalDrawerId} .mcms-critical-value-card span { font-size:6.3px !important; }
09236:         html[data-mcms-tablet-active="true"] #${SCRIPT.criticalDrawerId} .mcms-critical-value-card strong { font-size:10.2px !important; }
09237:         html[data-mcms-tablet-active="true"] #${SCRIPT.criticalDrawerId} .mcms-critical-values-label strong,
09238:         html[data-mcms-tablet-active="true"] #${SCRIPT.criticalDrawerId} .mcms-critical-values-label span { font-size:6.2px !important; }
09239:         html[data-mcms-tablet-active="true"] #${SCRIPT.criticalDrawerId} .mcms-critical-values-clear { min-height:28px !important; font-size:6.2px !important; }
09240: 
```

### Lines 9231-9241
```text
09231:         html[data-mcms-tablet-active="true"] #${SCRIPT.criticalDrawerId} .mcms-critical-value-card {
09232:             min-height:28px !important;
09233:             padding:3px 5px !important;
09234:         }
09235:         html[data-mcms-tablet-active="true"] #${SCRIPT.criticalDrawerId} .mcms-critical-value-card span { font-size:6.3px !important; }
09236:         html[data-mcms-tablet-active="true"] #${SCRIPT.criticalDrawerId} .mcms-critical-value-card strong { font-size:10.2px !important; }
09237:         html[data-mcms-tablet-active="true"] #${SCRIPT.criticalDrawerId} .mcms-critical-values-label strong,
09238:         html[data-mcms-tablet-active="true"] #${SCRIPT.criticalDrawerId} .mcms-critical-values-label span { font-size:6.2px !important; }
09239:         html[data-mcms-tablet-active="true"] #${SCRIPT.criticalDrawerId} .mcms-critical-values-clear { min-height:28px !important; font-size:6.2px !important; }
09240: 
09241:         html[data-mcms-mobile-active="true"] #${SCRIPT.criticalDrawerId} .mcms-critical-values {
```

### Lines 9232-9242
```text
09232:             min-height:28px !important;
09233:             padding:3px 5px !important;
09234:         }
09235:         html[data-mcms-tablet-active="true"] #${SCRIPT.criticalDrawerId} .mcms-critical-value-card span { font-size:6.3px !important; }
09236:         html[data-mcms-tablet-active="true"] #${SCRIPT.criticalDrawerId} .mcms-critical-value-card strong { font-size:10.2px !important; }
09237:         html[data-mcms-tablet-active="true"] #${SCRIPT.criticalDrawerId} .mcms-critical-values-label strong,
09238:         html[data-mcms-tablet-active="true"] #${SCRIPT.criticalDrawerId} .mcms-critical-values-label span { font-size:6.2px !important; }
09239:         html[data-mcms-tablet-active="true"] #${SCRIPT.criticalDrawerId} .mcms-critical-values-clear { min-height:28px !important; font-size:6.2px !important; }
09240: 
09241:         html[data-mcms-mobile-active="true"] #${SCRIPT.criticalDrawerId} .mcms-critical-values {
09242:             grid-template-columns:34px minmax(0,1fr) auto !important;
```

### Lines 9233-9243
```text
09233:             padding:3px 5px !important;
09234:         }
09235:         html[data-mcms-tablet-active="true"] #${SCRIPT.criticalDrawerId} .mcms-critical-value-card span { font-size:6.3px !important; }
09236:         html[data-mcms-tablet-active="true"] #${SCRIPT.criticalDrawerId} .mcms-critical-value-card strong { font-size:10.2px !important; }
09237:         html[data-mcms-tablet-active="true"] #${SCRIPT.criticalDrawerId} .mcms-critical-values-label strong,
09238:         html[data-mcms-tablet-active="true"] #${SCRIPT.criticalDrawerId} .mcms-critical-values-label span { font-size:6.2px !important; }
09239:         html[data-mcms-tablet-active="true"] #${SCRIPT.criticalDrawerId} .mcms-critical-values-clear { min-height:28px !important; font-size:6.2px !important; }
09240: 
09241:         html[data-mcms-mobile-active="true"] #${SCRIPT.criticalDrawerId} .mcms-critical-values {
09242:             grid-template-columns:34px minmax(0,1fr) auto !important;
09243:             gap:3px !important;
```

### Lines 9234-9244
```text
09234:         }
09235:         html[data-mcms-tablet-active="true"] #${SCRIPT.criticalDrawerId} .mcms-critical-value-card span { font-size:6.3px !important; }
09236:         html[data-mcms-tablet-active="true"] #${SCRIPT.criticalDrawerId} .mcms-critical-value-card strong { font-size:10.2px !important; }
09237:         html[data-mcms-tablet-active="true"] #${SCRIPT.criticalDrawerId} .mcms-critical-values-label strong,
09238:         html[data-mcms-tablet-active="true"] #${SCRIPT.criticalDrawerId} .mcms-critical-values-label span { font-size:6.2px !important; }
09239:         html[data-mcms-tablet-active="true"] #${SCRIPT.criticalDrawerId} .mcms-critical-values-clear { min-height:28px !important; font-size:6.2px !important; }
09240: 
09241:         html[data-mcms-mobile-active="true"] #${SCRIPT.criticalDrawerId} .mcms-critical-values {
09242:             grid-template-columns:34px minmax(0,1fr) auto !important;
09243:             gap:3px !important;
09244:             margin-top:1px !important;
```

### Lines 9237-9247
```text
09237:         html[data-mcms-tablet-active="true"] #${SCRIPT.criticalDrawerId} .mcms-critical-values-label strong,
09238:         html[data-mcms-tablet-active="true"] #${SCRIPT.criticalDrawerId} .mcms-critical-values-label span { font-size:6.2px !important; }
09239:         html[data-mcms-tablet-active="true"] #${SCRIPT.criticalDrawerId} .mcms-critical-values-clear { min-height:28px !important; font-size:6.2px !important; }
09240: 
09241:         html[data-mcms-mobile-active="true"] #${SCRIPT.criticalDrawerId} .mcms-critical-values {
09242:             grid-template-columns:34px minmax(0,1fr) auto !important;
09243:             gap:3px !important;
09244:             margin-top:1px !important;
09245:             padding:4px 0 0 !important;
09246:         }
09247:         html[data-mcms-mobile-active="true"] #${SCRIPT.criticalDrawerId} .mcms-critical-values-grid {
```

### Lines 9243-9253
```text
09243:             gap:3px !important;
09244:             margin-top:1px !important;
09245:             padding:4px 0 0 !important;
09246:         }
09247:         html[data-mcms-mobile-active="true"] #${SCRIPT.criticalDrawerId} .mcms-critical-values-grid {
09248:             grid-template-columns:repeat(3,minmax(0,1fr)) !important;
09249:             gap:2px !important;
09250:         }
09251:         html[data-mcms-mobile-active="true"] #${SCRIPT.criticalDrawerId} .mcms-critical-value-card {
09252:             display:flex !important;
09253:             min-height:24px !important;
```

### Lines 9249-9259
```text
09249:             gap:2px !important;
09250:         }
09251:         html[data-mcms-mobile-active="true"] #${SCRIPT.criticalDrawerId} .mcms-critical-value-card {
09252:             display:flex !important;
09253:             min-height:24px !important;
09254:             grid-template-columns:none !important;
09255:             gap:1px !important;
09256:             padding:3px 2px !important;
09257:             text-align:center !important;
09258:         }
09259:         html[data-mcms-mobile-active="true"] #${SCRIPT.criticalDrawerId} .mcms-critical-value-card span { font-size:5.1px !important; }
```

### Lines 9282-9292
```text
09282:         }
09283:         @keyframes mcms-critical-docked-enter {
09284:             from { opacity:0; clip-path:inset(0 0 0 12px); }
09285:             to { opacity:1; clip-path:inset(0 0 0 0); }
09286:         }
09287:         html[data-mcms-tablet-active="true"] #${SCRIPT.criticalDrawerId}.mcms-sidebar-docked {
09288:             left:var(--mcms-critical-dock-left) !important;
09289:             right:auto !important;
09290:             top:var(--mcms-critical-dock-top) !important;
09291:             bottom:auto !important;
09292:             width:var(--mcms-critical-dock-width) !important;
```

### Lines 9367-9377
```text
09367:         html[data-mcms-ui-theme="fallout4"] #mcms-alliance-buildings-map-notice button { border-color:#8cff66 !important; background:#284f23 !important; color:#eaffdf !important; }
09368:         html[data-mcms-ui-theme="umbrella"] #mcms-alliance-buildings-map-notice { border-color:#d82632 !important; border-left-color:#d82632 !important; background:#17191d !important; color:#fff !important; }
09369:         html[data-mcms-ui-theme="umbrella"] #mcms-alliance-buildings-map-notice button { border-color:#f05c65 !important; background:#b1121c !important; color:#fff !important; }
09370:         html[data-mcms-ui-theme="factorio"] #mcms-alliance-buildings-map-notice { border-color:#f6922d !important; border-left-color:#f6922d !important; background:#292a25 !important; color:#f7ead2 !important; }
09371:         html[data-mcms-ui-theme="factorio"] #mcms-alliance-buildings-map-notice button { border-color:#f9bd75 !important; background:#bd5f13 !important; color:#fff4df !important; }
09372:         @media (max-width:700px) {
09373:             #mcms-alliance-buildings-map-notice { align-items:stretch !important; flex-direction:column !important; }
09374:             #mcms-alliance-buildings-map-notice button { width:100% !important; min-height:40px !important; }
09375:         }
09376: 
09377: 
```

### Lines 9447-9457
```text
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
```

### Lines 9515-9525
```text
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
```

### Lines 9752-9762
```text
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
```

### Lines 9796-9806
```text
09796:         html[data-mcms-ui-theme] #${SCRIPT.criticalDrawerId} .mcms-critical-type-badge.mcms-type-alliance {
09797:             border-color:rgba(79,174,255,.90) !important;
09798:             color:#8ed1ff !important;
09799:         }
09800: 
09801:         @media (max-width:760px) {
09802:             html[data-mcms-ui-theme="fallout4"] #${SCRIPT.majorIncidentFeedId} .mcms-incident-feed-label::after { display:none !important; }
09803:             #${SCRIPT.majorIncidentFeedId} .mcms-incident-feed-label { padding:0 7px !important; font-size:7.5px !important; letter-spacing:.4px !important; }
09804:             #${SCRIPT.majorIncidentFeedId} .mcms-incident-feed-item { gap:5px !important; padding:0 10px !important; }
09805:             #${SCRIPT.majorIncidentFeedId} .mcms-incident-name { font-size:10px !important; }
09806:             #${SCRIPT.majorIncidentFeedId} .mcms-incident-postcode { font-size:9px !important; }
```

### Lines 9809-9819
```text
09809: 
09810: 
09811:         /* v3.19.0 Mission Age Watch expansion, location intelligence and distance ordering. */
09812:         #${SCRIPT.criticalDrawerId} .mcms-drawer-expand {
09813:             display:inline-grid !important;
09814:             grid-template-columns:auto auto !important;
09815:             place-items:center !important;
09816:             gap:3px !important;
09817:             min-width:58px !important;
09818:             height:31px !important;
09819:             padding:0 6px !important;
```

### Lines 9858-9868
```text
09858:             scrollbar-width:thin !important;
09859:             padding-right:2px !important;
09860:         }
09861:         #${SCRIPT.criticalDrawerId} .mcms-critical-sort-controls {
09862:             display:grid !important;
09863:             grid-template-columns:auto repeat(3,minmax(42px,1fr)) !important;
09864:             align-items:stretch !important;
09865:             gap:3px !important;
09866:             max-width:278px !important;
09867:             margin-top:4px !important;
09868:         }
```

### Lines 9920-9930
```text
09920:         #${SCRIPT.criticalDrawerId} .mcms-critical-location {
09921:             display:inline-flex !important;
09922:             min-width:0 !important;
09923:             align-items:center !important;
09924:             gap:3px !important;
09925:             flex-wrap:wrap !important;
09926:         }
09927:         #${SCRIPT.criticalDrawerId} .mcms-critical-city,
09928:         #${SCRIPT.criticalDrawerId} .mcms-critical-postcode,
09929:         #${SCRIPT.criticalDrawerId} .mcms-critical-distance {
09930:             display:inline-flex !important;
```

### Lines 9937-9947
```text
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
```

### Lines 9942-9952
```text
09942:             white-space:nowrap !important;
09943:         }
09944:         #${SCRIPT.criticalDrawerId} .mcms-critical-city { color:#f5f7fa !important; }
09945:         #${SCRIPT.criticalDrawerId} .mcms-critical-postcode { border-color:rgba(88,194,255,.64) !important; color:#9fddff !important; }
09946:         #${SCRIPT.criticalDrawerId} .mcms-critical-distance { border-color:rgba(106,224,196,.55) !important; color:#aef3df !important; }
09947:         html[data-mcms-tablet-active="true"] #${SCRIPT.criticalDrawerId} .mcms-drawer-expand {
09948:             min-width:74px !important;
09949:             height:44px !important;
09950:             border-radius:10px !important;
09951:             font-size:16px !important;
09952:         }
```

### Lines 9948-9958
```text
09948:             min-width:74px !important;
09949:             height:44px !important;
09950:             border-radius:10px !important;
09951:             font-size:16px !important;
09952:         }
09953:         html[data-mcms-tablet-active="true"] #${SCRIPT.criticalDrawerId} .mcms-drawer-expand small { font-size:6.5px !important; }
09954:         html[data-mcms-tablet-active="true"] #${SCRIPT.criticalDrawerId} .mcms-critical-sort-controls { max-width:340px !important; }
09955:         html[data-mcms-tablet-active="true"] #${SCRIPT.criticalDrawerId} .mcms-critical-sort-button { min-height:27px !important; }
09956:         html[data-mcms-tablet-active="true"] #${SCRIPT.criticalDrawerId} .mcms-critical-sort-button span { font-size:7.8px !important; }
09957:         html[data-mcms-tablet-active="true"] #${SCRIPT.criticalDrawerId} .mcms-critical-city,
09958:         html[data-mcms-tablet-active="true"] #${SCRIPT.criticalDrawerId} .mcms-critical-postcode,
```

### Lines 9949-9959
```text
09949:             height:44px !important;
09950:             border-radius:10px !important;
09951:             font-size:16px !important;
09952:         }
09953:         html[data-mcms-tablet-active="true"] #${SCRIPT.criticalDrawerId} .mcms-drawer-expand small { font-size:6.5px !important; }
09954:         html[data-mcms-tablet-active="true"] #${SCRIPT.criticalDrawerId} .mcms-critical-sort-controls { max-width:340px !important; }
09955:         html[data-mcms-tablet-active="true"] #${SCRIPT.criticalDrawerId} .mcms-critical-sort-button { min-height:27px !important; }
09956:         html[data-mcms-tablet-active="true"] #${SCRIPT.criticalDrawerId} .mcms-critical-sort-button span { font-size:7.8px !important; }
09957:         html[data-mcms-tablet-active="true"] #${SCRIPT.criticalDrawerId} .mcms-critical-city,
09958:         html[data-mcms-tablet-active="true"] #${SCRIPT.criticalDrawerId} .mcms-critical-postcode,
09959:         html[data-mcms-tablet-active="true"] #${SCRIPT.criticalDrawerId} .mcms-critical-distance {
```

### Lines 9950-9960
```text
09950:             border-radius:10px !important;
09951:             font-size:16px !important;
09952:         }
09953:         html[data-mcms-tablet-active="true"] #${SCRIPT.criticalDrawerId} .mcms-drawer-expand small { font-size:6.5px !important; }
09954:         html[data-mcms-tablet-active="true"] #${SCRIPT.criticalDrawerId} .mcms-critical-sort-controls { max-width:340px !important; }
09955:         html[data-mcms-tablet-active="true"] #${SCRIPT.criticalDrawerId} .mcms-critical-sort-button { min-height:27px !important; }
09956:         html[data-mcms-tablet-active="true"] #${SCRIPT.criticalDrawerId} .mcms-critical-sort-button span { font-size:7.8px !important; }
09957:         html[data-mcms-tablet-active="true"] #${SCRIPT.criticalDrawerId} .mcms-critical-city,
09958:         html[data-mcms-tablet-active="true"] #${SCRIPT.criticalDrawerId} .mcms-critical-postcode,
09959:         html[data-mcms-tablet-active="true"] #${SCRIPT.criticalDrawerId} .mcms-critical-distance {
09960:             min-height:19px !important;
```

### Lines 9951-9961
```text
09951:             font-size:16px !important;
09952:         }
09953:         html[data-mcms-tablet-active="true"] #${SCRIPT.criticalDrawerId} .mcms-drawer-expand small { font-size:6.5px !important; }
09954:         html[data-mcms-tablet-active="true"] #${SCRIPT.criticalDrawerId} .mcms-critical-sort-controls { max-width:340px !important; }
09955:         html[data-mcms-tablet-active="true"] #${SCRIPT.criticalDrawerId} .mcms-critical-sort-button { min-height:27px !important; }
09956:         html[data-mcms-tablet-active="true"] #${SCRIPT.criticalDrawerId} .mcms-critical-sort-button span { font-size:7.8px !important; }
09957:         html[data-mcms-tablet-active="true"] #${SCRIPT.criticalDrawerId} .mcms-critical-city,
09958:         html[data-mcms-tablet-active="true"] #${SCRIPT.criticalDrawerId} .mcms-critical-postcode,
09959:         html[data-mcms-tablet-active="true"] #${SCRIPT.criticalDrawerId} .mcms-critical-distance {
09960:             min-height:19px !important;
09961:             padding-inline:6px !important;
```

### Lines 9952-9962
```text
09952:         }
09953:         html[data-mcms-tablet-active="true"] #${SCRIPT.criticalDrawerId} .mcms-drawer-expand small { font-size:6.5px !important; }
09954:         html[data-mcms-tablet-active="true"] #${SCRIPT.criticalDrawerId} .mcms-critical-sort-controls { max-width:340px !important; }
09955:         html[data-mcms-tablet-active="true"] #${SCRIPT.criticalDrawerId} .mcms-critical-sort-button { min-height:27px !important; }
09956:         html[data-mcms-tablet-active="true"] #${SCRIPT.criticalDrawerId} .mcms-critical-sort-button span { font-size:7.8px !important; }
09957:         html[data-mcms-tablet-active="true"] #${SCRIPT.criticalDrawerId} .mcms-critical-city,
09958:         html[data-mcms-tablet-active="true"] #${SCRIPT.criticalDrawerId} .mcms-critical-postcode,
09959:         html[data-mcms-tablet-active="true"] #${SCRIPT.criticalDrawerId} .mcms-critical-distance {
09960:             min-height:19px !important;
09961:             padding-inline:6px !important;
09962:             font-size:6.8px !important;
```

### Lines 9953-9963
```text
09953:         html[data-mcms-tablet-active="true"] #${SCRIPT.criticalDrawerId} .mcms-drawer-expand small { font-size:6.5px !important; }
09954:         html[data-mcms-tablet-active="true"] #${SCRIPT.criticalDrawerId} .mcms-critical-sort-controls { max-width:340px !important; }
09955:         html[data-mcms-tablet-active="true"] #${SCRIPT.criticalDrawerId} .mcms-critical-sort-button { min-height:27px !important; }
09956:         html[data-mcms-tablet-active="true"] #${SCRIPT.criticalDrawerId} .mcms-critical-sort-button span { font-size:7.8px !important; }
09957:         html[data-mcms-tablet-active="true"] #${SCRIPT.criticalDrawerId} .mcms-critical-city,
09958:         html[data-mcms-tablet-active="true"] #${SCRIPT.criticalDrawerId} .mcms-critical-postcode,
09959:         html[data-mcms-tablet-active="true"] #${SCRIPT.criticalDrawerId} .mcms-critical-distance {
09960:             min-height:19px !important;
09961:             padding-inline:6px !important;
09962:             font-size:6.8px !important;
09963:         }
```

### Lines 9954-9964
```text
09954:         html[data-mcms-tablet-active="true"] #${SCRIPT.criticalDrawerId} .mcms-critical-sort-controls { max-width:340px !important; }
09955:         html[data-mcms-tablet-active="true"] #${SCRIPT.criticalDrawerId} .mcms-critical-sort-button { min-height:27px !important; }
09956:         html[data-mcms-tablet-active="true"] #${SCRIPT.criticalDrawerId} .mcms-critical-sort-button span { font-size:7.8px !important; }
09957:         html[data-mcms-tablet-active="true"] #${SCRIPT.criticalDrawerId} .mcms-critical-city,
09958:         html[data-mcms-tablet-active="true"] #${SCRIPT.criticalDrawerId} .mcms-critical-postcode,
09959:         html[data-mcms-tablet-active="true"] #${SCRIPT.criticalDrawerId} .mcms-critical-distance {
09960:             min-height:19px !important;
09961:             padding-inline:6px !important;
09962:             font-size:6.8px !important;
09963:         }
09964:         html[data-mcms-mobile-active="true"] #${SCRIPT.criticalDrawerId} .mcms-drawer-expand { display:none !important; }
```

### Lines 9961-9971
```text
09961:             padding-inline:6px !important;
09962:             font-size:6.8px !important;
09963:         }
09964:         html[data-mcms-mobile-active="true"] #${SCRIPT.criticalDrawerId} .mcms-drawer-expand { display:none !important; }
09965:         html[data-mcms-mobile-active="true"] #${SCRIPT.criticalDrawerId} .mcms-critical-sort-controls {
09966:             grid-template-columns:auto repeat(3,minmax(0,1fr)) !important;
09967:             max-width:none !important;
09968:         }
09969:         html[data-mcms-mobile-active="true"] #${SCRIPT.criticalDrawerId} .mcms-critical-location { gap:2px !important; }
09970:         html[data-mcms-mobile-active="true"] #${SCRIPT.criticalDrawerId} .mcms-critical-city,
09971:         html[data-mcms-mobile-active="true"] #${SCRIPT.criticalDrawerId} .mcms-critical-postcode,
```

### Lines 9979-9989
```text
09979:         /* v3.20.1 Mission Age Watch official-event metadata plus exact-title fallback detection. */
09980:         #${SCRIPT.criticalDrawerId} .mcms-drawer-heading { display:block !important; min-width:0 !important; }
09981:         #${SCRIPT.criticalDrawerId} .mcms-drawer-identity,
09982:         #${SCRIPT.criticalDrawerId} .mcms-drawer-header-controls { min-width:0 !important; }
09983:         #${SCRIPT.criticalDrawerId} .mcms-critical-type-filters {
09984:             grid-template-columns:auto repeat(4,minmax(0,1fr)) !important;
09985:         }
09986:         #${SCRIPT.criticalDrawerId} .mcms-critical-type-filter:not(.mcms-filter-active) {
09987:             opacity:.62 !important;
09988:             filter:saturate(.72) brightness(.88) !important;
09989:         }
```

### Lines 10013-10023
```text
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
```

### Lines 10029-10039
```text
10029:             align-items:start !important;
10030:             padding-bottom:6px !important;
10031:         }
10032:         #${SCRIPT.criticalDrawerId}.mcms-critical-expanded .mcms-drawer-heading {
10033:             display:grid !important;
10034:             grid-template-columns:repeat(auto-fit,minmax(min(100%,280px),1fr)) !important;
10035:             align-items:start !important;
10036:             gap:8px !important;
10037:         }
10038:         #${SCRIPT.criticalDrawerId}.mcms-critical-expanded .mcms-drawer-header-controls {
10039:             display:grid !important;
```

### Lines 10035-10045
```text
10035:             align-items:start !important;
10036:             gap:8px !important;
10037:         }
10038:         #${SCRIPT.criticalDrawerId}.mcms-critical-expanded .mcms-drawer-header-controls {
10039:             display:grid !important;
10040:             grid-template-columns:repeat(auto-fit,minmax(min(100%,210px),1fr)) !important;
10041:             gap:6px !important;
10042:             align-items:start !important;
10043:         }
10044:         #${SCRIPT.criticalDrawerId}.mcms-critical-expanded .mcms-critical-age-filters,
10045:         #${SCRIPT.criticalDrawerId}.mcms-critical-expanded .mcms-critical-sort-controls {
```

### Lines 10066-10076
```text
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
```

### Lines 10067-10077
```text
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
```

### Lines 10070-10080
```text
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

### Lines 10073-10083
```text
10073:         }
10074:         #${SCRIPT.criticalDrawerId}.mcms-critical-expanded .mcms-critical-lowerline {
10075:             grid-template-columns:minmax(0,1fr) 126px !important;
10076:         }
10077:         html[data-mcms-mobile-active="true"] #${SCRIPT.criticalDrawerId} .mcms-critical-type-filters {
10078:             grid-template-columns:repeat(2,minmax(0,1fr)) !important;
10079:         }
10080:         html[data-mcms-mobile-active="true"] #${SCRIPT.criticalDrawerId} .mcms-critical-type-label { grid-column:1 / -1 !important; }
10081: 
10082: 
10083:         /*
```

### Lines 10263-10273
```text
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
```

### Lines 10268-10278
```text
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
```

### Lines 10275-10285
```text
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
```

### Lines 10279-10289
```text
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
```

### Lines 10285-10295
```text
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
```

### Lines 10294-10304
```text
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
```

### Lines 10705-10715
```text
10705:         @keyframes mcmsBondGunBarrel {
10706:             from { transform:rotate(-5deg) scale(1.08); }
10707:             to { transform:rotate(355deg) scale(1.08); }
10708:         }
10709: 
10710:         html[data-mcms-tablet-active="true"][data-mcms-ui-theme="bond007"] #${SCRIPT.panelId} .mcms-header::before {
10711:             width:112px !important;
10712:             height:36px !important;
10713:             right:92px !important;
10714:         }
10715:         html[data-mcms-mobile-active="true"][data-mcms-ui-theme="bond007"] #${SCRIPT.panelId} .mcms-header::before {
```

### Lines 10768-10778
```text
10768:             color:#d9d4c9 !important;
10769:         }
10770:         html[data-mcms-ui-theme="bond007"] #${SCRIPT.panelId} .mcms-drag-handle {
10771:             padding-right:98px !important;
10772:         }
10773:         html[data-mcms-tablet-active="true"][data-mcms-ui-theme="bond007"] #${SCRIPT.panelId} .mcms-drag-handle {
10774:             padding-right:88px !important;
10775:         }
10776:         html[data-mcms-tablet-active="true"][data-mcms-ui-theme="bond007"] #${SCRIPT.panelId} .mcms-header::before {
10777:             width:76px !important;
10778:             height:26px !important;
```

### Lines 10771-10781
```text
10771:             padding-right:98px !important;
10772:         }
10773:         html[data-mcms-tablet-active="true"][data-mcms-ui-theme="bond007"] #${SCRIPT.panelId} .mcms-drag-handle {
10774:             padding-right:88px !important;
10775:         }
10776:         html[data-mcms-tablet-active="true"][data-mcms-ui-theme="bond007"] #${SCRIPT.panelId} .mcms-header::before {
10777:             width:76px !important;
10778:             height:26px !important;
10779:             right:60px !important;
10780:             top:14px !important;
10781:             opacity:.72 !important;
```

### Lines 10808-10818
```text
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
```

### Lines 10809-10819
```text
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
```

### Lines 10810-10820
```text
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
```

### Lines 10827-10837
```text
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
```

### Lines 10829-10839
```text
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
```

### Lines 10830-10840
```text
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
```

### Lines 10839-10849
```text
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
```

### Lines 10840-10850
```text
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
```

### Lines 10888-10898
```text
10888:             background-size:clamp(84px,20%,138px) auto,auto !important;
10889:         }
10890:         #${SCRIPT.payoutFlashId}[data-template="jamesBond"] .mcms-payout-title {
10891:             padding-inline:clamp(0px,8%,78px) !important;
10892:         }
10893:         @media (max-width:620px) {
10894:             #${SCRIPT.payoutFlashId} .mcms-payout-banner {
10895:                 width:calc(100% - 12px) !important;
10896:                 min-width:0 !important;
10897:                 padding:20px 14px 18px !important;
10898:             }
```

### Lines 10917-10927
```text
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
```

### Lines 10918-10928
```text
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
```

### Lines 10929-10939
```text
10929:             #${SCRIPT.payoutFlashId}[data-template="jamesBond"] .mcms-payout-title {
10930:                 padding-inline:0 !important;
10931:                 padding-top:24px !important;
10932:             }
10933:         }
10934:         @media (prefers-reduced-motion:reduce) {
10935:             html[data-mcms-ui-theme="bond007"] #${SCRIPT.panelId}.mcms-open,
10936:             html[data-mcms-ui-theme="bond007"] #${SCRIPT.majorIncidentFeedId}::before,
10937:             #${SCRIPT.payoutFlashId}[data-template="jamesBond"] .mcms-payout-theme-fx-a {
10938:                 animation:none !important;
10939:             }
```

### Lines 10941-10951
```text
10941:             html[data-mcms-ui-theme="bond007"] #${SCRIPT.panelId} button {
10942:                 transition:none !important;
10943:             }
10944:         }
10945: 
10946:         @media (prefers-reduced-motion:reduce) {
10947:             #${SCRIPT.criticalDrawerId}.mcms-open,
10948:             #${SCRIPT.criticalDrawerId}.mcms-critical-refreshing .mcms-drawer-refresh,
10949:             #${SCRIPT.criticalDrawerId} .mcms-critical-state-no-scene .mcms-critical-state-signal::before,
10950:             #${SCRIPT.criticalDrawerId} .mcms-critical-state-no-scene .mcms-critical-state-signal::after,
10951:             #${SCRIPT.criticalDrawerId} .mcms-critical-state-enroute .mcms-critical-state-signal,
```

### Lines 10972-10982
```text
10972:          * status filters are non-contradictory, unknown data remains neutral, and the
10973:          * progressively-rendered list stays readable across every interface theme.
10974:          */
10975:         #${SCRIPT.criticalDrawerId} .mcms-critical-refreshed {
10976:             display:flex !important;
10977:             flex-wrap:wrap !important;
10978:             gap:3px 8px !important;
10979:         }
10980:         #${SCRIPT.criticalDrawerId} .mcms-critical-category-filters,
10981:         #${SCRIPT.criticalDrawerId} .mcms-critical-type-filters {
10982:             display:grid !important;
```

### Lines 10978-10988
```text
10978:             gap:3px 8px !important;
10979:         }
10980:         #${SCRIPT.criticalDrawerId} .mcms-critical-category-filters,
10981:         #${SCRIPT.criticalDrawerId} .mcms-critical-type-filters {
10982:             display:grid !important;
10983:             grid-template-columns:auto repeat(4,minmax(0,1fr)) !important;
10984:             gap:4px !important;
10985:             margin-top:5px !important;
10986:         }
10987:         #${SCRIPT.criticalDrawerId} .mcms-critical-type-filters {
10988:             grid-template-columns:auto repeat(3,minmax(0,1fr)) !important;
```

### Lines 10983-10993
```text
10983:             grid-template-columns:auto repeat(4,minmax(0,1fr)) !important;
10984:             gap:4px !important;
10985:             margin-top:5px !important;
10986:         }
10987:         #${SCRIPT.criticalDrawerId} .mcms-critical-type-filters {
10988:             grid-template-columns:auto repeat(3,minmax(0,1fr)) !important;
10989:         }
10990:         #${SCRIPT.criticalDrawerId} .mcms-critical-category-label {
10991:             display:flex !important;
10992:             align-items:center !important;
10993:             justify-content:center !important;
```

### Lines 11000-11010
```text
11000:             text-transform:uppercase !important;
11001:         }
11002:         #${SCRIPT.criticalDrawerId} .mcms-critical-category-filter {
11003:             position:relative !important;
11004:             display:grid !important;
11005:             grid-template-columns:minmax(0,1fr) auto !important;
11006:             align-items:center !important;
11007:             min-width:0 !important;
11008:             min-height:27px !important;
11009:             gap:5px !important;
11010:             padding:4px 7px !important;
```

### Lines 11014-11024
```text
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
```

### Lines 11030-11040
```text
11030:         #${SCRIPT.criticalDrawerId} .mcms-category-special { color:#ff9fe8 !important; border-color:rgba(255,74,204,.82) !important; background:rgba(80,8,63,.54) !important; }
11031: 
11032:         /* v4.1.1: keep Sort and Distance Origin controls on distinct rows so
11033:            labels cannot collide in expanded, tablet or narrower desktop layouts. */
11034:         #${SCRIPT.criticalDrawerId} .mcms-critical-sort-controls {
11035:             grid-template-columns:auto repeat(3,minmax(50px,1fr)) !important;
11036:             grid-auto-rows:minmax(21px,auto) !important;
11037:         }
11038:         #${SCRIPT.criticalDrawerId} .mcms-critical-sort-button span {
11039:             display:block !important;
11040:             width:100% !important;
```

### Lines 11038-11048
```text
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
```

### Lines 11039-11049
```text
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
```

### Lines 11045-11055
```text
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
```

### Lines 11056-11066
```text
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
```

### Lines 11058-11068
```text
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
```

### Lines 11063-11073
```text
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
```

### Lines 11065-11075
```text
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
```

### Lines 11083-11093
```text
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
```

### Lines 11094-11104
```text
11094:         #${SCRIPT.criticalDrawerId} .mcms-critical-eligibility.mcms-not-eligible { color:#ffd47b !important; background:rgba(91,57,2,.74) !important; }
11095:         #${SCRIPT.criticalDrawerId} .mcms-critical-data-badge.mcms-data-sync { color:#d8e6ee !important; background:rgba(68,88,102,.82) !important; animation:mcmsCriticalSyncPulse 1.4s ease-in-out infinite !important; }
11096:         #${SCRIPT.criticalDrawerId} .mcms-critical-data-badge.mcms-data-unknown { color:#d5dce1 !important; background:rgba(63,68,73,.72) !important; }
11097:         @keyframes mcmsCriticalSyncPulse { 50% { filter:brightness(1.45); box-shadow:0 0 8px rgba(173,207,230,.38); } }
11098: 
11099:         #${SCRIPT.criticalDrawerId} .mcms-critical-live-markers { display:flex !important; flex-wrap:wrap !important; justify-content:flex-end !important; gap:4px !important; }
11100:         #${SCRIPT.criticalDrawerId} .mcms-critical-prisoners { display:inline-flex !important; align-items:center !important; gap:3px !important; min-height:20px !important; padding:3px 7px !important; border:1px solid rgba(255,159,67,.82) !important; border-radius:999px !important; background:rgba(92,41,5,.82) !important; color:#ffd0a5 !important; }
11101:         #${SCRIPT.criticalDrawerId} .mcms-critical-prisoners strong { font-size:9px !important; }
11102:         #${SCRIPT.criticalDrawerId} .mcms-critical-prisoners small { font-size:5.4px !important; font-weight:950 !important; }
11103:         #${SCRIPT.criticalDrawerId} .mcms-critical-unit-extras { display:flex !important; flex-wrap:wrap !important; gap:3px !important; grid-column:1 / -1 !important; }
11104:         #${SCRIPT.criticalDrawerId} .mcms-critical-unit-extra { display:inline-flex !important; align-items:center !important; gap:3px !important; padding:2px 5px !important; border:1px solid rgba(255,255,255,.22) !important; border-radius:999px !important; background:rgba(255,255,255,.06) !important; font-size:5.2px !important; }
```

### Lines 11098-11108
```text
11098: 
11099:         #${SCRIPT.criticalDrawerId} .mcms-critical-live-markers { display:flex !important; flex-wrap:wrap !important; justify-content:flex-end !important; gap:4px !important; }
11100:         #${SCRIPT.criticalDrawerId} .mcms-critical-prisoners { display:inline-flex !important; align-items:center !important; gap:3px !important; min-height:20px !important; padding:3px 7px !important; border:1px solid rgba(255,159,67,.82) !important; border-radius:999px !important; background:rgba(92,41,5,.82) !important; color:#ffd0a5 !important; }
11101:         #${SCRIPT.criticalDrawerId} .mcms-critical-prisoners strong { font-size:9px !important; }
11102:         #${SCRIPT.criticalDrawerId} .mcms-critical-prisoners small { font-size:5.4px !important; font-weight:950 !important; }
11103:         #${SCRIPT.criticalDrawerId} .mcms-critical-unit-extras { display:flex !important; flex-wrap:wrap !important; gap:3px !important; grid-column:1 / -1 !important; }
11104:         #${SCRIPT.criticalDrawerId} .mcms-critical-unit-extra { display:inline-flex !important; align-items:center !important; gap:3px !important; padding:2px 5px !important; border:1px solid rgba(255,255,255,.22) !important; border-radius:999px !important; background:rgba(255,255,255,.06) !important; font-size:5.2px !important; }
11105:         #${SCRIPT.criticalDrawerId} .mcms-critical-unit-extra strong { font-size:7px !important; }
11106:         #${SCRIPT.criticalDrawerId} .mcms-unit-transporting { color:#ffc47a !important; border-color:rgba(255,153,40,.68) !important; }
11107:         #${SCRIPT.criticalDrawerId} .mcms-unit-awaiting { color:#ffe18b !important; border-color:rgba(255,212,82,.68) !important; }
11108:         #${SCRIPT.criticalDrawerId} .mcms-unit-oos { color:#d4dbe0 !important; border-color:rgba(172,186,196,.55) !important; }
```

### Lines 11118-11128
```text
11118:         #${SCRIPT.criticalDrawerId} .mcms-critical-row { content-visibility:auto !important; contain-intrinsic-size:112px !important; }
11119:         #${SCRIPT.criticalDrawerId} .mcms-critical-list-footer { display:flex !important; align-items:center !important; justify-content:space-between !important; gap:8px !important; padding:7px !important; border:1px solid rgba(255,255,255,.14) !important; border-radius:7px !important; background:rgba(12,18,23,.88) !important; color:#c9d8e2 !important; font-size:7px !important; font-weight:900 !important; }
11120:         #${SCRIPT.criticalDrawerId} .mcms-critical-list-footer button { padding:5px 9px !important; border:1px solid rgba(87,183,244,.72) !important; border-radius:5px !important; background:rgba(5,61,96,.88) !important; color:#d9f2ff !important; font:950 7px/1 Arial,sans-serif !important; cursor:pointer !important; }
11121: 
11122:         html[data-mcms-mobile-active="true"] #${SCRIPT.criticalDrawerId} .mcms-critical-category-filters,
11123:         html[data-mcms-mobile-active="true"] #${SCRIPT.criticalDrawerId} .mcms-critical-type-filters { grid-template-columns:repeat(2,minmax(0,1fr)) !important; }
11124:         html[data-mcms-mobile-active="true"] #${SCRIPT.criticalDrawerId} .mcms-critical-category-label,
11125:         html[data-mcms-mobile-active="true"] #${SCRIPT.criticalDrawerId} .mcms-critical-type-label { grid-column:1 / -1 !important; min-height:18px !important; }
11126:         html[data-mcms-mobile-active="true"] #${SCRIPT.criticalDrawerId} .mcms-critical-sort-controls { grid-template-columns:repeat(3,minmax(0,1fr)) !important; }
11127:         html[data-mcms-mobile-active="true"] #${SCRIPT.criticalDrawerId} .mcms-critical-sort-label,
11128:         html[data-mcms-mobile-active="true"] #${SCRIPT.criticalDrawerId} .mcms-critical-origin-control { grid-column:1 / -1 !important; }
```

### Lines 11121-11131
```text
11121: 
11122:         html[data-mcms-mobile-active="true"] #${SCRIPT.criticalDrawerId} .mcms-critical-category-filters,
11123:         html[data-mcms-mobile-active="true"] #${SCRIPT.criticalDrawerId} .mcms-critical-type-filters { grid-template-columns:repeat(2,minmax(0,1fr)) !important; }
11124:         html[data-mcms-mobile-active="true"] #${SCRIPT.criticalDrawerId} .mcms-critical-category-label,
11125:         html[data-mcms-mobile-active="true"] #${SCRIPT.criticalDrawerId} .mcms-critical-type-label { grid-column:1 / -1 !important; min-height:18px !important; }
11126:         html[data-mcms-mobile-active="true"] #${SCRIPT.criticalDrawerId} .mcms-critical-sort-controls { grid-template-columns:repeat(3,minmax(0,1fr)) !important; }
11127:         html[data-mcms-mobile-active="true"] #${SCRIPT.criticalDrawerId} .mcms-critical-sort-label,
11128:         html[data-mcms-mobile-active="true"] #${SCRIPT.criticalDrawerId} .mcms-critical-origin-control { grid-column:1 / -1 !important; }
11129:         html[data-mcms-mobile-active="true"] #${SCRIPT.criticalDrawerId} .mcms-critical-lock-origin { grid-column:1 / -1 !important; min-height:28px !important; }
11130:         html[data-mcms-mobile-active="true"] #${SCRIPT.criticalDrawerId} .mcms-critical-summary { grid-template-columns:repeat(2,minmax(0,1fr)) !important; }
11131:         html[data-mcms-mobile-active="true"] #${SCRIPT.criticalDrawerId} .mcms-critical-values { grid-template-columns:auto minmax(0,1fr) auto !important; }
```

### Lines 11125-11135
```text
11125:         html[data-mcms-mobile-active="true"] #${SCRIPT.criticalDrawerId} .mcms-critical-type-label { grid-column:1 / -1 !important; min-height:18px !important; }
11126:         html[data-mcms-mobile-active="true"] #${SCRIPT.criticalDrawerId} .mcms-critical-sort-controls { grid-template-columns:repeat(3,minmax(0,1fr)) !important; }
11127:         html[data-mcms-mobile-active="true"] #${SCRIPT.criticalDrawerId} .mcms-critical-sort-label,
11128:         html[data-mcms-mobile-active="true"] #${SCRIPT.criticalDrawerId} .mcms-critical-origin-control { grid-column:1 / -1 !important; }
11129:         html[data-mcms-mobile-active="true"] #${SCRIPT.criticalDrawerId} .mcms-critical-lock-origin { grid-column:1 / -1 !important; min-height:28px !important; }
11130:         html[data-mcms-mobile-active="true"] #${SCRIPT.criticalDrawerId} .mcms-critical-summary { grid-template-columns:repeat(2,minmax(0,1fr)) !important; }
11131:         html[data-mcms-mobile-active="true"] #${SCRIPT.criticalDrawerId} .mcms-critical-values { grid-template-columns:auto minmax(0,1fr) auto !important; }
11132:         html[data-mcms-mobile-active="true"] #${SCRIPT.criticalDrawerId} .mcms-critical-value-mode { grid-column:2 / 3 !important; }
11133:         html[data-mcms-mobile-active="true"] #${SCRIPT.criticalDrawerId} .mcms-critical-values-grid { grid-column:1 / -1 !important; }
11134:         html[data-mcms-mobile-active="true"] #${SCRIPT.criticalDrawerId} .mcms-critical-showing { grid-column:1 / 3 !important; }
11135: 
```

### Lines 11126-11136
```text
11126:         html[data-mcms-mobile-active="true"] #${SCRIPT.criticalDrawerId} .mcms-critical-sort-controls { grid-template-columns:repeat(3,minmax(0,1fr)) !important; }
11127:         html[data-mcms-mobile-active="true"] #${SCRIPT.criticalDrawerId} .mcms-critical-sort-label,
11128:         html[data-mcms-mobile-active="true"] #${SCRIPT.criticalDrawerId} .mcms-critical-origin-control { grid-column:1 / -1 !important; }
11129:         html[data-mcms-mobile-active="true"] #${SCRIPT.criticalDrawerId} .mcms-critical-lock-origin { grid-column:1 / -1 !important; min-height:28px !important; }
11130:         html[data-mcms-mobile-active="true"] #${SCRIPT.criticalDrawerId} .mcms-critical-summary { grid-template-columns:repeat(2,minmax(0,1fr)) !important; }
11131:         html[data-mcms-mobile-active="true"] #${SCRIPT.criticalDrawerId} .mcms-critical-values { grid-template-columns:auto minmax(0,1fr) auto !important; }
11132:         html[data-mcms-mobile-active="true"] #${SCRIPT.criticalDrawerId} .mcms-critical-value-mode { grid-column:2 / 3 !important; }
11133:         html[data-mcms-mobile-active="true"] #${SCRIPT.criticalDrawerId} .mcms-critical-values-grid { grid-column:1 / -1 !important; }
11134:         html[data-mcms-mobile-active="true"] #${SCRIPT.criticalDrawerId} .mcms-critical-showing { grid-column:1 / 3 !important; }
11135: 
11136:         /* v4.3.2: compact Mission Age Watch View Controls submenu. */
```

### Lines 11141-11151
```text
11141:             max-width:278px !important;
11142:             margin-top:5px !important;
11143:         }
11144:         #${SCRIPT.criticalDrawerId} .mcms-critical-view-trigger {
11145:             display:grid !important;
11146:             grid-template-columns:minmax(0,1fr) auto !important;
11147:             grid-template-areas:"label chevron" "summary chevron" !important;
11148:             align-items:center !important;
11149:             width:100% !important;
11150:             min-width:0 !important;
11151:             min-height:36px !important;
```

### Lines 11182-11192
```text
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
```

### Lines 11183-11193
```text
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
```

### Lines 11263-11273
```text
11263:         #${SCRIPT.criticalDrawerId}.mcms-critical-expanded .mcms-critical-view-menu .mcms-critical-sort-controls {
11264:             width:100% !important;
11265:             max-width:none !important;
11266:             margin-top:6px !important;
11267:         }
11268:         html[data-mcms-tablet-active="true"] #${SCRIPT.criticalDrawerId} .mcms-drawer-header-controls {
11269:             max-width:360px !important;
11270:         }
11271:         html[data-mcms-tablet-active="true"] #${SCRIPT.criticalDrawerId} .mcms-critical-view-trigger {
11272:             min-height:44px !important;
11273:             padding:7px 10px !important;
```

### Lines 11266-11276
```text
11266:             margin-top:6px !important;
11267:         }
11268:         html[data-mcms-tablet-active="true"] #${SCRIPT.criticalDrawerId} .mcms-drawer-header-controls {
11269:             max-width:360px !important;
11270:         }
11271:         html[data-mcms-tablet-active="true"] #${SCRIPT.criticalDrawerId} .mcms-critical-view-trigger {
11272:             min-height:44px !important;
11273:             padding:7px 10px !important;
11274:             border-radius:10px !important;
11275:         }
11276:         html[data-mcms-tablet-active="true"] #${SCRIPT.criticalDrawerId} .mcms-critical-view-trigger-label { font-size:7px !important; }
```

### Lines 11271-11281
```text
11271:         html[data-mcms-tablet-active="true"] #${SCRIPT.criticalDrawerId} .mcms-critical-view-trigger {
11272:             min-height:44px !important;
11273:             padding:7px 10px !important;
11274:             border-radius:10px !important;
11275:         }
11276:         html[data-mcms-tablet-active="true"] #${SCRIPT.criticalDrawerId} .mcms-critical-view-trigger-label { font-size:7px !important; }
11277:         html[data-mcms-tablet-active="true"] #${SCRIPT.criticalDrawerId} .mcms-critical-view-trigger strong { font-size:8.5px !important; }
11278:         html[data-mcms-tablet-active="true"] #${SCRIPT.criticalDrawerId} .mcms-critical-view-menu { padding:9px !important; border-radius:10px !important; }
11279:         html[data-mcms-mobile-active="true"] #${SCRIPT.criticalDrawerId} .mcms-drawer-header-controls {
11280:             max-width:none !important;
11281:         }
```

### Lines 11272-11282
```text
11272:             min-height:44px !important;
11273:             padding:7px 10px !important;
11274:             border-radius:10px !important;
11275:         }
11276:         html[data-mcms-tablet-active="true"] #${SCRIPT.criticalDrawerId} .mcms-critical-view-trigger-label { font-size:7px !important; }
11277:         html[data-mcms-tablet-active="true"] #${SCRIPT.criticalDrawerId} .mcms-critical-view-trigger strong { font-size:8.5px !important; }
11278:         html[data-mcms-tablet-active="true"] #${SCRIPT.criticalDrawerId} .mcms-critical-view-menu { padding:9px !important; border-radius:10px !important; }
11279:         html[data-mcms-mobile-active="true"] #${SCRIPT.criticalDrawerId} .mcms-drawer-header-controls {
11280:             max-width:none !important;
11281:         }
11282:         html[data-mcms-mobile-active="true"] #${SCRIPT.criticalDrawerId} .mcms-critical-view-trigger {
```

### Lines 11273-11283
```text
11273:             padding:7px 10px !important;
11274:             border-radius:10px !important;
11275:         }
11276:         html[data-mcms-tablet-active="true"] #${SCRIPT.criticalDrawerId} .mcms-critical-view-trigger-label { font-size:7px !important; }
11277:         html[data-mcms-tablet-active="true"] #${SCRIPT.criticalDrawerId} .mcms-critical-view-trigger strong { font-size:8.5px !important; }
11278:         html[data-mcms-tablet-active="true"] #${SCRIPT.criticalDrawerId} .mcms-critical-view-menu { padding:9px !important; border-radius:10px !important; }
11279:         html[data-mcms-mobile-active="true"] #${SCRIPT.criticalDrawerId} .mcms-drawer-header-controls {
11280:             max-width:none !important;
11281:         }
11282:         html[data-mcms-mobile-active="true"] #${SCRIPT.criticalDrawerId} .mcms-critical-view-trigger {
11283:             min-height:42px !important;
```

### Lines 11281-11291
```text
11281:         }
11282:         html[data-mcms-mobile-active="true"] #${SCRIPT.criticalDrawerId} .mcms-critical-view-trigger {
11283:             min-height:42px !important;
11284:         }
11285:         html[data-mcms-mobile-active="true"] #${SCRIPT.criticalDrawerId} .mcms-critical-view-menu .mcms-critical-age-filters {
11286:             grid-template-columns:repeat(4,minmax(0,1fr)) !important;
11287:         }
11288:         html[data-mcms-mobile-active="true"] #${SCRIPT.criticalDrawerId} .mcms-critical-view-menu .mcms-critical-age-label {
11289:             grid-column:1 / -1 !important;
11290:             justify-content:flex-start !important;
11291:             min-height:14px !important;
```

### Lines 11290-11300
```text
11290:             justify-content:flex-start !important;
11291:             min-height:14px !important;
11292:             padding-left:1px !important;
11293:         }
11294:         html[data-mcms-mobile-active="true"] #${SCRIPT.criticalDrawerId} .mcms-critical-view-menu .mcms-critical-sort-controls {
11295:             grid-template-columns:repeat(3,minmax(0,1fr)) !important;
11296:         }
11297:         html[data-mcms-mobile-active="true"] #${SCRIPT.criticalDrawerId} .mcms-critical-view-menu .mcms-critical-sort-label,
11298:         html[data-mcms-mobile-active="true"] #${SCRIPT.criticalDrawerId} .mcms-critical-view-menu .mcms-critical-origin-control,
11299:         html[data-mcms-mobile-active="true"] #${SCRIPT.criticalDrawerId} .mcms-critical-view-menu .mcms-critical-lock-origin {
11300:             grid-column:1 / -1 !important;
```

### Lines 11298-11308
```text
11298:         html[data-mcms-mobile-active="true"] #${SCRIPT.criticalDrawerId} .mcms-critical-view-menu .mcms-critical-origin-control,
11299:         html[data-mcms-mobile-active="true"] #${SCRIPT.criticalDrawerId} .mcms-critical-view-menu .mcms-critical-lock-origin {
11300:             grid-column:1 / -1 !important;
11301:         }
11302: 
11303:         @media (prefers-reduced-motion: reduce) {
11304:             #${SCRIPT.criticalDrawerId} .mcms-critical-data-badge.mcms-data-sync,
11305:             html[data-mcms-ui-theme] #${SCRIPT.criticalDrawerId} .mcms-critical-state-syncing .mcms-critical-state-signal { animation:none !important; }
11306:         }
11307: 
11308: 
```

### Lines 11370-11380
```text
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
```

### Lines 11371-11381
```text
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
```

### Lines 11374-11384
```text
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
```

### Lines 11379-11389
```text
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
```

### Lines 11393-11403
```text
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
```

### Lines 11394-11404
```text
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
```

### Lines 11398-11408
```text
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
```

### Lines 11399-11409
```text
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
```

### Lines 11412-11422
```text
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
```

### Lines 11420-11430
```text
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
```

### Lines 11421-11431
```text
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
```

### Lines 11550-11560
```text
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
```

### Lines 11551-11561
```text
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
```

### Lines 11654-11664
```text
11654:         #${SCRIPT.payoutFlashId}.mcms-payout-fit-tight[data-template="biohazard"] .mcms-payout-kicker {
11655:             font-size:7px !important;
11656:             letter-spacing:.9px !important;
11657:         }
11658: 
11659:         @media (max-width:760px) {
11660:             html[data-mcms-ui-theme="umbrella"] #${SCRIPT.panelId} .mcms-header {
11661:                 background:
11662:                     repeating-linear-gradient(90deg,rgba(216,25,63,.025) 0 1px,transparent 1px 16px),
11663:                     linear-gradient(180deg,#262a31,#14171d) !important;
11664:             }
```

### Lines 11661-11671
```text
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
```

### Lines 11662-11672
```text
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
```

### Lines 11672-11682
```text
11672:             #${SCRIPT.payoutFlashId}[data-template="biohazard"] .mcms-payout-mission { font-size:clamp(10px,3.3vw,14px) !important; }
11673:             #${SCRIPT.payoutFlashId}[data-template="biohazard"] .mcms-payout-kicker { font-size:7px !important; letter-spacing:1px !important; }
11674:             #${SCRIPT.payoutFlashId}[data-template="biohazard"] .mcms-payout-banner::after { opacity:.06 !important; background-size:88px auto,62px auto !important; }
11675:             #${SCRIPT.payoutFlashId}[data-template="biohazard"] .mcms-payout-banner::before { left:16px !important; right:16px !important; max-width:calc(100% - 32px) !important; font-size:6px !important; letter-spacing:.65px !important; }
11676:         }
11677:         @media (prefers-reduced-motion:reduce) {
11678:             html[data-mcms-ui-theme="umbrella"] #${SCRIPT.panelId} .mcms-header::after,
11679:             html[data-mcms-ui-theme="umbrella"] #${SCRIPT.controlId} .mcms-float-btn.mcms-on { animation:none !important; }
11680:         }
11681: 
11682:         /* v4.2.0 searchable Help Centre and browser-style guide viewer. */
```

### Lines 11719-11729
```text
11719:             border:1px solid #8f7a3f !important; border-radius:2px !important; background:#111316 !important; color:#f0d47f !important;
11720:         }
11721:         html[data-mcms-ui-theme="bond007"] #${SCRIPT.panelId} .mcms-help-button:hover,
11722:         html[data-mcms-ui-theme="bond007"] #${SCRIPT.panelId} .mcms-help-button:focus-visible { border-color:#d5b85f !important; background:#292313 !important; color:#fff0b6 !important; }
11723:         html[data-mcms-ui-theme="bond007"] #${SCRIPT.panelId} .mcms-header::before { right:90px !important; }
11724:         html[data-mcms-tablet-active="true"][data-mcms-ui-theme="bond007"] #${SCRIPT.panelId} .mcms-header::before { right:108px !important; }
11725:         html[data-mcms-mobile-active="true"][data-mcms-ui-theme="bond007"] #${SCRIPT.panelId} .mcms-header::before { right:101px !important; }
11726: 
11727:         #${SCRIPT.helpCenterId} {
11728:             display:none !important; position:fixed !important; inset:0 !important; z-index:2147483600 !important;
11729:             align-items:center !important; justify-content:center !important; padding:18px !important;
```

### Lines 11737-11747
```text
11737:             display:flex !important; flex-direction:column !important; overflow:hidden !important;
11738:             border:1px solid rgba(92,190,232,.42) !important; border-radius:16px !important;
11739:             background:#071018 !important; box-shadow:0 28px 90px rgba(0,0,0,.72),inset 0 1px rgba(255,255,255,.05) !important;
11740:         }
11741:         #${SCRIPT.helpCenterId} .mcms-help-toolbar {
11742:             min-height:56px !important; display:grid !important; grid-template-columns:minmax(0,1fr) auto !important; align-items:center !important; gap:12px !important;
11743:             padding:8px 10px 8px 14px !important; border-bottom:1px solid rgba(93,175,212,.25) !important;
11744:             background:linear-gradient(180deg,#102532,#091720) !important; color:#edf8ff !important;
11745:         }
11746:         #${SCRIPT.helpCenterId} .mcms-help-brand { min-width:0 !important; display:flex !important; align-items:center !important; gap:10px !important; }
11747:         #${SCRIPT.helpCenterId} .mcms-help-brand-icon {
```

### Lines 11748-11758
```text
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
```

### Lines 11759-11769
```text
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
```

### Lines 11764-11774
```text
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
```

### Lines 11765-11775
```text
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
```

### Lines 11786-11796
```text
11786:             width:min(520px,100%) !important; padding:24px !important; border:1px solid rgba(96,184,224,.32) !important; border-radius:16px !important;
11787:             background:#0d1f2a !important; color:#eaf6fb !important; text-align:center !important; box-shadow:0 18px 48px rgba(0,0,0,.40) !important;
11788:         }
11789:         #${SCRIPT.helpCenterId} .mcms-help-error-card strong { display:block !important; font-size:18px !important; }
11790:         #${SCRIPT.helpCenterId} .mcms-help-error-card p { margin:9px 0 16px !important; color:#9db5c1 !important; font-size:11px !important; line-height:1.45 !important; }
11791:         #${SCRIPT.helpCenterId} .mcms-help-error-actions { display:flex !important; justify-content:center !important; flex-wrap:wrap !important; gap:8px !important; }
11792:         #${SCRIPT.helpCenterId} .mcms-help-error-actions button { min-height:38px !important; padding:0 14px !important; border:1px solid #4286a5 !important; border-radius:9px !important; background:#12384b !important; color:#fff !important; cursor:pointer !important; font-size:11px !important; font-weight:900 !important; }
11793:         @media (max-width:760px) {
11794:             #${SCRIPT.helpCenterId} { padding:0 !important; }
11795:             #${SCRIPT.helpCenterId} .mcms-help-window { width:100% !important; height:100% !important; min-height:100% !important; border:0 !important; border-radius:0 !important; }
11796:             #${SCRIPT.helpCenterId} .mcms-help-toolbar { min-height:58px !important; padding-top:calc(8px + env(safe-area-inset-top)) !important; }
```

### Lines 11788-11798
```text
11788:         }
11789:         #${SCRIPT.helpCenterId} .mcms-help-error-card strong { display:block !important; font-size:18px !important; }
11790:         #${SCRIPT.helpCenterId} .mcms-help-error-card p { margin:9px 0 16px !important; color:#9db5c1 !important; font-size:11px !important; line-height:1.45 !important; }
11791:         #${SCRIPT.helpCenterId} .mcms-help-error-actions { display:flex !important; justify-content:center !important; flex-wrap:wrap !important; gap:8px !important; }
11792:         #${SCRIPT.helpCenterId} .mcms-help-error-actions button { min-height:38px !important; padding:0 14px !important; border:1px solid #4286a5 !important; border-radius:9px !important; background:#12384b !important; color:#fff !important; cursor:pointer !important; font-size:11px !important; font-weight:900 !important; }
11793:         @media (max-width:760px) {
11794:             #${SCRIPT.helpCenterId} { padding:0 !important; }
11795:             #${SCRIPT.helpCenterId} .mcms-help-window { width:100% !important; height:100% !important; min-height:100% !important; border:0 !important; border-radius:0 !important; }
11796:             #${SCRIPT.helpCenterId} .mcms-help-toolbar { min-height:58px !important; padding-top:calc(8px + env(safe-area-inset-top)) !important; }
11797:             #${SCRIPT.helpCenterId} .mcms-help-brand-copy small { display:none !important; }
11798:             #${SCRIPT.helpCenterId} .mcms-help-action { min-width:40px !important; width:40px !important; padding:0 !important; }
```

### Lines 11798-11808
```text
11798:             #${SCRIPT.helpCenterId} .mcms-help-action { min-width:40px !important; width:40px !important; padding:0 !important; }
11799:             #${SCRIPT.helpCenterId} .mcms-help-source { display:none !important; }
11800:             #${SCRIPT.helpCenterId} .mcms-help-address { padding-left:8px !important; padding-right:8px !important; }
11801:             #${SCRIPT.helpCenterId} .mcms-help-address-text { font-size:8px !important; }
11802:         }
11803:         @media (prefers-reduced-motion:reduce) {
11804:             #${SCRIPT.helpCenterId}.mcms-loading .mcms-help-progress::before { animation:none !important; width:100% !important; }
11805:         }
11806: 
11807:         /* v4.4.2 Tablet command-panel stacking and cohesive sticky navigation.
11808:            The header and tab strip now move as one sticky unit, preventing the
```

### Lines 11810-11820
```text
11810:            the open Tablet Command Panel. */
11811:         #${SCRIPT.panelId} .mcms-panel-sticky-stack {
11812:             position:relative !important;
11813:             min-width:0 !important;
11814:         }
11815:         html[data-mcms-tablet-active="true"] #${SCRIPT.panelId}.mcms-open {
11816:             z-index:1040 !important;
11817:             isolation:isolate !important;
11818:         }
11819:         html[data-mcms-tablet-active="true"] #${SCRIPT.criticalDrawerId}.mcms-open {
11820:             z-index:1035 !important;
```

### Lines 11814-11824
```text
11814:         }
11815:         html[data-mcms-tablet-active="true"] #${SCRIPT.panelId}.mcms-open {
11816:             z-index:1040 !important;
11817:             isolation:isolate !important;
11818:         }
11819:         html[data-mcms-tablet-active="true"] #${SCRIPT.criticalDrawerId}.mcms-open {
11820:             z-index:1035 !important;
11821:         }
11822:         html[data-mcms-tablet-active="true"] #${SCRIPT.panelId} .mcms-panel-sticky-stack {
11823:             position:sticky !important;
11824:             top:-12px !important;
```

### Lines 11817-11827
```text
11817:             isolation:isolate !important;
11818:         }
11819:         html[data-mcms-tablet-active="true"] #${SCRIPT.criticalDrawerId}.mcms-open {
11820:             z-index:1035 !important;
11821:         }
11822:         html[data-mcms-tablet-active="true"] #${SCRIPT.panelId} .mcms-panel-sticky-stack {
11823:             position:sticky !important;
11824:             top:-12px !important;
11825:             z-index:24 !important;
11826:             margin:-12px -12px 12px !important;
11827:             padding:0 12px !important;
```

### Lines 11827-11837
```text
11827:             padding:0 12px !important;
11828:             background:rgba(8,12,18,.995) !important;
11829:             border-bottom:1px solid rgba(255,255,255,.13) !important;
11830:             box-shadow:0 8px 14px rgba(0,0,0,.24) !important;
11831:         }
11832:         html[data-mcms-tablet-active="true"] #${SCRIPT.panelId} .mcms-panel-sticky-stack .mcms-header {
11833:             position:relative !important;
11834:             top:auto !important;
11835:             z-index:2 !important;
11836:             margin:0 -12px !important;
11837:             padding:10px 12px 9px !important;
```

### Lines 11835-11845
```text
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
```

### Lines 11863-11873
```text
11863:         #${SCRIPT.controlId} .mcms-economy-btn:focus-visible { background:rgba(43,92,38,.88) !important; color:#fff !important; border-color:#9ee58a !important; }
11864:         #${SCRIPT.controlId} .mcms-economy-btn.mcms-on {
11865:             background:linear-gradient(180deg,#2f8f45,#176329) !important; color:#fff !important; border-color:#b9f5a7 !important;
11866:             box-shadow:0 0 0 2px rgba(155,235,130,.17),0 5px 16px rgba(0,0,0,.25) !important;
11867:         }
11868:         html[data-mcms-tablet-active="true"] #${SCRIPT.controlId} { grid-template-columns:109px minmax(0,1fr) !important; }
11869:         html[data-mcms-tablet-active="true"] #${SCRIPT.controlId} .mcms-launch-row { grid-area:menu !important; width:109px !important; gap:5px !important; }
11870:         html[data-mcms-tablet-active="true"] #${SCRIPT.controlId} .mcms-shell { grid-area:auto !important; width:52px !important; }
11871:         html[data-mcms-tablet-active="true"] #${SCRIPT.controlId} .mcms-economy-btn { width:52px !important; height:48px !important; border-radius:13px !important; }
11872:         html[data-mcms-command-bar-open="false"][data-mcms-tablet-active="true"] #${SCRIPT.controlId} {
11873:             width:109px !important; max-width:109px !important; grid-template-columns:109px !important; grid-template-areas:"menu" !important;
```

### Lines 11864-11874
```text
11864:         #${SCRIPT.controlId} .mcms-economy-btn.mcms-on {
11865:             background:linear-gradient(180deg,#2f8f45,#176329) !important; color:#fff !important; border-color:#b9f5a7 !important;
11866:             box-shadow:0 0 0 2px rgba(155,235,130,.17),0 5px 16px rgba(0,0,0,.25) !important;
11867:         }
11868:         html[data-mcms-tablet-active="true"] #${SCRIPT.controlId} { grid-template-columns:109px minmax(0,1fr) !important; }
11869:         html[data-mcms-tablet-active="true"] #${SCRIPT.controlId} .mcms-launch-row { grid-area:menu !important; width:109px !important; gap:5px !important; }
11870:         html[data-mcms-tablet-active="true"] #${SCRIPT.controlId} .mcms-shell { grid-area:auto !important; width:52px !important; }
11871:         html[data-mcms-tablet-active="true"] #${SCRIPT.controlId} .mcms-economy-btn { width:52px !important; height:48px !important; border-radius:13px !important; }
11872:         html[data-mcms-command-bar-open="false"][data-mcms-tablet-active="true"] #${SCRIPT.controlId} {
11873:             width:109px !important; max-width:109px !important; grid-template-columns:109px !important; grid-template-areas:"menu" !important;
11874:         }
```

### Lines 11865-11875
```text
11865:             background:linear-gradient(180deg,#2f8f45,#176329) !important; color:#fff !important; border-color:#b9f5a7 !important;
11866:             box-shadow:0 0 0 2px rgba(155,235,130,.17),0 5px 16px rgba(0,0,0,.25) !important;
11867:         }
11868:         html[data-mcms-tablet-active="true"] #${SCRIPT.controlId} { grid-template-columns:109px minmax(0,1fr) !important; }
11869:         html[data-mcms-tablet-active="true"] #${SCRIPT.controlId} .mcms-launch-row { grid-area:menu !important; width:109px !important; gap:5px !important; }
11870:         html[data-mcms-tablet-active="true"] #${SCRIPT.controlId} .mcms-shell { grid-area:auto !important; width:52px !important; }
11871:         html[data-mcms-tablet-active="true"] #${SCRIPT.controlId} .mcms-economy-btn { width:52px !important; height:48px !important; border-radius:13px !important; }
11872:         html[data-mcms-command-bar-open="false"][data-mcms-tablet-active="true"] #${SCRIPT.controlId} {
11873:             width:109px !important; max-width:109px !important; grid-template-columns:109px !important; grid-template-areas:"menu" !important;
11874:         }
11875:         html[data-mcms-mobile-active="true"] #${SCRIPT.controlId} .mcms-launch-row { display:contents !important; }
```

### Lines 11866-11876
```text
11866:             box-shadow:0 0 0 2px rgba(155,235,130,.17),0 5px 16px rgba(0,0,0,.25) !important;
11867:         }
11868:         html[data-mcms-tablet-active="true"] #${SCRIPT.controlId} { grid-template-columns:109px minmax(0,1fr) !important; }
11869:         html[data-mcms-tablet-active="true"] #${SCRIPT.controlId} .mcms-launch-row { grid-area:menu !important; width:109px !important; gap:5px !important; }
11870:         html[data-mcms-tablet-active="true"] #${SCRIPT.controlId} .mcms-shell { grid-area:auto !important; width:52px !important; }
11871:         html[data-mcms-tablet-active="true"] #${SCRIPT.controlId} .mcms-economy-btn { width:52px !important; height:48px !important; border-radius:13px !important; }
11872:         html[data-mcms-command-bar-open="false"][data-mcms-tablet-active="true"] #${SCRIPT.controlId} {
11873:             width:109px !important; max-width:109px !important; grid-template-columns:109px !important; grid-template-areas:"menu" !important;
11874:         }
11875:         html[data-mcms-mobile-active="true"] #${SCRIPT.controlId} .mcms-launch-row { display:contents !important; }
11876:         html[data-mcms-mobile-active="true"] #${SCRIPT.controlId} .mcms-economy-btn {
```

### Lines 11867-11877
```text
11867:         }
11868:         html[data-mcms-tablet-active="true"] #${SCRIPT.controlId} { grid-template-columns:109px minmax(0,1fr) !important; }
11869:         html[data-mcms-tablet-active="true"] #${SCRIPT.controlId} .mcms-launch-row { grid-area:menu !important; width:109px !important; gap:5px !important; }
11870:         html[data-mcms-tablet-active="true"] #${SCRIPT.controlId} .mcms-shell { grid-area:auto !important; width:52px !important; }
11871:         html[data-mcms-tablet-active="true"] #${SCRIPT.controlId} .mcms-economy-btn { width:52px !important; height:48px !important; border-radius:13px !important; }
11872:         html[data-mcms-command-bar-open="false"][data-mcms-tablet-active="true"] #${SCRIPT.controlId} {
11873:             width:109px !important; max-width:109px !important; grid-template-columns:109px !important; grid-template-areas:"menu" !important;
11874:         }
11875:         html[data-mcms-mobile-active="true"] #${SCRIPT.controlId} .mcms-launch-row { display:contents !important; }
11876:         html[data-mcms-mobile-active="true"] #${SCRIPT.controlId} .mcms-economy-btn {
11877:             width:auto !important; min-width:0 !important; height:var(--mcms-mobile-filter-height,44px) !important; border-radius:10px !important; pointer-events:auto !important;
```

### Lines 11868-11878
```text
11868:         html[data-mcms-tablet-active="true"] #${SCRIPT.controlId} { grid-template-columns:109px minmax(0,1fr) !important; }
11869:         html[data-mcms-tablet-active="true"] #${SCRIPT.controlId} .mcms-launch-row { grid-area:menu !important; width:109px !important; gap:5px !important; }
11870:         html[data-mcms-tablet-active="true"] #${SCRIPT.controlId} .mcms-shell { grid-area:auto !important; width:52px !important; }
11871:         html[data-mcms-tablet-active="true"] #${SCRIPT.controlId} .mcms-economy-btn { width:52px !important; height:48px !important; border-radius:13px !important; }
11872:         html[data-mcms-command-bar-open="false"][data-mcms-tablet-active="true"] #${SCRIPT.controlId} {
11873:             width:109px !important; max-width:109px !important; grid-template-columns:109px !important; grid-template-areas:"menu" !important;
11874:         }
11875:         html[data-mcms-mobile-active="true"] #${SCRIPT.controlId} .mcms-launch-row { display:contents !important; }
11876:         html[data-mcms-mobile-active="true"] #${SCRIPT.controlId} .mcms-economy-btn {
11877:             width:auto !important; min-width:0 !important; height:var(--mcms-mobile-filter-height,44px) !important; border-radius:10px !important; pointer-events:auto !important;
11878:         }
```

### Lines 11875-11885
```text
11875:         html[data-mcms-mobile-active="true"] #${SCRIPT.controlId} .mcms-launch-row { display:contents !important; }
11876:         html[data-mcms-mobile-active="true"] #${SCRIPT.controlId} .mcms-economy-btn {
11877:             width:auto !important; min-width:0 !important; height:var(--mcms-mobile-filter-height,44px) !important; border-radius:10px !important; pointer-events:auto !important;
11878:         }
11879:         html[data-mcms-command-bar-open="false"][data-mcms-mobile-active="true"] #${SCRIPT.controlId} {
11880:             width:104px !important; max-width:104px !important; grid-template-columns:50px 50px !important;
11881:         }
11882: 
11883:         html[data-mcms-economy="true"] .leaflet-tile-pane img.leaflet-tile { filter:none !important; }
11884:         html[data-mcms-economy="true"] .leaflet-fade-anim .leaflet-tile,
11885:         html[data-mcms-economy="true"] .leaflet-zoom-animated,
```

### Lines 11980-11990
```text
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
```

### Lines 11981-11991
```text
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
```

### Lines 12028-12038
```text
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
```

### Lines 12039-12049
```text
12039:         #${SCRIPT.criticalDrawerId} :is(button,input,select,[tabindex]):focus-visible, #${SCRIPT.vehicleStatusId} :is(button,input,select,[tabindex]):focus-visible,
12040:         #${SCRIPT.helpCenterId} :is(button,input,select,a,[tabindex]):focus-visible { outline:3px solid #8cddff !important; outline-offset:2px !important; }
12041:         #${SCRIPT.panelId} :is(button,input,select):disabled, #${SCRIPT.criticalDrawerId} :is(button,input,select):disabled,
12042:         #${SCRIPT.vehicleStatusId} :is(button,input,select):disabled { opacity:.55 !important; cursor:not-allowed !important; }
12043: 
12044:         html:not([data-mcms-tablet-active="true"]):not([data-mcms-mobile-active="true"]) #${SCRIPT.panelId} {
12045:             width:min(360px,calc(100vw - 24px)) !important; max-width:calc(100vw - 24px) !important;
12046:         }
12047:         html:not([data-mcms-tablet-active="true"]):not([data-mcms-mobile-active="true"]) #${SCRIPT.panelId} .mcms-header {
12048:             grid-template-columns:minmax(0,1fr) 32px 32px 32px !important; gap:6px !important; min-height:48px !important;
12049:         }
```

### Lines 12042-12052
```text
12042:         #${SCRIPT.vehicleStatusId} :is(button,input,select):disabled { opacity:.55 !important; cursor:not-allowed !important; }
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
```

### Lines 12043-12053
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
```

### Lines 12045-12055
```text
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
```

### Lines 12046-12056
```text
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
```

### Lines 12047-12057
```text
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
```

### Lines 12048-12058
```text
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
```

### Lines 12049-12059
```text
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
```

### Lines 12050-12060
```text
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
```

### Lines 12051-12061
```text
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
```

### Lines 12058-12068
```text
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
```

### Lines 12059-12069
```text
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
```

### Lines 12062-12072
```text
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
```

### Lines 12063-12073
```text
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
```

### Lines 12064-12074
```text
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
```

### Lines 12065-12075
```text
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
```

### Lines 12070-12080
```text
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
```

### Lines 12077-12087
```text
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
```

### Lines 12078-12088
```text
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
```

### Lines 12083-12093
```text
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
```

### Lines 12085-12095
```text
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
```

### Lines 12086-12096
```text
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
```

### Lines 12087-12097
```text
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
```

### Lines 12089-12099
```text
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
```

### Lines 12090-12100
```text
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
```

### Lines 12093-12103
```text
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
```

### Lines 12109-12119
```text
12109:             width:auto !important; max-width:min(320px,calc(100vw - 20px)) !important; transform:translateY(-6px) !important;
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
```

### Lines 12112-12122
```text
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
```

### Lines 12113-12123
```text
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
```

### Lines 12116-12126
```text
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
```

### Lines 12119-12129
```text
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
```

### Lines 12123-12133
```text
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
```

### Lines 12130-12140
```text
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
```

### Lines 12132-12142
```text
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
```

### Lines 12133-12143
```text
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
```

### Lines 12134-12144
```text
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
```

### Lines 12177-12187
```text
12177:         }
12178:         body .modal-backdrop { z-index:1190 !important; }
12179:         body .modal,
12180:         body .bootbox.modal,
12181:         body [role="dialog"][aria-modal="true"] { z-index:1200 !important; }
12182:         html[data-mcms-tablet-active="true"][data-mcms-ui-theme] #${SCRIPT.panelId} .mcms-reset-panel,
12183:         html[data-mcms-mobile-active="true"][data-mcms-ui-theme] #${SCRIPT.panelId} .mcms-reset-panel { display:none !important; }
12184: 
12185:         /* v4.9.0: compact Mission Age Watch Quick Views and Advanced Filters. */
12186:         #${SCRIPT.criticalDrawerId} .mcms-critical-filter-deck {
12187:             display:grid !important;
```

### Lines 12192-12202
```text
12192:             border-bottom:1px solid rgba(255,255,255,.12) !important;
12193:             background:rgba(4,9,13,.36) !important;
12194:         }
12195:         #${SCRIPT.criticalDrawerId} .mcms-critical-filter-overview {
12196:             display:grid !important;
12197:             grid-template-columns:minmax(0,1fr) auto auto !important;
12198:             align-items:center !important;
12199:             gap:8px !important;
12200:             min-width:0 !important;
12201:             min-height:34px !important;
12202:             padding:5px 7px !important;
```

### Lines 12214-12224
```text
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
```

### Lines 12215-12225
```text
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
```

### Lines 12220-12230
```text
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
```

### Lines 12253-12263
```text
12253:             font-size:5.2px !important;
12254:             letter-spacing:.12px !important;
12255:         }
12256:         #${SCRIPT.criticalDrawerId} .mcms-critical-quick-views {
12257:             display:grid !important;
12258:             grid-template-columns:repeat(6,minmax(58px,1fr)) !important;
12259:             gap:4px !important;
12260:         }
12261:         #${SCRIPT.criticalDrawerId} .mcms-critical-quick-view {
12262:             position:relative !important;
12263:             display:grid !important;
```

### Lines 12259-12269
```text
12259:             gap:4px !important;
12260:         }
12261:         #${SCRIPT.criticalDrawerId} .mcms-critical-quick-view {
12262:             position:relative !important;
12263:             display:grid !important;
12264:             grid-template-columns:minmax(0,1fr) auto !important;
12265:             align-items:center !important;
12266:             min-width:0 !important;
12267:             min-height:30px !important;
12268:             gap:4px !important;
12269:             padding:4px 7px !important;
```

### Lines 12275-12285
```text
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
```

### Lines 12277-12287
```text
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
```

### Lines 12303-12313
```text
12303:         #${SCRIPT.criticalDrawerId} .mcms-quick-stable { color:#a6edc1 !important; border-color:rgba(69,190,116,.48) !important; }
12304:         #${SCRIPT.criticalDrawerId} .mcms-quick-my-units { color:#f2e0a4 !important; border-color:rgba(220,196,119,.56) !important; }
12305: 
12306:         #${SCRIPT.criticalDrawerId} .mcms-critical-filter-deck .mcms-critical-category-filters {
12307:             display:grid !important;
12308:             grid-template-columns:62px repeat(4,minmax(64px,1fr)) !important;
12309:             gap:4px !important;
12310:             margin:0 !important;
12311:         }
12312:         #${SCRIPT.criticalDrawerId} .mcms-critical-filter-deck .mcms-critical-category-filter {
12313:             min-height:28px !important;
```

### Lines 12317-12327
```text
12317:         #${SCRIPT.criticalDrawerId} .mcms-critical-filter-deck .mcms-critical-category-filter i { font-size:5.8px !important; }
12318: 
12319:         #${SCRIPT.criticalDrawerId} .mcms-critical-advanced-shell { display:grid !important; gap:4px !important; }
12320:         #${SCRIPT.criticalDrawerId} .mcms-critical-advanced-toggle {
12321:             display:grid !important;
12322:             grid-template-columns:minmax(0,1fr) auto !important;
12323:             align-items:center !important;
12324:             width:100% !important;
12325:             min-height:31px !important;
12326:             gap:8px !important;
12327:             padding:5px 8px !important;
```

### Lines 12337-12347
```text
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
```

### Lines 12338-12348
```text
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
```

### Lines 12355-12365
```text
12355:             background:rgba(5,15,21,.76) !important;
12356:         }
12357:         #${SCRIPT.criticalDrawerId} .mcms-critical-advanced-panel[hidden] { display:none !important; }
12358:         #${SCRIPT.criticalDrawerId} .mcms-critical-advanced-panel .mcms-critical-summary {
12359:             display:grid !important;
12360:             grid-template-columns:1fr !important;
12361:             gap:7px !important;
12362:             margin:0 !important;
12363:         }
12364:         #${SCRIPT.criticalDrawerId} .mcms-critical-advanced-group { display:grid !important; gap:4px !important; }
12365:         #${SCRIPT.criticalDrawerId} .mcms-critical-advanced-status-grid {
```

### Lines 12362-12372
```text
12362:             margin:0 !important;
12363:         }
12364:         #${SCRIPT.criticalDrawerId} .mcms-critical-advanced-group { display:grid !important; gap:4px !important; }
12365:         #${SCRIPT.criticalDrawerId} .mcms-critical-advanced-status-grid {
12366:             display:grid !important;
12367:             grid-template-columns:repeat(6,minmax(56px,1fr)) !important;
12368:             gap:4px !important;
12369:         }
12370:         #${SCRIPT.criticalDrawerId} .mcms-critical-advanced-condition-grid {
12371:             display:grid !important;
12372:             grid-template-columns:repeat(2,minmax(0,1fr)) !important;
```

### Lines 12367-12377
```text
12367:             grid-template-columns:repeat(6,minmax(56px,1fr)) !important;
12368:             gap:4px !important;
12369:         }
12370:         #${SCRIPT.criticalDrawerId} .mcms-critical-advanced-condition-grid {
12371:             display:grid !important;
12372:             grid-template-columns:repeat(2,minmax(0,1fr)) !important;
12373:             gap:4px !important;
12374:         }
12375:         #${SCRIPT.criticalDrawerId} .mcms-critical-advanced-panel .mcms-critical-summary-card {
12376:             min-height:31px !important;
12377:             padding:5px 7px !important;
```

### Lines 12381-12391
```text
12381:         #${SCRIPT.criticalDrawerId} .mcms-summary-attention { border-color:rgba(255,151,53,.72) !important; color:#ffc17d !important; }
12382:         #${SCRIPT.criticalDrawerId} .mcms-summary-attention.mcms-filter-active { background:rgba(99,44,4,.90) !important; }
12383: 
12384:         #${SCRIPT.criticalDrawerId} .mcms-drawer-list { margin-top:5px !important; }
12385: 
12386:         html[data-mcms-tablet-active="true"] #${SCRIPT.criticalDrawerId} .mcms-critical-quick-views,
12387:         html[data-mcms-tablet-active="true"] #${SCRIPT.criticalDrawerId} .mcms-critical-advanced-status-grid {
12388:             grid-template-columns:repeat(3,minmax(0,1fr)) !important;
12389:         }
12390:         html[data-mcms-tablet-active="true"] #${SCRIPT.criticalDrawerId} .mcms-critical-filter-deck .mcms-critical-category-filters {
12391:             grid-template-columns:repeat(4,minmax(0,1fr)) !important;
```

### Lines 12382-12392
```text
12382:         #${SCRIPT.criticalDrawerId} .mcms-summary-attention.mcms-filter-active { background:rgba(99,44,4,.90) !important; }
12383: 
12384:         #${SCRIPT.criticalDrawerId} .mcms-drawer-list { margin-top:5px !important; }
12385: 
12386:         html[data-mcms-tablet-active="true"] #${SCRIPT.criticalDrawerId} .mcms-critical-quick-views,
12387:         html[data-mcms-tablet-active="true"] #${SCRIPT.criticalDrawerId} .mcms-critical-advanced-status-grid {
12388:             grid-template-columns:repeat(3,minmax(0,1fr)) !important;
12389:         }
12390:         html[data-mcms-tablet-active="true"] #${SCRIPT.criticalDrawerId} .mcms-critical-filter-deck .mcms-critical-category-filters {
12391:             grid-template-columns:repeat(4,minmax(0,1fr)) !important;
12392:         }
```

### Lines 12383-12393
```text
12383: 
12384:         #${SCRIPT.criticalDrawerId} .mcms-drawer-list { margin-top:5px !important; }
12385: 
12386:         html[data-mcms-tablet-active="true"] #${SCRIPT.criticalDrawerId} .mcms-critical-quick-views,
12387:         html[data-mcms-tablet-active="true"] #${SCRIPT.criticalDrawerId} .mcms-critical-advanced-status-grid {
12388:             grid-template-columns:repeat(3,minmax(0,1fr)) !important;
12389:         }
12390:         html[data-mcms-tablet-active="true"] #${SCRIPT.criticalDrawerId} .mcms-critical-filter-deck .mcms-critical-category-filters {
12391:             grid-template-columns:repeat(4,minmax(0,1fr)) !important;
12392:         }
12393:         html[data-mcms-tablet-active="true"] #${SCRIPT.criticalDrawerId} .mcms-critical-filter-deck .mcms-critical-category-label {
```

### Lines 12385-12395
```text
12385: 
12386:         html[data-mcms-tablet-active="true"] #${SCRIPT.criticalDrawerId} .mcms-critical-quick-views,
12387:         html[data-mcms-tablet-active="true"] #${SCRIPT.criticalDrawerId} .mcms-critical-advanced-status-grid {
12388:             grid-template-columns:repeat(3,minmax(0,1fr)) !important;
12389:         }
12390:         html[data-mcms-tablet-active="true"] #${SCRIPT.criticalDrawerId} .mcms-critical-filter-deck .mcms-critical-category-filters {
12391:             grid-template-columns:repeat(4,minmax(0,1fr)) !important;
12392:         }
12393:         html[data-mcms-tablet-active="true"] #${SCRIPT.criticalDrawerId} .mcms-critical-filter-deck .mcms-critical-category-label {
12394:             grid-column:1 / -1 !important;
12395:             min-height:16px !important;
```

### Lines 12386-12396
```text
12386:         html[data-mcms-tablet-active="true"] #${SCRIPT.criticalDrawerId} .mcms-critical-quick-views,
12387:         html[data-mcms-tablet-active="true"] #${SCRIPT.criticalDrawerId} .mcms-critical-advanced-status-grid {
12388:             grid-template-columns:repeat(3,minmax(0,1fr)) !important;
12389:         }
12390:         html[data-mcms-tablet-active="true"] #${SCRIPT.criticalDrawerId} .mcms-critical-filter-deck .mcms-critical-category-filters {
12391:             grid-template-columns:repeat(4,minmax(0,1fr)) !important;
12392:         }
12393:         html[data-mcms-tablet-active="true"] #${SCRIPT.criticalDrawerId} .mcms-critical-filter-deck .mcms-critical-category-label {
12394:             grid-column:1 / -1 !important;
12395:             min-height:16px !important;
12396:         }
```

### Lines 12388-12398
```text
12388:             grid-template-columns:repeat(3,minmax(0,1fr)) !important;
12389:         }
12390:         html[data-mcms-tablet-active="true"] #${SCRIPT.criticalDrawerId} .mcms-critical-filter-deck .mcms-critical-category-filters {
12391:             grid-template-columns:repeat(4,minmax(0,1fr)) !important;
12392:         }
12393:         html[data-mcms-tablet-active="true"] #${SCRIPT.criticalDrawerId} .mcms-critical-filter-deck .mcms-critical-category-label {
12394:             grid-column:1 / -1 !important;
12395:             min-height:16px !important;
12396:         }
12397:         html[data-mcms-mobile-active="true"] #${SCRIPT.criticalDrawerId} .mcms-critical-filter-deck { padding:5px !important; }
12398:         html[data-mcms-mobile-active="true"] #${SCRIPT.criticalDrawerId} .mcms-critical-filter-overview {
```

### Lines 12394-12404
```text
12394:             grid-column:1 / -1 !important;
12395:             min-height:16px !important;
12396:         }
12397:         html[data-mcms-mobile-active="true"] #${SCRIPT.criticalDrawerId} .mcms-critical-filter-deck { padding:5px !important; }
12398:         html[data-mcms-mobile-active="true"] #${SCRIPT.criticalDrawerId} .mcms-critical-filter-overview {
12399:             grid-template-columns:minmax(0,1fr) auto !important;
12400:         }
12401:         html[data-mcms-mobile-active="true"] #${SCRIPT.criticalDrawerId} .mcms-critical-filter-overview-count { grid-column:1 / 2 !important; }
12402:         html[data-mcms-mobile-active="true"] #${SCRIPT.criticalDrawerId} .mcms-critical-filter-overview button { grid-column:2 / 3 !important; grid-row:1 / 3 !important; }
12403:         html[data-mcms-mobile-active="true"] #${SCRIPT.criticalDrawerId} .mcms-critical-quick-views,
12404:         html[data-mcms-mobile-active="true"] #${SCRIPT.criticalDrawerId} .mcms-critical-advanced-status-grid,
```

### Lines 12401-12411
```text
12401:         html[data-mcms-mobile-active="true"] #${SCRIPT.criticalDrawerId} .mcms-critical-filter-overview-count { grid-column:1 / 2 !important; }
12402:         html[data-mcms-mobile-active="true"] #${SCRIPT.criticalDrawerId} .mcms-critical-filter-overview button { grid-column:2 / 3 !important; grid-row:1 / 3 !important; }
12403:         html[data-mcms-mobile-active="true"] #${SCRIPT.criticalDrawerId} .mcms-critical-quick-views,
12404:         html[data-mcms-mobile-active="true"] #${SCRIPT.criticalDrawerId} .mcms-critical-advanced-status-grid,
12405:         html[data-mcms-mobile-active="true"] #${SCRIPT.criticalDrawerId} .mcms-critical-advanced-condition-grid {
12406:             grid-template-columns:repeat(2,minmax(0,1fr)) !important;
12407:         }
12408:         html[data-mcms-mobile-active="true"] #${SCRIPT.criticalDrawerId} .mcms-critical-filter-deck .mcms-critical-category-filters {
12409:             grid-template-columns:repeat(2,minmax(0,1fr)) !important;
12410:         }
12411:         html[data-mcms-mobile-active="true"] #${SCRIPT.criticalDrawerId} .mcms-critical-filter-deck .mcms-critical-category-label { grid-column:1 / -1 !important; }
```

### Lines 12404-12414
```text
12404:         html[data-mcms-mobile-active="true"] #${SCRIPT.criticalDrawerId} .mcms-critical-advanced-status-grid,
12405:         html[data-mcms-mobile-active="true"] #${SCRIPT.criticalDrawerId} .mcms-critical-advanced-condition-grid {
12406:             grid-template-columns:repeat(2,minmax(0,1fr)) !important;
12407:         }
12408:         html[data-mcms-mobile-active="true"] #${SCRIPT.criticalDrawerId} .mcms-critical-filter-deck .mcms-critical-category-filters {
12409:             grid-template-columns:repeat(2,minmax(0,1fr)) !important;
12410:         }
12411:         html[data-mcms-mobile-active="true"] #${SCRIPT.criticalDrawerId} .mcms-critical-filter-deck .mcms-critical-category-label { grid-column:1 / -1 !important; }
12412:         html[data-mcms-economy="true"] #${SCRIPT.criticalDrawerId} .mcms-critical-quick-view,
12413:         html[data-mcms-economy="true"] #${SCRIPT.criticalDrawerId} .mcms-critical-advanced-toggle,
12414:         html[data-mcms-economy="true"] #${SCRIPT.criticalDrawerId} .mcms-critical-advanced-toggle i {
```

### Lines 12493-12503
```text
12493:                 radial-gradient(circle at 90% 10%,rgba(214,182,95,.13),transparent 31%),
12494:                 linear-gradient(145deg,#20242a,#07080a 69%) !important;
12495:             color:#f2ecdd !important;
12496:             box-shadow:0 24px 64px rgba(0,0,0,.72),inset 0 0 0 1px rgba(255,255,255,.04),0 0 22px rgba(172,135,46,.14) !important;
12497:         }
12498:         html:not([data-mcms-tablet-active="true"]):not([data-mcms-mobile-active="true"])[data-mcms-ui-theme="bond007"] #${SCRIPT.panelId} {
12499:             width:min(420px,calc(100vw - 24px)) !important;
12500:         }
12501:         html[data-mcms-ui-theme="bond007"] #${SCRIPT.panelId} .mcms-header {
12502:             min-height:62px !important;
12503:             padding-right:10px !important;
```

### Lines 12502-12512
```text
12502:             min-height:62px !important;
12503:             padding-right:10px !important;
12504:             border-bottom:1px solid rgba(231,205,127,.72) !important;
12505:             background:linear-gradient(90deg,rgba(255,255,255,.075),rgba(255,255,255,.012) 55%,rgba(214,182,95,.045)) !important;
12506:         }
12507:         html:not([data-mcms-tablet-active="true"]):not([data-mcms-mobile-active="true"])[data-mcms-ui-theme="bond007"] #${SCRIPT.panelId} .mcms-header::before {
12508:             right:122px !important;
12509:             top:15px !important;
12510:             width:62px !important;
12511:             height:27px !important;
12512:             background-image:url("${THEME_ASSETS.bond007Logo}") !important;
```

### Lines 12538-12548
```text
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
```

### Lines 12539-12549
```text
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
```

### Lines 12547-12557
```text
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
```

### Lines 12548-12558
```text
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
```

### Lines 12551-12561
```text
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
```

### Lines 12558-12568
```text
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
```

### Lines 12569-12579
```text
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
```

### Lines 12580-12590
```text
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
```

### Lines 12581-12591
```text
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
```

### Lines 12583-12593
```text
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
```

### Lines 12591-12601
```text
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
```

### Lines 12603-12613
```text
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
```

### Lines 12605-12615
```text
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
```

### Lines 12773-12783
```text
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
```

### Lines 12774-12784
```text
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
```

### Lines 12788-12798
```text
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
```

### Lines 12789-12799
```text
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
```

### Lines 12836-12846
```text
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
```

### Lines 12908-12918
```text
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
```

### Lines 12909-12919
```text
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
```

### Lines 12991-13001
```text
12991:         @keyframes mcmsBondAssetBarrel {
12992:             from { transform:translate(-50%,-50%) rotate(-7deg); }
12993:             to { transform:translate(-50%,-50%) rotate(353deg); }
12994:         }
12995: 
12996:         html[data-mcms-tablet-active="true"][data-mcms-ui-theme="bond007"] #${SCRIPT.panelId} .mcms-header {
12997:             background:
12998:                 url("${THEME_ASSETS.bond007CommandSeal}") right 184px center/38px auto no-repeat,
12999:                 linear-gradient(90deg,rgba(255,255,255,.075),rgba(255,255,255,.012) 55%,rgba(214,182,95,.045)) !important;
13000:         }
13001:         html[data-mcms-tablet-active="true"][data-mcms-ui-theme="bond007"] #${SCRIPT.panelId} .mcms-header::before {
```

### Lines 12996-13006
```text
12996:         html[data-mcms-tablet-active="true"][data-mcms-ui-theme="bond007"] #${SCRIPT.panelId} .mcms-header {
12997:             background:
12998:                 url("${THEME_ASSETS.bond007CommandSeal}") right 184px center/38px auto no-repeat,
12999:                 linear-gradient(90deg,rgba(255,255,255,.075),rgba(255,255,255,.012) 55%,rgba(214,182,95,.045)) !important;
13000:         }
13001:         html[data-mcms-tablet-active="true"][data-mcms-ui-theme="bond007"] #${SCRIPT.panelId} .mcms-header::before {
13002:             display:block !important;
13003:             right:113px !important;
13004:             top:14px !important;
13005:             width:66px !important;
13006:             height:25px !important;
```

### Lines 13009-13019
```text
13009:             background-position:center !important;
13010:             background-repeat:no-repeat !important;
13011:             filter:invert(1) sepia(.24) saturate(.68) brightness(1.3) !important;
13012:             opacity:.88 !important;
13013:         }
13014:         html[data-mcms-tablet-active="true"][data-mcms-ui-theme="bond007"] #${SCRIPT.panelId} .mcms-drag-handle {
13015:             padding-right:146px !important;
13016:         }
13017: 
13018:         html[data-mcms-mobile-active="true"][data-mcms-ui-theme="bond007"] #${SCRIPT.panelId} .mcms-header {
13019:             min-height:58px !important;
```

### Lines 13026-13036
```text
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
```

### Lines 13031-13041
```text
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
```

### Lines 13066-13076
```text
13066:             background-size:30px auto,auto !important;
13067:             background-position:6px center,center !important;
13068:             font-size:7px !important;
13069:         }
13070: 
13071:         @media (max-width:980px) {
13072:             #${SCRIPT.payoutFlashId}[data-template="jamesBond"] .mcms-payout-theme-fx-b {
13073:                 right:4px !important;
13074:                 width:clamp(165px,27vw,245px) !important;
13075:                 height:70% !important;
13076:                 opacity:.92 !important;
```

### Lines 13074-13084
```text
13074:                 width:clamp(165px,27vw,245px) !important;
13075:                 height:70% !important;
13076:                 opacity:.92 !important;
13077:             }
13078:         }
13079:         @media (max-width:700px) {
13080:             #${SCRIPT.payoutFlashId}[data-template="jamesBond"] .mcms-payout-theme-fx-b { display:none !important; }
13081:             #${SCRIPT.payoutFlashId}[data-template="jamesBond"] .mcms-payout-banner {
13082:                 width:calc(100% - 20px) !important;
13083:                 min-height:0 !important;
13084:                 padding:44px 18px 23px !important;
```

### Lines 13141-13151
```text
13141:             pointer-events:none !important;
13142:         }
13143:         #${SCRIPT.payoutFlashId}[data-template="jamesBond"] .mcms-payout-banner {
13144:             isolation:isolate !important;
13145:         }
13146:         @media (max-height:640px) and (min-width:701px) {
13147:             #${SCRIPT.payoutFlashId}[data-template="jamesBond"] .mcms-payout-theme-fx-b {
13148:                 height:72% !important;
13149:                 width:clamp(150px,20vw,250px) !important;
13150:             }
13151:         }
```

### Lines 13159-13169
```text
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
```

### Lines 13163-13173
```text
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
```

### Lines 13164-13174
```text
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
```

### Lines 13178-13188
```text
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
```

### Lines 13179-13189
```text
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
```

### Lines 13181-13191
```text
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
```

### Lines 13196-13206
```text
13196:                 font-size:7px !important;
13197:                 letter-spacing:.75px !important;
13198:             }
13199:         }
13200: 
13201:         @media (prefers-reduced-motion:reduce) {
13202:             #${SCRIPT.payoutFlashId}[data-template="jamesBond"] .mcms-payout-theme-fx-a { animation:none !important; }
13203:         }
13204: 
13205:         /* v4.10.2: translucent 007 dossier with a protected reading field and portrait reveal zone. */
13206:         #${SCRIPT.payoutFlashId}[data-template="jamesBond"] .mcms-payout-theme-fx-b {
```

### Lines 13254-13264
```text
13254:         #${SCRIPT.payoutFlashId}[data-template="jamesBond"] .mcms-payout-mission,
13255:         #${SCRIPT.payoutFlashId}[data-template="jamesBond"] .mcms-payout-amount {
13256:             text-shadow:0 1px rgba(255,255,255,.92),0 2px 8px rgba(247,242,228,.70) !important;
13257:         }
13258: 
13259:         @media (max-width:980px) and (min-width:701px) {
13260:             #${SCRIPT.payoutFlashId}[data-template="jamesBond"] .mcms-payout-theme-fx-b {
13261:                 right:max(0px,calc(50% - 330px)) !important;
13262:                 width:clamp(190px,28vw,270px) !important;
13263:                 height:82% !important;
13264:             }
```

### Lines 13282-13292
```text
13282:             #${SCRIPT.payoutFlashId}[data-template="jamesBond"] .mcms-payout-banner::after {
13283:                 right:238px !important;
13284:             }
13285:         }
13286: 
13287:         @media (max-width:700px) {
13288:             #${SCRIPT.payoutFlashId}[data-template="jamesBond"] .mcms-payout-theme-fx-b {
13289:                 display:none !important;
13290:             }
13291:             #${SCRIPT.payoutFlashId}[data-template="jamesBond"] .mcms-payout-banner {
13292:                 width:calc(100% - 20px) !important;
```

### Lines 13305-13315
```text
13305:             #${SCRIPT.payoutFlashId}[data-template="jamesBond"] .mcms-payout-banner::after {
13306:                 right:15px !important;
13307:             }
13308:         }
13309: 
13310:         @media (max-height:640px) and (min-width:701px) {
13311:             #${SCRIPT.payoutFlashId}[data-template="jamesBond"] .mcms-payout-theme-fx-b {
13312:                 height:76% !important;
13313:                 width:clamp(190px,24vw,290px) !important;
13314:             }
13315:             #${SCRIPT.payoutFlashId}[data-template="jamesBond"] .mcms-payout-banner {
```

### Lines 13367-13377
```text
13367:         #${SCRIPT.payoutFlashId}.mcms-payout-controls-safe[data-template="jamesBond"] .mcms-payout-theme-fx-b {
13368:             bottom:var(--mcms-payout-safe-bottom-offset,-2%) !important;
13369:             height:min(72%,var(--mcms-payout-safe-height,700px)) !important;
13370:             width:clamp(185px,24vw,300px) !important;
13371:         }
13372:         @media (max-width:980px) and (min-width:701px) {
13373:             #${SCRIPT.payoutFlashId}.mcms-payout-controls-safe[data-template="jamesBond"] .mcms-payout-banner {
13374:                 padding:33px clamp(205px,29vw,238px) 17px 28px !important;
13375:             }
13376:             #${SCRIPT.payoutFlashId}.mcms-payout-controls-safe[data-template="jamesBond"] .mcms-payout-theme-fx-b {
13377:                 width:clamp(165px,25vw,235px) !important;
```

### Lines 13385-13395
```text
13385:         }
13386:         #${SCRIPT.payoutFlashId}.mcms-payout-controls-safe[data-template="jamesBond"] .mcms-payout-theme-fx-b {
13387:             bottom:calc(var(--mcms-payout-safe-bottom-offset,-2%) - clamp(42px,6vh,58px)) !important;
13388:             height:min(82%,calc(var(--mcms-payout-safe-height,700px) + 54px)) !important;
13389:         }
13390:         @media (max-width:980px) and (min-width:701px) {
13391:             #${SCRIPT.payoutFlashId}[data-template="jamesBond"] .mcms-payout-theme-fx-b {
13392:                 bottom:-6% !important;
13393:                 height:90% !important;
13394:             }
13395:             #${SCRIPT.payoutFlashId}.mcms-payout-controls-safe[data-template="jamesBond"] .mcms-payout-theme-fx-b {
```

### Lines 13396-13406
```text
13396:                 bottom:calc(var(--mcms-payout-safe-bottom-offset,-2%) - clamp(26px,4vh,34px)) !important;
13397:                 width:clamp(190px,34vw,255px) !important;
13398:                 height:min(82%,calc(var(--mcms-payout-safe-height,700px) + 34px)) !important;
13399:             }
13400:         }
13401:         @media (max-width:700px) {
13402:             #${SCRIPT.payoutFlashId}[data-template="jamesBond"] .mcms-payout-theme-fx-b {
13403:                 display:none !important;
13404:             }
13405:         }
13406: 
```

### Lines 13405-13415
```text
13405:         }
13406: 
13407:         /* v4.11.0: compact Smart Bookmark Labels; theme colours and artwork remain untouched. */
13408:         #${SCRIPT.controlId} .mcms-screen-pins {
13409:             display:flex !important;
13410:             flex-wrap:wrap !important;
13411:             grid-template-columns:none !important;
13412:             align-items:center !important;
13413:             align-content:flex-start !important;
13414:             justify-content:flex-start !important;
13415:             gap:5px !important;
```

### Lines 13406-13416
```text
13406: 
13407:         /* v4.11.0: compact Smart Bookmark Labels; theme colours and artwork remain untouched. */
13408:         #${SCRIPT.controlId} .mcms-screen-pins {
13409:             display:flex !important;
13410:             flex-wrap:wrap !important;
13411:             grid-template-columns:none !important;
13412:             align-items:center !important;
13413:             align-content:flex-start !important;
13414:             justify-content:flex-start !important;
13415:             gap:5px !important;
13416:             width:auto !important;
```

### Lines 13428-13438
```text
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
```

### Lines 13430-13440
```text
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
```

### Lines 13449-13459
```text
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
```

### Lines 13456-13466
```text
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
```

### Lines 13457-13467
```text
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
```

### Lines 13467-13477
```text
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
```

### Lines 13469-13479
```text
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
```

### Lines 13475-13485
```text
13475:         }
13476:         #${SCRIPT.panelId} .mcms-bookmark-name-btn:hover .mcms-bookmark-name-main,
13477:         #${SCRIPT.panelId} .mcms-bookmark-name-btn:focus-visible .mcms-bookmark-name-main {
13478:             text-decoration:underline !important;
13479:         }
13480:         html[data-mcms-tablet-active="true"] #${SCRIPT.controlId} .mcms-screen-pins {
13481:             display:flex !important;
13482:             flex-wrap:wrap !important;
13483:             justify-content:flex-start !important;
13484:             align-items:center !important;
13485:             gap:5px !important;
```

### Lines 13477-13487
```text
13477:         #${SCRIPT.panelId} .mcms-bookmark-name-btn:focus-visible .mcms-bookmark-name-main {
13478:             text-decoration:underline !important;
13479:         }
13480:         html[data-mcms-tablet-active="true"] #${SCRIPT.controlId} .mcms-screen-pins {
13481:             display:flex !important;
13482:             flex-wrap:wrap !important;
13483:             justify-content:flex-start !important;
13484:             align-items:center !important;
13485:             gap:5px !important;
13486:             width:100% !important;
13487:             max-width:none !important;
```

### Lines 13486-13496
```text
13486:             width:100% !important;
13487:             max-width:none !important;
13488:             max-height:none !important;
13489:             overflow:visible !important;
13490:         }
13491:         html[data-mcms-tablet-active="true"] #${SCRIPT.controlId} .mcms-screen-pin-btn {
13492:             flex:0 0 auto !important;
13493:             width:auto !important;
13494:             min-width:56px !important;
13495:             max-width:126px !important;
13496:             height:var(--mcms-tablet-pin-height,31px) !important;
```

### Lines 13491-13501
```text
13491:         html[data-mcms-tablet-active="true"] #${SCRIPT.controlId} .mcms-screen-pin-btn {
13492:             flex:0 0 auto !important;
13493:             width:auto !important;
13494:             min-width:56px !important;
13495:             max-width:126px !important;
13496:             height:var(--mcms-tablet-pin-height,31px) !important;
13497:             padding:0 11px !important;
13498:             border-radius:9px !important;
13499:             font-size:10px !important;
13500:         }
13501:         html[data-mcms-mobile-active="true"] #${SCRIPT.controlId} .mcms-screen-pins {
```

### Lines 13498-13508
```text
13498:             border-radius:9px !important;
13499:             font-size:10px !important;
13500:         }
13501:         html[data-mcms-mobile-active="true"] #${SCRIPT.controlId} .mcms-screen-pins {
13502:             display:flex !important;
13503:             flex-wrap:wrap !important;
13504:             justify-content:flex-start !important;
13505:             align-items:center !important;
13506:             gap:4px !important;
13507:             width:100% !important;
13508:             max-width:none !important;
```

### Lines 13718-13728
```text
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
```

### Lines 13722-13732
```text
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
```

### Lines 13729-13739
```text
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
```

### Lines 13733-13743
```text
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
```

### Lines 13738-13748
```text
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
```

### Lines 13745-13755
```text
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
```

### Lines 13989-13999
```text
13989:         #${SCRIPT.payoutFlashId}[data-template="hyruleQuest"][data-tier="elite"] .mcms-payout-amount { color:#fffce1 !important; }
13990: 
13991:         @keyframes mcmsHyruleRuneTurn { from { transform:rotate(0deg); } to { transform:rotate(360deg); } }
13992:         @keyframes mcmsHyrulePulse { 0%,100% { filter:brightness(.9) drop-shadow(0 0 5px rgba(66,229,211,.22)); } 50% { filter:brightness(1.2) drop-shadow(0 0 14px rgba(66,229,211,.58)); } }
13993: 
13994:         html[data-mcms-tablet-active="true"][data-mcms-ui-theme="hyrule"] #${SCRIPT.panelId}::before { width:280px !important; height:280px !important; right:-60px !important; opacity:.13 !important; }
13995:         html[data-mcms-mobile-active="true"][data-mcms-ui-theme="hyrule"] #${SCRIPT.panelId}::before { width:170px !important; height:170px !important; right:-45px !important; top:86px !important; opacity:.11 !important; }
13996:         html[data-mcms-mobile-active="true"] #${SCRIPT.payoutFlashId}[data-template="hyruleQuest"] .mcms-payout-banner {
13997:             width:min(94%,620px) !important;
13998:             min-height:220px !important;
13999:             padding:36px 24px 28px !important;
```

### Lines 14018-14028
```text
14018:         html[data-mcms-economy="true"] #${SCRIPT.payoutFlashId}[data-template="hyruleQuest"] .mcms-payout-theme-fx-c,
14019:         html[data-mcms-economy="true"] #${SCRIPT.payoutFlashId}[data-template="hyruleQuest"] .mcms-payout-theme-particles {
14020:             animation:none !important;
14021:             display:none !important;
14022:         }
14023:         @media (prefers-reduced-motion:reduce) {
14024:             html[data-mcms-ui-theme="hyrule"] #${SCRIPT.panelId}::after,
14025:             #${SCRIPT.payoutFlashId}[data-template="hyruleQuest"] .mcms-payout-theme-fx-a { animation:none !important; }
14026:         }
14027: 
14028: 
```

### Lines 14453-14463
```text
14453:         return deviceLayoutStatusText();
14454:     }
14455: 
14456:     function refreshTabletModeUi(panel = document.getElementById(SCRIPT.panelId)) {
14457:         if (!panel) return;
14458:         panel.classList.toggle('mcms-tablet-active', tabletModeActive);
14459:         panel.classList.toggle('mcms-mobile-active', mobileModeActive);
14460:         const tabletSelect = panel.querySelector('[data-setting="tablet-mode"]');
14461:         const mobileSelect = panel.querySelector('[data-setting="mobile-mode"]');
14462:         if (tabletSelect && document.activeElement !== tabletSelect) tabletSelect.value = state.tabletMode;
14463:         if (mobileSelect && document.activeElement !== mobileSelect) mobileSelect.value = state.mobileMode;
```

### Lines 14459-14469
```text
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
```

### Lines 14478-14488
```text
14478:         if (subtitle) subtitle.textContent = layoutHelp;
14479:     }
14480: 
14481:     function clearTabletDockSizing(control = document.getElementById(SCRIPT.controlId)) {
14482:         if (control) {
14483:             control.style.removeProperty('--mcms-tablet-dock-width');
14484:             control.style.removeProperty('--mcms-tablet-filter-columns');
14485:             control.style.removeProperty('--mcms-tablet-pin-columns');
14486:             control.style.removeProperty('--mcms-tablet-filter-height');
14487:             control.style.removeProperty('--mcms-tablet-pin-height');
14488:             control.style.removeProperty('--mcms-mobile-dock-width');
```

### Lines 14479-14489
```text
14479:     }
14480: 
14481:     function clearTabletDockSizing(control = document.getElementById(SCRIPT.controlId)) {
14482:         if (control) {
14483:             control.style.removeProperty('--mcms-tablet-dock-width');
14484:             control.style.removeProperty('--mcms-tablet-filter-columns');
14485:             control.style.removeProperty('--mcms-tablet-pin-columns');
14486:             control.style.removeProperty('--mcms-tablet-filter-height');
14487:             control.style.removeProperty('--mcms-tablet-pin-height');
14488:             control.style.removeProperty('--mcms-mobile-dock-width');
14489:             control.style.removeProperty('--mcms-mobile-columns');
```

### Lines 14480-14490
```text
14480: 
14481:     function clearTabletDockSizing(control = document.getElementById(SCRIPT.controlId)) {
14482:         if (control) {
14483:             control.style.removeProperty('--mcms-tablet-dock-width');
14484:             control.style.removeProperty('--mcms-tablet-filter-columns');
14485:             control.style.removeProperty('--mcms-tablet-pin-columns');
14486:             control.style.removeProperty('--mcms-tablet-filter-height');
14487:             control.style.removeProperty('--mcms-tablet-pin-height');
14488:             control.style.removeProperty('--mcms-mobile-dock-width');
14489:             control.style.removeProperty('--mcms-mobile-columns');
14490:             control.style.removeProperty('--mcms-mobile-pin-columns');
```

### Lines 14481-14491
```text
14481:     function clearTabletDockSizing(control = document.getElementById(SCRIPT.controlId)) {
14482:         if (control) {
14483:             control.style.removeProperty('--mcms-tablet-dock-width');
14484:             control.style.removeProperty('--mcms-tablet-filter-columns');
14485:             control.style.removeProperty('--mcms-tablet-pin-columns');
14486:             control.style.removeProperty('--mcms-tablet-filter-height');
14487:             control.style.removeProperty('--mcms-tablet-pin-height');
14488:             control.style.removeProperty('--mcms-mobile-dock-width');
14489:             control.style.removeProperty('--mcms-mobile-columns');
14490:             control.style.removeProperty('--mcms-mobile-pin-columns');
14491:             control.style.removeProperty('--mcms-mobile-filter-height');
```

### Lines 14482-14492
```text
14482:         if (control) {
14483:             control.style.removeProperty('--mcms-tablet-dock-width');
14484:             control.style.removeProperty('--mcms-tablet-filter-columns');
14485:             control.style.removeProperty('--mcms-tablet-pin-columns');
14486:             control.style.removeProperty('--mcms-tablet-filter-height');
14487:             control.style.removeProperty('--mcms-tablet-pin-height');
14488:             control.style.removeProperty('--mcms-mobile-dock-width');
14489:             control.style.removeProperty('--mcms-mobile-columns');
14490:             control.style.removeProperty('--mcms-mobile-pin-columns');
14491:             control.style.removeProperty('--mcms-mobile-filter-height');
14492:             control.style.removeProperty('--mcms-mobile-pin-height');
```

### Lines 14581-14591
```text
14581:             filterHeight = 46;
14582:             pinHeight = 29;
14583:             estimatedHeight = estimateTabletDockHeight(filterCount, filterColumns, pinCount, pinColumns, filterHeight, pinHeight, gap);
14584:         }
14585: 
14586:         control.style.setProperty('--mcms-tablet-dock-width', `${Math.floor(dockWidth)}px`);
14587:         control.style.setProperty('--mcms-tablet-filter-columns', String(filterColumns));
14588:         control.style.setProperty('--mcms-tablet-pin-columns', String(pinColumns));
14589:         control.style.setProperty('--mcms-tablet-filter-height', `${filterHeight}px`);
14590:         control.style.setProperty('--mcms-tablet-pin-height', `${pinHeight}px`);
14591:         control.dataset.mcmsTabletFit = `${Math.floor(dockWidth)}:${filterColumns}:${pinColumns}:${Math.round(estimatedHeight)}`;
```

### Lines 14582-14592
```text
14582:             pinHeight = 29;
14583:             estimatedHeight = estimateTabletDockHeight(filterCount, filterColumns, pinCount, pinColumns, filterHeight, pinHeight, gap);
14584:         }
14585: 
14586:         control.style.setProperty('--mcms-tablet-dock-width', `${Math.floor(dockWidth)}px`);
14587:         control.style.setProperty('--mcms-tablet-filter-columns', String(filterColumns));
14588:         control.style.setProperty('--mcms-tablet-pin-columns', String(pinColumns));
14589:         control.style.setProperty('--mcms-tablet-filter-height', `${filterHeight}px`);
14590:         control.style.setProperty('--mcms-tablet-pin-height', `${pinHeight}px`);
14591:         control.dataset.mcmsTabletFit = `${Math.floor(dockWidth)}:${filterColumns}:${pinColumns}:${Math.round(estimatedHeight)}`;
14592:         return true;
```

### Lines 14583-14593
```text
14583:             estimatedHeight = estimateTabletDockHeight(filterCount, filterColumns, pinCount, pinColumns, filterHeight, pinHeight, gap);
14584:         }
14585: 
14586:         control.style.setProperty('--mcms-tablet-dock-width', `${Math.floor(dockWidth)}px`);
14587:         control.style.setProperty('--mcms-tablet-filter-columns', String(filterColumns));
14588:         control.style.setProperty('--mcms-tablet-pin-columns', String(pinColumns));
14589:         control.style.setProperty('--mcms-tablet-filter-height', `${filterHeight}px`);
14590:         control.style.setProperty('--mcms-tablet-pin-height', `${pinHeight}px`);
14591:         control.dataset.mcmsTabletFit = `${Math.floor(dockWidth)}:${filterColumns}:${pinColumns}:${Math.round(estimatedHeight)}`;
14592:         return true;
14593:     }
```

### Lines 14584-14594
```text
14584:         }
14585: 
14586:         control.style.setProperty('--mcms-tablet-dock-width', `${Math.floor(dockWidth)}px`);
14587:         control.style.setProperty('--mcms-tablet-filter-columns', String(filterColumns));
14588:         control.style.setProperty('--mcms-tablet-pin-columns', String(pinColumns));
14589:         control.style.setProperty('--mcms-tablet-filter-height', `${filterHeight}px`);
14590:         control.style.setProperty('--mcms-tablet-pin-height', `${pinHeight}px`);
14591:         control.dataset.mcmsTabletFit = `${Math.floor(dockWidth)}:${filterColumns}:${pinColumns}:${Math.round(estimatedHeight)}`;
14592:         return true;
14593:     }
14594: 
```

### Lines 14585-14595
```text
14585: 
14586:         control.style.setProperty('--mcms-tablet-dock-width', `${Math.floor(dockWidth)}px`);
14587:         control.style.setProperty('--mcms-tablet-filter-columns', String(filterColumns));
14588:         control.style.setProperty('--mcms-tablet-pin-columns', String(pinColumns));
14589:         control.style.setProperty('--mcms-tablet-filter-height', `${filterHeight}px`);
14590:         control.style.setProperty('--mcms-tablet-pin-height', `${pinHeight}px`);
14591:         control.dataset.mcmsTabletFit = `${Math.floor(dockWidth)}:${filterColumns}:${pinColumns}:${Math.round(estimatedHeight)}`;
14592:         return true;
14593:     }
14594: 
14595:     function estimateMobileDockHeight(commandCount, columns, pinCount, pinColumns, commandHeight, pinHeight, gap) {
```

### Lines 14724-14734
```text
14724:         activeDeviceLayout = resolveDeviceLayout();
14725:         tabletModeActive = resolveTabletMode(activeDeviceLayout);
14726:         mobileModeActive = resolveMobileMode(activeDeviceLayout);
14727:         const tabletViewport = getViewportMetrics();
14728:         root.setAttribute('data-mcms-device-layout', activeDeviceLayout);
14729:         root.setAttribute('data-mcms-tablet-mode', String(state.tabletMode));
14730:         root.setAttribute('data-mcms-tablet-active', String(Boolean(tabletModeActive)));
14731:         root.setAttribute('data-mcms-mobile-mode', String(state.mobileMode));
14732:         root.setAttribute('data-mcms-mobile-active', String(Boolean(mobileModeActive)));
14733:         root.setAttribute('data-mcms-tablet-orientation', tabletViewport.orientation);
14734:         root.setAttribute('data-mcms-mobile-orientation', tabletViewport.orientation);
```

### Lines 14725-14735
```text
14725:         tabletModeActive = resolveTabletMode(activeDeviceLayout);
14726:         mobileModeActive = resolveMobileMode(activeDeviceLayout);
14727:         const tabletViewport = getViewportMetrics();
14728:         root.setAttribute('data-mcms-device-layout', activeDeviceLayout);
14729:         root.setAttribute('data-mcms-tablet-mode', String(state.tabletMode));
14730:         root.setAttribute('data-mcms-tablet-active', String(Boolean(tabletModeActive)));
14731:         root.setAttribute('data-mcms-mobile-mode', String(state.mobileMode));
14732:         root.setAttribute('data-mcms-mobile-active', String(Boolean(mobileModeActive)));
14733:         root.setAttribute('data-mcms-tablet-orientation', tabletViewport.orientation);
14734:         root.setAttribute('data-mcms-mobile-orientation', tabletViewport.orientation);
14735:         root.setAttribute('data-mcms-show-alliance-missions', String(Boolean(state.visibility.allianceMissions)));
```

### Lines 14728-14738
```text
14728:         root.setAttribute('data-mcms-device-layout', activeDeviceLayout);
14729:         root.setAttribute('data-mcms-tablet-mode', String(state.tabletMode));
14730:         root.setAttribute('data-mcms-tablet-active', String(Boolean(tabletModeActive)));
14731:         root.setAttribute('data-mcms-mobile-mode', String(state.mobileMode));
14732:         root.setAttribute('data-mcms-mobile-active', String(Boolean(mobileModeActive)));
14733:         root.setAttribute('data-mcms-tablet-orientation', tabletViewport.orientation);
14734:         root.setAttribute('data-mcms-mobile-orientation', tabletViewport.orientation);
14735:         root.setAttribute('data-mcms-show-alliance-missions', String(Boolean(state.visibility.allianceMissions)));
14736:         root.setAttribute('data-mcms-show-my-missions', String(Boolean(state.visibility.myMissions)));
14737:         root.setAttribute('data-mcms-show-vehicles', String(Boolean(state.visibility.vehicles)));
14738:         root.setAttribute('data-mcms-show-buildings', String(Boolean(state.visibility.buildings)));
```

### Lines 20309-20319
```text
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
```

### Lines 20328-20338
```text
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
```

### Lines 21501-21511
```text
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
```

### Lines 21502-21512
```text
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
```

### Lines 21504-21514
```text
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
```

### Lines 26836-26846
```text
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
```

### Lines 26838-26848
```text
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
```

### Lines 27876-27886
```text
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
```

### Lines 27877-27887
```text
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
```

### Lines 27878-27888
```text
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
```

### Lines 27879-27889
```text
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
```

### Lines 27880-27890
```text
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
```

### Lines 27881-27891
```text
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
```

### Lines 27882-27892
```text
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
```

### Lines 27883-27893
```text
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
```

### Lines 27884-27894
```text
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
```

### Lines 27887-27897
```text
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
```

### Lines 27888-27898
```text
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
```

### Lines 27891-27901
```text
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
```

### Lines 27893-27903
```text
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
```

### Lines 27897-27907
```text
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
```

### Lines 27898-27908
```text
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
```

### Lines 27913-27923
```text
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
```

### Lines 27919-27929
```text
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
```

### Lines 27934-27944
```text
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
```

### Lines 27935-27945
```text
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
```

### Lines 27946-27956
```text
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
```

### Lines 27953-27963
```text
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
```

### Lines 27954-27964
```text
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
```

### Lines 27969-27979
```text
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
```

### Lines 27971-27981
```text
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
```

### Lines 27978-27988
```text
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
```

### Lines 27980-27990
```text
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
```

### Lines 27987-27997
```text
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
```

### Lines 27988-27998
```text
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
```

### Lines 28001-28011
```text
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
```

### Lines 28002-28012
```text
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
```

### Lines 28023-28033
```text
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
```

### Lines 28042-28052
```text
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
```

### Lines 28043-28053
```text
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
```

### Lines 28045-28055
```text
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
```

### Lines 28048-28058
```text
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
```

### Lines 28049-28059
```text
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
```

### Lines 28054-28064
```text
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
```

### Lines 28057-28067
```text
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
```

### Lines 28066-28076
```text
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
```

### Lines 28075-28085
```text
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
```

### Lines 28087-28097
```text
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
```

### Lines 28092-28102
```text
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
```

### Lines 28095-28105
```text
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
```

### Lines 28097-28107
```text
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
```

### Lines 28112-28122
```text
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
```

### Lines 28114-28124
```text
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
```

### Lines 28116-28126
```text
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
```

### Lines 28118-28128
```text
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
```

### Lines 28122-28132
```text
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
```

### Lines 28124-28134
```text
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
```

### Lines 28126-28136
```text
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
```

### Lines 28131-28141
```text
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
```

### Lines 28133-28143
```text
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
```

### Lines 28140-28150
```text
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
```

### Lines 28146-28156
```text
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
```

### Lines 28153-28163
```text
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
```

### Lines 28619-28629
```text
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
```

### Lines 28620-28630
```text
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
```

### Lines 28625-28635
```text
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
```

### Lines 28626-28636
```text
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
```

### Lines 28698-28708
```text
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
```

### Lines 28739-28749
```text
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
```

### Lines 28754-28764
```text
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
```

### Lines 28755-28765
```text
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
```

### Lines 29710-29720
```text
29710:             missionOverlayVersions.clear();
29711:             markerRegistryCache.clear();
29712:             criticalMissionStableCache.clear();
29713:             removeOldInstances();
29714:             const root = document.documentElement;
29715:             for (const attribute of ['data-mcms-ui-theme', 'data-mc-map-skin', 'data-mcms-clean', 'data-mcms-marker-focus', 'data-mcms-mission-pulse', 'data-mcms-road-priority', 'data-mcms-compact-dock', 'data-mcms-command-bar-open', 'data-mcms-economy', 'data-mcms-map-moving', 'data-mcms-alliance-buildings-map', 'data-mcms-alliance-buildings-page', 'data-mcms-device-layout', 'data-mcms-tablet-mode', 'data-mcms-tablet-active', 'data-mcms-tablet-orientation', 'data-mcms-mobile-mode', 'data-mcms-mobile-active', 'data-mcms-mobile-orientation', 'data-mcms-show-alliance-missions', 'data-mcms-show-my-missions', 'data-mcms-show-vehicles', 'data-mcms-show-buildings', 'data-mcms-critical-view', 'data-mcms-help-open']) root.removeAttribute(attribute);
29716:         });
29717: 
29718:         runtimeSetTimeout(() => runAutoNight(true), 180);
29719:         if (state.economyMode) runtimeSetTimeout(() => setEconomyMode(true, false), 420);
29720:         console.debug(`[${SCRIPT.name}] v${SCRIPT.version} audited runtime ready.`);
```

## Long control-label candidates

- 64 chars | `Show your own committed unit counts beside missions. Shortcut: 8` | lines 27966
- 63 chars | `Toolkit runtime stopped while stabilising the financial ledger.` | lines 25683
- 62 chars | `Show a formatted mission value in opened MissionChief windows.` | lines 27962
- 62 chars | `Show/hide confidently detected buildings/stations. Shortcut: 4` | lines 27765, 27929
- 61 chars | `Show only personal missions aged 8 hours or more. Shortcut: 9` | lines 27980
- 61 chars | `Show/hide confidently detected alliance missions. Shortcut: 2` | lines 27763, 27927
- 61 chars | `Show/hide confidently detected personal missions. Shortcut: 1` | lines 27762, 27926
- 60 chars | `The file does not contain MissionChief Map Command settings.` | lines 23187
- 57 chars | `patient (?:transport|treatment)|hospital\\s*-\\s*alliance` | lines 24342
- 56 chars | `Animate genuinely new mission spawns with a radar pulse.` | lines 27964
- 56 chars | `MissionChief Map Command Toolkit Private Settings Backup` | lines 22995
- 56 chars | `The selected custom date range contains no elapsed time.` | lines 25495
- 55 chars | `Draw coverage rings around detected buildings/stations.` | lines 27909
- 55 chars | `Show missions with units on scene and no detected issue` | lines 21179
- 55 chars | `Show official developer-launched Special Event missions` | lines 21232
- 54 chars | `Edit ${escapeHtml(bookmark.name)} name and short label` | lines 28232
- 54 chars | `Show your committed units beside missions. Shortcut: 8` | lines 27769
- 53 chars | `building complex.*upgrad|upgraded to building complex` | lines 24349
- 53 chars | `building constructed|station constructed|new building` | lines 24349
- 53 chars | `Choose the reference point used for mission distances` | lines 21041
- 53 chars | `Show Standard, Timed Event and Special Event missions` | lines 21232
- 53 chars | `Sort furthest from the selected distance origin first` | lines 21051
- 52 chars | `Lock distance calculations to the current map centre` | lines 21041
- 52 chars | `Show/hide confidently detected vehicles. Shortcut: 3` | lines 27764, 27928
- 51 chars | `Hold left-click on this title area. Position saves.` | lines 14475
- 51 chars | `Show every mission regardless of age · newest first` | lines 1067
- 50 chars | `height:34px !important;line-height:34px !important` | lines 27978, 27979
- 50 chars | `Hold left-click and drag this bar to move the menu` | lines 14476, 27873
- 50 chars | `Hover a mission marker for a live mission summary.` | lines 27961
- 50 chars | `Import a current or legacy toolkit settings backup` | lines 28105
- 50 chars | `Restore Mission Age Watch to the mission-list area` | lines 20682
- 50 chars | `Show missions aged 16 hours or more · oldest first` | lines 1069
- 50 chars | `Show missions aged 24 hours or more · oldest first` | lines 1070
- 50 chars | `Sort closest to the selected distance origin first` | lines 21051
- 50 chars | `width:100% !important;margin-bottom:8px !important` | lines 28003
- 50 chars | `📈 MissionChief Financial Command — Executive Audit` | lines 26498
- 49 chars | `><span>${escapeHtml(label)}</span><i aria-hidden=` | lines 21049
- 49 chars | `Export failed: settings file could not be created` | lines 23076
- 49 chars | `MissionChief Map Command Toolkit searchable guide` | lines 27570
- 48 chars | `TOP SECRET // SECTION 00 FINANCIAL AUTHORISATION` | lines 12905
- 48 chars | `Vehicle data is still loading for these missions` | lines 21686
- 47 chars | `${escapeHtml(criticalValueTitle(label, group))}` | lines 21628
- 47 chars | `AUTOMATED COMMAND NETWORK  //  ASSEMBLY CONTROL` | lines 7060
- 47 chars | `Loading complete fleet · visible vehicles shown` | lines 20517
- 47 chars | `Reset all Mission Age Watch filters and sorting` | lines 21207
- 47 chars | `Short screen label (leave blank for automatic):` | lines 18867, 18902
- 47 chars | `Show Alliance-owned or Alliance-shared missions` | lines 21220
- 47 chars | `Show ordinary timed or community Event missions` | lines 21232
- 47 chars | `Waiting for the first live data synchronisation` | lines 21826
- 47 chars | `width:100% !important;margin-top:7px !important` | lines 28025, 28038, 28039
- 46 chars | `${escapeHtml(`${ageText} · ${severityLabel}`)}` | lines 15949
- 46 chars | `Hide map controls for screenshots. Shortcut: C` | lines 27905
- 46 chars | `Open or close Vehicle Code Status. Shortcut: V` | lines 27771
- 46 chars | `Update this bookmark from the current map view` | lines 28238
- 46 chars | `vehicle bought|vehicle purchase|bought vehicle` | lines 24347
- 45 chars | `, ownership, category, specialEvent?.label ||` | lines 19985
- 45 chars | `Reconstructed from current balance and ledger` | lines 26089
- 44 chars | `Expand Mission Age Watch over the Radio area` | lines 20682, 20786, 20786
- 44 chars | `Open or close Mission Age Watch. Shortcut: W` | lines 27772
- 44 chars | `Reconciled against saved balance checkpoints` | lines 26098
- 43 chars | `Open age, sort and distance-origin controls` | lines 20770
- 43 chars | `Pulse detected mission markers. Shortcut: P` | lines 27907
- 42 chars | `) { event.preventDefault(); toggleFeature(` | lines 27692, 27693, 27694, 27695
- 41 chars | `Import failed: settings file is too large` | lines 23235
- 40 chars | `).length + String(embed?.author?.name ||` | lines 26442
- 40 chars | `).length + String(embed?.footer?.text ||` | lines 26442
- 40 chars | `Select valid custom start and end dates.` | lines 25491
- 39 chars | `).length + String(embed?.description ||` | lines 26442
- 39 chars | `Estimated time until mission completion` | lines 21836
- 39 chars | `🧠 Audit Intelligence & Capital Strategy` | lines 26520
- 38 chars | `MC Map Command private settings backup` | lines 23060
- 37 chars | `, minAgeMs: 8 * 60 * 60 * 1000, sort:` | lines 1068
- 37 chars | `Jump to ${escapeHtml(entry.fullName)}` | lines 28272, 28272
- 37 chars | `The public guide could not be loaded.` | lines 27621
- 36 chars | `Exit clean mode. Shortcut: C or Esc.` | lines 27742
- 36 chars | `Mission ordering and distance origin` | lines 20781
- 36 chars | `Open Mission Age Watch view controls` | lines 20770
- 36 chars | `Zoom to ${escapeHtml(entry.caption)}` | lines 21852, 21852
- 35 chars | `Automatically switch skins by time.` | lines 28084
- 35 chars | `Increase road contrast. Shortcut: R` | lines 27908
- 35 chars | `Show Personal and Alliance missions` | lines 21220
- 34 chars | `>10 minutes</option><option value=` | lines 27972
- 34 chars | `>15 minutes</option><option value=` | lines 27972
- 34 chars | `>20 minutes</option><option value=` | lines 27972
- 34 chars | `>30 minutes</option><option value=` | lines 27972
- 34 chars | `>45 minutes</option><option value=` | lines 27972
- 34 chars | `>All values</option><option value=` | lines 27936
- 34 chars | `All Available MissionChief History` | lines 25476
- 34 chars | `}${report.ledgerScanLimitReached ?` | lines 26437
- 33 chars | `>Always on</option><option value=` | lines 28055, 28056
- 33 chars | `Jump to ${escapeHtml(place.name)}` | lines 28212
- 33 chars | `Open ${escapeHtml(entry.caption)}` | lines 21852, 21852
- 33 chars | `Persistent map visibility filters` | lines 27761
- 33 chars | `Private settings export cancelled` | lines 23038
- 33 chars | `Private settings import cancelled` | lines 23246
- 32 chars | `:scope > .mcms-mission-value-row` | lines 21425
- 32 chars | `>10 miles</option><option value=` | lines 27921, 27955
- 32 chars | `>25 miles</option><option value=` | lines 27921, 27955
- 32 chars | `>50 miles</option><option value=` | lines 27955
- 31 chars | `>5 miles</option><option value=` | lines 27921
- 31 chars | `Mission Age Watch view controls` | lines 20775
- 31 chars | `Open the guide source on GitHub` | lines 27563, 27563
- 31 chars | `}${report.ledgerScanCancelled ?` | lines 26437
- 30 chars | `Open or close toolkit settings` | lines 27756, 27756
- 30 chars | `SIS // SECTION 00 // EYES ONLY` | lines 12521, 12768
- 29 chars | `${escapeHtml(title || label)}` | lines 27704
- 29 chars | `>Top 3</option><option value=` | lines 28016
- 29 chars | `>Top 5</option><option value=` | lines 28016
- 29 chars | `All toolkit settings exported` | lines 23062, 23074
- 29 chars | `LSSM mission release controls` | lines 16881
- 29 chars | `MI6 FUNDS TRANSFER AUTHORISED` | lines 1010
- 29 chars | `Mission Age Watch quick views` | lines 20795
- 29 chars | `Patient Transport & Treatment` | lines 24342
- 28 chars | `${clearingStyle} aria-label=` | lines 21849
- 28 chars | `>10K+</option><option value=` | lines 27936
- 28 chars | `>15K+</option><option value=` | lines 27936
- 28 chars | `LSSM mission release control` | lines 16871
- 28 chars | `Umbrella Containment Cashout` | lines 1044
- 28 chars | `Unclassified Positive Income` | lines 24356
- 28 chars | `} ${element.querySelector?.(` | lines 19153
- 27 chars | `>5K+</option><option value=` | lines 27936
- 27 chars | `AUTOMATION REWARD CONFIRMED` | lines 1004
- 27 chars | `CREDIT ALLOCATION CONFIRMED` | lines 1005
- 27 chars | `Import all toolkit settings` | lines 28105
- 27 chars | `Ledger head remained stable` | lines 26437
- 27 chars | `Mission operational filters` | lines 20806
- 27 chars | `Open searchable Help Centre` | lines 27878, 27878
- 27 chars | `Prisoner transport required` | lines 16234
- 27 chars | `Resource shortfall detected` | lines 17607
- 27 chars | `Since Toolkit Session Start` | lines 25486
- 27 chars | `span, small, .label, .badge` | lines 15167
- 27 chars | `VAULT-TEC REWARD AUTHORIZED` | lines 1003
- 27 chars | `} ${element.getAttribute?.(` | lines 19153, 19153, 19153
- 26 chars | `) || node.querySelector?.(` | lines 28828
- 26 chars | `).trim().toLowerCase() !==` | lines 16944, 17293
- 26 chars | `allow-scripts allow-popups` | lines 27570
- 26 chars | `CREDIT TRANSFER AUTHORIZED` | lines 1007
- 26 chars | `Patient transport required` | lines 16234, 16474
- 26 chars | `Show missions owned by you` | lines 21220
- 26 chars | `Vehicle status-code counts` | lines 20467
- 25 chars | `: state.heatmap.service +` | lines 18672
- 25 chars | `Close Vehicle Code Status` | lines 20460, 20460
- 25 chars | `CREDIT TRANSFER CONFIRMED` | lines 1001
- 25 chars | `Discord Financial Command` | lines 27486
- 25 chars | `Mission Age Watch filters` | lines 20793
- 25 chars | `Mission ownership filters` | lines 20792
- 25 chars | `Refresh Mission Age Watch` | lines 20787, 20787
- 25 chars | `Settings export cancelled` | lines 23066
- 25 chars | `Since Last Discord Report` | lines 25486
- 24 chars | `) || icon.querySelector(` | lines 14754
- 24 chars | `007 Intelligence Cashout` | lines 1048
- 24 chars | `: Object.freeze({ label:` | lines 1068
- 24 chars | `Advanced mission filters` | lines 20805
- 24 chars | `Disable blocker & reload` | lines 28915
- 24 chars | `iOS mobile layout active` | lines 14448
- 24 chars | `Major incident news feed` | lines 19406
- 24 chars | `Mission category filters` | lines 20799
- 24 chars | `Refunds & Reimbursements` | lines 24340
- 24 chars | `Unrecognised Game Status` | lines 20433
- 24 chars | `VEHICLES NEED ASSISTANCE` | lines 19918
- 24 chars | `} ${element.className ||` | lines 19153
- 23 chars | `) : allEntries.length ?` | lines 21861
- 23 chars | `Alliance mission payout` | lines 20384
- 23 chars | `Close Mission Age Watch` | lines 20788, 20788
- 23 chars | `Complete personal fleet` | lines 20517
- 23 chars | `Current Toolkit Session` | lines 25481
- 23 chars | `Custom Financial Period` | lines 25497
- 23 chars | `EMPIRE PAYOUT CONFIRMED` | lines 1000
- 23 chars | `Enable blocker & reload` | lines 28915
- 23 chars | `Personal mission payout` | lines 20384
- 23 chars | `Pinned screen shortcuts` | lines 27774
- 23 chars | `Reload the latest guide` | lines 27562, 27562
- 23 chars | `} ${input.getAttribute(` | lines 19094
- 22 chars | `, anchor.getAttribute(` | lines 14758
- 22 chars | `, icon.getAttribute?.(` | lines 14751
- 22 chars | `Alliance Contributions` | lines 24353
- 22 chars | `Auto-load all vehicles` | lines 28083
- 22 chars | `BF Bad Company Cashout` | lines 1024
- 22 chars | `iOS Mobile Mode active` | lines 28357
- 22 chars | `Missing resource types` | lines 17607
- 22 chars | `Mission value overview` | lines 20790
- 22 chars | `Recruitment & Staffing` | lines 24352
- 22 chars | `Toolkit settings reset` | lines 23266
- 22 chars | `}${counts[key] === 0 ?` | lines 21230
- 21 chars | `Dark Fantasy Inspired` | lines 1006
- 21 chars | `desktop layout active` | lines 14448
- 21 chars | `Desktop layout active` | lines 28357
- 21 chars | `GTA Vice City Cashout` | lines 1020
- 21 chars | `invalid settings file` | lines 23254
- 21 chars | `NEW ALLIANCE INCIDENT` | lines 22812
- 21 chars | `Pixel Arcade Inspired` | lines 1009
- 21 chars | `Revenue concentration` | lines 26194
- 21 chars | `RUPEE REWARD ACQUIRED` | lines 1011
- 21 chars | `Unclassified Spending` | lines 24357
- 20 chars | `) state.tabletMode =` | lines 28343
- 20 chars | `Available at Station` | lines 1097
- 20 chars | `Bad Company Inspired` | lines 999
- 20 chars | `Buildings & Stations` | lines 24349
- 20 chars | `Collapse command bar` | lines 27757, 27757, 28611
- 20 chars | `Disable Economy Mode` | lines 28600
- 20 chars | `Event & Bonus Income` | lines 24346
- 20 chars | `MOBILE COMMAND PANEL` | lines 14470
- 20 chars | `NO VEHICLES AT SCENE` | lines 19948
- 20 chars | `Refresh vehicle data` | lines 20459, 20459
- 20 chars | `Show normal missions` | lines 21232
- 20 chars | `SYNCING VEHICLE DATA` | lines 19927
- 20 chars | `TABLET COMMAND PANEL` | lines 14470
- 20 chars | `tablet layout active` | lines 14448
- 20 chars | `Training & Education` | lines 24351
- 20 chars | `Umbrella Containment` | lines 975, 1007
- 19 chars | `, img.getAttribute(` | lines 14767
- 19 chars | `><span aria-hidden=` | lines 21835, 21843
- 19 chars | `ASSISTANCE REQUIRED` | lines 19046
- 19 chars | `Balance unavailable` | lines 26298
- 19 chars | `Clear and Available` | lines 1096
- 19 chars | `Daily Login Rewards` | lines 24344
- 19 chars | `Enable Economy Mode` | lines 27759, 27759, 28600
- 19 chars | `Factorio Industrial` | lines 1004
- 19 chars | `Hyrule Quest Reward` | lines 1011, 1052
- 19 chars | `Quick mission views` | lines 20797
- 19 chars | `Requesting Dispatch` | lines 1100
- 19 chars | `Reset menu position` | lines 27877
- 19 chars | `SCORE BONUS AWARDED` | lines 1009
- 19 chars | `Underworld Inspired` | lines 1008
- 19 chars | `Vehicle Code Status` | lines 20450
- 19 chars | `}</small></span>` :` | lines 21834, 21835
- 18 chars | `, accountingGroup:` | lines 24348, 24350
- 18 chars | `><div><span class=` | lines 16493
- 18 chars | `Cyberpunk Inspired` | lines 1001
- 18 chars | `daily login reward` | lines 24344
- 18 chars | `Expand command bar` | lines 28611
- 18 chars | `Mission value mode` | lines 21631
- 18 chars | `Prisoner Transport` | lines 24343
- 18 chars | `Tablet Mode active` | lines 28357
- 18 chars | `Transport required` | lines 16234, 16318, 16318
- 18 chars | `Vice City Inspired` | lines 998
- 18 chars | `} ${input.title ||` | lines 19094
- 17 chars | `)?.textContent ||` | lines 24426
- 17 chars | `, lat, lng].join(` | lines 19985
- 17 chars | `Alliance Missions` | lines 24341, 27927
- 17 chars | `Arial Narrow Bold` | lines 3240, 3254, 3389
- 17 chars | `AWAITING RESPONSE` | lines 19052
- 17 chars | `Close Help Centre` | lines 27564, 27564
- 17 chars | `Cyberpunk Cashout` | lines 1032
- 17 chars | `Hellfire Inspired` | lines 1002
- 17 chars | `Mission age range` | lines 20780
- 17 chars | `Mission Age Watch` | lines 20759
- 17 chars | `On scene / stable` | lines 21152
- 17 chars | `Personal Missions` | lines 27926
- 17 chars | `Scarface Inspired` | lines 1000
