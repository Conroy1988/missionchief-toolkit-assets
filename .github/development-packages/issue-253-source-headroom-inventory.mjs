#!/usr/bin/env node
import fs from 'node:fs';
import path from 'node:path';
import process from 'node:process';
import { parse } from 'acorn';
import { analyseSource } from '../scripts/deep_performance_audit.mjs';

const root = process.cwd();
const sourcePath = path.join(root, 'src/MissionChief_Map_Command_Toolkit.user.js');
const reportPath = path.join(root, 'docs/issue-253-source-headroom-inventory.md');
const jsonPath = path.join(root, 'docs/issue-253-source-headroom-inventory.json');
const source = fs.readFileSync(sourcePath, 'utf8');
const ast = parse(source, { ecmaVersion: 'latest', sourceType: 'script', locations: true, ranges: true });
const deep = analyseSource(source, 'src/MissionChief_Map_Command_Toolkit.user.js');

function expressionName(node) {
  if (!node) return '';
  if (node.type === 'Identifier') return node.name;
  if (node.type === 'MemberExpression') {
    const object = expressionName(node.object);
    const property = node.computed && node.property?.type === 'Literal' ? String(node.property.value) : node.property?.name || '';
    return object && property ? `${object}.${property}` : property || object;
  }
  return '';
}

function unwrap(node) {
  if (!node) return node;
  if (node.type === 'CallExpression' && ['Object.freeze', 'Object.seal'].includes(expressionName(node.callee)) && node.arguments.length === 1) return unwrap(node.arguments[0]);
  return node;
}

function jsonLike(node) {
  node = unwrap(node);
  if (!node) return false;
  if (node.type === 'Literal') return ['string', 'number', 'boolean'].includes(typeof node.value) || node.value === null;
  if (node.type === 'UnaryExpression' && ['-', '+'].includes(node.operator)) return jsonLike(node.argument);
  if (node.type === 'TemplateLiteral') return node.expressions.length === 0;
  if (node.type === 'ArrayExpression') return node.elements.every(element => element === null || jsonLike(element));
  if (node.type === 'ObjectExpression') return node.properties.every(property => property.type === 'Property' && property.kind === 'init' && !property.computed && jsonLike(property.value));
  return false;
}

function countEntries(node) {
  node = unwrap(node);
  if (!node) return 0;
  if (node.type === 'ArrayExpression') return node.elements.length;
  if (node.type === 'ObjectExpression') return node.properties.length;
  return 1;
}

const staticLiterals = [];
for (const statement of ast.body) {
  if (statement.type !== 'VariableDeclaration') continue;
  for (const declaration of statement.declarations) {
    if (declaration.id?.type !== 'Identifier' || !declaration.init) continue;
    const candidate = unwrap(declaration.init);
    if (!['ObjectExpression', 'ArrayExpression', 'TemplateLiteral'].includes(candidate?.type)) continue;
    staticLiterals.push({
      name: declaration.id.name,
      kind: candidate.type,
      startLine: declaration.loc.start.line,
      endLine: declaration.loc.end.line,
      lines: declaration.loc.end.line - declaration.loc.start.line + 1,
      bytes: Buffer.byteLength(source.slice(declaration.start, declaration.end), 'utf8'),
      entries: countEntries(candidate),
      jsonLike: jsonLike(candidate)
    });
  }
}
staticLiterals.sort((a, b) => b.lines - a.lines || b.bytes - a.bytes || a.name.localeCompare(b.name));

const lines = source.split(/\r?\n/u);
const blankLines = lines.filter(line => !line.trim()).length;
const commentOnlyLines = lines.filter(line => /^\s*(?:\/\/|\/\*|\*|\*\/)/u.test(line)).length;
const whitespaceOnlySavings = blankLines;

function normalizedLine(line) {
  return line.trim().replace(/\s+/gu, ' ');
}

const repeatedBlocks = [];
for (const width of [8, 6, 4]) {
  const seen = new Map();
  for (let index = 0; index + width <= lines.length; index += 1) {
    const blockLines = lines.slice(index, index + width);
    if (blockLines.some(line => line.includes('`'))) continue;
    const normalized = blockLines.map(normalizedLine).join('\n');
    if (normalized.length < 180 || normalized.split('\n').filter(Boolean).length < width - 1) continue;
    const locations = seen.get(normalized) || [];
    locations.push(index + 1);
    seen.set(normalized, locations);
  }
  for (const [block, locations] of seen) {
    if (locations.length < 2) continue;
    repeatedBlocks.push({ width, occurrences: locations.length, recoverableLines: (locations.length - 1) * width, locations: locations.slice(0, 12), preview: block.split('\n').slice(0, 3).join(' / ') });
  }
}
repeatedBlocks.sort((a, b) => b.recoverableLines - a.recoverableLines || b.width - a.width || a.locations[0] - b.locations[0]);

