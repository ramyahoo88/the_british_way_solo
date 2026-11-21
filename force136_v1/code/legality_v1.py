"""Independent legality check of every Force 136 action against the publisher's rules.

The checks below are written from GMT's Japanese Occupation player aid (British Operations and Special
Activities, British Limited Operations and Pass, MPAJA Card Icons) and rulebook sections 1.4.1-1.4.3,
1.15, 2.4, 3.2, 4.1-4.2, 6.3-6.5. They do not use the bot's own procedures: each check looks only at
the position before and after an Operation, Special Activity, icon or Propaganda step, and asks
whether a British player could legally have done that.

A legal action is not necessarily what the printed bot rules prescribe; verify_v1.py and fuzz_v1.py
check that. This script checks the claim in rules section 1: "It pays every cost and follows every
rule a British player follows."

usage: python3 legality_v1.py games [seeds]        policy games, all five levels (default 16 seeds)
       python3 legality_v1.py fuzz  [positions]    random positions from fuzz_v1.random_state (default 2000)
       python3 legality_v1.py selftest             ten planted illegal actions; each must be caught
Exit status 1 if any violation is found.
"""
import sys,os,itertools,collections,random,json
from copy import deepcopy
HERE=os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0,HERE)
import engine as E
from engine import ORDER,PROV,POP,ADJ,EDGES,BOXES
import force136_v1 as V

EC=('Northern EC','Southern EC')
G=('red_u','red_a','blue_u','blue_a')
ALLOWED_SA={'CONTACT':{'SUPPLY','GATHER','RAID'},'TRAIN':{'SUPPLY','RAID'},'SABOTAGE':{'GATHER','RAID'},'AMBUSH':{'GATHER','RAID'}}

def snap(g):
    return dict(board=deepcopy(g.board),sab=dict(g.sabotage),R=g.resistance,cap=dict(g.cap),zipper=g.zipper,
                avail={k:g.available(k) for k in ('red','blue','cache','camp','force136')},
                removed=set(g.removed_intel),rail_adj={r:set(g.rail_adj(r)) for r in EDGES},level=g.level)
def gcount(v,c=None):return sum(v[k] for k in G if c is None or k.startswith(c))
def cubes(v):return v['troops']+v['police']
def caches_near(b,s):return sum(b[x]['cache'] for x in ORDER if x==s or x in ADJ[s])

class Bad(Exception):pass
def need(cond,msg):
    if not cond:raise Bad(msg)

def only_changed(a,b,spaces_fields,what):
    """No field outside spaces_fields may differ, except a New Village removed under rule 1.15."""
    for s in ORDER:
        for k in a['board'][s]:
            if a['board'][s][k]!=b['board'][s][k] and (s,k) not in spaces_fields:
                if k=='new_village' and a['board'][s][k] and not b['board'][s][k]:
                    v=b['board'][s];need((gcount(v) or v['cache']) and not cubes(v),f'{what}: New Village removed illegally in {s}')
                    continue
                raise Bad(f'{what}: unexpected change {s}.{k} {a["board"][s][k]}->{b["board"][s][k]}')

# ---------------------------------------------------------------- Operations
def check_train(a,b):
    A,B=a['board'],b['board'];touched=set()
    for c,total in (('red',10),('blue',4)):
        placed=removed=0
        for s in ORDER:
            du=B[s][c+'_u']-A[s][c+'_u'];da=B[s][c+'_a']-A[s][c+'_a']
            if not du and not da:continue
            touched|={(s,c+'_u'),(s,c+'_a')}
            if du>0:                                      # a Train space
                need(A[s]['force136'] and s not in EC,f'Train placed {c} in {s} without Force 136 or in an EC')
                need(da<=0 and -da<=du,f'Train: odd status change in {s}')
                placed+=du;removed+=-da                   # -da = Active pieces re-placed Underground here
            else:
                need(du<=0 and da<=0,f'Train: odd change in {s}');removed+=-(du+da)
        need(placed-removed<=a['avail'][c],f'Train placed more {c} than Available')
        need(removed==0 or placed-removed==a['avail'][c],f'Train took {c} from the map while {c} was Available (1.4.1)')
    for s in ORDER:
        gain=sum(max(0,B[s][c+'_u']-A[s][c+'_u']) for c in ('red','blue'))
        redgain=max(0,B[s]['red_u']-A[s]['red_u'])
        if gain:
            if A[s]['cache']:need(gain<=2,f'Train placed {gain} at the Cache in {s}')
            else:
                need(gain<=1,f'Train placed {gain} in {s} without a Cache')
                need(not redgain or A[s]['camp'],f'Train placed MPAJA in {s} without a Camp or Cache')
    only_changed(a,b,touched,'Train')
    need(a['sab']==b['sab'] and a['R']==b['R'],'Train changed Sabotage or Resistance')

