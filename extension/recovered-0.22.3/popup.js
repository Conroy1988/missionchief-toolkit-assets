// Use one request with both response conventions. Some WebExtension hosts expose
// a Promise but deliver the actual value only to the callback. Never resend:
// callers include writes and job operations that must not be duplicated.
function sendRuntimeMessage(message) {
  return new Promise((resolve,reject)=>{
    let settled=false;
    const finish=(error,value)=>{
      if(settled)return;settled=true;clearTimeout(timer);
      if(error)reject(error);else resolve(value);
    };
    const failure=code=>Object.assign(new Error(code),{code});
    const timer=setTimeout(()=>finish(failure('MESSAGE_TIMEOUT')),25000);
    try {
      const pending=chrome.runtime.sendMessage(message,value=>{
        const error=chrome.runtime.lastError;
        if(error){finish(failure('MESSAGE_CONNECTION_FAILED'));return;}
        if(value===undefined||value===null){finish(failure('MESSAGE_EMPTY_CALLBACK'));return;}
        finish(null,value);
      });
      if(pending&&typeof pending.then==='function'){
        pending.then(value=>{
          // An empty Promise resolution is not evidence that the callback is done.
          if(value!==undefined&&value!==null)finish(null,value);
        },()=>finish(failure('MESSAGE_CONNECTION_FAILED')));
      }
    } catch {finish(failure('MESSAGE_CONNECTION_FAILED'));}
  });
}

