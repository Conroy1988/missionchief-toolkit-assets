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
