import sys,collections
from rulebot import RuleGame
from expert import ExpertGame,british_candidates,apply_british,british_value
from exp4 import variants
def name(p):
    return (p.get('op') or p['kind'])+('+'+p['sa'] if p.get('sa') else '')+('/'+p['box'][0])
class D(RuleGame):
    P=variants['A'];weights=None
    def bot_turn(self,free):
        # expert choice
        best=None
        for plan in british_candidates(self,free):
            p=self.clone()
            try:apply_british(p,plan)
            except Exception:continue
            tempo=0.8 if plan['box']=='Limited' else 0.3 if plan['box']=='Event' else 0
            val=british_value(p)+tempo
            if best is None or val>best[0]:best=(val,plan)
        before=dict(self.metrics)
        RuleGame.bot_turn(self,free)
        k=[k for k in self.metrics if k.startswith('b_') and self.metrics[k]!=before.get(k,0)][0][2:]
        full='Op & SA' in free
        PAIRS[(full,k,name(best[1]))]+=1
PAIRS=collections.Counter()
for s in range(7000,7000+int(sys.argv[1])):
    for pol in ['extraction','hunting','repair','adaptive','counter','mixed']:
        g=D(s);g.policy=pol;g.run()
tot=collections.Counter()
for (full,r,e),n in PAIRS.items():tot[(full,r)]+=n
for full in [True,False]:
    print('FULL' if full else 'LIMITED/EVENT')
    for (f,r,e),n in sorted(PAIRS.items(),key=lambda x:-x[1]):
        if f==full and n>=8:print(f'  rule {r:16s} expert {e:20s} {n}  ({n/tot[(f,r)]:.0%})')
