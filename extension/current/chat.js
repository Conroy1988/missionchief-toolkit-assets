/* Reversible presentation for native alliance chat. Never submits a message. */
(function(){'use strict';
const clean=s=>String(s||'').replace(/\s+/g,' ').trim();
function fingerprint(s){let h=2166136261;for(const c of clean(s)){h^=c.charCodeAt(0);h=Math.imul(h,16777619);}return (h>>>0).toString(16);}
function accountKey(doc,origin){const href=Array.from(doc.querySelectorAll('.navbar a[href^="/profile/"]')).map(a=>a.getAttribute('href')).find(h=>/^\/profile\/\d+\/?$/.test(h));return href?'tkb:chat:'+origin+':'+href.match(/\d+/)[0]:null;}
function mount(doc,initial={},save=()=>{}){
 const outer=doc.getElementById('chat_outer'),heading=doc.getElementById('chat_panel_heading'),body=doc.getElementById('chat_panel_body'),messages=doc.getElementById('mission_chat_messages'),notice=doc.getElementById('alliance_chat_header_info');
 if(!outer||!heading||!body||!messages||doc.getElementById('tkb-chat-controls'))return null;
 let disposed=false,collapsed=initial.collapsed===true,unread=0,query='',timer=null;
 let noticeHash=fingerprint(notice?.textContent),noticeHidden=initial.noticeHidden===true&&initial.noticeHash===noticeHash;
 let known=new Set(Array.from(messages.children).map(e=>e.id).filter(Boolean));
 const controls=doc.createElement('div');controls.id='tkb-chat-controls';controls.innerHTML='<button type="button" data-collapse aria-controls="chat_panel_body"></button>';
 heading.append(controls);
 const toolbar=doc.createElement('div');toolbar.className='tkb-chat-tools';toolbar.innerHTML='<label>Search chat<input type="search" data-search placeholder="Message or player…" aria-controls="mission_chat_messages"></label><span data-results role="status"></span>';
 messages.before(toolbar);
 let noticeControl=null;if(notice){noticeControl=doc.createElement('div');noticeControl.className='tkb-chat-notice-control';noticeControl.innerHTML='<span>Alliance notice</span><button type="button" aria-controls="alliance_chat_header_info" data-notice></button>';notice.before(noticeControl);}
 const collapse=controls.querySelector('button'),search=toolbar.querySelector('input'),result=toolbar.querySelector('[data-results]');
 const stop=e=>e.stopPropagation();for(const el of [controls,toolbar,noticeControl].filter(Boolean))for(const event of ['pointerdown','mousedown','touchstart','dblclick'])el.addEventListener(event,stop);
 outer.classList.add('tkb-chat-enhanced');
 function persist(){try{Promise.resolve(save({collapsed,noticeHidden,noticeHash})).catch(()=>{});}catch{}}
 function render(){outer.classList.toggle('tkb-chat-collapsed',collapsed);collapse.textContent=collapsed?'Open chat'+(unread?' · '+(unread>99?'99+':unread)+' new':''):'−';collapse.title=collapsed?'Expand chat':'Collapse chat';collapse.setAttribute('aria-label',collapsed?'Expand chat'+(unread?', '+unread+' new messages':''):'Collapse chat');collapse.setAttribute('aria-expanded',String(!collapsed));
 if(notice){notice.classList.toggle('tkb-chat-notice-hidden',noticeHidden);const b=noticeControl.querySelector('button');b.textContent=noticeHidden?'Show notice':'×';b.title=noticeHidden?'Show alliance notice':'Hide alliance notice';b.setAttribute('aria-label',b.title);b.setAttribute('aria-expanded',String(!noticeHidden));}
 }
 function filter(){let count=0;const rows=Array.from(messages.children).filter(e=>e.tagName==='LI');for(const row of rows){const show=!query||clean(row.textContent).toLowerCase().includes(query);row.classList.toggle('tkb-chat-filtered',!show);if(show)count++;}result.textContent=query?count+' of '+rows.length+' loaded messages':'';}
 function refresh(){if(disposed)return;const rows=Array.from(messages.children).filter(e=>e.id);for(const row of rows){if(!known.has(row.id)){known.add(row.id);if(collapsed)unread++;}}if(known.size>5000)known=new Set(rows.map(e=>e.id));const hash=fingerprint(notice?.textContent);if(hash!==noticeHash){noticeHash=hash;noticeHidden=false;persist();}filter();render();}
 collapse.onclick=e=>{e.stopPropagation();collapsed=!collapsed;if(!collapsed)unread=0;render();persist();};
 if(noticeControl)noticeControl.querySelector('button').onclick=e=>{e.stopPropagation();noticeHidden=!noticeHidden;render();persist();};
 search.oninput=()=>{query=search.value.trim().toLowerCase();filter();};
 const style=doc.createElement('style');style.textContent=CSS;doc.head.append(style);render();filter();
 const Observer=doc.defaultView?.MutationObserver;let observer;if(Observer){observer=new Observer(()=>{if(timer||disposed)return;timer=doc.defaultView.setTimeout(()=>{timer=null;refresh();},100);});observer.observe(messages,{childList:true,subtree:true,characterData:true});if(notice)observer.observe(notice,{childList:true,subtree:true,characterData:true});}
 return {refresh,destroy(){disposed=true;observer?.disconnect();if(timer)doc.defaultView.clearTimeout(timer);for(const row of messages.children)row.classList.remove('tkb-chat-filtered');notice?.classList.remove('tkb-chat-notice-hidden');outer.classList.remove('tkb-chat-enhanced','tkb-chat-collapsed');controls.remove();toolbar.remove();noticeControl?.remove();style.remove();}};
}
const CSS=`
#chat_outer.tkb-chat-enhanced #chat_panel{border:1px solid #535c66;border-top:2px solid #ee405a;border-radius:9px;background:#0f151a;color:#e3e9ee;overflow:visible;box-shadow:0 8px 24px #0005}
#chat_outer.tkb-chat-enhanced #chat_panel_heading{background:linear-gradient(120deg,#20272e,#10151b);color:#fff;border:0;border-radius:7px 7px 0 0;padding:8px 10px;font:700 13px/1.5 system-ui;display:flex;flex-wrap:wrap;align-items:center;gap:7px}
#chat_outer.tkb-chat-enhanced #chat_panel_heading>.btn-group{margin:0!important;float:none!important;order:2;margin-left:auto!important}#chat_outer.tkb-chat-enhanced #chat_panel_heading>.clearfix{display:none}
#chat_outer.tkb-chat-enhanced #chat_panel_heading .btn{background:#27313b;border:1px solid #53616e;color:#dbe5ed;margin-right:3px!important;border-radius:4px;font-size:11px}
#tkb-chat-controls{display:flex;order:3}#tkb-chat-controls button,.tkb-chat-notice-control button{border:1px solid #586775;background:#202b35;color:#f0f6fb;padding:4px 9px;min-height:28px;min-width:28px;border-radius:5px;font:700 12px/1.4 system-ui;cursor:pointer}
#chat_outer.tkb-chat-enhanced #chat_panel_body{background:#0f151a;color:#d8e1e9;padding:8px 10px;scrollbar-width:thin;scrollbar-color:#63707c #151d25}
.tkb-chat-notice-control{display:flex;justify-content:space-between;align-items:center;gap:8px;margin:0 0 5px;color:#b5c2cd;font:700 10px/1.5 system-ui;letter-spacing:.6px;text-transform:uppercase}
#chat_outer.tkb-chat-enhanced #alliance_chat_header_info{background:#182832;border:1px solid #36596b;border-left:3px solid #5faac6;border-radius:5px;color:#d5eaf4;padding:10px;font:12px/1.55 system-ui;margin:0 0 10px;overflow-wrap:anywhere;max-height:150px;overflow:auto}
#chat_outer.tkb-chat-enhanced #alliance_chat_header_info.tkb-chat-notice-hidden{display:none!important}
#chat_outer.tkb-chat-enhanced #new_alliance_chat{margin:8px 0 10px}#chat_outer.tkb-chat-enhanced #new_alliance_chat .form-group{margin-bottom:0}
#chat_outer.tkb-chat-enhanced #alliance_chat_message{background:#090e13;color:#f4f7fa;border:1px solid #637485;border-radius:6px;min-height:34px;font:13px system-ui;padding:7px 10px}#chat_outer.tkb-chat-enhanced #new_alliance_chat label{color:#c5d1db;font:12px system-ui}
.tkb-chat-tools{display:flex;flex-wrap:wrap;align-items:center;gap:5px;margin:6px 0 8px}.tkb-chat-tools label{flex:1;margin:0;color:#aebdca;font:10px/1.4 system-ui}.tkb-chat-tools input{display:block;width:100%;box-sizing:border-box;margin-top:3px;padding:6px 8px;border:1px solid #3f5263;border-radius:5px;background:#141e27;color:#e5eef6;font:12px/1.4 system-ui}.tkb-chat-tools [data-results]{font:10px system-ui;color:#aebdca}
#chat_outer.tkb-chat-enhanced #mission_chat_messages{padding:0;margin:0;list-style:none;font:12px/1.65 system-ui;color:#d6e1eb}
#chat_outer.tkb-chat-enhanced #mission_chat_messages>li{padding:7px 8px;margin:0 0 3px;border-left:2px solid transparent;border-bottom:1px solid #2a3742;border-radius:3px;overflow-wrap:anywhere;background:#141d25}
#chat_outer.tkb-chat-enhanced #mission_chat_messages>li:nth-child(even){background:#19232c}#chat_outer.tkb-chat-enhanced #mission_chat_messages>li.chatToSelf{border-left-color:#ff7590;background:#35202c}
#chat_outer.tkb-chat-enhanced #mission_chat_messages a{color:#91cef5}#chat_outer.tkb-chat-enhanced .mission_chat_message_username{color:#bccbd8;font-size:11px}#chat_outer.tkb-chat-enhanced .mission_chat_message_username a{font-weight:750;color:#d3e8f8}
#chat_outer.tkb-chat-enhanced #mission_chat_messages>li.tkb-chat-filtered{display:none!important}
#chat_outer.tkb-chat-collapsed{height:auto!important;min-height:0!important}#chat_outer.tkb-chat-collapsed #chat_panel_body,#chat_outer.tkb-chat-collapsed>.ui-resizable-handle{display:none!important}#chat_outer.tkb-chat-collapsed #chat_panel{height:auto!important;min-height:0!important;margin-bottom:0!important}#chat_outer.tkb-chat-collapsed #chat_panel_heading{border-radius:7px;padding-block:5px}#chat_outer.tkb-chat-collapsed #chat_panel_heading>.btn-group{display:none!important}#chat_outer.tkb-chat-collapsed #tkb-chat-controls{margin-left:auto}
#chat_outer.tkb-chat-enhanced button:focus-visible,#chat_outer.tkb-chat-enhanced input:focus-visible,#chat_outer.tkb-chat-enhanced a:focus-visible{outline:2px solid #ff93a8;outline-offset:2px}
@media(max-width:500px){#chat_outer.tkb-chat-enhanced #chat_panel_heading{gap:4px;padding:6px}#chat_outer.tkb-chat-enhanced #chat_panel_body{padding:6px}.tkb-chat-tools input{font-size:16px}#chat_outer.tkb-chat-enhanced #alliance_chat_message{font-size:16px}}
`;
if(typeof module!=='undefined'&&module.exports){module.exports={mount,fingerprint,accountKey,CSS};return;}
if(location.pathname!=='/')return;let view=null,generation=0;
async function start(){const run=++generation;try{const key=accountKey(document,location.origin),saved=await chrome.storage.local.get(['enabled',...(key?[key]:[])]);if(run!==generation)return;if(saved.enabled===false){view?.destroy();view=null;}else if(!view)view=mount(document,key?saved[key]:{},value=>key?chrome.storage.local.set({[key]:value}):undefined);}catch{/* Keep the native chat available. */}}
void start();chrome.storage.onChanged.addListener((c,a)=>{if(a==='local'&&c.enabled)void start();});
})();
