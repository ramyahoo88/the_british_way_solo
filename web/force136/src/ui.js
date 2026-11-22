(function(){
 'use strict';
 const C=window.Force136Deck,D=JSON.parse(document.getElementById('force136-data').textContent);
 const $=id=>document.getElementById(id), title=s=>s[0].toUpperCase()+s.slice(1);
 const storage={getItem:k=>window.localStorage.getItem(k),setItem:(k,v)=>window.localStorage.setItem(k,v)};
 const restored=C.recover(storage);let game=restored.save?.game||null,undo=restored.save?.undo||[],mode='full',pending=null,locked=false,notesBefore=null,notesRecorded=false;
 const levels={recruit:{start:2,text:'Resistance starts at 2. Skip Raid everywhere it appears in a Special Activity list.'},agent:{start:2,text:'Resistance starts at 2. Use the standard Force 136 rules.'},veteran:{start:4,text:'Resistance starts at 4.'},legend:{start:4,text:'Resistance starts at 4. Add 1 Resistance after each nonfinal Propaganda, after the Resistance phase and Zipper placement. The bonus does not move the Zipper.'},mastermind:{start:6,text:'Resistance starts at 6. Add 2 Resistance after each nonfinal Propaganda, after the Resistance phase and Zipper placement. The bonus does not move the Zipper.'}};
 try{const prefs=JSON.parse(storage.getItem('force136.display')||'{}');if(prefs.mode==='limited')mode='limited';}catch(_){}
 let noticeReason='';
 function notice(message,reason=''){noticeReason=reason;$('notice').textContent=message;$('notice').hidden=!message;}
 if(restored.notice==='recovered')notice('Recovered your last valid autosave. The most recent save was damaged; your backup deck is open.','recovered');
 if(restored.notice==='damaged')notice('The saved deck could not be opened. Import a backup or start a new game. The damaged save has been left in place.','damaged');
 if(restored.notice==='storage')notice('Autosave is unavailable in this browser. Export a save before closing the app.','storage');
 function persist(){if(!game)return;const ok=C.persist(storage,C.envelope(game,undo));$('save-status').textContent=ok?'Saved on this device.':'Not saved — export a backup.';if(!ok)notice('Autosave is unavailable. Your deck still works here; export a save before closing.','storage');else if(['storage','damaged','recovered'].includes(noticeReason))notice('');}
 function clearScore(reset=false){$('score-result').textContent='';if(reset)$('score-form').reset();}
 function replace(next,keepUndo=true,resetScore=false){if(locked)return;const validated=C.validateGame(next);if(resetScore||game?.id!==validated.id)clearScore(true);if(game&&keepUndo)undo.push(C.clone(game));undo=undo.slice(-30);game=validated;persist();render();}
 function openDialog(id){const d=$(id);if(!d.open)d.showModal();}
 function showView(view){
  document.querySelectorAll('.view').forEach(n=>n.hidden=n.id!=='view-'+view);
  document.querySelectorAll('.tabs button').forEach(n=>{if(n.dataset.view===view)n.setAttribute('aria-current','page');else n.removeAttribute('aria-current');});
  if(view==='history')renderHistory();
 }
 function showRule(number){showView('rules');$('rule-search').value='';filterRules();const section=$('rule-'+number);section.open=true;section.scrollIntoView({behavior:'auto',block:'start'});}
 function showDetail(kind,key){
  const safeName=kind==='goal'?key:title(key),html=kind==='goal'?D.goals[key]:D.procedures[key];
  if(!html)return;
  $('detail-content').innerHTML='<p class="eyebrow">'+(kind==='goal'?'GOAL · RULE 5':'PROCEDURE · RULE 6')+'</p><h2 tabindex="-1">'+safeName+'</h2><details class="detail-terms"><summary>Terms</summary>'+D.terms+'</details>'+html+(game?.level==='recruit'?'<p class="callout">Recruit: skip Raid in every Special Activity list.</p>':'')+'<div class="detail-procedures">'+Object.keys(D.procedures).map(p=>'<button class="text-button" data-procedure="'+p+'">'+title(p)+'</button>').join('')+'</div>';
  openDialog('detail-dialog');
  $('detail-content').querySelector('h2').focus({preventScroll:true});
  $('detail-dialog').scrollTop=0;
 }
 function renderCard(){
  const target=$('directive');
  if(!game||game.current===null){target.innerHTML='<div class="empty-card"><div><div class="seal" aria-hidden="true">136</div><h2>'+(!game?'Your Directive deck':game.draws?'Turn complete.':'The deck is shuffled.')+'</h2><p>'+(!game?'Nine cards replace the printed Directive deck. Set up your board, choose a level, and begin.':'Reveal a Directive when Force 136 is to act on the current official Event card.')+'</p></div></div>';return;}
  const card=D.cards.find(c=>c.id===game.current),order=mode==='full'?['PLACE',...card.goals,'CONTACT']:['PLACE',card.limited_first,card.limited_first==='AMBUSH'?'TRAIN':'AMBUSH','CONTACT'];
  target.innerHTML='<div class="directive-top"><span>FORCE 136</span><span>DIRECTIVE '+card.id+' / 9</span></div><div class="card-main"><h2>'+card.name+'</h2><p class="card-subtitle">Draw '+game.draws+' · Cycle '+game.cycle+'</p><p class="priority-label">'+(mode==='full'?'OPERATION & SPECIAL ACTIVITY':'LIMITED OPERATION')+'</p><ol class="priority-list">'+order.map((g,i)=>'<li><button data-goal="'+g+'" aria-label="'+g+' goal details"><span class="order-number">'+(i+1)+'</span><span class="goal-word goal-'+g+'">'+g+'</span>'+(['PLACE','CONTACT'].includes(g)?'<span class="order-note">'+(g==='PLACE'?'if Available':'fallback')+'</span>':'')+'</button></li>').join('')+'</ol></div><div class="card-bottom"><p>'+ (mode==='full'?'Use the first goal that qualifies. Resolve the Operation, then choose its Special Activity.':'Use the first goal that qualifies. No Special Activity. British Limited Train or Ambush may still use every F136 space.')+(game.level==='recruit'?' <strong>Recruit: skip Raid.</strong>':'')+'</p><p>If nothing qualifies, Pass in the leftmost free box, without Contact. The Event box is closed on J6 and J9.</p></div>';
 }
 function renderHistory(){
  const rows=game?.history.slice().reverse()||[];$('history-empty').hidden=rows.length>0;
  $('history-list').innerHTML=rows.map(e=>{const c=D.cards.find(c=>c.id===e.card),active=e.turn===game.draws&&game.current!==null;return '<li><span class="history-turn">Draw '+e.turn+'</span><span class="history-name">'+c.name+'<span class="history-meta">Directive '+c.id+' · cycle '+e.cycle+'</span></span><span class="pill">'+(active?'Current':e.cycle===game.cycle?'Discarded':'Earlier cycle')+'</span></li>';}).join('');
 }
 function render(){
  document.body.classList.toggle('has-game',!!game);
  renderCard();renderHistory();
  $('draw').textContent=!game?'Start game':game.current!==null?'Draw next Directive':'Draw Directive';
  $('draw').disabled=locked;$('undo').disabled=locked||undo.length===0;$('finish').disabled=locked||!game||game.current===null;$('new-open').disabled=locked;$('notes').disabled=locked||!game;
  if(document.activeElement!==$('notes'))$('notes').value=game?.notes||'';
  $('pile-counts').textContent=game?game.deck.length+' in deck · '+game.discard.length+' discarded'+(game.current!==null?' · 1 current':''):'9 Directives';
  $('cycle-count').textContent=game?'Cycle '+game.cycle:'Automatic reshuffle';
  $('session-badge').textContent=game?title(game.level)+' · '+game.draws+' Directive'+(game.draws===1?'':'s')+' drawn':'Nine cards. Ready when you are.';
  $('level-reminder').hidden=!game||game.level==='agent';$('level-reminder').textContent=game?title(game.level)+': '+levels[game.level].text:'';
  $('level-detail').textContent=game?title(game.level)+'. '+levels[game.level].text:'Choose a level when starting. Start at Agent and move up after two wins in a row.';
  $('export').disabled=!game;$('import').disabled=locked;$('import-confirm').disabled=locked;$('start-confirm').disabled=locked;
  $('save-summary').textContent=game?title(game.level)+' · '+game.draws+' Directives drawn · cycle '+game.cycle+'.':'Start a game to save a deck.';
  document.querySelectorAll('[data-mode]').forEach(n=>n.setAttribute('aria-pressed',String(n.dataset.mode===mode)));
  $('mode-help').textContent=mode==='full'?'Resolve the Operation first, then choose the Special Activity from the resulting board.':'No Special Activity. Limited Train and Ambush can still use every eligible F136 space.';
 }
 function openSetup(){if(locked)return;$('level').value=game?.level||'agent';$('setup-level-detail').textContent=levels[$('level').value].text;$('replace-warning').hidden=!game;openDialog('setup-dialog');}
 function filterRules(){const query=$('rule-search').value.trim().toLowerCase();let count=0;document.querySelectorAll('.rule-section').forEach(section=>{section.hidden=!!query&&!section.textContent.toLowerCase().includes(query);if(!section.hidden){count++;if(query)section.open=true;}});$('search-count').textContent=query?count+' matching section'+(count===1?'':'s')+(count?'':'. Try a shorter term.'):'All 11 sections. Open a heading to read.';}
 document.addEventListener('click',e=>{
  const b=e.target.closest('button');if(!b)return;
  if(b.dataset.view)showView(b.dataset.view);
  if(b.dataset.rule)showRule(b.dataset.rule);
  if(b.dataset.goal)showDetail('goal',b.dataset.goal);
  if(b.dataset.procedure)showDetail('procedure',b.dataset.procedure);
  if(b.dataset.close)$(b.dataset.close).close();
  if(b.dataset.mode){mode=b.dataset.mode;try{storage.setItem('force136.display',JSON.stringify({mode}));}catch(_){}render();}
 });
 $('draw').addEventListener('click',()=>{if(!game){openSetup();return;}replace(C.draw(game));});
 $('finish').addEventListener('click',()=>{if(game?.current!==null&&game)replace(C.finishTurn(game));});
 $('undo').addEventListener('click',()=>{if(locked||!undo.length)return;const previous=undo.pop();if(game?.id!==previous.id)clearScore(true);game=previous;persist();render();});
 $('new-open').addEventListener('click',openSetup);
 $('level').addEventListener('change',()=>$('setup-level-detail').textContent=levels[$('level').value].text);
 $('start-confirm').addEventListener('click',()=>{if(locked)return;let seed;const a=new Uint32Array(1);if(window.crypto?.getRandomValues){crypto.getRandomValues(a);seed=a[0]||1;}else seed=((Date.now()^Math.floor(Math.random()*4294967295))>>>0)||1;replace(C.newGame($('level').value,seed,'game-'+Date.now()+'-'+seed));$('setup-dialog').close();showView('deck');});
 $('notes').addEventListener('focus',()=>{notesBefore=game?C.clone(game):null;notesRecorded=false;});
 $('notes').addEventListener('blur',()=>{notesBefore=null;notesRecorded=false;});
 $('notes').addEventListener('input',()=>{if(!game||locked)return;if(!notesRecorded){undo.push(C.clone(notesBefore||game));undo=undo.slice(-30);notesRecorded=true;$('undo').disabled=false;}game.notes=$('notes').value;persist();});
 $('save-open').addEventListener('click',()=>{render();$('save-error').textContent='';openDialog('save-dialog');});
 function download(content,type,filename){const url=URL.createObjectURL(new Blob([content],{type}));const a=document.createElement('a');a.href=url;a.download=filename;document.body.appendChild(a);a.click();a.remove();setTimeout(()=>URL.revokeObjectURL(url),1000);}
 $('export').addEventListener('click',()=>{if(game)download(JSON.stringify(C.envelope(game,undo),null,2),'application/json','Force_136_draw_'+game.draws+'.json');});
 $('import').addEventListener('click',()=>{$('save-file').value='';$('save-file').click();});
 $('save-file').addEventListener('change',async()=>{const file=$('save-file').files[0];if(!file)return;try{if(file.size>C.MAX_SAVE_BYTES)throw new Error('Save file exceeds the 4 MB limit.');pending=C.parseSave(await file.text());const g=pending.game;$('import-summary').textContent=title(g.level)+' · '+g.draws+' Directives drawn · cycle '+g.cycle+(g.current===null?'. No current Directive.':'. Current: '+D.cards.find(c=>c.id===g.current).name+'.');$('save-dialog').close();openDialog('import-dialog');}catch(error){$('save-error').textContent=error.message;}});
 $('import-confirm').addEventListener('click',()=>{if(!pending||locked)return;if(!game)undo=pending.undo;replace(pending.game,!!game,true);pending=null;$('import-dialog').close();showView('deck');});
 $('levels-open').addEventListener('click',()=>showRule('9'));
 $('rule-search').addEventListener('input',filterRules);
 $('print-rules').addEventListener('click',()=>{$('rule-search').value='';filterRules();document.querySelectorAll('.rule-section').forEach(n=>n.open=true);window.print();});
 for(const event of ['input','change'])$('score-form').addEventListener(event,()=>clearScore());
 $('score-form').addEventListener('submit',e=>{e.preventDefault();if(!$('score-final').checked)return;try{const winner=C.winner(Number($('score-r').value),Number($('score-c').value),Number($('score-f').value));$('score-result').textContent=winner==='MPAJA'?'MPAJA wins. Both Japan and Force 136 lose.':winner==='Japan'?'Japan wins.':'Force 136 wins. Japan loses.';}catch(error){$('score-result').textContent=error.message;}});
 window.addEventListener('storage',e=>{if(e.key!==C.KEY)return;locked=true;notice('Another tab changed this deck. Reload this page before drawing, or export your current deck first.','conflict');const b=document.createElement('button');b.className='text-button';b.textContent='Reload saved deck';b.addEventListener('click',()=>location.reload());$('notice').appendChild(b);render();});
 const descriptions={PLACE:'An Available Force 136 marker.',AMBUSH:'A useful Ambush in a F136 space.',INTEL:'An Operation that lets Gather reveal 2+.',SUPPLY:'Directive 9: Train, then convert a Camp.',TRAIN:'Place at least one guerrilla.',CONTACT:'Place or move a Force 136 marker.'};
 $('goal-grid').innerHTML=Object.keys(descriptions).map(g=>'<button class="goal-tile goal-'+g+'" data-goal="'+g+'">'+g+'<small>'+descriptions[g]+'</small></button>').join('');
 $('procedure-links').innerHTML=Object.keys(D.procedures).map(p=>'<button class="text-button" data-procedure="'+p+'">'+title(p)+'</button>').join('');
 filterRules();render();
 if(game&&restored.notice!=='storage')$('save-status').textContent=restored.notice==='recovered'?'Backup recovered on this device.':'Saved deck restored.';
})();
