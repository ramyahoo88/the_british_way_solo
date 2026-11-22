const {test}=require('node:test');
const assert=require('node:assert/strict');
const C=require('../src/core.js');
const memory=()=>{const map=new Map();return {getItem:k=>map.get(k)??null,setItem:(k,v)=>map.set(k,v),map};};
test('Nine unique Directives per cycle across 1000 seeds and four cycles',()=>{
 for(let seed=1;seed<=1000;seed++){
  let g=C.newGame('agent',seed);C.validateGame(g);
  for(let cycle=1;cycle<=4;cycle++){
   const ids=[];
   for(let i=0;i<9;i++){g=C.draw(g);ids.push(g.current);C.validateGame(g);if(i%2===0){g=C.finishTurn(g);C.validateGame(g);}}
   assert.deepEqual(ids.slice().sort((a,b)=>a-b),[1,2,3,4,5,6,7,8,9]);assert.equal(g.cycle,cycle);
  }
 }
});
test('Undo then redraw at the shuffle boundary returns the identical card and RNG state',()=>{
 let g=C.newGame('agent',9031);for(let i=0;i<9;i++)g=C.draw(g);
 const before=C.clone(g),first=C.draw(g),replay=C.draw(before);assert.deepEqual(first,replay);
 assert.equal(first.cycle,2);assert.equal(before.current,g.current);assert.equal(g.deck.length,0);
});
test('Finishing the turn discards only once; drawing after explicit discard matches implicit discard',()=>{
 const g=C.draw(C.newGame('agent',77));const ended=C.finishTurn(g);
 assert.equal(ended.current,null);assert.equal(ended.discard.length,1);
 assert.deepEqual(C.finishTurn(ended),ended);assert.deepEqual(C.draw(g),C.draw(ended));
});
test('Fresh deck has no current card; all levels use the same nine-card draw procedure',()=>{
 const decks=C.LEVELS.map(l=>C.newGame(l,441));assert.ok(decks.every(g=>g.current===null&&g.draws===0));
 for(const d of decks)assert.deepEqual(d.deck,decks[0].deck);
});
test('Saves round-trip notes and Undo; Undo persists through reload',()=>{
 const old=C.draw(C.newGame('legend',312)),g=C.draw(old);g.notes='J25 / Resistance 11 / <not markup>';
 const e=C.envelope(g,[old]);assert.deepEqual(C.parseSave(JSON.stringify(e)),e);
 const s=memory();assert.equal(C.persist(s,e),true);const restored=C.recover(s);
 assert.equal(restored.notice,null);assert.deepEqual(restored.save,e);assert.deepEqual(C.draw(restored.save.undo[0]),C.draw(old));
});
test('Damage recovery uses the backup and never rotates a corrupt primary over it',()=>{
 const s=memory(),a=C.envelope(C.newGame('agent',90),[]),b=C.envelope(C.draw(a.game),[a.game]);
 C.persist(s,a);C.persist(s,b);s.map.set(C.KEY,'{"broken":');
 const backup=s.getItem(C.BACKUP),recovered=C.recover(s);assert.equal(recovered.notice,'recovered');assert.deepEqual(recovered.save,a);
 C.persist(s,b);assert.equal(s.getItem(C.BACKUP),backup);assert.deepEqual(C.recover(s).save,b);
});
test('Both damaged saves remain in place; unavailable storage cannot crash a game',()=>{
 const s=memory();s.map.set(C.KEY,'bad');s.map.set(C.BACKUP,'bad backup');assert.equal(C.recover(s).notice,'damaged');assert.equal(s.getItem(C.KEY),'bad');
 const denied={getItem(){throw Error('denied')},setItem(){throw Error('denied')}};
 assert.equal(C.recover(denied).notice,'storage');assert.equal(C.persist(denied,C.envelope(C.newGame('recruit',5),[])),false);
});
test('Reject damaged or incompatible imports before state replacement',()=>{
 const e=C.envelope(C.draw(C.newGame('agent',12)),[]);
 const mutants=[v=>v.schemaVersion=99,v=>v.rulesVersion='0.9',v=>v.game.deck[0]=v.game.current,v=>v.game.deck.pop(),v=>v.game.rng=0,v=>v.game.level='other',v=>v.game.draws++,v=>v.game.current=10,v=>v.game.notes=3,v=>v.game.history[0].card=10,v=>v.game.history[0].turn=5,v=>v.undo=[{}]];
 for(const mutate of mutants){const v=C.clone(e);mutate(v);assert.throws(()=>C.parseSave(JSON.stringify(v)));}
 assert.throws(()=>C.parseSave('<html>'));assert.throws(()=>C.parseSave(' '.repeat(C.MAX_SAVE_BYTES+1)));
});
test('Final victory includes strict Camp comparison and 20 always wins for Force 136',()=>{
 for(let r=0;r<=20;r++)for(let camps=0;camps<=8;camps++)for(let markers=0;markers<=3;markers++){
  const expected=r===20?'Force 136':r<18?'Japan':camps<markers?'Force 136':'MPAJA';
  assert.equal(C.winner(r,camps,markers),expected);
 }
 assert.equal(C.winner(18,0,0),'MPAJA');assert.equal(C.winner(19,2,2),'MPAJA');assert.throws(()=>C.winner(21,1,1));assert.throws(()=>C.winner(18.5,1,1));
});
test('Long histories remain valid and contain only the latest 200 revealed draws',()=>{
 let g=C.newGame('mastermind',917);for(let i=0;i<240;i++)g=C.draw(g);C.validateGame(g);
 assert.equal(g.history.length,200);assert.equal(g.history[0].turn,41);
 assert.equal(C.envelope(g,Array(35).fill(g)).undo.length,30);
});
test('Maximum Unicode notes, history and Undo can be exported and reimported',()=>{
 let g=C.newGame('agent',171);for(let i=0;i<240;i++)g=C.draw(g);g.notes='界'.repeat(20000);
 const e=C.envelope(g,Array(30).fill(g)),json=JSON.stringify(e,null,2);
 assert.ok(Buffer.byteLength(json)<C.MAX_SAVE_BYTES);assert.deepEqual(C.parseSave(json),e);
});
