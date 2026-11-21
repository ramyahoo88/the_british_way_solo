"""Narrated sample game: Force 136 v1.0 (Agent) vs the 'adaptive' Japan policy."""
import sys,json
from copy import deepcopy
import force136_v1 as F
from engine import ORDER,gs,cubes,POP
def brief(b):
    out=[]
    for s in ORDER:
        v=b[s];bits=[]
        if v['troops']:bits.append(f"{v['troops']}T")
        if v['police']:bits.append(f"{v['police']}P")
        if v['kempeitai']:bits.append(f"{v['kempeitai']}K")
        if v['red_u'] or v['red_a']:bits.append(f"red {v['red_u']}u/{v['red_a']}a")
        if v['blue_u'] or v['blue_a']:bits.append(f"blue {v['blue_u']}u/{v['blue_a']}a")
        if v['force136']:bits.append('F136')
        if v['camp']:bits.append('Camp')
        if v['cache']:bits.append('Cache')
        if v['opposition']:bits.append('Opp')
        if v['intel'] is not None:bits.append(f"Intel {v['intel']}")
        if bits:out.append(f"{s}: "+', '.join(bits))
    return out
def diff(a,b):
    ch=[]
    for s in ORDER:
        if a[s]!=b[s]:
            d={k:(a[s][k],b[s][k]) for k in a[s] if a[s][k]!=b[s][k] and k!='population'}
            ch.append(f"{s}: "+', '.join(f"{k} {x}->{y}" for k,(x,y) in d.items()))
    return ch
class Narr(F.Force136):
    def bot_turn(self,free):
        before=deepcopy(self.board);R=self.resistance
        F.Force136.bot_turn(self,free)
        p=self.last_plan;d=self.directive
        self.narr.append(dict(draw=self.draw,event=self.event,campaign=self.campaign,free=free,card=f"{d['id']} {d['name']}: {' > '.join(d['goals'])}; Limited {d['limited_first']} first",
            goal=p['goal'],box=p['box'],op=p['op'],sa=p.get('sa'),R=(R,self.resistance),changes=diff(before,self.board),sab=[r for r,n in self.sabotage.items() if n]))
    def japan_turn(self,free):
        before=deepcopy(self.board);R=self.resistance
        F.Force136.japan_turn(self,free)
        self.narr.append(dict(draw=self.draw,event=self.event,who='Japan',box=self.chosen.get('J'),R=(R,self.resistance),changes=diff(before,self.board),res=self.resources))
    def propaganda(self,final=False):
        R=self.resistance;r=F.Force136.propaganda(self,final)
        self.narr.append(dict(draw=self.draw,prop=True,final=final,R=(R,self.resistance),terms={k:r[k] for k in('intel','caches','majorities','resource_penalty','neutral_penalty','police_penalty','net_change')}))
        return r
seed=int(sys.argv[1]);pol=sys.argv[2]
g=Narr(seed);g.policy=pol;g.narr=[];g.quiet=True
start=brief(g.board)
r=g.run()
json.dump(dict(seed=seed,policy=pol,start=start,narr=g.narr,winner=r['winner'],R=r['final_resistance']),open(f'sample_{seed}_{pol}.json','w'),indent=1)
print(r['winner'],r['final_resistance'],len(g.narr))
for x in g.narr[:8]:print(json.dumps(x)[:600])
