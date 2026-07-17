# Issue #70 reconciliation field inspection

Matches: **7**

## Line 26222

`function calculateVaultReconciliation(vault, period, currentTransactions, currentBalance) {`

```javascript
26177:             activeHours: Math.round(activeHours * 100) / 100,
26178:             calendarHours: Math.round(calendarHours * 100) / 100,
26179:             calendarDays: Math.round(calendarDays * 1000) / 1000,
26180:             classificationConfidence,
26181:             unclassifiedAmount,
26182:             unclassifiedCount,
26183:             unclassifiedEntries,
26184:             operatingMarginPercent,
26185:             capitalInvestmentRatioPercent,
26186:             incomeConcentrationPercent,
26187:             incomeVolatilityPercent,
26188:             topIncomeCategory,
26189:             topPayouts,
26190:             buckets
26191:         };
26192:     }
26193: 
26194:     function percentageChange(current, previous) {
26195:         const currentValue = Number(current) || 0;
26196:         const previousValue = Number(previous) || 0;
26197:         if (!previousValue) return currentValue ? null : 0;
26198:         return ((currentValue - previousValue) / Math.abs(previousValue)) * 100;
26199:     }
26200: 
26201:     function formatPercentageChange(value) {
26202:         if (value === null || !Number.isFinite(value)) return 'New activity';
26203:         const rounded = Math.round(value * 10) / 10;
26204:         return `${rounded > 0 ? '+' : ''}${rounded.toLocaleString('en-GB')}%`;
26205:     }
26206: 
26207:     function buildFinancialComparison(current, previous) {
26208:         return {
26209:             incomeChange: percentageChange(current.income, previous.income),
26210:             operatingResultChange: percentageChange(current.operatingResult, previous.operatingResult),
26211:             capitalInvestmentChange: percentageChange(current.capitalInvestment, previous.capitalInvestment),
26212:             spendingChange: percentageChange(current.spending, previous.spending),
26213:             netChange: percentageChange(current.net, previous.net),
26214:             missionChange: current.missionCount - previous.missionCount,
26215:             averageRewardChange: percentageChange(current.averageMissionReward, previous.averageMissionReward),
26216:             activeVelocityChange: percentageChange(current.activeIncomePerHour, previous.activeIncomePerHour),
26217:             currentNet: current.net,
26218:             previousNet: previous.net
26219:         };
26220:     }
26221: 
26222:     function calculateVaultReconciliation(vault, period, currentTransactions, currentBalance) {
26223:         const checkpoints = Array.isArray(vault?.balanceCheckpoints) ? vault.balanceCheckpoints.slice().sort((a, b) => a.timestamp - b.timestamp) : [];
26224:         let startCheckpoint = null;
26225:         let endCheckpoint = null;
26226:         for (const checkpoint of checkpoints) {
26227:             if (checkpoint.timestamp <= period.startMs) startCheckpoint = checkpoint;
26228:             if (checkpoint.timestamp >= period.endMs && !endCheckpoint) endCheckpoint = checkpoint;
26229:         }
26230:         if (!endCheckpoint && Number.isFinite(Number(currentBalance)) && Math.abs(Date.now() - period.endMs) < 10 * 60 * 1000) {
26231:             endCheckpoint = { timestamp: Date.now(), balance: Math.round(currentBalance) };
26232:         }
26233:         if (!startCheckpoint || !endCheckpoint || endCheckpoint.timestamp <= startCheckpoint.timestamp) {
26234:             return { reconciled: false, difference: null, label: 'Reconstructed from current balance and ledger', startCheckpoint, endCheckpoint };
26235:         }
26236:         const movement = currentTransactions
26237:             .filter(entry => entry.timestamp > startCheckpoint.timestamp && entry.timestamp <= endCheckpoint.timestamp)
26238:             .reduce((sum, entry) => sum + Number(entry.amount || 0), 0);
26239:         const difference = Math.round((endCheckpoint.balance - startCheckpoint.balance) - movement);
26240:         return {
26241:             reconciled: Math.abs(difference) <= 1,
26242:             difference,
26243:             label: Math.abs(difference) <= 1 ? 'Reconciled against saved balance checkpoints' : `Checkpoint variance ${formatSignedCredits(difference)}`,
26244:             startCheckpoint,
26245:             endCheckpoint
26246:         };
26247:     }
26248: 
26249:     function financialScoreLabel(score) {
26250:         if (score >= 90) return { grade: 'A+', label: 'Exceptional command' };
26251:         if (score >= 82) return { grade: 'A', label: 'Strong command' };
26252:         if (score >= 74) return { grade: 'B+', label: 'Healthy expansion' };
26253:         if (score >= 66) return { grade: 'B', label: 'Stable position' };
26254:         if (score >= 56) return { grade: 'C+', label: 'Mixed position' };
26255:         if (score >= 45) return { grade: 'C', label: 'Watch position' };
26256:         if (score >= 32) return { grade: 'D', label: 'Financial pressure' };
26257:         return { grade: 'F', label: 'Critical pressure' };
26258:     }
26259: 
26260:     function calculateFinancialScorecard(summary, comparison, { complete = true, balanceAvailable = true, reconciled = false, closingBalance = null } = {}) {
26261:         const incomeTrend = comparison?.incomeChange;
26262:         let revenue = 65;
26263:         if (Number.isFinite(incomeTrend)) revenue += Math.max(-25, Math.min(25, incomeTrend / 2));
26264:         if (summary.activeIncomePerHour > summary.incomePerHour * 1.5) revenue += 4;
26265:         revenue = Math.round(clamp(revenue, 0, 100, 65));
26266: 
26267:         let efficiency = 55 + summary.operatingMarginPercent * 0.45;
26268:         if (summary.operatingExpense === 0 && summary.income > 0) efficiency += 8;
26269:         efficiency = Math.round(clamp(efficiency, 0, 100, 55));
26270: 
26271:         const dailyOperatingExpense = summary.operatingExpense / Math.max(1 / 24, Number(summary.calendarDays) || 1 / 24);
26272:         const runwayDays = balanceAvailable && dailyOperatingExpense > 0 ? Math.max(0, Number(closingBalance) || 0) / dailyOperatingExpense : null;
26273:         let liquidity = balanceAvailable ? 65 : 40;
26274:         if (runwayDays !== null) liquidity += Math.max(-30, Math.min(30, (runwayDays - 7) * 2));
26275:         liquidity = Math.round(clamp(liquidity, 0, 100, 60));
26276: 
26277:         const capexRatio = summary.capitalInvestmentRatioPercent;
26278:         let growth = summary.capitalInvestment > 0 ? 72 : 58;
26279:         if (capexRatio > 200) growth -= 18;
26280:         else if (capexRatio > 120) growth -= 8;
26281:         else if (capexRatio >= 20 && capexRatio <= 100) growth += 10;
26282:         growth = Math.round(clamp(growth, 0, 100, 60));
26283: 
26284:         let confidence = summary.classificationConfidence;
26285:         if (!complete) confidence -= 18;
26286:         if (!balanceAvailable) confidence -= 8;
26287:         if (reconciled) confidence += 5;
```

