import json,time,sys,os
from multiprocessing import Pool
POLS=tuple(os.environ.get('POLS','extraction,hunting,repair,adaptive,counter,mixed').split(','))
def one(args):
    seed,pol,level=args
    import force136_v1
    g=force136_v1.Force136(seed,level=level);g.policy=pol;r=g.run()
    m=r['metrics']
    return dict(seed=seed,pol=pol,level=level,winner=r['winner'],R=r['final_resistance'],camps=r['camps'],f136=r['force136'],draws=r['draws'],
                goals={k[2:]:v for k,v in m.items() if k.startswith('g_')},
                ops={k[2:]:v for k,v in m.items() if k.startswith('o_')})
if __name__=='__main__':
    start=int(sys.argv[1]);n=int(sys.argv[2]);name=sys.argv[3]
    levels=sys.argv[4].split(',') if len(sys.argv)>4 else ['recruit','agent','veteran','legend']
    with Pool(2) as pool:
        rows=pool.map(one,[(s,p,l) for l in levels for s in range(start,start+n) for p in POLS],chunksize=8)
    json.dump(rows,open(f'results_{name}.json','w'))
    for l in levels:
        rs=[r for r in rows if r['level']==l];N=len(rs)
        w=sum(r['winner']=='Force 136' for r in rs)/N;m=sum(r['winner']=='MPAJA' for r in rs)/N
        per={p:round(sum(r['winner']=='Force 136' for r in rs if r['pol']==p)/sum(1 for r in rs if r['pol']==p),3) for p in POLS}
        print(l,N,'win',round(w,3),'mpaja',round(m,3),'R',round(sum(r['R'] for r in rs)/N,2),per,flush=True)
