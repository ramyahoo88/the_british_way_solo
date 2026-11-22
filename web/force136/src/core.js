/* Force 136 digital deck. The physical board remains the authority. */
(function (root, factory) {
  const api = factory();
  if (typeof module === 'object' && module.exports) module.exports = api;
  else root.Force136Deck = api;
})(typeof globalThis === 'object' ? globalThis : this, function () {
  'use strict';
  const APP_VERSION = '1.0.1', RULES_VERSION = '1.1', MAX_SAVE_BYTES = 4 * 1024 * 1024;
  const LEVELS = ['recruit', 'agent', 'veteran', 'legend', 'mastermind'];
  const KEY = 'force136.deck.v1', BACKUP = 'force136.deck.backup.v1';
  const clone = value => JSON.parse(JSON.stringify(value));
  const integer = (v, min, max) => Number.isInteger(v) && v >= min && v <= max;
  function check(condition, message) { if (!condition) throw new Error(message); }
  function randomBelow(game, limit) {
    const ceiling = Math.floor(4294967296 / limit) * limit;
    let x;
    do {
      x = game.rng;
      x ^= x << 13; x ^= x >>> 17; x ^= x << 5;
      game.rng = x >>> 0; x = game.rng;
    } while (x >= ceiling);
    return x % limit;
  }
  function shuffle(game, cards) {
    const deck = cards.slice();
    for (let i = deck.length - 1; i > 0; i--) {
      const j = randomBelow(game, i + 1);
      [deck[i], deck[j]] = [deck[j], deck[i]];
    }
    return deck;
  }
  function newGame(level, seed, id) {
    check(LEVELS.includes(level), 'Unknown level.');
    check(integer(seed, 1, 4294967295), 'Invalid shuffle seed.');
    const g = { level, id: id || 'game-' + seed, rng: seed, cycle: 1, draws: 0,
      deck: [], discard: [], current: null, history: [], notes: '' };
    g.deck = shuffle(g, [1,2,3,4,5,6,7,8,9]);
    return g;
  }
  function finishTurn(game) {
    const g = clone(game);
    if (g.current !== null) { g.discard.push(g.current); g.current = null; }
    return g;
  }
  function draw(game) {
    let g = finishTurn(game);
    if (g.deck.length === 0) {
      g.deck = shuffle(g, g.discard); g.discard = []; g.cycle++;
    }
    g.current = g.deck.shift(); g.draws++;
    g.history.push({ turn: g.draws, cycle: g.cycle, card: g.current });
    if (g.history.length > 200) g.history.shift();
    return g;
  }
  function validateGame(value) {
    check(value && typeof value === 'object' && !Array.isArray(value), 'Missing deck.');
    const g = value;
    check(LEVELS.includes(g.level), 'Unknown level.');
    check(typeof g.id === 'string' && g.id.length > 0 && g.id.length <= 100, 'Invalid game identifier.');
    check(integer(g.rng, 1, 4294967295), 'Invalid shuffle state.');
    check(integer(g.cycle, 1, 100000) && integer(g.draws, 0, 900000), 'Invalid draw count.');
    check(Array.isArray(g.deck) && Array.isArray(g.discard), 'Missing deck piles.');
    check(g.deck.length <= 9 && g.discard.length <= 9, 'Invalid pile size.');
    check(g.current === null || integer(g.current, 1, 9), 'Invalid current Directive.');
    const all = [...g.deck, ...g.discard, ...(g.current === null ? [] : [g.current])];
    check(all.length === 9 && new Set(all).size === 9 && all.every(x => integer(x,1,9)), 'The deck must contain each of the nine Directives exactly once.');
    const used = g.discard.length + (g.current === null ? 0 : 1);
    check(g.cycle===1 || used>0, 'A new cycle begins only when its first Directive is drawn.');
    check(g.draws === (g.cycle - 1) * 9 + used, 'Draw count and piles disagree.');
    check(g.deck.length === 9 - used, 'Deck count disagrees.');
    check(Array.isArray(g.history) && g.history.length === Math.min(g.draws,200), 'Draw history is incomplete.');
    for (let i=0;i<g.history.length;i++) {
      const e=g.history[i], turn=g.draws-g.history.length+i+1;
      check(e && e.turn===turn && e.cycle===Math.ceil(turn/9) && integer(e.card,1,9), 'Invalid draw history.');
    }
    const seen=new Map();
    for(const e of g.history){if(!seen.has(e.cycle))seen.set(e.cycle,new Set());check(!seen.get(e.cycle).has(e.card),'Repeated Directive in recorded history.');seen.get(e.cycle).add(e.card);}
    const cycleEntries=g.history.filter(e=>e.cycle===g.cycle).map(e=>e.card);
    check(cycleEntries.length===used && new Set(cycleEntries).size===used, 'Repeated Directive in a cycle.');
    check(JSON.stringify(cycleEntries)===JSON.stringify([...g.discard,...(g.current===null?[]:[g.current])]), 'History and piles disagree.');
    if(g.current!==null) check(g.history.at(-1)?.card===g.current, 'Current Directive and history disagree.');
    check(typeof g.notes === 'string' && g.notes.length <= 20000, 'Notes are too long.');
    return {level:g.level,id:g.id,rng:g.rng,cycle:g.cycle,draws:g.draws,deck:g.deck.slice(),discard:g.discard.slice(),current:g.current,
      history:g.history.map(e=>({turn:e.turn,cycle:e.cycle,card:e.card})),notes:g.notes};
  }
  function envelope(game, undo) {
    return {format:'force136-digital-deck',schemaVersion:1,appVersion:APP_VERSION,rulesVersion:RULES_VERSION,
      game:validateGame(game),undo:(undo||[]).slice(-30).map(validateGame)};
  }
  function parseSave(input) {
    check(typeof input==='string' && input.length<=MAX_SAVE_BYTES && new TextEncoder().encode(input).byteLength<=MAX_SAVE_BYTES, 'Save file exceeds the 4 MB limit.');
    let v;try {v=JSON.parse(input);}catch (_) {throw new Error('This is not a readable JSON save.');}
    check(v?.format==='force136-digital-deck' && v.schemaVersion===1, 'This save format is not supported.');
    check(v.rulesVersion===RULES_VERSION, 'This save uses a different version of the Force 136 rules.');
    check(Array.isArray(v.undo) && v.undo.length<=30, 'Invalid Undo history.');
    return envelope(v.game,v.undo);
  }
  function recover(storage) {
    let primary=null, backup=null;
    try {primary=storage.getItem(KEY);backup=storage.getItem(BACKUP);}catch (_) {return {save:null,notice:'storage'};}
    if(primary!==null) {try{return {save:parseSave(primary),notice:null};}catch (_) {}}
    if(backup!==null) {try{return {save:parseSave(backup),notice:'recovered'};}catch (_) {}}
    return {save:null,notice:primary!==null||backup!==null?'damaged':null};
  }
  function persist(storage, save) {
    const data=JSON.stringify(envelope(save.game,save.undo));
    try {
      const previous=storage.getItem(KEY);
      if(previous!==null) {try {parseSave(previous);storage.setItem(BACKUP,previous);}catch (_) {}}
      storage.setItem(KEY,data);return true;
    } catch (_) {return false;}
  }
  function winner(resistance,camps,markers) {
    check(integer(resistance,0,20) && integer(camps,0,4) && integer(markers,0,3), 'Enter whole counts: Resistance 0–20, Jungle Camps 0–4, Force 136 markers 0–3.');
    if(resistance===20 || (resistance>=18 && camps<markers)) return 'Force 136';
    return resistance>=18?'MPAJA':'Japan';
  }
  return {APP_VERSION,RULES_VERSION,MAX_SAVE_BYTES,LEVELS,KEY,BACKUP,clone,newGame,draw,finishTurn,validateGame,envelope,parseSave,recover,persist,winner};
});
