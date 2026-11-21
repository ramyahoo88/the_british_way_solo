import sys,time
from rulebot import *
from expert import ExpertGame
B=dict(full=['PLACE','INTEL','SUPPLY','STRIKE','TRAIN','CONTACT'],limited=['PLACE','STRIKE','TRAIN','CONTACT'],intel_min=2,first_limited=False)
class G(RuleGame):P=B
n=int(sys.argv[1])
for cls,name in [(ExpertGame,'expert'),(G,'rule')]:
    t=time.time();s,res=evaluate(cls,range(7000,7000+n),policies=('counter','mixed'))
    for p in ['counter','mixed']:
        rs=[r for r in res if r['policy']==p];print(name,p,sum(r['winner']=='Force 136' for r in rs)/len(rs),round(sum(r['final_resistance'] for r in rs)/len(rs),2))
    print(round(time.time()-t,1),flush=True)
