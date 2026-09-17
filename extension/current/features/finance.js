(() => {const seed=window.__MCMS_EXTENSION_SEED__||window.__MCMS_EXTENSION_PILOT__?.documentIdentity;if(!seed||(seed.documentToken&&(location.origin!==seed.origin||document.documentElement.getAttribute('data-mcms-extension-document')!==seed.documentToken)))return;
(()=>{'use strict';window.__MCMS_EXTENSION_FEATURES__ ||= Object.create(null);window.__MCMS_EXTENSION_FEATURES__["finance"] ||= {"refreshFinancialRuleFeed":__mcmsModuleContext=>(async function refreshFinancialRuleFeed(force = false) {
        if (!__mcmsModuleContext.state.financialVault.ruleFeedEnabled) {
            __mcmsModuleContext.activeFinancialRules = __mcmsModuleContext.BUILTIN_FINANCIAL_RULES.map(rule => (0,__mcmsModuleContext.compileFinancialRule)({ ...rule, source: 'built-in' }));
            __mcmsModuleContext.activeFinancialFallbacks = { income: { ...__mcmsModuleContext.BUILTIN_FINANCIAL_FALLBACKS.income }, spending: { ...__mcmsModuleContext.BUILTIN_FINANCIAL_FALLBACKS.spending } };
            __mcmsModuleContext.activeFinancialRuleVersion = 'built-in';
            (0,__mcmsModuleContext.setFinanceRuleFeedStatus)('Built-in classification rules active.', 'neutral');
            return false;
        }
        if (__mcmsModuleContext.financeRuleRefreshPromise) return __mcmsModuleContext.financeRuleRefreshPromise;
        __mcmsModuleContext.financeRuleRefreshPromise = (async () => {
            const cachedAt = (0,__mcmsModuleContext.loadCachedFinancialRules)();
            if (!force && cachedAt && __mcmsModuleContext.Date.now() - cachedAt < __mcmsModuleContext.FINANCE_RULE_CACHE_TTL_MS) {
                (0,__mcmsModuleContext.setFinanceRuleFeedStatus)(`Classification feed ${__mcmsModuleContext.activeFinancialRuleVersion} · cached`, 'good');
                return true;
            }
            (0,__mcmsModuleContext.setFinanceRuleFeedStatus)('Checking the central classification rule feed…', 'busy');
            try {
                const response = await (0,__mcmsModuleContext.financeExternalRequest)({ url: `${__mcmsModuleContext.FINANCE_RULE_FEED_URL}?v=${__mcmsModuleContext.Date.now()}` });
                if (response.status < 200 || response.status >= 300) throw new __mcmsModuleContext.Error(`Rule feed returned HTTP ${response.status}.`);
                const payload = __mcmsModuleContext.JSON.parse(response.responseText || '{}');
                if (!(0,__mcmsModuleContext.applyFinancialRulePayload)(payload, { cache: true })) throw new __mcmsModuleContext.Error('Rule feed failed schema validation.');
                (0,__mcmsModuleContext.setFinanceRuleFeedStatus)(`Classification feed ${__mcmsModuleContext.activeFinancialRuleVersion} active.`, 'good');
                return true;
            } catch (err) {
                const cached = (0,__mcmsModuleContext.loadCachedFinancialRules)();
                if (!cached) {
                    __mcmsModuleContext.activeFinancialRules = __mcmsModuleContext.BUILTIN_FINANCIAL_RULES.map(rule => (0,__mcmsModuleContext.compileFinancialRule)({ ...rule, source: 'built-in' }));
                    __mcmsModuleContext.activeFinancialRuleVersion = 'built-in';
                }
                (0,__mcmsModuleContext.setFinanceRuleFeedStatus)(`${err?.message || 'Rule feed unavailable'} Using ${__mcmsModuleContext.activeFinancialRuleVersion}.`, cached ? 'neutral' : 'bad');
                return false;
            }
        })().finally(() => { __mcmsModuleContext.financeRuleRefreshPromise = null; });
        return __mcmsModuleContext.financeRuleRefreshPromise;
    }),
"refreshFinancialPolicyFeed":__mcmsModuleContext=>(async function refreshFinancialPolicyFeed(force = false) {
        if (!__mcmsModuleContext.state.financialVault.ruleFeedEnabled) {
            __mcmsModuleContext.activeFinancialPolicy = (0,__mcmsModuleContext.clonePlainData)(__mcmsModuleContext.BUILTIN_FINANCIAL_POLICY);
            __mcmsModuleContext.activeFinancialPolicyVersion = 'built-in';
            return false;
        }
        if (__mcmsModuleContext.financePolicyRefreshPromise) return __mcmsModuleContext.financePolicyRefreshPromise;
        __mcmsModuleContext.financePolicyRefreshPromise = (async () => {
            const cachedAt = (0,__mcmsModuleContext.loadCachedFinancialPolicy)();
            if (!force && cachedAt && __mcmsModuleContext.Date.now() - cachedAt < __mcmsModuleContext.FINANCE_POLICY_CACHE_TTL_MS) return true;
            try {
                const response = await (0,__mcmsModuleContext.financeExternalRequest)({ url: `${__mcmsModuleContext.FINANCE_POLICY_FEED_URL}?v=${__mcmsModuleContext.Date.now()}` });
                if (response.status < 200 || response.status >= 300) throw new __mcmsModuleContext.Error(`Audit policy returned HTTP ${response.status}.`);
                const payload = __mcmsModuleContext.JSON.parse(response.responseText || '{}');
                if (!(0,__mcmsModuleContext.applyFinancialPolicyPayload)(payload, { cache: true })) throw new __mcmsModuleContext.Error('Audit policy failed schema validation.');
                return true;
            } catch (err) {
                const cached = (0,__mcmsModuleContext.loadCachedFinancialPolicy)();
                if (!cached) {
                    __mcmsModuleContext.activeFinancialPolicy = (0,__mcmsModuleContext.clonePlainData)(__mcmsModuleContext.BUILTIN_FINANCIAL_POLICY);
                    __mcmsModuleContext.activeFinancialPolicyVersion = 'built-in';
                }
                return false;
            }
        })().finally(() => { __mcmsModuleContext.financePolicyRefreshPromise = null; });
        return __mcmsModuleContext.financePolicyRefreshPromise;
    }),
"refreshFinancialIntelligenceFeeds":__mcmsModuleContext=>(async function refreshFinancialIntelligenceFeeds(force = false) {
        if (!__mcmsModuleContext.state.financialVault.ruleFeedEnabled) {
            await __mcmsModuleContext.Promise.all([(0,__mcmsModuleContext.refreshFinancialRuleFeed)(force), (0,__mcmsModuleContext.refreshFinancialPolicyFeed)(force)]);
            (0,__mcmsModuleContext.setFinanceRuleFeedStatus)('Built-in financial intelligence active. No player data is uploaded.', 'neutral');
            return false;
        }
        (0,__mcmsModuleContext.setFinanceRuleFeedStatus)('Checking GitHub financial intelligence feeds…', 'busy');
        const [rulesOk, policyOk] = await __mcmsModuleContext.Promise.all([(0,__mcmsModuleContext.refreshFinancialRuleFeed)(force), (0,__mcmsModuleContext.refreshFinancialPolicyFeed)(force)]);
        const tone = rulesOk || policyOk ? 'good' : 'neutral';
        (0,__mcmsModuleContext.setFinanceRuleFeedStatus)(`GitHub intelligence ${__mcmsModuleContext.activeFinancialRuleVersion} · policy ${__mcmsModuleContext.activeFinancialPolicyVersion}. No player data is uploaded.`, tone);
        return rulesOk || policyOk;
    }),
"exportFinancialArchive":__mcmsModuleContext=>(async function exportFinancialArchive(){}),
"testDiscordWebhook":__mcmsModuleContext=>(async function testDiscordWebhook(){await (0,__mcmsModuleContext.pilotCall)({op:'discordOpen'}).promise;(0,__mcmsModuleContext.setDiscordStatus)('Use Check connection in the Discord screen. No message is sent by this check.');}),
"fetchCreditOverviewPage":__mcmsModuleContext=>(async function fetchCreditOverviewPage(pageNumber) {
        const page = __mcmsModuleContext.Math.max(1, __mcmsModuleContext.Math.round((0,__mcmsModuleContext.Number)(pageNumber) || 1));
        const attempts = __mcmsModuleContext.Math.max(1, __mcmsModuleContext.Math.min(5, (0,__mcmsModuleContext.Number)(__mcmsModuleContext.activeFinancialPolicy?.scan?.retryAttempts) || 3));
        let lastError = null;
        for (let attempt = 0; attempt < attempts; attempt++) {
            try {
                const path = page === 1 ? '/credits/overview' : `/credits/overview?page=${page}`;
                const result = await (0,__mcmsModuleContext.fetchSameOriginDocument)(path);
                return (0,__mcmsModuleContext.parseCreditOverviewDocument)(result.doc, page);
            } catch (err) {
                lastError = err;
                if (attempt >= attempts - 1) break;
                const delay = __mcmsModuleContext.Math.min(4000, 350 * __mcmsModuleContext.Math.pow(2, attempt) + __mcmsModuleContext.Math.floor(__mcmsModuleContext.Math.random() * 180));
                (0,__mcmsModuleContext.setDiscordStatus)(`MissionChief credits overview page ${page.toLocaleString('en-GB')} needs another attempt…`, 'busy');
                if (!await (0,__mcmsModuleContext.runtimeDelay)(delay)) throw new __mcmsModuleContext.Error('Toolkit runtime stopped while retrying the credits overview.');
            }
        }
        throw lastError || new __mcmsModuleContext.Error(`MissionChief credits overview page ${page} could not be read.`);
    }),
"fetchCreditOverview":__mcmsModuleContext=>(async function fetchCreditOverview(requiredStartMs, requiredEndMs, options) {
        const force = (0,__mcmsModuleContext.Boolean)(options?.force);
        const now = __mcmsModuleContext.Date.now();
        const startMs = __mcmsModuleContext.Math.max(0, (0,__mcmsModuleContext.Number)(requiredStartMs) || 0);
        const endMs = __mcmsModuleContext.Math.max(startMs + 1, (0,__mcmsModuleContext.Number)(requiredEndMs) || now);
        if (!force && now - (0,__mcmsModuleContext.Number)(__mcmsModuleContext.financialOverviewCache.fetchedAt || 0) < __mcmsModuleContext.FINANCE_OVERVIEW_CACHE_TTL_MS && (0,__mcmsModuleContext.financialOverviewCacheCovers)(startMs, endMs)) {
            return { ...__mcmsModuleContext.financialOverviewCache, rows: __mcmsModuleContext.financialOverviewCache.rows.slice(), available: true, fromCache: true, coverageReached: true, error: '' };
        }
        const rowsByDate = new __mcmsModuleContext.Map();
        let malformedRowCount = 0;
        let duplicateDateCount = 0;
        let pageCount = 0;
        let lastPage = 1;
        let failure = null;
        const targetStart = (0,__mcmsModuleContext.localDayStart)(startMs);
        try {
            for (let page = 1; page <= __mcmsModuleContext.Math.min(lastPage, __mcmsModuleContext.FINANCE_OVERVIEW_MAX_PAGES); page++) {
                const parsed = await (0,__mcmsModuleContext.fetchCreditOverviewPage)(page);
                pageCount++;
                lastPage = __mcmsModuleContext.Math.max(lastPage, (0,__mcmsModuleContext.Number)(parsed.lastPage) || 1);
                malformedRowCount += (0,__mcmsModuleContext.Number)(parsed.malformedRowCount) || 0;
                duplicateDateCount += (0,__mcmsModuleContext.Number)(parsed.duplicateDateCount) || 0;
                for (const row of parsed.rows) {
                    if (rowsByDate.has(row.dateKey)) {
                        duplicateDateCount++;
                        continue;
                    }
                    rowsByDate.set(row.dateKey, row);
                }
                const oldest = parsed.rows.length ? __mcmsModuleContext.Math.min(...parsed.rows.map(row => row.dayStartMs)) : __mcmsModuleContext.Infinity;
                if (startMs > 0 && oldest <= targetStart) break;
                if (page >= lastPage) break;
                if (page % __mcmsModuleContext.FINANCE_FETCH_YIELD_EVERY === 0 && !await (0,__mcmsModuleContext.runtimeDelay)(25)) throw new __mcmsModuleContext.Error('Toolkit runtime stopped while reading the credits overview.');
            }
        } catch (err) {
            failure = err;
        }
        const rows = __mcmsModuleContext.Array.from(rowsByDate.values()).sort((a, b) => b.dayStartMs - a.dayStartMs);
        if (!rows.length) {
            const cached = __mcmsModuleContext.financialOverviewCache.rows?.length ? __mcmsModuleContext.financialOverviewCache : null;
            if (cached) return { ...cached, rows: cached.rows.slice(), available: true, fromCache: true, stale: true, coverageReached: (0,__mcmsModuleContext.financialOverviewCacheCovers)(startMs, endMs, cached), error: failure?.message || 'MissionChief credits overview was unavailable.' };
            return { available: false, rows: [], pageCount, lastPage, complete: false, coverageReached: false, malformedRowCount, duplicateDateCount, fromCache: false, stale: false, error: failure?.message || 'MissionChief credits overview was unavailable.' };
        }
        const coverageStartMs = __mcmsModuleContext.Math.min(...rows.map(row => row.dayStartMs));
        const coverageEndMs = __mcmsModuleContext.Math.max(...rows.map(row => row.dayEndMs));
        const complete = !failure && pageCount >= __mcmsModuleContext.Math.min(lastPage, __mcmsModuleContext.FINANCE_OVERVIEW_MAX_PAGES);
        const cache = {
            fetchedAt: now,
            rows,
            pageCount,
            lastPage,
            coverageStartMs,
            coverageEndMs,
            complete,
            malformedRowCount,
            duplicateDateCount
        };
        __mcmsModuleContext.financialOverviewCache = cache;
        return { ...cache, rows: rows.slice(), available: true, fromCache: false, stale: false, coverageReached: (0,__mcmsModuleContext.financialOverviewCacheCovers)(startMs, endMs, cache), error: failure?.message || '' };
    }),
"fetchCreditLedgerPage":__mcmsModuleContext=>(async function fetchCreditLedgerPage(pageNumber) {
        const page = __mcmsModuleContext.Math.max(1, __mcmsModuleContext.Math.round((0,__mcmsModuleContext.Number)(pageNumber) || 1));
        const attempts = __mcmsModuleContext.Math.max(1, __mcmsModuleContext.Math.min(5, (0,__mcmsModuleContext.Number)(__mcmsModuleContext.activeFinancialPolicy?.scan?.retryAttempts) || 3));
        let lastError = null;
        for (let attempt = 0; attempt < attempts; attempt++) {
            try {
                const path = page === 1 ? '/credits' : `/credits?page=${page}`;
                if(__mcmsModuleContext.pilot.creditScanActive&&__mcmsModuleContext.financeArchiveScanCancelled)throw (0,__mcmsModuleContext.Error)('Finance scan stopped.');
                __mcmsModuleContext.pilot.creditProgress?.('Reading ledger page '+page+'…');
                const result = await (0,__mcmsModuleContext.fetchSameOriginDocument)(path);
                if(!result.doc.querySelector('table'))throw (0,__mcmsModuleContext.Error)('MissionChief did not return a Credits ledger. Check that you are signed in.');
                return (0,__mcmsModuleContext.parseCreditsListDocument)(result.doc, page);
            } catch (err) {
                lastError = err;
                if(__mcmsModuleContext.pilot.creditScanActive&&__mcmsModuleContext.financeArchiveScanCancelled)throw err;
                if (attempt >= attempts - 1) break;
                const delay = __mcmsModuleContext.Math.min(4000, 350 * __mcmsModuleContext.Math.pow(2, attempt) + __mcmsModuleContext.Math.floor(__mcmsModuleContext.Math.random() * 180));
                (0,__mcmsModuleContext.setDiscordStatus)(`MissionChief ledger page ${page.toLocaleString('en-GB')} needs another attempt…`, 'busy');
                if (!await (0,__mcmsModuleContext.runtimeDelay)(delay)) throw new __mcmsModuleContext.Error('Toolkit runtime stopped while retrying the financial ledger.');
            }
        }
        throw lastError || new __mcmsModuleContext.Error(`MissionChief ledger page ${page} could not be read.`);
    }),
"fetchCreditAccount":__mcmsModuleContext=>(async function fetchCreditAccount(){
  __mcmsModuleContext.pilot.creditProgress?.('Reading current Credits balance…');
  try{const {body:data}=await (0,__mcmsModuleContext.readCreditDocument)('/api/credits','json',20000,true);
    const balance=(0,__mcmsModuleContext.Number)(data?.credits_user_current);
    return {currentBalance:__mcmsModuleContext.Number.isFinite(balance)?__mcmsModuleContext.Math.round(balance):null,userName:(0,__mcmsModuleContext.String)(data?.user_name||'').trim(),userId:(0,__mcmsModuleContext.Number)(data?.user_id)||null};
  }catch(error){if(__mcmsModuleContext.pilot.creditScanActive)throw error;return null;}
}),
"fetchFinancialLedger":__mcmsModuleContext=>(async function fetchFinancialLedger(requiredStartMs, attempt = 0, forceFull = false, exhaustive = false) {
        const account = await (0,__mcmsModuleContext.fetchCreditAccount)();
        const player = (0,__mcmsModuleContext.financePlayerIdentity)(account);
        const identity = (0,__mcmsModuleContext.ensureFinanceVaultCredential)(player);
        let vault = (0,__mcmsModuleContext.loadFinanceVault)(player, identity.deviceId);
        const vaultStats = (0,__mcmsModuleContext.financeVaultStats)(vault);
        const wantsAllAvailable = (0,__mcmsModuleContext.Number)(requiredStartMs) <= 0;
        const deepMode = (0,__mcmsModuleContext.Boolean)(exhaustive || (wantsAllAvailable && !vault.archiveComplete));
        const effectiveRequiredStart = wantsAllAvailable && __mcmsModuleContext.Number.isFinite((0,__mcmsModuleContext.Number)(vault.coverageStartMs)) ? (0,__mcmsModuleContext.Number)(vault.coverageStartMs) : (0,__mcmsModuleContext.Number)(requiredStartMs);
        const canUseIncremental = (0,__mcmsModuleContext.Boolean)(
            __mcmsModuleContext.state.financialVault.enabled &&
            !forceFull &&
            !deepMode &&
            vaultStats.count &&
            __mcmsModuleContext.Number.isFinite((0,__mcmsModuleContext.Number)(vault.coverageStartMs)) &&
            (0,__mcmsModuleContext.Number)(vault.coverageStartMs) <= effectiveRequiredStart &&
            __mcmsModuleContext.Number.isFinite((0,__mcmsModuleContext.Number)(vault.coverageEndMs))
        );
        const knownSourceKeys = canUseIncremental ? new __mcmsModuleContext.Set(vault.transactions.map(entry => entry.sourceKey)) : new __mcmsModuleContext.Set();
        const vaultLatestTimestamp = canUseIncremental ? (0,__mcmsModuleContext.Number)(vault.coverageEndMs) || vaultStats.lastTimestamp || 0 : 0;
        let pendingEntries = [];
        let invalidTimestampCount = 0;
        let lastPage = 1;
        let fetchedPages = 0;
        let oldestTimestamp = __mcmsModuleContext.Infinity;
        let reachedStart = false;
        let firstPageAnchor = '';
        let overlapFound = false;
        let scanCancelled = false;
        let scanLimitReached;
        let lastProcessedPage = 0;
        const scanOccurrenceCounts = new __mcmsModuleContext.Map();
        const absorbPage = (parsed, page) => {
            fetchedPages++;
            lastProcessedPage = __mcmsModuleContext.Math.max(lastProcessedPage, page);
            invalidTimestampCount += parsed.invalidTimestampCount;
            let pageOverlap = 0;
            let pageOldest = __mcmsModuleContext.Infinity;
            for (const entry of parsed.entries) {
                const normalisedEntry = (0,__mcmsModuleContext.normaliseFinancialLedgerEntry)(entry);
                if (!normalisedEntry) continue;
                const occurrence = (scanOccurrenceCounts.get(normalisedEntry.sourceKey) || 0) + 1;
                scanOccurrenceCounts.set(normalisedEntry.sourceKey, occurrence);
                pendingEntries.push({ ...normalisedEntry, occurrence });
                if (normalisedEntry.timestamp < oldestTimestamp) oldestTimestamp = normalisedEntry.timestamp;
                if (normalisedEntry.timestamp < pageOldest) pageOldest = normalisedEntry.timestamp;
                if (canUseIncremental && knownSourceKeys.has(normalisedEntry.sourceKey)) pageOverlap++;
            }
            reachedStart = __mcmsModuleContext.Number.isFinite(oldestTimestamp) && oldestTimestamp <= effectiveRequiredStart;
            if (canUseIncremental && pageOverlap >= 3 && __mcmsModuleContext.Number.isFinite(pageOldest) && pageOldest <= vaultLatestTimestamp) overlapFound = true;
        };
        const persistCheckpoint = ({ final = false, completeRange = false } = {}) => {
            if (!__mcmsModuleContext.state.financialVault.enabled || (!pendingEntries.length && !final)) return;
            vault = (0,__mcmsModuleContext.mergeFinanceVaultEntries)(vault, pendingEntries, {
                coverageStartMs: __mcmsModuleContext.Number.isFinite(oldestTimestamp) ? oldestTimestamp : null,
                coverageEndMs: __mcmsModuleContext.Date.now(),
                fullScan: forceFull || deepMode,
                deepScan: deepMode && final && completeRange,
                sourceLastPage: lastPage,
                deepScanCursorPage: deepMode ? lastProcessedPage : null,
                deepScanTotalPages: deepMode ? lastPage : null,
                deepScanAnchor: deepMode ? firstPageAnchor : null,
                deepScanInProgress: deepMode ? !completeRange : null,
                archiveComplete: final ? completeRange : null,
                currentBalance: final ? account?.currentBalance : null
            });
            pendingEntries = [];
        };
        const firstPage = await (0,__mcmsModuleContext.fetchCreditLedgerPage)(1);
        lastPage = __mcmsModuleContext.Math.max(1, firstPage.lastPage || 1);
        firstPageAnchor = (0,__mcmsModuleContext.financialLedgerAnchor)(firstPage.entries);
        let deepScanStartPage = 2;
        const resumableDeepScan = (0,__mcmsModuleContext.Boolean)(
            deepMode &&
            vault.deepScanInProgress &&
            vault.deepScanAnchor &&
            vault.deepScanAnchor === firstPageAnchor &&
            (0,__mcmsModuleContext.Number)(vault.deepScanTotalPages) === lastPage &&
            (0,__mcmsModuleContext.Number)(vault.deepScanCursorPage) >= 1 &&
            (0,__mcmsModuleContext.Number)(vault.deepScanCursorPage) < lastPage
        );
        if (resumableDeepScan) {
            deepScanStartPage = __mcmsModuleContext.Math.max(2, (0,__mcmsModuleContext.Number)(vault.deepScanCursorPage) + 1);
            lastProcessedPage = (0,__mcmsModuleContext.Number)(vault.deepScanCursorPage);
            oldestTimestamp = __mcmsModuleContext.Number.isFinite((0,__mcmsModuleContext.Number)(vault.coverageStartMs)) ? (0,__mcmsModuleContext.Number)(vault.coverageStartMs) : __mcmsModuleContext.Infinity;
            for (const existing of vault.transactions) {
                const sourceKey = (0,__mcmsModuleContext.String)(existing.sourceKey || '');
                if (!sourceKey) continue;
                scanOccurrenceCounts.set(sourceKey, __mcmsModuleContext.Math.max(scanOccurrenceCounts.get(sourceKey) || 0, (0,__mcmsModuleContext.Number)(existing.occurrence) || 1));
            }
            (0,__mcmsModuleContext.setFinanceVaultStatus)(`Resuming deep scan from MissionChief ledger page ${deepScanStartPage.toLocaleString('en-GB')}…`, 'busy');
        } else {
            absorbPage(firstPage, 1);
        }
        if (deepMode) {
            const configuredCap = __mcmsModuleContext.Math.max(100, __mcmsModuleContext.Math.min(__mcmsModuleContext.FINANCE_DEEP_SCAN_HARD_PAGE_CAP, (0,__mcmsModuleContext.Number)(__mcmsModuleContext.activeFinancialPolicy?.scan?.pageCap) || __mcmsModuleContext.FINANCE_DEEP_SCAN_HARD_PAGE_CAP));
            const targetLastPage = __mcmsModuleContext.Math.min(lastPage, configuredCap);
            const batchSize = __mcmsModuleContext.Math.max(1, __mcmsModuleContext.Math.min(__mcmsModuleContext.FINANCE_DEEP_SCAN_HARD_BATCH_CAP, (0,__mcmsModuleContext.Number)(__mcmsModuleContext.activeFinancialPolicy?.scan?.batchSize) || 3));
            const checkpointPages = __mcmsModuleContext.Math.max(20, __mcmsModuleContext.Math.min(500, (0,__mcmsModuleContext.Number)(__mcmsModuleContext.activeFinancialPolicy?.scan?.checkpointPages) || __mcmsModuleContext.FINANCE_SCAN_CHECKPOINT_PAGES));
            scanLimitReached = targetLastPage < lastPage;
            for (let cursor = deepScanStartPage; cursor <= targetLastPage; cursor += batchSize) {
                if (__mcmsModuleContext.financeArchiveScanCancelled) {
                    scanCancelled = true;
                    break;
                }
                const pages = __mcmsModuleContext.Array.from({ length: __mcmsModuleContext.Math.min(batchSize, targetLastPage - cursor + 1) }, (_, index) => cursor + index);
                const results = await __mcmsModuleContext.Promise.all(pages.map(page => (0,__mcmsModuleContext.fetchCreditLedgerPage)(page)));
                for (let index = 0; index < pages.length; index++) absorbPage(results[index], pages[index]);
                if (__mcmsModuleContext.state.financialVault.enabled && lastProcessedPage % checkpointPages < batchSize) persistCheckpoint();
                (0,__mcmsModuleContext.setDiscordStatus)(`Deep MissionChief ledger scan · page ${lastProcessedPage.toLocaleString('en-GB')} of ${lastPage.toLocaleString('en-GB')} · ${__mcmsModuleContext.Math.round(lastProcessedPage / __mcmsModuleContext.Math.max(1, targetLastPage) * 100)}%`, 'busy');
                (0,__mcmsModuleContext.setFinanceVaultStatus)(`Deep scan reading page ${lastProcessedPage.toLocaleString('en-GB')} of ${lastPage.toLocaleString('en-GB')}…`, 'busy');
                if (lastProcessedPage % 15 === 0 && !await (0,__mcmsModuleContext.runtimeDelay)(45)) throw new __mcmsModuleContext.Error('Toolkit runtime stopped while deep-scanning the financial ledger.');
            }
            reachedStart = !scanCancelled && !scanLimitReached && lastProcessedPage >= lastPage;
        } else {
            let page = 2;
            while (page <= __mcmsModuleContext.Math.min(lastPage, __mcmsModuleContext.FINANCE_MAX_LEDGER_PAGES)) {
                if (reachedStart || overlapFound) break;
                if (canUseIncremental && page > __mcmsModuleContext.FINANCE_INCREMENTAL_MAX_PAGES) break;
                const parsed = await (0,__mcmsModuleContext.fetchCreditLedgerPage)(page);
                absorbPage(parsed, page);
                if (page % __mcmsModuleContext.FINANCE_FETCH_YIELD_EVERY === 0) {
                    (0,__mcmsModuleContext.setDiscordStatus)(`${canUseIncremental ? 'Synchronising new ledger activity' : 'Reading MissionChief ledger'} · page ${page.toLocaleString('en-GB')} of ${lastPage.toLocaleString('en-GB')}…`, 'busy');
                    if (!await (0,__mcmsModuleContext.runtimeDelay)(35)) throw new __mcmsModuleContext.Error('Toolkit runtime stopped while reading the financial ledger.');
                }
                page++;
            }
            scanLimitReached = lastProcessedPage >= __mcmsModuleContext.FINANCE_MAX_LEDGER_PAGES && lastProcessedPage < lastPage;
        }
        if (canUseIncremental && !overlapFound && !reachedStart && lastProcessedPage < lastPage) {
            (0,__mcmsModuleContext.setDiscordStatus)('Local archive overlap was not found. Performing one complete requested-range scan…', 'busy');
            return fetchFinancialLedger(requiredStartMs, attempt, true, false);
        }
        let ledgerStable = true;
        if (fetchedPages > 1 && firstPageAnchor) {
            const verificationPage = await (0,__mcmsModuleContext.fetchCreditLedgerPage)(1);
            ledgerStable = (0,__mcmsModuleContext.financialLedgerAnchor)(verificationPage.entries) === firstPageAnchor;
            if (!ledgerStable && !deepMode && attempt < 1) {
                (0,__mcmsModuleContext.setDiscordStatus)('New credit activity appeared during the scan. Restarting once for an accurate report…', 'busy');
                if (!await (0,__mcmsModuleContext.runtimeDelay)(80)) throw new __mcmsModuleContext.Error('Toolkit runtime stopped while stabilising the financial ledger.');
                return fetchFinancialLedger(requiredStartMs, attempt + 1, forceFull, false);
            }
            if (!ledgerStable && deepMode) {
                (0,__mcmsModuleContext.setFinanceVaultStatus)('MissionChief added ledger activity during the deep scan. Progress was retained and the next run will safely rescan from the changed first page.', 'neutral');
            }
        }
        if (!pendingEntries.length && !vault.transactions.length) throw new __mcmsModuleContext.Error('MissionChief’s timestamped credit ledger could not be read.');
        const coverageReachedThisScan = deepMode
            ? (!scanCancelled && !scanLimitReached && ledgerStable && lastProcessedPage >= lastPage)
            : (ledgerStable && (reachedStart || overlapFound || lastProcessedPage >= lastPage));
        persistCheckpoint({ final: true, completeRange: coverageReachedThisScan });
        if (!__mcmsModuleContext.state.financialVault.enabled) {
            pendingEntries = (0,__mcmsModuleContext.decorateFinancialEntries)(pendingEntries);
        }
        const combinedEntries = __mcmsModuleContext.state.financialVault.enabled
            ? vault.transactions.filter(entry => wantsAllAvailable || entry.timestamp >= __mcmsModuleContext.Math.min(effectiveRequiredStart, (0,__mcmsModuleContext.Number)(vault.coverageStartMs) || effectiveRequiredStart))
            : pendingEntries;
        const coverageReached = wantsAllAvailable
            ? (__mcmsModuleContext.state.financialVault.enabled ? (0,__mcmsModuleContext.Boolean)(vault.archiveComplete) : coverageReachedThisScan)
            : (__mcmsModuleContext.state.financialVault.enabled
                ? __mcmsModuleContext.Number.isFinite((0,__mcmsModuleContext.Number)(vault.coverageStartMs)) && (0,__mcmsModuleContext.Number)(vault.coverageStartMs) <= effectiveRequiredStart
                : coverageReachedThisScan);
        const complete = coverageReached && ledgerStable && invalidTimestampCount === 0 && !scanCancelled && !scanLimitReached;
        const stats = (0,__mcmsModuleContext.financeVaultStats)(vault);
        if (__mcmsModuleContext.state.financialVault.enabled) {
            const mode = deepMode ? 'Deep' : canUseIncremental ? 'Incremental' : 'Requested-range';
            const suffix = scanCancelled
                ? ' Scan stopped; collected pages were retained.'
                : scanLimitReached
                    ? ' Page safety cap reached.'
                    : !ledgerStable
                        ? ' New ledger activity appeared during the scan; progress remains resumable.'
                        : '';
            (0,__mcmsModuleContext.setFinanceVaultStatus)(`${mode} archive scan stored ${stats.count.toLocaleString('en-GB')} transactions.${suffix}`, scanCancelled || scanLimitReached ? 'neutral' : 'good');
            (0,__mcmsModuleContext.renderFinanceVaultStatus)();
        }
        return {
            entries: combinedEntries,
            pageCount: fetchedPages,
            lastPage,
            invalidTimestampCount,
            oldestTimestamp: combinedEntries.length ? combinedEntries[0].timestamp : null,
            coverageReached,
            ledgerStable,
            scanRetries: attempt,
            scanCancelled,
            scanLimitReached,
            archiveComplete: (0,__mcmsModuleContext.Boolean)(vault.archiveComplete),
            archiveTruncated: (0,__mcmsModuleContext.Boolean)(vault.archiveTruncated),
            droppedTransactions: (0,__mcmsModuleContext.Number)(vault.droppedTransactions) || 0,
            complete,
            account,
            vault,
            vaultTransactionCount: stats.count,
            ledgerSource: __mcmsModuleContext.state.financialVault.enabled
                ? (deepMode ? 'Local archive + deep MissionChief scan' : canUseIncremental ? 'Local archive + incremental MissionChief scan' : 'Local archive + requested-range scan')
                : (deepMode ? 'Direct deep MissionChief ledger scan' : 'Direct MissionChief ledger scan')
        };
    }),
"scanFinancialArchive":__mcmsModuleContext=>(async function scanFinancialArchive(){}),
"buildFinancialReport":__mcmsModuleContext=>(async function buildFinancialReport() {
        let period = (0,__mcmsModuleContext.resolveFinancialPeriod)();
        const reportComplexity = (0,__mcmsModuleContext.normaliseDiscordReportComplexity)(__mcmsModuleContext.state.discordReport.complexity);
        const comparisonEnabled = (0,__mcmsModuleContext.discordReportComplexityAtLeast)('informative', reportComplexity) && __mcmsModuleContext.state.discordReport.includeComparison && period.id !== 'allAvailable';
        const requiredStartMs = comparisonEnabled ? period.comparisonStartMs : period.startMs;
        (0,__mcmsModuleContext.setDiscordStatus)('Updating GitHub intelligence and reading the MissionChief Financial Archive…', 'busy');
        await (0,__mcmsModuleContext.refreshFinancialIntelligenceFeeds)(false);
        const allAvailable = period.id === 'allAvailable';
        if (allAvailable) {
            __mcmsModuleContext.financeArchiveScanBusy = true;
            __mcmsModuleContext.financeArchiveScanCancelled = false;
        }
        let ledger;
        try {
            ledger = await (0,__mcmsModuleContext.fetchFinancialLedger)(requiredStartMs, 0, false, false);
        } finally {
            if (allAvailable) {
                __mcmsModuleContext.financeArchiveScanBusy = false;
                __mcmsModuleContext.financeArchiveScanCancelled = false;
            }
        }
        if (allAvailable) {
            const oldest = ledger.oldestTimestamp || ledger.entries[0]?.timestamp || __mcmsModuleContext.Date.now();
            period = {
                ...period,
                startMs: oldest,
                durationMs: __mcmsModuleContext.Math.max(1, period.endMs - oldest),
                comparisonStartMs: 0,
                comparisonEndMs: 0,
                rangeLabel: (0,__mcmsModuleContext.formatPeriodRange)(oldest, period.endMs),
                comparisonRangeLabel: 'Not applicable'
            };
        }
        const currentTransactions = [];
        const previousTransactions = [];
        let afterPeriodNet = 0;
        const now = __mcmsModuleContext.Date.now();
        for (const entry of ledger.entries) {
            if (entry.timestamp >= period.startMs && entry.timestamp < period.endMs) currentTransactions.push(entry);
            else if (comparisonEnabled && entry.timestamp >= period.comparisonStartMs && entry.timestamp < period.comparisonEndMs) previousTransactions.push(entry);
            if (entry.timestamp >= period.endMs && entry.timestamp <= now) afterPeriodNet += entry.amount;
        }
        const overview = await (0,__mcmsModuleContext.fetchCreditOverview)(comparisonEnabled ? period.comparisonStartMs : period.startMs, period.endMs);
        const currentLedgerSummary = (0,__mcmsModuleContext.summariseFinancialTransactions)(currentTransactions, period);
        const current = (0,__mcmsModuleContext.reconcileFinancialOverview)(currentLedgerSummary, currentTransactions, period, overview);
        const previousPeriod = { ...period, startMs: period.comparisonStartMs, endMs: period.comparisonEndMs, durationMs: period.durationMs };
        const previousLedgerSummary = comparisonEnabled ? (0,__mcmsModuleContext.summariseFinancialTransactions)(previousTransactions, previousPeriod) : null;
        const previous = previousLedgerSummary ? (0,__mcmsModuleContext.reconcileFinancialOverview)(previousLedgerSummary, previousTransactions, previousPeriod, overview) : null;
        const comparison = previous ? (0,__mcmsModuleContext.buildFinancialComparison)(current, previous) : null;
        const account = ledger.account;
        const currentBalance = __mcmsModuleContext.Number.isFinite(account?.currentBalance) ? account.currentBalance : null;
        const closingBalance = currentBalance === null ? null : currentBalance - afterPeriodNet;
        const openingBalance = closingBalance === null ? null : closingBalance - current.net;
        const balanceAvailable = openingBalance !== null && closingBalance !== null;
        const reconciliation = (0,__mcmsModuleContext.calculateVaultReconciliation)(ledger.vault, period, ledger.entries, currentBalance);
        const overviewAudit = current.overviewAudit || { status: 'unavailable', label: 'Credits overview unavailable', unresolvedVariance: 0 };
        const reconciliationLabel = `${balanceAvailable ? reconciliation.label : 'Balance unavailable'} · ${overviewAudit.label}`;
        const drawdown = (0,__mcmsModuleContext.calculateFinancialDrawdown)(openingBalance, current.transactions);
        const aggregateVerified = ['reconciled', 'not-applicable'].includes(overviewAudit.status);
        const scorecard = (0,__mcmsModuleContext.calculateFinancialScorecard)(current, comparison, { complete: ledger.complete && overviewAudit.status !== 'partial', balanceAvailable, reconciled: reconciliation.reconciled && aggregateVerified, closingBalance });
        let forecastSummary = current;
        let forecastPeriod = period;
        const forecastEnabled = reportComplexity === 'wolf' && __mcmsModuleContext.state.discordReport.includeForecast;
        if (forecastEnabled && period.durationMs > 30 * 86400000) {
            const recentStart = __mcmsModuleContext.Math.max(period.startMs, period.endMs - 30 * 86400000);
            const recentTransactions = currentTransactions.filter(entry => entry.timestamp >= recentStart);
            forecastPeriod = { ...period, startMs: recentStart, durationMs: __mcmsModuleContext.Math.max(1, period.endMs - recentStart), id: 'recent30' };
            forecastSummary = (0,__mcmsModuleContext.summariseFinancialTransactions)(recentTransactions, forecastPeriod);
        }
        const forecast = forecastEnabled ? { ...(0,__mcmsModuleContext.buildFinancialForecast)(forecastSummary, forecastPeriod, closingBalance), basisDays: __mcmsModuleContext.Math.max(1, __mcmsModuleContext.Math.round(forecastPeriod.durationMs / 86400000)) } : null;
        const report = {
            generatedAt: __mcmsModuleContext.Date.now(),
            signature: (0,__mcmsModuleContext.currentFinancialReportSignature)(),
            complexity: reportComplexity,
            period,
            reportDate: (0,__mcmsModuleContext.localIsoDate)(),
            reportDateLabel: `${period.label} · ${period.rangeLabel}`,
            userName: account?.userName || ledger.vault?.player?.name || '',
            userId: account?.userId || ledger.vault?.player?.id || null,
            currentBalance,
            openingBalance,
            closingBalance,
            reconciliationDifference: reconciliation.difference,
            reconciled: reconciliation.reconciled,
            balanceCalculated: balanceAvailable,
            reconciliationLabel,
            ledgerComplete: ledger.complete,
            ledgerCoverageReached: ledger.coverageReached,
            ledgerPages: ledger.pageCount,
            ledgerLastPage: ledger.lastPage,
            ledgerStable: ledger.ledgerStable,
            ledgerScanRetries: ledger.scanRetries,
            ledgerScanCancelled: ledger.scanCancelled,
            ledgerScanLimitReached: ledger.scanLimitReached,
            ledgerSource: ledger.ledgerSource,
            archiveComplete: ledger.archiveComplete,
            archiveTruncated: ledger.archiveTruncated,
            droppedTransactions: ledger.droppedTransactions,
            vaultTransactionCount: ledger.vaultTransactionCount,
            invalidTimestampCount: ledger.invalidTimestampCount,
            overviewAvailable: (0,__mcmsModuleContext.Boolean)(overviewAudit.available),
            overviewStatus: overviewAudit.status,
            overviewLabel: overviewAudit.label,
            overviewRowsUsed: overviewAudit.rowsUsed,
            overviewPages: overviewAudit.pageCount,
            overviewLastPage: overviewAudit.lastPage,
            overviewCoverageReached: overviewAudit.coverageReached,
            overviewMalformedRows: overviewAudit.malformedRowCount,
            overviewDuplicateDates: overviewAudit.duplicateDateCount,
            overviewIncome: overviewAudit.overviewIncome,
            overviewSpending: overviewAudit.overviewSpending,
            overviewNet: overviewAudit.overviewNet,
            ledgerCheckpointIncome: overviewAudit.ledgerIncome,
            ledgerCheckpointSpending: overviewAudit.ledgerSpending,
            ledgerCheckpointNet: overviewAudit.ledgerNet,
            overviewIncomeVariance: overviewAudit.incomeVariance,
            overviewSpendingVariance: overviewAudit.spendingVariance,
            overviewNetVariance: overviewAudit.netVariance,
            overviewUnresolvedVariance: overviewAudit.unresolvedVariance,
            overviewAudit,
            aggregateReconciled: aggregateVerified,
            comparison,
            previous,
            scorecard,
            grade: { score: scorecard.overall, grade: scorecard.grade, label: scorecard.label, marginPercent: scorecard.operatingMarginPercent },
            forecast,
            drawdown,
            chartBlob: null,
            ...current
        };
        report.riskAlerts = (0,__mcmsModuleContext.discordReportComplexityAtLeast)('informative', reportComplexity) && __mcmsModuleContext.state.discordReport.includeRisk ? (0,__mcmsModuleContext.buildFinancialRiskAlerts)(current, comparison, {
            ledgerComplete: ledger.complete,
            drawdown,
            scorecard,
            archiveTruncated: ledger.archiveTruncated,
            droppedTransactions: ledger.droppedTransactions,
            scanLimitReached: ledger.scanLimitReached,
            scanCancelled: ledger.scanCancelled,
            overviewStatus: overviewAudit.status,
            overviewVariance: overviewAudit.unresolvedVariance
        }) : [];
        report.chartBlob = __mcmsModuleContext.state.discordReport.includeChart ? await (0,__mcmsModuleContext.buildFinancialChartBlob)(report) : null;
        return report;
    }),
"buildFinancialChartBlob":__mcmsModuleContext=>(async function buildFinancialChartBlob(report) {
        try {
            const complexity = (0,__mcmsModuleContext.normaliseDiscordReportComplexity)(report.complexity || __mcmsModuleContext.state.discordReport.complexity);
            const canvas = __mcmsModuleContext.document.createElement('canvas');
            canvas.width = 1200;
            canvas.height = 675;
            const context = canvas.getContext('2d');
            if (!context) return null;
            const gradient = context.createLinearGradient(0, 0, 1200, 675);
            gradient.addColorStop(0, '#0b1018');
            gradient.addColorStop(0.55, '#111a27');
            gradient.addColorStop(1, '#080b11');
            context.fillStyle = gradient;
            context.fillRect(0, 0, 1200, 675);
            context.fillStyle = 'rgba(88,166,255,0.12)';
            context.beginPath();
            context.arc(1060, 70, 230, 0, __mcmsModuleContext.Math.PI * 2);
            context.fill();
            context.fillStyle = 'rgba(124,77,255,0.08)';
            context.beginPath();
            context.arc(140, 650, 280, 0, __mcmsModuleContext.Math.PI * 2);
            context.fill();
            context.fillStyle = '#ffffff';
            context.font = '900 34px Arial, sans-serif';
            const graphicTitle = complexity === 'simple'
                ? 'MISSIONCHIEF FINANCE REPORT'
                : complexity === 'informative'
                    ? 'MISSIONCHIEF FINANCE BRIEFING'
                    : 'MISSIONCHIEF FINANCIAL INTELLIGENCE';
            context.fillText(graphicTitle, 54, 58);
            context.fillStyle = 'rgba(255,255,255,0.62)';
            context.font = '600 18px Arial, sans-serif';
            const complexityLabel = complexity === 'wolf' ? 'THE WOLF' : complexity.toUpperCase();
            context.fillText(`${complexityLabel} · ${report.period.label}`, 54, 89);
            context.fillText(report.period.rangeLabel, 54, 116);
            (0,__mcmsModuleContext.roundRectPath)(context, 1002, 38, 142, 70, 20);
            context.fillStyle = report.net > 0 ? 'rgba(46,204,113,0.18)' : report.net < 0 ? 'rgba(231,76,60,0.18)' : 'rgba(241,196,15,0.18)';
            context.fill();
            context.fillStyle = report.net > 0 ? '#67e69b' : report.net < 0 ? '#ff8378' : '#f4d35e';
            context.font = `900 ${complexity === 'wolf' ? 30 : 22}px Arial, sans-serif`;
            context.textAlign = 'center';
            const resultLabel = report.net > 0 ? 'AHEAD' : report.net < 0 ? 'BEHIND' : 'EVEN';
            context.fillText(complexity === 'wolf' ? report.grade.grade : resultLabel, 1073, 73);
            context.font = '700 13px Arial, sans-serif';
            context.fillText(complexity === 'wolf' ? `${report.grade.score}/100` : (0,__mcmsModuleContext.formatSignedCompactCredits)(report.net), 1073, 96);
            context.textAlign = 'left';
            const metricWidth = 261;
            const metricGap = 15;
            (0,__mcmsModuleContext.drawFinancialMetricCard)(context, 54, 148, metricWidth, 98, 'Money in', (0,__mcmsModuleContext.formatSignedCompactCredits)(report.income), '#2ecc71');
            (0,__mcmsModuleContext.drawFinancialMetricCard)(context, 54 + (metricWidth + metricGap), 148, metricWidth, 98, 'Money out', (0,__mcmsModuleContext.formatSignedCompactCredits)(-__mcmsModuleContext.Math.abs(report.spending || 0)), '#e74c3c');
            (0,__mcmsModuleContext.drawFinancialMetricCard)(context, 54 + 2 * (metricWidth + metricGap), 148, metricWidth, 98, 'Net change', (0,__mcmsModuleContext.formatSignedCompactCredits)(report.net), report.net >= 0 ? '#58a6ff' : '#ff6b61');
            (0,__mcmsModuleContext.drawFinancialMetricCard)(context, 54 + 3 * (metricWidth + metricGap), 148, metricWidth, 98, 'Closing balance', report.closingBalance === null ? 'Unavailable' : (0,__mcmsModuleContext.formatCompactCredits)(report.closingBalance), '#f1c40f');
            const chartX = 54;
            const chartY = 288;
            const chartW = 730;
            const chartH = 250;
            (0,__mcmsModuleContext.roundRectPath)(context, chartX, chartY, chartW, chartH, 18);
            context.fillStyle = 'rgba(255,255,255,0.04)';
            context.fill();
            context.fillStyle = '#ffffff';
            context.font = '800 19px Arial, sans-serif';
            context.fillText('NET BALANCE MOVEMENT', chartX + 22, chartY + 32);
            const buckets = report.buckets.slice(-12);
            const maxMagnitude = __mcmsModuleContext.Math.max(1, ...buckets.map(bucket => __mcmsModuleContext.Math.abs(bucket.net)));
            const plotTop = chartY + 58;
            const plotBottom = chartY + chartH - 38;
            const zeroY = plotTop + (plotBottom - plotTop) / 2;
            context.strokeStyle = 'rgba(255,255,255,0.14)';
            context.lineWidth = 1;
            context.beginPath();
            context.moveTo(chartX + 22, zeroY);
            context.lineTo(chartX + chartW - 22, zeroY);
            context.stroke();
            const slotW = (chartW - 52) / __mcmsModuleContext.Math.max(1, buckets.length);
            buckets.forEach((bucket, index) => {
                const height = __mcmsModuleContext.Math.max(2, __mcmsModuleContext.Math.abs(bucket.net) / maxMagnitude * ((plotBottom - plotTop) / 2 - 8));
                const x = chartX + 29 + index * slotW;
                const y = bucket.net >= 0 ? zeroY - height : zeroY;
                (0,__mcmsModuleContext.roundRectPath)(context, x, y, __mcmsModuleContext.Math.max(8, slotW - 10), height, 4);
                context.fillStyle = bucket.net >= 0 ? '#2ecc71' : '#e74c3c';
                context.fill();
                context.fillStyle = 'rgba(255,255,255,0.52)';
                context.font = '600 11px Arial, sans-serif';
                context.textAlign = 'center';
                context.fillText(bucket.label, x + __mcmsModuleContext.Math.max(8, slotW - 10) / 2, chartY + chartH - 15);
            });
            context.textAlign = 'left';
            const detailX = 810;
            const detailY = 288;
            const detailW = 334;
            const detailH = 250;
            (0,__mcmsModuleContext.roundRectPath)(context, detailX, detailY, detailW, detailH, 18);
            context.fillStyle = 'rgba(255,255,255,0.04)';
            context.fill();
            context.fillStyle = '#ffffff';
            context.font = '800 19px Arial, sans-serif';
            context.fillText(complexity === 'simple' ? 'AT A GLANCE' : complexity === 'informative' ? 'USEFUL CONTEXT' : 'OPERATING SNAPSHOT', detailX + 22, detailY + 32);
            const lines = (0,__mcmsModuleContext.financialSnapshotRows)(report, complexity);
            lines.forEach((line, index) => {
                const y = detailY + 65 + index * 29;
                (0,__mcmsModuleContext.drawFinancialSnapshotRow)(context, detailX + 22, y, detailW - 44, line[0], line[1]);
            });
            context.fillStyle = 'rgba(255,255,255,0.42)';
            context.font = '600 14px Arial, sans-serif';
            context.fillText(`${report.activityCount.toLocaleString('en-GB')} transactions · ${report.ledgerPages.toLocaleString('en-GB')} ledger pages · ${report.overviewRowsUsed ? `${report.overviewRowsUsed.toLocaleString('en-GB')} overview day${report.overviewRowsUsed === 1 ? '' : 's'}` : 'overview unavailable'} · Generated ${new __mcmsModuleContext.Date(report.generatedAt).toLocaleString('en-GB')}`, 54, 620);
            context.fillStyle = 'rgba(255,255,255,0.27)';
            context.font = '600 12px Arial, sans-serif';
            context.fillText(`${__mcmsModuleContext.SCRIPT.name} v${__mcmsModuleContext.SCRIPT.version} · ${complexity === 'wolf' ? 'The Wolf financial intelligence' : `${complexityLabel} finance report`} · generated locally`, 54, 648);
            return await new __mcmsModuleContext.Promise(resolve => {
                canvas.toBlob(resolve, 'image/png', 0.92);
            });
        } catch (err) {
            return null;
        }
    }),
"sendDiscordWithRetry":__mcmsModuleContext=>(async function sendDiscordWithRetry(factory, maximumAttempts = 3) {
        let response = null;
        for (let attempt = 0; attempt < maximumAttempts; attempt++) {
            response = await factory();
            if (response.status !== 429 && response.status < 500) return response;
            if (attempt >= maximumAttempts - 1) return response;
            const delayMs = (0,__mcmsModuleContext.discordRetryDelayMs)(response, attempt);
            (0,__mcmsModuleContext.setDiscordStatus)(`Discord delivery delayed by rate limits. Retrying in ${__mcmsModuleContext.Math.ceil(delayMs / 1000)}s…`, 'busy');
            if (!await (0,__mcmsModuleContext.runtimeDelay)(delayMs)) throw new __mcmsModuleContext.Error('Toolkit runtime stopped during Discord retry.');
        }
        return response;
    }),
"sendDiscordFinancialPayload":__mcmsModuleContext=>(async function sendDiscordFinancialPayload(webhookUrl, report) {
        const hasChart = (0,__mcmsModuleContext.Boolean)(report.chartBlob && __mcmsModuleContext.state.discordReport.includeChart);
        const payload = (0,__mcmsModuleContext.buildDiscordFinancialPayload)(report, { withAttachment: hasChart });
        let response;
        if (hasChart) {
            response = await (0,__mcmsModuleContext.sendDiscordWithRetry)(() => {
                const formData = new __mcmsModuleContext.FormData();
                formData.append('payload_json', __mcmsModuleContext.JSON.stringify(payload));
                formData.append('files[0]', report.chartBlob, __mcmsModuleContext.FINANCE_CHART_FILENAME);
                return (0,__mcmsModuleContext.discordHttpRequest)({
                    method: 'POST',
                    url: (0,__mcmsModuleContext.discordWebhookEndpoint)(webhookUrl, { wait: true }),
                    data: formData
                });
            });
            if (response.status === 400 || response.status === 413 || response.status === 415) {
                const errorText = (0,__mcmsModuleContext.String)(response.responseText || '').toLowerCase();
                const attachmentRelated = response.status === 413 || response.status === 415 || /attachment|file|upload|multipart|request entity too large/iu.test(errorText);
                if (attachmentRelated) {
                    const fallbackPayload = (0,__mcmsModuleContext.buildDiscordFinancialPayload)(report, { withAttachment: false });
                    response = await (0,__mcmsModuleContext.sendDiscordWithRetry)(() => (0,__mcmsModuleContext.discordHttpRequest)({
                        method: 'POST',
                        url: (0,__mcmsModuleContext.discordWebhookEndpoint)(webhookUrl, { wait: true }),
                        headers: { 'Content-Type': 'application/json' },
                        data: __mcmsModuleContext.JSON.stringify(fallbackPayload)
                    }));
                }
            }
        } else {
            response = await (0,__mcmsModuleContext.sendDiscordWithRetry)(() => (0,__mcmsModuleContext.discordHttpRequest)({
                method: 'POST',
                url: (0,__mcmsModuleContext.discordWebhookEndpoint)(webhookUrl, { wait: true }),
                headers: { 'Content-Type': 'application/json' },
                data: __mcmsModuleContext.JSON.stringify(payload)
            }));
        }
        if (response.status < 200 || response.status >= 300) throw new __mcmsModuleContext.Error((0,__mcmsModuleContext.parseDiscordError)(response));
        return response;
    }),
"postDiscordFinancialReport":__mcmsModuleContext=>(async function postDiscordFinancialReport(){
  if(__mcmsModuleContext.discordFinanceBusy)return;__mcmsModuleContext.discordFinanceBusy=true;
  (0,__mcmsModuleContext.setDiscordStatus)('Preparing the financial report for review…','busy');
  try{__mcmsModuleContext.pilot.discordLastReportAt=await (0,__mcmsModuleContext.pilotCall)({op:'discordReceipt',account:__mcmsModuleContext.pilot.account()}).promise;const report=await (0,__mcmsModuleContext.buildFinancialReport)();let chart;if(report.chartBlob&&__mcmsModuleContext.state.discordReport.includeChart){chart=await new __mcmsModuleContext.Promise((resolve,reject)=>{const reader=new __mcmsModuleContext.FileReader();reader.onload=()=>resolve(reader.result);reader.onerror=()=>reject((0,__mcmsModuleContext.Error)('Chart could not be read. Choose Text only and prepare again.'));reader.readAsDataURL(report.chartBlob);});}await (0,__mcmsModuleContext.pilotCall)({op:'discordPost',account:__mcmsModuleContext.pilot.account(),kind:'finance',generatedAt:report.generatedAt,payload:(0,__mcmsModuleContext.buildDiscordFinancialPayload)(report,{withAttachment:false}),chart}).promise;(0,__mcmsModuleContext.setDiscordStatus)('Posted to Discord.','good');}
  catch(error){(0,__mcmsModuleContext.setDiscordStatus)(error.message,'bad');}
  finally{__mcmsModuleContext.discordFinanceBusy=false;}
})};})();

})();
