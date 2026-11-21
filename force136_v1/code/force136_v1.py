"""Force 136 v1.0 — the printed bot, as code.

A card-driven British opponent for The British Way: Japanese Occupation
(standard standalone scenario; the human plays Japan). Each function names the
rules section it implements. The simulation engine (engine.py, expert.py) is
the separate development executor; this module only makes British choices.

Words used in the printed rules
  F136 space    a space with a Force 136 marker
  red / blue    MPAJA guerrilla / non-MPAJA guerrilla
  cubes         Troops + Police in a space
  good shot     cubes minus Supply Caches in and adjacent to the space is 3 or
                less (the Ambush die then succeeds on at least 3 faces)
  exposed       a F136 marker sharing a space with Kempeitai and no Jungle Camp
                (or any F136 with Kempeitai once the Japanese side of J22 is in play)
"""
from engine import *
from expert import FastGame
import random

MAP_ORDER=list(ORDER)    # Kedah, Perak, Kelantan, Trengganu, Pahang, Selangor, Kuala Lumpur, Negri Sembilan, Johore, N EC, S EC
RAIL_LIST=['Perak-Pahang-Selangor','Negri Sembilan-Pahang','Perak-Kelantan','Thailand-Perak',
           'Thailand-Kelantan *','Negri Sembilan-Johore *','Pahang-Johore *','Thailand-Kedah *']
def mo(s):return MAP_ORDER.index(s)

# §2 Directive deck. Every card starts with PLACE; the card lists the next four goals
# and which of AMBUSH/TRAIN comes first on a Limited Operation.
def card(i,name,goals,limited_first):
    return dict(id=i,name=name,goals=goals,limited_first=limited_first)
DECK=[
 card(1,'Jungle ambush',        ['AMBUSH','INTEL','SUPPLY','TRAIN'],'AMBUSH'),
 card(2,'Hit the convoy',       ['AMBUSH','INTEL','SUPPLY','TRAIN'],'AMBUSH'),
 card(3,'Strike from the hills',['AMBUSH','INTEL','SUPPLY','TRAIN'],'AMBUSH'),
 card(4,'Arm the cells',        ['AMBUSH','INTEL','TRAIN','SUPPLY'],'TRAIN'),
 card(5,'Recruit and strike',   ['AMBUSH','INTEL','TRAIN','SUPPLY'],'TRAIN'),
 card(6,'Ears in the kampongs', ['INTEL','AMBUSH','SUPPLY','TRAIN'],'AMBUSH'),
 card(7,'Count the trains',     ['INTEL','AMBUSH','SUPPLY','TRAIN'],'AMBUSH'),
 card(8,'Radio from the ridge', ['INTEL','AMBUSH','TRAIN','SUPPLY'],'TRAIN'),
 card(9,'Stockpile',            ['AMBUSH','SUPPLY','INTEL','TRAIN'],'TRAIN'),
]
# §9 Levels
LEVELS={'recruit':dict(raid=False,start_r=2,bonus=0),
        'agent':  dict(raid=True, start_r=2,bonus=0),
        'veteran':dict(raid=True, start_r=4,bonus=0),
        'legend': dict(raid=True, start_r=4,bonus=1)}