def check_contact(a,b):
    A,B=a['board'],b['board']
    df={s:B[s]['force136']-A[s]['force136'] for s in ORDER if B[s]['force136']!=A[s]['force136']}
    touched=set((s,'force136') for s in df)
    arrivals=[s for s,d in df.items() if d>0]
    if not df:
        only_changed(a,b,set(),'Contact (no effect)');return
    if sum(df.values())==1:                                # placed one marker from Available
        need(len(df)==1 and a['avail']['force136']>=1,'Contact placed a marker that was not Available')
        need(arrivals[0] in PROV,'Contact placed a marker outside a Province')
    else:                                                  # moved markers to adjacent spaces
        need(sum(df.values())==0,'Contact changed the number of markers')
        srcs=[s for s,d in df.items() if d<0]
        need(len(srcs)==1 and len(arrivals)==1 and df[srcs[0]]==-1,'Contact move: expected one marker moved')
        need(arrivals[0] in ADJ[srcs[0]],'Contact moved a marker to a non-adjacent space')
        moved=0
        for k in ('blue_u','blue_a'):
            d=B[arrivals[0]][k]-A[arrivals[0]][k]
            if d:
                need(d>0 and A[srcs[0]][k]-B[srcs[0]][k]==d,'Contact escort: guerrilla count mismatch')
                moved+=d;touched|={(arrivals[0],k),(srcs[0],k)}
        need(moved<=1,'Contact moved more than one non-MPAJA guerrilla with a marker')
    d=arrivals[0]
    if d in PROV and not A[d]['camp']:
        need(B[d]['camp'],'Contact did not place a Jungle Camp with the marker');touched.add((d,'camp'))
        gone=[s for s in PROV if A[s]['camp'] and not B[s]['camp']]
        if a['avail']['camp']>0:need(not gone,'Contact removed a Camp although one was Available')
        else:
            need(len(gone)==1,'Contact with no Camp Available must relocate exactly one Camp (1.10)');touched.add((gone[0],'camp'))
    only_changed(a,b,touched,'Contact')
    need(a['sab']==b['sab'] and a['R']==b['R'],'Contact changed Sabotage or Resistance')

def activations(a,b,what):
    """Spaces where exactly one Underground guerrilla became Active; nothing else may happen to guerrillas."""
    A,B=a['board'],b['board'];out={}
    for s in ORDER:
        for c in ('red','blue'):
            du=B[s][c+'_u']-A[s][c+'_u'];da=B[s][c+'_a']-A[s][c+'_a']
            if du or da:
                need(du==-1 and da==1 and s not in out,f'{what}: guerrilla change in {s} is not one activation')
                out[s]=c
    return out

def match_rails(spaces,rails,rail_adj):
    """Is there a one-to-one assignment of new Sabotage markers to activating spaces, each adjacent?"""
    if len(spaces)!=len(rails):return False
    return any(all(s in rail_adj[r] for s,r in zip(spaces,perm)) for perm in itertools.permutations(rails))

def check_sabotage(a,b):
    A,B=a['board'],b['board'];act=activations(a,b,'Sabotage')
    extra=[s for s in act if not A[s]['force136']]
    need(len(extra)<=(1 if a['cap'].get(27)=='U' else 0),'Sabotage in a space without Force 136')
    new=[r for r in EDGES if b['sab'][r]!=a['sab'][r]]
    need(all(a['sab'][r]==0 and b['sab'][r]==1 for r in new),'Sabotage placed on a railway that already had Sabotage')
    need(match_rails(list(act),new,a['rail_adj']),'Sabotage markers do not match activated spaces')
    only_changed(a,b,{(s,c+x) for s,c in act.items() for x in ('_u','_a')},'Sabotage')
    need(a['R']==b['R'],'Sabotage changed Resistance')

