import sys,json,time
from rulebot import *
variants={
 'base':dict(full=['INTEL','SUPPLY','STRIKE','TRAIN','CONTACT'],limited=['TRAIN','CONTACT'],intel_min=2,first_limited=False),
 'place_lim':dict(full=['INTEL','SUPPLY','STRIKE','TRAIN','CONTACT'],limited=['PLACE','TRAIN','STRIKE','CONTACT'],intel_min=2,first_limited=False),
 'place_both':dict(full=['INTEL','SUPPLY','STRIKE','TRAIN','CONTACT'],limited=['PLACE','TRAIN','STRIKE','CONTACT'],intel_min=2,first_limited=False,full_place=True),
 'strike_lim':dict(full=['INTEL','SUPPLY','STRIKE','TRAIN','CONTACT'],limited=['PLACE','STRIKE','TRAIN','CONTACT'],intel_min=2,first_limited=False),
 'supply_first':dict(full=['SUPPLY','INTEL','STRIKE','TRAIN','CONTACT'],limited=['PLACE','TRAIN','STRIKE','CONTACT'],intel_min=2,first_limited=False),
}
n=int(sys.argv[1]);names=sys.argv[2].split(',') if len(sys.argv)>2 else list(variants)
for name in names:
    P=variants[name];t=time.time()
    class G(RuleGame):pass
    G.P=P
    s,res=evaluate(G,range(6000,6000+n));print(name,s,round(time.time()-t,1),flush=True)
