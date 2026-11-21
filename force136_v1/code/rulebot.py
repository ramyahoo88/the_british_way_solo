"""Rule-based Force 136 policies: candidate tabletop procedures expressed in code.

Every decision here must be checkable at the table from public information.
"""
from engine import *
from expert import FastGame,british_value,british_candidates,apply_british
import collections

def gather_count(g):
    """Distinct concealed chits Gather could reveal now (public count)."""
    p=g.clone();return len(p.gather())

def useful_strikes(g):
    return [s for s in ORDER if g.board[s]['force136'] and g.strike_option(s)]

def supply_sites(g):
    b=g.board
    return [s for s in PROV if b[s]['camp'] and b[s]['force136'] and not b[s]['cache']] if g.available('cache') else []

def total_yield(sab):
    return sum(live_and_yield(sab)[1].values())

class RuleGame(FastGame):
    def rail_choice(self,s,region='C',stack=False,eligible=None):
        if stack or not self.P.get('cut_rail'):return FastGame.rail_choice(self,s,region,stack,eligible)
        candidates=[r for r in EDGES if s in self.rail_adj(r) and not self.sabotage[r] and (eligible is None or r in eligible)]
        if not candidates:return None
        base=total_yield(self.sabotage);order=DATA['rail_orders'][region]
        def cut(r):
            a=dict(self.sabotage);a[r]=1;return base-total_yield(a)
        return min(candidates,key=lambda r:(-cut(r),order.index(r)))
    def cut_available(self):
        base=total_yield(self.sabotage)
        for s in ORDER:
            if self.board[s]['force136'] and ug(self.board[s]):
                r=self.rail_choice(s,'C')
                if r:
                    a=dict(self.sabotage);a[r]=1
                    if total_yield(a)<base:return True
        return False
    P=dict(full=['INTEL','SUPPLY','STRIKE','TRAIN','CONTACT'],limited=['TRAIN','CONTACT'],
           intel_min=2,event='list',first_limited=False)
    def plan_goal(self,goal,box):
        """Return (plan,useful) for a goal in a box, testing on a clone."""
        full=box=='Op & SA';b=self.board
        if ':' in goal:
            goal,cond=goal.split(':')
            if cond.startswith('res') and self.resources<int(cond[3:]):return None
            if cond=='live' and not live_and_yield(self.sabotage)[0]-{r for r,n in self.sabotage.items() if n}:return None
            if cond.startswith('camp') and self.campaign<int(cond[4:]):return None
            if cond=='cut' and not self.cut_available():return None
        if goal=='INTEL':
            if not full:return None
            n=gather_count(self)
            # Gather needs an accompanying op: Ambush if useful, else Sabotage if useful, else Contact hold/move.
            opts=[]
            if useful_strikes(self):opts.append(dict(kind='OP',op='STRIKE',sa='GATHER',box=box))
            opts.append(dict(kind='OP',op='CONTACT',task='INTEL',sa='GATHER',box=box))
            for plan in opts:
                p=self.clone();before=sum(v['intel'] is not None for v in p.board.values())
                apply_british(p,plan,self.region_)
                got=sum(v['intel'] is not None for v in p.board.values())-before
                if got>=self.P['intel_min']:return plan
            return None
        if goal=='SUPPLY':
            if not full or not self.available('cache'):return None
            opts=[]
            if supply_sites(self):
                opts.append(dict(kind='OP',op='TRAIN',sa='SUPPLY',box=box))
            opts.append(dict(kind='OP',op='CONTACT',task='SUPPLY',sa='SUPPLY',box=box))
            for plan in opts:
                p=self.clone();c=p.count('cache');apply_british(p,plan,self.region_)
                if p.count('cache')>c:return plan
            return None
        if goal=='STRIKE':
            if not useful_strikes(self):return None
            if not full:return dict(kind='OP',op='STRIKE',sa=None,box=box)
            for sa in self.P.get('strike_sa',['GATHER','RAID']):
                p=self.clone();p.strike()
                if sa=='GATHER' and p.gather():return dict(kind='OP',op='STRIKE',sa='GATHER',box=box)
                if sa=='RAID':
                    q=self.clone();q.strike()
                    if q.raid():return dict(kind='OP',op='STRIKE',sa='RAID',box=box)
            return dict(kind='OP',op='STRIKE',sa=None,box=box)
        if goal=='TRAIN':
            p=self.clone()
            if not p.train():return None
            if not full:return dict(kind='OP',op='TRAIN',sa=None,box=box)
            for sa in ['SUPPLY','RAID']:
                q=self.clone();q.train()
                if q.special(sa):return dict(kind='OP',op='TRAIN',sa=sa,box=box)
            return dict(kind='OP',op='TRAIN',sa=None,box=box)
        if goal=='RAIL':
            p=self.clone()
            if not p.rail(self.region_):return None
            if not full:return dict(kind='OP',op='RAIL',sa=None,box=box)
            for sa in ['GATHER','RAID']:
                q=self.clone();q.rail(self.region_)
                if q.special(sa):return dict(kind='OP',op='RAIL',sa=sa,box=box)
            return dict(kind='OP',op='RAIL',sa=None,box=box)
        if goal=='PLACE':
            if not self.available('force136'):return None
            goal='CONTACT'
        if goal=='CONTACT':
            p=self.clone()
            if not p.contact(self.P.get('contact_task','SUPPLY')):return None
            plan=dict(kind='OP',op='CONTACT',task=self.P.get('contact_task','SUPPLY'),sa=None,box=box)
            if full:
                for sa in ['SUPPLY','GATHER','RAID']:
                    q=self.clone();q.contact(plan['task'])
                    if q.special(sa):plan['sa']=sa;break
            return plan
        raise ValueError(goal)
    def event_ok(self):
        return False
    def bot_turn(self,free):
        self.region_='C';self._free=free
        self.card={'id':'R','rail_order':'C','primary':'SUPPLY','other_special':'SUPPLY > GATHER > RAID','preparation':'TRAIN','b_events':'YES'}
        plan=None
        if 'Event' in free and self.event not in (6,9) and self.event_ok():
            plan=dict(kind='EVENT',box='Event')
        if not plan and 'Op & SA' in free and not (self.P['first_limited'] and 'Limited' in free):
            for goal in self.P['full']:
                plan=self.plan_goal(goal,'Op & SA')
                if plan:break
        if not plan and 'Limited' in free:
            for goal in self.P['limited']:
                plan=self.plan_goal(goal,'Limited')
                if plan:break
        if not plan and 'Op & SA' in free:
            for goal in self.P['full']:
                plan=self.plan_goal(goal,'Op & SA')
                if plan:break
        if not plan:
            box=min(free,key=BOXES.index);plan=dict(kind='PASS',box=box)
        self.chosen['B']=plan['box'];apply_british(self,plan,self.region_)
        self.inc('b_'+(plan.get('op') or plan['kind'])+('+'+plan['sa'] if plan.get('sa') else ''))
        self.card=None

