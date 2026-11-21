"""v1.0.1 results on fresh seeds 0-999, all five levels, six Japan policies (6,000 games per level)."""
import json,csv,gzip,collections,sys
from multiprocessing import Pool
from holdout_v1 import one,POLS
LEVELS=('recruit','agent','veteran','legend','mastermind')
if __name__=='__main__':
    start=int(sys.argv[1]) if len(sys.argv)>1 else 0;n=int(sys.argv[2]) if len(sys.argv)>2 else 1000
    name=sys.argv[3] if len(sys.argv)>3 else 'fresh_v101'
    with Pool(2) as pool:rows=pool.map(one,[(s,p,l) for l in LEVELS for s in range(start,start+n) for p in POLS],chunksize=16)
    with gzip.open(f'results_{name}.csv.gz','wt',newline='') as f:
        w=csv.writer(f);w.writerow(['seed','policy','level','winner','final_resistance','camps','force136'])
        for r in rows:w.writerow([r['seed'],r['pol'],r['level'],r['winner'],r['R'],r['camps'],r['f136']])
    summ={}
    for l in LEVELS:
        rs=[r for r in rows if r['level']==l];N=len(rs)
        g=collections.Counter();o=collections.Counter()
        for r in rs:g.update(r['goals']);o.update(r['ops'])
        tg=sum(g.values());to=sum(o.values())
        summ[l]=dict(n=N,win=round(sum(r['winner']=='Force 136' for r in rs)/N,4),mpaja=round(sum(r['winner']=='MPAJA' for r in rs)/N,4),
                     R=round(sum(r['R'] for r in rs)/N,2),turns=round(tg/N,2),
                     per={p:round(sum(r['winner']=='Force 136' for r in rs if r['pol']==p)/sum(1 for r in rs if r['pol']==p),3) for p in POLS},
                     goals={k:round(v/tg,3) for k,v in g.most_common()},ops={k:round(v/to,3) for k,v in o.most_common(14)})
        print(l,json.dumps({k:summ[l][k] for k in ('n','win','mpaja','R','per')}),flush=True)
    json.dump(summ,open(f'{name}_summary.json','w'),indent=1)
