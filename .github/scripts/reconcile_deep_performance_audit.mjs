#!/usr/bin/env node
import fs from 'node:fs';
import process from 'node:process';
import { renderMarkdown } from './deep_performance_audit.mjs';

export function reconcileReport(data) {
  const resolved = Number(data.summary?.broadSubtreeObservers || 0);
  const unresolved = (data.unresolvedObserveCalls || []).filter(item => /\bsubtree\s*:\s*true\b/u.test(String(item.options || ''))).length;
  const total = resolved + unresolved;

  data.schemaVersion = 4;
  data.summary.resolvedBroadSubtreeObservers = resolved;
  data.summary.unresolvedBroadSubtreeObservers = unresolved;
  data.summary.broadSubtreeObservers = total;

  data.baselineCrossCheck.measuredBroadSubtreeObservers = total;
  data.baselineCrossCheck.resolvedBroadSubtreeObservers = resolved;
  data.baselineCrossCheck.unresolvedBroadSubtreeObservers = unresolved;
  // Retained for the schema-3 renderer used by the underlying analyser.
  data.baselineCrossCheck.measuredResolvedBroadSubtreeObservers = total;

  const scope = (data.findings || []).find(item => item.category === 'observer-scope');
  if (scope) {
    scope.message = `${total} observer registrations use subtree:true (${resolved} locally resolved and ${unresolved} cross-function); ownership and callback evidence are required before narrowing or merging them.`;
  }
  return data;
}

export function renderReconciledMarkdown(data) {
  const markdown = renderMarkdown(data);
  const oldLine = `- Resolved broad subtree registrations: \`${data.summary.broadSubtreeObservers}\``;
  const replacement = [
    `- Broad subtree registrations: \`${data.summary.broadSubtreeObservers}\``,
    `- Locally resolved broad registrations: \`${data.summary.resolvedBroadSubtreeObservers}\``,
    `- Cross-function broad registrations: \`${data.summary.unresolvedBroadSubtreeObservers}\``
  ].join('\n');
  return markdown.replace(oldLine, replacement);
}

function main() {
  const [jsonPath, markdownPath] = process.argv.slice(2);
  if (!jsonPath || !markdownPath) {
    console.error('Usage: reconcile_deep_performance_audit.mjs REPORT.json REPORT.md');
    process.exit(2);
  }
  const data = reconcileReport(JSON.parse(fs.readFileSync(jsonPath, 'utf8')));
  fs.writeFileSync(jsonPath, `${JSON.stringify(data, null, 2)}\n`, 'utf8');
  fs.writeFileSync(markdownPath, renderReconciledMarkdown(data), 'utf8');
  console.log(JSON.stringify({
    resolvedBroadSubtreeObservers: data.summary.resolvedBroadSubtreeObservers,
    unresolvedBroadSubtreeObservers: data.summary.unresolvedBroadSubtreeObservers,
    broadSubtreeObservers: data.summary.broadSubtreeObservers
  }, null, 2));
}

if (process.argv[1] && new URL(import.meta.url).pathname === process.argv[1]) main();
