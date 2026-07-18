PAYLOAD = r'''    function scanMissionRequirementsWindows() {
        if (runtime.destroyed || !missionRequirementsPrimaryRuntime()) return;
        if (!state.missionRequirements) {
            clearMissionRequirementsPanels();
            return;
        }
        const activeSources = new Set();
        const activeDocuments = new WeakSet();
        for (const candidate of missionRequirementsWindowCandidates()) {
            const source = missionRequirementsSourceForCandidate(candidate) || missionRequirementsAnchorForCandidate(candidate);
            if (!source || source.isConnected === false) continue;
            const doc = source.ownerDocument || candidate?.root?.ownerDocument || document;
            if (!doc || activeDocuments.has(doc)) continue;
            activeDocuments.add(doc);
            ensureMissionRequirementsDocumentStyle(doc);
            if (missionRequirementsLssmActive(candidate, source)) {
                missionRequirementsRemoveRecord(source);
                continue;
            }
            activeSources.add(source);
            missionRequirementsEnsureRecord({ ...candidate, source }, source);
        }
        for (const source of Array.from(missionRequirementsRecords.keys())) {
            if (source.isConnected === false || !activeSources.has(source)) missionRequirementsRemoveRecord(source);
        }
    }'''
