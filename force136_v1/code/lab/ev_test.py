import sys,json,time
from multiprocessing import Pool
FULL=['PLACE','STRIKE','SUPPLY','TRAIN','INTEL','CONTACT']
LIM=['PLACE','STRIKE','TRAIN','CONTACT']
POLS=('extraction','hunting','repair','adaptive','counter','mixed')
def one(args):
    seed,pol,EV=args
    import rulebot
    class G(rulebot.EventRuleGame):pass
    G.P=dict(full=FULL,limited=LIM,intel_min=2,first_limited=False);G.EV=EV
    g=G(seed);g.policy=pol;r=g.run()
    return (seed,pol,r['winner']=='Force 136',r['final_resistance'],r['winner']=='MPAJA')
if __name__=='__main__':
    n=int(sys.argv[1]);start=int(sys.argv[2])
    evs=[int(x) for x in sys.argv[3].split(',')]
    seeds=range(start,start+n)
    with Pool(2) as pool:
        base=pool.map(one,[(s,p,{}) for s in seeds for p in POLS],chunksize=8)
        bmap={(a,b):(w,r) for a,b,w,r,m in base}
        print('base win',sum(x[2] for x in base)/len(base),'R',sum(x[3] for x in base)/len(base),flush=True)
        res={}
        for j in evs:
            for mode in ['always','second']:
                out=pool.map(one,[(s,p,{j:mode}) for s in seeds for p in POLS],chunksize=8)
                dw=sum(o[2]-bmap[(o[0],o[1])][0] for o in out)/len(out);dr=sum(o[3]-bmap[(o[0],o[1])][1] for o in out)/len(out)
                res[f'{j}{mode[0]}']=(round(dw,3),round(dr,3))
                print(j,mode,round(dw,3),round(dr,3),flush=True)
        json.dump(res,open(f'ev_test_{start}.json','w'))
