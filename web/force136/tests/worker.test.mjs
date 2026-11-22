import {test} from 'node:test';
import assert from 'node:assert/strict';
import fs from 'node:fs';
import worker from '../deployment/pages-worker.mjs';
const env={ASSETS:{fetch:async()=>new Response('Existing static asset',{status:200})}};
const call=(p,method='GET')=>worker.fetch(new Request('https://example.com'+p,{method}),env);
test('App routes serve the exact reviewed standalone HTML',async()=>{
 const expected=fs.readFileSync(new URL('../dist/index.html',import.meta.url),'utf8');
 for(const path of ['/games/force136/','/games/force136/index.html','/games/force136/Force_136_Digital_Deck.html','/downloads/force136']){
  const r=await call(path);assert.equal(r.status,200);assert.equal(await r.text(),expected);
 }
 assert.equal((await call('/downloads/force136')).headers.get('content-disposition'),'attachment; filename="Force_136_Digital_Deck.html"');
});
test('Catalog retains the old companions and adds Force 136 exactly once',async()=>{
 const home=await (await call('/')).text();assert.equal((home.match(/id="force136-title"/g)||[]).length,1);
 const before=fs.readFileSync(new URL('../deployment/home_before.html',import.meta.url),'utf8');
 for(const article of before.matchAll(/<article\b[\s\S]*?<\/article>/g))assert.ok(home.includes(article[0]),'An old companion changed');
 assert.equal((home.match(/<article\b/g)||[]).length,11);
});
test('Every linked printable PDF is unchanged; HEAD, 404 and method handling work',async()=>{
 const printables=JSON.parse(fs.readFileSync(new URL('../source_data/printables.json',import.meta.url),'utf8'));
 const hub=await (await call('/games/force136/printables/')).text();
 assert.equal(hub,fs.readFileSync(new URL('../dist/printables.html',import.meta.url),'utf8'));
 assert.equal(await (await call('/games/force136/printables/index.html')).text(),hub);
 const app=await (await call('/games/force136/')).text();
 assert.ok(!app.includes('github.com')&&!hub.includes('github.com'));
 for(const item of printables){
  assert.ok(hub.includes('../'+item.file),'A printable is missing from the downloads page');
  assert.ok(app.includes('/games/force136/'+item.file),'A printable is missing from the Rules tab');
  const path='/games/force136/'+item.file;
  const pdf=await call(path);assert.equal(pdf.status,200);assert.equal(pdf.headers.get('content-type'),'application/pdf');
  assert.deepEqual(Buffer.from(await pdf.arrayBuffer()),fs.readFileSync(new URL('../source_data/'+item.file,import.meta.url)));
  const head=await call(path,'HEAD');assert.equal(head.headers.get('content-type'),'application/pdf');assert.equal(await head.text(),'');
 }
 assert.equal(await (await call('/games/force136/','HEAD')).text(),'');
 assert.equal(await (await call('/games/force136/printables/','HEAD')).text(),'');
 assert.equal((await call('/games/force136/missing.js')).status,404);
 assert.equal((await call('/games/force136/missing.pdf')).status,404);
 assert.equal((await call('/games/force136/','POST')).status,405);
 assert.equal((await call('/games/force136')).status,308);
 assert.equal((await call('/games/force136/printables')).status,308);
});
test('Other companions use retained static assets and download headers remain',async()=>{
 assert.equal(await (await call('/games/pendragon/')).text(),'Existing static asset');
 const headers=fs.readFileSync(new URL('../deployment/headers.txt',import.meta.url),'utf8');
 assert.ok(headers.includes('A_Glorious_Chance_Solo_v0.2.18.html'));assert.ok(headers.includes('Pendragon_Solo_v1.0.0.html'));
 const routes=JSON.parse(fs.readFileSync(new URL('../deployment/routes.json',import.meta.url),'utf8'));
 assert.ok(!routes.include.includes('/*'));assert.ok(!routes.include.includes('/games/*'));
});
