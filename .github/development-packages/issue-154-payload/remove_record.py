PAYLOAD = r'''    function missionRequirementsRemoveRecord(source) {
        const record = missionRequirementsRecords.get(source);
        if (!record) {
            missionRequirementsRestoreSource(source);
            if (source?.getAttribute?.('data-mcms-requirements-anchor') === '1') source.remove?.();
            return;
        }
        if (record.frame) runtimeCancelAnimationFrame(record.frame);
        runtimeUntrackObserver(record.observer);
        try { record.panel?.remove(); } catch (err) {}
        missionRequirementsRestoreSource(record.source);
        if (record.source?.getAttribute?.('data-mcms-requirements-anchor') === '1') record.source.remove?.();
        missionRequirementsRecords.delete(source);
    }'''
