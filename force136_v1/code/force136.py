"""Force 136 v1 — card-driven British opponent for Japanese Occupation, as code.

This module is the rules-as-code for the printed bot. Every choice below is
meant to match one sentence of the printed rules. It overrides the engine's
British procedures, so Events and Propaganda use the same priorities.

Vocabulary used in the printed rules:
  F136 space  = a space with a Force 136 marker.
  red         = MPAJA guerrilla (red cylinder); blue = non-MPAJA guerrilla.
  good shot   = an Ambush die roll that succeeds on 3+ faces (die + caches in or
                adjacent > cubes in the space).
"""
from engine import *
from expert import FastGame
import random

MAPO=list(ORDER)          # printed map order
def mo(s):return MAPO.index(s)

# ---------------------------------------------------------------- the deck
# Each Directive card: name, full-turn goal order, Raid/Gather preference.
A,T='AMBUSH>TRAIN','TRAIN>AMBUSH'
def _card(i,name,goals,lim):
    full=['PLACE']+[{'AMBUSH':'STRIKE'}.get(g,g) for g in goals]
    limited=['PLACE','STRIKE','TRAIN','CONTACT'] if lim==A else ['PLACE','TRAIN','STRIKE','CONTACT']
    return dict(id=i,name=name,goals=goals,lim=lim,full=full,limited=limited)
DECK=[
 _card(1,'Jungle ambush',      ['AMBUSH','INTEL','SUPPLY','TRAIN'],A),
 _card(2,'Hit the convoy',     ['AMBUSH','INTEL','SUPPLY','TRAIN'],A),
 _card(3,'Strike from the hills',['AMBUSH','INTEL','SUPPLY','TRAIN'],A),
 _card(4,'Arm the cells',      ['AMBUSH','INTEL','TRAIN','SUPPLY'],T),
 _card(5,'Recruit and strike', ['AMBUSH','INTEL','TRAIN','SUPPLY'],T),
 _card(6,'Ears in the kampongs',['INTEL','AMBUSH','SUPPLY','TRAIN'],A),
 _card(7,'Count the trains',   ['INTEL','AMBUSH','SUPPLY','TRAIN'],A),
 _card(8,'Radio from the ridge',['INTEL','AMBUSH','TRAIN','SUPPLY'],T),
 _card(9,'Stockpile',          ['AMBUSH','SUPPLY','INTEL','TRAIN'],T),
]
LEVELS={
 'recruit':dict(noraid=True),
 'agent':dict(),
 'veteran':dict(start_r=4),
 'legend':dict(start_r=4,prop_bonus=1),
 'mastermind':dict(start_r=6,prop_bonus=2),
}
STANDARD=dict(simple_rail=True,place_pref='nocubes',strike_sa=('GATHER2','RAID','GATHER'),place_sa=('GATHER2','SUPPLY','RAID','GATHER'))

