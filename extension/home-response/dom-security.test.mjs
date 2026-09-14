import test from 'node:test';
import assert from 'node:assert/strict';
import fs from 'node:fs';
import vm from 'node:vm';
import {JSDOM} from 'jsdom';

const source = fs.readFileSync(new URL('../recovered-0.22.3/toolkit.js', import.meta.url), 'utf8');
function helpers(window) {
  const names = ['escapeHtml', 'decodeMissionTextEntities', 'setInnerHtmlIfChanged'];
  const functions = names.map(name => {
    const start = source.indexOf('    function ' + name + '(');
    assert.ok(start >= 0);
    const end = source.indexOf('\n    function ', start + 1);
    assert.ok(end > start);
    return source.slice(start, end);
  }).join('\n');
  const context = {document: window.document};
  vm.createContext(context);
  vm.runInContext(functions, context);
  return context;
}

test('mission entity decoding preserves captions and keeps markup inert on every pass', () => {
  const dom = new JSDOM('<!doctype html><body></body>');
  const h = helpers(dom.window);
  assert.equal(h.decodeMissionTextEntities('A &amp;quot;quoted&amp;quot; &amp; caf&eacute; &#x1F691;'), 'A "quoted" & café 🚑');
  assert.equal(h.decodeMissionTextEntities('A < B &amp; C'), 'A < B & C');
  for (const input of [
    '</textarea><img src=x onerror="alert(1)">&amp;',
    '&lt;/textarea&gt;&lt;svg onload="alert(1)"&gt;',
    '&amp;lt;img src=x onerror=alert(1)&amp;gt;'
  ]) {
    const decoded = h.decodeMissionTextEntities(input);
    const host = dom.window.document.createElement('div');
    h.setInnerHtmlIfChanged(host, '<strong>' + h.escapeHtml(decoded) + '</strong>');
    assert.equal(host.textContent, decoded);
    assert.equal(host.querySelector('img,svg,script,textarea'), null);
    assert.equal(host.querySelector('strong').attributes.length, 0);
  }
  dom.window.close();
});

test('shared rendering keeps DOM text inert in text and quoted attributes and retains cache behaviour', () => {
  const dom = new JSDOM('<!doctype html><body></body>');
  const h = helpers(dom.window);
  const input = dom.window.document.createElement('span');
  input.textContent = '" autofocus onfocus="alert(1)"><img src=x onerror=alert(1)> & \'';
  const escaped = h.escapeHtml(input.textContent);
  const host = dom.window.document.createElement('div');
  const markup = '<button title="' + escaped + '">' + escaped + '</button>';
  assert.equal(h.setInnerHtmlIfChanged(host, markup), true);
  const button = host.firstElementChild;
  assert.equal(button.textContent, input.textContent);
  assert.equal(button.title, input.textContent);
  assert.deepEqual([...button.attributes].map(a => a.name), ['title']);
  assert.equal(host.querySelector('img'), null);
  assert.equal(h.setInnerHtmlIfChanged(host, markup), false);
  assert.equal(host.firstElementChild, button);
  assert.equal(h.setInnerHtmlIfChanged(host, '<em>Updated</em>'), true);
  assert.equal(host.textContent, 'Updated');
  dom.window.close();
});
