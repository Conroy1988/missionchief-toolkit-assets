// Runs in the isolated content world. Only read-only mission HTML is exposed.
export function createGameReader(fetcher = fetch) {
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
