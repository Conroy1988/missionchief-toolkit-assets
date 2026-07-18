#!/usr/bin/env python3
from __future__ import annotations

from pathlib import Path
import hashlib
import json
import subprocess

ROOT = Path(__file__).resolve().parents[2]
SRC = ROOT / "src" / "MissionChief_Map_Command_Toolkit.user.js"
RUNTIME_TEST = ROOT / ".github" / "scripts" / "test_mission_requirements_runtime.js"
CONTRACT = ROOT / ".github" / "scripts" / "test_mission_requirements_contract.py"
CATALOGUE_FIXTURE = ROOT / ".github" / "fixtures" / "mission-catalogue-pages.json"
DIAGNOSTIC = ROOT / "docs" / "diagnostics" / "issue-163-source-extract.txt"


def replace_once(text: str, old: str, new: str, label: str) -> str:
    count = text.count(old)
    if count != 1:
        raise AssertionError(f"{label}: expected one match, found {count}")
    return text.replace(old, new, 1)


def insert_before(text: str, marker: str, addition: str, label: str) -> str:
    if addition.strip() in text:
        return text
    return replace_once(text, marker, addition + marker, label)


def replace_function(text: str, name: str, replacement: str) -> str:
    marker = f"    function {name}("
    start = text.find(marker)
    if start < 0:
        raise AssertionError(f"function {name} missing")
    next_function = text.find("\n    function ", start + len(marker))
    if next_function < 0:
        raise AssertionError(f"next function after {name} missing")
    return text[:start] + replacement.rstrip() + "\n" + text[next_function + 1:]


def run(*cmd: str) -> None:
    subprocess.run(cmd, cwd=ROOT, check=True)