class F136Game(FastGame):
    directives=DECK
    P=STANDARD
    level='agent'
    direction=1
    def mo(self,s):return MAPO.index(s)*self.direction
    def __init__(self,seed,corner=False,level=None):
        if level:self.level=level
        if self.level!='agent' or LEVELS.get(self.level):self.P=dict(self.P,**LEVELS[self.level])
        FastGame.__init__(self,seed,corner)
        self.dqueue=[];self.ddisc=[];self.dcycle=0;self.directive=None
        if self.P.get('start_r'):self.resistance=self.P['start_r']
        if self.P.get('start_zip'):self.move_zipper(target=self.P['start_zip'])
    # ------------------------------------------------------ helpers
    def f136_spaces(self):return [s for s in MAPO if self.board[s]['force136']]
    def good_shot(self,s,need=3):
        v=self.board[s];bonus=self.cache_bonus(s)
        return sum(d+bonus>cubes(v) for d in range(1,7))>=need
    # ------------------------------------------------------ AMBUSH
    def ambush_target(self,s,color=None):
        v=self.board[s]
        if not (v[color+'_u'] if color else ug(v)):return None
        if s=='Kuala Lumpur':
            return 'Police' if v['police'] else None
        if self.good_shot(s):
            if v['kempeitai']:return 'Kempeitai'
            if v['troops']:return 'Troop'
        if v['police']:return 'Police'
        return None
    def strike_option(self,s,force_color=None,bose=False):
        # compatibility for engine callers (J11/J13/J26, Raid probes)
        if bose:
            v=self.board[s]
            if not (v[force_color+'_u'] if force_color else ug(v)):return None
            return ('Bose',6) if v['troops'] and self.good_shot(s) else None
        t=self.ambush_target(s,force_color)
        return (t,6) if t else None
    def strike_rank(self,s,color=None,bose=False):return (self.mo(s),)
    def strike(self,locations=None,color=None,bose=False,extra=True):
        sites=[s for s in (locations if locations is not None else self.f136_spaces())]
        if locations is None and extra and self.cap.get(27)=='U' and not bose:
            rem=[s for s in MAPO if not self.board[s]['force136'] and self.ambush_target(s,color)]
            if rem:sites.append(rem[0])
        hits=[]
        for s in sorted(sites,key=mo):
            if bose:
                if not self.strike_option(s,color,True):continue
                self.activate(s,color)
                if self.die('Ambush',s)+self.cache_bonus(s)>cubes(self.board[s]):self.resistance=clamp(self.resistance+2)
                hits.append((s,'Bose'));break
            t=self.ambush_target(s,color)
            if not t:continue
            self.activate(s,color);hits.append((s,t))
            if t=='Police':self.board[s]['police']-=1
            elif self.die('Ambush',s)+self.cache_bonus(s)>cubes(self.board[s]):
                f='kempeitai' if t=='Kempeitai' else 'troops'
                self.board[s][f]-=1;self.board['Kuala Lumpur'][f]+=1;self.resistance=clamp(self.resistance+1)
        self.cleanup();self.inc('ambush_attempts',len(hits));return hits
    # ------------------------------------------------------ CONTACT
    def place_rank(self,s):
        b=self.board[s];pp=self.P.get('place_pref','default')
        if pp=='guerrillas':return (bool(b['kempeitai']),-gs(b),bool(b['cache']) if self.available('cache') else False,-POP[s],self.mo(s))
        if pp=='intel':
            reach=sum(1 for t in ({s}|ADJ[s]) if POP[t] and self.board[t]['intel'] is None and ug(self.board[t]))
            return (bool(b['kempeitai']),-reach,bool(b['cache']) if self.available('cache') else False,-gs(b),-POP[s],self.mo(s))
        if pp=='nocubes':return (bool(b['kempeitai']),bool(b['cache']) if self.available('cache') else False,cubes(b)>0,-gs(b),-POP[s],self.mo(s))
        return (bool(b['kempeitai']),bool(b['cache']) if self.available('cache') else False,-gs(b),-POP[s],self.mo(s))
    def contact(self,task=None,hold=False):
        """Place an Available F136; otherwise move one exposed F136 to safety."""
        b=self.board
        if hold:return []
        if self.available('force136'):
            dests=[s for s in PROV if not b[s]['force136']]
            if not dests:return []
            s=min(dests,key=self.place_rank);b[s]['force136']+=1;self.add_camp(s);self.cleanup()
            return [('Available',s)]
        # move: an exposed marker (Kempeitai, no Camp) to an adjacent Province without F136 or Kempeitai
        for src in self.f136_spaces():
            v=b[src]
            if v['kempeitai'] and (not v['camp'] or self.cap.get(22)=='S'):
                dests=[d for d in ADJ[src] if d in PROV and not b[d]['force136'] and not b[d]['kempeitai']]
                if dests:
                    d=min(dests,key=self.place_rank)
                    v['force136']-=1;b[d]['force136']+=1
                    # escort: 1 blue guerrilla if the destination has no red
                    if blue(v) and not red(b[d]) and gs(v)>1:
                        f='blue_u' if v['blue_u'] else 'blue_a';v[f]-=1;b[d][f]+=1
                    self.add_camp(d);self.cleanup();return [(src,d)]
        return []
    # ------------------------------------------------------ TRAIN
    TRAIN_MODE='last'          # v1.0.1: donors first, then refresh in the Train space
    def train_color(self,s):
        v=self.board[s];r=red(v);bl=blue(v);red_ok=v['camp'] or v['cache']
        if r and bl:c='red' if r>=bl else 'blue'
        elif r:c='red'
        elif bl:c='blue'
        elif self.P.get('color_text'):c='red' if red_ok and self.available('red') else 'blue'
        else:c='red' if red_ok and (self.available('red') or not self.available('blue') or self.P.get('simple_color')) else 'blue'
        if c=='red' and not red_ok:return None
        return c
    def train_one(self,s,c,used):
        v=self.board[s]
        if self.available(c):v[c+'_u']+=1;return True
        mode=self.TRAIN_MODE
        if mode in('refresh','both') and v[c+'_a']:
            v[c+'_a']-=1;v[c+'_u']+=1;return True
        if self.P.get('nodonor'):return False
        if mode in('donor','both','last'):
            donors=[x for x in MAPO if x!=s and not self.board[x]['force136'] and (self.board[x][c+'_a'] or self.board[x][c+'_u'])
                    and self.donor_ok(x)]
            if donors:
                x=min(donors,key=lambda x:(not self.board[x][c+'_a'],-cubes(self.board[x]),self.mo(x)))
                f=c+('_a' if self.board[x][c+'_a'] else '_u');self.board[x][f]-=1;v[c+'_u']+=1;return True
        if mode=='last' and v[c+'_a']:
            v[c+'_a']-=1;v[c+'_u']+=1;return True
        return False
    def train(self,locations=None,reserve_cache_donors=False):
        n=0;used={}
        for s in (locations or [s for s in self.f136_spaces() if POP[s]]):
            v=self.board[s]
            for _ in range(2 if v['cache'] else 1):
                c=self.train_color(s)
                if not c or not self.train_one(s,c,used):break
                n+=1
        self.cleanup();return n
    # ------------------------------------------------------ GATHER
    def gather(self):
        selected=[];revealed=[]
        for k in range(3 if self.cap.get(19)=='U' else 2):
            def targets(a):return self.gather_targets(a,self.cap.get(19)!='S' or k==0)
            anchors=[s for s in self.f136_spaces() if s not in selected and targets(s)]
            if not anchors:break
            a=min(anchors,key=lambda s:(-len(targets(s)),self.mo(s)))
            selected.append(a)
            for s in targets(a):
                if self.cap.get(22)!='U':self.activate(s)
                self.board[s]['intel']=1 if self.preview else self.secret[s];revealed.append(s)
                if self.preview:self.uncertain=True
        self.inc('gather_reveals',len(revealed));return revealed
    # ------------------------------------------------------ SUPPLY
    def supply(self):
        """Choose Provinces first (limit, and no more than Caches Available), then convert/roll."""
        limit=min(3 if self.zipper>=12 else 2,self.available('cache'))
        selected=[];remote=False
        while len(selected)<limit:
            sites=[s for s in PROV if self.board[s]['camp'] and not self.board[s]['cache'] and s not in selected
                   and (self.board[s]['force136'] or self.cap.get(8)=='U' and not remote)]
            if not sites:break
            s=min(sites,key=lambda s:(not self.board[s]['force136'],bool(self.board[s]['kempeitai']),-gs(self.board[s]),-POP[s],self.mo(s)))
            selected.append(s)
            if not self.board[s]['force136']:remote=True
        n=0
        for s in selected:
            if self.cap.get(8)=='S' and self.die('Supply',s)<=2:continue
            self.board[s]['camp']=False;self.board[s]['cache']=True;n+=1
        if self.cap.get(27)=='S' and selected:
            el=[s for s in selected if self.board[s]['opposition']]
            if el:self.board[min(el,key=lambda s:(POP[s],self.mo(s)))]['opposition']=False
        self.cleanup()
        self.inc('caches_built',n);return n
    # ------------------------------------------------------ RAID
    RAID_ORDER=('SABOTAGE','AMBUSH','MAJORITY')
    def raid(self):
        if self.P.get('noraid'):return []
        return self.raid_()
    def raid_(self):
        """Up to 2 (3 at Zipper 20) destinations adjacent to a cache.
        Destination: 1 Ambush, 2 Sabotage, 3 new guerrilla majority (then map order).
        Source: adjacent cache space that keeps a guerrilla and its majority; most guerrillas.
        Never mix colours; prefer red. Send 1 underground guerrilla to attack, else the
        fewest (1-2) that create a majority."""
        b=self.board;dests=[];moved=set()
        for _ in range(3 if self.zipper==20 else 2):
            best=None
            for d in MAPO:
                if d in dests:continue
                w=b[d]
                for src in MAPO:
                    if src not in ADJ[d]:continue
                    v=b[src]
                    if not v['cache']:continue
                    for c in ('red','blue'):
                        if (c=='red' and blue(w)) or (c=='blue' and red(w)):continue
                        have=v[c+'_u']+v[c+'_a']
                        if not have:continue
                        kinds=[]
                        if v[c+'_u'] and self.donor_ok(src,1):
                            probe=self.clone();probe.board[src][c+'_u']-=1;probe.board[d][c+'_u']+=1
                            if probe.ambush_target(d,c):kinds.append(('AMBUSH',1))
                            if self.rail_choice(d,'C') is not None and d!='Kuala Lumpur' or (d=='Kuala Lumpur' and self.rail_choice(d,'C')):
                                kinds.append(('SABOTAGE',1))
                        need=cubes(w)-gs(w)+1
                        if not gs(w)>cubes(w) and 1<=need<=2 and have>=need and self.donor_ok(src,need):kinds.append(('MAJORITY',need))
                        for kind,nn in kinds:
                            key=(self.RAID_ORDER.index(kind),self.mo(d),-gs(v),self.mo(src),c!='red')
                            if best is None or key<best[0]:best=(key,src,d,c,kind,nn)
            if not best:break
            _,src,d,c,kind,nn=best;v=b[src];w=b[d]
            for i in range(nn):
                f=c+'_u' if v[c+'_u'] else c+'_a'
                if kind!='MAJORITY':f=c+'_u'
                v[f]-=1;w[f]+=1
            dests.append(d)
            if kind=='AMBUSH':self.strike([d],c,extra=False)
            elif kind=='SABOTAGE':
                r=self.rail_choice(d,'C')
                if r:self.activate(d,c);self.sabotage[r]+=1
            self.cleanup()
        self.inc('raid_destinations',len(dests));return dests
    # ------------------------------------------------------ goals
    RAIL_LIST=['Perak-Pahang-Selangor','Negri Sembilan-Pahang','Perak-Kelantan','Thailand-Perak','Thailand-Kelantan *','Negri Sembilan-Johore *','Pahang-Johore *','Thailand-Kedah *']
    def rail_choice(self,s,region='C',stack=False,eligible=None):
        if stack or not self.P.get('simple_rail'):return FastGame.rail_choice(self,s,region,stack,eligible)
        c=[r for r in self.RAIL_LIST if s in self.rail_adj(r) and not self.sabotage[r] and (eligible is None or r in eligible)]
        return c[0] if c else None
    def rail(self,region='C',locations=None,color=None,extra=True):
        if locations is not None:return FastGame.rail(self,region,locations,color,extra)
        b=self.board;sites=self.f136_spaces()
        if extra and self.cap.get(27)=='U':
            more=[s for s in MAPO if not b[s]['force136'] and ug(b[s]) and self.rail_choice(s)]
            if more:sites=sorted(sites+more[:1],key=self.mo)
        return FastGame.rail(self,region,sites,color,False)
    def gather_n(self):
        p=self.clone();return len(p.gather())
    def useful_ambush(self):
        t=[self.ambush_target(s) for s in self.f136_spaces()];t=[x for x in t if x]
        need=self.P.get('strike_need','any')
        if need=='any':return bool(t)
        if need=='police_or_two':return 'Police' in t or len(t)>=2
        if need=='two':return len(t)>=2
        return bool(t)
    def sa_does(self,p,x):
        q=p.clone()
        if x=='GATHER2':return len(q.gather())>=2
        return bool(q.special(x))
    def try_sa(self,order):
        for sa in order:
            p=self.clone()
            if p.special(sa):return sa
        return None
    def goal_plan(self,goal,full):
        if not self.preview:self.inc('checks')
        b=self.board
        if goal=='PLACE':
            if not self.available('force136'):return None
            if not full:return dict(op='CONTACT')
            return dict(op='CONTACT',sa_list=self.P.get('place_sa',('SUPPLY','GATHER','RAID')))
        if goal=='STRIKE':
            if not self.useful_ambush():return None
            if not full:return dict(op='STRIKE')
            return dict(op='STRIKE',sa_list=self.P.get('strike_sa',('GATHER','RAID')))
        if goal=='INTEL':
            if not full:return None
            for op in ('STRIKE','RAIL','CONTACT'):
                p=self.clone()
                if op=='STRIKE' and not self.useful_ambush():continue
                if op=='RAIL' and not p.rail('C',extra=False):continue
                if op=='STRIKE':p.strike(extra=False)
                if op=='CONTACT' and not p.contact():continue
                if len(p.clone().gather())>=self.P.get('intel_min',2):return dict(op=op,sa='GATHER')
            return None
        if goal=='SUPPLY':
            if not full or not self.available('cache'):return None
            p=self.clone()
            if not p.train() and self.P.get('supply_needs_train'):return None
            if p.clone().supply():return dict(op='TRAIN',sa='SUPPLY')
            return None
        if goal=='TRAIN':
            p=self.clone()
            if not p.train():return None
            if not full:return dict(op='TRAIN')
            return dict(op='TRAIN',sa_list=self.P.get('train_sa',('SUPPLY','RAID')))
        if goal=='CONTACT':
            p=self.clone()
            if not p.contact():return None
            if not full:return dict(op='CONTACT')
            return dict(op='CONTACT',sa_list=('SUPPLY','GATHER','RAID'))
        raise ValueError(goal)
    def draw_directive(self):
        if not self.dqueue:
            cards=list(self.ddisc) if self.ddisc else list(self.directives)
            random.Random(stable(self.seed,'directive',self.dcycle)).shuffle(cards)
            self.dcycle+=1;self.dqueue=cards;self.ddisc=[]
        self.directive=self.dqueue.pop(0);self.ddisc.append(self.directive)
    # ------------------------------------------------------ between turns
    def placement_rank(self,s):
        # Mobilize / forced placements when pieces run short: map order
        return (self.mo(s),)
    def opp_pick(self,sites):
        return min(sites,key=lambda s:(-POP[s],self.mo(s)))
    def icon(self,j):
        b=self.board
        if j in MOBILIZE:
            sites=[s for s in PROV if b[s]['camp'] and not b[s]['terror'] and not b[s]['opposition']]
            if sites:b[self.opp_pick(sites)]['opposition']=True
            self.cleanup();return
        if j in KILL:
            sites=[s for s in MAPO if red(b[s]) and b[s]['police']]
            if sites:b[min(sites,key=lambda s:(b[s]['police']!=1,not b[s]['force136'],self.mo(s)))]['police']-=1
            self.cleanup();return
        return FastGame.icon(self,j)
    def redeploy_f136(self):
        b=self.board
        movers=[(src,b[src]['force136']) for src in MAPO if b[src]['force136'] and b[src]['kempeitai']
                and (not b[src]['camp'] or self.cap.get(22)=='S')]
        for src,n in movers:
            for _ in range(n):
                dests=[s for s in PROV if b[s]['camp'] and not b[s]['force136'] and not b[s]['kempeitai']]
                if not dests:break
                d=min(dests,key=lambda s:(-gs(b[s]),self.mo(s)));b[src]['force136']-=1;b[d]['force136']+=1
    def propaganda(self,final=False):
        result=self.score_only(final);self.record('Final scoring' if final else 'Nonfinal scoring',result)
        if final:return result
        b=self.board
        for rail in self.RAIL_LIST:
            if self.sabotage[rail]:
                sites=[s for s in self.rail_adj(rail) if POP[s] and not b[s]['terror'] and not b[s]['opposition']]
                if sites:b[self.opp_pick(sites)]['opposition']=True
        self.construct();self.supply();self.reprisal()
        self.redeploy_f136()
        sites=[s for s in ORDER if b[s]['troops']>gs(b[s])]
        if sites:
            movable=0
            for s in ORDER:
                keep=min(b[s]['police'],1) if s not in sites and b[s]['force136'] and b[s]['kempeitai'] else 0
                movable+=b[s]['police']-keep;b[s]['police']=keep
            ranked=sorted(sites,key=lambda s:(bool(b[s]['police']),not bool(b[s]['force136']),ix(s)))
            for i in range(movable):b[ranked[i%len(ranked)]]['police']+=1
            total=self.count('kempeitai')
            for v in b.values():v['kempeitai']=0
            ranked=sorted(sites,key=lambda s:(not bool(b[s]['force136']),gs(b[s])-b[s]['police'],ix(s)))
            for i in range(total):b[ranked[i%len(ranked)]]['kempeitai']+=1
        for v in b.values():
            v['terror']=0
            for c in ['red','blue']:v[c+'_u']+=v[c+'_a'];v[c+'_a']=0
        self.reset_intel(self.campaign)
        b['Kuala Lumpur']['troops']+=self.away_troops;self.away_troops=0
        if self.away_f:
            camps=[s for s in PROV if b[s]['camp']]
            if camps:
                dst=min(camps,key=lambda s:(bool(b[s]['kempeitai']),bool(b[s]['force136']),-gs(b[s]),ix(s)))
                b[dst]['force136']+=self.away_f
            self.away_f=0
        self.campaign+=1;self.first='B';self.regular_seen=0;self.chosen={};self.record('Reset complete',{})
        return result
    def score_only(self,final=False):
        r=FastGame.score_only(self,final)
        bonus=self.P.get('prop_bonus',0)
        if bonus and (not final or self.P.get('bonus_final')):
            self.resistance=clamp(self.resistance+bonus)
            if final:
                self.winner='Japan' if self.resistance<18 else 'Force 136' if self.resistance==20 or self.count('camp')<self.count('force136') else 'MPAJA'
        return r
    def die(self,tag,space=''):
        d=FastGame.die(self,tag,space)
        if tag=='Ambush' and self.P.get('amb_bonus') and not self.preview:d+=self.P['amb_bonus']
        return d
    def event_ok(self,free):return False
    def window_open(self):
        block=(self.draw-1)//7;pos=(self.draw-1)%7+1
        return pos>=5 and self.campaign==block+1
    def execute(self,plan):
        op=plan['op']
        if op=='CONTACT':self.contact(hold=plan.get('hold',False))
        elif op=='TRAIN':self.train()
        elif op=='STRIKE':self.strike()
        elif op=='RAIL':self.rail('C')
        if plan.get('sa_list'):
            plan['sa']=None
            for x in plan['sa_list']:
                if self.sa_does(self,x):plan['sa']=x.replace('2','');break
        if plan.get('sa'):self.special(plan['sa'])
    def bot_turn(self,free):
        self.card={'id':'D','rail_order':'C','primary':'SUPPLY','other_special':'SUPPLY > GATHER > RAID','preparation':'TRAIN','b_events':'NO'}
        self.draw_directive();d=self.directive
        self.direction=-1 if d.get('south') else 1
        plan=None
        if 'Event' in free and self.event not in (6,9) and self.event_ok(free):
            plan=dict(op='EVENT',box='Event')
        order=list(d['full'])
        if self.P.get('late_intel') and self.window_open():
            pos=self.P['late_intel']
            order=[g for g in order if g!='INTEL'];order.insert(0 if pos=='top' else 1,'INTEL')
        if self.P.get('final_supply') and self.campaign==3 and self.count('camp')>=self.count('force136'):
            order=[g for g in order if g!='SUPPLY'];order.insert(0,'SUPPLY')
        if not plan and self.P.get('jp_event_limited') and self.chosen.get('J')=='Event' and 'Limited' in free:
            for goal in self.P.get('limited',['PLACE','STRIKE','TRAIN','CONTACT']):
                p=self.goal_plan(goal,False)
                if p:plan=dict(p,box='Limited',goal=goal);break
        if not plan and 'Op & SA' in free:
            for goal in order+['CONTACT']:
                p=self.goal_plan(goal,True)
                if p:plan=dict(p,box='Op & SA',goal=goal);break
        if not plan and 'Limited' in free:
            for goal in d.get('limited',self.P.get('limited',['PLACE','STRIKE','TRAIN','CONTACT'])):
                p=self.goal_plan(goal,False)
                if p:plan=dict(p,box='Limited',goal=goal);break
        if not plan:plan=dict(op='PASS',box=min(free,key=BOXES.index))
        self.chosen['B']=plan['box']
        if plan['op']=='EVENT':self.execute_event(self.event,'U')
        elif plan['op']=='PASS':self.contact()
        else:self.execute(plan)
        self.inc('b_'+plan['op']+('+'+plan['sa'] if plan.get('sa') else ''))
        self.card=None
