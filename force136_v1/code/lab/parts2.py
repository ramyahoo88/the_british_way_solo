import collections,sys
from engine import Game
import expert,rulebot
from scoreparts import patch
B=dict(full=['PLACE','INTEL','SUPPLY','STRIKE','TRAIN','CONTACT'],limited=['PLACE','STRIKE','TRAIN','CONTACT'],intel_min=2,first_limited=False)
class G(rulebot.RuleGame):P=B
pol=sys.argv[2]
for cls in [expert.ExpertGame,G]:
    patch(cls)
    agg=collections.defaultdict(lambda:collections.defaultdict(float));cnt=collections.Counter();jp=collections.Counter();bm=collections.Counter()
    for s in range(7000,7000+int(sys.argv[1])):
        g=cls(s);g.policy=pol;g.parts=[];g.run()
        for k,v in g.metrics.items():
            if k.startswith('japan_'):jp[k]+=v
            if k in('force136_eliminated','caches_assaulted','gather_reveals','ambush_attempts','caches_built','sabotages','raid_destinations'):bm[k]+=v
        for x in g.parts:
            cnt[x['c']]+=1
            for k,v in x.items():agg[x['c']][k]+=v
    print(cls.__name__,dict(jp),dict(bm))
    for c in sorted(agg):print(' camp',c,{k:round(v/cnt[c],2) for k,v in agg[c].items() if k!='c'})
