import test from 'node:test';import assert from 'node:assert/strict';import {readFileSync} from 'node:fs';import {createRequire} from 'node:module';
const {JSDOM}=createRequire(new URL('../home-response/package.json',import.meta.url))('jsdom');
const html=readFileSync(new URL('popup.html',import.meta.url),'utf8'),js=readFileSync(new URL('popup.js',import.meta.url),'utf8');
async function setup({url='https://www.missionchief.co.uk/',running=false,callback=false}={}){
 const dom=new JSDOM(html,{url:'https://extension.test/',runScripts:'outside-only'}),w=dom.window,calls=[];
 w.setInterval=()=>1;w.close=()=>calls.push('close');
 w.chrome={runtime:{getManifest:()=>({version:'1.3.0'}),sendMessage:(m,cb)=>{calls.push(m.op);const value={ok:true,value:{jobs:running?[{tabId:7,state:'running'}]:[]}};if(callback){setTimeout(()=>cb(value),0);return Promise.resolve();}return Promise.resolve(value);}},storage:{local:{get:async()=>({enabled:false}),set:async value=>calls.push(value)}},tabs:{query:async()=>[{id:7,url}],sendMessage:async()=>({state:'off',saving:'saved'}),reload:async id=>calls.push(['reload',id])}};
 w.eval(js);await new Promise(r=>setTimeout(r,25));return {w,calls,dom};
}
test('minimal popup links are correct and no old setup or task panels remain',()=>{
 const dom=new JSDOM(html),d=dom.window.document;assert.equal(d.querySelector('.support').href,'https://discord.gg/mXnTHuNfvu');assert.equal(d.querySelector('.kofi').href,'https://ko-fi.com/D4P124RWI9');assert.equal(d.querySelectorAll('button').length,1);assert.equal(d.querySelector('#setup,#connection,#workspace,.stats,.job'),null);dom.window.close();
});
test('apply saves choice and reloads the active game tab with callback-only response',async()=>{
 const {w,calls,dom}=await setup({callback:true});w.document.querySelector('#enabled').checked=true;w.document.querySelector('#reload').click();await new Promise(r=>setTimeout(r,30));assert.ok(calls.some(v=>v?.enabled===true));assert.ok(calls.some(v=>Array.isArray(v)&&v[0]==='reload'&&v[1]===7));dom.window.close();
});
test('unsupported pages and running tasks do not allow reload',async()=>{
 for(const options of [{url:'https://example.com/'},{running:true}]){const {w,calls,dom}=await setup(options);assert.equal(w.document.querySelector('#reload').disabled,true);assert.equal(calls.some(v=>Array.isArray(v)&&v[0]==='reload'),false);dom.window.close();}
});