catalogue_runtime = r'''
    const MISSION_REQUIREMENTS_CATALOGUE_TTL_MS = 6 * 60 * 60 * 1000;
    const MISSION_REQUIREMENTS_CATALOGUE_STALE_MS = 7 * 24 * 60 * 60 * 1000;
    const MISSION_REQUIREMENTS_CATALOGUE_RETRY_MS = 60 * 1000;
    const MISSION_REQUIREMENTS_CATALOGUE_CACHE_LIMIT = 96;
    const missionRequirementsCatalogueCache = new Map();

    function missionRequirementsCatalogueText(node) {
        return String(node?.textContent || node?.innerText || '').replace(/\s+/gu, ' ').trim();
    }

    function missionRequirementsCatalogueDescriptor(candidate) {
        const scopes = [candidate?.root, candidate?.mount].filter(Boolean);
        let matched = null;
        for (const scope of scopes) {
            const links = Array.from(scope.querySelectorAll?.('a[href*="/einsaetze/"]') || []);
            for (const link of links) {
                const href = String(link.getAttribute?.('href') || link.href || '');
                const match = href.match(/\/einsaetze\/(\d+)(?:\?[^#]*\boverlay_index=(\d+))?/iu);
                if (!match) continue;
                matched = { id: Number(match[1]), overlayIndex: match[2] === undefined ? null : Number(match[2]) };
                break;
            }
            if (matched) break;
        }
        if (!matched) {
            const id = missionRequirementsMissionTypeId(candidate);
            if (id === null || id === undefined || !Number.isFinite(Number(id)) || Number(id) < 0) return null;
            matched = { id: Number(id), overlayIndex: null };
        }
        const doc = candidate?.root?.ownerDocument || candidate?.mount?.ownerDocument;
        const location = doc?.defaultView?.location || pageWindow.location || {};
        const origin = location.origin || `${location.protocol || 'https:'}//${location.host || 'www.missionchief.co.uk'}`;
        const path = `/einsaetze/${matched.id}${matched.overlayIndex === null ? '' : `?overlay_index=${matched.overlayIndex}`}`;
        return { ...matched, origin, path, url: `${origin}${path}`, key: `${origin}${path}` };
    }

    function missionRequirementsCatalogueRequirement(label, value) {
        const rawLabel = missionRequirementsCatalogueText({ textContent: label });
        const rawValue = missionRequirementsCatalogueText({ textContent: value });
        const quantity = missionRequirementsOptionalNumber(rawValue);
        if (quantity === null) return null;
        const cleanedLabel = rawLabel
            .replace(/^(?:required|requirement\s+of|needed)\s+/iu, '')
            .replace(/\s*\([^)]*%[^)]*\)\s*$/u, '')
            .trim();
        if (!cleanedLabel) return null;
        const probabilityMatch = `${rawLabel} ${rawValue}`.match(/(\d+(?:\.\d+)?)\s*%/u);
        const probability = probabilityMatch ? Math.max(0, Math.min(100, Number(probabilityMatch[1]))) : 100;
        const sourceText = `${quantity} ${cleanedLabel}`;
        for (const group of ['vehicles', 'staff', 'other']) {
            const parsed = missionRequirementsParseText(sourceText, group);
            if (!parsed.requirements.length) continue;
            const requirement = parsed.requirements[0];
            return {
                ...requirement,
                missing: quantity,
                baseline: quantity,
                baselineText: `${quantity.toLocaleString('en-GB')}${probability < 100 ? ` (${probability}% chance)` : ''}`,
                probability,
                catalogueLabel: rawLabel,
                catalogueValue: rawValue,
                catalogueKnown: true
            };
        }
        const inferredGroup = missionRequirementsInferGroup(cleanedLabel, 'vehicles');
        const key = `catalogue-${cleanedLabel.toLowerCase().replace(/[^a-z0-9]+/gu, '-').replace(/^-|-$/gu, '').slice(0, 70) || 'unknown'}`;
        return {
            key,
            requirement: cleanedLabel,
            missing: quantity,
            baseline: quantity,
            baselineText: `${quantity.toLocaleString('en-GB')}${probability < 100 ? ` (${probability}% chance)` : ''}`,
            probability,
            group: inferredGroup,
            definition: { key, label: cleanedLabel, aliases: [cleanedLabel], group: inferredGroup, types: [], equipment: [], factors: {}, countable: false },
            catalogueLabel: rawLabel,
            catalogueValue: rawValue,
            catalogueKnown: false
        };
    }

    function missionRequirementsCatalogueParseDocument(doc, descriptor = {}) {
        if (!doc?.querySelectorAll) throw new Error('catalogue document unavailable');
        const requirements = [];
        const unresolved = [];
        const preconditions = {};
        const other = {};
        const tables = Array.from(doc.querySelectorAll('table') || []);
        for (const table of tables) {
            const tableText = missionRequirementsCatalogueText(table);
            let kind = /Vehicle\s+and\s+Personnel\s+Requirements/iu.test(tableText) ? 'requirements'
                : /Reward\s+and\s+Precondition/iu.test(tableText) ? 'preconditions'
                    : /Other\s+information/iu.test(tableText) ? 'other' : null;
            const rows = Array.from(table.querySelectorAll?.('tr') || []);
            for (const row of rows) {
                const cells = Array.from(row.querySelectorAll?.('th, td') || []);
                if (cells.length < 2) continue;
                const label = missionRequirementsCatalogueText(cells[0]);
                const value = missionRequirementsCatalogueText(cells[1]);
                if (!label || /^(?:Value|Vehicle\s+and\s+Personnel\s+Requirements|Reward\s+and\s+Precondition|Other\s+information)$/iu.test(label)) continue;
                if (!kind && /^(?:Required|Requirement\s+of|Needed)\b/iu.test(label)) kind = 'requirements';
                if (kind === 'requirements') {
                    const parsed = missionRequirementsCatalogueRequirement(label, value);
                    if (parsed) requirements.push(parsed);
                    else unresolved.push({ label, value });
                } else if (kind === 'preconditions') {
                    preconditions[label] = value;
                } else if (kind === 'other') {
                    other[label] = value;
                }
            }
        }
        const titleNode = doc.querySelector?.('h1, [data-mission-title], .mission-title');
        const title = missionRequirementsSafeDiagnostic(missionRequirementsCatalogueText(titleNode), 140) || `Mission ${descriptor.id ?? 'Unknown'}`;
        const variationLinks = Array.from(doc.querySelectorAll('a[href*="/einsaetze/"]') || []);
        const seenVariations = new Set();
        const variations = [];
        for (const link of variationLinks) {
            const href = String(link.getAttribute?.('href') || link.href || '');
            if (!/\/einsaetze\/\d+/u.test(href) || seenVariations.has(href)) continue;
            seenVariations.add(href);
            variations.push({ href: missionRequirementsSafeDiagnostic(href, 180), title: missionRequirementsSafeDiagnostic(missionRequirementsCatalogueText(link), 140) });
        }
        const findValue = (source, pattern) => {
            const entry = Object.entries(source).find(([key]) => pattern.test(key));
            return entry ? entry[1] : '';
        };
        return {
            id: descriptor.id ?? null,
            overlayIndex: descriptor.overlayIndex ?? null,
            path: descriptor.path || '',
            url: descriptor.url || '',
            title,
            requirements,
            unresolved,
            preconditions,
            other,
            averageCredits: missionRequirementsOptionalNumber(findValue(preconditions, /Average\s+credits/iu)),
            maxPatients: missionRequirementsOptionalNumber(findValue(other, /Max\.?\s*Patients/iu)),
            patientTransportProbability: missionRequirementsOptionalNumber(findValue(other, /Probability.*transport/iu)),
            variations,
            fetchedAt: Date.now(),
            stale: false
        };
    }

    function missionRequirementsCataloguePrune() {
        if (missionRequirementsCatalogueCache.size <= MISSION_REQUIREMENTS_CATALOGUE_CACHE_LIMIT) return;
        const ordered = Array.from(missionRequirementsCatalogueCache.entries()).sort((a, b) => (a[1]?.touchedAt || 0) - (b[1]?.touchedAt || 0));
        while (ordered.length && missionRequirementsCatalogueCache.size > MISSION_REQUIREMENTS_CATALOGUE_CACHE_LIMIT) {
            missionRequirementsCatalogueCache.delete(ordered.shift()[0]);
        }
    }

    function missionRequirementsCatalogueCacheStore(key, value, now = Date.now()) {
        missionRequirementsCatalogueCache.set(key, {
            value,
            expiresAt: now + MISSION_REQUIREMENTS_CATALOGUE_TTL_MS,
            staleUntil: now + MISSION_REQUIREMENTS_CATALOGUE_STALE_MS,
            retryAt: 0,
            promise: null,
            touchedAt: now
        });
        missionRequirementsCataloguePrune();
        return value;
    }

    function missionRequirementsCatalogueCacheLookup(key, now = Date.now()) {
        const entry = missionRequirementsCatalogueCache.get(key);
        if (!entry?.value) return null;
        if (now > entry.staleUntil) {
            missionRequirementsCatalogueCache.delete(key);
            return null;
        }
        entry.touchedAt = now;
        return { value: entry.value, stale: now > entry.expiresAt };
    }

    function missionRequirementsCatalogueFailureFallback(key, now = Date.now()) {
        return missionRequirementsCatalogueCacheLookup(key, now);
    }

    function missionRequirementsCatalogueEnsure(record) {
        const descriptor = missionRequirementsCatalogueDescriptor(record?.candidate);
        record.catalogueDescriptor = descriptor;
        if (!descriptor) {
            record.catalogueState = 'unavailable';
            return null;
        }
        const now = Date.now();
        const cached = missionRequirementsCatalogueCacheLookup(descriptor.key, now);
        if (cached) {
            record.catalogue = { ...cached.value, stale: cached.stale };
            record.catalogueState = cached.stale ? 'stale' : 'ready';
            if (!cached.stale) return record.catalogue;
        }
        let entry = missionRequirementsCatalogueCache.get(descriptor.key) || { value: cached?.value || null, retryAt: 0, promise: null, touchedAt: now };
        if (entry.promise) {
            entry.promise.finally(() => missionRequirementsScheduleRecord(record));
            return record.catalogue || null;
        }
        if (entry.retryAt > now) return record.catalogue || null;
        const doc = record?.source?.ownerDocument || record?.candidate?.root?.ownerDocument || record?.candidate?.mount?.ownerDocument;
        const view = doc?.defaultView || pageWindow;
        const fetcher = typeof view?.fetch === 'function' ? view.fetch.bind(view) : typeof pageWindow.fetch === 'function' ? pageWindow.fetch.bind(pageWindow) : null;
        const DOMParserCtor = view?.DOMParser || pageWindow.DOMParser;
        if (!fetcher || typeof DOMParserCtor !== 'function') {
            record.catalogueState = record.catalogue ? 'stale' : 'unavailable';
            return record.catalogue || null;
        }
        record.catalogueState = record.catalogue ? 'stale' : 'loading';
        const promise = Promise.resolve(fetcher(descriptor.url, { credentials: 'same-origin', headers: { Accept: 'text/html' } }))
            .then(response => {
                if (!response || response.ok === false) throw new Error(`catalogue HTTP ${response?.status || 'failure'}`);
                return response.text();
            })
            .then(html => {
                const parsedDoc = new DOMParserCtor().parseFromString(String(html || ''), 'text/html');
                const catalogue = missionRequirementsCatalogueParseDocument(parsedDoc, descriptor);
                missionRequirementsCatalogueCacheStore(descriptor.key, catalogue);
                record.catalogue = catalogue;
                record.catalogueState = 'ready';
                return catalogue;
            })
            .catch(error => {
                const fallback = missionRequirementsCatalogueFailureFallback(descriptor.key);
                const current = missionRequirementsCatalogueCache.get(descriptor.key) || entry;
                current.retryAt = Date.now() + MISSION_REQUIREMENTS_CATALOGUE_RETRY_MS;
                current.promise = null;
                current.touchedAt = Date.now();
                missionRequirementsCatalogueCache.set(descriptor.key, current);
                record.catalogueError = missionRequirementsSafeDiagnostic(error?.message || 'catalogue request failed', 160);
                if (fallback) {
                    record.catalogue = { ...fallback.value, stale: true };
                    record.catalogueState = 'stale';
                    return record.catalogue;
                }
                record.catalogueState = 'error';
                return null;
            })
            .finally(() => missionRequirementsScheduleRecord(record));
        entry.promise = promise;
        entry.touchedAt = now;
        missionRequirementsCatalogueCache.set(descriptor.key, entry);
        return record.catalogue || null;
    }

    function missionRequirementsCatalogueCompare(parsed, catalogue) {
        if (!catalogue?.requirements?.length) return { state: 'unavailable', summary: 'No catalogue requirements available', issues: [] };
        const baseline = new Map(catalogue.requirements.map(item => [item.key, Number(item.baseline ?? item.missing) || 0]));
        const issues = [];
        for (const live of parsed?.requirements || []) {
            if (!baseline.has(live.key)) issues.push(`Live-only requirement: ${live.requirement}`);
            else if ((Number(live.missing) || 0) > baseline.get(live.key)) issues.push(`Live quantity exceeds catalogue: ${live.requirement}`);
        }
        if (parsed?.unresolved?.length) issues.push(`${parsed.unresolved.length} unresolved live fragment${parsed.unresolved.length === 1 ? '' : 's'}`);
        return { state: issues.length ? 'mismatch' : 'compatible', summary: issues.length ? issues.join('; ') : 'Live requirements are compatible with the catalogue baseline', issues };
    }

    function missionRequirementsCataloguePanelHtml(catalogue) {
        const rows = Array.from(catalogue?.requirements || []);
        const stale = catalogue?.stale === true;
        const rowHtml = rows.map(row => `<tr data-row-state="unresolved"><td>${escapeHtml(row.requirement)}</td><td data-label="Catalogue baseline">${escapeHtml(row.baselineText || String(row.baseline ?? row.missing ?? '?'))}</td></tr>`).join('');
        const unresolved = Array.from(catalogue?.unresolved || []);
        const unresolvedHtml = unresolved.length ? `<div class="mcms-req-unknown"><b>Unmapped catalogue entries</b>${unresolved.map(item => `<span>${escapeHtml(`${item.label}: ${item.value}`)}</span>`).join('')}</div>` : '';
        const note = stale
            ? 'Using a cached official catalogue baseline because the latest catalogue request failed. Current outstanding requirements are unavailable.'
            : 'Official MissionChief catalogue baseline only. Current outstanding requirements are unavailable, so do not treat these quantities as still needed.';
        const title = missionRequirementsSafeDiagnostic(catalogue?.title || '', 100);
        const summary = `${stale ? 'Cached ' : ''}official baseline${title ? ` · ${title}` : ''}`;
        const table = rows.length
            ? `<table aria-label="MissionChief catalogue baseline requirements"><colgroup><col class="mcms-req-name-col"><col class="mcms-req-number-col"></colgroup><thead><tr><th scope="col">Requirement</th><th scope="col">Catalogue baseline</th></tr></thead><tbody>${rowHtml}</tbody></table>`
            : '<div class="mcms-req-fallback"><span class="mcms-req-fallback-message">The official catalogue lists no fixed vehicle or personnel requirements for this mission.</span></div>';
        return {
            stateName: 'warning',
            html: `<div class="mcms-req-head"><div class="mcms-req-title"><i aria-hidden="true"></i><span>Mission Requirements</span></div><span class="mcms-req-summary">${escapeHtml(summary)}</span><button type="button" class="mcms-req-collapse" data-mcms-requirements-collapse aria-label="Collapse mission requirements" aria-expanded="true">⌃</button></div><div class="mcms-req-body">${table}<div class="mcms-req-unknown"><b>Baseline planning data</b><span>${escapeHtml(note)}</span></div>${unresolvedHtml}</div>`
        };
    }

    function missionRequirementsCatalogueDiagnosticLines(record, parsed) {
        const descriptor = record?.catalogueDescriptor || missionRequirementsCatalogueDescriptor(record?.candidate);
        const catalogue = record?.catalogue;
        const comparison = missionRequirementsCatalogueCompare(parsed, catalogue);
        const rows = Array.from(catalogue?.requirements || []).slice(0, 24).map(item => `  - ${item.requirement}: ${item.baselineText || item.baseline || item.missing}`);
        return [
            '### Official MissionChief catalogue',
            `- State: ${missionRequirementsSafeDiagnostic(record?.catalogueState || 'not requested', 40)}`,
            `- Definition ID: ${descriptor?.id ?? 'Unavailable'}`,
            `- Overlay index: ${descriptor?.overlayIndex ?? 'None'}`,
            `- Path: ${missionRequirementsSafeDiagnostic(descriptor?.path || '', 180) || 'Unavailable'}`,
            `- Catalogue title: ${missionRequirementsSafeDiagnostic(catalogue?.title || '', 140) || 'Unavailable'}`,
            `- Parsed catalogue rows: ${catalogue?.requirements?.length || 0}`,
            `- Unmapped catalogue rows: ${catalogue?.unresolved?.length || 0}`,
            `- Average credits: ${catalogue?.averageCredits ?? 'Unavailable'}`,
            `- Max patients: ${catalogue?.maxPatients ?? 'Unavailable'}`,
            `- Mission variations: ${catalogue?.variations?.length || 0}`,
            `- Live/catalogue comparison: ${missionRequirementsSafeDiagnostic(comparison.summary, 500)}`,
            ...(rows.length ? ['', 'Catalogue requirement summary:', ...rows] : []),
            ''
        ];
    }

'''

