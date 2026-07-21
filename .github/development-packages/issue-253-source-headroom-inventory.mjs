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
  if (node.type === 'NewExpression' && ['Map', 'Set'].includes(expressionName(node.callee)) && node.arguments.length === 1) return unwrap(node.arguments[0]);
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

const staticLiterals = [];
walk(ast, (node, _parent, owner) => {
  if (node.type !== 'VariableDeclarator' || node.id?.type !== 'Identifier' || !node.init) return;
  const candidate = unwrap(node.init);
  if (!['ObjectExpression', 'ArrayExpression', 'TemplateLiteral'].includes(candidate?.type)) return;
  const lines = node.loc.end.line - node.loc.start.line + 1;
  if (lines < 3) return;
  staticLiterals.push({
    name: node.id.name,
    owner,
    kind: candidate.type,
    startLine: node.loc.start.line,
    endLine: node.loc.end.line,
    lines,
    bytes: Buffer.byteLength(source.slice(node.start, node.end), 'utf8'),
    entries: countEntries(candidate),
    jsonLike: jsonLike(candidate)
  });
});
staticLiterals.sort((a, b) => b.lines - a.lines || b.bytes - a.bytes || a.name.localeCompare(b.name));

const sourceLines = source.split(/\r?\n/u);
const blankLines = sourceLines.filter(line => !line.trim()).length;
const commentOnlyLines = sourceLines.filter(line => /^\s*(?:\/\/|\/\*|\*|\*\/)/u.test(line)).length;

function normalizedLine(line) {
  return line.trim().replace(/\s+/gu, ' ');
}

const repeatedBlocks = [];
for (const width of [8, 6, 4]) {
  const seen = new Map();
  for (let index = 0; index + width <= sourceLines.length; index += 1) {
    const blockLines = sourceLines.slice(index, index + width);
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

const externalizable = staticLiterals.filter(item => item.jsonLike && item.lines >= 20);
const lowRiskCandidates = externalizable.map(item => ({ ...item, estimatedRecoveredLines: Math.max(0, item.lines - 3), method: 'Readable src/data catalogue plus deterministic compact embedding in the canonical userscript.' }));
const report = {
  schemaVersion: 2,
  source: deep.source,
  currentHeadroom: 32000 - deep.source.lines,
  blankLines,
  commentOnlyLines,
  topFunctionsByLines: deep.topFunctionsByLines,
  largeTemplates: deep.largeTemplates,
  staticLiterals,
  externalizableJsonLikeLiterals: lowRiskCandidates,
  repeatedBlocks: repeatedBlocks.slice(0, 40),
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
  '## Static literal candidates across all scopes',
  '',
  table(['Name', 'Owner', 'Kind', 'Lines', 'Bytes', 'Entries', 'JSON-like', 'Estimated recovered lines'], staticLiterals.slice(0, 60).map(item => [item.name, item.owner, item.kind, item.lines, item.bytes, item.entries, item.jsonLike, item.jsonLike ? Math.max(0, item.lines - 3) : '—'])),
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
  table(['Name', 'Owner', 'Lines', 'Bytes', 'Entries', 'Estimated recovered lines'], lowRiskCandidates.slice(0, 30).map(item => [item.name, item.owner, item.lines, item.bytes, item.entries, item.estimatedRecoveredLines])),
  '',
  'This inventory is static structural evidence. A production change still requires exact generated-value parity and the complete repository test suite.',
  ''
].join('\n');
fs.writeFileSync(reportPath, md, 'utf8');
console.log(`Wrote ${path.relative(root, reportPath)} and ${path.relative(root, jsonPath)}`);
console.log(`Source lines: ${deep.source.lines}; headroom: ${32000 - deep.source.lines}; JSON-like candidates: ${lowRiskCandidates.length}`);
