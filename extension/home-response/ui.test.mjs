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
test('preloads named map centres before preview and reorders without changing selection',async()=>{
 const oldFetch=window.fetch,oldL=window.L,tooltips=[],clicks=[],requests=[];
 const layer=()=>({addTo(){return this;},bindTooltip(label){tooltips.push(label);return this;},on(name,fn){clicks.push(fn);return this;}});
 window.L={map:()=>({setView(){return this;},on(){},invalidateSize(){},remove(){},fitBounds(){}}),tileLayer:layer,layerGroup:()=>({...layer(),clearLayers(){}}),circleMarker:layer,geoJSON:()=>({...layer(),getBounds:()=>[]})};
 window.fetch=async url=>{requests.push(new URL(url).pathname);return {ok:true,url:String(url),text:async()=>JSON.stringify(String(url).endsWith('/api/credits')?{user_id:1}:{result:[{id:11,building_type:7,caption:'A distant centre',longitude:-1,latitude:54},{id:12,building_type:7,caption:'<b>Near centre</b>',longitude:-3.01,latitude:54}]})};};
 const grid=document.createElement('div');document.body.append(grid);mount(grid);grid.querySelector('button').click();
 const original=globalThis.fetch;
 try{await new Promise(r=>setTimeout(r,10));const select=document.querySelector('[data-dispatch]');assert.equal(select.options.length,3);assert.ok(requests.includes('/api/v2/buildings'));assert.equal(document.querySelector('[data-build]').disabled,true);assert.ok(tooltips.some(t=>t.textContent==='<b>Near centre</b>'&&t.children.length===0));
 select.value='11';globalThis.fetch=async()=>({ok:true,json:async()=>[{display_name:'City',lon:-3,lat:54,geojson:{type:'Polygon',coordinates:[[[-3.1,53.9],[-2.9,53.9],[-2.9,54.1],[-3.1,54.1],[-3.1,53.9]]]}}]});
 document.querySelector('[data-city]').value='City';await document.querySelector('[data-search]').onclick();document.querySelector('[data-places]').value='0';await document.querySelector('[data-places]').onchange();
 assert.equal(select.options[0].value,'12');assert.match(select.options[0].textContent,/nearest/);assert.equal(select.value,'11');clicks.at(-2)();assert.equal(select.value,'12');
 }finally{globalThis.fetch=original;document.querySelector('[data-close]').click();grid.remove();window.fetch=oldFetch;window.L=oldL;}
});
