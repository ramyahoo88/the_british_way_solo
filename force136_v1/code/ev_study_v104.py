"""Event study on the v1.0.4 bot (corrected Japan), which led to v1.1's Event step (J4 and J25 as second player).

The baseline is v1.0.4: the printed v1.1 bot with its Event step switched off (class V104), which is v1.0.4
move for move.

For one Event card J, the variant bot takes the Event box (and executes the British side) when that card is
revealed and the Event box is free:

  use   : when its British side would do something, whether Force 136 is first or second to act
  deny  : as 'use', and also as first player when the British side would do nothing (taking the box
          then only keeps the Japanese side away from Japan)
  second: only as second player (Japan has already acted), when its British side would do something

The bot still draws its Directive card that turn (and discards it), so its Directive deck stays in step
with the baseline. Games are paired with the unchanged bot on the same seed and Japan policy; they are
identical until card J is revealed. Each decision is recorded: whether Force 136 was first or second,
what it would otherwise have done, and whether the British side would have done something.

usage: python3 ev_study_v104.py screen [seeds] [first_seed]      every Event card, both variants
       python3 ev_study_v104.py confirm CARD:MODE[,..] [seeds] [first_seed]
"""
import sys,os,json,random,collections
from multiprocessing import Pool
HERE=os.path.dirname(os.path.abspath(__file__));sys.path.insert(0,HERE)
import force136_v1 as F
from engine import BOXES,CAPS
from copy import deepcopy
POLS=('extraction','hunting','repair','adaptive','counter','mixed')
CARDS=[j for j in range(1,33) if j not in (6,9)]

def state(g):
    return (deepcopy(g.board),dict(g.sabotage),g.resistance,g.resources,g.zipper,dict(g.cap),g.lost_k,g.lost_cache,
            g.away_f,g.away_troops,tuple(sorted(g.removed_intel)))

class V104(F.Force136):
    """v1.0.4: the v1.1 bot without its Event step."""
    def take_event(self,free):return False

class EvBot(V104):
    J=None;MODE='use'
    def useful(self):
        p=self.clone();before=state(p);p.execute_event(self.event,'U');return state(p)!=before
    def bot_turn(self,free):
        if self.event!=self.J or 'Event' not in free or self.event in (6,9):
            return V104.bot_turn(self,free)
        first='J' not in self.chosen
        u=self.useful()
        take=(u and not first) if self.MODE=='second' else (u or (self.MODE=='deny' and first))
        # what the unchanged bot would do here (a preview, so dice and chits are not touched)
        q=self.clone();q.draw_directive();normal=q.choose(free)
        self.ev_info=dict(first=first,useful=u,take=take,free=list(free),normal=(normal['box'],normal['op'],normal['goal']))
        if not take:return V104.bot_turn(self,free)
        self.card=None;self.draw_directive()                 # draw and discard, as on any turn
        self.chosen['B']='Event';self.execute_event(self.event,'U');self.cleanup()
        self.last_plan=dict(box='Event',op='EVENT',goal='EVENT',sa=None)
        self.inc('g_EVENT');self.inc('o_E:EVENT')

def deck(seed):
    return set(F.Force136(seed).deck)

def one(args):
    seed,pol,J,mode=args
    if J is None:
        g=V104(seed)
    else:
        cls=type('B',(EvBot,),{'J':J,'MODE':mode});g=cls(seed)
    g.policy=pol;r=g.run()
    return (seed,pol,J,mode,r['winner']=='Force 136',r['final_resistance'],getattr(g,'ev_info',None))

def subset(r,pos):
    i=r[6]
    if pos=='all':return True
    if pos=='first':return i['first']
    if pos=='second':return not i['first']
    if pos=='second_lim':return not i['first'] and i['normal'][0]=='Limited'     # Japan took Op & SA: Event instead of a Limited Op
    if pos=='second_full':return not i['first'] and i['normal'][0]=='Op & SA'    # Japan took Limited: Event instead of Op & SA
def summarize(rows,base,key):
    """Paired effect over the games where the decision point arose, split by position."""
    out={}
    for pos in ('first','second','second_lim','second_full','all'):
        rs=[r for r in rows if r[6] and subset(r,pos) and r[6]['take']]
        if not rs:continue
        d=[(r[0],r[4]-base[(r[0],r[1])][0],r[5]-base[(r[0],r[1])][1]) for r in rs]
        by=collections.defaultdict(lambda:[0,0,0])
        for s,dw,dr in d:by[s][0]+=dw;by[s][1]+=dr;by[s][2]+=1
        seeds=list(by);rnd=random.Random(7);bs=[]
        for _ in range(2000):
            ss=rnd.choices(seeds,k=len(seeds));n=sum(by[s][2] for s in ss)
            bs.append(sum(by[s][0] for s in ss)/n)
        bs.sort()
        out[pos]=dict(n=len(d),dwin=round(100*sum(x[1] for x in d)/len(d),2),ci=(round(100*bs[50],2),round(100*bs[1950],2)),
                      dR=round(sum(x[2] for x in d)/len(d),3))
    return out

if __name__=='__main__':
    what=sys.argv[1]
    if what=='screen':
        n=int(sys.argv[2]) if len(sys.argv)>2 else 256;first=int(sys.argv[3]) if len(sys.argv)>3 else 410000
        specs=[(j,m) for j in CARDS for m in (('use',) if j in CAPS else ('use','deny'))]   # a capability's British side always does something
    else:
        specs=[(int(x.split(':')[0]),x.split(':')[1]) for x in sys.argv[2].split(',')]
        n=int(sys.argv[3]) if len(sys.argv)>3 else 1000;first=int(sys.argv[4]) if len(sys.argv)>4 else 420000
    seeds=list(range(first,first+n));decks={s:deck(s) for s in seeds}
    with Pool(2) as pool:
        base_rows=pool.map(one,[(s,p,None,None) for s in seeds for p in POLS],chunksize=16)
        base={(r[0],r[1]):(r[4],r[5]) for r in base_rows}
        print('base',len(base_rows),round(100*sum(r[4] for r in base_rows)/len(base_rows),2),flush=True)
        results={}
        for j,m in specs:
            jobs=[(s,p,j,m) for s in seeds if j in decks[s] for p in POLS]
            rows=pool.map(one,jobs,chunksize=16)
            dec=[r for r in rows if r[6]]
            info=dict(decisions=len(dec),first=sum(r[6]['first'] for r in dec),useful=sum(r[6]['useful'] for r in dec),
                      taken=sum(r[6]['take'] for r in dec),
                      normal=collections.Counter(f"{'F' if r[6]['first'] else 'S'}:{r[6]['normal'][0]}:{r[6]['normal'][1]}" for r in dec if r[6]['take']).most_common(4))
            res=summarize(rows,base,(j,m))
            results[f'{j}:{m}']=dict(info=info,effect=res,rows=[(r[0],r[1],r[4],r[5],r[6]) for r in rows if r[6]])
            print(j,m,json.dumps(info),json.dumps(res),flush=True)
    results['_base']=[(r[0],r[1],r[4],r[5]) for r in base_rows]
    json.dump(results,open(f'ev_{what}_{first}_{n}.json','w'))
