import sys,os,csv,gzip,random
CODE=os.environ['F136_CODE']   # force136_v1/code of a checkout at commit 338cb0d
sys.path.insert(0,CODE);sys.path.insert(0,os.path.dirname(os.path.abspath(__file__)))
from multiprocessing import Pool
import jp_loss,jp_redeploy
POLS=jp_loss.POLS
class Both(jp_redeploy.KeepK):
    lose_guerrilla=jp_loss.UFirst.lose_guerrilla
def one(a):
    seed,pol,level=a;g=Both(seed,level=level);g.policy=pol;r=g.run();return (seed,pol,level,r['winner'],r['final_resistance'])
if __name__=='__main__':
    n=int(sys.argv[1]);levels=sys.argv[2].split(',')
    with Pool(2) as p:rows=p.map(one,[(s,q,l) for l in levels for s in range(n) for q in POLS],chunksize=16)
    base={(int(r['seed']),r['policy'],r['level']):r for r in csv.DictReader(gzip.open(os.path.join(CODE,'results','results_fresh_v101.csv.gz'),'rt')) if int(r['seed'])<n}
    for l in levels:
        rs=[r for r in rows if r[2]==l]
        w=sum(r[3]=='Force 136' for r in rs)/len(rs);wb=sum(base[(r[0],r[1],l)]['winner']=='Force 136' for r in rs)/len(rs)
        by={}
        for r in rs:by[r[0]]=by.get(r[0],0)+(r[3]=='Force 136')-(base[(r[0],r[1],l)]['winner']=='Force 136')
        rnd=random.Random(1);ks=list(by.values());bs=sorted(sum(rnd.choices(ks,k=len(ks)))/(6*len(ks)) for _ in range(4000))
        print(l,'variant',round(w,4),'baseline',round(wb,4),'diff',round(w-wb,4),'CI',round(bs[100],4),round(bs[3900],4),
              {q:round(sum(r[3]=='Force 136' for r in rs if r[1]==q)/sum(1 for r in rs if r[1]==q),3) for q in POLS},flush=True)