new_report = r'''    function missionRequirementsReportUrl(record, reason = 'unknown') {
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
        missionRequirementsCatalogueEnsure(record);
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
            ...missionRequirementsCatalogueDiagnosticLines(record, parsed),
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
            const params = new URLSearchParams({ template: 'mission-info-missing.yml', title: issueTitle, diagnostic: body });
            return `https://github.com/Conroy1988/missionchief-toolkit-assets/issues/new?${params.toString()}`;
        };
        let url = build();
        while (url.length > 7600 && body.length > 1800) {
            body = `${body.slice(0, Math.max(1500, body.length - 500))}\n\n_Report shortened to fit GitHub's issue URL limit._`;
            url = build();
        }
        return url;
    }'''

new_render = r'''    function missionRequirementsRenderRecord(record) {
        if (!record?.source?.isConnected || !record?.candidate?.mount?.isConnected || !record?.panel?.isConnected) {
            scheduleMissionRequirementsScan(0);
            return;
        }
        if (missionRequirementsLssmActive(record.candidate, record.source)) {
            missionRequirementsRemoveRecord(record.source);
            return;
        }
        missionRequirementsCatalogueEnsure(record);
        const presentCatalogue = reason => {
            if (!record.catalogue) return false;
            missionRequirementsRestoreSource(record.source);
            missionRequirementsPresent(record, missionRequirementsCataloguePanelHtml({ ...record.catalogue, stale: record.catalogueState === 'stale' }), reason);
            return true;
        };
        const age = Date.now() - (record.startedAt || Date.now());
        const anchor = record.source.getAttribute?.('data-mcms-requirements-anchor') === '1';
        if (anchor) {
            if (presentCatalogue('live requirement source absent; official catalogue baseline shown')) return;
            missionRequirementsRestoreSource(record.source);
            const loading = record.catalogueState === 'loading' || age < 1200;
            missionRequirementsPresent(record, missionRequirementsFallbackHtml(loading ? 'loading' : 'error'), loading ? '' : 'requirement source and catalogue unavailable');
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
            if (presentCatalogue(`parser exception; official catalogue baseline shown: ${err?.message || 'unknown'}`)) return;
            missionRequirementsRestoreSource(record.source);
            missionRequirementsPresent(record, missionRequirementsFallbackHtml(record.catalogueState === 'loading' ? 'loading' : 'error'), `parser exception: ${err?.message || 'unknown'}`);
            return;
        }
        if (!parsed.requirements.length) {
            if (presentCatalogue(parsed.unresolved.length ? 'live requirement text unparseable; official catalogue baseline shown' : 'no quantified live requirements; official catalogue baseline shown')) return;
            missionRequirementsRestoreSource(record.source);
            missionRequirementsPresent(record, missionRequirementsFallbackHtml(record.catalogueState === 'loading' ? 'loading' : 'error'), parsed.unresolved.length ? 'requirement text unparseable' : 'no quantified requirements detected');
            return;
        }
        missionRequirementsHideSource(record.source);
        missionRequirementsPresent(record, missionRequirementsPanelHtml(missionRequirementsResolve(record.candidate, parsed), parsed.unresolved), parsed.unresolved.length ? 'partially unresolved requirement text' : '');
    }'''

