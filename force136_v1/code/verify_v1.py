"""Independent verification of Force 136 v1.0 (revised after the GPT review of commit 615c870).

Three checks, each of which can fail a game on its own:

1. Cross-check. The printed-rules bot (force136_v1.Force136) and the clean-room bot
   (cleanroom.CleanForce136) play the same seed. Their traces must match at every British turn
   (plan, board, Sabotage markers, Resistance, capabilities), after every Propaganda round
   (board, Resistance, Zipper) and in the final result (winner, Resistance, Camps, markers).
2. Scoring oracle. Every Propaganda scoring, in both implementations, is recomputed from the
   rulebook text alone (Japanese Occupation rules 6.1.1-6.2.4, 7.0.1 and 1.13) plus the level's
   printed bonus. This catches errors in code the two bots share (the engine's scoring), which a
   cross-check cannot see.
3. Coverage. Forced-capability games put each side of every capability card (J8, J12, J15, J19,
   J22, J27) in play from the start, so British-side effects that the Japan policies never choose
   are exercised. Coverage counters report how often each British-side effect actually fired.

usage: python3 verify_v1.py [seeds_per_block]          (default 32)
       python3 verify_v1.py --mutants [seeds]           (mutation tests: each must be caught)
"""
import sys,os,json,collections
from copy import deepcopy
HERE=os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0,HERE)
for d in (os.path.join(HERE,'cleanroom'),os.path.join(os.path.dirname(HERE),'cleanroom')):
    if os.path.exists(os.path.join(d,'cleanroom.py')):sys.path.append(d);break
import engine
from engine import ORDER,PROV,ug,gs,cubes
import force136_v1 as V
import cleanroom as C

POLS=('extraction','hunting','repair','adaptive','counter','mixed')
LEVELS=('recruit','agent','veteran','legend','mastermind')
CAPS=(8,12,15,19,22,27)
ST_ORIG=engine.score_terms
BONUS={'recruit':0,'agent':0,'veteran':0,'legend':1,'mastermind':2}   # printed rules, section 10

class Box:                      # not a dict/list/set, so FastGame.clone shares it instead of copying it
    def __init__(self):self.items=[];self.fail=[];self.cov=collections.Counter()

def bkey(board):return tuple((s,tuple(sorted(v.items()))) for s,v in sorted(board.items()))
def tracks(g):
    """Public tracks and bookkeeping outside the board: Resistance, Resources, Zipper, Cache track,
    lost pieces, pieces away (J25 and Troops off-map), removed Intel, capabilities, deck position."""
    return (g.resistance,g.resources,g.zipper,g.track_cache,g.lost_cache,g.lost_k,g.away_troops,g.away_f,
            tuple(sorted(g.removed_intel)),tuple(sorted(g.cap.items())),tuple(sorted(g.sabotage.items())),
            g.campaign,g.deck_pos,g.draw)

# ---------------------------------------------------------------- 2. scoring oracle (rulebook only)
def oracle(pre,final,bonus):
    """Return (Resistance after scoring, winner or None, notes) from the pre-scoring snapshot."""
    b=deepcopy(pre['board']);notes=[]
    def red_(v):return v['red_u']+v['red_a']
    def blue_(v):return v['blue_u']+v['blue_a']
    back=0
    for v in b.values():                                  # 6.1.1 Clashes: one MPAJA + one other
        if red_(v) and blue_(v):
            for c in ('red','blue'):
                k=c+'_a' if v[c+'_a'] else c+'_u';v[k]-=1
            back+=1
    new_village_neutral=pre['cap15']=='S'                   # J15 (Japanese side): New Villages count as Neutral
    def opposed(s):return b[s]['opposition'] and not (new_village_neutral and b[s]['new_village'])
    avail=pre['red_avail']+back
    sites=[s for s in V.MAP_ORDER if opposed(s)]            # 6.1.2 Mobilize: one MPAJA per Opposition space
    if len(sites)>avail:notes.append('mobilize shortage')
    for s in sites[:avail]:b[s]['red_u']+=1
    intel=sum(v['intel'] for v in b.values() if v['intel'])                       # 6.2.1
    caches=sum(1 for v in b.values() if v['cache'])                              # 6.2.2
    imbalance=sum(1 for v in b.values()
                  if red_(v)+blue_(v)>v['troops']+v['police'])                   # 6.2.2 (Kempeitai are not cubes)
    res=pre['resources']//4                                                       # 6.2.3
    neutral=sum(b[s]['population'] for s in b if not opposed(s))//5             # 6.2.4
    police=sum(1 for v in b.values() if v['police'])//3                          # 6.2.4
    R=min(20,max(0,pre['R']+intel+caches+imbalance-res-neutral-police))          # 1.13
    if not final:
        return min(20,R+bonus),None,notes                                         # level bonus, nonfinal only
    camps=sum(1 for v in b.values() if v['camp']);f136=sum(v['force136'] for v in b.values())
    w='Japan' if R<18 else 'Force 136' if R==20 or camps<f136 else 'MPAJA'       # 7.0.1
    return R,w,notes

