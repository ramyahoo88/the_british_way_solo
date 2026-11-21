import collections,sys
from engine import Game
import expert,rulebot
def patch(cls):
    orig=cls.score_only
    def score_only(self,final=False):
        r=orig(self,final)
        if not self.preview:
            self.parts.append(dict(c=self.campaign,intel=r['intel'],caches=r['caches'],maj=r['majorities'],res=r['resource_penalty'],neut=r['neutral_penalty'],pol=r['police_penalty'],net=r['net_change'],Rb=r['resistance_before'],F=self.count('force136'),clash=r['clashes']))
        return r
    cls.score_only=score_only
for cls in [expert.ExpertGame,rulebot.RuleGame]:
    patch(cls)
    agg=collections.defaultdict(lambda:collections.defaultdict(float));cnt=collections.Counter()
    for s in range(6000,6000+int(sys.argv[1])):
        for p in ['extraction','hunting','repair','adaptive']:
            g=cls(s);g.policy=p;g.parts=[];g.run()
            for x in g.parts:
                cnt[x['c']]+=1
                for k,v in x.items():agg[x['c']][k]+=v
    print(cls.__name__)
    for c in sorted(agg):print(' camp',c,{k:round(v/cnt[c],2) for k,v in agg[c].items() if k!='c'})
