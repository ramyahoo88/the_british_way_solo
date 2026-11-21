"""Research executor for Japanese Occupation; paper bot v0.2 is separate input.

Selectors use public fields; secret Intel resides in a referee-only dictionary.
This is a new development model, not an independently certified game engine.
"""
from __future__ import annotations
from copy import deepcopy
from pathlib import Path
import hashlib,json,random
ROOT=Path(__file__).resolve().parent
DATA=json.loads((ROOT/'baseline/bot_data.json').read_text())
ORDER=('Kedah','Perak','Kelantan','Trengganu','Pahang','Selangor','Kuala Lumpur','Negri Sembilan','Johore','Northern EC','Southern EC')
POP=dict(zip(ORDER,[2,3,2,1,1,1,2,2,2,0,0]))
PROV=tuple(s for s in ORDER if s not in ('Kuala Lumpur','Northern EC','Southern EC'))
MOUNTAIN={'Perak','Selangor'};JUNGLE=set(PROV)-MOUNTAIN
NORTH={'Kedah','Perak','Kelantan'}
ADJ={
 'Kedah':{'Perak'},'Perak':{'Kedah','Kelantan','Pahang','Selangor','Northern EC'},
 'Kelantan':{'Perak','Trengganu','Pahang','Northern EC'},'Trengganu':{'Kelantan','Pahang'},
 'Pahang':{'Perak','Kelantan','Trengganu','Selangor','Kuala Lumpur','Negri Sembilan','Johore','Northern EC','Southern EC'},
 'Selangor':{'Perak','Pahang','Kuala Lumpur','Negri Sembilan'},'Kuala Lumpur':{'Selangor','Pahang','Negri Sembilan'},
 'Negri Sembilan':{'Selangor','Kuala Lumpur','Pahang','Johore','Southern EC'},'Johore':{'Negri Sembilan','Pahang','Southern EC'},
 'Northern EC':{'Perak','Kelantan','Pahang'},'Southern EC':{'Pahang','Negri Sembilan','Johore'}}
# Border interiors and their EC/Kuala Lumpur ends. Corner sensitivity is exposed
# as a named option rather than quietly deciding an unresolved map reading.
RA={
 'Thailand-Kedah *':{'Kedah'},'Thailand-Perak':{'Perak'},'Thailand-Kelantan *':{'Kelantan'},
 'Perak-Kelantan':{'Perak','Kelantan','Northern EC'},
 'Perak-Pahang-Selangor':{'Perak','Pahang','Selangor','Northern EC','Kuala Lumpur'},
 'Negri Sembilan-Pahang':{'Negri Sembilan','Pahang','Kuala Lumpur','Southern EC'},
 'Negri Sembilan-Johore *':{'Negri Sembilan','Johore','Southern EC'},
 'Pahang-Johore *':{'Pahang','Johore','Southern EC'}}
EDGES={
 'Thailand-Kedah *':('Exit K','NW'),'Thailand-Perak':('NW','N'),
 'Thailand-Kelantan *':('N','Exit T'),'Perak-Kelantan':('N','Northern EC'),
 'Perak-Pahang-Selangor':('Northern EC','Kuala Lumpur'),
 'Negri Sembilan-Pahang':('Kuala Lumpur','Southern EC'),
 'Negri Sembilan-Johore *':('Southern EC','Exit S'),'Pahang-Johore *':('Southern EC','Exit E')}
MOBILIZE={1,2,3,4,10,12,14,15,18,23,24,30,31,32}
FOOD={5,6,11,19,27,28};SEIZE={7,8,9,16,17,25};KILL={13,20,21,22,26,29}
CAPS={8,12,15,19,22,27}
PAIR={'TRAIN':['SUPPLY','RAID'],'CONTACT':['SUPPLY','GATHER','RAID'],'RAIL':['GATHER','RAID'],'STRIKE':['GATHER','RAID']}
BOXES=['Limited','Event','Op & SA']
def ix(s):return ORDER.index(s)
def gs(v):return sum(v[k] for k in ('red_u','red_a','blue_u','blue_a'))
def ug(v):return v['red_u']+v['blue_u']
def red(v):return v['red_u']+v['red_a']
def blue(v):return v['blue_u']+v['blue_a']
def cubes(v):return v['troops']+v['police']
def clamp(x):return min(20,max(0,x))
def stable(seed,*args):return int.from_bytes(hashlib.sha256(repr((seed,args)).encode()).digest()[:8],'big')
def new_board():
    return {s:dict(population=POP[s],troops=0,police=0,red_u=0,red_a=0,blue_u=0,blue_a=0,
                   force136=0,kempeitai=0,camp=False,cache=False,new_village=False,
                   opposition=False,terror=0,intel=None) for s in ORDER}