# ---------------------------------------------------------------- tracing wrapper
def traced(cls,forced=None):
    class T(cls):
        def __init__(self,*a,**k):
            cls.__init__(self,*a,**k);self.box=Box()
            if forced:self.cap.update(forced)
        def score_only(self,final=False):
            if self.preview:return cls.score_only(self,final)
            pre=dict(board=deepcopy(self.board),resources=self.resources,R=self.resistance,
                     red_avail=self.available('red'),cap15=self.cap.get(15))
            r=cls.score_only(self,final)
            R,w,notes=oracle(pre,final,BONUS[self.level])
            if R!=self.resistance or (final and w!=self.winner) or self.resources!=0:
                self.box.fail.append(dict(draw=self.draw,final=final,expected=(R,w),got=(self.resistance,self.winner),notes=notes))
            self.box.items.append(('score',self.draw,final,pre['R'],self.resistance,self.winner if final else None))
            return r
        def propaganda(self,final=False):
            r=cls.propaganda(self,final)
            if not self.preview and not final:
                self.box.items.append(('reset',self.draw,bkey(self.board),tracks(self)))
            return r
        def bot_turn(self,free):
            if self.preview:return cls.bot_turn(self,free)
            mine=isinstance(self,V.Force136)       # coverage is counted on the printed-rules bot
            c22=mine and self.cap.get(22)=='U';c27=mine and self.cap.get(27)=='U'
            if c27:
                b=self.board
                amb=any(not b[s]['force136'] and V.Force136.ambush_target(self,s) for s in ORDER)
                sab=any(not b[s]['force136'] and ug(b[s]) and V.Force136.rail_choice(self,s) for s in ORDER)
            cls.bot_turn(self,free);p=self.last_plan
            ops={p.get('op'),p.get('sa')}
            if c22 and 'GATHER' in ops:self.box.cov['J22 British: Gather without activating']+=1
            if c27 and 'AMBUSH' in ops and amb:self.box.cov['J27 British: extra Ambush space']+=1
            if c27 and 'SABOTAGE' in ops and sab:self.box.cov['J27 British: extra Sabotage space']+=1
            if mine and self.cap.get(8)=='U' and 'SUPPLY' in ops:self.box.cov['J8 British: Supply']+=1
            if mine and self.cap.get(19)=='U' and 'GATHER' in ops:self.box.cov['J19 British: Gather']+=1
            self.box.items.append(('turn',self.draw,tuple(free),self.directive['id'],
                                   (p.get('box'),p.get('op'),p.get('sa')),p.get('goal'),bkey(self.board),tracks(self)))
    T.__name__='Traced'+cls.__name__
    return T

def play(cls,seed,pol,level,forced=None):
    g=traced(cls,forced)(seed,level=level);g.policy=pol;r=g.run()
    res=(r['winner'],r['final_resistance'],r['camps'],r['force136'],r['draws'],r['ending'],tracks(g))
    return g.box,res

def compare(a,b):
    if len(a.items)!=len(b.items):return 'length',len(a.items),len(b.items)
    for i,(x,y) in enumerate(zip(a.items,b.items)):
        if x!=y:return i,x[:2],x[0]
    return None

