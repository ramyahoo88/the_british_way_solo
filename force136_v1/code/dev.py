import sys,time,ast
from multiprocessing import Pool
import os
POLS=tuple(os.environ.get('POLS','extraction,hunting,repair,adaptive,counter,mixed').split(','))
def one(args):
    seed,pol,attrs=args
    import force136
    cls=type('A',(force136.F136Game,),attrs)
    g=cls(seed);g.policy=pol;r=g.run()
    return (pol,r['winner']=='Force 136',r['final_resistance'],r['winner']=='MPAJA')
def run(attrs,seeds,pool):
    out=pool.map(one,[(s,p,attrs) for s in seeds for p in POLS],chunksize=8)
    n=len(out);w=sum(o[1] for o in out)/n;R=sum(o[2] for o in out)/n;m=sum(o[3] for o in out)/n
    per={p:round(sum(o[1] for o in out if o[0]==p)/sum(1 for o in out if o[0]==p),2) for p in POLS}
    return round(w,3),round(R,2),round(m,3),per
if __name__=='__main__':
    start=int(sys.argv[1]);n=int(sys.argv[2])
    with Pool(2) as pool:
        for spec in sys.argv[3:]:
            t=time.time();print(spec,run(ast.literal_eval(spec),range(start,start+n),pool),round(time.time()-t),flush=True)
