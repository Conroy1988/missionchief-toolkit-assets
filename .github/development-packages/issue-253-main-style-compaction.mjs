#!/usr/bin/env node
import crypto from 'node:crypto';
import fs from 'node:fs';
import path from 'node:path';
import process from 'node:process';
import { parse } from 'acorn';
import { analyseSource } from '../scripts/deep_performance_audit.mjs';

const root = process.cwd();
const sourcePath = path.join(root, 'src/MissionChief_Map_Command_Toolkit.user.js');
const distPaths = [
  path.join(root, 'dist/MissionChief_Map_Command_Toolkit.user.js'),
  path.join(root, 'dist/MissionChief_Map_Command_Toolkit.txt')
];
const fixturePath = path.join(root, '.github/fixtures/main-style-source-headroom.json');
const reportJsonPath = path.join(root, 'docs/issue-253-source-headroom-inventory.json');
const reportMdPath = path.join(root, 'docs/issue-253-source-headroom-inventory.md');
const oldVersion = '4.20.20';
const newVersion = '4.20.21';
const original = fs.readFileSync(sourcePath, 'utf8');
const before = analyseSource(original, 'src/MissionChief_Map_Command_Toolkit.user.js');
const ast = parse(original, { ecmaVersion: 'latest', sourceType: 'script', locations: true, ranges: true });

function functionName(node, parent) {
  if (node.id?.name) return node.id.name;
  if (parent?.type === 'VariableDeclarator' && parent.id?.type === 'Identifier') return parent.id.name;
  if (parent?.type === 'Property' && parent.key?.type === 'Identifier') return parent.key.name;
  return `<anonymous@${node.loc.start.line}>`;
}

function walk(node, visitor, parent = null, owner = '<top-level>') {
  if (!node || typeof node !== 'object' || typeof node.type !== 'string') return;
  const nextOwner = ['FunctionDeclaration', 'FunctionExpression', 'ArrowFunctionExpression'].includes(node.type) ? functionName(node, parent) : owner;
  visitor(node, parent, nextOwner);
  for (const [key, value] of Object.entries(node)) {
    if (['start', 'end', 'loc', 'range'].includes(key)) continue;
    if (Array.isArray(value)) for (const child of value) walk(child, visitor, node, nextOwner);
    else if (value && typeof value === 'object' && typeof value.type === 'string') walk(value, visitor, node, nextOwner);
  }
}

const candidates = [];
walk(ast, (node, _parent, owner) => {
  if (node.type !== 'TemplateLiteral' || owner !== 'installMainStyles') return;
  candidates.push({ node, bytes: Buffer.byteLength(original.slice(node.start + 1, node.end - 1), 'utf8') });
});
if (!candidates.length) throw new Error('installMainStyles template literal was not found');
candidates.sort((a, b) => b.bytes - a.bytes);
const target = candidates[0].node;
if (candidates[0].bytes < 800000) throw new Error(`unexpected installMainStyles template size: ${candidates[0].bytes}`);

const raw = original.slice(target.start + 1, target.end - 1);
const rawLines = raw.split('\n');
const keptLines = rawLines.filter((line, index) => index === 0 || index === rawLines.length - 1 || line.trim());
const removedBlankLines = rawLines.length - keptLines.length;
if (removedBlankLines < 500) throw new Error(`only ${removedBlankLines} blank lines are safely removable; Issue #253 requires at least 500`);
const beforeNonEmpty = rawLines.filter(line => line.trim());
const afterRaw = keptLines.join('\n');
const afterNonEmpty = keptLines.filter(line => line.trim());
if (beforeNonEmpty.length !== afterNonEmpty.length || beforeNonEmpty.some((line, index) => line !== afterNonEmpty[index])) {
  throw new Error('non-empty main-style source lines changed during compaction');
}
const nonEmptyPayload = beforeNonEmpty.join('\n');
const nonEmptyLinesSha256 = crypto.createHash('sha256').update(nonEmptyPayload, 'utf8').digest('hex');

let compacted = original.slice(0, target.start + 1) + afterRaw + original.slice(target.end - 1);
if ((compacted.match(/4\.20\.20/gu) || []).length !== 2) throw new Error('expected exactly two 4.20.20 source version markers');
compacted = compacted.replaceAll(oldVersion, newVersion);
parse(compacted, { ecmaVersion: 'latest', sourceType: 'script' });
const after = analyseSource(compacted, 'src/MissionChief_Map_Command_Toolkit.user.js');
if (before.source.lines - after.source.lines !== removedBlankLines) {
  throw new Error(`source line delta ${before.source.lines - after.source.lines} does not match removed blank lines ${removedBlankLines}`);
}
if (after.source.lines > before.source.lines - 500) throw new Error('candidate does not recover the required 500 source lines');
if (after.summary.mutationObserverConstructions !== before.summary.mutationObserverConstructions ||
    after.summary.resizeObserverConstructions !== before.summary.resizeObserverConstructions ||
    after.summary.schedulerCalls !== before.summary.schedulerCalls) {
  throw new Error('observer or scheduler structure changed during whitespace-only compaction');
}

