import sys,os
from multiprocessing import Pool
POLS=('extraction','hunting','repair','adaptive','counter','mixed')
def make(mode):
    import force136_v1 as F
    from engine import gs,cubes,ADJ
    class G(F.Force136):
        def thin_cache(self):
            b=self.board
            for s in self.f136_spaces():
                v=b[s]
                if v['cache'] and gs(v)<=self.TH and (v['troops'] or any(b[x]['troops'] for x in ADJ[s])):return True
            return False
        def choose(self,free):
            if self.thin_cache():
                p=self.clone()
                if p.train():
                    if 'Op & SA' in free and mode in('full','both'):
                        return dict(op='TRAIN',sa=self.first_sa(p,('SUPPLY','RAID')),box='Op & SA',goal='GUARD')
                    if 'Limited' in free and 'Op & SA' not in free and mode in('lim','both'):
                        return dict(op='TRAIN',box='Limited',goal='GUARD')
            return F.Force136.choose(self,free)
    return G
def one(args):
    seed,pol,mode,th=args
    G=make(mode);G.TH=th
    g=G(seed);g.policy=pol;r=g.run()
    return (pol,r['winner']=='Force 136',r['final_resistance'])
if __name__=='__main__':
    start=int(sys.argv[1]);n=int(sys.argv[2])
    with Pool(2) as pool:
        for spec in sys.argv[3:]:
            mode,th=spec.split(':');th=int(th)
            out=pool.map(one,[(s,p,mode,th) for s in range(start,start+n) for p in POLS],chunksize=8)
            per={p:round(sum(o[1] for o in out if o[0]==p)/sum(1 for o in out if o[0]==p),2) for p in POLS}
            print(spec,round(sum(o[1] for o in out)/len(out),3),round(sum(o[2] for o in out)/len(out),2),per,flush=True)
