import vm from 'node:vm';
import fs from 'node:fs';
import path from 'node:path';
import assert from 'node:assert/strict';
import {fileURLToPath} from 'node:url';
const root=path.resolve(path.dirname(fileURLToPath(import.meta.url)),'..');
const source=fs.readFileSync(path.join(root,'src/app.js'),'utf8');
const verseText=JSON.parse(fs.readFileSync(path.join(root,'data/krv.json'),'utf8')).JHN['3'].find(r=>r[0]==='16')[1];
const html=fs.readFileSync(path.join(root,'docs/krv/jhn/3/index.html'),'utf8');
const baseConfig=JSON.parse(html.match(/<script type="application\/json" id="page-config">(.*?)<\/script>/s)[1]);
function setup({mode='clipboard',hash='',ui='ko'}={}){
 const events={},calls={copies:[],shares:[],navigation:[],dialog:0},storage=new Map(), nodes=new Map();
 function node(extra={}){return {listeners:{},dataset:{},style:{},textContent:'',value:'',disabled:false,addEventListener(t,f){this.listeners[t]=f;},setAttribute(k,v){this[k]=v;},focus(){},select(){},remove(){},...extra};}
 const config={...baseConfig,base:ui==='ko'?'/bible-viewer/':'/bible-viewer/en/'};
 const status=node();const picker=node({value:'1'});const version=node({value:'krv'});const book=node({value:'jhn'});const chapter=node({value:'3'});
 const area=node();const dialog=node({querySelector(){return area;},showModal(){calls.dialog++;},close(){calls.dialog--;}});
 const article=node({dataset:{verse:'16'},querySelector(){return {textContent:verseText};}});
 for(const [k,v] of Object.entries({'#page-config':node({textContent:JSON.stringify(config)}),'#status':status,'#verse-picker':picker,'#book-picker':book,'#chapter-picker':chapter,'#copy-dialog':dialog}))nodes.set(k,v);
 const location={hash,assign(url){calls.navigation.push(url);}};
 const theme=node();
 const document={documentElement:{dataset:{},style:{setProperty(k,v){calls[k]=v;}}},querySelector(selector){return selector==='[data-action=theme]'?theme:nodes.get(selector)||null;},querySelectorAll(selector){return selector==='[data-version-picker]'?[version]:[];},getElementById(id){return id==='v16'?article:id==='v1'?article:null;},addEventListener(t,f){events[t]=f;},createElement(){return node();},body:{appendChild(){}},execCommand(){return false;}};
 const navigator={clipboard:{async writeText(value){if(mode==='denied')throw new Error('Denied');calls.copies.push(value);}}};
 if(['native','abort','share-denied'].includes(mode))navigator.share=async payload=>{if(mode==='abort')throw Object.assign(new Error(),{name:'AbortError'});if(mode==='share-denied')throw new Error('Denied');calls.shares.push(payload);};
 const context={document,navigator,location,localStorage:{getItem:k=>storage.get(k),setItem:(k,v)=>storage.set(k,v)},setTimeout:()=>1,clearTimeout(){},window:{addEventListener(t,f){events[t]=f;}}};
 vm.runInNewContext(source,context);
 async function click(action){const button=node({dataset:{action},closest(){return article;}});await events.click({target:{closest(){return button;}}});assert.equal(button.disabled,false);}
 return {calls,picker,version,book,chapter,status,area,dialog,click,location,storage,document};
}
const expected=`요한복음 3:16 · 개역한글판\n${verseText}\nhttps://nanalab.kr/bible-viewer/krv/jhn/3/#v16`;
let tested=0;
{
 const s=setup();await s.click('copy');assert.equal(s.calls.copies[0],expected);assert.equal(s.status.textContent,baseConfig.labels.copied);tested++;
}
{
 const s=setup({mode:'native'});await s.click('share');assert.equal(s.calls.shares[0].text,expected.split('\n').slice(0,2).join('\n'));assert.equal(s.calls.shares[0].url,expected.split('\n').at(-1));assert.equal(s.calls.copies.length,0);tested++;
}
{
 const s=setup();await s.click('share');assert.equal(s.calls.copies[0],expected);assert.equal(s.status.textContent,baseConfig.labels.shareCopied);tested++;
}
{
 const s=setup({mode:'share-denied'});await s.click('share');assert.equal(s.calls.copies[0],expected);tested++;
}
{
 const s=setup({mode:'abort'});await s.click('share');assert.equal(s.calls.copies.length,0);assert.equal(s.status.textContent,'');tested++;
}
{
 const s=setup({mode:'denied'});await s.click('copy');assert.equal(s.calls.dialog,1);assert.equal(s.area.value,expected);await s.click('close-dialog');assert.equal(s.calls.dialog,0);tested++;
}
{
 const s=setup({hash:'#v16',ui:'en'});s.version.value='bsb';s.version.listeners.change();assert.equal(s.calls.navigation[0],'/bible-viewer/en/bsb/jhn/3/#v16');tested++;
}
{
 const s=setup({hash:'#v16'});await s.click('share-selected');assert.equal(s.calls.copies[0],expected);assert.equal(s.picker.value,'16');tested++;
}
{
 const s=setup({hash:'#v999'});assert.equal(s.status.textContent,baseConfig.labels.missingVerse);s.picker.value='16';await s.click('share-selected');assert.equal(s.calls.copies[0],expected);tested++;
}
{
 const s=setup();s.book.value='rev';s.book.listeners.change();assert.equal(s.calls.navigation[0],'/bible-viewer/krv/rev/1/');s.chapter.value='4';s.chapter.listeners.change();assert.equal(s.calls.navigation[1],'/bible-viewer/krv/jhn/4/');tested++;
}
{
 const s=setup();for(let i=0;i<30;i++)await s.click('font-up');assert.equal(s.calls['--verse-size'],'28px');for(let i=0;i<30;i++)await s.click('font-down');assert.equal(s.calls['--verse-size'],'16px');await s.click('theme');assert.equal(s.storage.get('bible-viewer-theme'),'dark');tested++;
}
const report={status:'passed',behavior_cases:tested,verse_and_canonical_url_copy:true,native_share_payload:true,share_fallback:true,share_cancel:true,manual_copy_fallback:true,same_chapter_version_switch:true,selected_verse_share:true,missing_verse_fallback:true,book_chapter_navigation:true,font_limits_and_theme:true};
fs.writeFileSync(path.join(root,'evidence/runtime-check.json'),JSON.stringify(report,null,2)+'\n');console.log(JSON.stringify(report));
