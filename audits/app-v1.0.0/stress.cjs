/* Independent audit: run node stress.cjs /path/to/web/force136. */
const fs=require('node:fs'),path=require('node:path'),assert=require('node:assert/strict');
const app=path.resolve(process.argv[2]||'../force136_app');
const C=require(path.join(app,'src/core.js'));
const out=path.join(__dirname,'evidence');fs.mkdirSync(out,{recursive:true});
// Deliberately independent oracle for pile transitions and draw counts.
function invariant(g){
 const piles=g.deck.concat(g.discard,g.current===null?[]:[g.current]);
 assert.deepEqual([...piles].sort((a,b)=>a-b),[1,2,3,4,5,6,7,8,9]);
 assert.equal(g.draws,(g.cycle-1)*9+9-g.deck.length);
 assert.equal(g.history.length,Math.min(200,g.draws));
 if(g.current!==null)assert.equal(g.current,g.history.at(-1).card);
 for(const cycle of new Set(g.history.map(e=>e.cycle))){
  const entries=g.history.filter(e=>e.cycle===cycle);assert.equal(new Set(entries.map(e=>e.card)).size,entries.length);
 }
}
const runs=1000,levels=['recruit','agent','veteran','legend','mastermind'];let draws=0,roundTrips=0,undone=0,finishes=0;
const firstCardCounts=Array(9).fill(0);
for(let run=0;run<runs;run++){
 const seed=2200001+run,level=levels[run%5];let g=C.newGame(level,seed),u=[];
 invariant(g);assert.equal(g.current,null);
 for(let turn=1;turn<=72;turn++){
  const before=C.clone(g);u.push(before);u=u.slice(-30);g=C.draw(g);draws++;
  if(turn===1)firstCardCounts[g.current-1]++;
  // Independent expected card before a nonshuffle draw.
  if(before.deck.length)assert.equal(g.current,before.deck[0]);
  assert.equal(g.draws,before.draws+1);assert.equal(g.cycle,Math.ceil(g.draws/9));invariant(g);
  if(turn%7===0){assert.deepEqual(C.draw(before),g);undone++;}
  if((run+turn)%3===0){const current=g.current,discard=g.discard.slice();g=C.finishTurn(g);assert.equal(g.current,null);assert.deepEqual(g.discard,[...discard,current]);assert.deepEqual(C.finishTurn(g),g);invariant(g);finishes++;}
  if(turn%11===0){g.notes='Seed '+seed+' / '+turn+' / <not HTML> 💠';const save=C.envelope(g,u),recovered=C.parseSave(JSON.stringify(save));assert.deepEqual(recovered.game,g);assert.deepEqual(recovered.undo,u);g=recovered.game;u=recovered.undo;roundTrips++;}
 }
}
const scorer=[];for(let r=0;r<=20;r++)for(let c=0;c<=4;c++)for(let f=0;f<=3;f++){
 const expected=r<18?'Japan':r===20?'Force 136':c>=f?'MPAJA':'Force 136';assert.equal(C.winner(r,c,f),expected);scorer.push([r,c,f,expected]);
}
// Detailed mutations cover every required state field and every pile/history relationship.
let g=C.newGame('legend',2200001);const undo=[];for(let i=0;i<12;i++){undo.push(g);g=C.draw(g);}
const good=C.envelope(g,undo),mutants={
 format:v=>v.format='other',schema:v=>v.schemaVersion=2,rules:v=>v.rulesVersion='1.0',
 level:v=>v.game.level='master',id:v=>v.game.id='',rng_zero:v=>v.game.rng=0,rng_float:v=>v.game.rng=3.5,
 cycle:v=>v.game.cycle++,draws:v=>v.game.draws++,deck_duplicate:v=>v.game.deck[0]=v.game.current,
 deck_missing:v=>v.game.deck.pop(),discard_duplicate:v=>v.game.discard[0]=v.game.current,
 current:v=>v.game.current=10,history_missing:v=>v.game.history.pop(),history_order:v=>v.game.history.reverse(),
 history_turn:v=>v.game.history[0].turn++,history_cycle:v=>v.game.history[0].cycle++,
 history_card:v=>v.game.history.at(-1).card=10,history_repeat:v=>v.game.history[1].card=v.game.history[0].card,
 notes_type:v=>v.game.notes={},notes_limit:v=>v.game.notes='x'.repeat(20001),undo_missing:v=>delete v.undo,
 undo_invalid:v=>v.undo=[{}],undo_limit:v=>v.undo=Array(31).fill(v.game),null_game:v=>v.game=null,
 no_piles:v=>delete v.game.deck};
for(const [name,mutate] of Object.entries(mutants)){const v=C.clone(good);mutate(v);assert.throws(()=>C.parseSave(JSON.stringify(v)),name);}
fs.writeFileSync(path.join(__dirname,'fixtures','seed-2200001.json'),JSON.stringify(good,null,2));
let bad=C.clone(good);bad.game.deck[0]=bad.game.current;fs.writeFileSync(path.join(__dirname,'fixtures','damaged-duplicate-card.json'),JSON.stringify(bad,null,2));
const map=new Map(),storage={getItem:k=>map.get(k)??null,setItem:(k,v)=>map.set(k,v)};
const s1=C.envelope(undo[0],[]),s2=C.envelope(undo[1],[undo[0]]);assert.equal(C.persist(storage,s1),true);assert.equal(C.persist(storage,s2),true);
map.set(C.KEY,'broken');const backup=map.get(C.BACKUP);assert.deepEqual(C.recover(storage).save,s1);assert.equal(C.persist(storage,s2),true);assert.equal(map.get(C.BACKUP),backup);
const result={seedRange:[2200001,2201000],sessions:runs,levels:5,draws,cyclesPerSession:8,roundTrips,undoReplayChecks:undone,explicitFinishes:finishes,firstCardCounts,scoringPositions:scorer.length,invalidSavesRejected:Object.keys(mutants),failures:0};
fs.writeFileSync(path.join(out,'stress-results.json'),JSON.stringify(result,null,2)+'\n');console.log(JSON.stringify(result,null,2));
