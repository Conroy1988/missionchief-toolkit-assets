#!/usr/bin/env node
import assert from 'node:assert/strict';
import { analyseSource, renderMarkdown } from './deep_performance_audit.mjs';

const css = 'x{display:block;}\n'.repeat(100);
const source = `// ==UserScript==
// @version 9.9.9
// ==/UserScript==
const MutationObserverCtor = window.MutationObserver;
function installFeature() {
  const observer = runtimeTrackObserver(new MutationObserverCtor(records => { if (records.length) renderPanel(); }));
  observer.observe(document.body, { childList: true, subtree: true });
  runtimeSetTimeout(() => renderPanel(), 250);
}
function renderPanel() {
  const root = document.querySelector('#root');
  const again = document.querySelector('#root');
  if (!root) return;
  root.textContent = 'ok';
  root.setAttribute('aria-live', 'polite');
}
function styles() {
  return \`${css}\`;
}
`;

const data = analyseSource(source, 'fixture.user.js');
assert.equal(data.schemaVersion, 3);
assert.equal(data.parser, 'acorn');
assert.equal(data.source.version, '9.9.9');
assert.equal(data.summary.mutationObserverConstructions, 1);
assert.equal(data.summary.resizeObserverConstructions, 0);
assert.equal(data.summary.observerConstructions, 1);
assert.equal(data.summary.observerRegistrations, 1);
assert.equal(data.summary.broadSubtreeObservers, 1);
assert.equal(data.summary.schedulerCalls, 1);
assert.equal(data.unresolvedObserveCalls.length, 0);

const observer = data.observerRegistrations[0];
assert.equal(observer.constructor, 'MutationObserver');
assert.equal(observer.tracked, true);
assert.equal(observer.disconnectSignal, true);
assert.equal(observer.subtree, true);

const repeated = data.repeatedSelectors.find(item => item.selector === '#root');
assert.ok(repeated);
assert.equal(repeated.count, 2);
assert.deepEqual(repeated.functions, ['renderPanel']);

const template = data.largeTemplates[0];
assert.equal(template.classification, 'css');
assert.equal(template.function, 'styles');

const install = data.topFunctionsByScore.find(item => item.name === 'installFeature');
assert.ok(install);
assert.equal(install.schedulers, 1);
assert.equal(install.observers, 1);
assert.equal(install.flow, 0, 'nested callback flow belongs to the callback, not the parent function');

const observerCallback = data.topFunctionsByScore.find(item => item.name.startsWith('MutationObserverCtor callback') && item.flow === 1);
assert.ok(observerCallback, 'observer callback should own its control-flow count');

const markdown = renderMarkdown(data);
assert.match(markdown, /AST-backed static structural evidence/);
assert.match(markdown, /Trusted-baseline cross-check/);
assert.match(markdown, /installFeature/);
assert.match(markdown, /Resolved observer registrations/);

console.log('AST-backed deep performance audit fixtures passed');