source = SRC.read_text(encoding="utf-8")
source = replace_once(source, "// @version      4.15.5", "// @version      4.16.0", "metadata version")
source = replace_once(source, "version: '4.15.5'", "version: '4.16.0'", "runtime version")
source = insert_before(source, "    function missionRequirementsResolve(candidate, parsed) {", catalogue_runtime, "catalogue runtime insertion")
source = replace_function(source, "missionRequirementsReportUrl", new_report)
source = replace_function(source, "missionRequirementsRenderRecord", new_render)
SRC.write_text(source, encoding="utf-8")

CATALOGUE_FIXTURE.parent.mkdir(parents=True, exist_ok=True)
CATALOGUE_FIXTURE.write_text(json.dumps({
    "capturedAt": "2026-07-18",
    "source": "https://www.missionchief.co.uk/einsaetze",
    "index": [
        {"title": "Bin fire", "href": "/einsaetze/0"},
        {"title": "Fire in Hospital - Major Incident", "href": "/einsaetze/34?overlay_index=0"}
    ],
    "pages": [
        {
            "name": "simple fire mission",
            "sourceUrl": "https://www.missionchief.co.uk/einsaetze/0",
            "id": 0,
            "title": "Bin fire",
            "sections": {
                "reward": [["Average credits", "110"], ["Required Fire Stations", "1"]],
                "requirements": [["Required Fire engines", "1"]],
                "other": [["Follow-Up Missions", "Phonebox on fire; Burning leaves; Burning bus shelter"]]
            },
            "variations": [],
            "expected": {"fire-engine": 1}
        },
        {
            "name": "personnel-heavy major incident",
            "sourceUrl": "https://www.missionchief.co.uk/einsaetze/34?overlay_index=0",
            "id": 34,
            "overlayIndex": 0,
            "title": "Fire in Hospital - Major Incident",
            "sections": {
                "reward": [["Average credits", "15500"], ["Required Fire Stations", "13"], ["Required Rescue Stations", "6"], ["Requirement of Police Stations", "5"]],
                "requirements": [["Required Fire engines", "10"], ["Required Police Cars", "3"], ["Required Fire Officers", "8"], ["Required ICCU or Ambulance Control Units", "1"], ["Required Rescue Support Vehicles", "2"], ["Required Water Carriers", "1"], ["Required Aerial Appliance Trucks", "2"], ["Required Breathing Apparatus Support Units", "1"], ["Required Operational Team Leaders", "1"], ["Required PRVs", "2"], ["Required SRVs", "2"], ["Required Welfare Vehicles", "1"], ["Required Ambulance Officers", "1"]],
                "other": [["Max. Patients", "25"], ["Probability that a patient has to be transported", "50"]]
            },
            "variations": [{"href": "/einsaetze/34?overlay_index=1", "title": "Fire in Hospital - Major Incident"}, {"href": "/einsaetze/34?overlay_index=2", "title": "Fire in Hospital - Major Incident"}],
            "expected": {"fire-engine": 10, "police-car": 3, "fire-officer": 8, "iccu-or-control": 1, "otl": 1, "ambulance-officer": 1}
        },
        {
            "name": "alternative and conditional requirements",
            "sourceUrl": "https://www.missionchief.co.uk/einsaetze/fixture-alternative",
            "id": 99991,
            "title": "Recorded alternative requirement fixture",
            "sections": {
                "reward": [["Average credits", "9000"]],
                "requirements": [["Required Fire Engines or RIVs", "3"], ["Required Police Cars", "2 (50%)"], ["Required Level 1 Public Order Officers", "8"], ["Required Level 2 Public Order Officers", "22"]],
                "other": [["Max. Patients", "4"]]
            },
            "variations": [{"href": "/einsaetze/99991?overlay_index=1", "title": "Recorded alternative requirement fixture"}],
            "expected": {"fire-engine-or-riv": 3, "police-car": 2, "public-order-level-1": 8, "public-order-level-2": 22},
            "conditional": {"police-car": 50}
        }
    ]
}, indent=2) + "\n", encoding="utf-8")

