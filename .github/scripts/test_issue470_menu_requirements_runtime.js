#!/usr/bin/env node
'use strict';
const fs = require('node:fs');
const path = require('node:path');
const vm = require('node:vm');
const root = path.resolve(__dirname, '..', '..');
const source = fs.readFileSync(path.join(root, 'src', 'MissionChief_Map_Command_Toolkit.user.js'), 'utf8');
const required = [
  'function toolkitTopLevelDocument(',
  'function toolkitPrimaryMapElement(',
  "if (!toolkitTopLevelDocument(document)) return true;",
  "element.style.setProperty('display', 'none', 'important')",
  'state.commandBarOpen = opening;',
  'function operationalRequirementsMissionKey(',
  'function operationalRequirementsEnsureRemoteSource(',
  'fetchSameOriginDocument(`/missions/${encodeURIComponent(key)}`)',
  ".alert-missing-vehicles[data-raw-html]",
  "doc.querySelectorAll('[data-raw-html]')",
  'context.boundRequirementMissionKey === missionKey',
  'panel.dataset.missionKey = missionKey'
];
for (const token of required) if (!source.includes(token)) throw new Error(`Missing Issue #470 contract token: ${token}`);
const toggleStart = source.indexOf('    function toggleCommandBar()');
const toggleEnd = source.indexOf('    function handleMapVisibilityToggle(', toggleStart);
const toggle = source.slice(toggleStart, toggleEnd);
if (!(toggle.indexOf('state.commandBarOpen = opening;') < toggle.indexOf('saveState();') && toggle.indexOf('saveState();') < toggle.indexOf('updateUI();'))) throw new Error('Command-bar state is not committed before UI reconciliation');
if (/commandBarAnimationTimer\s*=\s*runtimeSetTimeout/u.test(toggle)) throw new Error('Command-bar collapse still depends on a delayed state commit');
const resolverStart = source.indexOf('    function operationalRequirementsCandidateVisible(');
const resolverEnd = source.indexOf('    function operationalRequirementsRuntimeCatalog(', resolverStart);
if (resolverStart < 0 || resolverEnd <= resolverStart) throw new Error('Requirements resolver block is missing');
class Node {
  constructor({id='', text='', visible=true, cls='', attrs={}, mission=null, toolkit=false}={}) {
    Object.assign(this,{id,textContent:text,visible,className:cls,attrs,mission,toolkit,groups:[],isConnected:true,hidden:false,parentNode:{},parentElement:null,ownerDocument:null,firstElementChild:null});
  }
  getAttribute(name){ return this.attrs[name] ?? null; }
  setAttribute(name,value){ this.attrs[name]=String(value); }
  matches(selector){ return selector === '.alert-missing-vehicles' && this.className.includes('alert-missing-vehicles'); }
  getBoundingClientRect(){ return {width:this.visible?300:0,height:this.visible?60:0}; }
  getClientRects(){ return this.visible?[1]:[]; }
  querySelectorAll(selector){ return selector==='[data-requirement-type]'?this.groups:[]; }
  querySelector(selector){
    if(selector==='[data-requirement-type]') return this.groups[0]||null;
    if(selector.includes('input[name="mission_id"]')) return null;
    if(selector.includes('form[action*="/missions/"]')) return null;
    return null;
  }
  closest(selector){
    if(selector==='[data-mcms-operational-suite="requirements"]') return this.toolkit?this:null;
    if(selector.includes('#mission-form')||selector.includes('.mission-window')) return this.mission;
    if(selector.includes('[id="missing_text"]')&&this.id==='missing_text') return this;
    if(selector.includes('.alert-missing-vehicles')&&this.className.includes('alert-missing-vehicles')) return this;
    return null;
  }
}
const mission = new Node({id:'mission-form',visible:true,attrs:{'data-mission-id':'42'}});
const empty = new Node({id:'missing_text',visible:true,mission});
mission.firstElementChild=empty;
function attach(doc,nodes){ for(const node of nodes){ if(!node)continue; node.ownerDocument=doc; for(const group of node.groups||[]) group.ownerDocument=doc; } }
function makeDoc({pathname='/missions/42',native=[empty],carriers=[],groups=[],missionRoot=mission}={}) {
  const value={
    native,carriers,groups,missionRoot,
    baseURI:`https://www.missionchief.co.uk${pathname}`,
    URL:`https://www.missionchief.co.uk${pathname}`,
    defaultView:{location:{pathname,href:`https://www.missionchief.co.uk${pathname}`},getComputedStyle(node){return{display:node.visible?'block':'none',visibility:'visible'};}},
    querySelectorAll(selector){
      if(selector==='[id="missing_text"]')return this.native;
      if(selector==='[data-requirement-type]')return this.groups;
      if(selector==='.alert-missing-vehicles[data-raw-html]')return this.carriers.filter(node=>node.matches('.alert-missing-vehicles'));
      if(selector==='[data-raw-html]')return this.carriers;
      if(selector.includes('#mission-form')||selector.includes('.mission-window'))return [this.missionRoot];
      return [];
    },
    querySelector(selector){
      if(selector.includes('#mission-form[action'))return null;
      if(selector.includes('input[name="mission_id"]'))return null;
      if(selector.includes('#mission-form')||selector.includes('.mission-window'))return this.missionRoot;
      return null;
    },
    createRange(){return{createContextualFragment(html){
      const raw=String(html||'');
      const type=raw.match(/data-requirement-type="([^"]+)"/iu)?.[1]||'';
      const heading=raw.match(/<b>([^<]*)<\/b>/iu)?.[1]||'';
      const plain=raw.replace(/<[^>]+>/gu,' ').replace(/\s+/gu,' ').trim();
      const fragment=new Node({visible:false,text:plain});fragment.ownerDocument=value;
      if(type){const group=new Node({visible:false,text:plain,attrs:{'data-requirement-type':type}});group.ownerDocument=value;group.querySelector=selector=>selector==='b'&&heading?new Node({text:heading}):null;fragment.groups=[group];}
      return fragment;
    }}}
  };
  attach(value,[...native,...carriers,...groups,missionRoot]);
  return value;
}
const fetchedMission=new Node({id:'mission-form',visible:true,attrs:{'data-mission-id':'42'}});
const fetchedRoot=new Node({id:'missing_text',visible:true,mission:fetchedMission,text:'Needed 3 Fire Engines'});
const fetchedGroup=new Node({text:'Needed 3 Fire Engines',attrs:{'data-requirement-type':'vehicles'}});
fetchedGroup.querySelector=selector=>selector==='b'?new Node({text:'Needed'}):null;
fetchedRoot.groups=[fetchedGroup];
const fetchedDoc=makeDoc({pathname:'/missions/42',native:[fetchedRoot],groups:[fetchedGroup],missionRoot:fetchedMission});
let fetchCount=0;
const sandbox={
  console,
  runtime:{destroyed:false},
  fetchSameOriginDocument:async path=>{fetchCount+=1;if(String(path)!=='/missions/42')throw new Error('wrong mission URL');return{doc:fetchedDoc,url:'https://www.missionchief.co.uk/missions/42'};},
  scheduleOperationalSuiteScan(){},
  pageWindow:{location:{origin:'https://www.missionchief.co.uk',href:'https://www.missionchief.co.uk/'}},
  operationalRequirementNormaliseText:value=>String(value||'').replace(/\s+/gu,' ').trim(),
  URL,encodeURIComponent,Date,Map,Set,Array,Object,String,Number,RegExp,Promise,setTimeout,globalThis:null
};
sandbox.globalThis=sandbox;
vm.createContext(sandbox);
vm.runInContext(`${source.slice(resolverStart,resolverEnd)}
globalThis.resolveSource=operationalRequirementsResolveSource;
globalThis.remoteCache=operationalRequirementsRemoteCache;
globalThis.missionKey=operationalRequirementsMissionKey;`,sandbox);
(async()=>{
  const doc42=makeDoc();
  let selected=sandbox.resolveSource(doc42);
  if(selected?.root!==empty||selected?.raw)throw new Error('empty live placeholder was not retained while recovery started');
  await new Promise(resolve=>setTimeout(resolve,0));
  await new Promise(resolve=>setTimeout(resolve,0));
  selected=sandbox.resolveSource(doc42);
  if(selected?.kind!=='remote'||selected.root!==fetchedRoot||selected.anchor!==empty||selected.missionKey!=='42')throw new Error('mission-scoped remote requirement evidence was not selected');
  if(fetchCount!==1)throw new Error(`expected one bounded mission recovery request, received ${fetchCount}`);
  const generic=new Node({visible:false,mission,attrs:{'data-raw-html':'<div data-requirement-type="vehicles"><b>Needed</b> 2 Fire Engines</div>'}});
  const genericDoc=makeDoc({native:[empty],carriers:[generic]});
  const raw=sandbox.resolveSource(genericDoc,{includeRemote:false});
  if(raw?.kind!=='raw-html'||raw.groupedCount!==1||raw.suppressed)throw new Error('generic raw requirement carrier was not recovered');
  if(sandbox.missionKey(makeDoc({pathname:'/missions/43',missionRoot:new Node({id:'mission-form',visible:true,attrs:{'data-mission-id':'43'}})}))!=='43')throw new Error('mission identity extraction failed');
  if(!source.includes('// @version      5.0.7')||!source.includes("version: '5.0.7'"))throw new Error('v5.0.7 version metadata is incomplete');
  console.log('Issue #470 menu-state and mission-scoped requirement recovery passed.');
})().catch(error=>{console.error(error);process.exitCode=1;});