def check(seed,pol,level,forced=None,P=V.Force136,Q=C.CleanForce136):
    a,ra=play(P,seed,pol,level,forced);b,rb=play(Q,seed,pol,level,forced)
    out=dict(cross=None,oracle=len(a.fail)+len(b.fail),cov=a.cov)
    d=compare(a,b)
    if d:out['cross']=d
    elif ra!=rb:out['cross']=('result',ra,rb)
    return out

def blocks(n):
    """The verification blocks: normal games at every level, plus forced-capability games."""
    yield 'normal',[(s,p,l,None) for l in LEVELS for s in range(20000,20000+n) for p in POLS]
    for cap in CAPS:
        for side in ('U','S'):
            yield f'J{cap} {side}',[(s,p,'agent',{cap:side}) for s in range(21000,21000+n//2) for p in POLS]
    for side in ('U','S'):
        yield f'all {side}',[(s,p,l,{c:side for c in CAPS}) for l in ('agent','legend') for s in range(22000,22000+n//2) for p in POLS]

def run_block(jobs,P=V.Force136,Q=C.CleanForce136):
    games=len(jobs);cross=0;orc=0;cov=collections.Counter();ex=[]
    for s,p,l,f in jobs:
        o=check(s,p,l,f,P,Q);cov.update(o['cov'])
        if o['cross']:cross+=1;ex.append((s,p,l,f,o['cross']))
        if o['oracle']:orc+=1;ex.append((s,p,l,f,'oracle'))
    return dict(games=games,cross=cross,oracle=orc,cov=dict(cov),examples=[str(e)[:200] for e in ex[:3]])

# ---------------------------------------------------------------- mutation tests
def mutants():
    """Each mutant is a deliberate error. The checker must flag at least one game for each."""
    B=V.Force136
    class LegendBonusFinal(B):            # scoring error: the level bonus also applied at final scoring
        def score_only(self,final=False):
            r=B.score_only(self,final)
            if final and self.L['bonus']:
                self.resistance=min(20,self.resistance+self.L['bonus'])
                self.winner='Japan' if self.resistance<18 else 'Force 136' if self.resistance==20 or self.count('camp')<self.count('force136') else 'MPAJA'
            return r
    class AgentBonus(B):                  # scoring error: Agent gets +1 per nonfinal Propaganda
        def score_only(self,final=False):
            r=B.score_only(self,final)
            if not final:self.resistance=min(20,self.resistance+1)
            return r
    class TieToBritain(B):                # victory error: 18-19 with Camps == markers counted as a British win
        def score_only(self,final=False):
            r=B.score_only(self,final)
            if final and 18<=self.resistance<20 and self.count('camp')<=self.count('force136'):self.winner='Force 136'
            return r
    class J22Activates(B):                # British J22 ignored: Gather activates
        def gather(self):
            side=self.cap.get(22)
            if side=='U':self.cap[22]=None
            try:return B.gather(self)
            finally:
                if side=='U':self.cap[22]='U'
    class J27NoExtraAmbush(B):
        def strike(self,locations=None,color=None,bose=False,extra=True):return B.strike(self,locations,color,bose,False)
    class J27NoExtraSabotage(B):
        def rail(self,region='C',locations=None,color=None,extra=True):return B.rail(self,region,locations,color,False)
    class NoRefresh(B):                   # v1.0.1 Train fallback omitted (the v1.0 behaviour)
        def place_one(self,s,c):
            v=self.board[s]
            if self.available(c):v[c+'_u']+=1;return True
            donors=[x for x in V.MAP_ORDER if x!=s and not self.board[x]['force136']
                    and (self.board[x][c+'_a'] or self.board[x][c+'_u']) and self.donor_ok(x)]
            if not donors:return False
            x=min(donors,key=lambda x:(not self.board[x][c+'_a'],-cubes(self.board[x]),V.mo(x)))
            f=c+('_a' if self.board[x][c+'_a'] else '_u');self.board[x][f]-=1;v[c+'_u']+=1;return True
    class J27EngineOrder(B):              # British J27 extra Sabotage space chosen by the engine's railway order
        def rail(self,region='C',locations=None,color=None,extra=True):return V.FastGame.rail(self,region,locations,color,extra)
    Q=C.CleanForce136
    class GPTFinalPlusOne(Q):             # GPT's negative control: secondary adds 1 Resistance before final scoring
        def score_only(self,final=False):
            if final:self.resistance=min(20,self.resistance+1)
            return Q.score_only(self,final)
    class DeletedTurn(Q):                 # secondary skips its third turn's action (Pass, no Contact)
        def bot_turn(self,free):
            self._n=getattr(self,'_n',0)+(0 if self.preview else 1)
            if self._n==3 and not self.preview:
                self.draw_directive();self.chosen['B']=min(free,key=engine.BOXES.index)
                self.last_plan=dict(box=self.chosen['B'],op='PASS',sa=None,goal='PASS');return
            return Q.bot_turn(self,free)
    secondary=[('secondary: +1 Resistance before final scoring (GPT F1)',GPTFinalPlusOne,('agent',),None),
               ('secondary: one turn skipped',DeletedTurn,('agent',),None)]
    local=[('Legend bonus at final scoring',LegendBonusFinal,('legend','mastermind'),None),
           ('Agent bonus +1',AgentBonus,('agent',),None),
           ('18-19 tie counted for Britain',TieToBritain,('agent','legend'),None),
           ('Train refresh fallback omitted',NoRefresh,('agent',),None),
           ('British J22 ignored (Gather activates)',J22Activates,('agent',),{22:'U'}),
           ('British J27 ignored for Ambush',J27NoExtraAmbush,('agent',),{27:'U'}),
           ('British J27 ignored for Sabotage',J27NoExtraSabotage,('agent',),{27:'U'}),
           ('British J27 Sabotage space in railway order',J27EngineOrder,('agent',),{27:'U'})]
    return [(n,c,l,f,'P') for n,c,l,f in local]+[(n,c,l,f,'Q') for n,c,l,f in secondary]

def shared_mutants():
    """Errors in shared engine scoring code: the cross-check cannot see them; the oracle must."""
    st=engine.score_terms
    def neutral4(b,r):
        t=st(b,r);t['neutral_penalty']=t['neutral_population']//4;return t
    def no_police(b,r):
        t=st(b,r);t['police_penalty']=0;return t
    def caches_double(b,r):
        t=st(b,r);t['caches']*=2;return t
    return [('engine: Neutral Population /4',neutral4),('engine: no Police penalty',no_police),('engine: Caches count double',caches_double)]

if __name__=='__main__':
    if '--mutants' in sys.argv:
        n=int(sys.argv[-1]) if sys.argv[-1].isdigit() else 16
        rows=[]
        for name,cls,levels,forced,side in mutants():
            jobs=[(s,p,l,forced) for l in levels for s in range(23000,23000+n) for p in POLS]
            r=run_block(jobs,P=cls) if side=='P' else run_block(jobs,Q=cls);caught=r['cross']+r['oracle']
            rows.append((name,r['games'],r['cross'],r['oracle'],'CAUGHT' if caught else 'MISSED'));print(*rows[-1],flush=True)
        for name,fn in shared_mutants():
            engine.score_terms=fn
            try:
                jobs=[(s,p,'agent',None) for s in range(23000,23000+n) for p in POLS]
                r=run_block(jobs);caught=r['cross']+r['oracle']
            finally:engine.score_terms=ST_ORIG
            rows.append((name,r['games'],r['cross'],r['oracle'],'CAUGHT' if caught else 'MISSED'));print(*rows[-1],flush=True)
        json.dump(rows,open('verify_mutants.json','w'),indent=1)
        print('all caught' if all(r[-1]=='CAUGHT' for r in rows) else 'SOME MISSED')
    else:
        n=int(sys.argv[1]) if len(sys.argv)>1 else 32
        out={};tot=collections.Counter()
        for name,jobs in blocks(n):
            r=run_block(jobs);out[name]=r
            tot['games']+=r['games'];tot['cross']+=r['cross'];tot['oracle']+=r['oracle']
            print(f"{name:10s} games {r['games']:5d} cross-check failures {r['cross']} oracle failures {r['oracle']} {r['cov'] or ''} {r['examples'] or ''}",flush=True)
        print('TOTAL',dict(tot))
        json.dump(out,open('verify_results.json','w'),indent=1)