runtime = RUNTIME_TEST.read_text(encoding="utf-8")
runtime = replace_once(runtime, "const fixture = JSON.parse(fs.readFileSync(path.join(root, '.github', 'fixtures', 'mission-requirements-contract.json'), 'utf8'));", "const fixture = JSON.parse(fs.readFileSync(path.join(root, '.github', 'fixtures', 'mission-requirements-contract.json'), 'utf8'));\nconst catalogueFixture = JSON.parse(fs.readFileSync(path.join(root, '.github', 'fixtures', 'mission-catalogue-pages.json'), 'utf8'));", "catalogue fixture load")
runtime = replace_once(runtime, "version: '4.15.5'", "version: '4.16.0'", "runtime fixture version")
runtime = replace_once(runtime, "    fallbackHtml: missionRequirementsFallbackHtml,\n    reportUrl: missionRequirementsReportUrl,", "    fallbackHtml: missionRequirementsFallbackHtml,\n    catalogueDescriptor: missionRequirementsCatalogueDescriptor,\n    parseCatalogueDocument: missionRequirementsCatalogueParseDocument,\n    cataloguePanelHtml: missionRequirementsCataloguePanelHtml,\n    catalogueCompare: missionRequirementsCatalogueCompare,\n    catalogueCacheStore: missionRequirementsCatalogueCacheStore,\n    catalogueCacheLookup: missionRequirementsCatalogueCacheLookup,\n    catalogueFailureFallback: missionRequirementsCatalogueFailureFallback,\n    catalogueTtl: MISSION_REQUIREMENTS_CATALOGUE_TTL_MS,\n    catalogueStale: MISSION_REQUIREMENTS_CATALOGUE_STALE_MS,\n    reportUrl: missionRequirementsReportUrl,", "runtime API exposure")

