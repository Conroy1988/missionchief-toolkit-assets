#!/usr/bin/env node
import fs from 'node:fs';
import process from 'node:process';
import { parse } from 'acorn';

const FUNCTION_TYPES = new Set(['FunctionDeclaration', 'FunctionExpression', 'ArrowFunctionExpression']);

function propertyName(node) {
  if (!node) return null;
  if (node.type === 'Identifier') return node.name;
  if (node.type === 'Literal') return String(node.value);
  if (node.type !== 'MemberExpression') return null;
  if (!node.computed && node.property?.type === 'Identifier') return node.property.name;
  if (node.computed && node.property?.type === 'Literal') return String(node.property.value);
  return null;
}

function expressionName(node) {
  if (!node) return '';
  if (node.type === 'Identifier') return node.name;
  if (node.type === 'ChainExpression') return expressionName(node.expression);
  if (node.type === 'MemberExpression') {
    const object = expressionName(node.object);
    const property = propertyName(node);
    return object && property ? `${object}.${property}` : property || object;
  }
  return '';
}

function functionName(node, parent) {
  if (node.id?.name) return node.id.name;
  if (parent?.type === 'VariableDeclarator') return expressionName(parent.id);
  if (parent?.type === 'AssignmentExpression') return expressionName(parent.left);
  if (parent?.type === 'Property' || parent?.type === 'MethodDefinition') return propertyName(parent.key);
  return null;
}

function walk(node, visitor, parent = null) {
  if (!node || typeof node !== 'object' || typeof node.type !== 'string') return;
  visitor(node, parent);
  for (const [key, value] of Object.entries(node)) {
    if (['start', 'end', 'loc', 'range'].includes(key)) continue;
    if (Array.isArray(value)) {
      for (const child of value) walk(child, visitor, node);
    } else if (value && typeof value === 'object' && typeof value.type === 'string') {
      walk(value, visitor, node);
    }
  }
}

function main() {
  const [sourcePath, outputPath, ...requested] = process.argv.slice(2);
  if (!sourcePath || !outputPath || !requested.length) {
    console.error('Usage: extract_deep_performance_evidence.mjs SOURCE OUTPUT FUNCTION...');
    process.exit(2);
  }
  const source = fs.readFileSync(sourcePath, 'utf8');
  const ast = parse(source, { ecmaVersion: 'latest', sourceType: 'script', locations: true, ranges: true });
  const found = new Map();
  walk(ast, (node, parent) => {
    if (!FUNCTION_TYPES.has(node.type)) return;
    const name = functionName(node, parent);
    if (name && requested.includes(name) && !found.has(name)) found.set(name, node);
  });
  const missing = requested.filter(name => !found.has(name));
  if (missing.length) throw new Error(`Missing requested function evidence: ${missing.join(', ')}`);

  const lines = [
    '# Deep performance source evidence',
    '',
    '> Exact v4.20.17 source blocks selected from the AST-backed hotspot inventory. This is review evidence, not a proposed patch.',
    ''
  ];
  for (const name of requested) {
    const node = found.get(name);
    lines.push(`## ${name}`, '', `Lines ${node.loc.start.line}-${node.loc.end.line}`, '', '```javascript', source.slice(node.start, node.end), '```', '');
  }
  fs.writeFileSync(outputPath, `${lines.join('\n')}\n`, 'utf8');
  console.log(`Extracted ${requested.length} performance evidence blocks`);
}

try {
  main();
} catch (error) {
  console.error(error?.stack || String(error));
  process.exit(1);
}
