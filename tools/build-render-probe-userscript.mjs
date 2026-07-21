#!/usr/bin/env node
import fs from 'node:fs';
import path from 'node:path';
import crypto from 'node:crypto';
import process from 'node:process';
import * as acorn from 'acorn';

const TARGETS = Object.freeze(['updateUI', 'renderOperationalPanels']);

function sha256(value) {
    return crypto.createHash('sha256').update(value).digest('hex');
}

function walk(node, visit) {
    if (!node || typeof node !== 'object') return;
    visit(node);
    for (const value of Object.values(node)) {
        if (Array.isArray(value)) value.forEach(item => walk(item, visit));
        else if (value && typeof value === 'object' && typeof value.type === 'string') walk(value, visit);
    }
}

export function instrumentSource(source, targets = TARGETS) {
    const ast = acorn.parse(source, { ecmaVersion: 'latest', sourceType: 'script', allowHashBang: true });
    const found = new Map();
    walk(ast, node => {
        if (node.type === 'FunctionDeclaration' && node.id?.name && targets.includes(node.id.name)) {
            if (found.has(node.id.name)) throw new Error(`Duplicate function declaration: ${node.id.name}`);
            found.set(node.id.name, node);
        }
    });
    const missing = targets.filter(name => !found.has(name));
    if (missing.length) throw new Error(`Missing render probe target(s): ${missing.join(', ')}`);

    const replacements = targets.map(name => {
        const node = found.get(name);
        const bodyStart = node.body.start + 1;
        const bodyEnd = node.body.end - 1;
        const body = source.slice(bodyStart, bodyEnd);
        const safe = name.replace(/[^A-Za-z0-9_$]/g, '_');
        const replacement = `\n        const __mcmsRenderProbeToken_${safe} = globalThis.__MCMS_PROFILER__?.beginRender?.(${JSON.stringify(name)}) ?? null;\n        try {${body}\n        } finally {\n            globalThis.__MCMS_PROFILER__?.endRender?.(__mcmsRenderProbeToken_${safe});\n        }\n    `;
        return { start: bodyStart, end: bodyEnd, replacement, name };
    }).sort((a, b) => b.start - a.start);

    let generated = source;
    for (const item of replacements) generated = generated.slice(0, item.start) + item.replacement + generated.slice(item.end);
    generated = generated.replace(/^(\/\/ @name\s+.+)$/m, '$1 [Render Probe]');
    generated = generated.replace(/^(\/\/ @description\s+)(.+)$/m, '$1Development-only render probe build. $2');
    const sourceHash = sha256(source);
    generated = generated.replace('// ==/UserScript==', `// ==/UserScript==\n// MCMS render probe source SHA-256: ${sourceHash}`);
    return { generated, sourceHash, generatedHash: sha256(generated), targets: replacements.map(item => item.name).sort() };
}

function parseArgs(argv) {
    const result = {};
    for (let index = 0; index < argv.length; index += 1) {
        const key = argv[index];
        if (!key.startsWith('--')) throw new Error(`Unexpected argument: ${key}`);
        const value = argv[index + 1];
        if (!value || value.startsWith('--')) throw new Error(`Missing value for ${key}`);
        result[key.slice(2)] = value;
        index += 1;
    }
    return result;
}

function main() {
    const args = parseArgs(process.argv.slice(2));
    if (!args.source || !args.output || !args.manifest) {
        throw new Error('Usage: build-render-probe-userscript.mjs --source <file> --output <file> --manifest <file>');
    }
    const sourcePath = path.resolve(args.source);
    const outputPath = path.resolve(args.output);
    const manifestPath = path.resolve(args.manifest);
    if (sourcePath === outputPath) throw new Error('Render probe output must not overwrite the canonical source.');
    const source = fs.readFileSync(sourcePath, 'utf8');
    const result = instrumentSource(source);
    fs.mkdirSync(path.dirname(outputPath), { recursive: true });
    fs.mkdirSync(path.dirname(manifestPath), { recursive: true });
    fs.writeFileSync(outputPath, result.generated, 'utf8');
    fs.writeFileSync(manifestPath, JSON.stringify({
        schemaVersion: 1,
        source: path.relative(process.cwd(), sourcePath),
        output: path.basename(outputPath),
        sourceSha256: result.sourceHash,
        generatedSha256: result.generatedHash,
        instrumentedFunctions: result.targets,
        productionSourceModified: false,
    }, null, 2) + '\n', 'utf8');
}

if (process.argv[1] && path.resolve(process.argv[1]) === path.resolve(new URL(import.meta.url).pathname)) {
    try { main(); } catch (error) { console.error(error.message); process.exit(1); }
}
