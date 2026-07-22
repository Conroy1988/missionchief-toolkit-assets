    function toggleFeature(feature) {
        handleMapVisibilityToggle(feature);
        handleMissionWindowToggle(feature);
        handlePayoutAudioToggle(feature);
        if (feature === 'clean') state.cleanMode = !state.cleanMode;
        if (feature === 'shortcuts') state.shortcuts = !state.shortcuts;
        if (feature === 'autoLoadAllVehicles') {
            state.autoLoadAllVehicles = !state.autoLoadAllVehicles;
            if (state.autoLoadAllVehicles) installAutoLoadAllVehicles();
            else stopAutoLoadAllVehicles();
        }
        if (feature === 'allianceBuildingsMapBlocker') state.allianceBuildingsMap = state.allianceBuildingsMap === false;
        if (feature === 'majorIncidentFeed') state.majorIncidentFeed.enabled = !state.majorIncidentFeed.enabled;
        if (feature === 'allianceCredits') state.allianceCredits = !state.allianceCredits;
        if (feature === 'missionAge') state.missionAge = !state.missionAge;
        if (feature === 'unitCommitment') state.unitCommitment = !state.unitCommitment;
        if (feature === 'transportWatcher') state.transportWatcher = !state.transportWatcher;
        if (feature === 'stuckDetector') state.stuckDetector.enabled = !state.stuckDetector.enabled;
        if (feature === 'missionSpawn') state.missionSpawn.enabled = !state.missionSpawn.enabled;
        if (feature === 'missionSpawn') {
            missionSpawnArmed = false;
            runtimeClearTimeout(missionSpawnPrimeTimer);
            knownMissionIds.clear();
            if (state.missionSpawn.enabled) primeMissionSpawnDetector();
        }
        if (feature === 'resourceGap') state.resourceGap.enabled = !state.resourceGap.enabled;
        if (feature === 'criticalView') { toggleCriticalView(); return; }
        if (feature === 'compactDock') state.compactDock = !state.compactDock;
        if (feature === 'autoNight') {
            state.autoNight.enabled = !state.autoNight.enabled;
            state.autoNight.lastBucket = '';
        }
        if (state.cleanMode) closePanel();
        if (!criticalViewActive) saveState();
        applyRootAttributes();
        updateUI();
        applyMapVisibilityToggleEffects(feature);
        reconcileFeatureRefreshes({ includeSnapshots: missionSnapshotsNeeded(), positionPanel: false });
        applyMissionWindowToggleEffects(feature);
        applyPayoutAudioToggleEffects(feature);
        if (feature === 'autoLoadAllVehicles') showToast(state.autoLoadAllVehicles ? 'Auto-load all vehicles on' : 'Auto-load all vehicles off');
        if (feature === 'allianceCredits') showToast(state.allianceCredits ? 'Alliance credits on' : 'Alliance credits off');
        if (feature === 'missionAge') showToast(state.missionAge ? 'Personal mission age on' : 'Personal mission age off');
        if (feature === 'unitCommitment') {
            if (state.unitCommitment) {
                showToast('Loading unit assignments…');
                refreshPersonalVehicleData(true).then(ok => {
                    scheduleUnitCommitmentRefresh(0);
                    showToast(ok ? 'Unit Count on' : 'Unit Count on · live vehicle data unavailable');
                });
            } else showToast('Unit Count off');
        }
        if (feature === 'transportWatcher') showToast(state.transportWatcher ? 'Transport Watcher on' : 'Transport Watcher off');
        if (feature === 'majorIncidentFeed') {
            if (state.majorIncidentFeed.enabled) {
                refreshMissionSnapshots();
                scheduleMajorIncidentFeedRender(0);
            } else removeMajorIncidentFeed();
            showToast(state.majorIncidentFeed.enabled ? 'Major Incident Feed on' : 'Major Incident Feed off');
        }
        if (feature === 'allianceBuildingsMapBlocker') {
            if (state.allianceBuildingsMap === false) {
                installAllianceBuildingsEarlyStyle();
                installAllianceBuildingsLeafletAssignmentGuard();
                installAllianceBuildingsContextWatcherEarly();
            } else {
                clearAllianceBuildingsEarlyContext();
            }
            showToast(state.allianceBuildingsMap === false ? 'Alliance Map Blocker ON · reloading' : 'Alliance Map Blocker OFF · reloading');
            if (isAllianceBuildingsContext()) runtimeSetTimeout(() => location.reload(), 180);
        }
        if (feature === 'stuckDetector') showToast(state.stuckDetector.enabled ? `Stuck detector on · ${state.stuckDetector.thresholdMin} min` : 'Stuck detector off');
        if (feature === 'missionSpawn') showToast(state.missionSpawn.enabled ? 'New mission animation on' : 'New mission animation off');
        if (feature === 'resourceGap') {
            if (state.resourceGap.enabled) refreshPersonalVehicleData(false).then(() => { scheduleResourceGapRefresh(0); refreshVisibleMissionInspector(); });
            showToast(state.resourceGap.enabled ? `Resource Gap on · ${state.resourceGap.radiusMi}mi` : 'Resource Gap off');
        }
        if (feature === 'autoNight') runAutoNight(true);
    }
