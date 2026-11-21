"""'look' Japanese policy: one-ply lookahead against the actual Force 136 bot.
When Japan acts first on a card, its top candidates (by the adaptive value) are
scored after simulating Force 136's reply with sampled Directive cards."""
import random
import force136_v1 as F
from engine import Game,BOXES,stable
class LookMixin:
    K=8;SAMPLES=3
    BASE={'look':'adaptive','lookc':'counter','lookm':'mixed'}
    def japan_turn(self,free):
        me=self.policy
        if me not in self.BASE:return super().japan_turn(free)
        if 'B' in self.chosen:
            self.policy=self.BASE[me]
            try:return super().japan_turn(free)
            finally:self.policy=me
        self.policy=self.BASE[me]
        try:
            cands=[]
            for box in free:
                if box=='Event':
                    if self.event not in [6,9]:cands.append(dict(op='EVENT',box=box,sa=None))
                    continue
                for op in ['DEPLOY','CONSTRUCT','ASSAULT','SWEEP']:
                    special=[None] if box=='Limited' else ['EXTRACT'] if op=='DEPLOY' else [None,'REPRISAL','ELIMINATE']
                    for sa in special:
                        for strength in ([2,5,0] if op=='SWEEP' else [3]):
                            for timing in (['before','after'] if sa=='REPRISAL' else ['after']):
                                cands.append(dict(op=op,box=box,sa=sa,strength=strength,timing=timing))
            for c in cands:
                p=self.clone();p.jp_apply(c);c['_v1']=p.jp_value()+(1.0 if c['box']=='Limited' else .3 if c['box']=='Event' else 0)
            cands.sort(key=lambda c:-c['_v1'])
            best=None
            rng=random.Random(stable(self.seed,'look',self.draw))
            for c in cands[:self.K]:
                tot=0
                for k in range(self.SAMPLES):
                    p=self.clone();p.jp_apply(c);p.chosen=dict(self.chosen);p.chosen['J']=c['box']
                    bfree=[b for b in BOXES if b not in p.chosen.values() and not(self.event in [6,9] and b=='Event')]
                    p.dqueue=[rng.choice(F.DECK)]
                    p.bot_turn(bfree)          # a failing preview stops the run (it used to be skipped silently)
                    tot+=p.jp_value()
                v=tot/self.SAMPLES+(1.0 if c['box']=='Limited' else .3 if c['box']=='Event' else 0)
                if best is None or v>best[0]:best=(v,c)
            plan=best[1]
            self.chosen['J']=plan['box'];self.jp_apply(plan)
        finally:self.policy=me

class LookGame(LookMixin,F.Force136):pass
