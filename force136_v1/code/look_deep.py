import sys,json,time
from multiprocessing import Pool
def one(args):
    seed,level,pol,K,S=args
    import lookahead
    cls=type('D',(lookahead.LookGame,),{'K':K,'SAMPLES':S})
    g=cls(seed,level=level);g.policy=pol;r=g.run()
    return (seed,level,pol,r['winner'],r['final_resistance'])
if __name__=='__main__':
    start=int(sys.argv[1]);n=int(sys.argv[2]);levels=sys.argv[3].split(',');pol=sys.argv[4];K=int(sys.argv[5]);S=int(sys.argv[6])
    t=time.time()
    with Pool(2) as pool:out=pool.map(one,[(s,l,pol,K,S) for l in levels for s in range(start,start+n)],chunksize=2)
    for l in levels:
        rs=[o for o in out if o[1]==l]
        print(pol,f'K={K} S={S}',l,len(rs),'win',round(sum(o[3]=='Force 136' for o in rs)/len(rs),3),'R',round(sum(o[4] for o in rs)/len(rs),2),round(time.time()-t),flush=True)
