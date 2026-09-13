import { createDiscord } from './services/discord.js';
import { runCompatibility } from './services/compatibility.js';
import { executeScript } from './services/injection.js';
import { gameOrigin, readUrl } from './policy.js';
import { createSettings } from './services/settings.js';
import { createJobs } from './services/jobs.js';
import { createPublicReader } from './services/public-reader.js';
const publicReader=createPublicReader();
const discord=createDiscord(chrome.storage.local);
const settings = createSettings(chrome.storage.local);
const jobs = createJobs(chrome.storage.local, Date.now, async job => {try{const token=job.documentId.startsWith('fallback:')?job.documentId.split(':')[2]:null;return Boolean(await chrome.tabs.sendMessage(job.tabId,{op:'leaseProbe',...(token?{documentToken:token}:{})},token?{frameId:0}:{documentId:job.documentId}));}catch{return false;}});
const moduleLoads = new Map();


const starts = new Map();



function pageSender(sender) {
  const origin = gameOrigin(sender.url);
  if (!origin || sender.frameId !== 0 || !sender.tab?.id) throw Object.assign(Error('Unsupported page.'),{code:'UNSUPPORTED_PAGE'});
  if (!sender.documentId) throw Object.assign(Error('Browser did not provide a document ID.'),{code:'MISSING_DOCUMENT_ID'});
  return {origin, tabId: sender.tab.id, documentId: sender.documentId};
}
function target(sender) {
  const s = pageSender(sender);
  return sender.documentToken?{tabId:s.tabId,frameIds:[0]}:{tabId:s.tabId,documentIds:[s.documentId]};
}
async function startupStep(stage,run) {
  try{
    const result=await run();
    if(['identity-injection','seed-injection','toolkit-injection','startup-receipt'].includes(stage)){
      if(!Array.isArray(result))throw Error(`Browser returned ${typeof result} instead of an injection result array.`);
      const failure=result.find(entry=>entry?.error);
      if(failure)throw Error(typeof failure.error==='string'?failure.error:failure.error.message||'Injected script failed.');
    }
    return result;
  }catch(error){
    const wrapped=new Error(typeof error?.message==='string'?error.message:'Unknown startup error');
    wrapped.code=error?.code;wrapped.stage=error?.stage||stage;throw wrapped;
  }
}
function startupErrorDetail(error) {
  return String(error?.message||'Unknown startup error')
    .replace(/(?:https?|file|chrome-extension|moz-extension):\/\/[^\s)\]"']+/gi,'[URL]')
    .replace(/[A-Z0-9._%+-]+@[A-Z0-9.-]+\.[A-Z]{2,}/gi,'[email]')
    .replace(/\b[0-9a-f]{8}-[0-9a-f-]{27,}\b/gi,'[document ID]')
    .replace(/\b[A-Za-z0-9_-]{32,}\b/g,'[identifier]')
    .replace(/\b\d{4,}\b/g,'[number]').replace(/\s+/g,' ').slice(0,240);
}
async function identifyPage(sender,message) {
  if(sender.documentId){pageSender(sender);return sender;}
  const origin=gameOrigin(sender.url);
  if(!origin||sender.frameId!==0||!sender.tab?.id)throw Object.assign(Error('Unsupported page.'),{code:'UNSUPPORTED_PAGE'});
  const token=message?.documentToken;
  if(typeof token!=='string'||!/^[0-9a-f]{8}-[0-9a-f]{4}-4[0-9a-f]{3}-[89ab][0-9a-f]{3}-[0-9a-f]{12}$/i.test(token))throw Object.assign(Error('Missing page identity.'),{code:'MISSING_DOCUMENT_ID'});
  const [receipt]=await startupStep('identity-injection',()=>executeScript({target:{tabId:sender.tab.id,frameIds:[0]},world:'ISOLATED',func:(...args)=>{const receipt=args.pop();if(receipt)setTimeout(()=>document.documentElement.removeAttribute('data-mcms-receipt-'+receipt),10000);try{const value=((token,origin)=>location.origin===origin&&document.documentElement.getAttribute('data-mcms-extension-document')===token)(...args);if(receipt)document.documentElement.setAttribute('data-mcms-receipt-'+receipt,JSON.stringify({done:true,result:value===undefined?null:value}));return value;}catch(error){if(receipt)document.documentElement.setAttribute('data-mcms-receipt-'+receipt,JSON.stringify({done:true,error:String(error.message||error)}));throw error;}},args:[token,origin]}));
  if(receipt?.result!==true)throw Object.assign(Error('The game document changed. Reload the tab.'),{code:'DOCUMENT_CHANGED'});
  return {...sender,documentId:`fallback:${sender.tab.id}:${token}`,documentToken:token};
}
async function start(sender) {
  const {origin, documentId} = pageSender(sender);
  await startupStep('job-recovery',()=>jobs.interruptTab(sender.tab.id,documentId));
  const config = await startupStep('enabled-setting',()=>chrome.storage.local.get('enabled'));
  if (!config.enabled) return {state: 'off'};
  if (starts.has(documentId)) return starts.get(documentId);
  const job = (async () => {
    const loadedSettings=await startupStep('settings-load',()=>settings.load(origin));
    const result = await startupStep('seed-injection',()=>executeScript({target: target(sender), world: 'MAIN', func: (...args)=>{const receipt=args.pop();if(receipt)setTimeout(()=>document.documentElement.removeAttribute('data-mcms-receipt-'+receipt),10000);try{const value=(data => {
      if(data.documentToken&&(location.origin!==data.origin||document.documentElement.getAttribute('data-mcms-extension-document')!==data.documentToken))throw Error('Game document changed before startup.');
      if (window.__MCMS_EXTENSION_PILOT__) return 'already-started';
      const existing = window.__MC_MAP_COMMAND_TOOLKIT_RUNTIME__;
      if ((existing && !existing.destroyed) || window.__MCMS_FIRST_BYTE_BOOTSTRAP__) return 'userscript-active';
      window.__MCMS_EXTENSION_SEED__ = data;
      return 'ready';
    })(...args);if(receipt)document.documentElement.setAttribute('data-mcms-receipt-'+receipt,JSON.stringify({done:true,result:value===undefined?null:value}));return value;}catch(error){if(receipt)document.documentElement.setAttribute('data-mcms-receipt-'+receipt,JSON.stringify({done:true,error:String(error.message||error)}));throw error;}}, args: [{...loadedSettings, documentToken:sender.documentToken,origin,version: chrome.runtime.getManifest().version, financeStyleUrl:chrome.runtime.getURL('finance-dashboard.css'),commandStyleUrl:chrome.runtime.getURL('command-ui.css'),workspaceStyleUrl:chrome.runtime.getURL('workspace.css'),operationsStyleUrl:chrome.runtime.getURL('operations.css'),styleUrl: chrome.runtime.getURL('toolkit.css')}]}));
    const state = result[0]?.result;
    if (state !== 'ready') return {state};
    await startupStep('toolkit-injection',()=>executeScript({target: target(sender), world: 'MAIN', files: ['toolkit.js']}));
    const [receipt] = await startupStep('startup-receipt',()=>executeScript({target: target(sender), world: 'MAIN', func: (...args)=>{const receipt=args.pop();if(receipt)setTimeout(()=>document.documentElement.removeAttribute('data-mcms-receipt-'+receipt),10000);try{const value=(token => Boolean(window.__MCMS_EXTENSION_PILOT__)&&(!token||document.documentElement.getAttribute('data-mcms-extension-document')===token))(...args);if(receipt)document.documentElement.setAttribute('data-mcms-receipt-'+receipt,JSON.stringify({done:true,result:value===undefined?null:value}));return value;}catch(error){if(receipt)document.documentElement.setAttribute('data-mcms-receipt-'+receipt,JSON.stringify({done:true,error:String(error.message||error)}));throw error;}},args:[sender.documentToken||null]}));
    return {state: receipt?.result ? 'started' : 'userscript-active'};
  })();
  starts.set(documentId, job);
  try { return await job; } finally { starts.delete(documentId); }
}
chrome.runtime.onMessage.addListener((message, sender, respond) => {
  // Synchronous probe separates background availability from async reply support.
  if(message?.op==='ping'&&sender.id===chrome.runtime.id&&!sender.tab&&sender.url===chrome.runtime.getURL('popup.html')){respond({ok:true,value:{protocol:1}});return false;}
  const run = async () => {
    if(sender.id===chrome.runtime.id&&sender.url===chrome.runtime.getURL('discord.html')) {
      if(message.op==='discordStatus')return discord.status();
      if(message.op==='discordSave')return discord.save(message.url,message.label);
      if(message.op==='discordClear')return discord.clear();
      if(message.op==='discordTest')return discord.request(false);
      if(message.op==='discordSend')return discord.request(true,message.draftId,message.destinationId);
      throw Error('Unknown Discord operation.');
    }
    if (sender.id === chrome.runtime.id && !sender.tab && sender.url?.startsWith(chrome.runtime.getURL('popup.html'))) {
      if (message.op === 'status') {
        const tab = await chrome.tabs.get(message.tabId);
        const origin = gameOrigin(tab.url);
        return {version: chrome.runtime.getManifest().version, jobs: origin ? await jobs.list(origin) : []};
      }
      throw Error('Unknown popup operation.');
    }
    if(message?.op==='compatibility'){
      if(!gameOrigin(sender.url)||sender.frameId!==0||!sender.tab?.id)throw Error('Unsupported probe page.');
      return runCompatibility(sender);
    }
    sender=await startupStep('page-identity',()=>identifyPage(sender,message));
    if (!message || typeof message.id !== 'string' || message.id.length > 100) throw Error('Invalid request.');
    if (message.op === 'start') return start(sender);
    if (!(await chrome.storage.local.get('enabled')).enabled) throw Error('Pilot is off. Reload the game tab.');
    if(message.op==='jobsFocus'){if(!/^[a-zA-Z0-9_-]{1,64}$/.test(message.account||''))throw Error('Invalid account.');const job=(await jobs.list(pageSender(sender).origin,message.account)).find(j=>j.documentId===message.documentId&&j.state==='running');if(!job)throw Error('This task is no longer active.');await chrome.tabs.update(job.tabId,{active:true});return true;}
    if(message.op==='jobsList'){if(!/^[a-zA-Z0-9_-]{1,64}$/.test(message.account||''))throw Error('Invalid account.');const origin=pageSender(sender).origin;return {tabId:sender.tab.id,jobs:await jobs.list(origin,message.account),history:await jobs.history(origin,message.account)};}
    if(['discordDraft','discordReceipt'].includes(message.op)){
      if(!/^[a-zA-Z0-9_-]{1,64}$/.test(String(message.account||'')))throw Error('Sign into a game account before preparing a report.');
      const scope=pageSender(sender).origin+':'+message.account;
      if(message.op==='discordReceipt')return discord.receipt(scope);
      if(!['finance','sweep','sitrep'].includes(message.kind))throw Error('Unknown report type.');
      const generatedAt=Number(message.generatedAt);
      return discord.stage(message.payload,message.chart,{scope,kind:message.kind,generatedAt:Number.isFinite(generatedAt)&&generatedAt>0&&generatedAt<=Date.now()?generatedAt:Date.now()});
    }
    if(message.op==='discordOpen'){await chrome.tabs.create({url:chrome.runtime.getURL('discord.html')});return true;}
    if (message.op === 'request') return publicReader.read(sender.documentId,message);
    if (message.op === 'abort') { publicReader.abort(sender.documentId,message.requestId); return true; }
    if (message.op === 'saveBatch') return settings.save(pageSender(sender).origin, message.writes);
    if (message.op === 'job') return jobs.update(pageSender(sender), message);
    if (message.op === 'module') {
      if (!['administration','finance','customisation','intelligence'].includes(message.name)) throw Error('Unknown module.');
      const key = `${sender.documentId}:${message.name}`;
      if (!moduleLoads.has(key)) moduleLoads.set(key, executeScript({target:target(sender),world:'MAIN',files:[`features/${message.name}.js`]}));
      try {await moduleLoads.get(key);return true;} finally {moduleLoads.delete(key);}
    }
    throw Error('Unknown pilot operation.');
  };
  run().then(value => respond({ok: true, value}), error => respond({ok: false, error: error.message, code:error.code,...(message?.op==='start'?{startupStage:error.stage||'startup',startupDetail:startupErrorDetail(error)}:{})}));
  return true;
});

chrome.tabs.onRemoved?.addListener(tabId=>{void jobs.interruptTab(tabId);});
