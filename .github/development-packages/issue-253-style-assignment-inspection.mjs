#!/usr/bin/env node
import fs from 'node:fs';
import path from 'node:path';
import process from 'node:process';
import { parse } from 'acorn';

const root = process.cwd();
const sourcePath = path.join(root, 'src/MissionChief_Map_Command_Toolkit.user.js');
const reportPath = path.join(root, 'docs/issue-253-style-assignment-inspection.txt');
const source = fs.readFileSync(sourcePath, 'utf8');
const ast = parse(source, { ecmaVersion: 'latest', sourceType: 'script', locations: true, ranges: true });

function functionName(node, parent) {
  if (node.id?.name) return node.id.name;
  if (parent?.type === 'VariableDeclarator' && parent.id?.type === 'Identifier') return parent.id.name;
  return `<anonymous@${node.loc.start.line}>`;
}

const stack = [];
let best = null;
function walk(node, parent = null, owner = '<top-level>') {
  if (!node || typeof node !== 'object' || typeof node.type !== 'string') return;
  const nextOwner = ['FunctionDeclaration', 'FunctionExpression', 'ArrowFunctionExpression'].includes(node.type) ? functionName(node, parent) : owner;
  stack.push(node);
  if (node.type === 'TemplateLiteral' && nextOwner === 'installMainStyles') {
    const bytes = Buffer.byteLength(source.slice(node.start + 1, node.end - 1), 'utf8');
    if (!best || bytes > best.bytes) {
      best = { node, bytes, parents: stack.slice(0, -1).map(item => item.type) };
    }
  }
  for (const [key, value] of Object.entries(node)) {
    if (['start', 'end', 'loc', 'range'].includes(key)) continue;
    if (Array.isArray(value)) for (const child of value) walk(child, node, nextOwner);
    else if (value && typeof value === 'object' && typeof value.type === 'string') walk(value, node, nextOwner);
  }
  stack.pop();
}
walk(ast);
if (!best || best.bytes < 800000) throw new Error('main stylesheet template not found');
const { node, bytes, parents } = best;
const prefixStart = Math.max(0, node.start - 240);
const suffixEnd = Math.min(source.length, node.end + 120);
const prefix = source.slice(prefixStart, node.start + 1);
const suffix = source.slice(node.end - 1, suffixEnd);
const output = [
  `bytes=${bytes}`,
  `start=${node.start}`,
  `end=${node.end}`,
  `line=${node.loc.start.line}`,
  `parents=${parents.slice(-12).join(' > ')}`,
  '--- PREFIX THROUGH OPENING BACKTICK ---',
  prefix.replaceAll('\r', '\\r').replaceAll('\n', '\\n\n'),
  '--- CLOSING BACKTICK AND SUFFIX ---',
  suffix.replaceAll('\r', '\\r').replaceAll('\n', '\\n\n'),
  `quasis=${node.quasis.length}`,
  `expressions=${node.expressions.length}`,
];
fs.writeFileSync(reportPath, `${output.join('\n')}\n`, 'utf8');
console.log(`Wrote ${path.relative(root, reportPath)}`);
