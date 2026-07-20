#!/usr/bin/env node
/**
 * AST-backed structural performance inventory for the MissionChief Toolkit.
 *
 * This tool identifies profiling targets. It does not claim live runtime gains.
 */
import crypto from 'node:crypto';
import fs from 'node:fs';
import process from 'node:process';
import { parse } from 'acorn';

const FUNCTION_TYPES = new Set(['FunctionDeclaration', 'FunctionExpression', 'ArrowFunctionExpression']);
const FLOW_TYPES = new Set(['IfStatement', 'ForStatement', 'ForInStatement', 'ForOfStatement', 'WhileStatement', 'DoWhileStatement', 'SwitchCase', 'CatchClause', 'ConditionalExpression']);
const SCHEDULERS = new Set(['runtimeSetTimeout', 'runtimeSetInterval', 'runtimeRequestAnimationFrame', 'runtimeRunWhenIdle', 'setTimeout', 'setInterval', 'requestAnimationFrame']);
const DOM_READ_METHODS = new Set(['querySelector', 'querySelectorAll', 'getElementById', 'closest', 'matches', 'getAttribute', 'getBoundingClientRect', 'getClientRects']);
const DOM_WRITE_METHODS = new Set(['setAttribute', 'removeAttribute', 'appendChild', 'replaceChildren', 'insertBefore', 'insertAdjacentHTML', 'remove', 'before', 'after', 'replaceWith']);
const DOM_WRITE_PROPERTIES = new Set(['innerHTML', 'outerHTML', 'textContent', 'innerText', 'value', 'checked', 'hidden', 'disabled', 'selected', 'src', 'href']);
const CLASSLIST_METHODS = new Set(['add', 'remove', 'toggle', 'replace']);
const CSS_SIGNAL = /(?:!important|--[\w-]+\s*:|(?:display|position|color|background|border|font|padding|margin|width|height|opacity|transform|animation|z-index)\s*:)/iu;

function parseArguments(argv) {
  const result = {};
  for (let index = 0; index < argv.length; index += 1) {
    const key = argv[index];
    if (!key.startsWith('--')) throw new Error(`Unexpected argument: ${key}`);
    const value = argv[index + 1];
    if (!value || value.startsWith('--')) throw new Error(`Missing value for ${key}`);
    result[key.slice(2)] = value;
    index += 1;
  }
  for (const required of ['source', 'json-output', 'markdown-output']) {
    if (!result[required]) throw new Error(`Missing --${required}`);
  }
  return result;
}

function propertyName(node) {
  if (!node) return null;
  if (!node.computed && node.property?.type === 'Identifier') return node.property.name;
  if (node.computed && node.property?.type === 'Literal') return String(node.property.value);
  if (node.type === 'Identifier') return node.name;
  if (node.type === 'Literal') return String(node.value);
  return null;
}

function expressionName(node) {
  if (!node) return '';
  if (node.type === 'Identifier') return node.name;
  if (node.type === 'ThisExpression') return 'this';
  if (node.type === 'MemberExpression') {
    const object = expressionName(node.object);
    const property = propertyName(node);
    return object && property ? `${object}.${property}` : property || object;
  }
  return '';
}

function functionBaseName(node, parent) {
  if (node.id?.name) return node.id.name;
  if (parent?.type === 'VariableDeclarator' && parent.id?.type === 'Identifier') return parent.id.name;
  if (parent?.type === 'AssignmentExpression') return expressionName(parent.left) || null;
  if (parent?.type === 'Property' || parent?.type === 'MethodDefinition') return propertyName(parent.key) || null;
  if (parent?.type === 'CallExpression') {
    const callee = expressionName(parent.callee) || 'callback';
    return `${callee} callback`;
  }
  return null;
}

function literalString(node) {
  if (!node) return null;
  if (node.type === 'Literal' && typeof node.value === 'string') return node.value;
  if (node.type === 'TemplateLiteral' && node.expressions.length === 0) return node.quasis.map(part => part.value.cooked ?? part.value.raw).join('');
  return null;
}

function sourceText(source, node, limit = null) {
  const value = source.slice(node.start, node.end).replace(/\s+/gu, ' ').trim();
  return limit && value.length > limit ? `${value.slice(0, limit - 1)}…` : value;
}

