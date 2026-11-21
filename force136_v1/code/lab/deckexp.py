import sys,ast
from multiprocessing import Pool
from dev import one
POLS=('extraction','hunting','repair','adaptive','counter','mixed')
BASE={'place_pref':'nocubes','strike_sa':('GATHER2','RAID','GATHER'),'place_sa':('GATHER2','SUPPLY','RAID','GATHER')}
def D(full,lim='S',south=False):
    return dict(id=0,name='',full=['PLACE']+full,limited=['PLACE','STRIKE','TRAIN','CONTACT'] if lim=='S' else ['PLACE','TRAIN','STRIKE','CONTACT'],south=south)
DECKS={
 'mix9':[D(['STRIKE','INTEL','SUPPLY','TRAIN']),D(['STRIKE','INTEL','SUPPLY','TRAIN']),D(['STRIKE','INTEL','SUPPLY','TRAIN']),
         D(['STRIKE','INTEL','TRAIN','SUPPLY'],'T'),D(['STRIKE','INTEL','TRAIN','SUPPLY'],'T'),
         D(['INTEL','STRIKE','SUPPLY','TRAIN']),D(['INTEL','STRIKE','SUPPLY','TRAIN']),
         D(['INTEL','STRIKE','TRAIN','SUPPLY'],'T'),D(['STRIKE','SUPPLY','INTEL','TRAIN'],'T')],
 'one_north':[D(['STRIKE','INTEL','SUPPLY','TRAIN'])],
 'one_south':[D(['STRIKE','INTEL','SUPPLY','TRAIN'],south=True)],
 'mix6':[D(['STRIKE','INTEL','SUPPLY','TRAIN']),D(['STRIKE','INTEL','TRAIN','SUPPLY'],'T',True),D(['INTEL','STRIKE','SUPPLY','TRAIN'],'S',True),
         D(['INTEL','STRIKE','TRAIN','SUPPLY'],'T'),D(['STRIKE','SUPPLY','INTEL','TRAIN'],'T',True),D(['STRIKE','TRAIN','SUPPLY','INTEL'],'S')],
}
if __name__=='__main__':
    start=int(sys.argv[1]);n=int(sys.argv[2])
    with Pool(2) as pool:
        for name in sys.argv[3].split(','):
            out=pool.map(one,[(s,p,{'P':BASE,'directives':DECKS[name]}) for s in range(start,start+n) for p in POLS],chunksize=8)
            w=sum(o[1] for o in out)/len(out);R=sum(o[2] for o in out)/len(out);m=sum(o[3] for o in out)/len(out)
            per={p:round(sum(o[1] for o in out if o[0]==p)/sum(1 for o in out if o[0]==p),2) for p in POLS}
            print(name,round(w,3),round(R,2),round(m,3),per,flush=True)
