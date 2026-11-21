import sys,os
sys.path.insert(0,os.path.join(os.path.dirname(os.path.abspath(__file__)),'lab'))
from multiprocessing import Pool
def one(args):
    seed,name,pol,K,S,level=args
    import lookahead,variants
    cls=type('X',(lookahead.LookMixin,variants.VARIANTS[name]),{'K':K,'SAMPLES':S})
    g=cls(seed,level=level);g.policy=pol;r=g.run()
    return (r['winner']=='Force 136',r['final_resistance'])
if __name__=='__main__':
    start=int(sys.argv[1]);n=int(sys.argv[2]);pol=sys.argv[3];K=int(sys.argv[4]);S=int(sys.argv[5])
    with Pool(2) as pool:
        for name in sys.argv[6].split(','):
            out=pool.map(one,[(s,name,pol,K,S,'agent') for s in range(start,start+n)],chunksize=2)
            print(pol,K,S,f'{name:14s}',round(sum(o[0] for o in out)/n,3),round(sum(o[1] for o in out)/n,2),flush=True)
