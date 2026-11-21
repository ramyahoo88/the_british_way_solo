import sys,os
from multiprocessing import Pool
POLS=tuple(os.environ.get('POLS','extraction,hunting,repair,adaptive,counter,mixed').split(','))
def one(args):
    seed,pol,level,extra=args
    import force136
    cls=force136.F136Game
    if extra:cls=type('X',(cls,),{'P':dict(force136.STANDARD,**extra)})
    g=cls(seed,level=level);g.policy=pol;r=g.run()
    return (pol,r['winner']=='Force 136',r['final_resistance'],r['winner']=='MPAJA',r['draws'])
def run(level,extra,seeds,pool):
    out=pool.map(one,[(s,p,level,extra) for s in seeds for p in POLS],chunksize=8)
    n=len(out)
    per={p:round(sum(o[1] for o in out if o[0]==p)/sum(1 for o in out if o[0]==p),3) for p in POLS}
    return dict(level=level,extra=extra,n=n,win=round(sum(o[1] for o in out)/n,3),R=round(sum(o[2] for o in out)/n,2),mpaja=round(sum(o[3] for o in out)/n,3),per=per)
if __name__=='__main__':
    import ast,json
    start=int(sys.argv[1]);n=int(sys.argv[2])
    with Pool(2) as pool:
        for spec in sys.argv[3:]:
            level,extra=ast.literal_eval(spec)
            r=run(level,extra,range(start,start+n),pool);print(json.dumps(r),flush=True)