def check_ambush(a,b,rolls,limit_spaces=None,extra_ok=True):
    """rolls: {space: [die results]} logged during the Ambush."""
    A,B=a['board'],b['board'];act=activations(a,b,'Ambush')
    if limit_spaces is None:
        extra=[s for s in act if not A[s]['force136']]
        need(len(extra)<=(1 if extra_ok and a['cap'].get(27)=='U' else 0),'Ambush in a space without Force 136')
    else:need(set(act)<=set(limit_spaces),'Raid Ambush outside the Raid destination')
    touched={(s,c+x) for s,c in act.items() for x in ('_u','_a')}
    gained=0;moved_t=moved_k=0
    for s in ORDER:
        dt=B[s]['troops']-A[s]['troops'];dp=B[s]['police']-A[s]['police'];dk=B[s]['kempeitai']-A[s]['kempeitai']
        if s=='Kuala Lumpur':continue
        if dt or dp or dk:
            need(s in act,f'Ambush changed Japanese pieces in {s} without activating a guerrilla there')
            need((dt,dp,dk) in ((0,-1,0),(-1,0,0),(0,0,-1)),f'Ambush removed more than one piece in {s}')
            touched|={(s,'troops'),(s,'police'),(s,'kempeitai')}
            if dp==0:
                r=rolls.get(s,[])
                need(len(r)==1,f'Ambush moved a piece from {s} without exactly one roll')
                need(r[0]+caches_near(A,s)>cubes(A[s]),f'Ambush in {s} succeeded on a failing roll')
                gained+=1;moved_t+=-dt;moved_k+=-dk
            else:need(not rolls.get(s),f'Ambush in {s} rolled and also removed Police')
        elif s in act:
            v=A[s];need(cubes(v) or v['kempeitai'],f'Ambush in {s} with no Japanese forces or Kempeitai')
            r=rolls.get(s,[])
            need(len(r)==1 and not r[0]+caches_near(A,s)>cubes(v),f'Ambush in {s} did nothing without a failed roll')
    kl=B['Kuala Lumpur'];kl0=A['Kuala Lumpur']
    dp=kl['police']-kl0['police']
    if 'Kuala Lumpur' in act:
        need(dp in (0,-1),'Ambush in Kuala Lumpur: odd Police change')
        if dp==0:
            r=rolls.get('Kuala Lumpur',[]);need(len(r)==1,'Ambush in Kuala Lumpur did nothing without a roll')
    else:need(dp==0,'Police changed in Kuala Lumpur without an Ambush there')
    need(kl['troops']-kl0['troops']==moved_t and kl['kempeitai']-kl0['kempeitai']==moved_k,'Pieces moved by Ambush did not arrive in Kuala Lumpur')
    touched|={('Kuala Lumpur','troops'),('Kuala Lumpur','police'),('Kuala Lumpur','kempeitai')}
    need(b['R']==min(20,a['R']+gained),'Ambush Resistance gain is wrong')
    only_changed(a,b,touched,'Ambush')
    need(a['sab']==b['sab'],'Ambush changed Sabotage')
    for s in act:need(A[s]['red_u']+A[s]['blue_u']>0,'Ambush without an Underground guerrilla')

# ---------------------------------------------------------------- Special Activities
def check_gather(a,b):
    A,B=a['board'],b['board']
    revealed=[s for s in ORDER if A[s]['intel'] is None and B[s]['intel'] is not None]
    need(all(A[s]['intel']==B[s]['intel'] for s in ORDER if s not in revealed),'Gather changed a revealed chit')
    need(not any(s in a['removed'] for s in revealed),'Gather revealed a removed chit')
    touched={(s,'intel') for s in revealed}
    if a['cap'].get(22)=='U':
        for s in revealed:need(A[s]['red_u']+A[s]['blue_u']>0,f'Gather revealed {s} without an Underground guerrilla')
    else:
        act=activations(a,b,'Gather');need(set(act)==set(revealed),'Gather activations do not match reveals')
        touched|={(s,c+x) for s,c in act.items() for x in ('_u','_a')}
    limit=3 if a['cap'].get(19)=='U' else 2
    anchors=[s for s in ORDER if A[s]['force136']]
    ok=not revealed
    for k in range(1,limit+1):
        for combo in itertools.permutations(anchors,k):
            cover=set()
            for i,x in enumerate(combo):
                cover.add(x)
                if not (a['cap'].get(19)=='S' and i>0):cover|=ADJ[x]
            if set(revealed)<=cover:ok=True
    need(ok,f'Gather revealed {revealed} beyond {limit} Force 136 spaces and their neighbours')
    only_changed(a,b,touched,'Gather')
    need(a['sab']==b['sab'] and a['R']==b['R'],'Gather changed Sabotage or Resistance')

def check_supply(a,b,rolls=None):
    """rolls: {space: [die results]} logged during the Supply (Japanese side of J8). Under that side every
    selected space is rolled for, so the rolled spaces are the selected ones; otherwise the selected
    spaces are the converted ones."""
    A,B=a['board'],b['board'];rolls=rolls or {}
    conv=[s for s in ORDER if B[s]['cache'] and not A[s]['cache']]
    j8s=a['cap'].get(8)=='S'
    if j8s:
        need(all(len(r)==1 for r in rolls.values()),'J8: a Supply space was rolled for more than once')
        need(set(conv)<=set(rolls),'J8: a Camp was converted without its roll')
        for s,r in rolls.items():
            need((s in conv)==(r[0]>=3),f'J8: {s} rolled {r[0]} but was {"" if s in conv else "not "}converted')
        selected=list(rolls)
    else:
        need(not rolls,'Supply rolled without the Japanese side of J8')
        selected=list(conv)
    touched=set()
    need(len(selected)<=(3 if a['zipper']>=12 else 2),'Supply selected too many Provinces')
    need(len(selected)<=a['avail']['cache'],'Supply selected more Provinces than Caches Available')
    remote=0
    for s in selected:
        need(s in PROV and A[s]['camp'] and not A[s]['cache'],f'Supply selected {s}, which has no Jungle Camp to replace')
        if not A[s]['force136']:remote+=1
    for s in conv:
        need(not B[s]['camp'],f'Supply in {s} did not replace the Jungle Camp');touched|={(s,'camp'),(s,'cache')}
    need(remote<=(1 if a['cap'].get(8)=='U' else 0),'Supply in a Province without Force 136')
    lostopp=[s for s in ORDER if A[s]['opposition'] and not B[s]['opposition']]
    if a['cap'].get(27)=='S':                              # "Each Supply removes Opposition from 1 selected space (if possible)"
        could=[s for s in selected if A[s]['opposition']]
        need(len(lostopp)==(1 if could else 0) and set(lostopp)<=set(could),f'J27: Opposition removed in {lostopp}, selected spaces with Opposition {could}')
        touched|={(s,'opposition') for s in lostopp}
    else:need(not lostopp,'Supply removed Opposition without the Japanese side of J27')
    only_changed(a,b,touched,'Supply')
    need(a['sab']==b['sab'] and a['R']==b['R'],'Supply changed Sabotage or Resistance')

