(() => {const seed=window.__MCMS_EXTENSION_SEED__||window.__MCMS_EXTENSION_PILOT__?.documentIdentity;if(!seed||(seed.documentToken&&(location.origin!==seed.origin||document.documentElement.getAttribute('data-mcms-extension-document')!==seed.documentToken)))return;
(()=>{'use strict';window.__MCMS_EXTENSION_FEATURES__ ||= Object.create(null);window.__MCMS_EXTENSION_FEATURES__["intelligence"] ||= {"fetchUkKnowledgePayload":__mcmsModuleContext=>(async function fetchUkKnowledgePayload() {
        if (__mcmsModuleContext.ukKnowledgeLoadPromise) return __mcmsModuleContext.ukKnowledgeLoadPromise;
        __mcmsModuleContext.ukKnowledgeLoadPromise = (async () => {
        const [capabilities, units, personnel] = await __mcmsModuleContext.Promise.all([
            (0,__mcmsModuleContext.ukKnowledgeRequestJson)('capabilities.json'),
            (0,__mcmsModuleContext.ukKnowledgeRequestJson)('units.json'),
            (0,__mcmsModuleContext.ukKnowledgeRequestJson)('personnel.json')
        ]);
        const payload = (0,__mcmsModuleContext.validateUkKnowledgePayload)(capabilities, units, personnel, __mcmsModuleContext.Date.now());
        (0,__mcmsModuleContext.gmSetValueSafe)(__mcmsModuleContext.SCRIPT.ukKnowledgeCacheState, payload);
        return payload;
        })().finally(() => { __mcmsModuleContext.ukKnowledgeLoadPromise = null; });
        return __mcmsModuleContext.ukKnowledgeLoadPromise;
    }),
"openUkKnowledgeDossier":__mcmsModuleContext=>(async function openUkKnowledgeDossier(requirementName, requirementKey = '', trigger = null, force = false) {
        const name = (0,__mcmsModuleContext.ukKnowledgeText)(requirementName, 180);
        if (!name) return;
        __mcmsModuleContext.ukKnowledgeActiveRequirement = { name, key: (0,__mcmsModuleContext.normaliseUkKnowledgeKey)(requirementKey || name) };
        if (trigger?.isConnected) __mcmsModuleContext.ukKnowledgeReturnFocus = trigger;
        const cache = (0,__mcmsModuleContext.readUkKnowledgeCache)();
        const cachedModel = cache.payload
            ? (0,__mcmsModuleContext.ukKnowledgeRequirementModel)(name, requirementKey, cache.payload, cache.freshness === 'fresh' ? 'cache' : 'stale')
            : null;
        (0,__mcmsModuleContext.renderUkKnowledgeDossier)(
        cachedModel || (0,__mcmsModuleContext.ukKnowledgeRequirementModel)(name, requirementKey, null, 'local'),
        cache.freshness === 'fresh' && !force
            ? { tone: 'good', message: 'Verified guide intelligence loaded from the update-stable cache.' }
            : { tone: 'busy', message: cache.payload ? 'Showing cached intelligence while the UK Guide refreshes…' : 'Loading verified units, crew and training from the UK Guide…', loading: true }
        );
        (0,__mcmsModuleContext.operationalPressureBoardElement)()?.querySelector('[data-pressure-command="knowledge-close"]')?.focus?.({ preventScroll: true });
        if (cache.freshness === 'fresh' && !force) return;
        try {
        const payload = await (0,__mcmsModuleContext.fetchUkKnowledgePayload)();
        if (!__mcmsModuleContext.ukKnowledgeActiveRequirement || __mcmsModuleContext.ukKnowledgeActiveRequirement.name !== name) return;
        (0,__mcmsModuleContext.renderUkKnowledgeDossier)(
            (0,__mcmsModuleContext.ukKnowledgeRequirementModel)(name, requirementKey, payload, 'live'),
            { tone: 'good', message: 'Verified UK Guide intelligence is current.' }
        );
        } catch (err) {
        if (!__mcmsModuleContext.ukKnowledgeActiveRequirement || __mcmsModuleContext.ukKnowledgeActiveRequirement.name !== name) return;
        (0,__mcmsModuleContext.renderUkKnowledgeDossier)(
            cachedModel || (0,__mcmsModuleContext.ukKnowledgeRequirementModel)(name, requirementKey, null, 'local'),
            { tone: cache.payload ? 'warning' : 'bad', message: `${err?.message || 'The UK Guide could not be reached.'} ${cache.payload ? 'The bounded cached copy remains in use.' : 'The bundled capability catalogue remains available.'}` }
        );
        }
    }),
"refreshOperationalPressureBoard":__mcmsModuleContext=>(async function refreshOperationalPressureBoard(force = false) {
        if (__mcmsModuleContext.operationalPressureRefreshBusy) return null;
        __mcmsModuleContext.operationalPressureRefreshBusy = true;
        (0,__mcmsModuleContext.setOperationalSitrepStatus)('Refreshing mission and fleet intelligence…', 'busy');
        (0,__mcmsModuleContext.renderOperationalPressureBoard)();
        try {
            (0,__mcmsModuleContext.refreshMissionSnapshots)();
            await (0,__mcmsModuleContext.refreshPersonalVehicleData)((0,__mcmsModuleContext.Boolean)(force));
            (0,__mcmsModuleContext.refreshMissionSnapshots)();
            (0,__mcmsModuleContext.invalidateOperationalPressureSnapshot)();
            const snapshot = (0,__mcmsModuleContext.buildOperationalPressureSnapshot)(true);
            (0,__mcmsModuleContext.setOperationalSitrepStatus)(`Pressure picture refreshed at ${(0,__mcmsModuleContext.formatRefreshClockTime)(snapshot.generatedAt)}.`, 'good');
            return snapshot;
        } catch (err) {
            (0,__mcmsModuleContext.setOperationalSitrepStatus)(err?.message || 'Pressure intelligence could not be refreshed.', 'bad');
            return null;
        } finally {
            __mcmsModuleContext.operationalPressureRefreshBusy = false;
            (0,__mcmsModuleContext.renderOperationalPressureBoard)(true);
        }
    }),
"runToolkitDoctor":__mcmsModuleContext=>(async function runToolkitDoctor(){
  const checks=[];
  checks.push({label:'Extension version',tone:'good',detail:`Extension ${__mcmsModuleContext.seed.version}; browser-managed updates for store installations.`});
  checks.push({label:'Runtime ownership',tone:__mcmsModuleContext.document.querySelectorAll(`[id="${__mcmsModuleContext.SCRIPT.controlId}"]`).length===1?'good':'warn',detail:'Checking for one Toolkit launcher in this page.'});
  checks.push({label:'Settings',tone:__mcmsModuleContext.pilot.storageError?'bad':__mcmsModuleContext.saving||__mcmsModuleContext.pendingWrites.size?'warn':'good',detail:__mcmsModuleContext.pilot.storageError||((__mcmsModuleContext.saving||__mcmsModuleContext.pendingWrites.size)?'Changes are still saving.':'Extension settings are saved; changes are synchronised between game tabs.')});
  checks.push({label:'Packaged features',tone:'good',detail:`${__mcmsModuleContext.Object.keys(__mcmsModuleContext.window.__MCMS_EXTENSION_FEATURES__||{}).length} feature groups loaded on demand.`});
  checks.push({label:'Background task',tone:__mcmsModuleContext.pilot.job?'warn':'good',detail:__mcmsModuleContext.pilot.job?'A task is active. Review its progress in the extension popup.':'No active task in this tab.'});
  const report={installedVersion:__mcmsModuleContext.seed.version,availableVersion:'Browser managed',deviceLayout:__mcmsModuleContext.activeDeviceLayout,checks};
  (0,__mcmsModuleContext.renderToolkitDoctor)(report);return report;
}),
"loadHelpCenterGuide":__mcmsModuleContext=>(async function loadHelpCenterGuide(force = false) {
        const overlay = (0,__mcmsModuleContext.createHelpCenter)();
        const frame = overlay.querySelector('.mcms-help-frame');
        const status = overlay.querySelector('[data-help-status]');
        const errorText = overlay.querySelector('[data-help-error]');
        overlay.classList.add('mcms-loading');
        overlay.classList.remove('mcms-error');
        if (status) status.textContent = force ? 'Refreshing…' : 'Loading…';
        try {
            const documentText = await (0,__mcmsModuleContext.requestHelpGuideDocument)(force);
            if (!overlay.isConnected || __mcmsModuleContext.runtime.destroyed) return false;
            frame.srcdoc = (0,__mcmsModuleContext.protectHelpGuideDocument)(documentText);
            overlay.classList.remove('mcms-error');
            if (status) status.textContent = `Guide ${__mcmsModuleContext.HELP_CENTER.guideVersion} · online`;
            return true;
        } catch (err) {
            if (!overlay.isConnected || __mcmsModuleContext.runtime.destroyed) return false;
            overlay.classList.add('mcms-error');
            if (status) status.textContent = 'Offline fallback';
            if (errorText) errorText.textContent = `${err?.message || 'The public guide could not be loaded.'} The main Toolkit remains fully operational.`;
            return false;
        } finally {
            overlay.classList.remove('mcms-loading');
        }
    })};})();

})();
