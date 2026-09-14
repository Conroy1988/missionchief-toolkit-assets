        // A max-level hospital may no longer expose its expansion page.
        // Verify the authoritative owned record instead of requiring that page.
        if (item.hospitalTargetLevel) {
            if (item.typeId !== '4' || item.kind !== 'level' || item.actionSuffix !== 'expand_do/credits'
                || !Number.isInteger(item.hospitalTargetLevel) || item.hospitalTargetLevel <= before.level || item.hospitalTargetLevel > 30) {
                throw (0,__mcmsModuleContext.expansionPlannerSafetyStop)('Invalid hospital target after submission. Review the saved purchase before continuing.');
            }
            let hospitalAfter;
            try { hospitalAfter = await (0,__mcmsModuleContext.fetchExpansionPlannerBuilding)(item.buildingId); }
            catch (err) { throw (0,__mcmsModuleContext.expansionPlannerSafetyStop)(`Hospital purchase was submitted, but its current level could not be read: ${err?.message || 'unknown read error'}. Use Review & resume to verify it; no purchase will be repeated.`); }
            (0,__mcmsModuleContext.expansionPlannerAssertScope)(hospitalAfter, item, true);
            if (hospitalAfter.level !== item.hospitalTargetLevel) {
                throw (0,__mcmsModuleContext.expansionPlannerSafetyStop)(`Hospital purchase was submitted, but the game reports level ${hospitalAfter.level}; expected ${item.hospitalTargetLevel}. Use Review & resume to verify it; no purchase will be repeated.`);
            }
            return { record: hospitalAfter, detail: `Level ${hospitalAfter.level} · ${item.priceCredits.toLocaleString()} Credits verified` };
        }