def raid_steps(state,limit,used,trace,target,log):
    """Depth-first search: can a sequence of legal Raid steps turn `state` into `target`?
    state/target: (board, sab, R). Dice are checked separately (check_ambush on the nested Ambush)."""
    board,sab,R=state
    if board==target[0] and sab==target[1] and R==target[2]:return True
    if len(used)>=limit:return False
    log['nodes']=log.get('nodes',0)+1
    if log['nodes']>BUDGET:raise Undecided()
    T=target[0];strict=log.get('strict',False)
    for d in ORDER:
        if d in used:continue
        for src in ADJ[d]:
            if not board[src]['cache']:continue
            if strict and all(board[src][k]==T[src][k] for k in G):continue   # first pass: a source must still differ from the result
            pool=[k for k in G for _ in range(min(2,board[src][k]))]
            combos=set()
            for n in (1,2):
                for c in itertools.combinations(pool,n):combos.add(tuple(sorted(c)))
            for combo in combos:
                nb=deepcopy(board)
                for k in combo:nb[src][k]-=1;nb[d][k]+=1
                # prune: the source must now match the target unless it is touched again; keep it simple and
                # require the destination's guerrilla total to match the target after this step's optional action
                options=[(nb,dict(sab),R)]
                for c in ('red','blue'):
                    if nb[d][c+'_u']:
                        act=deepcopy(nb);act[d][c+'_u']-=1;act[d][c+'_a']+=1
                        for r in EDGES:                                  # Limited Sabotage there
                            if not sab[r] and d in log['rail_adj'][r]:
                                s2=dict(sab);s2[r]=1;options.append((act,s2,R))
                        v=nb[d]
                        if cubes(v) or v['kempeitai']:                   # Limited Ambush there
                            if v['police']:
                                x=deepcopy(act);x[d]['police']-=1;options.append((x,dict(sab),R))
                            options.append((act,dict(sab),R))            # failed roll
                            if d!='Kuala Lumpur':
                                for f in ('troops','kempeitai'):
                                    if v[f]:
                                        x=deepcopy(act);x[d][f]-=1;x['Kuala Lumpur'][f]+=1;options.append((x,dict(sab),min(20,R+1)))
                for nb2,s2,R2 in options:
                    for s in ORDER:                                      # New Village cleanup (1.15)
                        v=nb2[s]
                        if v['new_village'] and (gcount(v) or v['cache']) and not cubes(v):v['new_village']=False
                    # prune: spaces other than later sources/destinations must already match; require d to match
                    if any(nb2[d][k]!=T[d][k] for k in nb2[d]) and not T[d]['cache']:continue
                    if raid_steps((nb2,s2,R2),limit,used|{d},trace+[(src,d,combo)],target,log):return True
    return False

BUDGET=20000         # search nodes for one Raid step; not reached in practice
class Undecided(Exception):pass
def check_raid(a,b,steps=None):
    """steps: the positions observed after each Raid destination was resolved (witnesses). Each step must be
    one legal Raid step to a new destination, and the last must equal the final position."""
    need(a['level']!='recruit' or a['board']==b['board'],'Recruit must not Raid')
    limit=3 if a['zipper']==20 else 2
    seq=[(deepcopy(a['board']),dict(a['sab']),a['R'])]
    for st in (steps or []):
        if st!=seq[-1]:seq.append(st)
    final=(b['board'],b['sab'],b['R'])
    if seq[-1]!=final:seq.append(final)
    need(len(seq)-1<=limit,f'Raid used {len(seq)-1} destinations; the limit is {limit}')
    dests=[]
    for x,y in zip(seq,seq[1:]):
        gained=[s for s in ORDER if gcount(y[0][s])>gcount(x[0][s])]
        need(len(gained)==1,f'Raid step moved guerrillas into {gained}')
        need(gained[0] not in dests,f'Raid selected {gained[0]} twice');dests.append(gained[0])
        log=dict(rail_adj=a['rail_adj'],nodes=0,strict=False)
        need(raid_steps((deepcopy(x[0]),dict(x[1]),x[2]),1,frozenset(),[],y,log),f'Raid step into {gained[0]} is not a legal Raid step')

