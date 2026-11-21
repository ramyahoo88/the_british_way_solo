"""Reference British players for strength calibration (not the paper bot).

ExpertGame: one-step greedy British player with a hand-written value function,
searching every legal box/operation/special-activity combination the engine
supports. It is a yardstick for what a careful British player can reach
against the engine's Japanese policies.
"""
from engine import *
from engine import Game

TASK_FOR_CONTACT=['SUPPLY','INTEL','RAIL','STRIKE','TRAIN','RAID']

class FastGame(Game):
    quiet=True
    # Scripted stress policies (v1.0.2: strict contracts; v1.0 and v1.0.1 let Events through every filter,
    # and the eventhog filter accepted every plan). Each takes the best plan that meets its contract,
    # by the adaptive values; only if no plan meets it does it fall back to all plans.
    EXPLOIT={'brute':lambda p:p.get('sa')=='ELIMINATE' or p['op'] in('ASSAULT','SWEEP') and p['box']=='Limited',
             'tempo':lambda p:p['box']=='Limited',
             'econ':lambda p:p['op'] in('DEPLOY','CONSTRUCT'),
             'eventhog':lambda p:p['op']=='EVENT'}
    def japan_turn(self,free):
        pol=self.policy
        if pol not in self.EXPLOIT:return Game.japan_turn(self,free)
        keep=self.EXPLOIT[pol];self.policy='adaptive'
        try:
            candidates=[]
            for box in free:
                if box=='Event':
                    if self.event not in [6,9]:candidates.append(dict(op='EVENT',box=box,sa=None))
                    continue
                for op in ['DEPLOY','CONSTRUCT','ASSAULT','SWEEP']:
                    special=[None] if box=='Limited' else ['EXTRACT'] if op=='DEPLOY' else [None,'REPRISAL','ELIMINATE']
                    for sa in special:
                        for strength in ([2,5,0] if op=='SWEEP' else [3]):
                            candidates.append(dict(op=op,box=box,sa=sa,strength=strength,timing='after'))
            pool=[c for c in candidates if keep(c)] or candidates
            for plan in pool:
                probe=self.clone();probe.jp_apply(plan);plan['_value']=probe.jp_value()
            plan=max(pool,key=lambda p:p['_value'])
            self.chosen['J']=plan['box'];self.jp_apply(plan)
        finally:self.policy=pol
    def jp_value(self):
        if self.policy=='counter':return -british_value(self)
        if self.policy=='mixed':return 0.5*Game.jp_value(self)-0.5*british_value(self)
        return Game.jp_value(self)
    def record(self,kind,detail):
        if self.preview or self.quiet:return
        return Game.record(self,kind,detail)
    def clone(self):
        other=Game.__new__(type(self))
        d={}
        for k,v in self.__dict__.items():
            if k in ('log','secret','metrics','decisions'):continue
            if k=='board':d[k]={s:dict(x) for s,x in v.items()}
            elif isinstance(v,(dict,list,set)):d[k]=deepcopy(v)
            else:d[k]=v
        other.__dict__=d
        other.preview=True;other.secret={};other.log=[];other.metrics={};other.decisions=[];other.uncertain=False
        return other

def remaining_props(g):
    return max(1,4-g.campaign)

def british_value(g,w=None):
    """Higher is better for Force 136."""
    w=w or {}
    b=g.board
    if g.ended:
        return 1000 if g.winner=='Force 136' else -1000+g.resistance
    rp=remaining_props(g)
    terms=score_terms(b,g.resources)
    neutral=terms['neutral_population']
    police=sum(v['police']>0 for v in b.values())
    v=3.0*g.resistance
    v+=3.0*terms['intel']
    v+=w.get('cache',1.6)*rp*terms['caches']
    v+=w.get('maj',2.0)*terms['majorities']
    v-=w.get('res',0.75)*g.resources
    v-=w.get('neut',0.55)*neutral
    v-=w.get('pol',0.9)*police
    f=g.count('force136')
    v+=w.get('f136',2.5)*f
    for s,x in b.items():
        if x['force136'] and x['kempeitai']:
            faces=sum(d+x['police']>gs(x) for d in range(1,7))/6
            exposed= (not x['camp']) or g.cap.get(22)=='S'
            v-=faces*(2.5 if exposed else 0.8)
        if x['cache'] and x['troops'] and gs(x)<2:v-=w.get('unguard',1.2)*rp
        if x['force136']:v+=0.35*ug(x)
    # concealed intel reachable next turn
    reach=set()
    for s,x in b.items():
        if x['force136']:
            for t in g.gather_targets(s):reach.add(t)
    v+=w.get('reach',0.6)*len(reach)
    _,yields=live_and_yield(g.sabotage)
    v-=w.get('yield',0.9)*(sum(yields.values())+g.count('new_village'))*rp/3
    v+=0.5*sum(1 for r,n in g.sabotage.items() if n)
    # MPAJA clash exposure
    v-=1.0*sum(1 for x in b.values() if red(x) and blue(x))
    caps={8:2.5,12:1.5,15:1.2,19:1.8,22:2.0,27:2.0}
    v+=sum(caps[k]*(1 if side=='U' else -1) for k,side in g.cap.items())
    # final-round camp condition
    if g.campaign==3:
        v-=1.5*max(0,g.count('camp')-g.count('force136')+1)
    return v