catalogue_tests = r'''
function makeCatalogueDocument(page) {
    const sectionNames = {
        reward: 'Reward and Precondition',
        requirements: 'Vehicle and Personnel Requirements',
        other: 'Other information'
    };
    const tables = Object.entries(page.sections).map(([key, entries]) => {
        const rows = [[sectionNames[key], 'Value'], ...entries].map(values => ({
            querySelectorAll(selector) {
                if (selector !== 'th, td') return [];
                return values.map(text => ({ textContent: String(text), innerText: String(text) }));
            }
        }));
        return {
            textContent: [sectionNames[key], 'Value', ...entries.flat()].join(' '),
            innerText: [sectionNames[key], 'Value', ...entries.flat()].join(' '),
            querySelectorAll(selector) { return selector === 'tr' ? rows : []; }
        };
    });
    const links = (page.variations || []).map(item => ({
        textContent: item.title,
        innerText: item.title,
        getAttribute(name) { return name === 'href' ? item.href : null; }
    }));
    return {
        querySelector(selector) {
            return selector.includes('h1') ? { textContent: page.title, innerText: page.title } : null;
        },
        querySelectorAll(selector) {
            if (selector === 'table') return tables;
            if (selector === 'a[href*="/einsaetze/"]') return links;
            return [];
        }
    };
}

const parsedCatalogues = new Map();
for (const page of catalogueFixture.pages) {
    const descriptor = { id: page.id, overlayIndex: page.overlayIndex ?? null, path: `/einsaetze/${page.id}`, url: page.sourceUrl };
    const catalogue = api.parseCatalogueDocument(makeCatalogueDocument(page), descriptor);
    parsedCatalogues.set(page.name, catalogue);
    assert.strictEqual(catalogue.title, page.title, `${page.name}: title`);
    const quantities = Object.fromEntries(catalogue.requirements.map(item => [item.key, item.baseline]));
    for (const [key, value] of Object.entries(page.expected)) assert.strictEqual(quantities[key], value, `${page.name}: ${key}`);
    for (const [key, probability] of Object.entries(page.conditional || {})) {
        assert.strictEqual(catalogue.requirements.find(item => item.key === key)?.probability, probability, `${page.name}: conditional probability`);
    }
    assert.strictEqual(catalogue.variations.length, (page.variations || []).length, `${page.name}: variations`);
}

const simpleCatalogue = parsedCatalogues.get('simple fire mission');
assert.strictEqual(simpleCatalogue.averageCredits, 110, 'catalogue average credits');
assert(api.cataloguePanelHtml(simpleCatalogue).html.includes('Official MissionChief catalogue baseline only'), 'catalogue panel clearly marks baseline data');
assert(!api.cataloguePanelHtml(simpleCatalogue).html.includes('Still needed'), 'catalogue baseline must not claim current still-needed quantities');
const comparison = api.catalogueCompare({ requirements: [{ key: 'fire-engine', requirement: 'Fire Engine', missing: 2 }], unresolved: [] }, simpleCatalogue);
assert.strictEqual(comparison.state, 'mismatch', 'live quantity above baseline is reported as a mismatch');

const descriptorDoc = new FakeDocument();
descriptorDoc.defaultView = { location: { origin: 'https://www.missionchief.co.uk', protocol: 'https:', host: 'www.missionchief.co.uk' } };
const descriptorRoot = new FakeElement('div', descriptorDoc);
const descriptorLink = { getAttribute(name) { return name === 'href' ? '/einsaetze/34?overlay_index=2' : null; } };
descriptorRoot.queryAllMap.set('a[href*="/einsaetze/"]', [descriptorLink]);
const descriptor = api.catalogueDescriptor({ root: descriptorRoot, mount: descriptorRoot });
assert.deepStrictEqual(JSON.parse(JSON.stringify({ id: descriptor.id, overlayIndex: descriptor.overlayIndex, path: descriptor.path })), { id: 34, overlayIndex: 2, path: '/einsaetze/34?overlay_index=2' }, 'catalogue descriptor preserves mission variation');

api.catalogueCacheStore('fixture-cache', simpleCatalogue, 1000);
assert.strictEqual(api.catalogueCacheLookup('fixture-cache', 1001).stale, false, 'fresh catalogue cache');
assert.strictEqual(api.catalogueCacheLookup('fixture-cache', 1000 + api.catalogueTtl + 1).stale, true, 'expired catalogue remains bounded stale fallback');
assert.strictEqual(api.catalogueFailureFallback('fixture-cache', 1000 + api.catalogueTtl + 1).value.title, 'Bin fire', 'network failure reuses stale catalogue');
assert.strictEqual(api.catalogueCacheLookup('fixture-cache', 1000 + api.catalogueStale + 1), null, 'catalogue cache expires after stale boundary');

'''
runtime = replace_once(runtime, "const missingDoc = new FakeDocument();", catalogue_tests + "const missingDoc = new FakeDocument();", "catalogue runtime tests")
RUNTIME_TEST.write_text(runtime, encoding="utf-8")

