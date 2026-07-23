#!/usr/bin/env node
'use strict';
const fs = require('node:fs');
const path = require('node:path');
const vm = require('node:vm');
const root = path.resolve(__dirname, '..', '..');
const source = fs.readFileSync(path.join(root, 'src', 'MissionChief_Map_Command_Toolkit.user.js'), 'utf8');
const start = source.indexOf('    function operationalRequirementsCandidateVisible(');
const end = source.indexOf('    function operationalRequirementsRuntimeCatalog(', start);
if (start < 0 || end <= start) throw new Error('Issue #458 source resolver block is missing');
class Node {
  constructor({id='', text='', visible=true, cls='', attrs={}, mission=null, toolkit=false}={}) { Object.assign(this,{id,textContent:text,visible,className:cls,attrs,mission,toolkit,groups:[],isConnected:true,hidden:false,parentNode:{},parentElement:null,ownerDocument:null}); }
  getAttribute(name){ return this.attrs[name] ?? null; }
  setAttribute(name,value){ this.attrs[name]=String(value); }
  getBoundingClientRect(){ return {width:this.visible?300:0,height:this.visible?60:0}; }
  getClientRects(){ return this.visible?[1]:[]; }
  querySelectorAll(selector){ return selector==='[data-requirement-type]'?this.groups:[]; }
  querySelector(selector){ return selector==='[data-requirement-type]'?(this.groups[0]||null):null; }
  closest(selector){
    if(selector==='[data-mcms-operational-suite="requirements"]') return this.toolkit?this:null;
    if(selector.includes('#mission-form')||selector.includes('[data-mission-id]')) return this.mission;
    if(selector.includes('[id="missing_text"]')&&this.id==='missing_text') return this;
    if(selector.includes('.alert-missing-vehicles')&&this.className.includes('alert-missing-vehicles')) return this;
    return null;
  }
  set innerHTML(value){
    this.groups=Array.from(String(value).matchAll(/data-requirement-type="([^"]+)"[^>]*>(?:<b>([^<]*)<\/b>)?\s*([^<]*)/giu)).map(match=>{
      const group=new Node({text:`${match[2]||''} ${match[3]||''}`.trim(),visible:false,attrs:{'data-requirement-type':match[1]}});
      group.querySelector=selector=>selector==='b'&&match[2]?new Node({text:match[2]}):null;
      group.ownerDocument=this.ownerDocument;
      return group;
    });
    this.textContent=this.groups.map(group=>group.textContent).join(' ');
  }
}
const mission=visible=>new Node({id:'mission-form',visible});
function doc({native=[],carriers=[],groups=[],missionRoot=mission(true)}={}){
  const value={native,carriers,groups,missionRoot,defaultView:{getComputedStyle(node){return {display:node.visible?'block':'none',visibility:'visible'};}},querySelectorAll(selector){if(selector==='[id="missing_text"]')return this.native;if(selector==='[data-requirement-type]')return this.groups;if(selector==='.alert-missing-vehicles[data-raw-html]')return this.carriers;return[];},querySelector(selector){return selector.includes('#mission-form')?this.missionRoot:null;},createElement(){const node=new Node({visible:false});node.ownerDocument=value;return node;}};
  [...native,...carriers,...groups,missionRoot].filter(Boolean).forEach(node=>node.ownerDocument=value);
  return value;
}
const sandbox={console,operationalRequirementNormaliseText:value=>String(value||'').replace(/\s+/gu,' ').trim()};
sandbox.globalThis=sandbox;vm.createContext(sandbox);
vm.runInContext(`${source.slice(start,end)}\nglobalThis.resolveSource=operationalRequirementsResolveSource;`,sandbox);
const active=mission(true), empty=new Node({id:'missing_text',visible:true,mission:active});
const populated=new Node({id:'missing_text',visible:false,mission:active,text:'Vehicles needed 2 Fire Engines'});populated.groups.push(new Node({text:populated.textContent,attrs:{'data-requirement-type':'vehicles'}}));
let selected=sandbox.resolveSource(doc({native:[empty,populated],missionRoot:active}));
if(selected.root!==populated||selected.suppressed)throw new Error('populated duplicate did not outrank empty placeholder');
const staleMission=mission(false),stale=new Node({id:'missing_text',visible:false,mission:staleMission,text:'9 Old Fire Engines'});stale.groups.push(new Node({text:stale.textContent,attrs:{'data-requirement-type':'vehicles'}}));
selected=sandbox.resolveSource(doc({native:[stale,populated],missionRoot:active}));if(selected.root!==populated)throw new Error('active mission source did not outrank stale source');
const live=new Node({visible:true,cls:'alert alert-missing-vehicles',mission:active,attrs:{'data-raw-html':'<div data-requirement-type="vehicles"><b>Needed</b> 2 Fire Engines</div>'}});
selected=sandbox.resolveSource(doc({native:[empty],carriers:[live],missionRoot:active}));if(!selected?.suppressed||selected.kind!=='lssm-live')throw new Error('visible LSSM equivalent was not suppressed');
const hidden=new Node({visible:false,cls:'alert alert-missing-vehicles',mission:active,attrs:{'data-raw-html':'<div data-requirement-type="vehicles"><b>Needed</b> 3 Fire Engines</div>'}});
selected=sandbox.resolveSource(doc({native:[empty],carriers:[hidden],missionRoot:active}));if(selected?.kind!=='lssm-raw'||selected.groupedCount!==1||selected.suppressed)throw new Error('hidden LSSM raw evidence was not recovered');
const toolkit=new Node({id:'missing_text',visible:true,mission:active,toolkit:true,text:'99 Fake Requirements'});toolkit.groups.push(new Node({text:toolkit.textContent,attrs:{'data-requirement-type':'vehicles'}}));
selected=sandbox.resolveSource(doc({native:[toolkit,populated],missionRoot:active}));if(selected.root!==populated)throw new Error('Toolkit-owned markup contaminated source discovery');
const delayed=doc({native:[empty],missionRoot:active});selected=sandbox.resolveSource(delayed);if(selected.root!==empty||selected.raw||selected.groupedCount)throw new Error('empty placeholder was not retained as safe pending');delayed.native.push(populated);if(sandbox.resolveSource(delayed).root!==populated)throw new Error('later replacement source was not selected');
if(!source.includes('context.boundRequirementSource === sourceFingerprint'))throw new Error('observer source-rebind contract is missing');
if(!source.includes("element.querySelector?.('b')?.textContent"))throw new Error('native requirement heading removal is missing');
console.log('Issue #458 authoritative requirement-source runtime passed.');
