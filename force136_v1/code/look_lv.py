import sys
from multiprocessing import Pool
def one(args):
    seed,level,pol,K,S=args
    import lookahead
    cls=type('D',(lookahead.LookGame,),{'K':K,'SAMPLES':S})
    g=cls(seed,level=level);g.policy=pol;r=g.run()
    return (r['winner']=='Force 136',r['final_resistance'])
if __name__=='__main__':
    start=int(sys.argv[1]);n=int(sys.argv[2]);pol=sys.argv[3];K=int(sys.argv[4]);S=int(sys.argv[5])
    with Pool(2) as pool:
        for l in sys.argv[6].split(','):
            out=pool.map(one,[(s,l,pol,K,S) for s in range(start,start+n)],chunksize=2)
            print(pol,K,S,l,round(sum(o[0] for o in out)/n,3),round(sum(o[1] for o in out)/n,2),flush=True)
