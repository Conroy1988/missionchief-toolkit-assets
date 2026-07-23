#!/usr/bin/env node
/**
 * AST-backed structural performance inventory for the MissionChief Toolkit.
 *
 * The report identifies profiling targets. It is not a browser benchmark and
 * must never be used alone to justify a production runtime change.
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
  if (node.type === 'ThisExpression') return 'this';
  if (node.type === 'ChainExpression') return expressionName(node.expression);
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
  if (parent?.type === 'CallExpression') return `${expressionName(parent.callee) || 'callback'} callback`;
  if (parent?.type === 'NewExpression') return `${expressionName(parent.callee) || 'constructor'} callback`;
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

function walk(node, visitor, parent = null, owner = null) {
  if (!node || typeof node !== 'object' || typeof node.type !== 'string') return;
  const nextOwner = visitor(node, parent, owner) ?? owner;
  for (const [key, value] of Object.entries(node)) {
    if (['start', 'end', 'loc', 'range'].includes(key)) continue;
    if (Array.isArray(value)) {
      for (const child of value) walk(child, visitor, node, nextOwner);
    } else if (value && typeof value === 'object' && typeof value.type === 'string') {
      walk(value, visitor, node, nextOwner);
    }
  }
}

function directObserverKind(node, aliases) {
  if (!node) return null;
  if (node.type === 'Identifier') return aliases.get(node.name) || null;
  if (node.type === 'MemberExpression') {
    const name = propertyName(node);
    return name === 'MutationObserver' || name === 'ResizeObserver' ? name : null;
  }
  if (node.type === 'ChainExpression' || node.type === 'AwaitExpression') return directObserverKind(node.expression || node.argument, aliases);
  if (node.type === 'LogicalExpression' || node.type === 'BinaryExpression') return directObserverKind(node.left, aliases) || directObserverKind(node.right, aliases);
  if (node.type === 'ConditionalExpression') return directObserverKind(node.consequent, aliases) || directObserverKind(node.alternate, aliases);
  if (node.type === 'SequenceExpression') {
    for (const expression of node.expressions) {
      const kind = directObserverKind(expression, aliases);
      if (kind) return kind;
    }
  }
  return null;
}

function assignmentProperty(node) {
  return node?.type === 'MemberExpression' ? propertyName(node) : null;
}

function isStyleAssignment(left) {
  if (!left || left.type !== 'MemberExpression') return false;
  return propertyName(left.object) === 'style' || expressionName(left).includes('.style.');
}

function markdownTable(headers, rows) {
  if (!rows.length) return ['_None._'];
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

  const parents = new Map();
  walk(ast, (node, parent) => {
    if (parent) parents.set(node, parent);
    return null;
  });

  const aliases = new Map([
    ['MutationObserver', 'MutationObserver'],
    ['ResizeObserver', 'ResizeObserver']
  ]);
  for (let pass = 0; pass < 4; pass += 1) {
    walk(ast, (node) => {
      if (node.type !== 'VariableDeclarator' || node.id?.type !== 'Identifier' || !node.init) return null;
      const kind = directObserverKind(node.init, aliases);
      if (kind) aliases.set(node.id.name, kind);
      return null;
    });
  }

  const functionRecords = [];
  const functionByNode = new Map();
  const namesUsed = new Map();
  walk(ast, (node, parent, owner) => {
    if (!FUNCTION_TYPES.has(node.type)) return owner;
    const base = functionBaseName(node, parent) || `<anonymous@${node.loc.start.line}>`;
    const count = (namesUsed.get(base) || 0) + 1;
    namesUsed.set(base, count);
    const name = count === 1 ? base : `${base}@${node.loc.start.line}`;
    const wrapper = node.start < 5000 && node.end > source.length * 0.95;
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
      score: 0,
      wrapper
    };
    functionRecords.push(record);
    functionByNode.set(node, record);
    return record.id;
  });

  const objectBindings = new Map();
  walk(ast, (node, _parent, owner) => {
    if (node.type === 'VariableDeclarator' && node.id?.type === 'Identifier' && node.init?.type === 'ObjectExpression') {
      objectBindings.set(`${owner ?? 'top'}:${node.id.name}`, sourceText(source, node.init, 700));
    }
    return FUNCTION_TYPES.has(node.type) ? functionByNode.get(node)?.id ?? owner : owner;
  });

  function assignedName(node) {
    let current = node;
    while (current) {
      const parent = parents.get(current);
      if (!parent || FUNCTION_TYPES.has(parent)) return null;
      if (parent.type === 'VariableDeclarator' && parent.init === current) return expressionName(parent.id);
      if (parent.type === 'AssignmentExpression' && parent.right === current) return expressionName(parent.left);
      current = parent;
    }
    return null;
  }

  function hasAncestorCall(node, callName) {
    let current = node;
    while (current) {
      const parent = parents.get(current);
      if (!parent || FUNCTION_TYPES.has(parent)) return false;
      if (parent.type === 'CallExpression' && expressionName(parent.callee) === callName) return true;
      current = parent;
    }
    return false;
  }

  const observerConstructions = [];
  const rawObserveCalls = [];
  const signalMap = new Map();
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

  function recordSignal(owner, variable, key) {
    if (!variable) return;
    const id = ownerVariableKey(owner, variable);
    const signal = signalMap.get(id) || { tracked: false, disconnected: false, registry: false };
    signal[key] = true;
    signalMap.set(id, signal);
  }

  walk(ast, (node, parent, inheritedOwner) => {
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
    if (node.type === 'UpdateExpression' && node.argument?.type === 'MemberExpression') metric(owner, 'writes');

    if (node.type === 'NewExpression') {
      const kind = directObserverKind(node.callee, aliases);
      if (kind) {
        const variable = assignedName(node);
        observerConstructions.push({
          id: observerConstructions.length,
          constructor: kind,
          variable,
          line: node.loc.start.line,
          function: owner === null || owner === undefined ? '<top-level>' : functionRecords[owner].name,
          owner,
          trackedByWrapper: hasAncestorCall(node, 'runtimeTrackObserver'),
          registrations: []
        });
        metric(owner, 'observers');
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
        schedulerCalls.push({
          scheduler: method,
          line: node.loc.start.line,
          function: owner === null || owner === undefined ? '<top-level>' : functionRecords[owner].name,
          delayOrMode: method.includes('AnimationFrame') ? 'frame' : method === 'runtimeRunWhenIdle' ? 'idle' : node.arguments[1] ? sourceText(source, node.arguments[1], 100) : ''
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

      if (method === 'runtimeTrackObserver') {
        const variable = expressionName(node.arguments[0]);
        if (variable) recordSignal(owner, variable, 'tracked');
      }

      if (node.callee?.type === 'MemberExpression') {
        const object = expressionName(node.callee.object);
        if (method === 'disconnect') recordSignal(owner, object, 'disconnected');
        if (method === 'observe') {
          rawObserveCalls.push({
            line: node.loc.start.line,
            owner,
            function: owner === null || owner === undefined ? '<top-level>' : functionRecords[owner].name,
            observer: object,
            target: node.arguments[0] ? sourceText(source, node.arguments[0], 180) : '',
            optionsNode: node.arguments[1] || null
          });
        }
        if (['add', 'push', 'set'].includes(method) && node.arguments[0]) {
          const variable = expressionName(node.arguments[0]);
          if (variable && calleeName.toLowerCase().includes('observer')) recordSignal(owner, variable, 'registry');
        }
      }
    }

    return owner;
  });

  function findConstruction(owner, variable, line) {
    const exact = observerConstructions.filter(item => item.owner === owner && item.variable === variable && item.line <= line).at(-1);
    if (exact) return exact;
    return observerConstructions.filter(item => item.variable === variable && item.line <= line).at(-1) || null;
  }

  function resolveOptions(owner, node) {
    if (!node) return '';
    if (node.type === 'Identifier') return objectBindings.get(ownerVariableKey(owner, node.name)) || objectBindings.get(`top:${node.name}`) || sourceText(source, node, 700);
    return sourceText(source, node, 700);
  }

  const unresolvedObserveCalls = [];
  const observerRegistrations = [];
  for (const item of rawObserveCalls) {
    const construction = findConstruction(item.owner, item.observer, item.line);
    if (!construction) {
      unresolvedObserveCalls.push({ line: item.line, function: item.function, observer: item.observer, target: item.target, options: resolveOptions(item.owner, item.optionsNode) });
      continue;
    }
    const ownSignal = signalMap.get(ownerVariableKey(construction.owner, construction.variable)) || {};
    const callSignal = signalMap.get(ownerVariableKey(item.owner, item.observer)) || {};
    const options = resolveOptions(item.owner, item.optionsNode);
    const registration = {
      line: item.line,
      function: item.function,
      observer: item.observer,
      constructor: construction.constructor,
      target: item.target,
      options,
      subtree: /\bsubtree\s*:\s*true\b/u.test(options),
      childList: /\bchildList\s*:\s*true\b/u.test(options),
      attributes: /\battributes\s*:\s*true\b/u.test(options),
      tracked: Boolean(construction.trackedByWrapper || ownSignal.tracked || callSignal.tracked),
      registrySignal: Boolean(ownSignal.registry || callSignal.registry),
      disconnectSignal: Boolean(construction.trackedByWrapper || ownSignal.tracked || callSignal.tracked || ownSignal.disconnected || callSignal.disconnected)
    };
    observerRegistrations.push(registration);
    construction.registrations.push(registration);
  }

  for (const construction of observerConstructions) {
    const signal = construction.variable ? signalMap.get(ownerVariableKey(construction.owner, construction.variable)) || {} : {};
    construction.tracked = Boolean(construction.trackedByWrapper || signal.tracked);
    construction.registrySignal = Boolean(signal.registry);
    construction.disconnectSignal = Boolean(construction.trackedByWrapper || signal.tracked || signal.disconnected);
  }

  for (const record of functionRecords) {
    record.score = record.lines + record.flow * 6 + record.reads * 5 + record.writes * 8 + record.schedulers * 6 + record.observers * 10 + record.network * 12;
  }

  const schedulerByFunction = new Map();
  for (const item of schedulerCalls) schedulerByFunction.set(item.function, (schedulerByFunction.get(item.function) || 0) + 1);
  const repeatedSelectors = [...selectorIndex.values()]
    .filter(item => item.count >= 2)
    .map(item => ({ selector: item.selector, count: item.count, functions: [...item.functions].sort(), lines: item.lines.slice(0, 20) }))
    .sort((a, b) => b.count - a.count || a.selector.localeCompare(b.selector));

  largeTemplates.sort((a, b) => b.bytes - a.bytes || a.line - b.line);
  schedulerCalls.sort((a, b) => a.line - b.line || a.scheduler.localeCompare(b.scheduler));
  observerRegistrations.sort((a, b) => a.line - b.line);
  unresolvedObserveCalls.sort((a, b) => a.line - b.line);

  const splitLines = source.split(/\r?\n/u);
  const lineCount = source.endsWith('\n') ? splitLines.length - 1 : splitLines.length;
  const sourceSummary = {
    path: sourcePath,
    version: source.match(/^\/\/\s*@version\s+([^\s]+)/mu)?.[1] || 'unknown',
    sha256: crypto.createHash('sha256').update(source, 'utf8').digest('hex'),
    bytes: byteLength(source),
    lines: lineCount,
    nonemptyLines: splitLines.filter(value => value.trim()).length
  };

  const broadSubtreeObservers = observerRegistrations.filter(item => item.subtree).length;
  const visibleOwnershipSignals = observerRegistrations.filter(item => item.disconnectSignal || item.registrySignal).length;
  const mutationConstructions = observerConstructions.filter(item => item.constructor === 'MutationObserver').length;
  const resizeConstructions = observerConstructions.filter(item => item.constructor === 'ResizeObserver').length;
  const findings = [];
  const remaining = 64000 - sourceSummary.lines;
  if (remaining < 500) findings.push({ risk: 'high', category: 'source-headroom', message: `Only ${remaining} lines remain before the existing 32,000-line ceiling.` });
  if (largeTemplates[0]?.classification === 'css' && largeTemplates[0].bytes > 500000) findings.push({ risk: 'high', category: 'style-parse', message: 'The largest embedded CSS template exceeds 500 KB; live timing and visual contracts are required before changing style delivery.' });
  if (broadSubtreeObservers) findings.push({ risk: 'medium', category: 'observer-scope', message: `${broadSubtreeObservers} resolved observer registrations use subtree:true; ownership and callback evidence are required before narrowing or merging them.` });
  if (visibleOwnershipSignals < observerRegistrations.length) findings.push({ risk: 'medium', category: 'observer-ownership', message: `${observerRegistrations.length - visibleOwnershipSignals} resolved registrations lack an AST-visible disconnect, runtimeTrackObserver or observer-registry signal and require manual lifecycle verification.` });
  if (unresolvedObserveCalls.length) findings.push({ risk: 'review', category: 'observer-linkage', message: `${unresolvedObserveCalls.length} .observe() calls could not be linked to a constructor by local AST ownership and remain manual-review items.` });
  if (repeatedSelectors[0]?.count >= 4) findings.push({ risk: 'low', category: 'selector-repetition', message: 'Repeated literal selectors exist; cache only inside proven document/window lifetimes with invalidation fixtures.' });

  const rankedFunctions = functionRecords.filter(record => !record.wrapper);
  const sortRecords = (key, limit = 30) => [...rankedFunctions].sort((a, b) => b[key] - a[key] || b.lines - a.lines || a.name.localeCompare(b.name)).slice(0, limit).map(({ wrapper, ...item }) => item);

  return {
    schemaVersion: 3,
    tool: 'mcms-deep-performance-audit',
    parser: 'acorn',
    source: sourceSummary,
    baselineCrossCheck: {
      expectedMutationObserverConstructions: 11,
      measuredMutationObserverConstructions: mutationConstructions,
      expectedResizeObserverConstructions: 4,
      measuredResizeObserverConstructions: resizeConstructions,
      expectedBroadSubtreeObservers: 9,
      measuredResolvedBroadSubtreeObservers: broadSubtreeObservers,
      unresolvedObserveCalls: unresolvedObserveCalls.length
    },
    summary: {
      functionsAndCallbacks: functionRecords.length,
      rankedFunctions: rankedFunctions.length,
      largeTemplates: largeTemplates.length,
      mutationObserverConstructions: mutationConstructions,
      resizeObserverConstructions: resizeConstructions,
      observerConstructions: observerConstructions.length,
      observerRegistrations: observerRegistrations.length,
      broadSubtreeObservers,
      schedulerCalls: schedulerCalls.length,
      repeatedSelectors: repeatedSelectors.length
    },
    topFunctionsByScore: sortRecords('score'),
    topFunctionsByLines: sortRecords('lines'),
    topDomReaders: sortRecords('reads', 25).filter(item => item.reads),
    topDomWriters: sortRecords('writes', 25).filter(item => item.writes),
    topSchedulerFunctions: [...schedulerByFunction.entries()].map(([functionName, calls]) => ({ function: functionName, calls })).sort((a, b) => b.calls - a.calls || a.function.localeCompare(b.function)).slice(0, 30),
    observerConstructions: observerConstructions.map(({ owner, trackedByWrapper, ...item }) => item),
    observerRegistrations,
    unresolvedObserveCalls,
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
  const { source, summary, baselineCrossCheck } = data;
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
    `- Functions/callbacks: \`${summary.functionsAndCallbacks}\``,
    `- Scheduler calls: \`${summary.schedulerCalls}\``,
    `- MutationObserver constructions: \`${summary.mutationObserverConstructions}\``,
    `- ResizeObserver constructions: \`${summary.resizeObserverConstructions}\``,
    `- Resolved observer registrations: \`${summary.observerRegistrations}\``,
    `- Resolved broad subtree registrations: \`${summary.broadSubtreeObservers}\``,
    '',
    '## Trusted-baseline cross-check',
    '',
    ...markdownTable(
      ['Metric', 'Trusted baseline', 'AST inventory'],
      [
        ['MutationObserver constructions', baselineCrossCheck.expectedMutationObserverConstructions, baselineCrossCheck.measuredMutationObserverConstructions],
        ['ResizeObserver constructions', baselineCrossCheck.expectedResizeObserverConstructions, baselineCrossCheck.measuredResizeObserverConstructions],
        ['Broad subtree registrations', baselineCrossCheck.expectedBroadSubtreeObservers, baselineCrossCheck.measuredResolvedBroadSubtreeObservers],
        ['Unresolved observe calls', 'manual review', baselineCrossCheck.unresolvedObserveCalls]
      ]
    ),
    '',
    '## Findings',
    '',
    ...(data.findings.length ? data.findings.map(item => `- **${item.risk.toUpperCase()} · ${item.category}** — ${item.message}`) : ['- No static review findings.']),
    '',
    '## Highest structural hotspot scores',
    '',
    ...markdownTable(['Function', 'Lines', 'Bytes', 'Flow', 'Reads', 'Writes', 'Schedulers', 'Observers', 'Network', 'Score'], data.topFunctionsByScore.slice(0, 20).map(item => [item.name, item.lines, item.bytes, item.flow, item.reads, item.writes, item.schedulers, item.observers, item.network, item.score])),
    '',
    '## DOM-write concentration',
    '',
    ...markdownTable(['Function', 'Lines', 'Reads', 'Writes', 'Schedulers', 'Score'], data.topDomWriters.slice(0, 20).map(item => [item.name, item.lines, item.reads, item.writes, item.schedulers, item.score])),
    '',
    '## Scheduler concentration',
    '',
    ...markdownTable(['Function', 'Calls'], data.topSchedulerFunctions.slice(0, 20).map(item => [item.function, item.calls])),
    '',
    '## Resolved observer registrations',
    '',
    ...markdownTable(['Line', 'Function', 'Type', 'Target', 'Options', 'Tracked', 'Registry', 'Disconnect'], data.observerRegistrations.map(item => [item.line, item.function, item.constructor, item.target, item.options, item.tracked, item.registrySignal, item.disconnectSignal])),
    '',
    '## Unresolved observe calls',
    '',
    ...markdownTable(['Line', 'Function', 'Observer expression', 'Target', 'Options'], data.unresolvedObserveCalls.map(item => [item.line, item.function, item.observer, item.target, item.options])),
    '',
    '## Observer constructions without a matched registration',
    '',
    ...markdownTable(['Line', 'Function', 'Type', 'Variable', 'Tracked', 'Registry', 'Disconnect'], data.observerConstructions.filter(item => !item.registrations.length).map(item => [item.line, item.function, item.constructor, item.variable || '', item.tracked, item.registrySignal, item.disconnectSignal])),
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
