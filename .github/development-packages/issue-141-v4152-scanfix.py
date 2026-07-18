#!/usr/bin/env python3
from __future__ import annotations

from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
SELF = Path(__file__).resolve()
WRAPPER = ROOT / ".github" / "development-packages" / "issue-141-v4152-wrapper.py"
DIAGNOSTIC = ROOT / ".github" / "development-packages" / "issue-141-v4152-diagnostic.txt"

source = WRAPPER.read_text(encoding="utf-8")
start = source.find('scan_transform = """source = replace_function(source, \\"scanMissionRequirementsWindows\\"')
end_marker = 'package = package[:scan_start] + scan_transform + package[scan_end:]'
end = source.find(end_marker, start)
if start < 0 or end < 0:
    raise AssertionError("Issue #141 wrapper scan-transform boundaries were not found")
end += len(end_marker)

replacement = """old_scan = r'''function scanMissionRequirementsWindows() {
        if (!state.missionRequirements) {
            clearMissionRequirementsPanels();
            return;
        }
        const activeSources = new Set();
        const activeDocuments = new WeakSet();
        for (const candidate of missionValueWindowCandidates()) {
            const source = missionRequirementsSourceForCandidate(candidate);
            if (!source || !source.isConnected) continue;
            const doc = source.ownerDocument || document;
            if (activeDocuments.has(doc)) continue;
            if (missionRequirementsLssmActive(candidate, source)) {
                missionRequirementsRemoveRecord(source);
                activeDocuments.add(doc);
                continue;
            }
            const raw = missionRequirementsElementText(source);
            if (!raw) {
                missionRequirementsRemoveRecord(source);
                continue;
            }
            activeDocuments.add(doc);
            activeSources.add(source);
            missionRequirementsEnsureRecord(candidate, source);
        }
        for (const source of Array.from(missionRequirementsRecords.keys())) {
            if (!activeSources.has(source) || !source.isConnected) missionRequirementsRemoveRecord(source);
        }
    }'''
new_scan = r'''function scanMissionRequirementsWindows() {
        if (runtime.destroyed) return;
        if (!state.missionRequirements) {
            clearMissionRequirementsPanels();
            return;
        }
        const activeSources = new Set();
        const activeDocuments = new WeakSet();
        for (const candidate of missionRequirementsWindowCandidates()) {
            const source = missionRequirementsSourceForCandidate(candidate);
            if (!source || source.isConnected === false) continue;
            const doc = source.ownerDocument || candidate?.root?.ownerDocument || document;
            if (!doc || activeDocuments.has(doc)) continue;
            activeDocuments.add(doc);
            ensureMissionRequirementsDocumentStyle(doc);
            if (missionRequirementsLssmActive(candidate, source)) {
                missionRequirementsRemoveRecord(source);
                continue;
            }
            const raw = missionRequirementsElementText(source);
            if (!raw) {
                missionRequirementsRemoveRecord(source);
                continue;
            }
            activeSources.add(source);
            missionRequirementsEnsureRecord(candidate, source);
        }
        for (const source of Array.from(missionRequirementsRecords.keys())) {
            if (source.isConnected === false || !activeSources.has(source)) missionRequirementsRemoveRecord(source);
        }
    }'''
scan_transform = 'source = replace_once(source, old_scan, new_scan, "Mission Requirements direct native scan")'
package = package[:scan_start] + scan_transform + package[scan_end:]"""

source = source[:start] + replacement + source[end:]
namespace = {"__file__": str(WRAPPER), "__name__": "__main__"}
exec(compile(source, str(WRAPPER), "exec"), namespace, namespace)
DIAGNOSTIC.unlink(missing_ok=True)
SELF.unlink(missing_ok=True)
