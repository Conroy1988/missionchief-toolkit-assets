import test from 'node:test';import assert from 'node:assert/strict';import {JSDOM} from 'jsdom';import {readFileSync} from 'node:fs';import {execFileSync} from 'node:child_process';import vm from 'node:vm';
const root=new URL('../../',import.meta.url);execFileSync('python3',['extension/build-recovered.py'],{cwd:root});
const source=readFileSync(new URL('../../.dev/home-response-extension/toolkit.js',import.meta.url),'utf8');
test('icon form accepts blank/zero unassigned dispatch but rejects real changes',()=>{
 const dom=new JSDOM('<form><select name="building[leitstelle_building_id]"><option value="" selected>Unassigned</option><option value="42">Centre</option></select><input name="building[caption]" value="Example"></form>');
 const context=vm.createContext({stationIconSafeSkip:message=>new Error(message)}),start=source.indexOf('    function stationIconAssertFormValue('),end=source.indexOf('    function prepareStationIconSubmission(',start);
 vm.runInContext(source.slice(start,end),context);const form=dom.window.document.querySelector('form'),name='building[leitstelle_building_id]',check=context.stationIconAssertFormValue;
 check(form,name,'0');check(form,name,0);assert.equal(form.elements.namedItem(name).value,'');assert.throws(()=>check(form,name,'42'),/no longer matches/);
 form.elements.namedItem(name).value='42';check(form,name,'42');assert.throws(()=>check(form,name,'0'),/no longer matches/);assert.throws(()=>check(form,'building[caption]','Other'),/no longer matches/);
});
test('sticky Operations return keeps selections and running task state',()=>{
 const dom=new JSDOM('<section><div data-command-card="station-icon-copier"><h3 class="mcms-section-label">Icons</h3><label class="mcms-row"><input data-setting="source" value="chosen"></label><button data-action="stop-station-icons">Stop</button></div></section>');
 const context=vm.createContext({document:dom.window.document,setTimeout,clearInterval:()=>{},setInterval:()=>1,HomeResponseBuilder:{mount:()=>{}}});
 const start=source.indexOf('function createOperationsController(api){'),end=source.indexOf('// Presentation only.',start);
 vm.runInContext(source.slice(start,end),context);
 const runtime={running:true,queue:[]},api={styleUrl:'operations.css',active:()=>true,activate:()=>{},snapshot:()=>({runtime,count:0}),runtime:()=>runtime};
 const controller=context.createOperationsController(api),card=dom.window.document.querySelector('[data-command-card]');controller.add(card);controller.open('station-icon-copier');
 const back=card.querySelector('.mcms-operation-sticky > .mcms-operation-back');assert.ok(back);assert.equal(back.disabled,false);back.click();assert.equal(controller.current(),null);assert.equal(dom.window.document.querySelector('.mcms-operations-home').hidden,false);assert.equal(runtime.running,true);assert.equal(card.querySelector('input').value,'chosen');
 controller.open('station-icon-copier');assert.equal(card.querySelector('input').value,'chosen');controller.destroy();
});
test('Operations sidebar click returns home without bubbling into another navigation action',()=>{
 const start=source.indexOf('function click(e){const tab='),end=source.indexOf('\n  function key(e)',start);let backs=0,stopped=false;
 const context=vm.createContext({api:{back:()=>backs++},closeMenu:()=>{},setTimeout});vm.runInContext(source.slice(start,end),context);
 context.click({target:{closest:()=>({dataset:{tab:'administration'}})},preventDefault:()=>{},stopPropagation:()=>{stopped=true;}});assert.equal(backs,1);assert.equal(stopped,true);
 const css=readFileSync(new URL('../../.dev/home-response-extension/command-ui.css',import.meta.url),'utf8');assert.ok(!css.includes('.mcms-operation-description,.mcms-operation-back,'));assert.ok(css.includes('.mcms-operation-sticky > .mcms-operation-back{display:inline-flex!important'));
});
