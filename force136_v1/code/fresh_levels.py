"""Fresh-seed check after GPT's review: more Agent blocks, then every level on seeds 0-999."""
import json,sys
from multiprocessing import Pool
from holdout_v1 import one,POLS
if __name__=='__main__':
    jobs=[(s,p,'agent') for a in (50000,60000) for s in range(a,a+1000) for p in POLS]
    jobs+=[(s,p,l) for l in ('recruit','veteran','legend','mastermind') for s in range(0,1000) for p in POLS]
    with Pool(2) as pool:rows=pool.map(one,jobs,chunksize=16)
    json.dump([dict(seed=r['seed'],pol=r['pol'],level=r['level'],winner=r['winner'],R=r['R']) for r in rows],open('results_fresh_levels.json','w'))
    print('done',len(rows))
