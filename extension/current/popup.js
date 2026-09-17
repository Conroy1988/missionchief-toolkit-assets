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
let tabId=null,poll=null,refreshPromise=null,busy=false;
async function refresh(){
 if(refreshPromise)return refreshPromise;
 refreshPromise=(async()=>{
  const [diagnostics,status]=await Promise.all([chrome.tabs.sendMessage(tabId,{op:'diagnostics'}).catch(()=>null),sendRuntimeMessage({op:'status',tabId}).catch(()=>null)]);
  const running=(status?.value?.jobs||[]).some(j=>j.tabId===tabId&&j.state==='running');
  const unsafe=diagnostics?.saving==='saving'||diagnostics?.saving==='error';
  $('reload').disabled=busy||unsafe||running||!status?.ok;
  const ready=['started','already-started'].includes(diagnostics?.state);
  $('health').classList.toggle('ready',ready);$('health').setAttribute('aria-label',ready?'Toolkit running':'Toolkit not running');
  $('status').textContent=running?'A task is running. Finish or stop it in Operations before reloading.':unsafe?'Wait for your settings to save before reloading.':!status?.ok?'Cannot connect to the extension. Reopen this popup or contact Support.':ready?'Toolkit is running.':'Apply your choice and reload the game to connect.';
  if(diagnostics?.state==='userscript-active')$('status').textContent='Disable the old Toolkit userscript, then reload.';
  if(diagnostics?.state==='off')$('status').textContent='Toolkit is off. Turn it on, then apply and reload.';
 })();
 try{await refreshPromise;}finally{refreshPromise=null;}
}
async function initialise(){
 $('version').textContent=`Version ${chrome.runtime.getManifest().version}`;
 $('enabled').checked=Boolean((await chrome.storage.local.get('enabled')).enabled);
 const [tab]=await chrome.tabs.query({active:true,currentWindow:true});let url;
 try{url=new URL(tab?.url||'');}catch{}
 if(!url||url.protocol!=='https:'||!(url.hostname==='missionchief.co.uk'||url.hostname.endsWith('.missionchief.co.uk'))){$('status').textContent='Open MissionChief UK to turn on or reload the Toolkit.';return;}
 tabId=tab.id;$('enabled').disabled=false;
 $('enabled').onchange=()=>{$('status').textContent='Choose Apply & reload to save this change.';};
 $('reload').onclick=async()=>{if(busy)return;try{await refresh();if($('reload').disabled)return;busy=true;$('enabled').disabled=true;$('reload').disabled=true;await chrome.storage.local.set({enabled:$('enabled').checked});await chrome.tabs.reload(tabId);window.close();}catch{$('status').textContent='Could not save or reload. Try again, or contact Support.';}finally{busy=false;$('enabled').disabled=false;}};
 await refresh();poll=setInterval(()=>{if(!document.hidden&&!busy)refresh().catch(()=>{});},2000);
}
window.addEventListener('pagehide',()=>clearInterval(poll));
initialise().catch(()=>{$('status').textContent='Toolkit could not connect. Reopen this popup or contact Support.';});
