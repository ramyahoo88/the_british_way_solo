"""Narrated sample game: Force 136 (Agent) vs one Japan policy. Records every bot turn, Japanese move, icon,
Mandatory Event and Propaganda, with the position after each nonfinal Propaganda."""
import sys,json
from copy import deepcopy
import force136_v1 as F
from engine import ORDER,gs,cubes,POP,MOBILIZE,KILL,SEIZE
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
    def jp_apply(self,plan):
        if not self.preview:self.jp_plan=dict(op=plan['op'],sa=plan.get('sa'),timing=plan.get('timing'))
        return F.Force136.jp_apply(self,plan)
    def japan_turn(self,free):
        before=deepcopy(self.board);R=self.resistance;res=self.resources;caps=dict(self.cap)
        F.Force136.japan_turn(self,free)
        self.narr.append(dict(draw=self.draw,event=self.event,who='Japan',box=self.chosen.get('J'),R=(R,self.resistance),changes=diff(before,self.board),
                              res=(res,self.resources),plan=self.jp_plan,cap=[k for k in self.cap if k not in caps]))
    def icon(self,j):
        if self.preview:return F.Force136.icon(self,j)
        before=deepcopy(self.board);F.Force136.icon(self,j)
        name='Mobilize Population' if j in MOBILIZE else 'Kill Traitors' if j in KILL else 'Seize Supplies' if j in SEIZE else 'Food Shortage'
        self.narr.append(dict(draw=self.draw,event=j,icon=name,changes=diff(before,self.board)))
    def mandatory(self,j):
        if self.preview or j not in (6,9):return F.Force136.mandatory(self,j)
        before=deepcopy(self.board);R=self.resistance;n=len(self.narr)
        F.Force136.mandatory(self,j)
        self.narr.insert(n,dict(draw=self.draw,event=j,mandatory=True,R=(R,self.resistance),changes=[] if (j==9 and self.ended) else diff(before,self.board),ends=bool(j==9 and self.ended)))
    def propaganda(self,final=False):
        R=self.resistance;r=F.Force136.propaganda(self,final)
        self.narr.append(dict(draw=self.draw,prop=True,final=final,R=(R,self.resistance),zipper=self.zipper,
                              terms={k:r[k] for k in('intel','caches','majorities','resource_penalty','neutral_penalty','police_penalty','net_change')},
                              after=None if final else brief(self.board),sab=[x for x,n in self.sabotage.items() if n]))
        return r
seed=int(sys.argv[1]);pol=sys.argv[2]
g=Narr(seed);g.policy=pol;g.narr=[];g.quiet=True
start=brief(g.board)
r=g.run()
json.dump(dict(seed=seed,policy=pol,start=start,narr=g.narr,winner=r['winner'],R=r['final_resistance']),open(f'sample_{seed}_{pol}.json','w'),indent=1)
print(r['winner'],r['final_resistance'],len(g.narr))
for x in g.narr[:8]:print(json.dumps(x)[:600])