CHECK={'TRAIN':check_train,'CONTACT':check_contact,'SABOTAGE':check_sabotage,'GATHER':check_gather,'SUPPLY':check_supply,'RAID':check_raid}

# ---------------------------------------------------------------- between turns
def check_mobilize(a,b):
    A,B=a['board'],b['board']
    elig=[s for s in ORDER if A[s]['camp'] and not A[s]['terror'] and not A[s]['opposition']]
    new=[s for s in ORDER if B[s]['opposition'] and not A[s]['opposition']]
    need(len(new)==(1 if elig else 0) and set(new)<=set(elig),f'Mobilize Population: added Opposition in {new}, eligible {elig}')
    only_changed(a,b,{(s,'opposition') for s in new},'Mobilize Population')
def check_kill(a,b):
    A,B=a['board'],b['board']
    elig=[s for s in ORDER if A[s]['police'] and gcount(A[s],'red')]
    gone=[s for s in ORDER if B[s]['police']!=A[s]['police']]
    need(len(gone)==(1 if elig else 0) and set(gone)<=set(elig) and all(A[s]['police']-B[s]['police']==1 for s in gone),f'Kill Traitors: Police removed in {gone}, eligible {elig}')
    only_changed(a,b,{(s,'police') for s in gone},'Kill Traitors')
def check_resources_phase(a,b):
    A,B=a['board'],b['board']
    new=[s for s in ORDER if B[s]['opposition'] and not A[s]['opposition']]
    rails=[r for r in EDGES if a['sab'][r]]
    need(len(new)<=len(rails),'Resources phase: more Opposition than sabotaged railways')
    for s in new:need(POP[s] and not A[s]['terror'],f'Resources phase: Opposition in {s} (Terror or not a Province/Kuala Lumpur)')
    need(any(all(s in a['rail_adj'][r] for s,r in zip(new,perm)) for perm in itertools.permutations(rails,len(new))),'Resources phase: Opposition not adjacent to distinct sabotaged railways')
    only_changed(a,b,{(s,'opposition') for s in new},'Resources phase')
def check_redeploy(a,b):
    A,B=a['board'],b['board']
    df={s:B[s]['force136']-A[s]['force136'] for s in ORDER if B[s]['force136']!=A[s]['force136']}
    need(sum(df.values())==0,'Redeploy changed the number of markers')
    for s,d in df.items():
        if d>0:need(A[s]['camp'],f'Redeploy moved a marker to {s}, which has no Jungle Camp')
    only_changed(a,b,{(s,'force136') for s in df},'Redeploy')

