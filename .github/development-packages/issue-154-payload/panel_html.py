PAYLOAD = r'''    function missionRequirementsPanelHtml(rows, unresolved) {
        const definiteOutstanding = rows.filter(row => row.definitelyOpen).length;
        const uncertain = rows.filter(row => row.uncertain).length + unresolved.length;
        const stateName = missionRequirementsOverallState(rows, unresolved);
        const summary = stateName === 'success'
            ? 'All requirements covered'
            : stateName === 'warning'
                ? `${uncertain} requirement${uncertain === 1 ? '' : 's'} need confirmation`
                : `${definiteOutstanding} requirement${definiteOutstanding === 1 ? '' : 's'} outstanding`;
        const rowHtml = rows.map(row => {
            const rowState = row.covered ? 'covered' : row.uncertain ? 'unresolved' : row.partial ? 'partial' : 'open';
            const prefix = row.covered ? '✓ ' : '';
            return `<tr data-row-state="${rowState}"><td>${escapeHtml(prefix + row.requirement)}</td><td data-label="Missing on mission">${row.missing.toLocaleString('en-GB')}</td><td data-label="En-route">${escapeHtml(row.enRouteText)}</td><td class="mcms-req-still" data-label="Still needed">${escapeHtml(row.stillNeededText)}</td><td data-label="Selected">${escapeHtml(row.selectedText)}</td></tr>`;
        }).join('');
        const unknownHtml = unresolved.length
            ? `<div class="mcms-req-unknown"><b>Unresolved MissionChief requirement</b>${unresolved.map(item => `<span>${escapeHtml(item.text)}</span>`).join('')}<button type="button" class="mcms-req-report" data-mcms-report-mission>Report Mission</button></div>`
            : '';
        return {
            stateName,
            html: `<div class="mcms-req-head"><div class="mcms-req-title"><i aria-hidden="true"></i><span>Mission Requirements</span></div><span class="mcms-req-summary">${escapeHtml(summary)}</span><button type="button" class="mcms-req-collapse" data-mcms-requirements-collapse aria-label="Collapse mission requirements" aria-expanded="true">⌃</button></div><div class="mcms-req-body"><table aria-label="Live mission requirements"><colgroup><col class="mcms-req-name-col"><col class="mcms-req-number-col"><col class="mcms-req-number-col"><col class="mcms-req-number-col"><col class="mcms-req-number-col"></colgroup><thead><tr><th scope="col">Requirement</th><th scope="col">Missing on mission</th><th scope="col">En-route</th><th scope="col">Still needed</th><th scope="col">Selected</th></tr></thead><tbody>${rowHtml}</tbody></table>${unknownHtml}</div>`
        };
    }'''
