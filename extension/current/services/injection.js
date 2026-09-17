// One browser invocation: never retry script execution, which can mutate the page.
export function executeScript(options) {
  const receipt=options.func?crypto.randomUUID():null;
  if(receipt)options={...options,args:[...(options.args||[]),receipt]};
  const normalise=value=>{
    if(Array.isArray(value))return value;
    if(value&&typeof value==='object'&&(Object.hasOwn(value,'result')||Object.hasOwn(value,'error')))return [value];
    return null;
  };
  const shape=value=>value===null?'null':Array.isArray(value)?'array':typeof value;
  return new Promise((resolve,reject)=>{
    let settled=false,lastShape='no reply';
    const finish=(error,value)=>{
      if(settled)return;settled=true;clearTimeout(timer);
      if(error)reject(error);else resolve(value);
    };
    const timer=setTimeout(()=>finish(Error(`Injection response timed out; last response type: ${lastShape}.`)),25000);
    let checkingReceipt=false;
    const confirmReceipt=()=>{
      if(checkingReceipt||settled)return;checkingReceipt=true;
      if(!receipt){finish(null,[]);return;} // Files are verified by the following startup receipt / module consumer.
      try{
        const target=options.target.documentIds?{documentId:options.target.documentIds[0]}:{frameId:0};
        const confirm=value=>{if(value?.done===true){if(value.error)finish(Error(value.error));else finish(null,[{result:value.result}]);}else finish(Error('Injected script produced no verifiable page receipt.'));};
        const pending=chrome.tabs.sendMessage(options.target.tabId,{op:'injectionReceipt',receipt},target,value=>{
          const error=chrome.runtime.lastError;
          if(error){finish(Error('Could not read the injected script receipt.'));return;}
          confirm(value);
        });
        if(pending&&typeof pending.then==='function')pending.then(value=>{if(value!=null)confirm(value);},()=>finish(Error('Could not read the injected script receipt.')));
      }catch{finish(Error('Could not read the injected script receipt.'));}
    };
    const accept=(value,callback=false)=>{
      const results=normalise(value);
      if(results!==null){finish(null,results);return;}
      lastShape=shape(value);
      // Empty Promise/return values may precede the actual callback response.
      if(callback)confirmReceipt();
    };
    try {
      const pending=chrome.scripting.executeScript(options,value=>{
        const error=chrome.runtime.lastError;
        if(error){finish(Error(error.message||'Browser rejected script injection.'));return;}
        accept(value,true);
      });
      if(pending&&typeof pending.then==='function')pending.then(value=>accept(value),error=>finish(Error(error?.message||'Browser rejected script injection.')));
      else if(pending!==undefined)accept(pending);
    }catch(error){finish(Error(error?.message||'Browser rejected script injection.'));}
  });
}
