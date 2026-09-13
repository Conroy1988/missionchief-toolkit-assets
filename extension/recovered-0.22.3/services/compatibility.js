// Read-only, bounded startup audit. Each injection is issued once. No game data
// or settings values are collected; only known probe values and response shapes.
export function runCompatibility(sender) {
  const shape=(value,depth=0)=>{
    if(value===null)return 'null';
    if(typeof value!=='object')return typeof value;
    if(depth>=3)return Array.isArray(value)?'array':'object';
    const keys=Object.keys(value).slice(0,12),allowed=/^(?:\d+|result|results|error|message|frameId|documentId|value|data|success|length)$/;
    return {type:Array.isArray(value)?'array':'object',keys:keys.map(key=>({key:allowed.test(key)?key:'other',value:shape(value[key],depth+1)}))};
  };
  const tabMessage=message=>new Promise(resolve=>{
    let done=false;const end=value=>{if(done)return;done=true;clearTimeout(timer);resolve(value);};
    const timer=setTimeout(()=>end(null),2000);
    try{const p=chrome.tabs.sendMessage(sender.tab.id,message,{frameId:0},value=>{const e=chrome.runtime.lastError;end(e?null:value);});if(p?.then)p.then(value=>{if(value!=null)end(value);},()=>end(null));}catch{end(null);}
  });
  const inject=options=>new Promise(resolve=>{
    const report={callback:'not-called',promise:'not-returned'};let done=false;
    const end=()=>{if(done)return;done=true;clearTimeout(timer);resolve(report);};
    const timer=setTimeout(end,2000);
    try{
      const p=chrome.scripting.executeScript(options,value=>{const e=chrome.runtime.lastError;report.callback=shape(value);report.lastError=Boolean(e);end();});
      if(p?.then)p.then(value=>{report.promise=shape(value);if(report.callback==='not-called')setTimeout(end,100);},()=>{report.promise='rejected';end();});
      else report.returned=shape(p);
    }catch{report.threw=true;end();}
  });
  return (async()=>{
    const deadline=Date.now()+12000;
    const report={schema:1,tests:[],bridge:await tabMessage({op:'compatibilityPrepare'})};
    for(const world of ['ISOLATED','MAIN'])for(const kind of ['function','arguments','file']){
      if(Date.now()>deadline){report.tests.push({world,kind,skipped:'audit-time-budget'});continue;}
      await tabMessage({op:'compatibilityClear'});
      const options={target:{tabId:sender.tab.id,frameIds:[0]},world};
      if(kind==='file')options.files=['compatibility-probe.js'];
      else if(kind==='arguments'){
        options.func=value=>{const r={executed:true,argsValid:value==='mcms-probe-ok',bridgeWorld:globalThis.__MCMS_COMPAT_BRIDGE__===true};document.documentElement.setAttribute('data-mcms-compat-result',JSON.stringify(r));return r;};
        options.args=['mcms-probe-ok'];
      }else options.func=()=>{const r={executed:true,bridgeWorld:globalThis.__MCMS_COMPAT_BRIDGE__===true};document.documentElement.setAttribute('data-mcms-compat-result',JSON.stringify(r));return r;};
      const delivery=await inject(options);
      const proof=await tabMessage({op:'compatibilityRead'});
      report.tests.push({world,kind,delivery,proof});
    }
    report.assets=Date.now()<=deadline?await tabMessage({op:'compatibilityAssets'}):{skipped:'audit-time-budget'};
    await tabMessage({op:'compatibilityClear'});
    return report;
  })();
}
