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

// Runs in the isolated content world. Only read-only mission HTML is exposed.
function createGameReader(fetcher = fetch) {
  const inflight=new Map(), cache=new Map(), controllers=new Set();
  const metrics={requests:0,cacheHits:0,sharedReads:0};let cacheBytes=0;
  async function read(message) {
    if (!/^\d{1,15}$/.test(String(message.missionId))) throw Error('Invalid mission.');
    const key=`${message.missionId}:${message.mode==='full'?'full':'ajax'}`;
    if (!message.fresh && cache.get(key)?.expires>Date.now()) {metrics.cacheHits++;return cache.get(key).result;}
    if (inflight.has(key)) {if(message.fresh){await inflight.get(key).catch(()=>{});return read(message);}metrics.sharedReads++;return inflight.get(key);}
    if (inflight.size>=4) throw Error('Too many mission reads.');
    const promise=(async()=>{
      const controller=new AbortController();controllers.add(controller);
      const timer=setTimeout(()=>controller.abort(),15000);
      try {
        metrics.requests++;
        const response=await fetcher(`/missions/${message.missionId}`,{method:'GET',credentials:'same-origin',cache:'no-store',signal:controller.signal,
          headers:message.mode==='full'?{Accept:'text/html'}:{Accept:'text/html','X-Requested-With':'XMLHttpRequest'}});
        if (!response.ok) throw Error(`Mission read failed (${response.status}).`);
        const url=new URL(response.url,location.origin);
        if (url.origin!==location.origin || !new RegExp(`^/missions/${message.missionId}/?$`).test(url.pathname)) throw Error('Mission session expired.');
        const reader=response.body.getReader(),decoder=new TextDecoder();let size=0,html='';
        for(;;) {const {done,value}=await reader.read();if(done)break;size+=value.length;if(size>4*1024*1024){await reader.cancel();throw Error('Mission response too large.');}html+=decoder.decode(value,{stream:true});}
        html+=decoder.decode();
        if (!/missionH1|mission_vehicle_at_mission|mission_patient/.test(html)) throw Error('Incomplete mission page.');
        const result={html,url:url.href,status:response.status};
        if(size<=1024*1024){
          cacheBytes-=cache.get(key)?.bytes||0;cache.set(key,{result,bytes:size,expires:Date.now()+4000});cacheBytes+=size;
          while(cache.size>16||cacheBytes>4*1024*1024){const oldest=cache.keys().next().value;cacheBytes-=cache.get(oldest).bytes;cache.delete(oldest);}
        }
        return result;
      } finally {clearTimeout(timer);controllers.delete(controller);}
    })();
    inflight.set(key,promise);
    try{return await promise;}finally{inflight.delete(key);}
  }
  return {read,metrics,clear(){cache.clear();cacheBytes=0;},cancel(){for(const c of controllers)c.abort();cache.clear();cacheBytes=0;}};
}

