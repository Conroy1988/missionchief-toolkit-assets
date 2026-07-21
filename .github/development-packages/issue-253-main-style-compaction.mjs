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
const closingBraceJoinTarget = 15;
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

function standaloneCommentIndexes(lines) {
  const indexes = new Set();
  const blocks = [];
  for (let index = 1; index < lines.length - 1;) {
    const stripped = lines[index].trim();
    if (!stripped.startsWith('/*')) {
      index += 1;
      continue;
    }
    const start = index;
    let end = index;
    let valid = !lines[index].includes('${');
    const firstRemainder = stripped.slice(2);
    if (firstRemainder.includes('*/')) {
      valid = valid && !firstRemainder.split('*/', 2)[1].trim();
    } else {
      let found = false;
      for (let cursor = index + 1; cursor < lines.length - 1; cursor += 1) {
        end = cursor;
        if (lines[cursor].includes('${')) valid = false;
        if (lines[cursor].includes('*/')) {
          valid = valid && !lines[cursor].split('*/', 2)[1].trim();
          found = true;
          break;
        }
      }
      if (!found) valid = false;
    }
    if (valid) {
      for (let cursor = start; cursor <= end; cursor += 1) indexes.add(cursor);
      blocks.push({ startLine: start + 1, endLine: end + 1, lines: end - start + 1 });
    }
    index = end + 1;
  }
  return { indexes, blocks };
}

function removeStandaloneFormatting(lines) {
  const blankIndexes = new Set();
  for (let index = 1; index < lines.length - 1; index += 1) {
    if (!lines[index].trim()) blankIndexes.add(index);
  }
  const comments = standaloneCommentIndexes(lines);
  const removableIndexes = new Set([...blankIndexes, ...comments.indexes]);
  return {
    lines: lines.filter((_line, index) => !removableIndexes.has(index)),
    blankIndexes,
    comments,
    removableIndexes
  };
}

function canonicalCssFormatting(raw) {
  const stripped = removeStandaloneFormatting(raw.split('\n')).lines.join('\n');
  return stripped.replace(/\n[\t ]*}/gu, '}');
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
const formatting = removeStandaloneFormatting(rawLines);
const formattingOnlyLines = formatting.removableIndexes.size;
const compactedLines = [];
let joinedClosingBraceLines = 0;
for (const line of formatting.lines) {
  if (joinedClosingBraceLines < closingBraceJoinTarget && line.trim() === '}' && compactedLines.length) {
    compactedLines[compactedLines.length - 1] += '}';
    joinedClosingBraceLines += 1;
  } else {
    compactedLines.push(line);
  }
}
if (joinedClosingBraceLines !== closingBraceJoinTarget) {
  throw new Error(`only ${joinedClosingBraceLines} safe full-line closing braces were available; expected ${closingBraceJoinTarget}`);
}
const removedFormattingLines = formattingOnlyLines + joinedClosingBraceLines;
if (removedFormattingLines < 500) {
  throw new Error(`only ${removedFormattingLines} formatting lines are safely removable (${formatting.blankIndexes.size} blank, ${formatting.comments.indexes.size} comment, ${joinedClosingBraceLines} brace join); Issue #253 requires at least 500`);
}
const afterRaw = compactedLines.join('\n');
const beforeCanonical = canonicalCssFormatting(raw);
const afterCanonical = canonicalCssFormatting(afterRaw);
if (beforeCanonical !== afterCanonical) throw new Error('canonical CSS content changed during formatting-only compaction');
const canonicalCssSha256 = crypto.createHash('sha256').update(beforeCanonical, 'utf8').digest('hex');
const candidateTemplateSha256 = crypto.createHash('sha256').update(afterRaw, 'utf8').digest('hex');

let compacted = original.slice(0, target.start + 1) + afterRaw + original.slice(target.end - 1);
if ((compacted.match(/4\.20\.20/gu) || []).length !== 2) throw new Error('expected exactly two 4.20.20 source version markers');
compacted = compacted.replaceAll(oldVersion, newVersion);
parse(compacted, { ecmaVersion: 'latest', sourceType: 'script' });
const after = analyseSource(compacted, 'src/MissionChief_Map_Command_Toolkit.user.js');
if (before.source.lines - after.source.lines !== removedFormattingLines) {
  throw new Error(`source line delta ${before.source.lines - after.source.lines} does not match removed formatting lines ${removedFormattingLines}`);
}
if (after.source.lines > before.source.lines - 500) throw new Error('candidate does not recover the required 500 source lines');
if (after.summary.mutationObserverConstructions !== before.summary.mutationObserverConstructions ||
    after.summary.resizeObserverConstructions !== before.summary.resizeObserverConstructions ||
    after.summary.schedulerCalls !== before.summary.schedulerCalls) {
  throw new Error('observer or scheduler structure changed during formatting-only compaction');
}