def british_candidates(g,free):
    out=[]
    for box in free:
        if box=='Event':
            if g.event not in (6,9):out.append(dict(kind='EVENT',box=box))
            out.append(dict(kind='PASS',box=box))
            continue
        if box=='Limited':
            for op in ['TRAIN','RAIL','STRIKE']:out.append(dict(kind='OP',op=op,box=box,sa=None))
            for t in TASK_FOR_CONTACT:out.append(dict(kind='OP',op='CONTACT',task=t,box=box,sa=None))
            out.append(dict(kind='PASS',box=box))
            continue
        for op,sas in PAIR.items():
            tasks=TASK_FOR_CONTACT if op=='CONTACT' else [None]
            for t in tasks:
                for sa in [None]+sas:
                    out.append(dict(kind='OP',op=op,task=t,box=box,sa=sa))
            if op=='CONTACT':
                for sa in sas:out.append(dict(kind='OP',op=op,task=None,hold=True,box=box,sa=sa))
    return out

def apply_british(g,plan,region='C'):
    if plan['kind']=='EVENT':g.execute_event(g.event,'U');return
    if plan['kind']=='PASS':g.contact('SUPPLY' if g.available('cache') else 'INTEL');return
    op=plan['op']
    if op=='CONTACT':g.contact(plan.get('task'),hold=plan.get('hold',False))
    elif op=='TRAIN':g.train()
    elif op=='RAIL':g.rail(region)
    elif op=='STRIKE':g.strike()
    if plan.get('sa'):g.special(plan['sa'])

class ExpertGame(FastGame):
    weights=None
    def bot_turn(self,free):
        self.card={'id':'X','rail_order':'C','primary':'SUPPLY','other_special':'SUPPLY > GATHER > RAID','preparation':'TRAIN','b_events':'YES'}
        best=None
        for plan in british_candidates(self,free):
            p=self.clone()
            try:apply_british(p,plan)
            except (ValueError,AssertionError,KeyError):continue
            tempo=0.8 if plan['box']=='Limited' else 0.3 if plan['box']=='Event' else 0
            val=british_value(p,self.weights)+tempo
            if best is None or val>best[0]:best=(val,plan)
        plan=best[1]
        self.chosen['B']=plan['box'];apply_british(self,plan)
        self.inc('bot_turns');self.inc('b_'+(plan.get('op') or plan['kind'])+('+'+plan['sa'] if plan.get('sa') else ''))
        self.card=None

def run(cls,seeds,policies=('extraction','hunting','repair','adaptive'),**kw):
    import collections
    res=[]
    for s in seeds:
        for p in policies:
            g=cls(s);g.policy=p
            for k,v in kw.items():setattr(g,k,v)
            r=g.run();res.append(r)
    return res

if __name__=='__main__':
    import sys,time,collections
    t=time.time();n=int(sys.argv[1]) if len(sys.argv)>1 else 4
    res=run(ExpertGame,range(5000,5000+n))
    by=collections.defaultdict(list)
    for r in res:by[r['policy']].append(r)
    for p,rs in by.items():
        print(p,collections.Counter(r['winner'] for r in rs),round(sum(r['final_resistance'] for r in rs)/len(rs),2))
    agg=collections.Counter()
    for r in res:
        for k,v in r['metrics'].items():
            if k.startswith('b_'):agg[k]+=v
    print(agg.most_common(12))
    print('sec',round(time.time()-t,1))