def evaluate(cls,seeds,policies=('extraction','hunting','repair','adaptive'),**attrs):
    res=[]
    for s in seeds:
        for p in policies:
            g=cls(s);g.policy=p
            for k,v in attrs.items():setattr(g,k,v)
            res.append(g.run())
    n=len(res);w=sum(r['winner']=='Force 136' for r in res);m=sum(r['winner']=='MPAJA' for r in res)
    return dict(n=n,win=round(w/n,3),mpaja=round(m/n,3),R=round(sum(r['final_resistance'] for r in res)/n,2)),res

if __name__=='__main__':
    import sys,time
    t=time.time();n=int(sys.argv[1]) if len(sys.argv)>1 else 8
    s,res=evaluate(RuleGame,range(6000,6000+n));print(s,round(time.time()-t,1))
    agg=collections.Counter()
    for r in res:
        for k,v in r['metrics'].items():
            if k.startswith('b_'):agg[k]+=v
    print(agg.most_common(12))

class HybridGame(RuleGame):
    weights=None
    """Use the expert for some decision classes and rules for the rest."""
    HY='full'
    def bot_turn(self,free):
        cls=self.HY
        use_expert=(cls=='full' and 'Op & SA' in free) or (cls=='limited' and 'Op & SA' not in free) or cls=='all'
        if cls=='events' :
            from expert import british_candidates,apply_british,british_value
            # expert decides only whether to take the Event
            self.region_='C'
            if 'Event' in free and self.event not in (6,9):
                p=self.clone();apply_british(p,dict(kind='EVENT',box='Event'))
                q=self.clone();RuleGame.bot_turn(q,free)
                if british_value(p)+0.3>british_value(q):
                    self.chosen['B']='Event';apply_british(self,dict(kind='EVENT',box='Event'));self.inc('b_EVENT');return
            return RuleGame.bot_turn(self,free)
        if use_expert:
            from expert import ExpertGame
            return ExpertGame.bot_turn(self,free)
        return RuleGame.bot_turn(self,free)

# ---- Event conditions (public, countable at the table) ----
def n_terror(g):return sum(v['terror'] for v in g.board.values())
def n_f136_camp(g):return sum(bool(v['force136'] and v['camp']) for v in g.board.values())
def ev_cond(g,j):
    b=g.board
    if j==1:return min(3,n_terror(g))>=2 and g.resistance<20
    if j==2:return sum(not g.sabotage[r] and any(b[s]['opposition'] for s in g.rail_adj(r)) for r in EDGES)>=2
    if j==3:return sum(bool(v['force136']) for v in b.values())>=1 and g.available('red')>=1
    if j==4:return n_f136_camp(g)>=2
    if j==5:return sum(v['red_a']+v['blue_a'] for v in b.values())>=3
    if j==7:return True
    if j in (8,12,15,19,22,27):return True
    if j==10:return g.resources>=6
    if j==11:return sum(bool(ug(b[s])) for s in NORTH)>=2
    if j==13:return sum(v['red_u'] for v in b.values())>=2
    if j==14:return g.count('cache')>=2
    if j==16:return g.available('force136')>=1 and any(b[s]['camp'] and not b[s]['force136'] for s in PROV)
    if j==18:return g.available('blue')>=2
    if j==20:return False
    if j==21:return g.available('blue')>=2
    if j==23:return True
    if j==24:return True
    if j==25:return True
    if j==26:return any(v['force136'] and v['troops'] and ug(v) for v in b.values())
    if j==28:return any(b[s]['camp'] for s in PROV) and (g.available('force136') or g.available('cache'))
    if j==29:return True
    if j==30:return sum(bool(v['police'] and gs(v) and v['opposition']) for v in b.values())>=2
    if j==31:return sum(bool(v['troops'] and v['opposition']) for v in b.values())>=2 and g.resources>=2
    if j==32:return sum(bool(b[s]['camp'] and b[s]['opposition']) for s in PROV)>=2
    return False

class EventRuleGame(RuleGame):
    EV=None   # dict j -> 'always' | 'second'
    def event_ok(self):
        j=self.event;mode=(self.EV or {}).get(j)
        if not mode:return False
        if mode=='second' and 'Op & SA' in self._free:return False
        return ev_cond(self,j)
