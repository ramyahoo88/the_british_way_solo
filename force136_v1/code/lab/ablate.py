import sys,time
from multiprocessing import Pool
POLS=('extraction','hunting','repair','adaptive','counter','mixed')
def one(args):
    seed,pol,swap=args
    import force136
    from expert import FastGame
    attrs={}
    for m in swap:
        if m=='strike':
            for k in ['strike','strike_option','strike_rank']:attrs[k]=getattr(FastGame,k)
        else:attrs[m]=getattr(FastGame,m)
    cls=type('A',(force136.F136Game,),attrs)
    g=cls(seed);g.policy=pol;r=g.run()
    return (r['winner']=='Force 136',r['final_resistance'])
if __name__=='__main__':
    n=int(sys.argv[1]);start=int(sys.argv[2])
    with Pool(2) as pool:
        for swap in sys.argv[3].split(';'):
            sw=[x for x in swap.split(',') if x]
            out=pool.map(one,[(s,p,sw) for s in range(start,start+n) for p in POLS],chunksize=8)
            print(swap or 'none',round(sum(o[0] for o in out)/len(out),3),round(sum(o[1] for o in out)/len(out),2),flush=True)
