import itertools,json
from multiprocessing import Pool
from dev import one
POLS=('extraction','hunting','repair','adaptive','counter','mixed')
BASE={'place_pref':'nocubes','strike_sa':('GATHER2','RAID','GATHER'),'place_sa':('GATHER2','SUPPLY','RAID','GATHER')}
if __name__=='__main__':
    res=[]
    with Pool(2) as pool:
        for perm in itertools.permutations(['STRIKE','INTEL','SUPPLY','TRAIN']):
            for lim in (['PLACE','STRIKE','TRAIN','CONTACT'],['PLACE','TRAIN','STRIKE','CONTACT']):
                P=dict(BASE,limited=lim)
                deck=[dict(id=1,name='x',full=['PLACE']+list(perm))]
                out=pool.map(one,[(s,p,{'P':P,'directives':deck}) for s in range(10000,10064) for p in POLS],chunksize=8)
                w=sum(o[1] for o in out)/len(out);R=sum(o[2] for o in out)/len(out)
                res.append((round(w,3),round(R,2),perm,lim[1]));print(res[-1],flush=True)
    json.dump(sorted(res,reverse=True),open('sweep2.json','w'))