const prefixGroups = new Map();
for (const item of deep.topFunctionsByLines) {
  const match = item.name.match(/^(missionRequirements|transportSweep|financial|alliance|vehicle|payout|coverage|critical|command|mission|runtime|apply|render|create|update|load|build|install)/u);
  const prefix = match?.[1] || 'other';
  const group = prefixGroups.get(prefix) || { prefix, functions: 0, lines: 0, bytes: 0, names: [] };
  group.functions += 1;
  group.lines += item.lines;
  group.bytes += item.bytes;
  group.names.push(`${item.name} (${item.lines})`);
  prefixGroups.set(prefix, group);
}
const groupedHotspots = [...prefixGroups.values()].sort((a, b) => b.lines - a.lines || a.prefix.localeCompare(b.prefix));

const externalizable = staticLiterals.filter(item => item.jsonLike && item.lines >= 20);
const lowRiskCandidates = externalizable.map(item => ({
  ...item,
  estimatedRecoveredLines: Math.max(0, item.lines - 3),
  method: 'Move reviewed JSON-like source data to src/data and embed a generated compact literal into the canonical userscript.'
}));

const report = {
  schemaVersion: 1,
  source: deep.source,
  currentHeadroom: 32000 - deep.source.lines,
  blankLines,
  commentOnlyLines,
  whitespaceOnlySavings,
  topFunctionsByLines: deep.topFunctionsByLines,
  largeTemplates: deep.largeTemplates,
  staticLiterals,
  externalizableJsonLikeLiterals: lowRiskCandidates,
  repeatedBlocks: repeatedBlocks.slice(0, 40),
  groupedHotspots,
  safety: {
    excludedFirstPass: ['installMainStyles CSS delivery or selector grouping', 'observer ownership/scope', 'scheduler timing', 'network sequencing', 'cross-feature helper consolidation'],
    required: ['single bounded subsystem', 'exact generated runtime value parity', 'deterministic subsystem contracts', 'canonical source/dist parity', 'full performance and integrity gates']
  }
};
fs.mkdirSync(path.dirname(reportPath), { recursive: true });
fs.writeFileSync(jsonPath, `${JSON.stringify(report, null, 2)}\n`, 'utf8');

function table(headers, rows) {
  return [`| ${headers.join(' | ')} |`, `|${headers.map(() => '---').join('|')}|`, ...rows.map(row => `| ${row.map(value => String(value).replaceAll('|', '\\|')).join(' | ')} |`)].join('\n');
}

const md = [
  '# Issue #253 — source headroom structural inventory',
  '',
  `- Version: \`${deep.source.version}\``,
  `- SHA-256: \`${deep.source.sha256}\``,
  `- Source: **${deep.source.lines.toLocaleString('en-GB')} lines** / 32,000`,
  `- Remaining headroom: **${(32000 - deep.source.lines).toLocaleString('en-GB')} lines**`,
  `- Source bytes: **${deep.source.bytes.toLocaleString('en-GB')}**`,
  `- Blank physical lines: **${blankLines.toLocaleString('en-GB')}**`,
  `- Comment-only physical lines: **${commentOnlyLines.toLocaleString('en-GB')}**`,
  '',
  '## Largest functions and templates',
  '',
  table(['Function', 'Lines', 'Bytes', 'Flow', 'Reads', 'Writes'], deep.topFunctionsByLines.slice(0, 30).map(item => [item.name, item.lines, item.bytes, item.flow, item.reads, item.writes])),
  '',
  table(['Template owner', 'Type', 'Line', 'Bytes', 'Rules/braces'], deep.largeTemplates.slice(0, 20).map(item => [item.function, item.classification, item.line, item.bytes, item.braceCount])),
  '',
  '## Top-level static literal candidates',
  '',
  table(['Name', 'Kind', 'Lines', 'Bytes', 'Entries', 'JSON-like', 'Estimated recovered lines'], staticLiterals.slice(0, 50).map(item => [item.name, item.kind, item.lines, item.bytes, item.entries, item.jsonLike, item.jsonLike ? Math.max(0, item.lines - 3) : '—'])),
  '',
  '## Exact repeated source blocks',
  '',
  table(['Width', 'Occurrences', 'Potential lines', 'Locations', 'Preview'], repeatedBlocks.slice(0, 25).map(item => [item.width, item.occurrences, item.recoverableLines, item.locations.join(', '), item.preview])),
  '',
  '## First-pass safety decision',
  '',
  '- Do not touch stylesheet delivery, CSS selector grouping, observer scope, scheduler timing or network sequencing in the first source-headroom PR.',
  '- Prefer a JSON-like static catalogue with deterministic serialization and an exact runtime-value parity contract.',
  '- Keep the readable source catalogue in `src/data`; generate one compact literal in the canonical single-file userscript.',
  '- Use one subsystem and one rollback boundary.',
  '',
  '## Candidate ranking',
  '',
  table(['Name', 'Lines', 'Bytes', 'Entries', 'Estimated recovered lines'], lowRiskCandidates.slice(0, 20).map(item => [item.name, item.lines, item.bytes, item.entries, item.estimatedRecoveredLines])),
  '',
  'This inventory is static structural evidence. A production change still requires exact generated-value parity and the complete repository test suite.',
  ''
].join('\n');
fs.writeFileSync(reportPath, md, 'utf8');
console.log(`Wrote ${path.relative(root, reportPath)} and ${path.relative(root, jsonPath)}`);
console.log(`Source lines: ${deep.source.lines}; headroom: ${32000 - deep.source.lines}; JSON-like candidates: ${lowRiskCandidates.length}`);
