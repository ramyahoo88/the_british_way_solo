"""Sensitivity: Japan removes an Underground guerrilla first (Food Shortage icon, J11/J18 Japanese sides),
instead of the engine's Active-first choice. Assault still removes only Active pieces."""
import sys,os,csv,gzip,random
CODE=os.environ['F136_CODE']   # force136_v1/code of a checkout at commit 338cb0d
sys.path.insert(0,CODE)
from multiprocessing import Pool
import force136_v1 as V
from engine import red,blue
POLS=('extraction','hunting','repair','adaptive','counter','mixed')
class UFirst(V.Force136):
    def lose_guerrilla(self,s,british=True,forced_color=None,active_only=False):
        if british or active_only:return V.Force136.lose_guerrilla(self,s,british,forced_color,active_only)
        v=self.board[s];fields=[k for k in ['red_u','blue_u','red_a','blue_a'] if v[k] and (not forced_color or k.startswith(forced_color))]
        if not fields:return None
        k=min(fields,key=lambda k:(not k.endswith('_u'),-(red(v) if k.startswith('red') else blue(v)),not k.startswith('red')))
        v[k]-=1;return k
def one(a):
    seed,pol=a;g=UFirst(seed);g.policy=pol;r=g.run();return (seed,pol,r['winner'],r['final_resistance'])
if __name__=='__main__':
    n=int(sys.argv[1])
    with Pool(2) as p:rows=p.map(one,[(s,q) for s in range(n) for q in POLS],chunksize=16)
    base={(int(r['seed']),r['policy']):r for r in csv.DictReader(gzip.open(os.path.join(CODE,'results','results_fresh_v101.csv.gz'),'rt')) if r['level']=='agent' and int(r['seed'])<n}
    w=sum(r[2]=='Force 136' for r in rows)/len(rows);wb=sum(base[(r[0],r[1])]['winner']=='Force 136' for r in rows)/len(rows)
    by={}
    for r in rows:by[r[0]]=by.get(r[0],0)+(r[2]=='Force 136')-(base[(r[0],r[1])]['winner']=='Force 136')
    rnd=random.Random(1);ks=list(by.values());bs=sorted(sum(rnd.choices(ks,k=len(ks)))/(6*len(ks)) for _ in range(4000))
    print('variant',round(w,4),'baseline',round(wb,4),'diff',round(w-wb,4),'CI',round(bs[100],4),round(bs[3900],4))
    for q in POLS:
        rs=[r for r in rows if r[1]==q];print(q,round(sum(r[2]=='Force 136' for r in rs)/len(rs),3),round(sum(base[(r[0],r[1])]['winner']=='Force 136' for r in rs)/len(rs),3))
