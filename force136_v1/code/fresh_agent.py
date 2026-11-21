import json,sys
from multiprocessing import Pool
from holdout_v1 import one,POLS
if __name__=='__main__':
    blocks=[(0,1000),(30000,1000),(90000,1000)]
    jobs=[(s,p,'agent') for a,n in blocks for s in range(a,a+n) for p in POLS]
    with Pool(2) as pool: rows=pool.map(one,jobs,chunksize=16)
    json.dump([dict(seed=r['seed'],pol=r['pol'],winner=r['winner'],R=r['R']) for r in rows],open('results_fresh_agent.json','w'))
    import random
    for a,n in blocks:
        rs=[r for r in rows if a<=r['seed']<a+n]
        print(a,n,len(rs),round(sum(r['winner']=='Force 136' for r in rs)/len(rs),3),{p:round(sum(r['winner']=='Force 136' for r in rs if r['pol']==p)/n,3) for p in POLS},flush=True)
    w=sum(r['winner']=='Force 136' for r in rows)/len(rows);print('all',len(rows),round(w,3))
    # distribution of 192-seed block win rates
    by={}
    for r in rows: by.setdefault(r['seed'],[]).append(r['winner']=='Force 136')
    seeds=sorted(by);bl=[]
    for i in range(0,len(seeds)-191,192):
        ss=seeds[i:i+192];bl.append(sum(sum(by[s]) for s in ss)/(6*192))
    print('192-seed consecutive blocks',[round(x,3) for x in bl])
    rnd=random.Random(1);res=[]
    for _ in range(2000):
        ss=rnd.sample(seeds,192);res.append(sum(sum(by[s]) for s in ss)/(6*192))
    res.sort();print('random 192-seed subsets: 2.5%',round(res[50],3),'50%',round(res[1000],3),'97.5%',round(res[1950],3),'P(<=0.536)',sum(x<=0.536 for x in res)/2000)
    # bootstrap CI by seed
    bs=[]
    for _ in range(2000):
        ss=[rnd.choice(seeds) for _ in seeds];bs.append(sum(sum(by[s]) for s in ss)/(6*len(ss)))
    bs.sort();print('bootstrap 95%',round(bs[50],3),round(bs[1950],3))
