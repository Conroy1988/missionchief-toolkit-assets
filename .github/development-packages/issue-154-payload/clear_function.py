PAYLOAD = r'''    function clearMissionRequirementsPanels() {
        for (const source of Array.from(missionRequirementsRecords.keys())) missionRequirementsRemoveRecord(source);
        for (const context of transportSweepDocumentContexts()) {
            try {
                context.doc.querySelectorAll?.(`#${SCRIPT.missionRequirementsPanelId}`).forEach(panel => panel.remove());
                context.doc.querySelectorAll?.('[data-mcms-requirements-source-hidden="1"]').forEach(missionRequirementsRestoreSource);
                context.doc.querySelectorAll?.('[data-mcms-requirements-anchor="1"]').forEach(anchor => anchor.remove());
            } catch (err) {}
        }
    }'''