class Force136(FastGame):
    deck_cards=DECK
    def __init__(self,seed,corner=False,level='agent'):
        FastGame.__init__(self,seed,corner)
        self.level=level;self.L=LEVELS[level]
        self.resistance=self.L['start_r']
        self.dqueue=[];self.ddisc=[];self.dcycle=0;self.directive=None
    # ----------------------------------------------------------------- tests
    def f136_spaces(self):return [s for s in MAP_ORDER if self.board[s]['force136']]
    def good_shot(self,s):
        return cubes(self.board[s])-self.cache_bonus(s)<=3
    def exposed(self,s):
        v=self.board[s];return bool(v['force136'] and v['kempeitai'] and (not v['camp'] or self.cap.get(22)=='S'))
    # ----------------------------------------------------------------- §6.1 Contact
    def place_key(self,s):
        v=self.board[s]
        return (bool(v['kempeitai']),bool(v['cache']) and self.available('cache')>0,cubes(v)>0,-gs(v),-POP[s],mo(s))
    def contact(self,task=None,hold=False):
        b=self.board
        if self.available('force136'):
            dests=[s for s in PROV if not b[s]['force136']]
            if not dests:return []
            s=min(dests,key=self.place_key);b[s]['force136']+=1;self.add_camp(s);self.cleanup()
            return [('Available',s)]
        for src in self.f136_spaces():
            if not self.exposed(src):continue
            v=b[src]
            dests=[d for d in ADJ[src] if d in PROV and not b[d]['force136'] and not b[d]['kempeitai']]
            if not dests:continue
            d=min(dests,key=self.place_key)
            v['force136']-=1;b[d]['force136']+=1
            if blue(v) and not red(b[d]) and gs(v)>1:
                f='blue_u' if v['blue_u'] else 'blue_a';v[f]-=1;b[d][f]+=1
            self.add_camp(d);self.cleanup();return [(src,d)]
        return []
    # ----------------------------------------------------------------- §6.2 Train
    def train_color(self,s):
        v=self.board[s];r=red(v);bl=blue(v);red_ok=v['camp'] or v['cache']
        if r and bl:c='red' if r>=bl else 'blue'
        elif r:c='red'
        elif bl:c='blue'
        else:c='red' if red_ok and self.available('red') else 'blue'
        if c=='red' and not red_ok:return None
        return c
    def place_one(self,s,c):
        v=self.board[s]
        if self.available(c):v[c+'_u']+=1;return True
        donors=[x for x in MAP_ORDER if x!=s and not self.board[x]['force136'] and (self.board[x][c+'_a'] or self.board[x][c+'_u'])
                and self.donor_ok(x)]
        if not donors:return False
        x=min(donors,key=lambda x:(not self.board[x][c+'_a'],-cubes(self.board[x]),mo(x)))
        f=c+('_a' if self.board[x][c+'_a'] else '_u');self.board[x][f]-=1;v[c+'_u']+=1;return True
    def train(self,locations=None,reserve_cache_donors=False):
        n=0
        for s in (locations or [s for s in self.f136_spaces() if POP[s]]):
            for _ in range(2 if self.board[s]['cache'] else 1):
                c=self.train_color(s)
                if not c or not self.place_one(s,c):break
                n+=1
        self.cleanup();return n
    # ----------------------------------------------------------------- §6.3 Ambush
    def ambush_target(self,s,color=None):
        v=self.board[s]
        if not (v[color+'_u'] if color else ug(v)):return None
        if v['police']:return 'Police'
        if s=='Kuala Lumpur':return None
        if v['kempeitai'] and self.good_shot(s):return 'Kempeitai'
        if v['troops'] and self.good_shot(s):return 'Troop'
        return None
    def strike_option(self,s,force_color=None,bose=False):
        if bose:
            v=self.board[s]
            if not (v[force_color+'_u'] if force_color else ug(v)):return None
            return ('Bose',6) if v['troops'] and self.good_shot(s) else None
        t=self.ambush_target(s,force_color);return (t,6) if t else None
    def strike_rank(self,s,color=None,bose=False):return (mo(s),)
    def strike(self,locations=None,color=None,bose=False,extra=True):
        sites=list(locations) if locations is not None else self.f136_spaces()
        if locations is None and extra and self.cap.get(27)=='U' and not bose:
            rem=[s for s in MAP_ORDER if not self.board[s]['force136'] and self.ambush_target(s,color)]
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
        return hits
    # ----------------------------------------------------------------- §6.4 Sabotage
    def rail_choice(self,s,region='C',stack=False,eligible=None):
        if stack:return FastGame.rail_choice(self,s,region,stack,eligible)
        c=[r for r in RAIL_LIST if s in self.rail_adj(r) and not self.sabotage[r] and (eligible is None or r in eligible)]
        return c[0] if c else None
    # ----------------------------------------------------------------- §6.5 Gather
    def gather(self):
        selected=[];revealed=[]
        for k in range(3 if self.cap.get(19)=='U' else 2):
            def targets(a):return self.gather_targets(a,self.cap.get(19)!='S' or k==0)
            anchors=[s for s in self.f136_spaces() if s not in selected and targets(s)]
            if not anchors:break
            a=min(anchors,key=lambda s:(-len(targets(s)),mo(s)))
            selected.append(a)
            for s in targets(a):
                if self.cap.get(22)!='U':self.activate(s)
                self.board[s]['intel']=1 if self.preview else self.secret[s];revealed.append(s)
                if self.preview:self.uncertain=True
        return revealed
    # ----------------------------------------------------------------- §6.6 Supply
    def supply(self):
        n=0;selected=[];remote=False
        for _ in range(3 if self.zipper>=12 else 2):
            if not self.available('cache'):break
            sites=[s for s in PROV if self.board[s]['camp'] and not self.board[s]['cache'] and s not in selected
                   and (self.board[s]['force136'] or self.cap.get(8)=='U' and not remote)]
            if not sites:break
            s=min(sites,key=lambda s:(not self.board[s]['force136'],bool(self.board[s]['kempeitai']),-gs(self.board[s]),-POP[s],mo(s)))
            selected.append(s)
            if not self.board[s]['force136']:remote=True
            if self.cap.get(8)=='S' and self.die('Supply',s)<=2:continue
            self.board[s]['camp']=False;self.board[s]['cache']=True;n+=1
        if self.cap.get(27)=='S' and selected:
            el=[s for s in selected if self.board[s]['opposition']]
            if el:self.board[min(el,key=lambda s:(-POP[s],mo(s)))]['opposition']=False
        return n
    # ----------------------------------------------------------------- §6.7 Raid
    RAID_KINDS=('SABOTAGE','AMBUSH','MAJORITY')
    def raid(self):
        if not self.L['raid']:return []
        b=self.board;dests=[]
        for _ in range(3 if self.zipper==20 else 2):
            best=None
            for d in MAP_ORDER:
                if d in dests:continue
                w=b[d]
                for src in MAP_ORDER:
                    if src not in ADJ[d] or not b[src]['cache']:continue
                    v=b[src]
                    for c in ('red','blue'):
                        if (c=='red' and blue(w)) or (c=='blue' and red(w)):continue
                        have=v[c+'_u']+v[c+'_a']
                        if not have:continue
                        kinds=[]
                        if v[c+'_u'] and self.donor_ok(src,1):
                            if self.rail_choice(d) is not None:kinds.append(('SABOTAGE',1))
                            probe=self.clone();probe.board[src][c+'_u']-=1;probe.board[d][c+'_u']+=1
                            if probe.ambush_target(d,c):kinds.append(('AMBUSH',1))
                        need=cubes(w)-gs(w)+1
                        if not gs(w)>cubes(w) and 1<=need<=2 and have>=need and self.donor_ok(src,need):kinds.append(('MAJORITY',need))
                        for kind,nn in kinds:
                            key=(self.RAID_KINDS.index(kind),mo(d),-gs(v),mo(src),c!='red')
                            if best is None or key<best[0]:best=(key,src,d,c,kind,nn)
            if not best:break
            _,src,d,c,kind,nn=best;v=b[src];w=b[d]
            for i in range(nn):
                f=c+'_u' if (kind!='MAJORITY' or v[c+'_u']) else c+'_a'
                v[f]-=1;w[f]+=1
            dests.append(d)
            if kind=='AMBUSH':self.strike([d],c,extra=False)
            elif kind=='SABOTAGE':
                r=self.rail_choice(d)
                if r:self.activate(d,c);self.sabotage[r]+=1
            self.cleanup()
        return dests
    # ----------------------------------------------------------------- §5 goals
    def useful_ambush(self):return any(self.ambush_target(s) for s in self.f136_spaces())
    def sa_does(self,p,x):
        q=p.clone()
        if x=='GATHER2':return len(q.gather())>=2
        return bool(q.special(x))
    def first_sa(self,after,order):
        for x in order:
            if self.sa_does(after,x):return x.replace('2','')
        return None
    def goal(self,name,full):
        if name=='PLACE':
            if not self.available('force136'):return None
            if not full:return dict(op='CONTACT')
            p=self.clone();p.contact()
            return dict(op='CONTACT',sa=self.first_sa(p,('GATHER2','SUPPLY','RAID','GATHER')))
        if name=='AMBUSH':
            if not self.useful_ambush():return None
            if not full:return dict(op='AMBUSH')
            p=self.clone();p.strike()
            return dict(op='AMBUSH',sa=self.first_sa(p,('GATHER2','RAID','GATHER')))
        if name=='INTEL':
            if not full:return None
            for op in ('AMBUSH','SABOTAGE','CONTACT'):
                p=self.clone()
                if op=='AMBUSH':
                    if not self.useful_ambush():continue
                    p.strike()
                elif op=='SABOTAGE':
                    if not p.rail('C'):continue
                elif not p.contact():continue
                if len(p.clone().gather())>=2:return dict(op=op,sa='GATHER')
            return None
        if name=='SUPPLY':
            if not full or not self.available('cache'):return None
            p=self.clone()
            if not p.train():return None
            return dict(op='TRAIN',sa='SUPPLY') if p.clone().supply() else None
        if name=='TRAIN':
            p=self.clone()
            if not p.train():return None
            if not full:return dict(op='TRAIN')
            return dict(op='TRAIN',sa=self.first_sa(p,('SUPPLY','RAID')))
        if name=='CONTACT':
            p=self.clone()
            if not p.contact():return None
            if not full:return dict(op='CONTACT')
            return dict(op='CONTACT',sa=self.first_sa(p,('SUPPLY','GATHER','RAID')))
        raise ValueError(name)
    # ----------------------------------------------------------------- §4 the turn
    def draw_directive(self):
        if not self.dqueue:
            cards=list(self.ddisc) if self.ddisc else list(self.deck_cards)
            random.Random(stable(self.seed,'directive',self.dcycle)).shuffle(cards)
            self.dcycle+=1;self.dqueue=cards;self.ddisc=[]
        self.directive=self.dqueue.pop(0);self.ddisc.append(self.directive)
    def choose(self,free):
        d=self.directive;plan=None
        if 'Op & SA' in free:
            for g in ['PLACE']+d['goals']+['CONTACT']:
                p=self.goal(g,True)
                if p:return dict(p,box='Op & SA',goal=g)
        if 'Limited' in free:
            second='TRAIN' if d['limited_first']=='AMBUSH' else 'AMBUSH'
            for g in ['PLACE',d['limited_first'],second,'CONTACT']:
                p=self.goal(g,False)
                if p:return dict(p,box='Limited',goal=g)
        return dict(op='PASS',box=min(free,key=BOXES.index),goal='PASS')
    def execute(self,plan):
        op=plan['op']
        if op in('CONTACT','PASS'):self.contact()
        elif op=='TRAIN':self.train()
        elif op=='AMBUSH':self.strike()
        elif op=='SABOTAGE':self.rail('C')
        if plan.get('sa'):self.special(plan['sa'])
    def bot_turn(self,free):
        self.card=None
        self.draw_directive()
        plan=self.choose(free)
        self.chosen['B']=plan['box'];self.execute(plan)
        self.inc('g_'+plan['goal']);self.inc('o_'+plan['box'][0]+':'+plan['op']+('+'+plan['sa'] if plan.get('sa') else ''))
        self.last_plan=plan
    # ----------------------------------------------------------------- §7 between turns
    def placement_rank(self,s):return (mo(s),)
    def opp_pick(self,sites):return min(sites,key=lambda s:(-POP[s],mo(s)))
    def icon(self,j):
        b=self.board
        if j in MOBILIZE:
            sites=[s for s in PROV if b[s]['camp'] and not b[s]['terror'] and not b[s]['opposition']]
            if sites:b[self.opp_pick(sites)]['opposition']=True
            self.cleanup();return
        if j in KILL:
            sites=[s for s in MAP_ORDER if red(b[s]) and b[s]['police']]
            if sites:b[min(sites,key=lambda s:(b[s]['police']!=1,not b[s]['force136'],mo(s)))]['police']-=1
            self.cleanup();return
        return FastGame.icon(self,j)
    def score_only(self,final=False):
        r=FastGame.score_only(self,final)
        if self.L['bonus'] and not final:self.resistance=clamp(self.resistance+self.L['bonus'])
        return r
    def propaganda(self,final=False):
        result=self.score_only(final);self.record('Final scoring' if final else 'Nonfinal scoring',result)
        if final:return result
        b=self.board
        for rail in RAIL_LIST:                                   # Resources phase, British
            if self.sabotage[rail]:
                sites=[s for s in self.rail_adj(rail) if POP[s] and not b[s]['terror'] and not b[s]['opposition']]
                if sites:b[self.opp_pick(sites)]['opposition']=True
        self.construct()                                          # Japanese Construct
        self.supply()                                             # Support phase, British Supply
        self.reprisal()                                           # Japanese Reprisal
        moved=set()                                               # Redeploy, British
        for src in MAP_ORDER:
            if not b[src]['force136'] or src in moved or not self.exposed(src):continue
            dests=[s for s in PROV if b[s]['camp'] and not b[s]['force136'] and not b[s]['kempeitai']]
            if dests:
                d=min(dests,key=lambda s:(-gs(b[s]),mo(s)));b[src]['force136']-=1;b[d]['force136']+=1;moved.add(d)
        sites=[s for s in ORDER if b[s]['troops']>gs(b[s])]       # Redeploy, Japanese (engine policy)
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
        for v in b.values():                                      # Reset
            v['terror']=0
            for c in ['red','blue']:v[c+'_u']+=v[c+'_a'];v[c+'_a']=0
        self.reset_intel(self.campaign)
        b['Kuala Lumpur']['troops']+=self.away_troops;self.away_troops=0
        if self.away_f:                                           # J25 marker returns (British choice)
            camps=[s for s in PROV if b[s]['camp']]
            if camps:
                dst=min(camps,key=lambda s:(bool(b[s]['kempeitai']),bool(b[s]['force136']),-gs(b[s]),ix(s)))
                b[dst]['force136']+=self.away_f
            self.away_f=0
        self.campaign+=1;self.first='B';self.regular_seen=0;self.chosen={};self.record('Reset complete',{})
        return result
