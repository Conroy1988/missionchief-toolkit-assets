import test from 'node:test';import assert from 'node:assert/strict';import {JSDOM} from 'jsdom';
const dom=new JSDOM('<div id="grid"></div>',{url:'https://www.missionchief.co.uk/'});globalThis.window=dom.window;globalThis.document=dom.window.document;globalThis.Option=dom.window.Option;dom.window.HTMLDialogElement.prototype.showModal=function(){this.open=true;};
const {mount}=await import('./ui.mjs');
test('visual icon picker selects one image with an accessible selected state',async()=>{
 const {configureImages}=await import('./ui.mjs');configureImages({sources:async()=>({icons:[{id:'12',caption:'Example',customIconUrl:'https://example.com/icon.png',count:8}],unavailable:0})});
 const grid=document.createElement('div');document.body.append(grid);mount(grid);grid.querySelector('button').click();await document.querySelector('[data-load-icons]').onclick();
 const buttons=document.querySelectorAll('[data-icon-grid] button');assert.equal(buttons.length,2);assert.ok(buttons[1].querySelector('img'));buttons[1].click();assert.equal(document.querySelector('[data-image]').value,'12');assert.equal(buttons[1].getAttribute('aria-pressed'),'true');assert.equal(buttons[0].getAttribute('aria-pressed'),'false');document.querySelector('[data-close]').click();grid.remove();
});
test('Operations launcher is unique and exposes exact spacing and all verified vehicles',()=>{const grid=document.getElementById('grid');mount(grid);mount(grid);assert.equal(grid.children.length,1);grid.querySelector('button').click();assert.ok(document.querySelector('dialog').open);assert.deepEqual([...document.querySelector('[data-spacing]').options].map(o=>o.value),['1','3','4','6','8','10']);assert.equal(document.querySelector('[data-vehicle]').options.length,14);assert.equal(document.querySelector('[data-limit]').max,'1000');assert.equal(document.querySelector('[data-budget]'),null);assert.ok(document.querySelector('[data-cities]').options.length>60);assert.ok(document.querySelector('[data-image]'));assert.ok(document.querySelector('[data-build]').disabled);assert.ok(document.querySelector('[data-preview]').disabled);document.querySelector('[data-close]').click();assert.equal(document.querySelector('dialog'),null);});
test('area controls enable radius only when it defines the selected area',async()=>{
 const grid=document.createElement('div');document.body.append(grid);mount(grid);grid.querySelector('button').click();
 const mode=document.querySelector('[data-mode]'),radius=document.querySelector('[data-radius]'),finish=document.querySelector('[data-finish]');
 assert.equal(radius.disabled,true);assert.equal(finish.disabled,true);
 mode.value='radius';await mode.onchange();assert.equal(radius.disabled,false);assert.equal(finish.disabled,true);
 mode.value='draw';await mode.onchange();assert.equal(radius.disabled,true);assert.equal(finish.disabled,false);
 mode.value='boundary';await mode.onchange();assert.equal(radius.disabled,true);assert.equal(finish.disabled,true);assert.ok(document.querySelector('[data-build]').disabled);
 document.querySelector('[data-close]').click();grid.remove();
});
test('selecting a city restores boundary mode and point results never silently select radius',async()=>{
 const grid=document.createElement('div');document.body.append(grid);mount(grid);grid.querySelector('button').click();
 const original=globalThis.fetch;globalThis.fetch=async()=>({ok:true,json:async()=>[
 {display_name:'Test city',lon:-3,lat:54,geojson:{type:'Polygon',coordinates:[[[-3,54],[-2.9,54],[-2.9,54.1],[-3,54.1],[-3,54]]]}},
 {display_name:'Point only',lon:-3,lat:54,geojson:{type:'Point',coordinates:[-3,54]}}
 ]});
 try{const mode=document.querySelector('[data-mode]');mode.value='radius';await mode.onchange();document.querySelector('[data-city]').value='Test';await document.querySelector('[data-search]').onclick();
 const places=document.querySelector('[data-places]');places.value='0';await places.onchange();assert.equal(mode.value,'boundary');assert.equal(document.querySelector('[data-radius]').disabled,true);
 places.value='1';await places.onchange();assert.equal(mode.value,'boundary');assert.match(document.querySelector('[data-status]').textContent,/no mapped boundary/);assert.equal(document.querySelector('[data-build]').disabled,true);
 assert.ok(document.querySelector('[data-status]').compareDocumentPosition(document.querySelector('[data-map]'))&4);
 }finally{globalThis.fetch=original;document.querySelector('[data-close]').click();grid.remove();}
});
