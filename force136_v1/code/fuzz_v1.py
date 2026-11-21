"""Differential fuzzing of the two Force 136 implementations on random legal positions.

verify_v1.py compares the printed-rules bot (force136_v1) and the clean-room bot only on positions
that the computer Japan policies happen to reach. This script builds random positions directly
(any legal mix of pieces, markers, tracks and capability sides, including stacked Force 136 markers,
empty pools and British capability sides) and makes both bots act from each one:

  - a Force 136 turn with every Directive card and each set of free boxes,
  - a nonfinal Propaganda round (British Resources, Supply, Redeploy, J25 return),
  - a Mobilize Population icon and a Kill Traitors icon,
  - a Japanese Extract and a Japanese Construct (for the British sides of J15 and J12).

After each action the full public state of both bots must match. Any difference is a place where one
implementation does not follow the printed rules (or the rules can be read two ways).

usage: python3 fuzz_v1.py [positions] [first_seed]      (default 2000 positions from seed 700000)
Exit status 1 if any difference or invariant failure is found.
"""
import sys,os,random,json,collections
from copy import deepcopy
HERE=os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0,HERE)
for d in (os.path.join(HERE,'cleanroom'),os.path.join(os.path.dirname(HERE),'cleanroom')):
    if os.path.exists(os.path.join(d,'cleanroom.py')):sys.path.append(d);break
import engine as E
from engine import ORDER,PROV,POP,EDGES,CAPS,BOXES
import force136_v1 as V
import cleanroom as C
import clean_base

STATE=('board','sabotage','cap','resistance','resources','zipper','track_cache','lost_cache','lost_k',
       'away_troops','away_f','removed_intel','campaign','draw','event','first','chosen','regular_seen')
LEVELS=('recruit','agent','veteran','legend','mastermind')
FREE=(['Limited','Event','Op & SA'],['Limited','Event'],['Event','Op & SA'],['Limited','Op & SA'],['Limited'],['Op & SA'])

def random_state(rnd):
    """A random position that satisfies the engine's piece-count invariants."""
    b=E.new_board()
    hot=rnd.random()                                   # how crowded the map is
    def spread(n,field,spaces,clump=0.5):
        spaces=list(spaces)
        for _ in range(n):
            s=rnd.choice(spaces[:max(1,int(len(spaces)*clump))]) if rnd.random()<0.5 else rnd.choice(spaces)
            b[s][field]+=1
    order=list(ORDER);rnd.shuffle(order)
    away_troops=rnd.choice([0,0,0,3])
    spread(15-away_troops,'troops',order)
    spread(rnd.randint(0,6),'police',[s for s in order if POP[s]])
    lost_k=rnd.choice([0,0,0,1])
    spread(3-lost_k,'kempeitai',order)
    for colour,total in (('red',10),('blue',4)):
        n=rnd.choice([total,total,rnd.randint(0,total)]) if hot>0.4 else rnd.randint(0,total)
        for _ in range(n):
            s=rnd.choice(order[:6]) if rnd.random()<0.7 else rnd.choice(order)
            b[s][colour+('_u' if rnd.random()<0.55 else '_a')]+=1
    away_f=rnd.choice([0,0,0,0,1])
    nf=3-away_f if rnd.random()<0.7 else rnd.randint(0,3-away_f)   # usually no marker Available, so every goal is reached
    for _ in range(nf):
        r=rnd.random()
        s=rnd.choice(PROV) if r<0.9 else rnd.choice(ORDER)
        if r>0.75 and any(b[x]['force136'] for x in ORDER):          # sometimes stack
            s=rnd.choice([x for x in ORDER if b[x]['force136']])
        b[s]['force136']+=1
    for s in rnd.sample(PROV,rnd.randint(0,4)):b[s]['camp']=True
    zipper=rnd.choice([0,0,6,12,18,20]);track=sum(t>zipper for t in (6,18))
    lost_cache=rnd.choice([0,0,0,1])
    ncache=rnd.randint(0,5-lost_cache-track)
    for s in rnd.sample([s for s in ORDER if POP[s]],ncache):
        b[s]['cache']=True
        if rnd.random()<0.6 and sum(b[x]['red_u']+b[x]['red_a'] for x in ORDER)<=8:   # guarded Caches, so Raid has sources
            b[s]['red_u']+=1;b[s]['red_'+rnd.choice('ua')]+=1
    for s in ORDER:
        if POP[s]:
            b[s]['opposition']=rnd.random()<0.35
            b[s]['terror']=1 if rnd.random()<0.15 else 0
    for s in rnd.sample(PROV,rnd.randint(0,3)):b[s]['new_village']=True
    removed=set()
    for s in ORDER:
        if POP[s]:
            r=rnd.random()
            if r<0.3:b[s]['intel']=rnd.choice([0,1,2])
            elif r<0.35:removed.add(s)
    sab={r:(1 if rnd.random()<0.3 else 0) for r in EDGES}
    cap={}
    for c in CAPS:
        r=rnd.random()
        if r<0.25:cap[c]='U'
        elif r<0.5:cap[c]='S'
    return dict(board=b,sabotage=sab,cap=cap,resistance=rnd.randint(0,20),resources=rnd.randint(0,20),zipper=zipper,
                track_cache=track,lost_cache=lost_cache,lost_k=lost_k,away_troops=away_troops,away_f=away_f,
                removed_intel=removed,campaign=rnd.choice([1,2]),draw=rnd.randint(1,14),event=rnd.randint(1,32),
                first='B',chosen={},regular_seen=rnd.randint(0,5))