function byteLength(value) {
  return Buffer.byteLength(value, 'utf8');
}

function makeWalker(visitor) {
  function walk(node, parent = null, owner = null) {
    if (!node || typeof node !== 'object' || typeof node.type !== 'string') return;
    const nextOwner = visitor(node, parent, owner) ?? owner;
    for (const [key, value] of Object.entries(node)) {
      if (['start', 'end', 'loc', 'range'].includes(key)) continue;
      if (Array.isArray(value)) {
        for (const child of value) walk(child, node, nextOwner);
      } else if (value && typeof value === 'object' && typeof value.type === 'string') {
        walk(value, node, nextOwner);
      }
    }
  }
  return walk;
}

function detectObserverKind(node, aliases) {
  if (!node || typeof node !== 'object') return null;
  if (node.type === 'Identifier') return aliases.get(node.name) || null;
  if (node.type === 'MemberExpression') {
    const name = propertyName(node);
    if (name === 'MutationObserver' || name === 'ResizeObserver') return name;
  }
  for (const [key, value] of Object.entries(node)) {
    if (['start', 'end', 'loc', 'range'].includes(key)) continue;
    if (Array.isArray(value)) {
      for (const child of value) {
        const kind = detectObserverKind(child, aliases);
        if (kind) return kind;
      }
    } else if (value && typeof value === 'object') {
      const kind = detectObserverKind(value, aliases);
      if (kind) return kind;
    }
  }
  return null;
}

function assignmentProperty(node) {
  if (!node || node.type !== 'MemberExpression') return null;
  const name = propertyName(node);
  if (name) return name;
  return null;
}

function isStyleAssignment(left) {
  if (!left || left.type !== 'MemberExpression') return false;
  if (propertyName(left.object) === 'style') return true;
  return expressionName(left).includes('.style.');
}

function markdownTable(headers, rows) {
  return [
    `| ${headers.join(' | ')} |`,
    `|${headers.map(() => '---').join('|')}|`,
    ...rows.map(row => `| ${row.map(value => String(value).replaceAll('|', '\\|')).join(' | ')} |`)
  ];
}

