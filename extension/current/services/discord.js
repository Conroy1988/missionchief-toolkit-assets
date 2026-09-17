// Credentials remain in extension storage; only the Account page can edit them.
export function webhookUrl(raw) {
  let u;try{u=new URL(raw);}catch{throw Error('Enter a valid Discord webhook URL.');}
  if(u.protocol!=='https:'||!['discord.com','discordapp.com'].includes(u.hostname)||u.port||u.username||u.password||u.hash||!/^\/api(?:\/v\d+)?\/webhooks\/\d+\/[\w.-]+\/?$/.test(u.pathname))throw Error('Use an HTTPS Discord webhook URL.');
  for(const [key,value] of u.searchParams)if(key!=='thread_id'||!/^\d+$/.test(value))throw Error('Only a Discord thread_id query is supported.');
  u.hostname='discord.com';return u.href;
}
export function cleanPayload(raw) {
  if(!raw||JSON.stringify(raw).length>24000||!Array.isArray(raw.embeds)||!raw.embeds.length||raw.embeds.length>10)throw Error('Invalid report.');
  const text=(v,max)=>typeof v==='string'?v.slice(0,max):'';
  let total=0;
  const embeds=raw.embeds.map(e=>{
    const out={title:text(e.title,256),description:text(e.description,4096)};
    if(Number.isInteger(e.color))out.color=Math.max(0,Math.min(16777215,e.color));
    if(e.footer?.text)out.footer={text:text(e.footer.text,2048)};
    if(e.timestamp&&!Number.isNaN(Date.parse(e.timestamp)))out.timestamp=new Date(e.timestamp).toISOString();
    if(Array.isArray(e.fields))out.fields=e.fields.slice(0,25).map(f=>({name:text(f.name,256)||'—',value:text(f.value,1024)||'—',inline:f.inline===true}));
    total+=out.title.length+out.description.length+(out.footer?.text.length||0)+(out.fields||[]).reduce((n,f)=>n+f.name.length+f.value.length,0);
    return out;
  });
  if(total>6000)throw Error('Report exceeds Discord’s text limit.');
  return {username:text(raw.username,80)||'MissionChief Toolkit',allowed_mentions:{parse:[]},embeds};
}
export function createDiscord(storage,fetcher=fetch,now=Date.now) {
  const key='private:discord:v1',draftKey='private:discord:draft:v1';let busy=false;
  async function draft(){const d=(await storage.get(draftKey))[draftKey];if(d&&now()-d.created>=1800000){await storage.remove(draftKey);return null;}return d||null;}
  async function config(){return (await storage.get(key))[key]||{};}
  return {
    privateConfig: config,
    async restore(value,owner){if(busy)throw Error('A Discord request is running. Try again shortly.');const c=await config();const url=value.url?webhookUrl(value.url):'';await storage.set({[key]:{id:c.url===url&&c.owner===owner?c.id:crypto.randomUUID(),url,label:String(value.label||'Toolkit reports').slice(0,80),owner}});},
    async stage(payload,chart,context={}){if(busy)throw Error('Wait for the current Discord request.');busy=true;try{const old=await draft();if(old&&now()-old.created<3000)throw Error('A report was just prepared. Open Discord in the extension popup.');if(chart!==undefined&&(typeof chart!=='string'||chart.length>2800000||!/^data:image\/png;base64,iVBORw0KGgo[A-Za-z0-9+/=]+$/.test(chart)))throw Error('Chart must be a PNG smaller than 2 MB.');const d={id:crypto.randomUUID(),created:now(),payload:cleanPayload(payload),state:'ready',context,...(chart?{chart}:{})};await storage.set({[draftKey]:d});return d.id;}finally{busy=false;}},
    async receipt(scope){return Number((await storage.get('private:discord:last:'+scope))['private:discord:last:'+scope])||0;},
    async status(){const c=await config();return {configured:!!c.url,destinationId:c.id||'',label:c.label||'',draft:await draft()};},
    async save(raw,label,owner){if(busy)throw Error('Wait for the current Discord request.');busy=true;try{await storage.set({[key]:{id:crypto.randomUUID(),url:webhookUrl(raw),label:String(label||'Toolkit reports').slice(0,80),owner}});return true;}finally{busy=false;}},
    async clear(){if(busy)throw Error('Wait for the current Discord request.');busy=true;try{await storage.remove([key,draftKey]);return true;}finally{busy=false;}},
    async request(send,id,destinationId){
      if(busy)throw Error('A Discord request is already running.');busy=true;
      try{
        const c=await config();if(!c.url)throw Error('Save your Discord webhook first.');if(send&&(!destinationId||c.id!==destinationId))throw Error('The destination changed. Review it again before sending.');const url=new URL(webhookUrl(c.url));
        const d=send?await draft():null;
        if(send&&(!d||d.id!==id||!['ready','rate-limited'].includes(d.state)))throw Error('This report has expired or was already attempted. Prepare a fresh report if needed.');
        if(send&&d.retryAt>now())throw Error('Discord is rate limited. Wait before trying again.');
        if(send){url.searchParams.set('wait','true');d.state='sending';await storage.set({[draftKey]:d});}
        else url.search='';
        let response,body;
        if(send){const payload=cleanPayload(d.payload);if(d.chart){payload.embeds[0].image={url:'attachment://report.png'};body=new FormData();body.append('payload_json',JSON.stringify(payload));body.append('files[0]',new Blob([Uint8Array.from(atob(d.chart.split(',')[1]),c=>c.charCodeAt(0))],{type:'image/png'}),'report.png');}else body=JSON.stringify(payload);}
        const controller=new AbortController(),timer=setTimeout(()=>controller.abort(),15000);
        try{response=await fetcher(url.href,{method:send?'POST':'GET',credentials:'omit',redirect:'error',signal:controller.signal,...(send?{...(d.chart?{}:{headers:{'Content-Type':'application/json'}}),body}:{})});}
        catch{if(send){d.state='uncertain';await storage.set({[draftKey]:d});}throw Error(send?'Delivery could not be confirmed. Check Discord before preparing another report.':'Discord could not be reached. Check your connection and extension permissions.');}finally{clearTimeout(timer);}
        if(response.status===429){const data=await response.json().catch(()=>({}));if(send){d.state='rate-limited';d.retryAt=now()+Math.max(1000,Math.min(3600000,Number(data.retry_after)*1000||60000));await storage.set({[draftKey]:d});}throw Error('Discord is rate limited. Wait before trying again.');}
        if(!response.ok){if(send){d.state='failed';await storage.set({[draftKey]:d});}throw Error(`Discord rejected the request (${response.status}). Check the webhook and channel permissions.`);}
        if(send){d.state='sent';d.sentAt=now();await storage.set({[draftKey]:d,...(d.context?.kind==='finance'?{['private:discord:last:'+d.context.scope]:d.context.generatedAt}:{})});return {sent:true};}
        const data=await response.json();return {name:String(data.name||'Discord webhook').slice(0,80)};
      }finally{busy=false;}
    }
  };
}
