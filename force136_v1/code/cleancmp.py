import sys,json,collections
import os;sys.path.append(os.path.join(os.path.dirname(os.path.abspath(__file__)),'cleanroom'))
from copy import deepcopy
import force136_v1 as V
import cleanroom as C
def run(cls,seed,pol,level):
    g=cls(seed,level=level);g.policy=pol;tr=[]
    orig=cls.bot_turn
    def bt(self,free):
        before=deepcopy(self.board)
        orig(self,free);p=self.last_plan
        tr.append(dict(draw=self.draw,free=list(free),plan=(p.get('box'),p.get('op'),p.get('sa')),goal=p.get('goal'),before=before,after=deepcopy(self.board),sab=dict(self.sabotage),R=self.resistance,card=self.directive['id']))
    g.bot_turn=bt.__get__(g)
    r=g.run();return r,tr
def first_div(a,b):
    for x,y in zip(a,b):
        if x['plan']!=y['plan']:return 'plan',x,y
        if x['after']!=y['after'] or x['sab']!=y['sab']:return 'board',x,y
    return None
if __name__=='__main__':
    n=int(sys.argv[1]);levels=sys.argv[2].split(',')
    kinds=collections.Counter();examples=[]
    tot=0
    for l in levels:
        for s in range(20000,20000+n):
            for p in ['extraction','hunting','repair','adaptive','counter','mixed']:
                ra,ta=run(V.Force136,s,p,l);rb,tb=run(C.CleanForce136,s,p,l);tot+=1
                d=first_div(ta,tb)
                if d:
                    k,x,y=d;key=(k,x['plan'],y['plan'],x['goal'],y['goal']);kinds[key]+=1
                    if len(examples)<40:examples.append((s,p,l,k,x,y))
    print('games',tot,'diverging',sum(kinds.values()))
    for k,v in kinds.most_common(25):print(v,k)
    import pickle;pickle.dump(examples,open('cleancmp_examples.pkl','wb'))
