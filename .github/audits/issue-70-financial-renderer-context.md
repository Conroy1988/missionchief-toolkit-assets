# Issue #70 Financial Command renderer inspection

Canonical source: `src/MissionChief_Map_Command_Toolkit.user.js`
Source lines: **29882**
Matched locations: **2**

## Match at line 26243

Matched source: `label: Math.abs(difference) <= 1 ? 'Reconciled against saved balance checkpoints' : `Checkpoint variance ${formatSignedCredits(difference)}`,`

```javascript
26153:             otherIncome,
26154:             operatingExpense,
26155:             capitalInvestment,
26156:             operatingResult,
26157:             net,
26158:             incomeCount,
26159:             spendingCount,
26160:             activityCount: incomeCount + spendingCount,
26161:             missionCount,
26162:             missionIncome,
26163:             averageIncome: incomeCount ? Math.round(income / incomeCount) : 0,
26164:             averageSpend: spendingCount ? Math.round(spending / spendingCount) : 0,
26165:             averageMissionReward: missionCount ? Math.round(missionIncome / missionCount) : 0,
26166:             medianMissionReward: medianNumber(missionPayoutValues),
26167:             largestReward,
26168:             smallestReward: Number.isFinite(smallestReward) ? smallestReward : 0,
26169:             largestSpend,
26170:             allianceIncome,
26171:             personalIncome,
26172:             transportIncome,
26173:             allianceIncomePercent: income ? Math.round((allianceIncome / income) * 1000) / 10 : 0,
26174:             personalIncomePercent: income ? Math.round((personalIncome / income) * 1000) / 10 : 0,
26175:             incomePerHour: Math.round(income / calendarHours),
26176:             activeIncomePerHour: Math.round(income / activeHours),
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
26288:         confidence = Math.round(clamp(confidence, 0, 100, 75));
26289: 
26290:         const overall = Math.round(revenue * 0.25 + efficiency * 0.25 + liquidity * 0.20 + growth * 0.15 + confidence * 0.15);
26291:         const assessment = financialScoreLabel(overall);
26292:         return {
26293:             overall,
26294:             grade: assessment.grade,
26295:             label: assessment.label,
26296:             revenue,
26297:             efficiency,
26298:             liquidity,
26299:             growth,
26300:             confidence,
26301:             runwayDays: runwayDays === null ? null : Math.round(runwayDays * 10) / 10,
26302:             operatingMarginPercent: summary.operatingMarginPercent
26303:         };
26304:     }
26305: 
26306:     function calculateFinancialDrawdown(openingBalance, transactions) {
26307:         if (!Number.isFinite(Number(openingBalance))) return { peakBalance: null, lowBalance: null, largestDrawdown: null, largestDrawdownPercent: null };
26308:         let balance = Number(openingBalance);
26309:         let peak = balance;
26310:         let low = balance;
26311:         let largestDrawdown = 0;
26312:         let largestDrawdownPercent = 0;
26313:         for (const entry of transactions.slice().sort((a, b) => a.timestamp - b.timestamp)) {
26314:             balance += Number(entry.amount) || 0;
26315:             peak = Math.max(peak, balance);
26316:             low = Math.min(low, balance);
26317:             const drawdown = Math.max(0, peak - balance);
26318:             if (drawdown > largestDrawdown) {
26319:                 largestDrawdown = drawdown;
26320:                 largestDrawdownPercent = peak ? drawdown / peak * 100 : 0;
26321:             }
26322:         }
26323:         return { peakBalance: Math.round(peak), lowBalance: Math.round(low), largestDrawdown: Math.round(largestDrawdown), largestDrawdownPercent: Math.round(largestDrawdownPercent * 10) / 10 };
26324:     }
26325: 
26326:     function buildFinancialRiskAlerts(summary, comparison, context = {}) {
26327:         const alerts = [];
26328:         const add = (severity, title, detail) => alerts.push({ severity, title, detail });
26329:         const risk = activeFinancialPolicy?.risk || BUILTIN_FINANCIAL_POLICY.risk;
26330:         if (!context.ledgerComplete) add('high', 'Partial ledger coverage', 'The requested period was not fully verified from the MissionChief ledger or local archive.');
26331:         if (context.archiveTruncated) add('high', 'Local archive capacity reached', `${Number(context.droppedTransactions || 0).toLocaleString('en-GB')} older transactions were not retained locally. Run the report directly against MissionChief for the widest currently accessible range.`);
26332:         if (context.scanLimitReached) add('high', 'Ledger page safety cap reached', 'MissionChief exposed more ledger pages than the configured deep-scan safety cap. The report is extensive but not complete.');
26333:         if (context.scanCancelled) add('medium', 'Deep scan stopped', 'The report uses all pages collected before the scan was stopped. Those pages remain stored in the local archive.');
26334:         if (summary.classificationConfidence < risk.classificationCritical) add('high', 'Low classification confidence', `${summary.unclassifiedCount.toLocaleString('en-GB')} transactions remain uncertain; review the original descriptions.`);
26335:         else if (summary.classificationConfidence < risk.classificationWarning) add('medium', 'Classification review advised', `${summary.classificationConfidence.toLocaleString('en-GB')}% weighted classification confidence.`);
26336:         if (summary.operatingResult < 0) add('high', 'Negative operating result', `Operating activity is ${formatSignedCredits(summary.operatingResult)} before capital investment.`);
26337:         if (summary.capitalInvestmentRatioPercent >= risk.capitalIncomeRatio && summary.capitalInvestment > 0) add('medium', 'Aggressive capital deployment', `Capital investment is ${summary.capitalInvestmentRatioPercent.toLocaleString('en-GB')}% of period income.`);
26338:         if (summary.allianceIncomePercent >= risk.allianceConcentration) add('medium', 'Alliance income concentration', `${summary.allianceIncomePercent.toLocaleString('en-GB')}% of income is alliance-derived.`);
26339:         if (summary.incomeConcentrationPercent >= risk.categoryConcentration) add('medium', 'Revenue concentration', `${summary.incomeConcentrationPercent.toLocaleString('en-GB')}% of income came from ${summary.topIncomeCategory?.label || 'one category'}.`);
26340:         if (summary.incomeVolatilityPercent >= risk.volatilityWarning) add('low', 'High income volatility', `Bucket-to-bucket income volatility is ${summary.incomeVolatilityPercent.toLocaleString('en-GB')}%.`);
26341:         if (comparison && Number.isFinite(comparison.incomeChange) && comparison.incomeChange <= risk.revenueContraction) add('high', 'Revenue contraction', `Income fell ${Math.abs(Math.round(comparison.incomeChange * 10) / 10).toLocaleString('en-GB')}% versus the previous equivalent period.`);
26342:         if (Number.isFinite(context.drawdown?.largestDrawdownPercent) && context.drawdown.largestDrawdownPercent >= risk.drawdownWarning) add('medium', 'Material reserve drawdown', `Largest reconstructed drawdown was ${context.drawdown.largestDrawdownPercent.toLocaleString('en-GB')}%.`);
26343:         if (context.scorecard?.runwayDays !== null && context.scorecard?.runwayDays < risk.runwayCriticalDays) add('high', 'Low operating runway', `Current reserve covers approximately ${context.scorecard.runwayDays.toLocaleString('en-GB')} days at the observed operating-expense pace.`);
26344:         if (!alerts.length) add('good', 'No material alerts', 'No configured financial risk threshold was triggered for this period.');
26345:         return alerts.slice(0, 8);
26346:     }
26347: 
26348:     function buildFinancialForecast(summary, period, closingBalance) {
26349:         const durationDays = Math.max(1 / 24, period.durationMs / 86400000);
26350:         const dailyIncome = summary.income / durationDays;
26351:         const dailyOperatingResult = summary.operatingResult / durationDays;
26352:         const sevenDayIncome = Math.round(dailyIncome * 7);
26353:         const thirtyDayIncome = Math.round(dailyIncome * 30);
26354:         const recoveryDays = summary.capitalInvestment > 0 && dailyOperatingResult > 0 ? summary.capitalInvestment / dailyOperatingResult : null;
26355:         let endOfDayIncome = null;
26356:         if (period.id === 'today') {
26357:             const elapsedHours = Math.max(0.25, (Date.now() - localDayStart()) / 3600000);
26358:             endOfDayIncome = Math.round(summary.income / elapsedHours * 24);
26359:         }
26360:         const confidence = summary.activityCount >= 100 && durationDays >= 7 ? 'HIGH' : summary.activityCount >= 25 && durationDays >= 1 ? 'MEDIUM' : 'LOW';
26361:         return {
26362:             dailyIncome: Math.round(dailyIncome),
26363:             dailyOperatingResult: Math.round(dailyOperatingResult),
```