const $=id=>document.getElementById(id);
let tabId=null,snapshot=null,poll=null,refreshPromise=null;
const labels={'userscript-active':'Disable the Toolkit userscript, then reload.',started:'Toolkit is running.','already-started':'Toolkit is running.',off:'Toolkit is off in this tab.',error:'Toolkit could not start. Reload the game tab.','style-error':'Toolkit styles could not load. Reload the game tab.'};
const startupLabels={DOCUMENT_CHANGED:'The game page changed during startup. Reload this tab.',MESSAGE_TIMEOUT:'The browser did not deliver a background reply. Export diagnostics.',MESSAGE_CONNECTION_FAILED:'The browser could not connect to the extension background. Export diagnostics.',MESSAGE_EMPTY_CALLBACK:'The browser delivered an empty background reply. Export diagnostics.',STARTUP_TIMEOUT:'Browser startup did not respond within 15 seconds. Export diagnostics.',INVALID_STARTUP_RESPONSE:'Browser returned no valid startup response. Export diagnostics.',INJECTION_NO_RESULT:'Browser returned no page-injection result. Export diagnostics.',MISSING_DOCUMENT_ID:'Browser did not supply the document identity required by Toolkit.',UNSUPPORTED_PAGE:'Toolkit could not verify this game tab.',BACKGROUND_START_FAILED:'Toolkit background startup failed. Export diagnostics.',BACKGROUND_CONNECTION_FAILED:'Could not connect to the extension background. Export diagnostics.'};
function refresh(){if(refreshPromise)return refreshPromise;refreshPromise=refreshNow().finally(()=>{refreshPromise=null;});return refreshPromise;}
async function refreshNow(){
  if(!tabId)return;
  const [diagnostics,status,probe]=await Promise.all([chrome.tabs.sendMessage(tabId,{op:'diagnostics'}).catch(()=>null),sendRuntimeMessage({op:'status',tabId}).catch(error=>({ok:false,code:error.code})),sendRuntimeMessage({op:'ping'}).catch(error=>({ok:false,code:error.code}))]);
  snapshot={backgroundProbe:probe?.value?.protocol===1?'responsive':(probe?.code||'invalid-response'),extensionVersion:chrome.runtime.getManifest().version,tab:diagnostics,backgroundStatus:status?.ok===true?'responsive':(status?.code||'invalid-response'),jobs:status?.value?.jobs||[]};
  $('status').textContent=diagnostics?.error||(diagnostics?.startupDetail?`${diagnostics.startupStage}: ${diagnostics.startupDetail}`:null)||startupLabels[diagnostics?.startupCode]||(diagnostics?.state==='starting'?(diagnostics?.bootPhase==='waiting-page'?'Waiting for the game page to finish loading…':'Waiting for extension startup…'):null)||labels[diagnostics?.state]||'Reload MissionChief to connect this extension.';
  document.body.dataset.error=String(Boolean(diagnostics?.error||diagnostics?.state==='error'||diagnostics?.state==='style-error'));
  $('background-state').textContent=snapshot.backgroundProbe==='responsive'?'Responsive':'Unavailable — export diagnostics';
  $('game-state').textContent=['started','already-started'].includes(diagnostics?.state)?'Connected':diagnostics?.state==='off'?'Disabled':diagnostics?.state==='userscript-active'?'Duplicate Toolkit detected':diagnostics?.state==='starting'?'Starting':'Not connected';
  $('health').classList.toggle('ready',['started','already-started'].includes(diagnostics?.state));
  $('health').ariaLabel=diagnostics?.state||'Not connected';
  $('saving').textContent=diagnostics?.saving==='saving'?'Saving…':diagnostics?.saving==='error'?'Unsaved':diagnostics?.saving==='saved'?'Saved':'Unknown';
  $('startup').textContent=Number.isFinite(diagnostics?.bootMs)?`${diagnostics.bootMs} ms`:'—';
  $('reads').textContent=String(diagnostics?.requests??0);
  $('reload').disabled=diagnostics?.saving==='saving'||diagnostics?.saving==='error';
  $('workspace').disabled=!['started','already-started'].includes(diagnostics?.state);
  $('settings').disabled=!['started','already-started'].includes(diagnostics?.state);
  const jobs=snapshot.jobs.filter(j=>j.tabId===tabId).sort((a,b)=>b.updated-a.updated);
  const active=jobs.find(j=>j.state==='running'),recent=active||jobs[0];
  $('job').textContent=recent?`${({startTransportSweep:'Patient transport sweep',scanTransportSweepQueue:'Patient transport scan',startDispatchRecruitment:'Staff recruitment',scanDispatchRecruitmentStations:'Recruitment scan',startAllianceCourses:'Training courses',scanAllianceCourseQueue:'Academy scan',startExpansionPlanner:'Building expansions',scanExpansionPlanner:'Expansion scan',startStationIconCopier:'Copy station icons',scanStationIconTargets:'Icon scan'})[recent.operation]||'Operations task'} · ${({complete:'Finished',running:'Running',cancelled:'Stopped',interrupted:'Interrupted','check-required':'Needs checking',partial:'Partly completed',error:'Failed'})[recent.state]||recent.state}${recent.total?` · ${recent.checked}/${recent.total} checked · ${recent.found} found`:''}`:'No active task';
  $('progress').max=recent?.total||1;$('progress').value=recent?.checked||0;
  $('cancel').disabled=!active;$('recovery').hidden=!['interrupted','check-required','error','partial','cancelled'].includes(recent?.state);
  $('reload').disabled=$('reload').disabled||Boolean(active);
}
async function initialise(){
  const manifest=chrome.runtime.getManifest();$('version').textContent=manifest.version_name||`Extension ${manifest.version} · Toolkit 10.18.1`;
  const setup=await chrome.storage.local.get('setupCompleted');$('setup').open=setup.setupCompleted!==true;
  $('setup-done').onclick=async()=>{try{await chrome.storage.local.set({setupCompleted:true});$('setup').open=false;}catch{$('status').textContent='Setup could not be saved. Try again.';}};
  $('enabled').checked=Boolean((await chrome.storage.local.get('enabled')).enabled);
  $('enable-state').textContent=$('enabled').checked?'Enabled':'Disabled';
  const [tab]=await chrome.tabs.query({active:true,currentWindow:true});
  let url;try{url=new URL(tab?.url||'https://invalid.example');}catch{url=new URL('https://invalid.example');}
  if(url.protocol!=='https:'||!(url.hostname==='missionchief.co.uk'||url.hostname.endsWith('.missionchief.co.uk'))){$('status').textContent='Open MissionChief UK to use your Toolkit.';$('background-state').textContent='Not checked on this page';$('game-state').textContent='Unsupported page';for(const id of ['reload','settings','enabled','workspace','cancel','export'])$(id).disabled=true;return;}
  tabId=tab.id;
  $('reload').onclick=async()=>{await refresh();if($('reload').disabled)return;await chrome.storage.local.set({enabled:$('enabled').checked});await chrome.tabs.reload(tabId);window.close();};
  $('workspace').onclick=async()=>{try{await chrome.tabs.sendMessage(tabId,{op:'control',action:'workspace'});window.close();}catch{$('status').textContent='The game tab is not responding. Reload it, then reopen Toolkit.';}};
  $('settings').onclick=async()=>{try{await chrome.tabs.sendMessage(tabId,{op:'control',action:'settings'});window.close();}catch{$('status').textContent='The game tab is not responding. Reload it, then reopen Toolkit.';}};
  $('cancel').onclick=async()=>{await chrome.tabs.sendMessage(tabId,{op:'control',action:'cancel'});await refresh();};
  $('export').onclick=()=>{
    // Allowlist status plus worker-sanitised startup detail; no settings or page data.
    const report={version:snapshot?.extensionVersion,backgroundStatus:snapshot?.backgroundStatus,backgroundProbe:snapshot?.backgroundProbe,tab:snapshot?.tab?Object.fromEntries(['state','saving','bootPhase','startupCode','startupStage','startupDetail','compatibility','readyState','bootMs','messages','storageBatches','requests','cacheHits','sharedReads'].map(k=>[k,snapshot.tab[k]])):null,
      jobs:(snapshot?.jobs||[]).map(j=>({type:j.type,state:j.state,checked:j.checked,total:j.total,found:j.found}))};
    const url=URL.createObjectURL(new Blob([JSON.stringify(report,null,2)],{type:'application/json'}));
    const a=document.createElement('a');a.href=url;a.download='Toolkit-diagnostics.json';a.click();setTimeout(()=>URL.revokeObjectURL(url),1000);
  };
  await refresh();poll=setInterval(()=>{if(!document.hidden)refresh().catch(()=>{});},2000);
}
window.addEventListener('pagehide',()=>clearInterval(poll));
initialise().catch(error=>{$('status').textContent=error.message;});