## Line 26442

`const reconciliation = calculateVaultReconciliation(ledger.vault, period, ledger.entries, currentBalance);`

```javascript
26397:         const allAvailable = period.id === 'allAvailable';
26398:         if (allAvailable) {
26399:             financeArchiveScanBusy = true;
26400:             financeArchiveScanCancelled = false;
26401:         }
26402:         let ledger;
26403:         try {
26404:             ledger = await fetchFinancialLedger(requiredStartMs, 0, false, false);
26405:         } finally {
26406:             if (allAvailable) {
26407:                 financeArchiveScanBusy = false;
26408:                 financeArchiveScanCancelled = false;
26409:             }
26410:         }
26411:         if (allAvailable) {
26412:             const oldest = ledger.oldestTimestamp || ledger.entries[0]?.timestamp || Date.now();
26413:             period = {
26414:                 ...period,
26415:                 startMs: oldest,
26416:                 durationMs: Math.max(1, period.endMs - oldest),
26417:                 comparisonStartMs: 0,
26418:                 comparisonEndMs: 0,
26419:                 rangeLabel: formatPeriodRange(oldest, period.endMs),
26420:                 comparisonRangeLabel: 'Not applicable'
26421:             };
26422:         }
26423:         const currentTransactions = [];
26424:         const previousTransactions = [];
26425:         let afterPeriodNet = 0;
26426:         const now = Date.now();
26427:         for (const entry of ledger.entries) {
26428:             if (entry.timestamp >= period.startMs && entry.timestamp < period.endMs) currentTransactions.push(entry);
26429:             else if (comparisonEnabled && entry.timestamp >= period.comparisonStartMs && entry.timestamp < period.comparisonEndMs) previousTransactions.push(entry);
26430:             if (entry.timestamp >= period.endMs && entry.timestamp <= now) afterPeriodNet += entry.amount;
26431:         }
26432: 
26433:         const current = summariseFinancialTransactions(currentTransactions, period);
26434:         const previousPeriod = { ...period, startMs: period.comparisonStartMs, endMs: period.comparisonEndMs, durationMs: period.durationMs };
26435:         const previous = comparisonEnabled ? summariseFinancialTransactions(previousTransactions, previousPeriod) : null;
26436:         const comparison = previous ? buildFinancialComparison(current, previous) : null;
26437:         const account = ledger.account;
26438:         const currentBalance = Number.isFinite(account?.currentBalance) ? account.currentBalance : null;
26439:         const closingBalance = currentBalance === null ? null : currentBalance - afterPeriodNet;
26440:         const openingBalance = closingBalance === null ? null : closingBalance - current.net;
26441:         const balanceAvailable = openingBalance !== null && closingBalance !== null;
26442:         const reconciliation = calculateVaultReconciliation(ledger.vault, period, ledger.entries, currentBalance);
26443:         const reconciliationLabel = balanceAvailable ? reconciliation.label : 'Balance unavailable';
26444:         const drawdown = calculateFinancialDrawdown(openingBalance, current.transactions);
26445:         const scorecard = calculateFinancialScorecard(current, comparison, { complete: ledger.complete, balanceAvailable, reconciled: reconciliation.reconciled, closingBalance });
26446:         let forecastSummary = current;
26447:         let forecastPeriod = period;
26448:         if (state.discordReport.includeForecast && period.durationMs > 30 * 86400000) {
26449:             const recentStart = Math.max(period.startMs, period.endMs - 30 * 86400000);
26450:             const recentTransactions = currentTransactions.filter(entry => entry.timestamp >= recentStart);
26451:             forecastPeriod = { ...period, startMs: recentStart, durationMs: Math.max(1, period.endMs - recentStart), id: 'recent30' };
26452:             forecastSummary = summariseFinancialTransactions(recentTransactions, forecastPeriod);
26453:         }
26454:         const forecast = state.discordReport.includeForecast ? { ...buildFinancialForecast(forecastSummary, forecastPeriod, closingBalance), basisDays: Math.max(1, Math.round(forecastPeriod.durationMs / 86400000)) } : null;
26455:         const report = {
26456:             generatedAt: Date.now(),
26457:             signature: currentFinancialReportSignature(),
26458:             period,
26459:             reportDate: localIsoDate(),
26460:             reportDateLabel: `${period.label} · ${period.rangeLabel}`,
26461:             userName: account?.userName || ledger.vault?.player?.name || '',
26462:             userId: account?.userId || ledger.vault?.player?.id || null,
26463:             currentBalance,
26464:             openingBalance,
26465:             closingBalance,
26466:             reconciliationDifference: reconciliation.difference,
26467:             reconciled: reconciliation.reconciled,
26468:             balanceCalculated: balanceAvailable,
26469:             reconciliationLabel,
26470:             ledgerComplete: ledger.complete,
26471:             ledgerCoverageReached: ledger.coverageReached,
26472:             ledgerPages: ledger.pageCount,
26473:             ledgerLastPage: ledger.lastPage,
26474:             ledgerStable: ledger.ledgerStable,
26475:             ledgerScanRetries: ledger.scanRetries,
26476:             ledgerScanCancelled: ledger.scanCancelled,
26477:             ledgerScanLimitReached: ledger.scanLimitReached,
26478:             ledgerSource: ledger.ledgerSource,
26479:             archiveComplete: ledger.archiveComplete,
26480:             archiveTruncated: ledger.archiveTruncated,
26481:             droppedTransactions: ledger.droppedTransactions,
26482:             vaultTransactionCount: ledger.vaultTransactionCount,
26483:             invalidTimestampCount: ledger.invalidTimestampCount,
26484:             comparison,
26485:             previous,
26486:             scorecard,
26487:             grade: { score: scorecard.overall, grade: scorecard.grade, label: scorecard.label, marginPercent: scorecard.operatingMarginPercent },
26488:             forecast,
26489:             drawdown,
26490:             chartBlob: null,
26491:             ...current
26492:         };
26493:         report.riskAlerts = state.discordReport.includeRisk ? buildFinancialRiskAlerts(current, comparison, {
26494:             ledgerComplete: ledger.complete,
26495:             drawdown,
26496:             scorecard,
26497:             archiveTruncated: ledger.archiveTruncated,
26498:             droppedTransactions: ledger.droppedTransactions,
26499:             scanLimitReached: ledger.scanLimitReached,
26500:             scanCancelled: ledger.scanCancelled
26501:         }) : [];
26502:         report.chartBlob = state.discordReport.includeChart ? await buildFinancialChartBlob(report) : null;
26503:         return report;
26504:     }
26505: 
26506:     function escapeDiscordMarkdown(value) {
26507:         return String(value || '')
```