contract = CONTRACT.read_text(encoding="utf-8")
contract = replace_once(contract, 'RUNTIME_TEST = ROOT / ".github/scripts/test_mission_requirements_runtime.js"', 'RUNTIME_TEST = ROOT / ".github/scripts/test_mission_requirements_runtime.js"\nCATALOGUE_FIXTURE = ROOT / ".github/fixtures/mission-catalogue-pages.json"', "contract fixture path")
contract = replace_once(contract, '        "function missionRequirementsReportUrl(record, reason = \'unknown\')",', '        "function missionRequirementsReportUrl(record, reason = \'unknown\')",\n        "function missionRequirementsCatalogueDescriptor(candidate)",\n        "function missionRequirementsCatalogueParseDocument(doc, descriptor = {})",\n        "function missionRequirementsCatalogueEnsure(record)",\n        "function missionRequirementsCataloguePanelHtml(catalogue)",\n        "function missionRequirementsCatalogueCompare(parsed, catalogue)",\n        "Official MissionChief catalogue baseline only",\n        "/einsaetze/",', "contract catalogue markers")
contract = replace_once(contract, '    source = SOURCE.read_text(encoding="utf-8")\n    data = json.loads(FIXTURE.read_text(encoding="utf-8"))', '    source = SOURCE.read_text(encoding="utf-8")\n    data = json.loads(FIXTURE.read_text(encoding="utf-8"))\n    catalogue_fixture = json.loads(CATALOGUE_FIXTURE.read_text(encoding="utf-8"))\n    assert len(catalogue_fixture["pages"]) >= 3\n    assert any(page.get("variations") for page in catalogue_fixture["pages"])\n    assert any(page.get("conditional") for page in catalogue_fixture["pages"])', "contract catalogue assertions")
CONTRACT.write_text(contract, encoding="utf-8")

