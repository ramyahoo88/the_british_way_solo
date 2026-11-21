"""Turn-by-turn comparison of force136_v1 and the clean-room bot.
Superseded by verify_v1.py (full public state, Propaganda resets, final results, a scoring oracle,
forced-capability games and mutation tests). Kept, strengthened, for the review scripts that import it."""
import sys,os,json,collections
HERE=os.path.dirname(os.path.abspath(__file__))
for d in (os.path.join(HERE,'cleanroom'),os.path.join(os.path.dirname(HERE),'cleanroom')):
    if os.path.exists(os.path.join(d,'cleanroom.py')):sys.path.append(d);break
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
    if len(a)!=len(b):return 'length',len(a),len(b)
    for x,y in zip(a,b):
        if x['plan']!=y['plan'] or x.get('goal')!=y.get('goal') or x.get('card')!=y.get('card'):return 'plan',x,y
        if x['after']!=y['after'] or x['sab']!=y['sab']:return 'board',x,y
        if x.get('R')!=y.get('R'):return 'resistance',x,y
    return None
def result_div(ra,rb):
    keys=('winner','final_resistance','camps','force136','draws','ending')
    return None if all(ra[k]==rb[k] for k in keys) else ('result',{k:ra[k] for k in keys},{k:rb[k] for k in keys})
if __name__=='__main__':
    n=int(sys.argv[1]);levels=sys.argv[2].split(',')
    kinds=collections.Counter();examples=[]
    tot=0
    for l in levels:
        for s in range(20000,20000+n):
            for p in ['extraction','hunting','repair','adaptive','counter','mixed']:
                ra,ta=run(V.Force136,s,p,l);rb,tb=run(C.CleanForce136,s,p,l);tot+=1
                d=first_div(ta,tb) or result_div(ra,rb)
                if d:
                    k,x,y=d;key=(k,str(x)[:120],str(y)[:120]);kinds[key]+=1
                    if len(examples)<40:examples.append((s,p,l,k,x,y))
    print('games',tot,'diverging',sum(kinds.values()))
    for k,v in kinds.most_common(25):print(v,k)
    import pickle;pickle.dump(examples,open('cleancmp_examples.pkl','wb'))