(() => {
  const CHANNEL='mcms-extension-pilot-v1', reader=createGameReader();
  globalThis.__MCMS_COMPAT_BRIDGE__=true;
  const documentToken=crypto.randomUUID();
  const sendToBackground=message=>sendRuntimeMessage({...message,documentToken});
  const metrics={bootStarted:performance.now(),messages:0,storageBatches:0};
  let booted=false,active=false;
  let bootPhase='waiting-page',startupCode='',startupStage='',startupDetail='',readinessTimer=null;
  const post=(kind,payload)=>window.postMessage({channel:CHANNEL,direction:kind,...payload},location.origin);
  window.addEventListener('message', async event => {
    if(event.source!==window||event.origin!==location.origin||event.data?.channel!==CHANNEL||event.data?.direction!=='request')return;
    const payload=event.data.payload;
    if(!payload||typeof payload.id!=='string'||payload.id.length>100)return;
    if(!['accountOpen','accountSummary','discordReceipt','discordPost','discordDraft','discordOpen','request','abort','saveBatch','module','job','jobsList','jobsFocus','gameRead','cancelReads','clearReadCache','metrics'].includes(payload.op))return;
    metrics.messages++;
    let response;
    try {
      if(payload.op==='gameRead'&&!active)throw Error('Toolkit is disabled. Reload the game tab.');
      if(payload.op==='gameRead')response={ok:true,value:await reader.read(payload)};
      else if(payload.op==='clearReadCache'){reader.clear();response={ok:true,value:true};}
      else if(payload.op==='cancelReads'){reader.cancel();response={ok:true,value:true};}
      else if(payload.op==='metrics')response={ok:true,value:{...metrics,...reader.metrics}};
      else {if(payload.op==='saveBatch')metrics.storageBatches++;response=await sendToBackground(payload);}
    } catch(error){response={ok:false,error:error.message||'Extension connection lost. Reload this tab.'};}
    post('response',{id:payload.id,response});
  });
  chrome.storage.onChanged.addListener(async(changes,area)=>{
    if(area!=='local')return;
    if(changes.enabled?.newValue===false){active=false;reader.cancel();}
    const prefix=`settings:v2:${location.origin}:`,entries=[];
    for(const [key,change] of Object.entries(changes)){
      if(!key.startsWith(prefix))continue;
      const suffix=key.slice(prefix.length),colon=suffix.indexOf(':');
      if(colon<0)continue;
      if(change.newValue?.sharded){
        const all=await chrome.storage.local.get(null),state={};
        for(const [k,v] of Object.entries(all))if(k.startsWith(prefix+'state:')&&!v.deleted)state[k.slice((prefix+'state:').length)]=v.value;
        entries.push({area:'ls',key:suffix.slice(colon+1),value:JSON.stringify(state),revision:all[key].revision});
      }else entries.push({area:suffix.slice(0,colon),key:suffix.slice(colon+1),...change.newValue});
    }
    if(entries.length)post('settings',{entries});
  });
  chrome.runtime.onMessage.addListener((message,_sender,respond)=>{
    if(message.op==='compatibilityPrepare'){respond({readyState:document.readyState,worker:typeof Worker==='function',blob:typeof Blob==='function',storageEvents:Boolean(chrome.storage.onChanged),runtimeMessages:true});return;}
    if(message.op==='compatibilityClear'){document.documentElement.removeAttribute('data-mcms-compat-result');respond(true);return;}
    if(message.op==='compatibilityRead'){
      try{const r=JSON.parse(document.documentElement.getAttribute('data-mcms-compat-result'));respond(r?{executed:r.executed===true,bridgeWorld:r.bridgeWorld===true,...(typeof r.argsValid==='boolean'?{argsValid:r.argsValid}:{})}:null);}catch{respond(null);}return;
    }
    if(message.op==='compatibilityAssets'){
      const link=document.createElement('link');link.rel='stylesheet';link.href=chrome.runtime.getURL('compatibility-probe.css');
      let done=false;const finish=()=>{if(done)return;done=true;clearTimeout(timer);const css=getComputedStyle(document.documentElement).getPropertyValue('--mcms-compatibility-probe').trim()==='available';link.remove();respond({packagedStylesheet:css});};
      const timer=setTimeout(finish,1500);link.onload=finish;link.onerror=finish;document.documentElement.append(link);return true;
    }
    if(message.op==='injectionReceipt'&&/^[0-9a-f-]{36}$/i.test(message.receipt||'')){
      const key='data-mcms-receipt-'+message.receipt;
      const raw=document.documentElement.getAttribute(key);document.documentElement.removeAttribute(key);
      try{respond(raw?JSON.parse(raw):null);}catch{respond(null);}return;
    }
    if(message.op==='leaseProbe'){respond(!message.documentToken||message.documentToken===documentToken);return;}
    if(message.op==='diagnostics'){
      maybeBoot();
      const d=document.documentElement.dataset;
      respond({bootPhase,startupCode,startupStage,startupDetail,readyState:document.readyState,state:d.mcmsExtensionState||'starting',saving:d.mcmsExtensionSaving||'saved',error:d.mcmsExtensionStorageError||'',reloadRequired:d.mcmsExtensionReloadRequired==='true',...metrics,...reader.metrics});
    }else if(message.op==='control'&&['settings','cancel','workspace'].includes(message.action)){post('control',{action:message.action});respond({ok:true});}
  });
  const boot=()=>{
    if(booted)return;booted=true;
    document.documentElement.setAttribute('data-mcms-extension-document',documentToken);
    clearInterval(readinessTimer);
    bootPhase='waiting-background';
    document.documentElement.dataset.mcmsExtensionState='starting';
    const timeout=setTimeout(()=>{
      bootPhase='background-timeout';startupCode='STARTUP_TIMEOUT';
      document.documentElement.dataset.mcmsExtensionState='error';
    },15000);
    // Retain the original request: a late response is useful, but never replay startup.
    Promise.resolve().then(()=>sendToBackground({op:'start',id:'startup'})).then(result=>{
      if(!result||typeof result.ok!=='boolean'){
        bootPhase='failed';startupCode='INVALID_STARTUP_RESPONSE';
        document.documentElement.dataset.mcmsExtensionState='error';return;
      }
      startupStage=result.startupStage||'';startupDetail=result.startupDetail||'';
      const state=result.value?.state;
      if(result.ok&&!['off','started','already-started','userscript-active'].includes(state)){
        bootPhase='failed';startupCode='INJECTION_NO_RESULT';
        document.documentElement.dataset.mcmsExtensionState='error';return;
      }
      document.documentElement.dataset.mcmsExtensionState=result.ok?state:'error';
      active=result.ok&&['started','already-started'].includes(state);
      bootPhase=result.ok?'complete':'failed';
      startupCode=result.ok?'':(['MISSING_DOCUMENT_ID','UNSUPPORTED_PAGE','DOCUMENT_CHANGED'].includes(result.code)?result.code:'BACKGROUND_START_FAILED');
    }).catch(error=>{
      bootPhase='failed';startupCode=['MESSAGE_TIMEOUT','MESSAGE_CONNECTION_FAILED','MESSAGE_EMPTY_CALLBACK'].includes(error?.code)?error.code:'BACKGROUND_CONNECTION_FAILED';
      document.documentElement.dataset.mcmsExtensionState='error';
    }).finally(()=>{clearTimeout(timeout);metrics.bootMs=Math.round(performance.now()-metrics.bootStarted);if(bootPhase==='failed'){metrics.compatibility={state:'running'};sendToBackground({op:'compatibility',id:'compatibility'}).then(r=>{metrics.compatibility=r?.ok?r.value:{state:'unavailable'};}).catch(()=>{metrics.compatibility={state:'unavailable'};});}});
  };
  const maybeBoot=()=>{if(document.readyState!=='loading')boot();};
  document.addEventListener('DOMContentLoaded',boot,{once:true});
  document.addEventListener('readystatechange',maybeBoot);
  window.addEventListener('pageshow',maybeBoot);
  // Some extension hosts miss the DOMContentLoaded notification. Poll readiness briefly;
  // popup diagnostics also rechecks it, without injecting into a still-loading document.
  readinessTimer=setInterval(maybeBoot,250);
  setTimeout(()=>clearInterval(readinessTimer),30000);
  maybeBoot();
  window.addEventListener('pagehide',()=>{clearInterval(readinessTimer);reader.cancel();});
})();
