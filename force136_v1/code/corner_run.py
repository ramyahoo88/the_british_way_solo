import sys
from multiprocessing import Pool
POLS=('extraction','hunting','repair','adaptive','counter','mixed')
def one(args):
    seed,pol,corner=args
    import force136_v1 as F
    g=F.Force136(seed,corner=corner);g.policy=pol;r=g.run()
    return (r['winner']=='Force 136',r['final_resistance'])
if __name__=='__main__':
    with Pool(2) as pool:
        for corner in (False,True):
            out=pool.map(one,[(s,p,corner) for s in range(20000,20128) for p in POLS],chunksize=8)
            print('corner',corner,round(sum(o[0] for o in out)/len(out),3),round(sum(o[1] for o in out)/len(out),2),flush=True)