export function analyseSource(source, sourcePath = 'src/MissionChief_Map_Command_Toolkit.user.js') {
  const ast = parse(source, {
    ecmaVersion: 'latest',
    sourceType: 'script',
    allowHashBang: true,
    locations: true,
    ranges: true
  });

  const functionRecords = [];
  const functionByNode = new Map();
  const namesUsed = new Map();
  const aliases = new Map([
    ['MutationObserver', 'MutationObserver'],
    ['ResizeObserver', 'ResizeObserver']
  ]);

  const collectAliases = makeWalker((node) => {
    if (node.type === 'VariableDeclarator' && node.id?.type === 'Identifier' && node.init) {
      const kind = detectObserverKind(node.init, aliases);
      if (kind) aliases.set(node.id.name, kind);
    }
    return null;
  });
  for (let pass = 0; pass < 4; pass += 1) collectAliases(ast);

  const collectFunctions = makeWalker((node, parent, owner) => {
    if (!FUNCTION_TYPES.has(node.type)) return owner;
    const base = functionBaseName(node, parent) || `<anonymous@${node.loc.start.line}>`;
    const count = (namesUsed.get(base) || 0) + 1;
    namesUsed.set(base, count);
    const name = count === 1 ? base : `${base}@${node.loc.start.line}`;
    const record = {
      id: functionRecords.length,
      name,
      startLine: node.loc.start.line,
      endLine: node.loc.end.line,
      lines: node.loc.end.line - node.loc.start.line + 1,
      bytes: byteLength(source.slice(node.start, node.end)),
      flow: 0,
      reads: 0,
      writes: 0,
      schedulers: 0,
      observers: 0,
      network: 0,
      score: 0
    };
    functionRecords.push(record);
    functionByNode.set(node, record);
    return record.id;
  });
  collectFunctions(ast);

  const observers = [];
  const observerByOwnerVariable = new Map();
  const observerSignals = new Map();
  const registrations = [];
  const schedulerCalls = [];
  const largeTemplates = [];
  const selectorIndex = new Map();

  function metric(owner, key, amount = 1) {
    if (owner === null || owner === undefined) return;
    functionRecords[owner][key] += amount;
  }

  function ownerVariableKey(owner, variable) {
    return `${owner ?? 'top'}:${variable}`;
  }

  function nearestObserver(owner, variable, beforeLine) {
    const direct = observerByOwnerVariable.get(ownerVariableKey(owner, variable));
    if (direct) return direct;
    return observers.filter(item => item.variable === variable && item.line <= beforeLine).at(-1) || null;
  }

  const analyse = makeWalker((node, parent, inheritedOwner) => {
    const owner = FUNCTION_TYPES.has(node.type) ? functionByNode.get(node)?.id ?? inheritedOwner : inheritedOwner;

    if (FLOW_TYPES.has(node.type)) metric(owner, 'flow');

    if (node.type === 'TemplateLiteral') {
      const raw = source.slice(node.start + 1, node.end - 1);
      const bytes = byteLength(raw);
      if (bytes >= 1000) {
        const classification = CSS_SIGNAL.test(raw) && raw.includes('{') && raw.includes('}') ? 'css' : raw.includes('<') && raw.includes('>') ? 'html' : 'text';
        largeTemplates.push({
          line: node.loc.start.line,
          bytes,
          classification,
          braceCount: classification === 'css' ? (raw.match(/\{/gu) || []).length : 0,
          function: owner === null || owner === undefined ? '<top-level>' : functionRecords[owner].name
        });
      }
    }

    if (node.type === 'AssignmentExpression') {
      const property = assignmentProperty(node.left);
      if ((property && DOM_WRITE_PROPERTIES.has(property)) || isStyleAssignment(node.left)) metric(owner, 'writes');
    }

    if (node.type === 'UpdateExpression' && node.argument?.type === 'MemberExpression') {
      metric(owner, 'writes');
    }

    if (node.type === 'NewExpression') {
      const kind = detectObserverKind(node.callee, aliases);
      if (kind) {
        let variable = null;
        if (parent?.type === 'VariableDeclarator' && parent.id?.type === 'Identifier') variable = parent.id.name;
        else if (parent?.type === 'AssignmentExpression' && parent.left?.type === 'Identifier') variable = parent.left.name;
        const item = {
          id: observers.length,
          constructor: kind,
          variable,
          line: node.loc.start.line,
          function: owner === null || owner === undefined ? '<top-level>' : functionRecords[owner].name,
          owner,
          tracked: false,
          disconnectSignal: false,
          registrySignal: false,
          registrations: []
        };
        observers.push(item);
        metric(owner, 'observers');
        if (variable) observerByOwnerVariable.set(ownerVariableKey(owner, variable), item);
      }
      if (propertyName(node.callee) === 'XMLHttpRequest') metric(owner, 'network');
    }

    if (node.type === 'CallExpression') {
      const calleeName = expressionName(node.callee);
      const method = node.callee?.type === 'MemberExpression' ? propertyName(node.callee) : node.callee?.type === 'Identifier' ? node.callee.name : null;

      if (method && DOM_READ_METHODS.has(method)) metric(owner, 'reads');
      if (method && DOM_WRITE_METHODS.has(method)) metric(owner, 'writes');
      if (node.callee?.type === 'MemberExpression' && propertyName(node.callee.object) === 'classList' && CLASSLIST_METHODS.has(method)) metric(owner, 'writes');

      if (SCHEDULERS.has(method)) {
        metric(owner, 'schedulers');
        const delayOrMode = method.includes('AnimationFrame') ? 'frame' : method === 'runtimeRunWhenIdle' ? 'idle' : node.arguments[1] ? sourceText(source, node.arguments[1], 100) : '';
        schedulerCalls.push({
          scheduler: method,
          line: node.loc.start.line,
          function: owner === null || owner === undefined ? '<top-level>' : functionRecords[owner].name,
          delayOrMode
        });
      }

      if (method === 'fetch' || calleeName === 'GM_xmlhttpRequest' || calleeName === 'GM.xmlHttpRequest') metric(owner, 'network');

      if ((method === 'querySelector' || method === 'querySelectorAll') && node.arguments.length) {
        const selector = literalString(node.arguments[0]);
        if (selector !== null) {
          const entry = selectorIndex.get(selector) || { selector, count: 0, functions: new Set(), lines: [] };
          entry.count += 1;
          entry.functions.add(owner === null || owner === undefined ? '<top-level>' : functionRecords[owner].name);
          entry.lines.push(node.loc.start.line);
          selectorIndex.set(selector, entry);
        }
      }

      if (method === 'runtimeTrackObserver' && node.arguments[0]?.type === 'Identifier') {
        const variable = node.arguments[0].name;
        const signal = observerSignals.get(ownerVariableKey(owner, variable)) || {};
        signal.tracked = true;
        observerSignals.set(ownerVariableKey(owner, variable), signal);
      }

      if (node.callee?.type === 'MemberExpression' && node.callee.object?.type === 'Identifier') {
        const variable = node.callee.object.name;
        if (method === 'disconnect') {
          const signal = observerSignals.get(ownerVariableKey(owner, variable)) || {};
          signal.disconnected = true;
          observerSignals.set(ownerVariableKey(owner, variable), signal);
        }
        if (method === 'observe') {
          const linked = nearestObserver(owner, variable, node.loc.start.line);
          const target = node.arguments[0] ? sourceText(source, node.arguments[0], 180) : '';
          const options = node.arguments[1] ? sourceText(source, node.arguments[1], 700) : '';
          const registration = {
            line: node.loc.start.line,
            function: owner === null || owner === undefined ? '<top-level>' : functionRecords[owner].name,
            observer: variable,
            constructor: linked?.constructor || 'unknown',
            target,
            options,
            subtree: /\bsubtree\s*:\s*true\b/u.test(options),
            childList: /\bchildList\s*:\s*true\b/u.test(options),
            attributes: /\battributes\s*:\s*true\b/u.test(options),
            tracked: false,
            disconnectSignal: false,
            registrySignal: false
          };
          registrations.push(registration);
          if (linked) linked.registrations.push(registration);
        }
      }

      if (node.callee?.type === 'MemberExpression' && ['add', 'push', 'set'].includes(method) && node.arguments[0]?.type === 'Identifier') {
        const variable = node.arguments[0].name;
        const text = calleeName.toLowerCase();
        if (text.includes('observer')) {
          const signal = observerSignals.get(ownerVariableKey(owner, variable)) || {};
          signal.registry = true;
          observerSignals.set(ownerVariableKey(owner, variable), signal);
        }
      }
    }

    return owner;
  });
  analyse(ast);

  for (const observer of observers) {
    if (!observer.variable) continue;
    const signal = observerSignals.get(ownerVariableKey(observer.owner, observer.variable)) || {};
    observer.tracked = Boolean(signal.tracked);
    observer.disconnectSignal = Boolean(signal.disconnected || signal.tracked);
    observer.registrySignal = Boolean(signal.registry);
    for (const registration of observer.registrations) {
      registration.tracked = observer.tracked;
      registration.disconnectSignal = observer.disconnectSignal;
      registration.registrySignal = observer.registrySignal;
    }
  }

  for (const record of functionRecords) {
    record.score = record.lines + record.flow * 6 + record.reads * 5 + record.writes * 8 + record.schedulers * 6 + record.observers * 10 + record.network * 12;
  }

  const byScheduler = new Map();
  for (const item of schedulerCalls) byScheduler.set(item.function, (byScheduler.get(item.function) || 0) + 1);
  const repeatedSelectors = [...selectorIndex.values()]
    .filter(item => item.count >= 2)
    .map(item => ({ selector: item.selector, count: item.count, functions: [...item.functions].sort(), lines: item.lines.slice(0, 20) }))
    .sort((a, b) => b.count - a.count || a.selector.localeCompare(b.selector));

  largeTemplates.sort((a, b) => b.bytes - a.bytes || a.line - b.line);
  schedulerCalls.sort((a, b) => a.line - b.line || a.scheduler.localeCompare(b.scheduler));
  registrations.sort((a, b) => a.line - b.line);

  const lines = source.split(/\r?\n/u);
  const sourceSummary = {
    path: sourcePath,
    version: source.match(/^\/\/\s*@version\s+([^\s]+)/mu)?.[1] || 'unknown',
    sha256: crypto.createHash('sha256').update(source, 'utf8').digest('hex'),
    bytes: byteLength(source),
    lines: lines.length,
    nonemptyLines: lines.filter(value => value.trim()).length
  };
  const broadSubtreeObservers = registrations.filter(item => item.subtree).length;
  const visibleOwnershipSignals = registrations.filter(item => item.disconnectSignal || item.registrySignal).length;
  const findings = [];
  const remaining = 32000 - sourceSummary.lines;
  if (remaining < 500) findings.push({ risk: 'high', category: 'source-headroom', message: `Only ${remaining} lines remain before the existing 32,000-line ceiling.` });
  if (largeTemplates[0]?.classification === 'css' && largeTemplates[0].bytes > 500000) findings.push({ risk: 'high', category: 'style-parse', message: 'The largest embedded CSS template exceeds 500 KB; live timing and visual contracts are required before changing style delivery.' });
  if (broadSubtreeObservers) findings.push({ risk: 'medium', category: 'observer-scope', message: `${broadSubtreeObservers} observer registrations use subtree:true; ownership and callback evidence are required before narrowing or merging them.` });
  if (visibleOwnershipSignals < registrations.length) findings.push({ risk: 'medium', category: 'observer-ownership', message: `${registrations.length - visibleOwnershipSignals} registrations lack an AST-visible disconnect, runtimeTrackObserver or observer-registry signal and require manual lifecycle verification.` });
  if (repeatedSelectors[0]?.count >= 4) findings.push({ risk: 'low', category: 'selector-repetition', message: 'Repeated literal selectors exist; cache only inside proven document/window lifetimes with invalidation fixtures.' });

  const sortRecords = (key, limit = 30) => [...functionRecords].filter(record => record.name !== '<anonymous@47>').sort((a, b) => b[key] - a[key] || b.lines - a.lines || a.name.localeCompare(b.name)).slice(0, limit);

  return {
    schemaVersion: 2,
    tool: 'mcms-deep-performance-audit',
    parser: 'acorn',
    source: sourceSummary,
    summary: {
      namedFunctions: functionRecords.length,
      largeTemplates: largeTemplates.length,
      observerConstructions: observers.length,
      observerRegistrations: registrations.length,
      broadSubtreeObservers,
      schedulerCalls: schedulerCalls.length,
      repeatedSelectors: repeatedSelectors.length
    },
    topFunctionsByScore: sortRecords('score'),
    topFunctionsByLines: sortRecords('lines'),
    topDomReaders: sortRecords('reads', 25).filter(item => item.reads),
    topDomWriters: sortRecords('writes', 25).filter(item => item.writes),
    topSchedulerFunctions: [...byScheduler.entries()].map(([functionName, calls]) => ({ function: functionName, calls })).sort((a, b) => b.calls - a.calls || a.function.localeCompare(b.function)).slice(0, 30),
    observerConstructions: observers.map(({ owner, ...item }) => item),
    observerRegistrations: registrations,
    schedulerCalls,
    largeTemplates: largeTemplates.slice(0, 40),
    repeatedSelectors: repeatedSelectors.slice(0, 50),
    findings,
    interpretation: {
      staticOnly: true,
      liveEvidenceRequired: ['long tasks', 'layout shifts', 'mutation frequency', 'render frequency', 'style recalculation', 'memory retention'],
      safetyRule: 'Do not merge runtime changes solely to reduce a static count.'
    }
  };
}

export function renderMarkdown(data) {
  const { source, summary } = data;
  const lines = [
    '# MissionChief Toolkit deep performance audit',
    '',
    '> AST-backed static structural evidence only. Runtime gains require equivalent browser-profiler scenarios and deterministic behaviour parity.',
    '',
    '## Baseline',
    '',
    `- Parser: \`${data.parser}\``,
    `- Version: \`${source.version}\``,
    `- SHA-256: \`${source.sha256}\``,
    `- Source: \`${source.bytes.toLocaleString('en-GB')}\` bytes, \`${source.lines.toLocaleString('en-GB')}\` lines`,
    `- Functions/callbacks: \`${summary.namedFunctions}\``,
    `- Scheduler calls: \`${summary.schedulerCalls}\``,
    `- Observer constructions: \`${summary.observerConstructions}\``,
    `- Observer registrations: \`${summary.observerRegistrations}\``,
    `- Broad subtree registrations: \`${summary.broadSubtreeObservers}\``,
    '',
    '## Findings',
    '',
    ...(data.findings.length ? data.findings.map(item => `- **${item.risk.toUpperCase()} · ${item.category}** — ${item.message}`) : ['- No static review findings.']),
    '',
    '## Highest structural hotspot scores',
    '',
    ...markdownTable(
      ['Function', 'Lines', 'Bytes', 'Flow', 'Reads', 'Writes', 'Schedulers', 'Observers', 'Network', 'Score'],
      data.topFunctionsByScore.slice(0, 20).map(item => [item.name, item.lines, item.bytes, item.flow, item.reads, item.writes, item.schedulers, item.observers, item.network, item.score])
    ),
    '',
    '## DOM-write concentration',
    '',
    ...markdownTable(
      ['Function', 'Lines', 'Reads', 'Writes', 'Schedulers', 'Score'],
      data.topDomWriters.slice(0, 20).map(item => [item.name, item.lines, item.reads, item.writes, item.schedulers, item.score])
    ),
    '',
    '## Scheduler concentration',
    '',
    ...markdownTable(['Function', 'Calls'], data.topSchedulerFunctions.slice(0, 20).map(item => [item.function, item.calls])),
    '',
    '## Observer registrations',
    '',
    ...markdownTable(
      ['Line', 'Function', 'Type', 'Target', 'Options', 'Tracked', 'Registry', 'Disconnect'],
      data.observerRegistrations.map(item => [item.line, item.function, item.constructor, item.target, item.options, item.tracked, item.registrySignal, item.disconnectSignal])
    ),
    '',
    '## Observer constructions without a matched registration',
    '',
    ...markdownTable(
      ['Line', 'Function', 'Type', 'Variable', 'Tracked', 'Registry', 'Disconnect'],
      data.observerConstructions.filter(item => !item.registrations.length).map(item => [item.line, item.function, item.constructor, item.variable || '', item.tracked, item.registrySignal, item.disconnectSignal])
    ),
    '',
    '## Largest embedded templates',
    '',
    ...markdownTable(['Line', 'Function', 'Type', 'Bytes', 'Brace/rule estimate'], data.largeTemplates.slice(0, 20).map(item => [item.line, item.function, item.classification, item.bytes, item.braceCount])),
    '',
    '## Repeated literal selectors',
    '',
    ...markdownTable(['Count', 'Selector', 'Functions'], data.repeatedSelectors.slice(0, 25).map(item => [item.count, item.selector, item.functions.join(', ')])),
    '',
    '## Safety interpretation',
    '',
    '- A large function or repeated selector is a profiling target, not proof of a defect.',
    '- Observer count must not be reduced by merging different lifecycle owners.',
    '- Cached DOM references require explicit invalidation when MissionChief replaces documents, dialogs, frames or controls.',
    '- CSS extraction requires visual contracts and first-paint evidence.',
    '- Every runtime optimisation must be isolated, benchmarked and reversible.',
    ''
  ];
  return lines.join('\n');
}

function main() {
  const args = parseArguments(process.argv.slice(2));
  const source = fs.readFileSync(args.source, 'utf8');
  const data = analyseSource(source, args.source);
  fs.writeFileSync(args['json-output'], `${JSON.stringify(data, null, 2)}\n`, 'utf8');
  fs.writeFileSync(args['markdown-output'], renderMarkdown(data), 'utf8');
  console.log(JSON.stringify(data.summary, null, 2));
}

if (process.argv[1] && new URL(import.meta.url).pathname === process.argv[1]) {
  try {
    main();
  } catch (error) {
    console.error(error?.stack || String(error));
    process.exit(1);
  }
}
