import {safeKey} from '../policy.js';
export const STATE_KEY = 'mc_map_command_toolkit_state_v150';
export const prefixFor = origin => `settings:v2:${origin}:`;
const equal = (a,b) => JSON.stringify(a) === JSON.stringify(b);
const plain = x => x && typeof x === 'object' && !Array.isArray(x);
const safePath = path => path.length < 30 && path.every(k => !['__proto__','prototype','constructor'].includes(k));
export function changes(before, after, path = [], out = []) {
  if (equal(before,after)) return out;
  if (plain(before) && plain(after)) {
    for (const key of new Set([...Object.keys(before),...Object.keys(after)])) changes(before[key],after[key],[...path,key],out);
  } else out.push({path,before,after});
  return out;
}
export function mergeChanges(current, before, after) {
  let result = structuredClone(current);
  for (const change of changes(before,after)) {
    if (!safePath(change.path)) throw Error('Invalid settings path.');
    let actual = result;
    for (const key of change.path) actual = actual?.[key];
    if (!equal(actual,change.before) && !equal(actual,change.after)) throw Error('Settings changed in another tab. Reload before changing the same setting.');
    if (!change.path.length) { result = structuredClone(change.after); continue; }
    let parent = result;
    for (const key of change.path.slice(0,-1)) {
      if (!plain(parent?.[key])) throw Error('Settings changed in another tab. Reload first.');
      parent = parent[key];
    }
    const key = change.path.at(-1);
    if (change.after === undefined) delete parent[key]; else parent[key] = structuredClone(change.after);
  }
  return result;
}
export function createSettings(storage) {
  function stateValue(all,prefix,entry){if(!entry?.sharded)return entry?.value??null;const state={};for(const [k,v] of Object.entries(all))if(k.startsWith(prefix+'state:')&&!v.deleted)state[k.slice((prefix+'state:').length)]=v.value;return JSON.stringify(state);}
  let queue = Promise.resolve();
  async function load(origin) {
    const prefix = prefixFor(origin);
    const all = await storage.get(null);
    const seed = {ls:{},gm:{}};
    for (const [key,entry] of Object.entries(all)) {
      if (!key.startsWith(prefix)) continue;
      const suffix = key.slice(prefix.length), colon = suffix.indexOf(':');
      const area = suffix.slice(0,colon), name = suffix.slice(colon+1);
      if (['ls','gm'].includes(area) && safeKey(name) && (entry?.value !== null || entry?.sharded)) seed[area][name] = entry.sharded?stateValue(all,prefix,entry):entry.value;
    }
    if (!all[`${prefix}migrated`]) {
      const old = all[`pilot:${origin}`];
      const batch = {[`${prefix}migrated`]:true};
      for (const area of ['ls','gm']) for (const [key,value] of Object.entries(old?.[area] || {})) {
        if (!safeKey(key) || Object.hasOwn(seed[area],key)) continue;
        seed[area][key] = value;
        batch[`${prefix}${area}:${key}`] = {value,revision:1};
      }
      await storage.set(batch);
    }
    return seed;
  }
  async function save(origin, writes) {
    if (!Array.isArray(writes) || !writes.length || writes.length > 40) throw Error('Invalid settings batch.');
    const prefix = prefixFor(origin), batch = {}, receipt = [];
    const keys = writes.map(w => `${prefix}${w.area}:${w.key}`);
    const existing = await storage.get(null);
    const seen = new Set();
    for (const w of writes) {
      if (!['ls','gm'].includes(w.area) || !safeKey(w.key)) throw Error('Private or unknown storage key.');
      const key = `${prefix}${w.area}:${w.key}`;
      if (seen.has(key)) throw Error('Duplicate settings key.'); seen.add(key);
      if (JSON.stringify(w).length > 1100*1024) throw Error('Setting is too large.');
      if (w.area==='ls' && w.value!==null && typeof w.value!=='string') throw Error('Invalid local setting.');
      const storedEntry=existing[key] || {value:null,revision:0};
      const entry={...storedEntry,value:storedEntry.sharded?stateValue(existing,prefix,storedEntry):storedEntry.value};
      let value = w.value;
      if (w.key===STATE_KEY && w.area==='ls' && value!==null && entry.value!==null) {
        const current=JSON.parse(entry.value), after=JSON.parse(value), before=JSON.parse(w.before || '{}');
        value=JSON.stringify(mergeChanges(current,before,after));
      } else if (!equal(entry.value,w.before ?? null) && !equal(entry.value,w.value)) {
        throw Error('Settings changed in another tab. Reload before changing the same setting.');
      }
      if (value!==null && JSON.stringify(value).length>512*1024) throw Error('Setting is too large.');
      if (equal(entry.value,value)) { receipt.push({area:w.area,key:w.key,...entry}); continue; }
      const revision=entry.revision+1;
      if(w.area==='ls'&&w.key===STATE_KEY&&value!==null){
        const previous=entry.value?JSON.parse(entry.value):{},next=JSON.parse(value);
        if(!plain(next))throw Error('Invalid settings state.');
        for(const section of new Set([...Object.keys(previous),...Object.keys(next),...Object.keys(existing).filter(k=>k.startsWith(prefix+'state:')).map(k=>k.slice((prefix+'state:').length))])){
          if(!safePath([section]))throw Error('Invalid settings section.');
          if(!storedEntry.sharded||!equal(previous[section],next[section]))batch[`${prefix}state:${section}`]={value:next[section]??null,deleted:!Object.hasOwn(next,section),revision};
        }
        batch[key]={sharded:true,revision};
      }else batch[key]={value,revision};
      receipt.push({area:w.area,key:w.key,value,revision});
    }
    if (Object.keys(batch).length) await storage.set(batch);
    return receipt;
  }
  return {
    load(origin) { const next=queue.then(()=>load(origin)); queue=next.catch(()=>{}); return next; },
    save(origin,writes) { const next=queue.then(()=>save(origin,writes)); queue=next.catch(()=>{}); return next; }
  };
}