def score_terms(b,resources):
    return dict(intel=sum(v['intel'] or 0 for v in b.values()),caches=sum(v['cache'] for v in b.values()),
                majorities=sum(gs(v)>cubes(v) for v in b.values()),
                resource_penalty=resources//4,neutral_population=sum(v['population'] for v in b.values() if not v['opposition']),
                neutral_penalty=sum(v['population'] for v in b.values() if not v['opposition'])//5,
                police_penalty=sum(v['police']>0 for v in b.values())//3)

def live_and_yield(sabotage):
    graph={}
    for r,(a,b) in EDGES.items():
        if not sabotage[r]:graph.setdefault(a,[]).append((b,r));graph.setdefault(b,[]).append((a,r))
    live=set();yields={}
    for ec in ('Northern EC','Southern EC'):
        exits=set()
        def visit(n,seen,path):
            if n.startswith('Exit '):exits.add(n);live.update(path);return
            for nxt,r in graph.get(n,[]):
                if nxt not in seen:visit(nxt,seen|{nxt},path+[r])
        visit(ec,{ec},[]);yields[ec]=len(exits)
    return live,yields

class Game:
    def __init__(self,seed,corner=False):
        self.seed=seed;self.board=new_board();self.resistance=2;self.resources=0;self.zipper=0
        self.campaign=1;self.event=0;self.draw=0;self.regular_seen=0;self.first='B';self.chosen={}
        self.sabotage={r:0 for r in EDGES};self.cap={};self.lost_cache=0;self.lost_k=0;self.track_cache=2
        self.away_troops=0;self.away_f=0;self.removed_intel=set();self.secret={};self.preview=False
        self.card=None;self.age=0;self.bot_discard=[];self.bot_queue=[];self.corner=corner
        self.deck=[];self.deck_pos=0;self.ended=False;self.winner=None;self.log=[];self.decisions=[];self.metrics={}
        self.last_placements=0;self.uncertain=False;self.roll_counts={};self.policy='adaptive';self.variant='baseline'
        b=self.board
        for s in ('Perak','Johore','Kuala Lumpur','Northern EC','Southern EC'):b[s]['troops']=3
        for s in ('Perak','Johore','Kuala Lumpur'):b[s]['police']=1;b[s]['kempeitai']=1
        b['Kedah']['blue_u']=1;b['Kelantan']['blue_u']=1
        for s,n in [('Perak',2),('Pahang',1),('Negri Sembilan',1),('Johore',2)]:b[s]['red_u']=n
        for s in ('Perak','Negri Sembilan'):b[s]['force136']=1
        for s in ('Perak','Negri Sembilan','Johore'):b[s]['camp']=True
        b['Perak']['cache']=True;b['Perak']['opposition']=True;b['Johore']['opposition']=True
        self.reset_intel(0)
        events=list(range(1,33));rng=random.Random(stable(seed,'event-deck'));rng.shuffle(events)
        for p in range(3):
            pile=events[p*6:p*6+6];bottom=pile[-2:]+[33+p];rng.shuffle(bottom);self.deck+=pile[:4]+bottom
        self.new_bot_deck();self.invariants()
    def clone(self):
        other=Game.__new__(Game)
        other.__dict__={k:deepcopy(v) for k,v in self.__dict__.items() if k not in ['log','secret','metrics','decisions']}
        other.preview=True;other.secret={};other.log=[];other.metrics={};other.decisions=[];other.uncertain=False;return other
    def inc(self,k,n=1):
        if not self.preview:self.metrics[k]=self.metrics.get(k,0)+n
    def count(self,f):return sum(int(v[f]) for v in self.board.values())
    def available(self,kind):
        totals={'red':10,'blue':4,'police':6,'troops':15,'cache':5-self.lost_cache,'camp':4,'force136':3}
        if kind in ('red','blue'):return totals[kind]-sum(v[kind+'_u']+v[kind+'_a'] for v in self.board.values())
        return totals[kind]-self.count(kind)-(self.track_cache if kind=='cache' else self.away_troops if kind=='troops' else self.away_f if kind=='force136' else 0)
    def reset_intel(self,round):
        values=[0,0,0,1,1,1,2,2,2];random.Random(stable(self.seed,'intel',round)).shuffle(values)
        self.secret=dict(zip(ORDER[:9],values));self.removed_intel=set()
        for v in self.board.values():v['intel']=None
    def die(self,tag,space=''):
        if self.preview:
            self.uncertain=True
            return 1 if tag=='Ambush' and getattr(self,'bot_forecast',False) else 4
        key=(self.draw,tag,space);n=self.roll_counts.get(key,0);self.roll_counts[key]=n+1
        return random.Random(stable(self.seed,'die',*key,n)).randint(1,6)
    def rail_adj(self,r):
        v=set(RA[r])
        if self.corner:
            if r=='Thailand-Kedah *':v.add('Perak')
            if r=='Thailand-Perak':v.update(['Kedah','Kelantan'])
            if r=='Thailand-Kelantan *':v.add('Perak')
        return v
    def cleanup(self):
        for v in self.board.values():
            if v['new_village'] and (gs(v) or v['cache']) and not cubes(v):v['new_village']=False
    def invariants(self):
        self.cleanup()
        assert self.count('troops')+self.away_troops==15
        assert self.count('kempeitai')+self.lost_k==3
        assert 0<=self.resistance<=20 and 0<=self.resources<=20
        assert self.zipper in [0,6,12,18,20]
        for k in ['red','blue','police','cache','camp','force136']:assert self.available(k)>=0,(k,self.available(k))
        assert self.track_cache==sum(t>self.zipper for t in [6,18])
        for s,v in self.board.items():
            assert all(v[k]>=0 for k in ['troops','police','red_u','red_a','blue_u','blue_a','force136','kempeitai','terror'])
            if s not in PROV:assert not v['camp'] and not v['new_village']
            if not POP[s]:assert not v['cache'] and not v['opposition'] and v['intel'] is None
    def record(self,kind,detail):
        if self.preview:return
        self.invariants();self.log.append(dict(draw=self.draw,campaign=self.campaign,event=self.event,
             kind=kind,detail=detail,resistance=self.resistance,resources=self.resources,zipper=self.zipper,
             board=deepcopy(self.board),sabotage=deepcopy(self.sabotage),cap=deepcopy(self.cap),
             available={k:self.available(k) for k in ['red','blue','cache','camp','force136','police']},
             bot_card=self.card['id'] if self.card else None,bot_age=self.age,first=self.first))
    def add_camp(self,s):
        assert s in PROV
        if self.board[s]['camp']:return
        if self.available('camp')==0:
            src=min((x for x in PROV if self.board[x]['camp']),key=lambda x:(bool(self.board[x]['force136']),not self.board[x]['cache'],POP[x],-ix(x)))
            self.board[src]['camp']=False
        self.board[s]['camp']=True
    def move_zipper(self,steps=None,target=None):
        levels=[0,6,12,18,20];old=levels.index(self.zipper)
        new=max(0,min(4,old+steps)) if target is None else levels.index(target)
        newtrack=sum(t>levels[new] for t in [6,18]);difference=newtrack-self.track_cache
        # Return from Available first; count adjustment itself consumes these.
        if difference>self.available('cache'):
            for _ in range(difference-self.available('cache')):
                src=min((s for s in ORDER if self.board[s]['cache']),key=lambda s:(gs(self.board[s]),-self.board[s]['troops'],-ix(s)))
                self.board[src]['cache']=False
        self.zipper=levels[new];self.track_cache=newtrack
    def lose_guerrilla(self,s,british=True,forced_color=None,active_only=False):
        v=self.board[s];fields=[k for k in ['red_a','blue_a','red_u','blue_u'] if v[k] and (not forced_color or k.startswith(forced_color)) and (not active_only or k.endswith('_a'))]
        if not fields:return None
        if british:
            def rank(k):
                color=k.split('_')[0];own=red(v) if color=='red' else blue(v);other=blue(v) if color=='red' else red(v)
                return (not k.endswith('_a'),not(own<other and other>0),color!='blue')
        else:
            # Keep a minority of the other color for compulsory future clashes.
            def rank(k):return (not k.endswith('_a'),-(red(v) if k.startswith('red') else blue(v)),not k.startswith('red'))
        chosen=min(fields,key=rank);v[chosen]-=1;return chosen
    def activate(self,s,color=None):
        for c in ([color] if color else ['red','blue']):
            if self.board[s][c+'_u']:
                self.board[s][c+'_u']-=1;self.board[s][c+'_a']+=1;return c
        raise ValueError(('No underground actor',s,color))
    def donor_ok(self,s,n=1):
        v=self.board[s];left=gs(v)-n
        return left>=0 and not(v['cache'] and left<1) and not(gs(v)>cubes(v) and left<=cubes(v))
    def placement_rank(self,s):
        v=self.board[s];g=gs(v);c=cubes(v)
        return (not(v['force136'] and not g),not(v['cache'] and not g),not(g<=c<g+1),not v['force136'],not v['cache'],c,-POP[s],ix(s))
    def opp_rank(self,s):
        v=self.board[s]
        return (bool(self.cap.get(15)=='S' and v['new_village']),-POP[s],bool(v['terror']),ix(s))
    def place_g(self,s,color,relocate=True,mandatory=False,train=False,used=None,reserve_cache_donors=False):
        v=self.board[s];other='blue' if color=='red' else 'red'
        if not mandatory and v[other+'_u']+v[other+'_a']:return False
        if used is None:used={}
        def placed():used[(s,color)]=used.get((s,color),0)+1
        if self.available(color)>0:v[color+'_u']+=1;placed();return True
        if not relocate:return False
        if train and v[color+'_a']:
            v[color+'_a']-=1;v[color+'_u']+=1;placed();return True
        donors=[x for x in ORDER if x!=s and (self.board[x][color+'_a'] or self.board[x][color+'_u']>used.get((x,color),0))
                and self.donor_ok(x) and (not train or not self.board[x]['force136']) and (not reserve_cache_donors or not self.board[x]['cache'])]
        if not donors:return False
        src=min(donors,key=lambda x:(not bool(self.board[x][color+'_a']),-cubes(self.board[x]),-ix(x)))
        field=color+('_a' if self.board[src][color+'_a'] else '_u')
        self.board[src][field]-=1;v[color+'_u']+=1;placed();return True
    def train(self,locations=None,reserve_cache_donors=False):
        sites=[s for s in ORDER if POP[s] and self.board[s]['force136']] if locations is None else locations
        used={};n=0
        for s in sites:
            v=self.board[s];assert POP[s] and v['force136']
            for _ in range(2 if v['cache'] else 1):
                r=red(v);b=blue(v);color='red' if r>=b and r else 'blue' if b else 'red' if v['camp'] or v['cache'] else 'blue'
                if color=='red' and not(v['camp'] or v['cache']):break
                placed=self.place_g(s,color,train=True,used=used,mandatory=bool(r and b),reserve_cache_donors=reserve_cache_donors)
                if not placed and not(r or b):
                    other='blue' if color=='red' else 'red'
                    if other=='blue' or v['camp'] or v['cache']:placed=self.place_g(s,other,train=True,used=used,reserve_cache_donors=reserve_cache_donors)
                if placed:n+=1
                else:break
        self.cleanup();return n
    def gather_targets(self,anchor,allow_adj=True):
        return [s for s in ORDER if (s==anchor or allow_adj and s in ADJ[anchor]) and POP[s]
                and s not in self.removed_intel and self.board[s]['intel'] is None and ug(self.board[s])]
    def gather(self):
        selected=[];revealed=[]
        for n in range(3 if self.cap.get(19)=='U' else 2):
            anchors=[s for s in ORDER if self.board[s]['force136'] and s not in selected]
            def targets(s):return self.gather_targets(s,self.cap.get(19)!='S' or n==0)
            anchors=[s for s in anchors if targets(s)]
            if not anchors:break
            a=min(anchors,key=lambda s:(-len(targets(s)),s not in targets(s),bool(self.board[s]['kempeitai']),ix(s)))
            selected.append(a)
            for s in targets(a):
                if self.cap.get(22)!='U':self.activate(s)
                self.board[s]['intel']=1 if self.preview else self.secret[s];revealed.append(s)
                if self.preview:self.uncertain=True
        self.inc('gather_reveals',len(revealed));return revealed
    def supply(self):
        n=0;selected=[];remote=False
        for _ in range(3 if self.zipper>=12 else 2):
            if not self.available('cache'):break
            sites=[s for s in PROV if self.board[s]['camp'] and not self.board[s]['cache'] and s not in selected
                   and (self.board[s]['force136'] or self.cap.get(8)=='U' and not remote)]
            if not sites:break
            s=min(sites,key=lambda s:(bool(self.board[s]['kempeitai']),-gs(self.board[s]),-POP[s],ix(s)))
            selected.append(s)
            if not self.board[s]['force136']:remote=True
            if self.cap.get(8)=='S' and self.die('Supply',s)<=2:continue
            self.board[s]['camp']=False;self.board[s]['cache']=True;n+=1
            if not gs(self.board[s]):self.inc('unguarded_cache_placements')
        if self.cap.get(27)=='S':
            eligible=[s for s in selected if self.board[s]['opposition']]
            if eligible:self.board[max(eligible,key=self.opp_rank)]['opposition']=False
        self.inc('caches_built',n);return n
    def rail_choice(self,s,region='C',stack=False,eligible=None):
        candidates=[r for r in EDGES if s in self.rail_adj(r) and (stack or not self.sabotage[r]) and (eligible is None or r in eligible)]
        if not candidates:return None
        live,_=live_and_yield(self.sabotage);order=DATA['rail_orders'][region]
        return min(candidates,key=lambda r:(bool(self.sabotage[r]),self.sabotage[r] if stack else 0,r not in live,order.index(r)))
    def rail(self,region='C',locations=None,color=None,extra=True):
        if locations is None:
            sites=[s for s in ORDER if self.board[s]['force136']]
            if extra and self.cap.get(27)=='U':
                remote=[s for s in ORDER if not self.board[s]['force136'] and ug(self.board[s]) and self.rail_choice(s,region)]
                if remote:
                    order=DATA['rail_orders'][region];sites.append(min(remote,key=lambda s:(order.index(self.rail_choice(s,region)),ix(s))))
        else:sites=locations
        hit=[]
        for s in sites:
            if not (self.board[s][color+'_u'] if color else ug(self.board[s])):continue
            r=self.rail_choice(s,region)
            if r:
                self.activate(s,color);self.sabotage[r]+=1;hit.append(r)
        self.inc('sabotages',len(hit));return hit
    def cache_bonus(self,s):return sum(self.board[x]['cache'] for x in ORDER if x==s or x in ADJ[s])
    def strike_option(self,s,force_color=None,bose=False):
        v=self.board[s]
        if not (v[force_color+'_u'] if force_color else ug(v)):return None
        bonus=self.cache_bonus(s);faces=sum(d+bonus>cubes(v) for d in range(1,7))
        if bose:return ('Bose',faces) if v['troops'] and faces>=3 else None
        if v['kempeitai'] and faces>=3 and s!='Kuala Lumpur':return ('Kempeitai',faces)
        if v['police']:return ('Police',6)
        if v['troops'] and faces>=3 and s!='Kuala Lumpur':return ('Troop',faces)
        return None
    def strike_rank(self,s,color=None,bose=False):
        opt=self.strike_option(s,color,bose);v=self.board[s]
        category=0 if opt[0]=='Kempeitai' else 1 if opt[0]=='Police' and v['police']==1 else 2 if opt[0]=='Police' else 3
        return (category,-opt[1],-self.cache_bonus(s),ix(s))
    def strike(self,locations=None,color=None,bose=False,extra=True):
        if locations is None:
            sites=[s for s in ORDER if self.board[s]['force136'] and self.strike_option(s,color,bose)]
            if extra and self.cap.get(27)=='U' and not bose:
                rem=[s for s in ORDER if not self.board[s]['force136'] and self.strike_option(s,color)]
                if rem:sites.append(min(rem,key=lambda s:self.strike_rank(s,color)))
        else:sites=[s for s in locations if self.strike_option(s,color,bose)]
        sites=sorted(sites,key=lambda s:self.strike_rank(s,color,bose))
        hits=[]
        for s in sites:
            opt=self.strike_option(s,color,bose)
            if not opt:continue
            self.activate(s,color);kind,faces=opt;hits.append((s,kind))
            if kind=='Police':self.board[s]['police']-=1
            elif self.die('Ambush',s)+self.cache_bonus(s)>cubes(self.board[s]):
                if bose:self.resistance=clamp(self.resistance+2)
                else:
                    field='kempeitai' if kind=='Kempeitai' else 'troops';self.board[s][field]-=1;self.board['Kuala Lumpur'][field]+=1
                    self.resistance=clamp(self.resistance+1)
        self.inc('ambush_attempts',len(hits));return hits
    def primary_site_value(self,s,task):
        v=self.board[s]
        if task=='SUPPLY':return int(s in PROV and not v['cache'] and self.available('cache')>0)
        if task=='INTEL':return len(self.gather_targets(s))
        if task=='RAIL':return int(ug(v)>0 and self.rail_choice(s,self.region()) is not None)
        if task=='STRIKE':return int(self.strike_option(s) is not None)
        if task=='TRAIN':return 2 if v['cache'] else 1 if v['camp'] else 0
        if task=='RAID':return int(v['cache'] and gs(v)>1)
        return 0
    def region(self):return self.card['rail_order'] if self.card else 'C'
    def contact(self,task=None,hold=False):
        task=task or (self.card['primary'] if self.card else 'SUPPLY' if self.available('cache') else 'INTEL')
        if hold:return []
        if task=='INTEL' and any(self.gather_targets(s) for s in ORDER if self.board[s]['force136']):return []
        b=self.board
        def dr(s):return (bool(b[s]['kempeitai']),-self.primary_site_value(s,task),-gs(b[s]),-POP[s],ix(s))
        dests=[s for s in PROV if not b[s]['force136']]
        move=None
        if self.available('force136') and dests:
            s=min(dests,key=dr);b[s]['force136']+=1;move=('Available',s)
        elif not self.available('force136'):
            candidates=[]
            for src in ORDER:
                v=b[src]
                if not v['force136']:continue
                exposed=v['kempeitai'] and (not v['camp'] or self.cap.get(22)=='S')
                for dst in ADJ[src]:
                    if b[dst]['force136']:continue
                    # Preview a permitted blue escort for the primary's value.
                    ghost=self.clone();ghost.board[src]['force136']-=1;ghost.board[dst]['force136']+=1
                    if dst in PROV:ghost.board[dst]['camp']=True
                    if not red(ghost.board[dst]) and blue(v) and self.donor_ok(src):
                        field='blue_u' if v['blue_u'] else 'blue_a';ghost.board[src][field]-=1;ghost.board[dst][field]+=1
                    opens=(dst in PROV and not b[dst]['cache'] and self.available('cache'))
                    enables=ghost.primary_site_value(dst,task)>0
                    if exposed or enables or opens:
                        sr=(not bool(exposed),bool(self.primary_site_value(src,task)),bool(v['cache']),gs(v),-ix(src))
                        d=(bool(b[dst]['kempeitai']),-ghost.primary_site_value(dst,task),-gs(ghost.board[dst]),-POP[dst],ix(dst))
                        candidates.append((sr,d,src,dst))
            if candidates:
                _,_,src,dst=min(candidates);b[src]['force136']-=1;b[dst]['force136']+=1;move=(src,dst)
                if blue(b[src]) and not red(b[dst]) and self.donor_ok(src):
                    field='blue_u' if b[src]['blue_u'] else 'blue_a';b[src][field]-=1;b[dst][field]+=1
        if move and move[1] in PROV:self.add_camp(move[1])
        self.cleanup();return [move] if move else []
    def raid(self):
        destinations=[];used={};attacks=0
        for _ in range(3 if self.zipper==20 else 2):
            options=[]
            for dst in ORDER:
                if dst in destinations:continue
                for src in sorted(ADJ[dst],key=ix):
                    v=self.board[src];w=self.board[dst]
                    if not v['cache']:continue
                    for color in ['red','blue']:
                        other='blue' if color=='red' else 'red'
                        if w[other+'_u']+w[other+'_a']:continue
                        have=v[color+'_u']+v[color+'_a']-used.get((src,color+'_u'),0)-used.get((src,color+'_a'),0)
                        if not have:continue
                        if v[color+'_u']>used.get((src,color+'_u'),0) and self.donor_ok(src):
                            probe=self.clone();probe.board[dst][color+'_u']+=1
                            rail=probe.rail_choice(dst,self.region());strike=probe.strike_option(dst)
                            if rail:
                                live,_=live_and_yield(self.sabotage)
                                key=(0 if rail in live else 1,DATA['rail_orders'][self.region()].index(rail),ix(dst))
                                options.append((key,(-gs(v)+1,ix(src)),color!='red',src,dst,color,1,'RAIL'))
                            elif strike:
                                options.append(((2,*probe.strike_rank(dst)),(-gs(v)+1,ix(src)),color!='red',src,dst,color,1,'STRIKE'))
                        need=cubes(w)-gs(w)+1
                        if 1<=need<=2 and have>=need and self.donor_ok(src,need):
                            options.append(((3,ix(dst)),(-gs(v)+need,ix(src)),color!='red',src,dst,color,need,None))
            if not options:break
            _,_,_,src,dst,color,n,attack=min(options);v=self.board[src];w=self.board[dst]
            active_to_send=0;underground_to_send=0
            for i in range(n):
                field=color+'_u' if v[color+'_u']>used.get((src,color+'_u'),0) else color+'_a'
                if attack and i==0:assert field.endswith('_u')
                v[field]-=1;w[field]+=1;used[(dst,field)]=used.get((dst,field),0)+1
                if field.endswith('_u'):underground_to_send+=1
                else:active_to_send+=1
            destinations.append(dst)
            if attack=='RAIL':
                self.rail(self.region(),[dst],color,extra=False);attacks+=1
                used[(dst,color+'_u')]-=1;used[(dst,color+'_a')]=used.get((dst,color+'_a'),0)+1
            elif attack=='STRIKE':
                self.strike([dst],color,extra=False);attacks+=1
                used[(dst,color+'_u')]-=1;used[(dst,color+'_a')]=used.get((dst,color+'_a'),0)+1
            self.cleanup()
        self.inc('raid_destinations',len(destinations));return destinations
    def reveal_any(self,n):
        sites=[s for s in ORDER if POP[s] and s not in self.removed_intel and self.board[s]['intel'] is None]
        sites.sort(key=lambda s:(bool(self.board[s]['kempeitai']),ix(s)))
        for s in sites[:n]:self.board[s]['intel']=1 if self.preview else self.secret[s]
        if self.preview and sites[:n]:self.uncertain=True
        return sites[:n]
    def conceal_any(self,n):
        sites=[s for s in ORDER if self.board[s]['intel'] is not None]
        sites.sort(key=lambda s:(-self.board[s]['intel'],ix(s)))
        for s in sites[:n]:self.board[s]['intel']=None
    def event_placements(self,sites,color,n=None,each=False,mandatory=False,prefer_existing=False):
        used={};changed=0
        if each:
            for s in sorted(sites,key=self.placement_rank):
                if self.place_g(s,color,used=used,mandatory=mandatory):changed+=1
            self.last_placements+=changed
            return changed
        for _ in range(n):
            candidates=[]
            for s in sites:
                probe=self.clone()
                if probe.place_g(s,color,used=dict(used)):candidates.append(s)
            if not candidates:break
            s=min(candidates,key=lambda s:(not bool(blue(self.board[s])) if prefer_existing else False,self.placement_rank(s)))
            if self.place_g(s,color,used=used):changed+=1
        self.last_placements+=changed
        return changed
    def execute_event(self,j,side='U'):
        if j in CAPS:self.cap[j]=side;return
        self.last_placements=0
        b=self.board;S=side=='S';r=self.region()
        if j==1:
            if not S:self.resistance=clamp(self.resistance+min(3,sum(v['terror'] for v in b.values())))
            else:self.reprisal([s for s in ORDER if b[s]['troops'] and b[s]['opposition']],limit=11)
        elif j==2:
            eligible=[x for x in EDGES if any((not b[s]['opposition'] if S else b[s]['opposition']) for s in self.rail_adj(x) if POP[s])]
            if S:
                for x in self.best_repairs(eligible,2,all_markers=True):self.sabotage[x]=0
            else:
                order=DATA['rail_orders'][r]
                for _ in range(min(3,len(eligible))):
                    live,_=live_and_yield(self.sabotage)
                    x=min(eligible,key=lambda x:(bool(self.sabotage[x]),self.sabotage[x],x not in live,order.index(x)))
                    self.sabotage[x]+=1;eligible.remove(x)
        elif j==3:
            if S:self.resources=clamp(self.resources+sum(POP[s] for s in ORDER if not b[s]['opposition'])//2)
            else:
                sites=[s for s in ORDER if b[s]['force136']]
                self.event_placements(sites,'red',2);self.event_placements(sites,'blue',1)
        elif j==4:
            if S:
                for v in b.values():
                    if v['force136']:v['camp']=False
            else:self.resistance=clamp(self.resistance+sum(bool(v['force136'] and v['camp']) for v in b.values()))
        elif j==5:
            if S:
                sites=[s for s in ORDER if b[s]['opposition'] and b[s]['red_a']+b[s]['blue_a']]
                if sites:b[max(sites,key=lambda s:(POP[s],-ix(s)))]['opposition']=False
            else:
                for v in b.values():
                    for c in ['red','blue']:v[c+'_u']+=v[c+'_a'];v[c+'_a']=0
        elif j==7:
            self.move_zipper(-2 if S else 1)
            if not S:self.gather()
        elif j==10:
            if S:self.resources=clamp(self.resources+2*self.count('new_village'))
            else:self.resources-=self.resources//2
        elif j in [11,13]:
            if S and j==11:
                for s in ORDER:
                    if red(b[s]) and blue(b[s]):self.lose_guerrilla(s,False,'red');b[s]['opposition']=False
            elif S:self.eliminate([s for s in ORDER if b[s]['kempeitai']],limit=11)
            else:
                sites=[s for s in ORDER if (s in NORTH if j==11 else b[s]['red_u']>0)]
                color='red' if j==13 else None
                for _ in range(3 if j==11 else 2):
                    rails=[s for s in sites if (b[s]['red_u'] if color else ug(b[s])) and self.rail_choice(s,r)]
                    strikes=[s for s in sites if self.strike_option(s,color)]
                    if rails:
                        s=min(rails,key=lambda s:(DATA['rail_orders'][r].index(self.rail_choice(s,r)),ix(s)));self.rail(r,[s],color,False)
                    elif strikes:s=min(strikes,key=lambda s:self.strike_rank(s,color));self.strike([s],color,extra=False)
                    else:break
                    if j==11:sites.remove(s)
        elif j==14:
            if S:
                sites=[s for s in ORDER if b[s]['cache']]
                if sites:
                    s=max(sites,key=lambda s:(bool(b[s]['force136']),gs(b[s]),-ix(s)));b[s]['cache']=False;self.lost_cache+=1
            else:self.event_placements([s for s in ORDER if b[s]['cache']],'red',each=True,mandatory=True)
        elif j==16:
            if S:
                sites=[s for s in PROV if b[s]['force136'] and b[s]['camp']]
                if sites:b[max(sites,key=lambda s:(bool(b[s]['kempeitai']),-gs(b[s]),-ix(s)))]['camp']=False
                self.conceal_any(1)
            else:
                selected=set()
                for _ in range(2):
                    dests=[s for s in PROV if b[s]['camp'] and not b[s]['force136'] and s not in selected]
                    if not dests:break
                    dst=min(dests,key=lambda s:(bool(b[s]['kempeitai']),not(not b[s]['cache'] and self.available('cache')),-gs(b[s]),ix(s)))
                    if self.available('force136'):b[dst]['force136']+=1
                    else:
                        sources=[s for s in ORDER if b[s]['force136'] and s not in selected and s!=dst]
                        if not sources:break
                        src=min(sources,key=lambda s:(not bool(b[s]['kempeitai'] and (not b[s]['camp'] or self.cap.get(22)=='S')),gs(b[s]),-ix(s)))
                        b[src]['force136']-=1;b[dst]['force136']+=1
                    selected.add(dst)
        elif j==17:
            self.move_zipper(-1)
            for _ in range(3):
                s=max((s for s in ORDER if b[s]['troops']),key=lambda s:(s=='Kuala Lumpur',not bool(gs(b[s]) or b[s]['force136']),b[s]['troops'],-ix(s)))
                b[s]['troops']-=1;self.away_troops+=1
        elif j==18:
            if S:
                for s in sorted(NORTH,key=ix):
                    self.lose_guerrilla(s,False);b['Kuala Lumpur']['troops']+=b[s]['troops'];b[s]['troops']=0
            else:self.event_placements(sorted(NORTH,key=ix),'blue',3,prefer_existing=True)
        elif j==20:
            sites=[s for s in ORDER if b[s]['force136']]
            if sites:
                s=min(sites,key=lambda s:(bool(self.primary_site_value(s,self.card['primary'] if self.card else 'INTEL')),not bool(b[s]['kempeitai']),gs(b[s]),-ix(s)))
                b[s]['force136']-=1
            if S:
                hidden=[s for s in ORDER[:9] if b[s]['intel'] is None and s not in self.removed_intel]
                if hidden:
                    # Japan cannot inspect the selected chit; public tie uses map order.
                    s=hidden[0];value=1 if self.preview else self.secret[s]
                    self.resistance=clamp(self.resistance-value);self.removed_intel.add(s)
                    if self.preview:self.uncertain=True
            else:self.reveal_any(2)
        elif j==21:
            if S:
                sites=sorted(PROV,key=lambda s:(bool(b[s]['police']),not bool(b[s]['kempeitai']),not bool(b[s]['force136']),ix(s)))[:3]
                for s in sites:
                    if self.available('police'):b[s]['police']+=1
                self.eliminate([s for s in PROV if b[s]['police'] and b[s]['kempeitai']],limit=1)
            else:self.event_placements(ORDER,'blue',4)
        elif j==23:
            if S:
                sites=[s for s in PROV if b[s]['opposition'] and any(self.sabotage[x] and s in self.rail_adj(x) for x in EDGES)]
                for s in sorted(sites,key=lambda s:(-POP[s],ix(s)))[:2]:b[s]['opposition']=False
            else:
                eligible=list(EDGES);order=DATA['rail_orders'][r]
                for _ in range(2):
                    live,_=live_and_yield(self.sabotage)
                    x=min(eligible,key=lambda x:(bool(self.sabotage[x]),self.sabotage[x],x not in live,order.index(x)));self.sabotage[x]+=1;eligible.remove(x)
        elif j==24:
            if S:self.resistance=clamp(self.resistance-sum(bool(v['force136'] and v['camp']) for v in b.values()))
            else:self.move_zipper(1);self.supply()
        elif j==25:
            if S:
                sites=[s for s in ORDER if b[s]['force136']]
                if sites:
                    s=max(sites,key=lambda s:(len(self.gather_targets(s)),bool(b[s]['cache']),gs(b[s]),-ix(s)))
                    b[s]['force136']-=1;self.away_f+=1
            else:
                selected=False
                for task in ['SUPPLY','INTEL','RAID']:
                    probe=self.clone();probe.contact(task)
                    sa={'SUPPLY':'SUPPLY','INTEL':'GATHER','RAID':'RAID'}[task]
                    if probe.special(sa):self.contact(task);self.special(sa);selected=True;break
                if not selected:self.contact()
        elif j==26:
            if S:self.sweep_plan(limit=2,police_move=True)
            else:
                sites=[s for s in ORDER if b[s]['force136'] and self.strike_option(s,bose=True)]
                if sites:self.strike([min(sites,key=lambda s:(-self.strike_option(s,bose=True)[1],-self.cache_bonus(s),ix(s)))],bose=True)
        elif j==28:
            if S:
                sites=[s for s in PROV if (b[s]['force136'] or b[s]['cache']) and any(b[x]['troops'] for x in {s}|ADJ[s])]
                if sites:
                    s=max(sites,key=lambda s:(bool(b[s]['force136']),bool(b[s]['cache']),-gs(b[s]),-ix(s)))
                    if b[s]['force136']:b[s]['force136']-=1
                    else:b[s]['cache']=False
            else:
                sites=[s for s in PROV if b[s]['camp'] and (self.available('force136') or self.available('cache') and not b[s]['cache'])]
                if sites:
                    s=min(sites,key=lambda s:(bool(b[s]['kempeitai']),bool(b[s]['force136']),-gs(b[s]),ix(s)))
                    if self.available('force136'):b[s]['force136']+=1
                    if self.available('cache') and not b[s]['cache']:b[s]['cache']=True
        elif j==29:
            if S:self.reposition_k(anywhere=True);self.conceal_any(2)
            else:
                sites=[s for s in ORDER if b[s]['kempeitai']]
                if sites:
                    s=min(sites,key=lambda s:(not bool(b[s]['force136']),not bool(b[s]['intel'] and b[s]['intel']>0),-b[s]['police'],ix(s)))
                    b[s]['kempeitai']-=1;self.lost_k+=1
        elif j==30:
            if S:
                for s in ORDER:
                    if b[s]['troops'] and self.available('police'):b[s]['police']+=1
            else:
                sites=[s for s in ORDER if b[s]['police'] and gs(b[s]) and b[s]['opposition']]
                for s in sorted(sites,key=lambda s:(b[s]['police']!=1,ix(s)))[:3]:b[s]['police']-=1
        elif j==31:
            amount=sum(bool(v['troops']) and (S or v['opposition']) for v in b.values())
            self.resources=clamp(self.resources+amount if S else self.resources-amount)
        elif j==32:
            if S:
                sites=[s for s in PROV if any(self.sabotage[x] and s in self.rail_adj(x) for x in EDGES)]
                if sites:
                    s=max(sites,key=lambda s:(bool(b[s]['cache']),bool(b[s]['force136']),POP[s]*b[s]['opposition'],gs(b[s]),-ix(s)))
                    self.sweep_plan(limit=1,targets=[s]);self.reprisal([s],limit=1)
            else:self.event_placements([s for s in PROV if b[s]['camp'] and b[s]['opposition']],'red',each=True)
        else:raise ValueError(('Unhandled Event',j,side))
        self.cleanup()
    def reposition_k(self,anywhere=False):
        sites=[s for s in ORDER if anywhere or cubes(self.board[s])]
        if not sites:return
        total=self.count('kempeitai')
        for v in self.board.values():v['kempeitai']=0
        ranked=sorted(sites,key=lambda s:(not bool(self.board[s]['force136']),bool(self.board[s]['camp']) and self.cap.get(22)!='S',
                     gs(self.board[s])-self.board[s]['police'],-(self.board[s]['intel'] or 0),ix(s)))
        for i in range(total):self.board[ranked[i%len(ranked)]]['kempeitai']+=1
    def best_repairs(self,eligible,n,all_markers=False):
        work=self.clone();selected=[]
        for _ in range(n):
            candidates=[r for r in eligible if work.sabotage[r] and r not in selected]
            if not candidates:break
            base=sum(live_and_yield(work.sabotage)[1].values())
            def value(r):
                after=dict(work.sabotage);after[r]=0 if all_markers else after[r]-1
                gain=sum(live_and_yield(after)[1].values())-base
                return (-gain,after[r]!=0,DATA['rail_orders']['C'].index(r))
            r=min(candidates,key=value);selected.append(r);work.sabotage[r]=0 if all_markers else work.sabotage[r]-1
        return selected
    def repair(self,r,construct=False):
        assert self.sabotage[r]>0
        self.sabotage[r]-=1
        if construct and self.cap.get(12)=='U':
            sites=[s for s in self.rail_adj(r) if POP[s] and not self.board[s]['opposition']]
            if sites:self.board[min(sites,key=self.opp_rank)]['opposition']=True
    def construct(self,limit=3):
        selected=[]
        for _ in range(limit):
            options=[];before=sum(live_and_yield(self.sabotage)[1].values())
            for s in PROV:
                v=self.board[s]
                if s in selected or cubes(v)<=gs(v):continue
                rails=[r for r in EDGES if self.sabotage[r] and s in self.rail_adj(r)]
                for r in rails:
                    after=dict(self.sabotage);after[r]-=1
                    gain=sum(live_and_yield(after)[1].values())-before
                    options.append(((-gain,-self.sabotage[r],0,ix(s),r),s,r))
                if not v['new_village'] and self.count('new_village')<4 and any(x.endswith('EC') for x in ADJ[s]):
                    # Village creates Opposition, so no indiscriminate building.
                    priority=-1.1 if self.policy=='extraction' and v['opposition'] else -.25 if v['opposition'] else .4
                    options.append(((priority,0,1,ix(s),''),s,None))
            if not options:break
            _,s,r=min(options);selected.append(s)
            if r:self.repair(r,True)
            else:self.board[s]['new_village']=True;self.board[s]['opposition']=True
        self.cleanup();return selected
    def deploy(self,limit=3):
        sites=[s for s in ORDER if s=='Kuala Lumpur' or s in PROV and self.board[s]['troops'] and not self.board[s]['opposition']]
        ranked=sorted(sites,key=lambda s:(bool(self.board[s]['police']),not bool(self.board[s]['force136']),
                     not bool(self.board[s]['kempeitai']),ix(s)))
        changed=0
        for s in ranked[:limit]:
            if self.available('police'):self.board[s]['police']+=1;changed+=1
            else:
                donors=[x for x in ORDER if x!=s and self.board[x]['police']>1]
                if donors and not self.board[s]['police']:
                    src=max(donors,key=lambda x:(self.board[x]['police'],-ix(x)));self.board[src]['police']-=1;self.board[s]['police']+=1;changed+=1
        before=[self.board[s]['kempeitai'] for s in ORDER];self.reposition_k()
        return changed+int(before!=[self.board[s]['kempeitai'] for s in ORDER])
    def extract(self):
        if self.cap.get(12)=='S':
            rails=[r for r in EDGES if self.sabotage[r] and any(self.board[s]['troops'] for s in self.rail_adj(r))]
            best=self.best_repairs(rails,1)
            if best:self.repair(best[0])
        _,yields=live_and_yield(self.sabotage);gain=sum(yields.values())+self.count('new_village')
        old=self.resources;self.resources=clamp(self.resources+gain)
        if self.cap.get(15)=='U':
            used={}
            for s in sorted([s for s in PROV if self.board[s]['new_village']],key=self.placement_rank):
                c='blue' if blue(self.board[s]) and not red(self.board[s]) else 'red'
                self.place_g(s,c,used=used)
        return self.resources-old
    def reprisal(self,locations=None,limit=2):
        b=self.board;sites=[s for s in ORDER if b[s]['troops'] and (b[s]['opposition'] or gs(b[s]))] if locations is None else [s for s in locations if b[s]['troops']]
        sites=sorted(sites,key=lambda s:(not bool(b[s]['cache'] and gs(b[s])==1),-POP[s]*b[s]['opposition'],not bool(b[s]['force136']),ix(s)))[:limit]
        for s in sites:
            b[s]['terror']=max(1,b[s]['terror']);b[s]['opposition']=False
            fields=[k for k in ['red_u','blue_u','red_a','blue_a'] if b[s][k]]
            if not fields:continue
            options=[]
            for f in fields:
                color=f.split('_')[0];other='blue' if color=='red' else 'red'
                for dst in sorted(ADJ[s],key=ix):
                    v=b[dst]
                    key=(not bool(v[other+'_u']+v[other+'_a']),bool(v['force136'] or v['cache']),-cubes(v),not f.endswith('_u'),ix(dst),f)
                    options.append((key,f,dst))
            _,f,dst=min(options);b[s][f]-=1;b[dst][f]+=1
            if b[s]['cache'] and not gs(b[s]):self.inc('reprisal_unguarded_caches')
        self.cleanup();return sites
    def eliminate(self,locations=None,limit=2):
        b=self.board;sites=[s for s in ORDER if b[s]['kempeitai'] and (b[s]['camp'] or b[s]['force136'] or b[s]['intel'] is not None)] if locations is None else locations
        def key(s):
            v=b[s];removable=bool(v['force136'] and (not v['camp'] or self.cap.get(22)=='S'))
            chance=sum(d+v['police']>gs(v) for d in range(1,7))/6
            # Distinct purposeful policies differ in what they will suppress.
            w=4 if self.policy=='hunting' else 2.2
            expected=chance*(w if removable else 1.3 if v['camp'] else 0)
            return (-max(expected,(v['intel'] or 0)*1.0),ix(s))
        selected=[]
        for s in sorted(set(sites),key=key)[:limit]:
            v=b[s]
            if not v['kempeitai']:continue
            removable=v['force136'] and (not v['camp'] or self.cap.get(22)=='S')
            chance=sum(d+v['police']>gs(v) for d in range(1,7))/6
            marker_value=(4 if self.policy=='hunting' else 2.2) if removable else 1.3 if v['camp'] else 0
            if v['intel'] is not None and (v['intel']>=chance*marker_value or not(v['camp'] or v['force136'])):
                v['intel']=None;selected.append((s,'conceal'));continue
            if not(v['camp'] or v['force136']):continue
            selected.append((s,'roll'))
            if self.die('Eliminate',s)+v['police']>gs(v):
                if removable:
                    v['force136']-=1;self.resistance=clamp(self.resistance-1);self.inc('force136_eliminated')
                elif v['camp']:v['camp']=False
        return selected
    def assault(self,limit=3):
        b=self.board;sites=[s for s in ORDER if b[s]['troops'] and (b[s]['red_a']+b[s]['blue_a'] or b[s]['cache'] and not gs(b[s]))]
        sites.sort(key=lambda s:(not bool(b[s]['cache']),not bool(b[s]['force136']),-(b[s]['red_a']+b[s]['blue_a']),ix(s)))
        removed=0
        for s in sites[:limit]:
            v=b[s];n=v['troops']//2 if s in MOUNTAIN and not v['kempeitai'] else v['troops']
            for _ in range(n):
                if v['red_a']+v['blue_a']:self.lose_guerrilla(s,False,active_only=True);removed+=1
                elif v['cache'] and not gs(v):v['cache']=False;removed+=1;self.inc('caches_assaulted')
                else:break
        self.cleanup();return removed
    def sweep_plan(self,limit=3,targets=None,police_move=False,strength=3):
        b=self.board
        if targets is None:
            targets=[s for s in ORDER if ug(b[s]) or b[s]['force136'] or b[s]['cache']]
            targets.sort(key=lambda s:(not bool(b[s]['force136']) if self.policy=='hunting' else not bool(b[s]['cache']),
                           -ug(b[s]),not bool(b[s]['opposition']),ix(s)))
            targets=targets[:limit]
        selected=targets[:limit];left={s:b[s]['troops'] for s in ORDER};left_p={s:b[s]['police'] for s in ORDER};moves=[]
        for dst in selected:
            desired=max(1,min(7,gs(b[dst])+1)) if self.policy=='hunting' else max(2,min(6,2*ug(b[dst])))
            desired=min(desired,strength) if strength else desired
            need=max(0,desired-left[dst])
            sources=sorted(ADJ[dst],key=lambda s:(s in selected,not s.endswith('EC'),s!='Kuala Lumpur',-left[s],ix(s)))
            for src in sources:
                take=min(need,left[src]);left[src]-=take;need-=take
                if take:moves.append((src,dst,'troops',take))
                if police_move and need:
                    take=min(need,left_p[src]);left_p[src]-=take;need-=take
                    if take:moves.append((src,dst,'police',take))
        # Simultaneous transfer, no troop can be moved twice.
        for src,dst,f,n in moves:b[src][f]-=n;b[dst][f]+=n
        activated=0
        for s in selected:
            n=cubes(b[s])//2 if s in JUNGLE and not b[s]['kempeitai'] else cubes(b[s])
            for _ in range(min(n,ug(b[s]))):self.activate(s);activated+=1
        self.cleanup();return activated+sum(n for _,_,_,n in moves)
    def icon(self,j):
        b=self.board
        if j in MOBILIZE:
            sites=[s for s in PROV if b[s]['camp'] and not b[s]['terror'] and not b[s]['opposition']]
            if sites:b[min(sites,key=self.opp_rank)]['opposition']=True
        elif j in KILL:
            sites=[s for s in ORDER if red(b[s]) and b[s]['police']]
            if sites:
                s=min(sites,key=lambda s:(b[s]['police']!=1,not bool(b[s]['force136']),-(b[s]['intel'] or 0),ix(s)));b[s]['police']-=1
        elif j in SEIZE:
            sites=[s for s in ORDER[:9] if b[s]['cache'] and not b[s]['camp']]
            if sites:
                s=max(sites,key=lambda s:(bool(b[s]['force136']),gs(b[s]),-ix(s)));b[s]['cache']=False
                if s in PROV:self.add_camp(s)
        elif j in FOOD:
            sites=[s for s in ORDER if red(b[s]) and not b[s]['cache']]
            if sites:
                s=max(sites,key=lambda s:(bool(b[s]['force136'] and ug(b[s])==1),bool(gs(b[s])==1),bool(gs(b[s])==cubes(b[s])+1),-ix(s)))
                self.lose_guerrilla(s,False,'red')
        else:raise AssertionError(('Missing icon',j))
        self.cleanup()
    def mandatory(self,j):
        if j==6:
            for s in sorted(JUNGLE,key=ix):
                if self.die('Jungle',s)<=2:
                    v=self.board[s]
                    if gs(v):self.lose_guerrilla(s,True)
                    elif v['cache']:v['cache']=False
                    if v['police'] and v['troops']<=1:v['police']-=1
                    elif v['troops']:v['troops']-=1;self.board['Kuala Lumpur']['troops']+=1
                    elif v['police']:v['police']-=1
        if j==9 and self.campaign==3:self.propaganda(final=True)
        self.cleanup()
    def special(self,name):
        return {'SUPPLY':self.supply,'GATHER':self.gather,'RAID':self.raid}[name]()
    def operation(self,name,hold=False):
        return {'CONTACT':lambda:self.contact(hold=hold),'TRAIN':self.train,
                'RAIL':lambda:self.rail(self.region()),'STRIKE':self.strike}[name]()
    def new_bot_deck(self):
        cards=list(self.bot_discard) if self.bot_discard else list(DATA['cards'])
        random.Random(stable(self.seed,'bot-deck',getattr(self,'bot_cycles',0))).shuffle(cards)
        self.bot_cycles=getattr(self,'bot_cycles',0)+1;self.bot_queue=cards;self.bot_discard=[]
    def ensure_card(self):
        if not self.card:
            if not self.bot_queue:self.new_bot_deck()
            self.card=self.bot_queue.pop(0);self.age=0
    def sa_useful(self,sa):
        probe=self.clone();result=probe.special(sa);return bool(result)
    def task_plan(self,task,free):
        if task in ['SUPPLY','INTEL','RAID']:
            if 'Op & SA' not in free:return None
            probe=self.clone();sa={'SUPPLY':'SUPPLY','INTEL':'GATHER','RAID':'RAID'}[task]
            op='CONTACT';hold=False
            if task=='RAID':
                test=probe.clone()
                if test.train():op='TRAIN';probe.train()
                else:probe.contact(task)
            else:probe.contact(task)
            if not probe.special(sa):
                if task!='RAID':return None
                retry=self.clone();trained=retry.train(reserve_cache_donors=True)
                if trained and retry.raid():
                    return dict(task=task,op='TRAIN',box='Op & SA',sa=sa,hold=False,reserve_cache_donors=True)
                retry=self.clone();moved=retry.contact(task)
                if retry.raid():return dict(task=task,op='CONTACT',box='Op & SA',sa=sa,hold=False)
                retry=self.clone()
                if retry.raid():return dict(task=task,op='CONTACT',box='Op & SA',sa=sa,hold=True)
                return None
            return dict(task=task,op=op,box='Op & SA',sa=sa,hold=hold)
        probe=self.clone();probe.bot_forecast=True;effect=probe.operation(task)
        # Contact hold is useful when it provides a compatible Special Activity.
        sa=None
        if 'Op & SA' in free:
            for candidate in self.card['other_special'].split(' > '):
                if candidate in PAIR[task] and probe.sa_useful(candidate):sa=candidate;break
        if not effect and not(task=='CONTACT' and sa):return None
        box='Op & SA' if sa else 'Limited' if 'Limited' in free else 'Op & SA' if 'Op & SA' in free else None
        return dict(task=task,op=task,box=box,sa=sa,hold=False) if box else None
    def normal_plan(self,free):
        if self.count('force136')==0:
            plan=self.task_plan('CONTACT',free)
            if plan:return dict(plan,route='urgent')
        if self.campaign==3 and self.resistance>=16 and self.count('camp')>=self.count('force136'):
            plan=self.task_plan('SUPPLY',free)
            if plan:return dict(plan,route='urgent')
            if self.available('force136'):
                plan=self.task_plan('CONTACT',free)
                if plan:return dict(plan,route='urgent')
        for task in [self.card['primary']]+self.card['preparation'].split(' > '):
            plan=self.task_plan(task,free)
            if plan:return dict(plan,route='task' if task==self.card['primary'] else 'preparation')
        return dict(task='PASS',op='CONTACT',box=min(free,key=BOXES.index),sa=None,hold=False,route='pass')
    def threat_event(self,j):
        b=self.board;last=self.count('force136')==1
        if j==13:return last and any(v['force136'] and v['kempeitai'] and (not v['camp'] or self.cap.get(22)=='S') for v in b.values())
        if j in [20,25]:return last
        if j==14:return self.count('cache')>0
        if j==28:return any((b[s]['cache'] or last and b[s]['force136']) and any(b[x]['troops'] for x in {s}|ADJ[s]) for s in PROV)
        return False
    def event_rating(self,j):
        b=self.board;early=self.regular_seen<4;campaign=self.campaign;R=self.resistance
        def grade(n):return 'A' if n>=2 else 'B' if n==1 else None
        if j in [6,9,17]:return None
        if j==1:return grade(min(3,sum(v['terror'] for v in b.values()))) if R<20 else None
        if j==2:return grade(sum(not self.sabotage[r] and any(b[s]['opposition'] for s in self.rail_adj(r)) for r in EDGES))
        if j==4:return grade(min(20-R,sum(bool(v['force136'] and v['camp']) for v in b.values())))
        if j in CAPS:
            if campaign<=2:return 'A'
            if not early:return None
            useful={8:any(b[s]['camp'] and not b[s]['force136'] and not b[s]['cache'] for s in PROV) and self.available('cache')>0,
                    12:any(self.sabotage.values()),15:self.count('new_village')>0,
                    19:sum(bool(b[s]['force136'] and self.gather_targets(s)) for s in ORDER)>=3,
                    22:any(v['force136'] and ug(v) for v in b.values()),
                    27:any(not v['force136'] and ug(v) for v in b.values())}[j]
            return 'B' if useful else None
        if j==5:
            probe=self.clone();probe.execute_event(5)
            n=sum(v['red_a']+v['blue_a'] for s,v in b.items() if (v['force136'] or v['cache']) and
                  (probe.rail_choice(s,self.region()) or probe.strike_option(s) or probe.gather_targets(s)))
            return grade(n)
        if j==7:
            probe=self.clone();n=len(probe.gather())
            return 'A' if n>=2 else 'B' if n or self.zipper<20 else None
        if j==10:return 'A' if self.resources>=8 else 'B' if self.resources>=2 else None
        if j in [11,13]:
            probe=self.clone();old=sum(ug(v) for v in b.values());probe.execute_event(j)
            return grade(old-sum(ug(v) for v in probe.board.values()))
        if j==14:
            usable=[s for s in ORDER if b[s]['cache'] and not blue(b[s])]
            probe=self.clone();return grade(probe.event_placements(usable,'red',each=True))
        if j==16:
            probe=self.clone();old=[b[s]['force136'] for s in ORDER];probe.execute_event(j)
            if old==[probe.board[s]['force136'] for s in ORDER]:return None
            if probe.count('force136')>self.count('force136'):return 'A'
            return 'A' if any(b[s]['force136']>probe.board[s]['force136'] and b[s]['kempeitai'] and (not b[s]['camp'] or self.cap.get(22)=='S') for s in ORDER) else 'B'
        if j==20:
            n=sum(POP[s]>0 and b[s]['intel'] is None and s not in self.removed_intel for s in ORDER)
            probe=self.clone();normal=len(probe.gather())
            return 'B' if not early and self.count('force136')>=2 and n>=2 and normal<2 else None
        if j in [3,18,21,32]:
            probe=self.clone();probe.execute_event(j)
            return grade(probe.last_placements)
        if j==23:return 'A' if sum(not n for n in self.sabotage.values())>=2 else 'B'
        if j==24:
            probe=self.clone();probe.move_zipper(1);n=probe.supply()
            return 'A' if n>=2 else 'B' if n or self.zipper<20 else None
        if j==25:
            if any(self.task_plan(t,['Op & SA']) for t in ['SUPPLY','INTEL','RAID']):return 'A'
            probe=self.clone();return 'B' if probe.contact() else None
        if j==26:
            return 'A' if R<20 and any(v['force136'] and self.strike_option(s,bose=True) for s,v in b.items()) else None
        if j==28:
            probe=self.clone();f=self.count('force136');c=self.count('cache');probe.execute_event(j)
            return 'A' if probe.count('force136')>f or probe.count('cache')>c else None
        if j==29:return 'A' if self.count('kempeitai') else None
        if j==30:return grade(min(3,sum(bool(v['police'] and gs(v) and v['opposition']) for v in b.values())))
        if j==31:
            loss=min(self.resources,sum(bool(v['troops'] and v['opposition']) for v in b.values()))
            return 'A' if loss>=4 else 'B' if loss else None
        raise ValueError(('No Event policy',j))
    def bot_event_plan(self,free,normal=None):
        if 'Event' not in free or self.event in [6,9]:return None
        rating=self.event_rating(self.event);keen=self.card['b_events']=='YES'
        if rating=='A' or rating=='B' and keen:return dict(task='EVENT',box='Event',side='U',route='event',rating=rating)
        if self.threat_event(self.event) and 'J' not in self.chosen:
            if rating is None or rating=='B' and not keen and (normal or self.normal_plan(free))['route']=='pass':
                return dict(task='DENY',op='CONTACT',box='Event',route='event',sa=None,side=None,hold=False)
        return None
    def apply_bot_plan(self,plan):
        task=plan['task'];sa=plan.get('sa');result=None
        if task=='EVENT':self.execute_event(self.event,plan['side']);return
        if task in ['PASS','DENY']:self.contact();return
        if task in ['SUPPLY','INTEL','RAID']:
            if plan['op']=='TRAIN':self.train(reserve_cache_donors=plan.get('reserve_cache_donors',False))
            else:self.contact(task,hold=plan.get('hold',False))
            self.special(sa)
        else:
            self.operation(plan['op'],plan.get('hold',False))
            if plan['box']=='Op & SA' and not plan.get('no_sa'):
                for candidate in self.card['other_special'].split(' > '):
                    if candidate in PAIR[plan['op']] and self.sa_useful(candidate):self.special(candidate);break
    def score_only(self,final=False):
        b=self.board;clashes=0;resources_used=self.resources
        for s in ORDER:
            if red(b[s]) and blue(b[s]):
                self.lose_guerrilla(s,True,'red');self.lose_guerrilla(s,True,'blue');clashes+=1
        eligible=[s for s in ORDER[:9] if b[s]['opposition'] and not(self.cap.get(15)=='S' and b[s]['new_village'])]
        for s in sorted(eligible,key=self.placement_rank):
            if self.available('red')>0:b[s]['red_u']+=1
        effective=deepcopy(b)
        if self.cap.get(15)=='S':
            for v in effective.values():
                if v['new_village']:v['opposition']=False
        terms=score_terms(effective,self.resources)
        delta=terms['intel']+terms['caches']+terms['majorities']-terms['resource_penalty']-terms['neutral_penalty']-terms['police_penalty']
        before=self.resistance;self.resistance=clamp(before+delta);self.resources=0
        levels=[x for x in [0,6,12,18,20] if x<=self.resistance];self.move_zipper(target=max(levels))
        if final:
            self.winner='Japan' if self.resistance<18 else 'Force 136' if self.resistance==20 or self.count('camp')<self.count('force136') else 'MPAJA'
            self.ended=True
        return dict(resistance_before=before,net_change=delta,resistance_after=self.resistance,winner=self.winner,clashes=clashes,score_board=effective,resources_used=resources_used,**terms)
    def bot_choose(self,free):
        normal=self.normal_plan(free);event=self.bot_event_plan(free,normal)
        # Candidate experiment: recovery first, while retaining restoring Events.
        if self.variant in ['recovery_first','combined','primary_guard'] and self.count('force136')==0:
            if event and event['task']=='EVENT':
                probe=self.clone();probe.apply_bot_plan(event)
                if probe.count('force136')>0:return event
            if normal['route']=='urgent':return normal
        if self.campaign==3 and 'J' in self.chosen and len(self.deck)-self.deck_pos==1:
            candidates=[normal,self.task_plan('SUPPLY',free),event,self.task_plan('CONTACT',free)]
            if self.event==4 and 'Event' in free:candidates.append(dict(task='EVENT',side='S',box='Event',route='event'))
            for plan in candidates:
                if not plan:continue
                probe=self.clone();probe.apply_bot_plan(plan)
                if probe.uncertain:continue
                probe.score_only(True)
                if probe.winner=='Force 136':self.inc('final_guard_used');return dict(plan,route='final_guard')
        # The following are named experimental paper-policy changes. None is
        # part of the delivered v0.2 bot or selected by the baseline branch.
        if self.variant in ['cache_guard','combined','primary_guard']:
            urgent=[s for s in ORDER if self.board[s]['force136'] and self.board[s]['cache'] and gs(self.board[s])<2 and self.board[s]['troops']]
            if urgent:
                probe=self.clone();n=probe.train()
                if n and any(gs(probe.board[s])>gs(self.board[s]) for s in urgent):
                    box='Limited' if 'Limited' in free else 'Op & SA' if 'Op & SA' in free else None
                    if box:return dict(task='TRAIN',op='TRAIN',box=box,sa=None,no_sa=True,hold=False,route='cache_guard')
        if self.variant in ['late_intel','combined'] and self.regular_seen>=4:
            plan=self.task_plan('INTEL',free)
            if plan:
                probe=self.clone();before=sum(v['intel'] is not None for v in probe.board.values());probe.apply_bot_plan(plan)
                if sum(v['intel'] is not None for v in probe.board.values())-before>=2:return dict(plan,route='late_intel')
        if self.variant in ['primary_first','primary_guard'] and normal['route']=='task':return normal
        return event or normal
    def bot_turn(self,free):
        self.ensure_card();before_f=self.count('force136');before=deepcopy(self.board)
        plan=self.bot_choose(free)
        plan['card_id']=self.card['id'];plan['printed_primary']=self.card['primary']
        if not self.preview:
            self.decisions.append(dict(draw=self.draw,campaign=self.campaign,event=self.event,plan=deepcopy(plan),
                board_before=deepcopy(self.board),chosen_before=deepcopy(self.chosen),free=free,
                resistance=self.resistance,resources=self.resources,zipper=self.zipper,cap=deepcopy(self.cap),
                sabotage=deepcopy(self.sabotage),active_card=deepcopy(self.card),card_age=self.age,
                cards_remaining=len(self.deck)-self.deck_pos,regular_seen=self.regular_seen,
                available={k:self.available(k) for k in ['red','blue','cache','camp','force136','police']}))
        self.chosen['B']=plan['box'];self.apply_bot_plan(plan)
        self.inc('bot_turns');self.inc('task_'+plan['task']);self.inc('route_'+plan['route'])
        if not before_f:
            self.inc('turns_starting_without_force136')
            if self.count('force136')==0:self.inc('turns_without_recovery')
        if before==self.board:self.inc('board_unchanged_bot_turns')
        self.inc('unguarded_caches_end_bot',sum(v['cache'] and not gs(v) for v in self.board.values()))
        primary=plan['task']==self.card['primary'] and plan['task'] not in ['EVENT','DENY','PASS']
        if primary or self.age==1:self.bot_discard.append(self.card);self.card=None;self.age=0
        else:self.age=1
        self.record('British turn',plan)
    def jp_value(self):
        b=self.board;policy=self.policy
        if policy=='hunting':wr,wf,wcache,wintel,wres,wy=2.4,5.2,2.0,2.2,.35,.45
        elif policy=='extraction':wr,wf,wcache,wintel,wres,wy=2.5,1.8,2.2,2.0,.8,.7
        elif policy=='repair':wr,wf,wcache,wintel,wres,wy=2.7,2.0,2.3,2.3,.55,1.2
        else:wr,wf,wcache,wintel,wres,wy=3.1,3.3,2.6,3.2,.65,.65
        value=-wr*self.resistance+wres*self.resources-wf*self.count('force136')-wcache*self.count('cache')
        value-=wintel*sum(v['intel'] or 0 for v in b.values())
        value-=1.3*sum(gs(v)>cubes(v) for v in b.values())
        value+=.2*sum(POP[s] for s in ORDER if not b[s]['opposition'])+.5*sum(v['police']>0 for v in b.values())
        value+=wy*(sum(live_and_yield(self.sabotage)[1].values())+self.count('new_village'))
        for s,v in b.items():
            if v['force136']:
                if v['kempeitai']:
                    faces=sum(d+v['police']>gs(v) for d in range(1,7))/6
                    value+=faces*(1.5 if v['camp'] and self.cap.get(22)!='S' else 3.2)
                value-=.55*ug(v)
            if v['troops']:
                value+=.45*(v['red_a']+v['blue_a'])+(.8 if v['cache'] and not gs(v) else 0)
        cap_values={8:3.0,12:2.2,15:1.8,19:1.8,22:2.5,27:2.0}
        value+=sum(cap_values[k]*(1 if side=='S' else -1) for k,side in self.cap.items())
        return value
    def jp_apply(self,plan):
        if plan['op']=='EVENT':self.execute_event(self.event,'S');return
        op=plan['op'];sa=plan.get('sa');limit=1 if plan['box']=='Limited' else 3
        if plan.get('timing')=='before':
            if sa=='REPRISAL':self.reprisal()
            elif sa=='ELIMINATE':self.eliminate()
        if op=='DEPLOY':self.deploy(limit)
        elif op=='CONSTRUCT':self.construct(limit)
        elif op=='ASSAULT':self.assault(limit)
        elif op=='SWEEP':self.sweep_plan(limit,strength=plan.get('strength',3))
        elif op=='PASS':self.deploy(1)
        else:raise ValueError(op)
        if plan.get('timing')!='before':
            if sa=='EXTRACT':self.extract()
            elif sa=='REPRISAL':self.reprisal()
            elif sa=='ELIMINATE':self.eliminate()
    def japan_turn(self,free):
        candidates=[]
        for box in free:
            if box=='Event':
                if self.event not in [6,9]:candidates.append(dict(op='EVENT',box=box,sa=None))
                continue
            for op in ['DEPLOY','CONSTRUCT','ASSAULT','SWEEP']:
                special=[None] if box=='Limited' else ['EXTRACT'] if op=='DEPLOY' else [None,'REPRISAL','ELIMINATE']
                for sa in special:
                    for strength in ([2,5,0] if op=='SWEEP' else [3]):
                        for timing in (['before','after'] if sa=='REPRISAL' else ['after']):
                            candidates.append(dict(op=op,box=box,sa=sa,strength=strength,timing=timing))
        for plan in candidates:
            probe=self.clone();probe.jp_apply(plan)
            # A one-step heuristic, not an optimal or learning Japanese player.
            tempo=1.0 if plan['box']=='Limited' else .3 if plan['box']=='Event' else 0
            plan['_value']=probe.jp_value()+tempo
        assert candidates
        plan=max(candidates,key=lambda p:(p['_value'],-BOXES.index(p['box']),-['DEPLOY','CONSTRUCT','ASSAULT','SWEEP','EVENT'].index(p['op'])))
        self.chosen['J']=plan['box'];self.jp_apply(plan);self.inc('japan_'+plan['op'])
        if plan.get('sa'):self.inc('japan_'+plan['sa'])
        self.record('Japanese turn',plan)
    def propaganda(self,final=False):
        result=self.score_only(final);self.record('Final scoring' if final else 'Nonfinal scoring',result)
        if final:return result
        b=self.board
        for rail,n in self.sabotage.items():
            if n:
                sites=[s for s in self.rail_adj(rail) if POP[s] and not b[s]['terror'] and not b[s]['opposition']]
                if sites:b[min(sites,key=self.opp_rank)]['opposition']=True
        self.construct();self.supply();self.reprisal()
        selected=set()
        for src in ORDER:
            v=b[src]
            if not v['force136']:continue
            exposed=v['kempeitai'] and (not v['camp'] or self.cap.get(22)=='S')
            sites=[s for s in PROV if b[s]['camp'] and not b[s]['force136'] and s not in selected and s!=src]
            eligible=[s for s in sites if exposed or not gs(v) and not v['cache'] or self.available('cache') and v['cache'] and not b[s]['cache']]
            if eligible:
                dst=min(eligible,key=lambda s:(bool(b[s]['kempeitai']),not(not b[s]['cache'] and self.available('cache')),-gs(b[s]),-POP[s],ix(s)))
                v['force136']-=1;b[dst]['force136']+=1;selected.add(dst)
        sites=[s for s in ORDER if b[s]['troops']>gs(b[s])]
        if sites:
            # Leave existing police at otherwise ineligible intelligence sites;
            # every moved Police and Kempeitai has a legal destination.
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
        if self.card:self.bot_discard.append(self.card);self.card=None;self.age=0
        self.campaign+=1;self.first='B';self.regular_seen=0;self.chosen={};self.record('Reset complete',{})
        return result
    def run(self):
        while not self.ended:
            assert self.deck_pos<len(self.deck),'Deck exhausted without final scoring'
            self.event=self.deck[self.deck_pos];self.deck_pos+=1;self.draw+=1;self.chosen={}
            if self.event>=33:
                self.propaganda(final=self.campaign==3);continue
            self.regular_seen+=1;self.icon(self.event);self.mandatory(self.event)
            self.record('Icon and mandatory',{})
            if self.ended:break
            for who in [self.first,'J' if self.first=='B' else 'B']:
                free=[box for box in BOXES if box not in self.chosen.values() and not(self.event in [6,9] and box=='Event')]
                if who=='B':self.bot_turn(free)
                else:self.japan_turn(free)
            self.first=min(self.chosen,key=lambda who:BOXES.index(self.chosen[who]))
            self.invariants()
        return dict(seed=self.seed,policy=self.policy,variant=self.variant,corner=self.corner,winner=self.winner,
                    final_resistance=self.resistance,camps=self.count('camp'),force136=self.count('force136'),
                    regular_cards=sum(1 for x in self.log if x['kind']=='British turn'),draws=self.draw,
                    ending='J9' if self.event==9 else 'Propaganda',metrics=self.metrics,
                    event_order=[x for x in self.deck[:self.deck_pos]],bot_cycles=self.bot_cycles)
