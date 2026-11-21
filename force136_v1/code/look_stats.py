import sys,collections
from multiprocessing import Pool
def one(args):
    seed,K,S=args
    import lookahead
    from scoreparts import patch
    cls=type('D',(lookahead.LookGame,),{'K':K,'SAMPLES':S})
    g=cls(seed);g.policy='lookc'
    jp=collections.Counter()
    orig=cls.jp_apply
    def ja(self,plan):
        if not self.preview:jp[(plan['op'],plan.get('sa'),plan['box'])]+=1
        return orig(self,plan)
    cls.jp_apply=ja
    parts=[]
    origsc=cls.score_only
    def sc(self,final=False):
        r=origsc(self,final)
        if not self.preview:parts.append((r['intel'],r['caches'],r['majorities'],r['resource_penalty'],r['neutral_penalty'],r['police_penalty'],self.count('force136')))
        return r
    cls.score_only=sc
    r=g.run();m=r['metrics']
    return dict(win=r['winner']=='Force 136',R=r['final_resistance'],jp=dict((f'{a}/{b}/{c}',v) for (a,b,c),v in jp.items()),parts=parts,elim=m.get('force136_eliminated',0),cas=m.get('caches_assaulted',0))
if __name__=='__main__':
    n=int(sys.argv[1])
    with Pool(2) as pool:
        for K,S in [(8,3),(16,4)]:
            out=pool.map(one,[(s,K,S) for s in range(20000,20000+n)])
            jp=collections.Counter()
            for o in out:jp.update(o['jp'])
            print(f'K={K} S={S} win',sum(o['win'] for o in out)/n,'R',sum(o['R'] for o in out)/n,'F136 elim',sum(o['elim'] for o in out)/n,'caches assaulted',sum(o['cas'] for o in out)/n)
            print('  japan',[(k,round(v/n,2)) for k,v in jp.most_common(10)])
            for i in range(3):
                ps=[o['parts'][i] for o in out if len(o['parts'])>i]
                if ps:print('  prop',i+1,[round(sum(p[j] for p in ps)/len(ps),2) for j in range(7)],'(intel,caches,maj,res,neut,pol,F136)')
