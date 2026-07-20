#!/usr/bin/env node
import assert from 'node:assert/strict';
import { reconcileReport, renderReconciledMarkdown } from './reconcile_deep_performance_audit.mjs';

const report = {
  schemaVersion: 3,
  summary: { broadSubtreeObservers: 8 },
  baselineCrossCheck: {
    expectedMutationObserverConstructions: 12,
    measuredMutationObserverConstructions: 12,
    expectedResizeObserverConstructions: 4,
    measuredResizeObserverConstructions: 4,
    expectedBroadSubtreeObservers: 10,
    measuredResolvedBroadSubtreeObservers: 8,
    unresolvedObserveCalls: 3
  },
  unresolvedObserveCalls: [
    { options: '{ childList: true, subtree: true }' },
    { options: '{ childList: true, subtree: true }' },
    { options: '{ childList: true, subtree: false }' }
  ],
  findings: [{ category: 'observer-scope', message: 'old' }],
  parser: 'acorn',
  source: { version: '4.20.17', sha256: 'fixture', bytes: 1, lines: 1 },
  topFunctionsByScore: [],
  topDomWriters: [],
  topSchedulerFunctions: [],
  observerRegistrations: [],
  observerConstructions: [],
  largeTemplates: [],
  repeatedSelectors: []
};

const data = reconcileReport(report);
assert.equal(data.schemaVersion, 4);
assert.equal(data.summary.resolvedBroadSubtreeObservers, 8);
assert.equal(data.summary.unresolvedBroadSubtreeObservers, 2);
assert.equal(data.summary.broadSubtreeObservers, 10);
assert.equal(data.baselineCrossCheck.measuredBroadSubtreeObservers, 10);
assert.match(data.findings[0].message, /8 locally resolved and 2 cross-function/);

const markdown = renderReconciledMarkdown(data);
assert.match(markdown, /Broad subtree registrations: `10`/);
assert.match(markdown, /Locally resolved broad registrations: `8`/);
assert.match(markdown, /Cross-function broad registrations: `2`/);

console.log('Deep performance audit reconciliation fixtures passed');
