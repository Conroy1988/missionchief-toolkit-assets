(()=>{
 const notes=TKB_RELEASE_NOTES,key='tkbWhatsNewAcknowledgedVersion';let timer,checking=false,shown=false,finished=false;
 const manual=location.protocol==='chrome-extension:'||location.protocol==='moz-extension:';
 const stop=()=>clearTimeout(timer);
 async function show(){
  if(shown)return;shown=true;stop();
  const host=document.createElement('div');document.body.append(host);const shadow=host.attachShadow({mode:'open'});
  const style=document.createElement('style');style.textContent=`:host{color-scheme:dark}dialog{box-sizing:border-box;width:min(560px,94vw);max-height:86dvh;overflow:auto;padding:24px;border:1px solid #77838d;border-top:4px solid #ff4963;border-radius:10px;background:#20262c;color:#f5f7fa;font:15px/1.55 system-ui;box-shadow:0 20px 80px #0008}dialog::backdrop{background:#0009}h1{margin:0;font-size:26px}header p{color:#ccd4dc;margin:4px 0 18px}h2{font-size:16px;margin:18px 0 5px;color:#ff7487}ul{margin:0;padding-left:20px}li{margin:7px 0}footer{position:sticky;bottom:-24px;background:#20262c;padding:16px 0 4px}button{background:#b7203b;color:white;border:1px solid #ff7487;border-radius:5px;padding:10px 24px;font:600 15px system-ui;cursor:pointer}button:focus-visible{outline:3px solid white;outline-offset:3px}[role=status]{color:#ffd6db}
  .major-release{width:min(860px,94vw);max-height:90dvh;padding:0;overflow:hidden;background:#101114;border-color:#493039;border-top-color:#ed4056;box-shadow:0 24px 100px #000b}
  .major-release[open]{display:flex;flex-direction:column}
  .major-release header{padding:22px 26px 16px;border-bottom:1px solid #393037;background:linear-gradient(115deg,#25151b,#141519 65%);flex-shrink:0}
  .major-release h1{font-size:clamp(23px,4vw,32px);letter-spacing:-.5px}
  .major-release header p{margin:4px 0 14px;font-size:13px}
  .release-navigation{display:flex;align-items:center;gap:14px;color:#d5bdc3;font-size:12px;font-weight:600}
  .release-navigation select{min-width:0;flex:1;width:100%;max-width:450px;border:1px solid #6a3a46;border-radius:6px;padding:9px;background:#17181d;color:#fff;font:13px system-ui}
  .major-release .release-content{overflow:auto;min-height:0;padding:0 26px 22px;overscroll-behavior:contain;scrollbar-color:#864453 #17181d}
  .release-intro{color:#bfc4cd;font-size:14px;margin:18px 0 22px}
  .major-release section{border-top:1px solid #30272e;padding:6px 0 12px;scroll-margin-top:12px}
  .major-release h2{font-size:18px;color:#ff7b8b;margin:15px 0 10px;scroll-margin-top:14px}
  .major-release li{margin:9px 0;color:#e0e2e7;font-size:14px;line-height:1.65}
  .major-release li::marker{color:#ed4056}
  .major-release footer{position:static;flex-shrink:0;display:flex;align-items:center;justify-content:space-between;gap:16px;padding:14px 26px;background:#17181c;border-top:1px solid #393037}
  .major-release footer p{margin:0;font-size:12px;max-width:480px}
  .major-release footer button{flex-shrink:0}
  @media(max-width:520px){.major-release header{padding:16px}.major-release .release-content{padding:0 16px 16px}.major-release footer{padding:12px 16px}.release-navigation{display:block}.release-navigation select{display:block;margin-top:6px}.major-release footer p{font-size:11px}}
  `;
  const dialog=document.createElement('dialog');if(notes.major)dialog.className='major-release';dialog.setAttribute('aria-labelledby','tkb-whats-new-title');
  const header=document.createElement('header'),title=document.createElement('h1'),version=document.createElement('p');title.id='tkb-whats-new-title';title.textContent=notes.title||'What’s New';version.textContent=notes.major?`Map Command Toolkit · ${notes.previousVersion} → ${notes.version}`:`Map Command Toolkit · ${notes.version}`;header.append(title,version);dialog.append(header);
  const content=document.createElement('div');content.className='release-content';dialog.append(content);
  if(notes.intro){const intro=document.createElement('p');intro.className='release-intro';intro.textContent=notes.intro;content.append(intro);}
  let jump;
  if(notes.major){
   const navigation=document.createElement('label');navigation.className='release-navigation';navigation.textContent='Explore this release';
   jump=document.createElement('select');jump.setAttribute('aria-label','Jump to a release section');const first=document.createElement('option');first.value='';first.textContent=`${notes.sections.length} sections · ${notes.sections.reduce((total,section)=>total+section[1].length,0)} updates`;jump.append(first);navigation.append(jump);header.append(navigation);
  }
  let index=0;
  for(const [label,items]of notes.sections){const section=document.createElement('section'),heading=document.createElement('h2'),list=document.createElement('ul');heading.textContent=label;heading.id='release-section-'+index++;heading.tabIndex=-1;if(jump){const option=document.createElement('option');option.value=heading.id;option.textContent=label;jump.append(option);}for(const text of items){const li=document.createElement('li');li.textContent=text;list.append(li);}section.append(heading,list);content.append(section);}
  if(jump)jump.onchange=()=>{const target=shadow.getElementById(jump.value);if(target){target.scrollIntoView({block:'start'});target.focus({preventScroll:true});}};
  const footer=document.createElement('footer'),button=document.createElement('button'),status=document.createElement('p');button.textContent='Got it';status.setAttribute('role','status');if(notes.major)status.textContent='Shown once for 2.0.0. Reopen from the extension popup → What’s New.';footer.append(button,status);dialog.append(footer);shadow.append(style,dialog);
  let resolveClosed;const closed=new Promise(resolve=>resolveClosed=resolve);
  const dismiss=async()=>{button.disabled=true;try{await chrome.storage.local.set({[key]:notes.version});dialog.close();host.remove();resolveClosed();if(manual)window.close();}catch{status.textContent='Could not remember this update. Please try again.';button.disabled=false;}};
  button.onclick=dismiss;dialog.addEventListener('cancel',event=>{event.preventDefault();void dismiss();});dialog.showModal();button.focus();return closed;
 }
 async function check(){
  if(checking||shown)return;checking=true;
  try{
   const saved=await chrome.storage.local.get([key,'enabled']);if(saved[key]===notes.version){finished=true;stop();return;}
   if(!saved.enabled||document.hidden||location.pathname!=='/'||document.querySelector('dialog[open]'))return;
   // The operation locks also cover maintained tools that do not register legacy jobs.
   if(!navigator.locks?.query)return;
   const locks=await navigator.locks.query();if(locks.held.some(lock=>/mcms-.*(build|upgrade)/.test(lock.name)))return;
   const response=await chrome.runtime.sendMessage({op:'whatsNewStatus'});if(!response?.ok||!Array.isArray(response.value?.jobs)||response.value.jobs.some(job=>job.state==='running'))return;
   await navigator.locks.request('tkb-whats-new',{ifAvailable:true},async lock=>{if(!lock)return;if((await chrome.storage.local.get(key))[key]===notes.version){finished=true;return;}await show();});
  }catch{/* Wait for the extension to reconnect; do not interrupt uncertain activity. */}
  finally{checking=false;if(!shown&&!finished)timer=setTimeout(check,10000);}
 }
 window.addEventListener('pagehide',stop,{once:true});
 if(manual)void show();else timer=setTimeout(check,5000);
})();