# ---------------------------------------------------------------- instrumented bot
class Checked(V.Force136):
    """Force 136 with every real (non-preview) action checked. Violations collect in self.viol (shared)."""
    def __init__(self,*a,**k):
        V.Force136.__init__(self,*a,**k);self.viol=Viol();self._depth=0;self._rolls=None
    def _run(self,name,fn,*a,**k):
        if self.preview:return fn(*a,**k)
        top=self._depth==0;self._depth+=1
        before=snap(self) if (top or name=='AMBUSH') else None
        if name=='AMBUSH':saved=self._rolls;self._rolls=collections.defaultdict(list)
        if name=='SUPPLY' and top:self._srolls=collections.defaultdict(list)
        if name=='RAID' and top:self._raid_steps=[]
        try:r=fn(*a,**k)
        finally:self._depth-=1
        try:
            after=snap(self)
            if name=='AMBUSH':
                locs=k.get('locations',a[0] if a else None)
                check_ambush(before,after,dict(self._rolls),limit_spaces=locs,extra_ok=k.get('extra',True))
            elif top and name=='SUPPLY':check_supply(before,after,dict(self._srolls));self._srolls=None
            elif top and name=='RAID':check_raid(before,after,self._raid_steps);self._raid_steps=None
            elif top:CHECK[name](before,after)
            self.viol.n[name]+=1
        except Undecided:self.viol.n['RAID_UNDECIDED']+=1
        except Bad as e:
            self.viol.add(self,name,str(e),before)
        finally:
            if name=='AMBUSH':self._rolls=saved
        return r
    def die(self,tag,space=''):
        r=V.Force136.die(self,tag,space)
        if not self.preview and tag=='Ambush' and self._rolls is not None:self._rolls[space].append(r)
        if not self.preview and tag=='Supply' and getattr(self,'_srolls',None) is not None:self._srolls[space].append(r)
        return r
    def cleanup(self):
        V.Force136.cleanup(self)                    # the bot's Raid calls cleanup() after each destination: record the position
        if not self.preview and getattr(self,'_raid_steps',None) is not None:
            self._raid_steps.append((deepcopy(self.board),dict(self.sabotage),self.resistance))
    def contact(self,*a,**k):return self._run('CONTACT',V.Force136.contact,self,*a,**k)
    def train(self,*a,**k):return self._run('TRAIN',V.Force136.train,self,*a,**k)
    def strike(self,*a,**k):
        if k.get('bose') or (len(a)>2 and a[2]):return V.Force136.strike(self,*a,**k)
        return self._run('AMBUSH',lambda *aa,**kk:V.Force136.strike(self,*aa,**kk),*a,**k)
    def rail(self,region='C',locations=None,color=None,extra=True):
        if locations is not None or self._depth:return V.Force136.rail(self,region,locations,color,extra)
        return self._run('SABOTAGE',V.Force136.rail,self,region,locations,color,extra)
    def gather(self):return self._run('GATHER',V.Force136.gather,self)
    def supply(self):return self._run('SUPPLY',V.Force136.supply,self)
    def raid(self):return self._run('RAID',V.Force136.raid,self)
    def bot_turn(self,free):
        if self.preview:return V.Force136.bot_turn(self,free)
        self._in_turn=True;before=snap(self)
        try:V.Force136.bot_turn(self,free)
        finally:self._in_turn=False
        p=self.last_plan
        try:
            need(p['box'] in free,'chose a box that was not free')
            need(self.event not in (6,9) or p['box']!='Event','used the Event box on a Mandatory Event card (rule 5.4), even for a Pass')
            if p['op']=='PASS':
                after=snap(self);need(before['board']==after['board'] and before['sab']==after['sab'] and before['R']==after['R'],'a Pass changed the position')
            elif p['op']=='EVENT':                    # either side of an Event may be executed by either player (5.2)
                need(p['box']=='Event','executed an Event outside the Event box')
                self.viol.n[f'EVENT_J{self.event}']+=1
                after=snap(self)
                if self.event==4:                     # J4 British side: +1 Resistance per space with Force 136 and a Jungle Camp
                    n=sum(1 for v in before['board'].values() if v['force136'] and v['camp'])
                    need(after['board']==before['board'] and after['sab']==before['sab'],'J4 changed the board')
                    need(after['R']==min(20,before['R']+n),f"J4: Resistance {before['R']}->{after['R']}, expected +{n}")
                elif self.event==25:                  # J25 British side: Contact, then any one Special Activity
                    pass                              # the Contact and the Special Activity are each checked as they happen
                else:raise Bad(f'executed J{self.event}, which no printed rule allows')
            else:
                need(p['box'] in ('Limited','Op & SA'),'acted in the Event box')
                if p['box']=='Limited':need(not p.get('sa'),'Limited Operation with a Special Activity')
                elif p.get('sa'):need(p['sa'] in ALLOWED_SA[p['op']],f"{p['sa']} may not accompany {p['op']}")
            self.viol.n['TURN']+=1
        except Bad as e:self.viol.add(self,'TURN',str(e),before)
    def icon(self,j):
        if self.preview or not (j in E.MOBILIZE or j in E.KILL):return V.Force136.icon(self,j)
        before=snap(self);V.Force136.icon(self,j)
        try:
            (check_mobilize if j in E.MOBILIZE else check_kill)(before,snap(self));self.viol.n['ICON']+=1
        except Bad as e:self.viol.add(self,'ICON',str(e),before)

class Viol:                      # not a dict/list/set: FastGame.clone shares it
    def __init__(self):self.items=[];self.n=collections.Counter()
    def add(self,g,name,msg,before):
        self.items.append(dict(seed=g.seed,level=g.level,policy=g.policy,draw=g.draw,action=name,problem=msg,
                               plan=getattr(g,'last_plan',None) and {k:g.last_plan.get(k) for k in ('goal','box','op','sa')},
                               before=before and dict(board=before['board'],sab=before['sab'],cap=before['cap'],zipper=before['zipper'],avail=before['avail'])))

def games(n):
    tot=collections.Counter();items=[]
    for level in ('recruit','agent','veteran','legend','mastermind'):
        for seed in range(800000,800000+n):
            for pol in ('extraction','hunting','repair','adaptive','counter','mixed'):
                g=Checked(seed,level=level);g.policy=pol;g.run();tot.update(g.viol.n);tot['games']+=1;items+=g.viol.items
    return tot,items