## Line 26443

`const reconciliationLabel = balanceAvailable ? reconciliation.label : 'Balance unavailable';`

```javascript
26398:         if (allAvailable) {
26399:             financeArchiveScanBusy = true;
26400:             financeArchiveScanCancelled = false;
26401:         }
26402:         let ledger;
26403:         try {
26404:             ledger = await fetchFinancialLedger(requiredStartMs, 0, false, false);
26405:         } finally {
26406:             if (allAvailable) {
26407:                 financeArchiveScanBusy = false;
26408:                 financeArchiveScanCancelled = false;
26409:             }
26410:         }
26411:         if (allAvailable) {
26412:             const oldest = ledger.oldestTimestamp || ledger.entries[0]?.timestamp || Date.now();
26413:             period = {
26414:                 ...period,
26415:                 startMs: oldest,
26416:                 durationMs: Math.max(1, period.endMs - oldest),
26417:                 comparisonStartMs: 0,
26418:                 comparisonEndMs: 0,
26419:                 rangeLabel: formatPeriodRange(oldest, period.endMs),
26420:                 comparisonRangeLabel: 'Not applicable'
26421:             };
26422:         }
26423:         const currentTransactions = [];
26424:         const previousTransactions = [];
26425:         let afterPeriodNet = 0;
26426:         const now = Date.now();
26427:         for (const entry of ledger.entries) {
26428:             if (entry.timestamp >= period.startMs && entry.timestamp < period.endMs) currentTransactions.push(entry);
26429:             else if (comparisonEnabled && entry.timestamp >= period.comparisonStartMs && entry.timestamp < period.comparisonEndMs) previousTransactions.push(entry);
26430:             if (entry.timestamp >= period.endMs && entry.timestamp <= now) afterPeriodNet += entry.amount;
26431:         }
26432: 
26433:         const current = summariseFinancialTransactions(currentTransactions, period);
26434:         const previousPeriod = { ...period, startMs: period.comparisonStartMs, endMs: period.comparisonEndMs, durationMs: period.durationMs };
26435:         const previous = comparisonEnabled ? summariseFinancialTransactions(previousTransactions, previousPeriod) : null;
26436:         const comparison = previous ? buildFinancialComparison(current, previous) : null;
26437:         const account = ledger.account;
26438:         const currentBalance = Number.isFinite(account?.currentBalance) ? account.currentBalance : null;
26439:         const closingBalance = currentBalance === null ? null : currentBalance - afterPeriodNet;
26440:         const openingBalance = closingBalance === null ? null : closingBalance - current.net;
26441:         const balanceAvailable = openingBalance !== null && closingBalance !== null;
26442:         const reconciliation = calculateVaultReconciliation(ledger.vault, period, ledger.entries, currentBalance);
26443:         const reconciliationLabel = balanceAvailable ? reconciliation.label : 'Balance unavailable';
26444:         const drawdown = calculateFinancialDrawdown(openingBalance, current.transactions);
26445:         const scorecard = calculateFinancialScorecard(current, comparison, { complete: ledger.complete, balanceAvailable, reconciled: reconciliation.reconciled, closingBalance });
26446:         let forecastSummary = current;
26447:         let forecastPeriod = period;
26448:         if (state.discordReport.includeForecast && period.durationMs > 30 * 86400000) {
26449:             const recentStart = Math.max(period.startMs, period.endMs - 30 * 86400000);
26450:             const recentTransactions = currentTransactions.filter(entry => entry.timestamp >= recentStart);
26451:             forecastPeriod = { ...period, startMs: recentStart, durationMs: Math.max(1, period.endMs - recentStart), id: 'recent30' };
26452:             forecastSummary = summariseFinancialTransactions(recentTransactions, forecastPeriod);
26453:         }
26454:         const forecast = state.discordReport.includeForecast ? { ...buildFinancialForecast(forecastSummary, forecastPeriod, closingBalance), basisDays: Math.max(1, Math.round(forecastPeriod.durationMs / 86400000)) } : null;
26455:         const report = {
26456:             generatedAt: Date.now(),
26457:             signature: currentFinancialReportSignature(),
26458:             period,
26459:             reportDate: localIsoDate(),
26460:             reportDateLabel: `${period.label} · ${period.rangeLabel}`,
26461:             userName: account?.userName || ledger.vault?.player?.name || '',
26462:             userId: account?.userId || ledger.vault?.player?.id || null,
26463:             currentBalance,
26464:             openingBalance,
26465:             closingBalance,
26466:             reconciliationDifference: reconciliation.difference,
26467:             reconciled: reconciliation.reconciled,
26468:             balanceCalculated: balanceAvailable,
26469:             reconciliationLabel,
26470:             ledgerComplete: ledger.complete,
26471:             ledgerCoverageReached: ledger.coverageReached,
26472:             ledgerPages: ledger.pageCount,
26473:             ledgerLastPage: ledger.lastPage,
26474:             ledgerStable: ledger.ledgerStable,
26475:             ledgerScanRetries: ledger.scanRetries,
26476:             ledgerScanCancelled: ledger.scanCancelled,
26477:             ledgerScanLimitReached: ledger.scanLimitReached,
26478:             ledgerSource: ledger.ledgerSource,
26479:             archiveComplete: ledger.archiveComplete,
26480:             archiveTruncated: ledger.archiveTruncated,
26481:             droppedTransactions: ledger.droppedTransactions,
26482:             vaultTransactionCount: ledger.vaultTransactionCount,
26483:             invalidTimestampCount: ledger.invalidTimestampCount,
26484:             comparison,
26485:             previous,
26486:             scorecard,
26487:             grade: { score: scorecard.overall, grade: scorecard.grade, label: scorecard.label, marginPercent: scorecard.operatingMarginPercent },
26488:             forecast,
26489:             drawdown,
26490:             chartBlob: null,
26491:             ...current
26492:         };
26493:         report.riskAlerts = state.discordReport.includeRisk ? buildFinancialRiskAlerts(current, comparison, {
26494:             ledgerComplete: ledger.complete,
26495:             drawdown,
26496:             scorecard,
26497:             archiveTruncated: ledger.archiveTruncated,
26498:             droppedTransactions: ledger.droppedTransactions,
26499:             scanLimitReached: ledger.scanLimitReached,
26500:             scanCancelled: ledger.scanCancelled
26501:         }) : [];
26502:         report.chartBlob = state.discordReport.includeChart ? await buildFinancialChartBlob(report) : null;
26503:         return report;
26504:     }
26505: 
26506:     function escapeDiscordMarkdown(value) {
26507:         return String(value || '')
26508:             .replace(/\\/gu, '\\\\')
```