fs.writeFileSync(sourcePath, compacted, 'utf8');
for (const distPath of distPaths) fs.writeFileSync(distPath, compacted, 'utf8');
const fixture = {
  schemaVersion: 1,
  subsystem: 'installMainStyles',
  originalVersion: oldVersion,
  candidateVersion: newVersion,
  originalSourceLines: before.source.lines,
  candidateSourceLines: after.source.lines,
  recoveredSourceLines: removedBlankLines,
  originalTemplateLines: rawLines.length,
  candidateTemplateLines: keptLines.length,
  nonEmptyLineCount: beforeNonEmpty.length,
  nonEmptyLinesSha256,
  originalSourceSha256: before.source.sha256,
  candidateSourceSha256: after.source.sha256,
  invariant: 'All ordered non-empty template source lines are byte-for-byte identical; only blank physical lines were removed.'
};
fs.mkdirSync(path.dirname(fixturePath), { recursive: true });
fs.writeFileSync(fixturePath, `${JSON.stringify(fixture, null, 2)}\n`, 'utf8');

const report = {
  schemaVersion: 3,
  issue: 253,
  selectedSubsystem: 'installMainStyles blank physical lines',
  before: before.source,
  after: after.source,
  recoveredSourceLines: removedBlankLines,
  resultingHeadroom: 32000 - after.source.lines,
  template: {
    originalLines: rawLines.length,
    candidateLines: keptLines.length,
    nonEmptyLineCount: beforeNonEmpty.length,
    nonEmptyLinesSha256
  },
  structuralParity: {
    mutationObserverConstructions: [before.summary.mutationObserverConstructions, after.summary.mutationObserverConstructions],
    resizeObserverConstructions: [before.summary.resizeObserverConstructions, after.summary.resizeObserverConstructions],
    schedulerCalls: [before.summary.schedulerCalls, after.summary.schedulerCalls],
    selectorsDeclarationsAndInterpolations: 'ordered non-empty source lines unchanged'
  },
  excluded: ['selector grouping', 'declaration consolidation', 'cascade reordering', 'style delivery changes', 'observer changes', 'scheduler changes', 'network changes'],
  rollbackBoundary: 'Revert the single source-headroom implementation commit; no persistent state or migration is introduced.'
};
fs.writeFileSync(reportJsonPath, `${JSON.stringify(report, null, 2)}\n`, 'utf8');
const md = `# Issue #253 — safe source headroom\n\n## Measured baseline\n\n- Toolkit version: \`${oldVersion}\`\n- Source: **${before.source.lines.toLocaleString('en-GB')} lines** / 32,000\n- Remaining headroom: **${(32000 - before.source.lines).toLocaleString('en-GB')} lines**\n- Source SHA-256: \`${before.source.sha256}\`\n- Main stylesheet template: **${rawLines.length.toLocaleString('en-GB')} physical lines**, **${beforeNonEmpty.length.toLocaleString('en-GB')} non-empty lines**\n\n## Selected bounded subsystem\n\nOnly blank physical lines inside the existing \`installMainStyles\` template are removed. Every ordered non-empty line remains byte-for-byte identical. This preserves every selector, declaration, interpolation, rule order and cascade position.\n\nThe first implementation deliberately excludes selector grouping, declaration consolidation, stylesheet splitting, deferred delivery, observer scope, scheduler timing, state ownership and network sequencing.\n\n## Result\n\n- Candidate version: \`${newVersion}\`\n- Recovered source lines: **${removedBlankLines.toLocaleString('en-GB')}**\n- Candidate source lines: **${after.source.lines.toLocaleString('en-GB')}**\n- Resulting headroom: **${(32000 - after.source.lines).toLocaleString('en-GB')} lines**\n- Ordered non-empty stylesheet hash: \`${nonEmptyLinesSha256}\`\n- MutationObserver constructions: **${before.summary.mutationObserverConstructions} → ${after.summary.mutationObserverConstructions}**\n- ResizeObserver constructions: **${before.summary.resizeObserverConstructions} → ${after.summary.resizeObserverConstructions}**\n- Scheduler calls: **${before.summary.schedulerCalls} → ${after.summary.schedulerCalls}**\n\n## Permanent contract\n\nThe committed fixture records the original/candidate line counts, recovered line count and SHA-256 of the ordered non-empty stylesheet lines. Validation fails if blank lines return without review or if any non-empty line changes without updating the reviewed fixture.\n\n## Rollback boundary\n\nRevert the single implementation commit. No storage migration, retained DOM reference, lifecycle change or external dependency is introduced.\n`;
fs.writeFileSync(reportMdPath, md, 'utf8');
console.log(`Recovered ${removedBlankLines} source lines; ${after.source.lines} remain; headroom is ${32000 - after.source.lines}.`);