fs.writeFileSync(sourcePath, compacted, 'utf8');
for (const distPath of distPaths) fs.writeFileSync(distPath, compacted, 'utf8');
const fixture = {
  schemaVersion: 3,
  subsystem: 'installMainStyles',
  originalVersion: oldVersion,
  candidateVersion: newVersion,
  originalSourceLines: before.source.lines,
  candidateSourceLines: after.source.lines,
  recoveredSourceLines: removedFormattingLines,
  removedBlankLines: formatting.blankIndexes.size,
  removedStandaloneCommentLines: formatting.comments.indexes.size,
  removedStandaloneCommentBlocks: formatting.comments.blocks.length,
  joinedClosingBraceLines,
  originalTemplateLines: rawLines.length,
  candidateTemplateLines: compactedLines.length,
  canonicalCssSha256,
  candidateTemplateSha256,
  originalSourceSha256: before.source.sha256,
  candidateSourceSha256: after.source.sha256,
  invariant: 'Canonical CSS content is identical; only blank lines, standalone full-line CSS comments and fifteen newlines immediately before full-line closing braces were removed.'
};
fs.mkdirSync(path.dirname(fixturePath), { recursive: true });
fs.writeFileSync(fixturePath, `${JSON.stringify(fixture, null, 2)}\n`, 'utf8');

const report = {
  schemaVersion: 5,
  issue: 253,
  selectedSubsystem: 'installMainStyles standalone source formatting',
  before: before.source,
  after: after.source,
  recoveredSourceLines: removedFormattingLines,
  resultingHeadroom: 32000 - after.source.lines,
  template: {
    originalLines: rawLines.length,
    candidateLines: compactedLines.length,
    removedBlankLines: formatting.blankIndexes.size,
    removedStandaloneCommentLines: formatting.comments.indexes.size,
    removedStandaloneCommentBlocks: formatting.comments.blocks.length,
    joinedClosingBraceLines,
    canonicalCssSha256,
    candidateTemplateSha256
  },
  structuralParity: {
    mutationObserverConstructions: [before.summary.mutationObserverConstructions, after.summary.mutationObserverConstructions],
    resizeObserverConstructions: [before.summary.resizeObserverConstructions, after.summary.resizeObserverConstructions],
    schedulerCalls: [before.summary.schedulerCalls, after.summary.schedulerCalls],
    cssContent: 'canonical CSS formatting hash unchanged'
  },
  excluded: ['inline comment removal', 'selector grouping', 'declaration consolidation', 'cascade reordering', 'style delivery changes', 'observer changes', 'scheduler changes', 'network changes'],
  rollbackBoundary: 'Revert the single source-headroom implementation commit; no persistent state or migration is introduced.'
};
fs.writeFileSync(reportJsonPath, `${JSON.stringify(report, null, 2)}\n`, 'utf8');
const md = `# Issue #253 — safe source headroom\n\n## Measured baseline\n\n- Toolkit version: \`${oldVersion}\`\n- Source: **${before.source.lines.toLocaleString('en-GB')} lines** / 32,000\n- Remaining headroom: **${(32000 - before.source.lines).toLocaleString('en-GB')} lines**\n- Source SHA-256: \`${before.source.sha256}\`\n- Main stylesheet template: **${rawLines.length.toLocaleString('en-GB')} physical lines**\n\n## Selected bounded subsystem\n\nOnly standalone source formatting inside the existing \`installMainStyles\` template is removed: **${formatting.blankIndexes.size.toLocaleString('en-GB')} blank lines**, **${formatting.comments.indexes.size.toLocaleString('en-GB')} lines across ${formatting.comments.blocks.length.toLocaleString('en-GB')} full-line CSS comment blocks**, and **${joinedClosingBraceLines} newlines immediately before full-line closing braces**. The canonical CSS content is identical before and after.\n\nThe implementation deliberately excludes inline comment removal, selector grouping, declaration consolidation, stylesheet splitting, deferred delivery, observer scope, scheduler timing, state ownership and network sequencing.\n\n## Result\n\n- Candidate version: \`${newVersion}\`\n- Recovered source lines: **${removedFormattingLines.toLocaleString('en-GB')}**\n- Candidate source lines: **${after.source.lines.toLocaleString('en-GB')}**\n- Resulting headroom: **${(32000 - after.source.lines).toLocaleString('en-GB')} lines**\n- Canonical CSS hash: \`${canonicalCssSha256}\`\n- Candidate template hash: \`${candidateTemplateSha256}\`\n- MutationObserver constructions: **${before.summary.mutationObserverConstructions} → ${after.summary.mutationObserverConstructions}**\n- ResizeObserver constructions: **${before.summary.resizeObserverConstructions} → ${after.summary.resizeObserverConstructions}**\n- Scheduler calls: **${before.summary.schedulerCalls} → ${after.summary.schedulerCalls}**\n\n## Permanent contract\n\nThe committed fixture records the exact formatting categories removed, canonical CSS hash and exact candidate template hash. Validation fails if the reviewed template changes, removable formatting returns without review, line arithmetic drifts or the recovery falls below 500 lines.\n\n## Rollback boundary\n\nRevert the single implementation commit. No storage migration, retained DOM reference, lifecycle change or external dependency is introduced.\n`;
fs.writeFileSync(reportMdPath, md, 'utf8');
console.log(`Recovered ${removedFormattingLines} source lines (${formatting.blankIndexes.size} blank, ${formatting.comments.indexes.size} standalone comment, ${joinedClosingBraceLines} brace joins); ${after.source.lines} remain; headroom is ${32000 - after.source.lines}.`);