## Match at line 26803

Matched source: `context.fillText('OPERATING SNAPSHOT', detailX + 22, detailY + 32);`

```javascript
26713:         try {
26714:             const canvas = document.createElement('canvas');
26715:             canvas.width = 1200;
26716:             canvas.height = 675;
26717:             const context = canvas.getContext('2d');
26718:             if (!context) return null;
26719:             const gradient = context.createLinearGradient(0, 0, 1200, 675);
26720:             gradient.addColorStop(0, '#0b1018');
26721:             gradient.addColorStop(0.55, '#111a27');
26722:             gradient.addColorStop(1, '#080b11');
26723:             context.fillStyle = gradient;
26724:             context.fillRect(0, 0, 1200, 675);
26725: 
26726:             context.fillStyle = 'rgba(88,166,255,0.12)';
26727:             context.beginPath();
26728:             context.arc(1060, 70, 230, 0, Math.PI * 2);
26729:             context.fill();
26730:             context.fillStyle = 'rgba(124,77,255,0.08)';
26731:             context.beginPath();
26732:             context.arc(140, 650, 280, 0, Math.PI * 2);
26733:             context.fill();
26734: 
26735:             context.fillStyle = '#ffffff';
26736:             context.font = '900 34px Arial, sans-serif';
26737:             context.fillText('MISSIONCHIEF FINANCIAL INTELLIGENCE', 54, 58);
26738:             context.fillStyle = 'rgba(255,255,255,0.62)';
26739:             context.font = '600 18px Arial, sans-serif';
26740:             context.fillText(report.period.label, 54, 89);
26741:             context.fillText(report.period.rangeLabel, 54, 116);
26742: 
26743:             roundRectPath(context, 1002, 38, 142, 70, 20);
26744:             context.fillStyle = report.net >= 0 ? 'rgba(46,204,113,0.18)' : 'rgba(231,76,60,0.18)';
26745:             context.fill();
26746:             context.fillStyle = report.net >= 0 ? '#67e69b' : '#ff8378';
26747:             context.font = '900 30px Arial, sans-serif';
26748:             context.textAlign = 'center';
26749:             context.fillText(report.grade.grade, 1073, 73);
26750:             context.font = '700 14px Arial, sans-serif';
26751:             context.fillText(`${report.grade.score}/100`, 1073, 96);
26752:             context.textAlign = 'left';
26753: 
26754:             drawFinancialMetricCard(context, 54, 148, 337, 98, 'Income', formatSignedCompactCredits(report.income), '#2ecc71');
26755:             drawFinancialMetricCard(context, 412, 148, 337, 98, 'Operating result', formatSignedCompactCredits(report.operatingResult), report.operatingResult >= 0 ? '#58a6ff' : '#ff6b61');
26756:             drawFinancialMetricCard(context, 770, 148, 374, 98, 'Capital deployed', formatSignedCompactCredits(-Math.abs(report.capitalInvestment || 0)), '#f1c40f');
26757: 
26758:             const chartX = 54;
26759:             const chartY = 288;
26760:             const chartW = 730;
26761:             const chartH = 250;
26762:             roundRectPath(context, chartX, chartY, chartW, chartH, 18);
26763:             context.fillStyle = 'rgba(255,255,255,0.04)';
26764:             context.fill();
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
26876:                 return discordHttpRequest({
26877:                     method: 'POST',
26878:                     url: discordWebhookEndpoint(webhookUrl, { wait: true }),
26879:                     data: formData
26880:                 });
26881:             });
26882:             if (response.status === 400 || response.status === 413 || response.status === 415) {
26883:                 const errorText = String(response.responseText || '').toLowerCase();
26884:                 const attachmentRelated = response.status === 413 || response.status === 415 || /attachment|file|upload|multipart|request entity too large/iu.test(errorText);
26885:                 if (attachmentRelated) {
26886:                     const fallbackPayload = buildDiscordFinancialPayload(report, { withAttachment: false });
26887:                     response = await sendDiscordWithRetry(() => discordHttpRequest({
26888:                         method: 'POST',
26889:                         url: discordWebhookEndpoint(webhookUrl, { wait: true }),
26890:                         headers: { 'Content-Type': 'application/json' },
26891:                         data: JSON.stringify(fallbackPayload)
26892:                     }));
26893:                 }
26894:             }
26895:         } else {
26896:             response = await sendDiscordWithRetry(() => discordHttpRequest({
26897:                 method: 'POST',
26898:                 url: discordWebhookEndpoint(webhookUrl, { wait: true }),
26899:                 headers: { 'Content-Type': 'application/json' },
26900:                 data: JSON.stringify(payload)
26901:             }));
26902:         }
26903:         if (response.status < 200 || response.status >= 300) throw new Error(parseDiscordError(response));
26904:         return response;
26905:     }
26906:     function clearDiscordPreviewChartUrl() {
26907:         if (discordFinanceChartUrl) {
26908:             try { URL.revokeObjectURL(discordFinanceChartUrl); } catch (err) {}
26909:         }
26910:         discordFinanceChartUrl = '';
26911:     }
26912: 
26913:     function invalidateDiscordFinancialPreview() {
26914:         clearDiscordPreviewChartUrl();
26915:     }
26916: 
26917:     async function postDiscordFinancialReport() {
26918:         if (discordFinanceBusy) return;
26919:         let webhookUrl;
26920:         try { webhookUrl = readDiscordWebhookInput({ save: true }); }
26921:         catch (err) {
26922:             setDiscordStatus(err?.message || 'Enter a valid Discord webhook URL.', 'bad');
26923:             showToast('Discord webhook required');
```