def fuzz(n,first=900000):
    import fuzz_v1 as Z
    tot=collections.Counter();items=[]
    for i in range(n):
        seed=first+i;rnd=random.Random(seed);state=Z.random_state(rnd)
        level=Z.LEVELS[i%5]
        try:Z.make(V.Force136,seed,level,state)
        except AssertionError:continue
        tot['positions']+=1
        if rnd.random()<0.3:state['event']=rnd.choice([4,25])      # v1.1: exercise the Event step
        for ci in rnd.sample(range(9),3):
            for free in (Z.FREE[rnd.randrange(len(Z.FREE))],Z.FREE[0]):
                g=Z.make(Checked,seed,level,state);g.dqueue=[V.DECK[ci]]
                if len(free)==2:g.chosen={'J':[x for x in BOXES if x not in free][0]}   # Japan took the third box
                g.bot_turn(Z.offer(state,free));g.invariants();tot.update(g.viol.n);items+=g.viol.items
        for j in (1,13):
            g=Z.make(Checked,seed,level,state);g.icon(j);tot.update(g.viol.n);items+=g.viol.items
        # British Propaganda steps, one at a time
        g=Z.make(Checked,seed,level,state);b=g.board;before=snap(g)
        for rail in V.RAIL_LIST:
            if g.sabotage[rail]:
                sites=[s for s in g.rail_adj(rail) if POP[s] and not b[s]['terror'] and not b[s]['opposition']]
                if sites:b[g.opp_pick(sites)]['opposition']=True
        try:check_resources_phase(before,snap(g));tot['RESOURCES']+=1
        except Bad as e:g.viol.add(g,'RESOURCES',str(e),before);items+=g.viol.items
    return tot,items

