/* Final userscript migration notice. No game requests or setting deletion. */
(function () {
  'use strict';
  if (window.top !== window.self) return;
  const id = 'tkb-extension-migration-notice';
  const key = 'tkb-extension-migration-snooze-v1';
  const store = 'https://chromewebstore.google.com/detail/lmnojpchebgcochdfnfjmnficicnaaoc';
  const guide = 'https://github.com/Conroy1988/missionchief-toolkit-assets/blob/main/docs/MIGRATING_FROM_USERSCRIPT.md';
  function show() {
    if (!document.body || document.getElementById(id)) return;
    try { if (Number(localStorage.getItem(key)) > Date.now()) return; } catch (_) {}
    const host = document.createElement('aside');
    host.id = id;
    host.style.cssText = 'position:fixed;left:12px;bottom:12px;z-index:2147483647;width:min(400px,calc(100vw - 24px));';
    const root = host.attachShadow({mode: 'open'});
    const css = document.createElement('style');
    css.textContent = ':host{color-scheme:dark}*{box-sizing:border-box}.notice{background:#151820;color:#f5f6fa;border:1px solid #e43b4e;border-radius:12px;padding:20px;box-shadow:0 8px 32px #0008;font:14px/1.5 Arial,sans-serif;max-height:70vh;overflow:auto}h2{font-size:20px;line-height:1.2;margin:0 0 12px}p{margin:8px 0;color:#cbd2de}a{color:#fff}nav{display:flex;flex-wrap:wrap;gap:10px;margin:16px 0}.store{background:#c92d40;color:white;border-radius:6px;padding:9px 12px;text-decoration:none;font-weight:bold}button{font:inherit;background:#242936;color:#fff;border:1px solid #647087;border-radius:6px;padding:8px 12px;cursor:pointer}a:focus-visible,button:focus-visible{outline:3px solid #fff;outline-offset:3px}small{display:block;color:#a8b2c5;margin-top:12px}';
    const panel = document.createElement('section');
    panel.className = 'notice';panel.setAttribute('role','region');panel.setAttribute('aria-label','Toolkit extension migration');
    const h = document.createElement('h2');h.textContent = 'The Toolkit has moved to the Chrome Web Store';panel.append(h);
    for (const text of ['The Tampermonkey/userscript edition is no longer supported. Install the extension for supported updates.', 'Export any settings you need, then disable this Toolkit script before enabling the extension. You can keep Tampermonkey for other scripts.']) {
      const paragraph = document.createElement('p');paragraph.textContent = text;panel.append(paragraph);
    }
    const nav = document.createElement('nav');
    for (const [label,url,cls] of [['Get the extension',store,'store'],['Migration guide',guide,'']]) {
      const a = document.createElement('a');a.textContent=label;a.href=url;a.target='_blank';a.rel='noopener noreferrer';a.className=cls;nav.append(a);
    }
    panel.append(nav);
    const later = document.createElement('button');later.type='button';later.textContent='Remind me in 7 days';
    later.addEventListener('click',function(){try{localStorage.setItem(key,String(Date.now()+7*24*60*60*1000));}catch(_){}host.remove();});panel.append(later);
    const note=document.createElement('small');note.textContent='Your existing settings are untouched. The extension supports MissionChief UK; browser compatibility varies.';panel.append(note);
    root.append(css,panel);document.body.append(host);
  }
  if (document.readyState === 'loading') document.addEventListener('DOMContentLoaded',show,{once:true}); else show();
})();
