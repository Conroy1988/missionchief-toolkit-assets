#!/usr/bin/env node

import fs from 'node:fs';
import crypto from 'node:crypto';
import process from 'node:process';
import { parse } from 'acorn';

const [filePath, expectedVersion] = process.argv.slice(2);

if (!filePath || !expectedVersion) {
  console.error('Usage: validate_userscript.mjs FILE EXPECTED_VERSION');
  process.exit(2);
}

const source = fs.readFileSync(filePath, 'utf8');
const bytes = fs.readFileSync(filePath);

function fail(message) {
  console.error(`Validation failed: ${message}`);
  process.exit(1);
}

if (!source.startsWith('// ==UserScript==')) {
  fail('The downloaded file does not start with a userscript metadata block.');
}

const metadataVersion = source.match(/^\/\/\s*@version\s+(.+?)\s*$/m)?.[1]?.trim();
if (metadataVersion !== expectedVersion) {
  fail(`@version is '${metadataVersion ?? 'missing'}', expected '${expectedVersion}'.`);
}

const scriptBlock = source.match(/const\s+SCRIPT\s*=\s*\{([\s\S]*?)\n\s*\};/);
if (!scriptBlock) {
  fail('Could not find the SCRIPT configuration object.');
}

const internalVersion = scriptBlock[1].match(/\bversion\s*:\s*['"]([^'"]+)['"]/)?.[1];
if (internalVersion !== expectedVersion) {
  fail(`SCRIPT.version is '${internalVersion ?? 'missing'}', expected '${expectedVersion}'.`);
}

const requiredMetadata = [
  '// @author       Conroy1988',
  '// @license      MIT',
  '// @downloadURL https://update.greasyfork.org/scripts/586018/MissionChief%20Map%20Command%20Toolkit.user.js',
  '// @updateURL https://update.greasyfork.org/scripts/586018/MissionChief%20Map%20Command%20Toolkit.meta.js'
];

for (const line of requiredMetadata) {
  if (!source.includes(line)) fail(`Required userscript metadata is missing or changed: ${line}`);
}

const webhookPattern = /https:\/\/(?:canary\.)?discord(?:app)?\.com\/api\/webhooks\/\d+\/[A-Za-z0-9._-]+/;
if (webhookPattern.test(source)) {
  fail('A Discord webhook URL appears to be embedded in the published source.');
}

if (bytes.length < 100_000) {
  fail(`Published script is unexpectedly small: ${bytes.length} bytes.`);
}

if (bytes.length > 5_000_000) {
  fail(`Published script is unexpectedly large: ${bytes.length} bytes.`);
}

let ast;
try {
  ast = parse(source, {
    ecmaVersion: 'latest',
    sourceType: 'script',
    allowHashBang: true
  });
} catch (error) {
  fail(`JavaScript parser error: ${error.message}`);
}

const duplicateFunctions = [];
const duplicateObjectKeys = [];

function propertyName(property) {
  if (!property || property.computed) return null;
  if (property.key.type === 'Identifier') return property.key.name;
  if (property.key.type === 'Literal') return String(property.key.value);
  return null;
}

function checkBody(body, label) {
  const seen = new Set();
  for (const node of body ?? []) {
    if (node?.type !== 'FunctionDeclaration' || !node.id?.name) continue;
    if (seen.has(node.id.name)) duplicateFunctions.push(`${node.id.name} in ${label}`);
    seen.add(node.id.name);
  }
}

function walk(node, label = 'program') {
  if (!node || typeof node !== 'object') return;

  if (node.type === 'Program' || node.type === 'BlockStatement') {
    checkBody(node.body, label);
  }

  if (node.type === 'ObjectExpression') {
    const seen = new Set();
    for (const property of node.properties) {
      if (property.type !== 'Property') continue;
      const name = propertyName(property);
      if (name === null) continue;
      const key = `${property.kind ?? 'init'}:${name}`;
      if (seen.has(key)) duplicateObjectKeys.push(name);
      seen.add(key);
    }
  }

  for (const [key, value] of Object.entries(node)) {
    if (key === 'start' || key === 'end' || key === 'loc') continue;

    if (Array.isArray(value)) {
      for (const child of value) walk(child, `${label}/${node.type}`);
    } else if (value && typeof value === 'object' && typeof value.type === 'string') {
      walk(value, `${label}/${node.type}`);
    }
  }
}

walk(ast);

if (duplicateFunctions.length) {
  fail(`Duplicate function declarations: ${duplicateFunctions.join(', ')}`);
}

if (duplicateObjectKeys.length) {
  fail(`Duplicate object-literal keys: ${[...new Set(duplicateObjectKeys)].join(', ')}`);
}

const sha256 = crypto.createHash('sha256').update(bytes).digest('hex');
fs.writeFileSync('greasyfork-script.sha256', `${sha256}\n`, 'utf8');

console.log(`Validated version ${expectedVersion}`);
console.log(`Size: ${bytes.length.toLocaleString('en-GB')} bytes`);
console.log(`SHA-256: ${sha256}`);
console.log('Duplicate function declarations: 0');
console.log('Duplicate object-literal keys: 0');
