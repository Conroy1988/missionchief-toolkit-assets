import {readUrl} from '../policy.js';
export function createPublicReader(fetcher=fetch){
  const active=new Map(),requests=new Map(),cache=new Map();
  async function read(documentId,message){
    if(message.method!=='GET')throw Error('Only public GET requests are supported.');
    const url=readUrl(message.url),key=`${url}:${message.responseType||'text'}`,id=`${documentId}:${message.id}`;
    if(requests.has(id)||requests.size>=12)throw Error('Too many external requests.');
    if(cache.get(key)?.expires>Date.now())return structuredClone(cache.get(key).value);
    let job=active.get(key);
    if(!job){
      const controller=new AbortController();job={controller,readers:0};
      job.promise=(async()=>{
        const response=await fetcher(url,{credentials:'omit',redirect:'error',signal:controller.signal});
        const reader=response.body.getReader(),chunks=[];let size=0;
        for(;;){const {value,done}=await reader.read();if(done)break;size+=value.length;if(size>4*1024*1024){await reader.cancel();throw Error('Response too large.');}chunks.push(value);}
        const bytes=new Uint8Array(size);let offset=0;for(const c of chunks){bytes.set(c,offset);offset+=c.length;}
        const value={status:response.status,finalUrl:response.url,responseHeaders:[...response.headers].map(([k,v])=>`${k}: ${v}`).join('\r\n'),
          ...(message.responseType==='arraybuffer'?{bytes:Array.from(bytes)}:{responseText:new TextDecoder().decode(bytes)})};
        if(response.ok&&size<=512*1024){cache.set(key,{value,expires:Date.now()+60000});while(cache.size>6)cache.delete(cache.keys().next().value);}
        return value;
      })().finally(()=>active.delete(key));active.set(key,job);
    }
    job.readers++;
    let timer,abort;
    const cancelled=new Promise((_,reject)=>{abort=()=>reject(Error('Request cancelled.'));timer=setTimeout(()=>reject(Error('Request timed out.')),Math.min(20000,Math.max(1,Number(message.timeout)||15000)));});
    requests.set(id,abort);
    try{return structuredClone(await Promise.race([job.promise,cancelled]));}
    finally{clearTimeout(timer);requests.delete(id);if(--job.readers===0&&active.has(key))job.controller.abort();}
  }
  return {read,abort(documentId,id){requests.get(`${documentId}:${id}`)?.();}};
}