def make(cls,seed,level,state):
    g=cls(seed,level=level)
    for k,v in state.items():setattr(g,k,deepcopy(v))
    g.invariants()
    return g

def public(g):
    return (tuple((s,tuple(sorted(v.items()))) for s,v in sorted(g.board.items())),tuple(sorted(g.sabotage.items())),
            g.resistance,g.resources,g.zipper,g.track_cache,g.lost_cache,g.away_f,tuple(sorted(g.removed_intel)),
            tuple(sorted(g.chosen.items())))

def describe(a,b):
    out=[]
    for s in ORDER:
        d={k:(a.board[s][k],b.board[s][k]) for k in a.board[s] if a.board[s][k]!=b.board[s][k]}
        if d:out.append((s,d))
    for k in ('sabotage','resistance','resources','zipper','away_f','chosen'):
        if getattr(a,k)!=getattr(b,k):out.append((k,getattr(a,k),getattr(b,k)))
    return out

def run(n,first_seed,stop_after=40):
    rnd_master=random.Random(first_seed)
    found=[];counts=collections.Counter();kinds=collections.Counter()
    for i in range(n):
        seed=first_seed+i;rnd=random.Random(seed)
        try:state=random_state(rnd)
        except Exception as e:counts['generator_error']+=1;continue
        level=LEVELS[i%5]
        try:make(V.Force136,seed,level,state)
        except AssertionError:counts['illegal_position_skipped']+=1;continue
        counts['positions']+=1
        cards=rnd.sample(range(9),3)
        actions=[('turn',ci,f) for ci in cards for f in (FREE[rnd.randrange(len(FREE))],FREE[0])]
        actions+=[('propaganda',),('icon',1),('icon',13),('extract',),('construct',)]
        for act in actions:
            a=make(V.Force136,seed,level,state);b=make(C.CleanForce136,seed,level,state)
            try:
                if act[0]=='turn':
                    a.dqueue=[V.DECK[act[1]]];b.dqueue=[clean_base.CARDS[act[1]]]
                    a.bot_turn(list(act[2]));b.bot_turn(list(act[2]))
                    pa=a.last_plan;pb=b.last_plan
                    plan_same=all(pa.get(k)==pb.get(k) for k in ('goal','box','op','sa'))
                elif act[0]=='propaganda':
                    a.propaganda(False);b.propaganda(False);plan_same=True
                elif act[0]=='extract':                          # Japanese Extract: British J15 places guerrillas
                    a.extract();b.extract();plan_same=True
                elif act[0]=='construct':                        # Japanese Construct: British J12 places Opposition
                    a.construct();b.construct();plan_same=True
                else:
                    a.icon(act[1]);b.icon(act[1]);plan_same=True
                a.invariants();b.invariants()
            except Exception as e:
                counts['exception']+=1;kinds[('exception',act[0],type(e).__name__)]+=1
                if len(found)<stop_after:found.append(dict(seed=seed,level=level,action=act,error=repr(e)[:200]))
                continue
            counts['actions']+=1
            if not plan_same or public(a)!=public(b):
                counts['differences']+=1
                key=(act[0],) if act[0]!='turn' else ('turn',(pa.get('goal'),pa.get('op'),pa.get('sa')),(pb.get('goal'),pb.get('op'),pb.get('sa')))
                kinds[key]+=1
                if len(found)<stop_after:
                    found.append(dict(seed=seed,level=level,action=act,
                                      plans=(None if act[0]!='turn' else ({k:pa.get(k) for k in ('goal','box','op','sa')},{k:pb.get(k) for k in ('goal','box','op','sa')})),
                                      diff=describe(a,b)))
    return counts,kinds,found

if __name__=='__main__':
    n=int(sys.argv[1]) if len(sys.argv)>1 else 2000
    first=int(sys.argv[2]) if len(sys.argv)>2 else 700000
    counts,kinds,found=run(n,first)
    print(dict(counts))
    for k,v in kinds.most_common(30):print(v,k)
    json.dump(dict(counts=dict(counts),kinds=[(str(k),v) for k,v in kinds.most_common()],examples=found),open('fuzz_results.json','w'),indent=1,default=str)
    sys.exit(1 if counts['differences'] or counts['exception'] else 0)
