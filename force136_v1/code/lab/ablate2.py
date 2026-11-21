import sys
from multiprocessing import Pool
POLS=('extraction','hunting','repair','adaptive','counter','mixed')
def one(args):
    seed,pol,attrs,swap=args
    import force136
    from expert import FastGame
    a=dict(attrs)
    for m in swap:a[m]=getattr(FastGame,m)
    cls=type('A',(force136.F136Game,),a)
    g=cls(seed);g.policy=pol;r=g.run()
    return (r['winner']=='Force 136',r['final_resistance'])
if __name__=='__main__':
    import ast
    n=int(sys.argv[1]);start=int(sys.argv[2])
    with Pool(2) as pool:
        for spec in sys.argv[3:]:
            attrs,swap=ast.literal_eval(spec)
            out=pool.map(one,[(s,p,attrs,swap) for s in range(start,start+n) for p in POLS],chunksize=8)
            print(spec,round(sum(o[0] for o in out)/len(out),3),round(sum(o[1] for o in out)/len(out),2),flush=True)
