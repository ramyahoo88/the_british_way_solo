/* Inject into an isolated browser session on the app's preview URL.
 * Exercises the shipped DOM controls, native File API, storage and reloads.
 * Results appear in #force136-qa-result. Never use in a player's saved session.
 */
(async()=>{
 const results=[],$=id=>document.getElementById(id),K='force136.deck.v1',B='force136.deck.backup.v1';
 const check=(condition,name)=>{if(!condition)throw Error(name);results.push(name);};
 const saved=()=>JSON.parse(localStorage.getItem(K));
 const wait=async fn=>{for(let i=0;i<100;i++){if(fn())return;await new Promise(r=>setTimeout(r,30));}throw Error('UI wait timed out');};
 const pickView=name=>document.querySelector('.tabs [data-view="'+name+'"]').click();
 let iframe;
 try{
  check($('draw').textContent==='Start game','fresh page waits for setup');
  $('draw').click();check($('setup-dialog').open,'setup opens');check($('setup-level-detail').textContent.includes('starts at 2'),'Agent starting Resistance shown');
  $('start-confirm').click();check(!saved().game.current&&saved().game.draws===0,'starting shuffles without drawing');
  const ids=[];
  for(let i=0;i<9;i++){$('draw').click();const g=saved().game;ids.push(g.current);check($('directive').textContent.includes('DIRECTIVE '+g.current+' / 9'),'draw '+(i+1)+' matches applied state');}
  check(new Set(ids).size===9,'all nine Directives appear once');
  check($('directive').textContent.includes('Pass in the leftmost free box'),'card retains the Pass fallback');
  const ninth=saved();$('draw').click();const tenth=saved();check(tenth.game.cycle===2&&tenth.game.deck.length===8,'tenth draw reshuffles discards');
  $('undo').click();check(JSON.stringify(saved().game)===JSON.stringify(ninth.game),'Undo restores the ninth card and piles');
  $('draw').click();check(JSON.stringify(saved().game)===JSON.stringify(tenth.game),'redrawing after Undo preserves the shuffle');
  document.querySelector('[data-mode="limited"]').click();check($('directive').querySelectorAll('.priority-list li').length===4,'Limited display has four priorities');
  check($('directive').textContent.includes('No Special Activity'),'Limited reminder is visible');
  document.querySelector('[data-mode="full"]').click();check($('directive').querySelectorAll('.priority-list li').length>=5,'full display restores its priorities');
  document.querySelector('#directive [data-goal="PLACE"]').click();check($('detail-dialog').open&&$('detail-content').textContent.includes('Contact'),'goal opens its actual procedure');
  $('detail-content').querySelector('[data-procedure="contact"]').click();$('detail-dialog').scrollTop=145;$('detail-content').querySelector('[data-procedure="raid"]').click();
  check($('detail-dialog').scrollTop===0&&$('detail-content').querySelector('h2').textContent==='Raid','switching a scrolled procedure opens at its beginning');
  check(document.activeElement===$('detail-content').querySelector('h2'),'new procedure heading receives focus');
  $('detail-content').querySelector('.detail-terms summary').click();check($('detail-content').querySelector('.detail-terms').textContent.includes('Good shot:')&&$('detail-content').querySelector('.detail-terms').textContent.includes('Exposed:'),'procedure Terms includes the printed definitions');$('detail-dialog').close();
  $('notes').focus();$('notes').value='J25 / R11 / <img src=x onerror=window.qaUnsafe=1>';$('notes').dispatchEvent(new Event('input',{bubbles:true}));$('notes').blur();
  check(!window.qaUnsafe&&saved().game.notes.includes('<img'),'notes are saved as text');
  pickView('rules');$('rule-search').value='J27';$('rule-search').dispatchEvent(new Event('input',{bubbles:true}));check([...document.querySelectorAll('.rule-section')].some(x=>x.hidden),'rules search filters sections');check($('rule-6').open&&!$('rule-6').hidden,'matching rules expand');
  pickView('reference');$('score-final').checked=true;
  for(const [r,c,f,w] of [[18,0,0,'MPAJA wins'],[19,1,2,'Force 136 wins'],[20,4,0,'Force 136 wins'],[17,0,3,'Japan wins']]){
   $('score-r').value=r;$('score-c').value=c;$('score-f').value=f;$('score-form').querySelector('[type=submit]').click();check($('score-result').textContent.startsWith(w),'final scoring '+r+'/'+c+'/'+f);
  }
  $('score-r').value=0;$('score-r').dispatchEvent(new Event('input',{bubbles:true}));check($('score-result').textContent==='','changed counts clear the previous winner');
  $('score-form').querySelector('[type=submit]').click();$('score-final').checked=false;$('score-final').dispatchEvent(new Event('change',{bubbles:true}));check($('score-result').textContent==='','unchecking final Propaganda clears the previous winner');
  $('score-c').value=5;check(!$('score-c').checkValidity(),'Camp input rejects more than four');$('score-c').value=4;
  $('score-f').value=4;check(!$('score-f').checkValidity(),'marker input rejects more than three');$('score-f').value=3;
  pickView('deck');$('save-open').click();let blob;const original=URL.createObjectURL;URL.createObjectURL=x=>{blob=x;return original(x);};$('export').click();const exported=await blob.text();URL.createObjectURL=original;check(JSON.parse(exported).game.draws===10,'export contains the current deck and notes');$('save-dialog').close();
  $('draw').click();$('draw').click();$('draw').click();const beforeImport=saved().game;
  const load=async text=>{const dt=new DataTransfer();dt.items.add(new File([text],'deck.json',{type:'application/json'}));$('save-file').files=dt.files;$('save-file').dispatchEvent(new Event('change',{bubbles:true}));await wait(()=>$('import-dialog').open||$('save-error').textContent);};
  pickView('reference');$('score-final').checked=true;$('score-form').querySelector('[type=submit]').click();
  $('save-open').click();await load(exported);check($('import-dialog').open,'import offers a review before replacement');$('import-confirm').click();check(saved().game.draws===10,'import applies the reviewed deck');check(!$('score-final').checked&&$('score-result').textContent==='','import resets final confirmation and winner even for the same game');$('undo').click();check(JSON.stringify(saved().game)===JSON.stringify(beforeImport),'Undo restores the pre-import deck and notes');
  $('save-open').click();const bad=JSON.parse(exported);bad.game.deck[0]=bad.game.current;await load(JSON.stringify(bad));check($('save-error').textContent.includes('nine Directives'),'damaged import is rejected');check(saved().game.draws===13,'rejected import leaves the deck intact');$('save-dialog').close();
  pickView('reference');$('score-final').checked=true;$('score-form').querySelector('[type=submit]').click();
  $('new-open').click();$('level').value='recruit';$('level').dispatchEvent(new Event('change'));$('start-confirm').click();check(saved().game.level==='recruit'&&$('level-reminder').textContent.includes('Skip Raid'),'Recruit reminder is shown');check(!$('score-final').checked&&$('score-result').textContent==='','new game clears the previous final result');
  pickView('reference');$('score-final').checked=true;$('score-form').querySelector('[type=submit]').click();pickView('deck');$('undo').click();check(saved().game.level==='agent'&&saved().game.draws===13,'Undo restores the prior game after reset');check(!$('score-final').checked&&$('score-result').textContent==='','Undo across game identities clears the previous final result');
  iframe=document.createElement('iframe');iframe.style.cssText='width:390px;height:844px;position:absolute;top:10000px;left:0;border:0';document.body.append(iframe);
  const reload=async suffix=>{await new Promise((resolve,reject)=>{iframe.onload=resolve;iframe.onerror=reject;iframe.src=new URL('index.html?qa='+suffix,location.href).href;});await wait(()=>iframe.contentDocument?.getElementById('draw'));};
  await reload('saved');let doc=iframe.contentDocument;check(doc.getElementById('directive').textContent.includes('DIRECTIVE '+beforeImport.current+' / 9'),'reload restores the current card');
  check(doc.documentElement.scrollWidth<=doc.documentElement.clientWidth,'390px mobile layout has no horizontal overflow');
  check(doc.getElementById('draw').getBoundingClientRect().bottom<=iframe.contentWindow.innerHeight,'mobile Draw control is visible without scrolling');
  check(doc.querySelector('[data-mode="limited"]').getBoundingClientRect().bottom<=iframe.contentWindow.innerHeight,'mobile priority selector is visible before the card');
  doc.getElementById('undo').click();check(saved().game.draws===12,'Undo survives reload');await wait(()=>$('notice').textContent.includes('Another tab changed'));check($('draw').disabled,'a second tab locks the stale deck');
  const goodBackup=localStorage.getItem(B);localStorage.setItem(K,'{broken');await reload('recovery');doc=iframe.contentDocument;
  check(doc.getElementById('notice').textContent.includes('Recovered your last valid autosave'),'damaged primary recovers the backup');
  check(doc.getElementById('directive').textContent.includes('DIRECTIVE '+JSON.parse(goodBackup).game.current+' / 9'),'recovery restores the actual backup card');
  doc.getElementById('draw').click();check(localStorage.getItem(B)===goodBackup,'recovery never rotates a damaged save over the good backup');check(doc.getElementById('notice').hidden,'successful save clears the recovered-backup notice');
  localStorage.setItem(K,'broken');localStorage.setItem(B,'also broken');await reload('damaged');doc=iframe.contentDocument;
  check(doc.getElementById('notice').textContent.includes('could not be opened'),'both damaged saves are reported');check(localStorage.getItem(K)==='broken','damaged data is not silently overwritten');
  doc.getElementById('draw').click();doc.getElementById('start-confirm').click();check(doc.getElementById('notice').hidden&&doc.getElementById('save-status').textContent==='Saved on this device.','starting a new saved game clears the damaged-save warning');
  const nativeSet=iframe.contentWindow.Storage.prototype.setItem;
  try{iframe.contentWindow.Storage.prototype.setItem=function(k,v){if(k===K)throw new DOMException('QA quota fault','QuotaExceededError');return nativeSet.call(this,k,v);};doc.getElementById('draw').click();check(doc.getElementById('notice').textContent.includes('Autosave is unavailable'),'a genuinely failing write shows its warning');}
  finally{iframe.contentWindow.Storage.prototype.setItem=nativeSet;}
  doc.getElementById('draw').click();check(doc.getElementById('notice').hidden&&doc.getElementById('save-status').textContent==='Saved on this device.','a successful retry clears the old storage-failure warning');
  document.querySelector('[data-mode="limited"]').click();check($('draw').disabled&&$('notice').textContent.includes('Another tab changed'),'display changes preserve the cross-tab conflict lock and warning');
  const offline=await fetch('./Force_136_Digital_Deck.html');const html=await offline.text();check(offline.ok&&html.includes('force136-data')&&!/\bsrc="https?:/.test(html),'offline HTML contains all runtime data without remote scripts');
  check((await fetch('./Force_136_Rules.pdf')).headers.get('content-type').includes('application/pdf'),'rules PDF is served as PDF');
  iframe.remove();
  const node=document.createElement('pre');node.id='force136-qa-result';node.textContent=JSON.stringify({passed:results.length,results});document.body.append(node);
 }catch(error){if(iframe)iframe.remove();const node=document.createElement('pre');node.id='force136-qa-result';node.textContent=JSON.stringify({passed:results.length,results,error:error.stack});document.body.append(node);}
})();
