import sys,json
from multiprocessing import Pool
POLS=('extraction','hunting','repair','adaptive','counter','mixed')
def one(args):
    seed,pol,j,mode=args
    import force136_v1,rulebot
    from engine import BOXES
    class G(force136_v1.Force136):
        def choose(self,free):
            if j and 'Event' in free and self.event==j and self.event not in(6,9) and rulebot.ev_cond(self,j):
                if mode=='always' or 'Op & SA' not in free:return dict(op='EVENT',box='Event',goal='EVENT')
            return force136_v1.Force136.choose(self,free)
        def execute(self,plan):
            if plan['op']=='EVENT':self.execute_event(self.event,'U');return
            return force136_v1.Force136.execute(self,plan)
    g=G(seed);g.policy=pol;r=g.run()
    return (seed,pol,r['winner']=='Force 136',r['final_resistance'])
if __name__=='__main__':
    n=int(sys.argv[1]);start=int(sys.argv[2])
    evs=[1,2,3,4,5,7,8,10,11,12,13,14,15,16,18,19,21,22,23,24,25,26,27,28,29,30,31,32]
    seeds=range(start,start+n);res={}
    with Pool(2) as pool:
        base=pool.map(one,[(s,p,0,'') for s in seeds for p in POLS],chunksize=8)
        bmap={(a,b):(w,r) for a,b,w,r in base}
        print('base',sum(x[2] for x in base)/len(base),sum(x[3] for x in base)/len(base),flush=True)
        for j in evs:
            for mode in ['always','second']:
                out=pool.map(one,[(s,p,j,mode) for s in seeds for p in POLS],chunksize=8)
                dw=sum(o[2]-bmap[(o[0],o[1])][0] for o in out)/len(out);dr=sum(o[3]-bmap[(o[0],o[1])][1] for o in out)/len(out)
                res[f'{j}_{mode}']=(round(dw,3),round(dr,3));print(j,mode,round(dw,3),round(dr,3),flush=True)
    json.dump(res,open('ev_test_v1.json','w'),indent=0)
