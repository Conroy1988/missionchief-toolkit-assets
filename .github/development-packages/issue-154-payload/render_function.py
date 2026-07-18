PAYLOAD = r'''    function missionRequirementsSafeDiagnostic(value, limit = 600) {
        let text = String(value ?? '').replace(/[\u0000-\u001f\u007f]+/g, ' ').replace(/\s+/g, ' ').trim();
        text = text
            .replace(/https?:\/\/(?:discord(?:app)?\.com\/api\/webhooks|[^\s/]+\/webhooks)\/\S+/gi, '[redacted webhook]')
            .replace(/\b(?:csrf|authenticity|authorization|session|cookie|token|password|secret|api[_-]?key)\b\s*[:=]\s*[^\s,;]+/gi, match => `${match.split(/[:=]/)[0]}: [redacted]`)
            .replace(/\b[A-Z0-9._%+-]+@[A-Z0-9.-]+\.[A-Z]{2,}\b/gi, '[redacted email]')
            .replace(/-?\d{1,3}\.\d{4,}\s*[,/]\s*-?\d{1,3}\.\d{4,}/g, '[redacted coordinates]');
        return text.slice(0, Math.max(0, limit));
    }

    function missionRequirementsTypeSummary(units) {
        const counts = new Map();
        for (const unit of units || []) if (Number.isFinite(unit?.typeId) && unit.typeId >= 0) counts.set(unit.typeId, (counts.get(unit.typeId) || 0) + 1);
        return Array.from(counts.entries()).sort((a, b) => a[0] - b[0]).map(([type, count]) => `${type}×${count}`).join(', ') || 'None detected';
    }

    function missionRequirementsMissionTitle(record) {
        const root = record?.candidate?.root || record?.candidate?.mount;
        const node = root?.querySelector?.('[data-mission-title], #mission_name, .mission-title, .mission_caption, h1');
        return missionRequirementsSafeDiagnostic(node?.getAttribute?.('data-mission-title') || node?.textContent || node?.innerText || '', 100);
    }

    function missionRequirementsReportUrl(record, reason = 'unknown') {
        const candidate = record?.candidate || {};
        const source = record?.source;
        const root = candidate.root || candidate.mount;
        const doc = source?.ownerDocument || root?.ownerDocument;
        const view = doc?.defaultView || pageWindow;
        const missionId = missionRequirementsMissionIdentity(candidate, source) || 'Unknown';
        const title = missionRequirementsMissionTitle(record);
        const missionType = missionRequirementsMissionTypeId(candidate);
        const raw = source?.getAttribute?.('data-mcms-requirements-anchor') === '1' ? '' : missionRequirementsElementText(source);
        let parsed = { requirements: [], unresolved: [] };
        try { if (raw) parsed = missionRequirementsParseSource(source); } catch (err) {}
        const selected = missionRequirementsCollectUnits(candidate, 'selected');
        const enRoute = missionRequirementsCollectUnits(candidate, 'enroute');
        const classes = Array.from(source?.classList || []).filter(value => /^[A-Za-z0-9_-]{1,40}$/.test(value)).slice(0, 8).join(' ');
        const count = selector => { try { return root?.querySelectorAll?.(selector)?.length || 0; } catch (err) { return 0; } };
        const platform = missionRequirementsSafeDiagnostic(view?.navigator?.userAgentData?.platform || view?.navigator?.platform || 'Unknown', 80);
        const mobile = view?.navigator?.userAgentData?.mobile === true ? 'yes' : 'no/unknown';
        const path = missionRequirementsSafeDiagnostic(view?.location?.pathname || '', 180);
        const mode = state.uiMode || state.operatingMode || (Number(view?.innerWidth) <= 767 ? 'mobile' : Number(view?.innerWidth) <= 1180 ? 'tablet' : 'desktop');
        const fields = [
            '## Automatically harvested Mission Requirements diagnostic',
            '',
            '> Review this report before submitting. No GitHub token, cookies, chat, coordinates, addresses, vehicle IDs or authentication data are included.',
            '',
            `- **Failure reason:** ${missionRequirementsSafeDiagnostic(reason, 120) || 'Unknown'}`,
            `- **Mission ID:** ${missionId}`,
            `- **Mission title:** ${title || 'Unavailable'}`,
            `- **Mission type ID:** ${missionType ?? 'Unavailable'}`,
            `- **MissionChief path:** ${path || 'Unavailable'}`,
            `- **Toolkit version:** ${SCRIPT.version}`,
            `- **Layout:** ${missionRequirementsSafeDiagnostic(mode, 40)}`,
            `- **Viewport:** ${Number(view?.innerWidth) || 0}×${Number(view?.innerHeight) || 0}`,
            `- **Platform:** ${platform}; mobile=${mobile}`,
            '',
            '### Requirement source',
            `- Present: ${source?.getAttribute?.('data-mcms-requirements-anchor') === '1' ? 'No' : 'Yes'}`,
            `- Element: ${missionRequirementsSafeDiagnostic(source?.tagName || 'Unavailable', 30)}#${missionRequirementsSafeDiagnostic(source?.id || '', 60)}`,
            `- Classes: ${missionRequirementsSafeDiagnostic(classes, 180) || 'None'}`,
            `- Typed groups: ${count('[data-requirement-type]')}`,
            `- Parsed rows: ${parsed.requirements.length}`,
            `- Unresolved fragments: ${parsed.unresolved.length}`,
            '',
            '### Native selector counts',
            `- missing_text: ${count('#missing_text')}`,
            `- selected checkboxes: ${count('.vehicle_checkbox:checked')}`,
            `- en-route rows: ${count('#mission_vehicle_driving tbody tr')}`,
            `- selected vehicle types: ${missionRequirementsTypeSummary(selected)}`,
            `- en-route vehicle types: ${missionRequirementsTypeSummary(enRoute)}`,
            '',
            '### Visible requirement text',
            '```text',
            missionRequirementsSafeDiagnostic(raw, 1200) || 'Unavailable',
            '```'
        ];
        const issueTitle = `Mission requirements missing: ${title || `Mission ${missionId}`}`.slice(0, 180);
        let body = fields.join('\n');
        const build = () => {
            const params = new URLSearchParams({ title: issueTitle, labels: 'Mission Info Missing', body });
            return `https://github.com/Conroy1988/missionchief-toolkit-assets/issues/new?${params.toString()}`;
        };
        let url = build();
        while (url.length > 7600 && body.length > 1800) {
            body = `${body.slice(0, Math.max(1500, body.length - 500))}\n\n_Report shortened to fit GitHub's issue URL limit._`;
            url = build();
        }
        return url;
    }

    function missionRequirementsFallbackHtml(kind) {
        const loading = kind === 'loading';
        const empty = kind === 'empty';
        const message = loading ? 'Loading mission requirements…' : empty ? 'No outstanding requirements reported by MissionChief.' : 'Unable to pull mission requirements';
        const summary = loading ? 'Loading' : empty ? 'No outstanding requirements' : 'Requirements unavailable';
        const report = loading || empty ? '' : '<button type="button" class="mcms-req-report" data-mcms-report-mission>Report Mission</button>';
        return { stateName: 'warning', html: `<div class="mcms-req-head"><div class="mcms-req-title"><i aria-hidden="true"></i><span>Mission Requirements</span></div><span class="mcms-req-summary">${summary}</span></div><div class="mcms-req-fallback"><span class="mcms-req-fallback-message">${message}</span>${report}</div>` };
    }

    function missionRequirementsPresent(record, presentation, reason = '') {
        record.panel.dataset.state = presentation.stateName;
        record.panel.dataset.mcmsTheme = state.uiTheme;
        if (reason) record.panel.dataset.mcmsReportReason = reason;
        else delete record.panel.dataset.mcmsReportReason;
        setInnerHtmlIfChanged(record.panel, presentation.html);
        const collapse = record.panel.querySelector('[data-mcms-requirements-collapse]');
        if (collapse) {
            const expanded = !record.panel.classList.contains('mcms-collapsed');
            collapse.setAttribute('aria-expanded', String(expanded));
            collapse.setAttribute('aria-label', expanded ? 'Collapse mission requirements' : 'Expand mission requirements');
            collapse.textContent = expanded ? '⌃' : '⌄';
        }
    }

    function missionRequirementsRenderRecord(record) {
        if (!record?.source?.isConnected || !record?.candidate?.mount?.isConnected || !record?.panel?.isConnected) {
            scheduleMissionRequirementsScan(0);
            return;
        }
        if (missionRequirementsLssmActive(record.candidate, record.source)) {
            missionRequirementsRemoveRecord(record.source);
            return;
        }
        const age = Date.now() - (record.startedAt || Date.now());
        const anchor = record.source.getAttribute?.('data-mcms-requirements-anchor') === '1';
        if (anchor) {
            missionRequirementsRestoreSource(record.source);
            missionRequirementsPresent(record, missionRequirementsFallbackHtml(age < 1200 ? 'loading' : 'error'), age < 1200 ? '' : 'requirement source absent');
            return;
        }
        const raw = missionRequirementsElementText(record.source);
        if (!raw) {
            missionRequirementsRestoreSource(record.source);
            missionRequirementsPresent(record, missionRequirementsFallbackHtml(age < 1200 ? 'loading' : 'empty'));
            return;
        }
        let parsed;
        try { parsed = missionRequirementsParseSource(record.source); }
        catch (err) {
            missionRequirementsRestoreSource(record.source);
            missionRequirementsPresent(record, missionRequirementsFallbackHtml('error'), `parser exception: ${err?.message || 'unknown'}`);
            return;
        }
        if (!parsed.requirements.length) {
            missionRequirementsRestoreSource(record.source);
            missionRequirementsPresent(record, missionRequirementsFallbackHtml('error'), parsed.unresolved.length ? 'requirement text unparseable' : 'no quantified requirements detected');
            return;
        }
        missionRequirementsHideSource(record.source);
        missionRequirementsPresent(record, missionRequirementsPanelHtml(missionRequirementsResolve(record.candidate, parsed), parsed.unresolved), parsed.unresolved.length ? 'partially unresolved requirement text' : '');
    }'''
