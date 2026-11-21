import sys
from multiprocessing import Pool
def one(args):
    seed,K,S=args
    import lookahead,expert
    class X(lookahead.LookMixin,expert.ExpertGame):
        weights=None
        def __init__(self,seed,corner=False,level=None):expert.ExpertGame.__init__(self,seed,corner)
    X.K=K;X.SAMPLES=S
    g=X(seed);g.policy='lookc';r=g.run()
    return (r['winner']=='Force 136',r['final_resistance'])
if __name__=='__main__':
    start=int(sys.argv[1]);n=int(sys.argv[2]);K=int(sys.argv[3]);S=int(sys.argv[4])
    import time;t=time.time()
    with Pool(2) as pool:out=pool.map(one,[(s,K,S) for s in range(start,start+n)],chunksize=1)
    print('expert vs lookc',K,S,n,round(sum(o[0] for o in out)/n,3),round(sum(o[1] for o in out)/n,2),round(time.time()-t),flush=True)