## Line 26466

`reconciliationDifference: reconciliation.difference,`

```javascript
26421:             };
26422:         }
26423:         const currentTransactions = [];
26424:         const previousTransactions = [];
26425:         let afterPeriodNet = 0;
26426:         const now = Date.now();
26427:         for (const entry of ledger.entries) {
26428:             if (entry.timestamp >= period.startMs && entry.timestamp < period.endMs) currentTransactions.push(entry);
26429:             else if (comparisonEnabled && entry.timestamp >= period.comparisonStartMs && entry.timestamp < period.comparisonEndMs) previousTransactions.push(entry);
26430:             if (entry.timestamp >= period.endMs && entry.timestamp <= now) afterPeriodNet += entry.amount;
26431:         }
26432: 
26433:         const current = summariseFinancialTransactions(currentTransactions, period);
26434:         const previousPeriod = { ...period, startMs: period.comparisonStartMs, endMs: period.comparisonEndMs, durationMs: period.durationMs };
26435:         const previous = comparisonEnabled ? summariseFinancialTransactions(previousTransactions, previousPeriod) : null;
26436:         const comparison = previous ? buildFinancialComparison(current, previous) : null;
26437:         const account = ledger.account;
26438:         const currentBalance = Number.isFinite(account?.currentBalance) ? account.currentBalance : null;
26439:         const closingBalance = currentBalance === null ? null : currentBalance - afterPeriodNet;
26440:         const openingBalance = closingBalance === null ? null : closingBalance - current.net;
26441:         const balanceAvailable = openingBalance !== null && closingBalance !== null;
26442:         const reconciliation = calculateVaultReconciliation(ledger.vault, period, ledger.entries, currentBalance);
26443:         const reconciliationLabel = balanceAvailable ? reconciliation.label : 'Balance unavailable';
26444:         const drawdown = calculateFinancialDrawdown(openingBalance, current.transactions);
26445:         const scorecard = calculateFinancialScorecard(current, comparison, { complete: ledger.complete, balanceAvailable, reconciled: reconciliation.reconciled, closingBalance });
26446:         let forecastSummary = current;
26447:         let forecastPeriod = period;
26448:         if (state.discordReport.includeForecast && period.durationMs > 30 * 86400000) {
26449:             const recentStart = Math.max(period.startMs, period.endMs - 30 * 86400000);
26450:             const recentTransactions = currentTransactions.filter(entry => entry.timestamp >= recentStart);
26451:             forecastPeriod = { ...period, startMs: recentStart, durationMs: Math.max(1, period.endMs - recentStart), id: 'recent30' };
26452:             forecastSummary = summariseFinancialTransactions(recentTransactions, forecastPeriod);
26453:         }
26454:         const forecast = state.discordReport.includeForecast ? { ...buildFinancialForecast(forecastSummary, forecastPeriod, closingBalance), basisDays: Math.max(1, Math.round(forecastPeriod.durationMs / 86400000)) } : null;
26455:         const report = {
26456:             generatedAt: Date.now(),
26457:             signature: currentFinancialReportSignature(),
26458:             period,
26459:             reportDate: localIsoDate(),
26460:             reportDateLabel: `${period.label} · ${period.rangeLabel}`,
26461:             userName: account?.userName || ledger.vault?.player?.name || '',
26462:             userId: account?.userId || ledger.vault?.player?.id || null,
26463:             currentBalance,
26464:             openingBalance,
26465:             closingBalance,
26466:             reconciliationDifference: reconciliation.difference,
26467:             reconciled: reconciliation.reconciled,
26468:             balanceCalculated: balanceAvailable,
26469:             reconciliationLabel,
26470:             ledgerComplete: ledger.complete,
26471:             ledgerCoverageReached: ledger.coverageReached,
26472:             ledgerPages: ledger.pageCount,
26473:             ledgerLastPage: ledger.lastPage,
26474:             ledgerStable: ledger.ledgerStable,
26475:             ledgerScanRetries: ledger.scanRetries,
26476:             ledgerScanCancelled: ledger.scanCancelled,
26477:             ledgerScanLimitReached: ledger.scanLimitReached,
26478:             ledgerSource: ledger.ledgerSource,
26479:             archiveComplete: ledger.archiveComplete,
26480:             archiveTruncated: ledger.archiveTruncated,
26481:             droppedTransactions: ledger.droppedTransactions,
26482:             vaultTransactionCount: ledger.vaultTransactionCount,
26483:             invalidTimestampCount: ledger.invalidTimestampCount,
26484:             comparison,
26485:             previous,
26486:             scorecard,
26487:             grade: { score: scorecard.overall, grade: scorecard.grade, label: scorecard.label, marginPercent: scorecard.operatingMarginPercent },
26488:             forecast,
26489:             drawdown,
26490:             chartBlob: null,
26491:             ...current
26492:         };
26493:         report.riskAlerts = state.discordReport.includeRisk ? buildFinancialRiskAlerts(current, comparison, {
26494:             ledgerComplete: ledger.complete,
26495:             drawdown,
26496:             scorecard,
26497:             archiveTruncated: ledger.archiveTruncated,
26498:             droppedTransactions: ledger.droppedTransactions,
26499:             scanLimitReached: ledger.scanLimitReached,
26500:             scanCancelled: ledger.scanCancelled
26501:         }) : [];
26502:         report.chartBlob = state.discordReport.includeChart ? await buildFinancialChartBlob(report) : null;
26503:         return report;
26504:     }
26505: 
26506:     function escapeDiscordMarkdown(value) {
26507:         return String(value || '')
26508:             .replace(/\\/gu, '\\\\')
26509:             .replace(/([`*_~>|])/gu, '\\$1')
26510:             .replace(/@/gu, '@\u200b');
26511:     }
26512: 
26513:     function truncateDiscord(value, maximum = DISCORD_MAX_FIELD_LENGTH) {
26514:         const text = String(value || '');
26515:         return text.length <= maximum ? text : `${text.slice(0, Math.max(0, maximum - 1))}…`;
26516:     }
26517: 
26518:     function buildDiscordCategoryBreakdown(entries, prefix, limit) {
26519:         const rows = entries.slice(0, limit);
26520:         if (!rows.length) return 'No entries recorded.';
26521:         return truncateDiscord(rows.map(entry => `• **${escapeDiscordMarkdown(entry.label)}** — ${prefix}${entry.total.toLocaleString('en-GB')} Credits · ${entry.count.toLocaleString('en-GB')} entr${entry.count === 1 ? 'y' : 'ies'}`).join('\n'));
26522:     }
26523: 
26524:     function buildDiscordTopPayouts(report, limit = 5) {
26525:         if (!report.topPayouts.length) return 'No positive payouts recorded.';
26526:         return truncateDiscord(report.topPayouts.slice(0, limit).map((entry, index) => `${index + 1}. **${escapeDiscordMarkdown(entry.description)}** — +${entry.amount.toLocaleString('en-GB')} Credits`).join('\n'));
26527:     }
26528: 
26529:     function buildDiscordComparisonField(report) {
26530:         if (!report.comparison || !report.previous) return 'Comparison disabled.';
26531:         return [
```

## Line 26469

`reconciliationLabel,`

```javascript
26424:         const previousTransactions = [];
26425:         let afterPeriodNet = 0;
26426:         const now = Date.now();
26427:         for (const entry of ledger.entries) {
26428:             if (entry.timestamp >= period.startMs && entry.timestamp < period.endMs) currentTransactions.push(entry);
26429:             else if (comparisonEnabled && entry.timestamp >= period.comparisonStartMs && entry.timestamp < period.comparisonEndMs) previousTransactions.push(entry);
26430:             if (entry.timestamp >= period.endMs && entry.timestamp <= now) afterPeriodNet += entry.amount;
26431:         }
26432: 
26433:         const current = summariseFinancialTransactions(currentTransactions, period);
26434:         const previousPeriod = { ...period, startMs: period.comparisonStartMs, endMs: period.comparisonEndMs, durationMs: period.durationMs };
26435:         const previous = comparisonEnabled ? summariseFinancialTransactions(previousTransactions, previousPeriod) : null;
26436:         const comparison = previous ? buildFinancialComparison(current, previous) : null;
26437:         const account = ledger.account;
26438:         const currentBalance = Number.isFinite(account?.currentBalance) ? account.currentBalance : null;
26439:         const closingBalance = currentBalance === null ? null : currentBalance - afterPeriodNet;
26440:         const openingBalance = closingBalance === null ? null : closingBalance - current.net;
26441:         const balanceAvailable = openingBalance !== null && closingBalance !== null;
26442:         const reconciliation = calculateVaultReconciliation(ledger.vault, period, ledger.entries, currentBalance);
26443:         const reconciliationLabel = balanceAvailable ? reconciliation.label : 'Balance unavailable';
26444:         const drawdown = calculateFinancialDrawdown(openingBalance, current.transactions);
26445:         const scorecard = calculateFinancialScorecard(current, comparison, { complete: ledger.complete, balanceAvailable, reconciled: reconciliation.reconciled, closingBalance });
26446:         let forecastSummary = current;
26447:         let forecastPeriod = period;
26448:         if (state.discordReport.includeForecast && period.durationMs > 30 * 86400000) {
26449:             const recentStart = Math.max(period.startMs, period.endMs - 30 * 86400000);
26450:             const recentTransactions = currentTransactions.filter(entry => entry.timestamp >= recentStart);
26451:             forecastPeriod = { ...period, startMs: recentStart, durationMs: Math.max(1, period.endMs - recentStart), id: 'recent30' };
26452:             forecastSummary = summariseFinancialTransactions(recentTransactions, forecastPeriod);
26453:         }
26454:         const forecast = state.discordReport.includeForecast ? { ...buildFinancialForecast(forecastSummary, forecastPeriod, closingBalance), basisDays: Math.max(1, Math.round(forecastPeriod.durationMs / 86400000)) } : null;
26455:         const report = {
26456:             generatedAt: Date.now(),
26457:             signature: currentFinancialReportSignature(),
26458:             period,
26459:             reportDate: localIsoDate(),
26460:             reportDateLabel: `${period.label} · ${period.rangeLabel}`,
26461:             userName: account?.userName || ledger.vault?.player?.name || '',
26462:             userId: account?.userId || ledger.vault?.player?.id || null,
26463:             currentBalance,
26464:             openingBalance,
26465:             closingBalance,
26466:             reconciliationDifference: reconciliation.difference,
26467:             reconciled: reconciliation.reconciled,
26468:             balanceCalculated: balanceAvailable,
26469:             reconciliationLabel,
26470:             ledgerComplete: ledger.complete,
26471:             ledgerCoverageReached: ledger.coverageReached,
26472:             ledgerPages: ledger.pageCount,
26473:             ledgerLastPage: ledger.lastPage,
26474:             ledgerStable: ledger.ledgerStable,
26475:             ledgerScanRetries: ledger.scanRetries,
26476:             ledgerScanCancelled: ledger.scanCancelled,
26477:             ledgerScanLimitReached: ledger.scanLimitReached,
26478:             ledgerSource: ledger.ledgerSource,
26479:             archiveComplete: ledger.archiveComplete,
26480:             archiveTruncated: ledger.archiveTruncated,
26481:             droppedTransactions: ledger.droppedTransactions,
26482:             vaultTransactionCount: ledger.vaultTransactionCount,
26483:             invalidTimestampCount: ledger.invalidTimestampCount,
26484:             comparison,
26485:             previous,
26486:             scorecard,
26487:             grade: { score: scorecard.overall, grade: scorecard.grade, label: scorecard.label, marginPercent: scorecard.operatingMarginPercent },
26488:             forecast,
26489:             drawdown,
26490:             chartBlob: null,
26491:             ...current
26492:         };
26493:         report.riskAlerts = state.discordReport.includeRisk ? buildFinancialRiskAlerts(current, comparison, {
26494:             ledgerComplete: ledger.complete,
26495:             drawdown,
26496:             scorecard,
26497:             archiveTruncated: ledger.archiveTruncated,
26498:             droppedTransactions: ledger.droppedTransactions,
26499:             scanLimitReached: ledger.scanLimitReached,
26500:             scanCancelled: ledger.scanCancelled
26501:         }) : [];
26502:         report.chartBlob = state.discordReport.includeChart ? await buildFinancialChartBlob(report) : null;
26503:         return report;
26504:     }
26505: 
26506:     function escapeDiscordMarkdown(value) {
26507:         return String(value || '')
26508:             .replace(/\\/gu, '\\\\')
26509:             .replace(/([`*_~>|])/gu, '\\$1')
26510:             .replace(/@/gu, '@\u200b');
26511:     }
26512: 
26513:     function truncateDiscord(value, maximum = DISCORD_MAX_FIELD_LENGTH) {
26514:         const text = String(value || '');
26515:         return text.length <= maximum ? text : `${text.slice(0, Math.max(0, maximum - 1))}…`;
26516:     }
26517: 
26518:     function buildDiscordCategoryBreakdown(entries, prefix, limit) {
26519:         const rows = entries.slice(0, limit);
26520:         if (!rows.length) return 'No entries recorded.';
26521:         return truncateDiscord(rows.map(entry => `• **${escapeDiscordMarkdown(entry.label)}** — ${prefix}${entry.total.toLocaleString('en-GB')} Credits · ${entry.count.toLocaleString('en-GB')} entr${entry.count === 1 ? 'y' : 'ies'}`).join('\n'));
26522:     }
26523: 
26524:     function buildDiscordTopPayouts(report, limit = 5) {
26525:         if (!report.topPayouts.length) return 'No positive payouts recorded.';
26526:         return truncateDiscord(report.topPayouts.slice(0, limit).map((entry, index) => `${index + 1}. **${escapeDiscordMarkdown(entry.description)}** — +${entry.amount.toLocaleString('en-GB')} Credits`).join('\n'));
26527:     }
26528: 
26529:     function buildDiscordComparisonField(report) {
26530:         if (!report.comparison || !report.previous) return 'Comparison disabled.';
26531:         return [
26532:             `Income: **${formatPercentageChange(report.comparison.incomeChange)}**`,
26533:             `Operating result: **${formatPercentageChange(report.comparison.operatingResultChange)}**`,
26534:             `Capital deployed: **${formatPercentageChange(report.comparison.capitalInvestmentChange)}**`,
```

## Line 26581

``Balance audit: **${escapeDiscordMarkdown(report.reconciliationLabel)}**`,`

```javascript
26536:             `Mission count: **${report.comparison.missionChange > 0 ? '+' : ''}${report.comparison.missionChange.toLocaleString('en-GB')}**`,
26537:             `Average mission reward: **${formatPercentageChange(report.comparison.averageRewardChange)}**`
26538:         ].join('\n');
26539:     }
26540: 
26541:     function buildDiscordScorecardField(report) {
26542:         const score = report.scorecard;
26543:         return [
26544:             `Overall: **${score.grade} · ${score.overall}/100** — ${score.label}`,
26545:             `Revenue **${score.revenue}** · Efficiency **${score.efficiency}**`,
26546:             `Liquidity **${score.liquidity}** · Growth **${score.growth}**`,
26547:             `Audit confidence **${score.confidence}**${score.runwayDays === null ? '' : ` · Runway **${score.runwayDays.toLocaleString('en-GB')}d**`}`
26548:         ].join('\n');
26549:     }
26550: 
26551:     function buildDiscordRiskField(report) {
26552:         if (!report.riskAlerts?.length) return 'Risk analysis disabled.';
26553:         return truncateDiscord(report.riskAlerts.map(alert => {
26554:             const symbol = alert.severity === 'high' ? '🔴' : alert.severity === 'medium' ? '🟠' : alert.severity === 'low' ? '🟡' : '🟢';
26555:             return `${symbol} **${escapeDiscordMarkdown(alert.title)}** — ${escapeDiscordMarkdown(alert.detail)}`;
26556:         }).join('\n'), 1000);
26557:     }
26558: 
26559:     function buildDiscordForecastField(report) {
26560:         const forecast = report.forecast;
26561:         if (!forecast) return 'Forecasting disabled.';
26562:         return [
26563:             forecast.endOfDayIncome === null ? '' : `Projected end-of-day income: **${formatPlainCredits(forecast.endOfDayIncome)}**`,
26564:             `7-day income pace: **${formatPlainCredits(forecast.sevenDayIncome)}**`,
26565:             `30-day income pace: **${formatPlainCredits(forecast.thirtyDayIncome)}**`,
26566:             forecast.recoveryDays === null ? 'Capital recovery: **No positive operating pace available**' : `Capital recovery: **${forecast.recoveryDays.toLocaleString('en-GB')} days**`,
26567:             forecast.projectedSevenDayBalance === null ? '' : `Projected 7-day reserve: **${formatPlainCredits(forecast.projectedSevenDayBalance)}**`,
26568:             `Confidence: **${forecast.confidence}** · basis **${Number(forecast.basisDays || 1).toLocaleString('en-GB')} day${Number(forecast.basisDays || 1) === 1 ? '' : 's'}**`
26569:         ].filter(Boolean).join('\n');
26570:     }
26571: 
26572: 
26573:     function buildDiscordDataQualityField(report) {
26574:         const coverage = report.archiveComplete ? 'Complete accessible archive' : report.archiveTruncated ? 'Local archive capped' : report.ledgerComplete ? 'Full requested-period coverage' : 'Partial requested-period coverage';
26575:         return [
26576:             `Ledger source: **${escapeDiscordMarkdown(report.ledgerSource || 'MissionChief ledger')}**`,
26577:             `Archive history: **${Number(report.vaultTransactionCount || 0).toLocaleString('en-GB')} transactions** · **${coverage}**`,
26578:             `MissionChief pages: **${Number(report.ledgerPages || 0).toLocaleString('en-GB')} read / ${Number(report.ledgerLastPage || 0).toLocaleString('en-GB')} available**`,
26579:             `Classification confidence: **${report.classificationConfidence.toLocaleString('en-GB')}%** · rules **${escapeDiscordMarkdown(activeFinancialRuleVersion)}** · policy **${escapeDiscordMarkdown(activeFinancialPolicyVersion)}**`,
26580:             `Unclassified: **${report.unclassifiedCount.toLocaleString('en-GB')}** · ${formatPlainCredits(report.unclassifiedAmount)}`,
26581:             `Balance audit: **${escapeDiscordMarkdown(report.reconciliationLabel)}**`,
26582:             `${report.ledgerStable ? 'Ledger head remained stable' : 'New activity arrived during scanning; the local archive was left safely resumable'}${report.ledgerScanRetries ? ` · ${report.ledgerScanRetries} restart` : ''}${report.invalidTimestampCount ? ` · ${report.invalidTimestampCount} invalid timestamp rows` : ''}${report.ledgerScanLimitReached ? ' · page safety cap reached' : ''}${report.ledgerScanCancelled ? ' · scan stopped by user' : ''}`
26583:         ].join('\n');
26584:     }
26585: 
26586:     function discordEmbedCharacterCount(embed) {
26587:         let total = String(embed?.title || '').length + String(embed?.description || '').length + String(embed?.footer?.text || '').length + String(embed?.author?.name || '').length;
26588:         for (const field of embed?.fields || []) total += String(field.name || '').length + String(field.value || '').length;
26589:         return total;
26590:     }
26591: 
26592:     function fitDiscordEmbedsToBudget(embeds, maximum = 5900) {
26593:         const result = embeds.map(embed => ({ ...embed, fields: (embed.fields || []).map(field => ({ ...field })) }));
26594:         const count = () => result.reduce((sum, embed) => sum + discordEmbedCharacterCount(embed), 0);
26595:         const optionalNames = ['🏆 Highest Payouts', '📊 Previous Period', '🔭 Forecast', '🗄️ Archive Coverage'];
26596:         while (count() > maximum && optionalNames.length) {
26597:             const name = optionalNames.shift();
26598:             for (const embed of result) {
26599:                 const index = embed.fields.findIndex(field => field.name === name);
26600:                 if (index >= 0) { embed.fields.splice(index, 1); break; }
26601:             }
26602:         }
26603:         for (const embed of result) {
26604:             embed.description = truncateDiscord(embed.description || '', 3800);
26605:             embed.fields = embed.fields.slice(0, 25).map(field => ({ ...field, name: truncateDiscord(field.name, 256), value: truncateDiscord(field.value, 1000) }));
26606:         }
26607:         return result;
26608:     }
26609: 
26610:     function buildDiscordFinancialPayload(report, { withAttachment = false } = {}) {
26611:         const operatingTone = reportTone(report.operatingResult);
26612:         const colour = operatingTone === 'positive' ? 0x2ecc71 : operatingTone === 'negative' ? 0xe74c3c : 0xf1c40f;
26613:         const topLimit = state.discordReport.topCategories;
26614:         const condition = report.operatingResult > 0 ? 'POSITIVE OPERATING RESULT' : report.operatingResult < 0 ? 'NEGATIVE OPERATING RESULT' : 'OPERATING BREAK EVEN';
26615:         const description = [
26616:             `**${escapeDiscordMarkdown(report.period.label)}**`,
26617:             escapeDiscordMarkdown(report.period.rangeLabel),
26618:             `${condition} · **${formatSignedCredits(report.operatingResult)}**`,
26619:             `Net credit movement after investment: **${formatSignedCredits(report.net)}**`,
26620:             report.userName ? `Account: **${escapeDiscordMarkdown(report.userName)}**${report.userId ? ` · ID ${escapeDiscordMarkdown(report.userId)}` : ''}` : '',
26621:             report.period.note ? `_${escapeDiscordMarkdown(report.period.note)}_` : ''
26622:         ].filter(Boolean).join('\n');
26623: 
26624:         const balanceLines = report.openingBalance === null || report.closingBalance === null
26625:             ? ['Balance data was unavailable.']
26626:             : [
26627:                 `Opening: **${report.openingBalance.toLocaleString('en-GB')} Credits**`,
26628:                 `Closing: **${report.closingBalance.toLocaleString('en-GB')} Credits**`,
26629:                 `Peak: **${report.drawdown.peakBalance === null ? 'Unavailable' : report.drawdown.peakBalance.toLocaleString('en-GB')}**`,
26630:                 `Largest drawdown: **${report.drawdown.largestDrawdown === null ? 'Unavailable' : formatPlainCredits(report.drawdown.largestDrawdown)}${report.drawdown.largestDrawdownPercent === null ? '' : ` · ${report.drawdown.largestDrawdownPercent.toLocaleString('en-GB')}%`}**`
26631:             ];
26632: 
26633:         const productivity = [
26634:             `Missions/transport rewards: **${report.missionCount.toLocaleString('en-GB')}**`,
26635:             `Active time estimate: **${report.activeHours.toLocaleString('en-GB')}h**`,
26636:             `Active-hour income: **${formatPlainCredits(report.activeIncomePerHour)}**`,
26637:             `Calendar-hour income: **${formatPlainCredits(report.incomePerHour)}**`,
26638:             `Average / median mission: **${formatPlainCredits(report.averageMissionReward)} / ${formatPlainCredits(report.medianMissionReward)}**`,
26639:             `Alliance / personal share: **${report.allianceIncomePercent.toLocaleString('en-GB')}% / ${report.personalIncomePercent.toLocaleString('en-GB')}%**`
26640:         ].join('\n');
26641: 
26642:         const executive = {
26643:             title: '📈 MissionChief Financial Command — Executive Audit',
26644:             description: truncateDiscord(description, 4096),
26645:             color: colour,
26646:             timestamp: new Date(report.generatedAt).toISOString(),
```

## Line 26810

`['Audit basis', report.reconciliationLabel]`

```javascript
26765:             context.fillStyle = '#ffffff';
26766:             context.font = '800 19px Arial, sans-serif';
26767:             context.fillText('CREDIT MOVEMENT TREND', chartX + 22, chartY + 32);
26768:             const buckets = report.buckets.slice(-12);
26769:             const maxMagnitude = Math.max(1, ...buckets.map(bucket => Math.abs(bucket.net)));
26770:             const plotTop = chartY + 58;
26771:             const plotBottom = chartY + chartH - 38;
26772:             const zeroY = plotTop + (plotBottom - plotTop) / 2;
26773:             context.strokeStyle = 'rgba(255,255,255,0.14)';
26774:             context.lineWidth = 1;
26775:             context.beginPath();
26776:             context.moveTo(chartX + 22, zeroY);
26777:             context.lineTo(chartX + chartW - 22, zeroY);
26778:             context.stroke();
26779:             const slotW = (chartW - 52) / Math.max(1, buckets.length);
26780:             buckets.forEach((bucket, index) => {
26781:                 const height = Math.max(2, Math.abs(bucket.net) / maxMagnitude * ((plotBottom - plotTop) / 2 - 8));
26782:                 const x = chartX + 29 + index * slotW;
26783:                 const y = bucket.net >= 0 ? zeroY - height : zeroY;
26784:                 roundRectPath(context, x, y, Math.max(8, slotW - 10), height, 4);
26785:                 context.fillStyle = bucket.net >= 0 ? '#2ecc71' : '#e74c3c';
26786:                 context.fill();
26787:                 context.fillStyle = 'rgba(255,255,255,0.52)';
26788:                 context.font = '600 11px Arial, sans-serif';
26789:                 context.textAlign = 'center';
26790:                 context.fillText(bucket.label, x + Math.max(8, slotW - 10) / 2, chartY + chartH - 15);
26791:             });
26792:             context.textAlign = 'left';
26793: 
26794:             const detailX = 810;
26795:             const detailY = 288;
26796:             const detailW = 334;
26797:             const detailH = 250;
26798:             roundRectPath(context, detailX, detailY, detailW, detailH, 18);
26799:             context.fillStyle = 'rgba(255,255,255,0.04)';
26800:             context.fill();
26801:             context.fillStyle = '#ffffff';
26802:             context.font = '800 19px Arial, sans-serif';
26803:             context.fillText('OPERATING SNAPSHOT', detailX + 22, detailY + 32);
26804:             const lines = [
26805:                 ['Operating result', formatSignedCompactCredits(report.operatingResult)],
26806:                 ['Capital deployed', formatSignedCompactCredits(-Math.abs(report.capitalInvestment || 0))],
26807:                 ['Active-hour income', formatSignedCompactCredits(report.activeIncomePerHour || report.incomePerHour)],
26808:                 ['Classification', `${Number(report.classificationConfidence || 0).toLocaleString('en-GB', { maximumFractionDigits: 1 })}%`],
26809:                 ['Condition score', `${Number(report.scorecard?.overall || 0).toLocaleString('en-GB', { maximumFractionDigits: 0 })}/100`],
26810:                 ['Audit basis', report.reconciliationLabel]
26811:             ];
26812:             lines.forEach((line, index) => {
26813:                 const y = detailY + 65 + index * 29;
26814:                 context.fillStyle = 'rgba(255,255,255,0.58)';
26815:                 context.font = '600 15px Arial, sans-serif';
26816:                 context.fillText(line[0], detailX + 22, y);
26817:                 context.fillStyle = '#ffffff';
26818:                 context.font = '800 15px Arial, sans-serif';
26819:                 context.textAlign = 'right';
26820:                 context.fillText(String(line[1]), detailX + detailW - 22, y);
26821:                 context.textAlign = 'left';
26822:             });
26823: 
26824:             context.fillStyle = 'rgba(255,255,255,0.42)';
26825:             context.font = '600 14px Arial, sans-serif';
26826:             context.fillText(`${report.activityCount.toLocaleString('en-GB')} transactions · ${report.ledgerPages.toLocaleString('en-GB')} ledger pages · Generated ${new Date(report.generatedAt).toLocaleString('en-GB')}`, 54, 620);
26827:             context.fillStyle = 'rgba(255,255,255,0.27)';
26828:             context.font = '600 12px Arial, sans-serif';
26829:             context.fillText(`${SCRIPT.name} v${SCRIPT.version} · Deterministic local financial audit · projections are estimates`, 54, 648);
26830: 
26831:             return await new Promise(resolve => {
26832:                 canvas.toBlob(resolve, 'image/png', 0.92);
26833:             });
26834:         } catch (err) {
26835:             return null;
26836:         }
26837:     }
26838: 
26839:     function discordRetryDelayMs(response, attempt = 0) {
26840:         const headerText = String(response?.responseHeaders || '');
26841:         const retryHeader = headerText.match(/^retry-after:\s*([\d.]+)/imu);
26842:         if (retryHeader) {
26843:             const value = Number(retryHeader[1]);
26844:             if (Number.isFinite(value)) return Math.max(250, value > 1000 ? value : value * 1000);
26845:         }
26846:         try {
26847:             const body = JSON.parse(response?.responseText || '{}');
26848:             const retryAfter = Number(body?.retry_after);
26849:             if (Number.isFinite(retryAfter)) return Math.max(250, retryAfter > 1000 ? retryAfter : retryAfter * 1000);
26850:         } catch (err) {}
26851:         return Math.min(10000, 750 * Math.pow(2, attempt));
26852:     }
26853: 
26854:     async function sendDiscordWithRetry(factory, maximumAttempts = 3) {
26855:         let response = null;
26856:         for (let attempt = 0; attempt < maximumAttempts; attempt++) {
26857:             response = await factory();
26858:             if (response.status !== 429 && response.status < 500) return response;
26859:             if (attempt >= maximumAttempts - 1) return response;
26860:             const delayMs = discordRetryDelayMs(response, attempt);
26861:             setDiscordStatus(`Discord delivery delayed by rate limits. Retrying in ${Math.ceil(delayMs / 1000)}s…`, 'busy');
26862:             if (!await runtimeDelay(delayMs)) throw new Error('Toolkit runtime stopped during Discord retry.');
26863:         }
26864:         return response;
26865:     }
26866: 
26867:     async function sendDiscordFinancialPayload(webhookUrl, report) {
26868:         const hasChart = Boolean(report.chartBlob && state.discordReport.includeChart);
26869:         const payload = buildDiscordFinancialPayload(report, { withAttachment: hasChart });
26870:         let response;
26871:         if (hasChart) {
26872:             response = await sendDiscordWithRetry(() => {
26873:                 const formData = new FormData();
26874:                 formData.append('payload_json', JSON.stringify(payload));
26875:                 formData.append('files[0]', report.chartBlob, FINANCE_CHART_FILENAME);
```
