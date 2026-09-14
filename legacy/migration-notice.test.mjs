import {test} from 'node:test';
import assert from 'node:assert/strict';
import {readFileSync} from 'node:fs';
import {createRequire} from 'node:module';
const require=createRequire(new URL('../extension/home-response/package.json',import.meta.url));
const {JSDOM}=require('jsdom');
const script=readFileSync(new URL('./migration-notice.js',import.meta.url),'utf8');
const id='tkb-extension-migration-notice',key='tkb-extension-migration-snooze-v1';
function page(){return new JSDOM('<!doctype html><body><main id="game">Game</main></body>',{url:'https://www.missionchief.co.uk/',runScripts:'outside-only'});}
function run(w){w.eval(script);w.document.dispatchEvent(new w.Event('DOMContentLoaded'));}
test('notice loads once without altering game or existing settings',()=>{const d=page(),w=d.window;w.localStorage.setItem('existing','keep');run(w);run(w);assert.equal(w.document.querySelectorAll('#'+id).length,1);assert.equal(w.localStorage.getItem('existing'),'keep');assert.equal(w.document.getElementById('game').textContent,'Game');const root=w.document.getElementById(id).shadowRoot;assert.match(root.textContent,/no longer supported/);assert.equal(root.querySelector('a').href,'https://chromewebstore.google.com/detail/lmnojpchebgcochdfnfjmnficicnaaoc');assert.equal(root.querySelector('a').rel,'noopener noreferrer');d.window.close();});
test('seven day snooze suppresses notice until expiry',()=>{const d=page(),w=d.window;run(w);w.document.getElementById(id).shadowRoot.querySelector('button').click();assert.ok(Number(w.localStorage.getItem(key))>Date.now());run(w);assert.equal(w.document.getElementById(id),null);w.localStorage.setItem(key,String(Date.now()-1));run(w);assert.ok(w.document.getElementById(id));w.close();});
test('blocked storage still shows a dismissible notice',()=>{const d=page(),w=d.window;Object.defineProperty(w,'localStorage',{get(){throw Error('blocked');}});run(w);w.document.getElementById(id).shadowRoot.querySelector('button').click();assert.equal(w.document.getElementById(id),null);w.close();});
test('does not inject into child frames',()=>{const d=page(),w=d.window;const frame=w.document.createElement('iframe');w.document.body.append(frame);run(frame.contentWindow);assert.equal(frame.contentWindow.document.getElementById(id),null);w.close();});
