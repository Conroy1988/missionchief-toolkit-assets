/* Theme only the game's top navigation; all controls and handlers stay native. */
(function(){'use strict';
function mount(doc){const nav=doc.getElementById('main_navbar');if(!nav||nav.classList.contains('tkb-topbar'))return null;const brand=nav.querySelector('a.navbar-brand[href="/"]'),logo=brand?.querySelector('img.logoSmall');let mark=null;const oldLabel=brand?.getAttribute('aria-label');if(logo){logo.classList.add('tkb-original-logo');mark=doc.createElement('span');mark.className='tkb-topbar-mark';mark.setAttribute('aria-hidden','true');brand.append(mark);if(!oldLabel)brand.setAttribute('aria-label','MissionChief home');}
 const style=doc.createElement('style');style.textContent=CSS;doc.head.append(style);nav.classList.add('tkb-topbar');return {destroy(){nav.classList.remove('tkb-topbar');logo?.classList.remove('tkb-original-logo');mark?.remove();if(brand&&oldLabel===null)brand.removeAttribute('aria-label');style.remove();}};
}
const CSS=`
html body #main_navbar.tkb-topbar{background:linear-gradient(180deg,#17191c 0%,#080a0c 100%)!important;border:0!important;border-bottom:1px solid #8d2631!important;box-shadow:0 2px 8px #0005!important;color:#eef0f3!important}
html body #main_navbar.tkb-topbar .navbar-header,html body #main_navbar.tkb-topbar .navbar-collapse{background:transparent!important;border-color:#34383e!important}
html body #main_navbar.tkb-topbar .navbar-nav>li>a{background:transparent!important;color:#e4e8ee!important;text-shadow:none!important;transition:background-color .12s ease,color .12s ease}
html body #main_navbar.tkb-topbar .navbar-nav>li>a:hover,html body #main_navbar.tkb-topbar .navbar-nav>li>a:focus,html body #main_navbar.tkb-topbar .navbar-nav>.open>a,html body #main_navbar.tkb-topbar .navbar-nav>.active>a{background:#29181d!important;color:#fff!important;box-shadow:inset 0 -2px #ed384a!important}
html body #main_navbar.tkb-topbar .navbar-nav>li>a.highlight,html body #main_navbar.tkb-topbar .navbar-nav>li>a.alliance_forum_new,html body #main_navbar.tkb-topbar .navbar-nav>li>a.alliance_apply_new{background:#331b22!important;box-shadow:inset 0 -3px #ff5266!important;color:#fff!important}
html body #main_navbar.tkb-topbar .navbar-text,html body #main_navbar.tkb-topbar .sale-countdown-block{color:#e5d4d7!important;background:transparent!important}
html body #main_navbar.tkb-topbar .dropdown-menu{background:#111519!important;border:1px solid #454a52!important;border-top:2px solid #c92f42!important;border-radius:0 0 7px 7px!important;box-shadow:0 12px 25px #0006!important}
html body #main_navbar.tkb-topbar .dropdown-menu>li>a{background:transparent!important;color:#e4e8ef!important;text-shadow:none!important}
html body #main_navbar.tkb-topbar .dropdown-menu>li>a:hover,html body #main_navbar.tkb-topbar .dropdown-menu>li>a:focus{background:#302027!important;color:#fff!important}
html body #main_navbar.tkb-topbar .dropdown-menu>.disabled>a{color:#929aa5!important}html body #main_navbar.tkb-topbar .dropdown-header{color:#bdc4cd!important}html body #main_navbar.tkb-topbar .dropdown-menu .divider{background:#373d44!important}
html body #main_navbar.tkb-topbar #map_adress_search{background:#22262b!important;border:1px solid #555c66!important;border-radius:4px!important;color:#f3f5f7!important;padding-left:7px!important}
html body #main_navbar.tkb-topbar #map_adress_search::placeholder{color:#b6bdc6!important;opacity:1}
html body #main_navbar.tkb-topbar #map_adress_search:focus{outline:2px solid #e04b5b!important;outline-offset:1px!important}
html body #main_navbar.tkb-topbar .navbar-toggle{background:#1c2025!important;border-color:#5b626c!important}html body #main_navbar.tkb-topbar .navbar-toggle .icon-bar{background:#e1e5eb!important}
html body #main_navbar.tkb-topbar .navbar-toggle.alliance_forum_new{box-shadow:inset 0 -3px #ff5266!important}
html body #main_navbar.tkb-topbar .badge{background:#95303f!important;color:#fff!important}
html body #main_navbar.tkb-topbar a.navbar-brand{background:transparent!important}html body #main_navbar.tkb-topbar a.navbar-brand .tkb-original-logo{display:none!important}
html body #main_navbar.tkb-topbar .tkb-topbar-mark{display:inline-block!important;width:23px;height:25px;vertical-align:middle;background:#ef2929;-webkit-mask:url("data:image/svg+xml,%3Csvg%20xmlns%3D%22http%3A%2F%2Fwww.w3.org%2F2000%2Fsvg%22%20viewBox%3D%220%200%2030%2032%22%3E%3Cpath%20d%3D%22M12%201h7L7%2031H0z%20M23%201h7L18%2031h-7z%22%2F%3E%3C%2Fsvg%3E") center/contain no-repeat;mask:url("data:image/svg+xml,%3Csvg%20xmlns%3D%22http%3A%2F%2Fwww.w3.org%2F2000%2Fsvg%22%20viewBox%3D%220%200%2030%2032%22%3E%3Cpath%20d%3D%22M12%201h7L7%2031H0z%20M23%201h7L18%2031h-7z%22%2F%3E%3C%2Fsvg%3E") center/contain no-repeat}
html body #main_navbar.tkb-topbar a:focus-visible,html body #main_navbar.tkb-topbar button:focus-visible{outline:2px solid #ffabb5!important;outline-offset:-3px!important}
@media(prefers-reduced-motion:reduce){html body #main_navbar.tkb-topbar .navbar-nav>li>a{transition:none}}
`;
if(typeof module!=='undefined'&&module.exports){module.exports={mount,CSS};return;}
let view=null,generation=0;async function start(){const run=++generation;try{const settings=await chrome.storage.local.get('enabled');if(run!==generation)return;if(settings.enabled===false){view?.destroy();view=null;}else if(!view)view=mount(document);}catch{}}
void start();chrome.storage.onChanged.addListener((c,a)=>{if(a==='local'&&c.enabled)void start();});
})();
