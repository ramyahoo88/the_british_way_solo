"""Equivalence check: the printed-rules module (force136_v1) vs the tuning lab (force136 + STANDARD flags)."""
import sys,json
from multiprocessing import Pool
POLS=('extraction','hunting','repair','adaptive','counter','mixed')
def lab(seed,pol,level):
    import force136
    P=dict(force136.STANDARD,color_text=True,supply_needs_train=True)
    cls=type('L',(force136.F136Game,),{'P':P})
    g=cls(seed,level=level);g.policy=pol
    trace=[]
    orig=g.bot_turn
    def bt(free):
        before=dict(g.metrics);orig(free)
        k=sorted(k for k in g.metrics if k.startswith('b_') and g.metrics[k]!=before.get(k,0))
        trace.append((g.draw,k[0][2:].replace('STRIKE','AMBUSH').replace('RAIL','SABOTAGE')))
    g.bot_turn=bt;r=g.run()
    return r['winner'],r['final_resistance'],trace
def v1(seed,pol,level):
    import force136_v1
    g=force136_v1.Force136(seed,level=level);g.policy=pol
    trace=[]
    orig=g.bot_turn
    def bt(free):
        orig(free);p=g.last_plan
        trace.append((g.draw,p['op']+('+'+p['sa'] if p.get('sa') else '')))
    g.bot_turn=bt;r=g.run()
    return r['winner'],r['final_resistance'],trace
def one(args):
    s,p,level=args
    a=lab(s,p,level);b=v1(s,p,level)
    same=a[0]==b[0] and a[1]==b[1] and a[2]==b[2]
    first=None
    if not same:
        for x,y in zip(a[2],b[2]):
            if x!=y:first=(x,y);break
    return (s,p,level,same,first)
if __name__=='__main__':
    n=int(sys.argv[1]);levels=sys.argv[2].split(',')
    with Pool(2) as pool:
        out=pool.map(one,[(s,p,l) for s in range(40000,40000+n) for p in POLS for l in levels],chunksize=4)
    bad=[o for o in out if not o[3]]
    print('games',len(out),'mismatches',len(bad))
    for o in bad[:10]:print(o)