def selftest():
    """Planted illegal actions: the checker must flag each one."""
    import fuzz_v1 as Z
    class RedNoCamp(Checked):                  # Train places MPAJA where there is no Camp or Cache
        def train_color(self,s):
            c=V.Force136.train_color(self,s);return 'red' if c is None else c
    class AlwaysHit(Checked):                  # Ambush moves the piece whatever the roll
        def die(self,tag,space=''):
            r=Checked.die(self,tag,space);return 6 if tag=='Ambush' and not self.preview and False else r
        def strike(self,*a,**k):
            self._cheat=True
            try:return Checked.strike(self,*a,**k)
            finally:self._cheat=False
        def cache_bonus(self,s):return V.Force136.cache_bonus(self,s)+(9 if getattr(self,'_cheat',False) and not self.preview else 0)
    class Gather3(Checked):                    # Gather from three spaces without J19
        def gather(self):
            if self.preview:return V.Force136.gather(self)
            before=snap(self);had=self.cap.get(19);self.cap[19]='U'
            try:r=V.Force136.gather(self)
            finally:
                if had is None:self.cap.pop(19,None)
                else:self.cap[19]=had
            try:check_gather(before,snap(self));self.viol.n['GATHER']+=1
            except Bad as e:self.viol.add(self,'GATHER',str(e),before)
            return r
    class SupplyAnywhere(Checked):             # Supply in a Province without Force 136, no J8
        def supply(self):
            had=self.cap.get(8)
            def fn(g):
                g.cap[8]='U'
                try:return V.Force136.supply(g)
                finally:
                    if had is None:g.cap.pop(8,None)
                    else:g.cap[8]=had
            return self._run('SUPPLY',fn,self)
    class RaidThree(Checked):                  # a third Raid below Zipper 20
        def raid(self):
            def fn(g):
                z=g.zipper;g.zipper=20
                try:return V.Force136.raid(g)
                finally:g.zipper=z
            return self._run('RAID',fn,self)
    class EventBoxAct(Checked):                # acts in the Event box
        def choose(self,free):
            p=V.Force136.choose(self,free)
            if 'Event' in free and p['op']!='PASS':p=dict(p,box='Event')
            return p
    class J8Converts(Checked):                 # Japanese J8: the Camp is converted although the roll failed
        def supply(self):
            def fn(g):
                n=V.Force136.supply(g)
                for sp in PROV:
                    if g.board[sp]['camp'] and g.board[sp]['force136'] and not g.board[sp]['cache'] and g.available('cache'):
                        g.board[sp]['camp']=False;g.board[sp]['cache']=True
                return n
            return self._run('SUPPLY',fn,self)
    class J27Keeps(Checked):                   # Japanese J27: Supply happens but the Opposition stays
        def supply(self):
            def fn(g):
                opp={sp:g.board[sp]['opposition'] for sp in ORDER};n=V.Force136.supply(g)
                for sp in ORDER:g.board[sp]['opposition']=opp[sp]
                return n
            return self._run('SUPPLY',fn,self)
    class Die1(object):                        # mix-in: every Supply roll is a 1
        def die(self,tag,space=''):
            if tag=='Supply' and not self.preview:
                if getattr(self,'_srolls',None) is not None:self._srolls[space].append(1)
                return 1
            return super().die(tag,space)
    def one_space(cls,cap,opposition):
        g=cls(5954001);g.board=E.new_board();b=g.board
        b['Kuala Lumpur'].update(troops=15,police=6,kempeitai=3)
        b['Perak'].update(force136=1,camp=True,red_u=1,opposition=opposition)
        g.cap.update(cap);g.invariants();g.supply();return g
    class J4PerMarker(Checked):                # J4 counted per marker instead of per space
        def j4_gain(self):return sum(v['force136'] for v in self.board.values() if v['camp'])
    g=J4PerMarker(5954005);g.board=E.new_board();b=g.board
    b['Kuala Lumpur'].update(troops=15,police=6,kempeitai=3)
    b['Perak'].update(force136=2,camp=True);b['Kedah'].update(force136=1,camp=True)
    g.event=4;g.chosen={'J':'Op & SA'};g.invariants();g.dqueue=[V.DECK[0]];g.bot_turn(['Limited','Event'])
    j4=('Event: J4 counted per marker, not per space',1,int(bool(g.viol.items)),'CAUGHT' if g.viol.items and g.last_plan['op']=='EVENT' else 'MISSED')
    rows=[j4];print(*j4,flush=True)
    g=one_space(type('M',(Die1,J8Converts),{}),{8:'S'},False);ctl=one_space(type('K',(Die1,Checked),{}),{8:'S'},False)
    ok=bool(g.viol.items) and not ctl.viol.items and not ctl.board['Perak']['cache']
    rows.append(('Supply: Japanese J8, converted on a roll of 1',1,int(bool(g.viol.items)),'CAUGHT' if ok else 'MISSED'));print(*rows[-1],flush=True)
    g=one_space(J27Keeps,{27:'S'},True);ctl=one_space(Checked,{27:'S'},True)
    ok=bool(g.viol.items) and not ctl.viol.items and not ctl.board['Perak']['opposition']
    rows.append(('Supply: Japanese J27, Opposition not removed',1,int(bool(g.viol.items)),'CAUGHT' if ok else 'MISSED'));print(*rows[-1],flush=True)
    g=Checked(3374504);g.board=E.new_board();b=g.board                 # nothing qualifies: the bot Passes
    b['Kuala Lumpur'].update(troops=15,police=6,kempeitai=3)
    for sp in ('Kedah','Perak','Negri Sembilan'):b[sp].update(force136=1,red_u=1)
    for sp in ORDER:
        if POP[sp]:b[sp]['intel']=0
    g.event=6;g.invariants();g.dqueue=[V.DECK[0]];g.bot_turn(['Event','Op & SA'])      # an invalid offer: Event is closed on J6
    ok=g.last_plan['op']=='PASS' and g.last_plan['box']=='Event' and bool(g.viol.items)
    rows.append(('Turn: Pass in the Event box on J6',1,int(bool(g.viol.items)),'CAUGHT' if ok else 'MISSED'));print(*rows[-1],flush=True)
    for name,cls in (('Train: MPAJA without Camp or Cache',RedNoCamp),('Ambush: success on a failing roll',AlwaysHit),
                     ('Gather: three spaces without J19',Gather3),('Supply: Province without Force 136',SupplyAnywhere),
                     ('Raid: three destinations below Zipper 20',RaidThree),('Turn: acting in the Event box',EventBoxAct)):
        found=0;tried=0
        for i in range(400):
            seed=910000+i;rnd=random.Random(seed);state=Z.random_state(rnd)
            if name.startswith('Gather'):state['cap'].pop(19,None)
            if name.startswith('Supply'):state['cap'].pop(8,None)
            if name.startswith('Raid') and state['zipper']==20:continue
            try:Z.make(V.Force136,seed,'agent',state)
            except AssertionError:continue
            for ci in (0,5,8):
                g=Z.make(cls,seed,'agent',state);g.dqueue=[V.DECK[ci]]
                try:g.bot_turn(list(Z.FREE[0]))
                except Exception:continue
                tried+=1;found+=bool(g.viol.items)
            if found>=5:break
        if name.startswith('Gather'):          # needs three Force 136 spaces with no shared neighbours: build one
            g=Gather3(910999);g.board=E.new_board();b=g.board
            b['Kuala Lumpur'].update(troops=15,police=3,kempeitai=3)
            for sp in ('Kedah','Trengganu','Johore'):b[sp].update(force136=1,camp=True,red_u=1)
            g.invariants();g.gather();tried+=1;found+=bool(g.viol.items)
        rows.append((name,tried,found,'CAUGHT' if found else 'MISSED'));print(*rows[-1],flush=True)
    ok=all(r[-1]=='CAUGHT' for r in rows)
    json.dump(rows,open('legality_selftest_results.json','w'),indent=1)
    print('all caught' if ok else 'SOME MISSED');return 0 if ok else 1

if __name__=='__main__':
    mode=sys.argv[1] if len(sys.argv)>1 else 'games'
    if mode=='selftest':sys.exit(selftest())
    n=int(sys.argv[2]) if len(sys.argv)>2 else (16 if mode=='games' else 2000)
    tot,items=games(n) if mode=='games' else fuzz(n)
    kinds=collections.Counter((x['action'],x['problem']) for x in items)
    print(mode,dict(tot),'violations',len(items))
    for k,v in kinds.most_common(30):print(v,k)
    json.dump(dict(mode=mode,checked=dict(tot),violations=len(items),kinds=[(k[0],k[1],v) for k,v in kinds.most_common()],examples=items[:25]),
              open(f'legality_{mode}_results.json','w'),indent=1,default=str)
    sys.exit(1 if items else 0)
