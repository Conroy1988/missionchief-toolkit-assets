import test from 'node:test';
import assert from 'node:assert/strict';
import fs from 'node:fs';
import vm from 'node:vm';
import {JSDOM} from 'jsdom';

const source = fs.readFileSync(new URL('../recovered-0.22.3/toolkit.js', import.meta.url), 'utf8');
function helpers(window, extra = {}) {
  const names = ['escapeHtml', 'decodeMissionTextEntities', 'setInnerHtmlIfChanged', 'layoutStudioMarkup', 'notificationStudioMarkup'];
  const functions = names.map(name => {
    const start = source.indexOf('    function ' + name + '(');
    assert.ok(start >= 0);
    const end = source.indexOf('\n    function ', start + 1);
    assert.ok(end > start);
    return source.slice(start, end);
  }).join('\n');
  const context = {document: window.document, ...extra};
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

test('Layout Studio renders malformed saved layout values as text, never attributes or elements', () => {
  const dom = new JSDOM('<!doctype html><body></body>');
  const payload = '\"><img src=x onerror=alert(1)><span data-injected="yes';
  const preferences = {position:'bl', groupOrder:[payload], controlOrder:{[payload]:[payload]}, hiddenControls:[], panelWidth:payload, panelHeight:payload, panelHeightPx:payload};
  const h = helpers(dom.window, {
    state:{layoutBuilder:{layouts:{desktop:preferences}},commandBarPrimary:[]},
    POSITIONS:{bl:{label:'Bottom left'}}, LAYOUT_DEVICE_KEYS:['desktop','tablet','mobile'],
    LAYOUT_CONTROL_GROUPS:{[payload]:{label:'Map controls'}}, LAYOUT_CONTROL_LABELS:{[payload]:'Menu'},
    COMMAND_BAR_CONTROL_KEYS:[payload], DESKTOP_WORKSPACE_MAX_WIDTH:1600
  });
  const host=dom.window.document.createElement('div');
  h.setInnerHtmlIfChanged(host,h.layoutStudioMarkup('desktop'));
  assert.equal(host.querySelector('img,script,svg,[data-injected],[onerror]'),null);
  assert.equal(host.querySelector('[data-layout-value]').getAttribute('data-layout-value'),payload);
  assert.equal(host.querySelector('[data-layout-panel-width]').getAttribute('value'),payload);
  assert.ok(host.textContent.includes(payload));
  preferences.groupOrder=[];
  preferences.panelWidth=1000; preferences.panelHeight=85; preferences.panelHeightPx=700;
  h.setInnerHtmlIfChanged(host,h.layoutStudioMarkup('desktop'));
  assert.equal(host.querySelector('[data-layout-panel-width]').value,'1000');
  assert.equal(host.querySelector('[data-layout-panel-height]').value,'85');
  assert.ok(host.textContent.includes('Workspace height · 700px resized'));
  assert.equal(host.querySelector('[data-layout-position]').value,'bl');
  dom.window.close();
});


test('Notification volume cannot inject attributes or elements through saved settings', () => {
  const dom = new JSDOM('<!doctype html><body></body>');
  const notifications = {volume:'0.5" onpointerover="alert(1)"><img src=x onerror=alert(1)>',events:{},enabled:true,preset:'standard'};
  const h = helpers(dom.window, {state:{notifications},pageWindow:{},NOTIFICATION_PRESETS:{standard:{label:'Standard'}},NOTIFICATION_EVENT_META:{}});
  const host = dom.window.document.createElement('div');
  h.setInnerHtmlIfChanged(host,h.notificationStudioMarkup());
  assert.equal(host.querySelector('img,[onpointerover],[onerror]'),null);
  assert.equal(host.querySelector('[data-notification-setting="volume"]').getAttribute('value'),notifications.volume);
  notifications.volume=0.65;
  h.setInnerHtmlIfChanged(host,h.notificationStudioMarkup());
  assert.equal(host.querySelector('[data-notification-setting="volume"]').value,'0.65');
  assert.ok(host.textContent.includes('Master volume · 65%'));
  assert.equal(host.querySelector('[data-notification-setting="preset"]').value,'standard');
  dom.window.close();
});