changelog_path = ROOT / "CHANGELOG.md"
changelog = changelog_path.read_text(encoding="utf-8")
entry = '''## [4.16.0] - 2026-07-18

### Added
- Added an on-demand resolver for MissionChief's official Possible Missions catalogue and per-mission `Vehicle and Personnel Requirements` tables.
- Added variation-aware six-hour caching with a bounded stale fallback for temporary catalogue failures.
- Added an explicitly labelled official catalogue baseline when live MissionChief requirement data is absent or unparseable.
- Added catalogue title, definition, patient, variation and live-versus-catalogue diagnostics to **Report Mission**.

### Safety
- Live MissionChief `#missing_text`, en-route units and selected units remain authoritative whenever live data is available.
- Catalogue quantities are never presented as current **Still needed** values.

'''
if "## [4.16.0]" not in changelog:
    marker = "## [4.15.5]"
    if marker not in changelog:
        raise AssertionError("4.15.5 changelog marker missing")
    changelog = changelog.replace(marker, entry + marker, 1)
changelog_path.write_text(changelog, encoding="utf-8")

doc_path = ROOT / "docs" / "issue-163-mission-catalogue-resolver-contract.md"
doc_path.write_text('''# Issue #163 — MissionChief catalogue-backed requirements resolver

## Authority model

1. The active MissionChief mission window remains authoritative for current outstanding requirements.
2. Native selected checkboxes and the native en-route table remain authoritative for selected and travelling units.
3. `/einsaetze/<definition>` is an official static baseline and diagnostic cross-reference only.
4. Catalogue baseline values must never be labelled or calculated as current **Still needed** quantities.

## Retrieval

- Resolve the mission definition from a native `/einsaetze/` help link first, preserving `overlay_index` variations.
- Fall back to MissionChief's native mission type ID.
- Fetch only the active definition, using same-origin credentials.
- Cache a fresh definition for six hours, retain a bounded stale fallback for seven days, and cap the session cache at 96 entries.
- Never bulk-fetch the full mission catalogue during normal startup.

## Failure behaviour

- Live data available: render the live matrix immediately; catalogue retrieval is non-blocking.
- Live source absent or unparseable and catalogue available: render a clearly labelled official baseline table.
- Live source empty: preserve MissionChief's authoritative no-outstanding-requirements state.
- Network failure: use a bounded stale catalogue entry where available; otherwise keep the existing reportable failure state.
- When live data later appears, replace the baseline automatically with the live matrix.

## Diagnostics

Report Mission includes catalogue state, definition ID, variation, official title, parsed and unmapped rows, credits, patients, variation count, requirement summary, and live-versus-baseline mismatches.

## Validation

Recorded fixtures cover a simple mission, a personnel-heavy major incident, alternative vehicles, conditional requirements, public-order personnel, mission variations, cache expiry, stale fallback and live/catalogue mismatch detection.
''', encoding="utf-8")

if DIAGNOSTIC.exists():
    DIAGNOSTIC.unlink()
try:
    DIAGNOSTIC.parent.rmdir()
except OSError:
    pass

help_manifest_path = ROOT / "help" / "manifest.json"
help_manifest = json.loads(help_manifest_path.read_text(encoding="utf-8"))
help_manifest["guideVersion"] = "4.16.0"
help_manifest["toolkitVersion"] = "4.16.0"
help_manifest["updated"] = "2026-07-18"
help_manifest["runtimeGuidePatch"] = "Toolkit v4.16.0 adds an official MissionChief catalogue baseline without overriding live mission state."
help_manifest_path.write_text(json.dumps(help_manifest, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")

help_index = ROOT / "help" / "index.html"
help_text = help_index.read_text(encoding="utf-8")
help_index.write_text(help_text.replace("4.15.5", "4.16.0"), encoding="utf-8")

canonical = SRC.read_bytes()
dist_user = ROOT / "dist" / "MissionChief_Map_Command_Toolkit.user.js"
dist_txt = ROOT / "dist" / "MissionChief_Map_Command_Toolkit.txt"
dist_user.write_bytes(canonical)
dist_txt.write_bytes(canonical)
digest = hashlib.sha256(canonical).hexdigest()
(ROOT / "dist" / "SHA256SUMS.txt").write_text(f"{digest}  MissionChief_Map_Command_Toolkit.user.js\n{digest}  MissionChief_Map_Command_Toolkit.txt\n", encoding="utf-8")
manifest_path = ROOT / "dist" / "release-manifest.json"
manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
manifest["version"] = "4.16.0"
manifest["sha256"] = digest
manifest["bytes"] = len(canonical)
manifest["lines"] = canonical.count(b"\n")
manifest.setdefault("metadata", {})["runtimeVersion"] = "4.16.0"
manifest["distributionStatus"] = "dry-run-not-yet-greasyfork-source"
manifest_path.write_text(json.dumps(manifest, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")

run("node", "--check", str(SRC.relative_to(ROOT)))
run("node", str(RUNTIME_TEST.relative_to(ROOT)))
run("python3", str(CONTRACT.relative_to(ROOT)))
print(f"Issue #163 candidate ready: sha256={digest}")
