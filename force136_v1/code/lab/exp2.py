import sys,json,time
from rulebot import *
B=dict(full=['INTEL','SUPPLY','STRIKE','TRAIN','CONTACT'],limited=['PLACE','STRIKE','TRAIN','CONTACT'],intel_min=2,first_limited=False)
def V(**k):d=dict(B);d.update(k);return d
variants={
 'B':B,
 'intel1':V(intel_min=1),
 'intel3':V(intel_min=3),
 'strike_full2':V(full=['INTEL','STRIKE','SUPPLY','TRAIN','CONTACT']),
 'place_full':V(full=['PLACE','INTEL','SUPPLY','STRIKE','TRAIN','CONTACT']),
 'first_lim':V(first_limited=True),
 'rail_lim':V(limited=['PLACE','STRIKE','RAIL','TRAIN','CONTACT']),
 'raid_first':V(strike_sa=['RAID','GATHER']),
}
n=int(sys.argv[1]);start=int(sys.argv[2]);names=sys.argv[3].split(',') if len(sys.argv)>3 else list(variants)
for name in names:
    P=variants[name];t=time.time()
    class G(RuleGame):pass
    G.P=P
    s,res=evaluate(G,range(start,start+n));print(name,s,round(time.time()-t,1),flush=True)
