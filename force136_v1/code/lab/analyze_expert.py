import collections,json,sys
from expert import *
class TraceExpert(ExpertGame):
    def bot_turn(self,free):
        b=self.board
        feat=dict(campaign=self.campaign,regular=self.regular_seen,free=''.join(x[0] for x in free),
          f136=self.count('force136'),cache_av=self.available('cache'),caches=self.count('cache'),
          supply_now=sum(1 for s in PROV if b[s]['camp'] and b[s]['force136'] and not b[s]['cache']),
          gather=len(set(t for s in ORDER if b[s]['force136'] for t in self.gather_targets(s))),
          R=self.resistance,res=self.resources,event=self.event)
        before=dict(self.metrics)
        ExpertGame.bot_turn(self,free)
        k=[k for k in self.metrics if k.startswith('b_') and self.metrics[k]!=before.get(k,0)][0]
        feat['choice']=k[2:]
        self.trace.append(feat)
rows=[];res=[]
for s in range(6000,6000+int(sys.argv[1])):
    for p in ['extraction','hunting','repair','adaptive']:
        g=TraceExpert(s);g.policy=p;g.trace=[];r=g.run();res.append(r)
        for t in g.trace:t['policy']=p;t['win']=r['winner'];rows.append(t)
json.dump(rows,open('expert_trace.json','w'))
c=collections.Counter(r['winner'] for r in res);print(c,len(res),round(sum(r['final_resistance'] for r in res)/len(res),2))
for p in ['extraction','hunting','repair','adaptive']:
    rs=[r for r in res if r['policy']==p];print(p,collections.Counter(r['winner'] for r in rs),round(sum(r['final_resistance'] for r in rs)/len(rs),2))
