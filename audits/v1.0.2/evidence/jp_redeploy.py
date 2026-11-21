"""Sensitivity: at Japanese Redeploy (6.5.2, "may move"), a Kempeitai already with a Force 136 marker stays
there instead of being pulled away when that space is not a legal destination. Other Kempeitai move as before."""
import sys,os,csv,gzip,random
CODE=os.environ['F136_CODE']   # force136_v1/code of a checkout at commit 338cb0d
sys.path.insert(0,CODE)
from multiprocessing import Pool
import force136_v1 as V
from engine import *
POLS=('extraction','hunting','repair','adaptive','counter','mixed')
class KeepK(V.Force136):
    def propaganda(self,final=False):
        result=self.score_only(final)
        if final:return result
        b=self.board
        for rail in V.RAIL_LIST:
            if self.sabotage[rail]:
                sites=[s for s in self.rail_adj(rail) if POP[s] and not b[s]['terror'] and not b[s]['opposition']]
                if sites:b[self.opp_pick(sites)]['opposition']=True
        self.construct();self.supply();self.reprisal()
        movers=[(src,b[src]['force136']) for src in V.MAP_ORDER if b[src]['force136'] and self.exposed(src)]
        for src,n in movers:
            for _ in range(n):
                dests=[s for s in PROV if b[s]['camp'] and not b[s]['force136'] and not b[s]['kempeitai']]
                if not dests:break
                d=min(dests,key=lambda s:(-gs(b[s]),V.mo(s)));b[src]['force136']-=1;b[d]['force136']+=1
        sites=[s for s in ORDER if b[s]['troops']>gs(b[s])]
        if sites:
            movable=0
            for s in ORDER:
                keep=min(b[s]['police'],1) if s not in sites and b[s]['force136'] and b[s]['kempeitai'] else 0
                movable+=b[s]['police']-keep;b[s]['police']=keep
            ranked=sorted(sites,key=lambda s:(bool(b[s]['police']),not bool(b[s]['force136']),ix(s)))
            for i in range(movable):b[ranked[i%len(ranked)]]['police']+=1
            stay={s:min(b[s]['kempeitai'],1) for s in ORDER if b[s]['force136'] and b[s]['kempeitai'] and s not in sites}
            total=self.count('kempeitai')-sum(stay.values())
            for s,v in b.items():v['kempeitai']=stay.get(s,0)
            ranked=sorted(sites,key=lambda s:(not bool(b[s]['force136']),gs(b[s])-b[s]['police'],ix(s)))
            for i in range(total):b[ranked[i%len(ranked)]]['kempeitai']+=1
        for v in b.values():
            v['terror']=0
            for c in ['red','blue']:v[c+'_u']+=v[c+'_a'];v[c+'_a']=0
        self.reset_intel(self.campaign)
        b['Kuala Lumpur']['troops']+=self.away_troops;self.away_troops=0
        if self.away_f:
            camps=[s for s in PROV if b[s]['camp']]
            if camps:
                dst=min(camps,key=lambda s:(bool(b[s]['kempeitai']),bool(b[s]['force136']),-gs(b[s]),ix(s)))
                b[dst]['force136']+=self.away_f
            self.away_f=0
        self.campaign+=1;self.first='B';self.regular_seen=0;self.chosen={}
        return result
def one(a):
    seed,pol=a;g=KeepK(seed);g.policy=pol;r=g.run();return (seed,pol,r['winner'],r['final_resistance'])
if __name__=='__main__':
    n=int(sys.argv[1])
    with Pool(2) as p:rows=p.map(one,[(s,q) for s in range(n) for q in POLS],chunksize=16)
    base={(int(r['seed']),r['policy']):r for r in csv.DictReader(gzip.open(os.path.join(CODE,'results','results_fresh_v101.csv.gz'),'rt')) if r['level']=='agent' and int(r['seed'])<n}
    w=sum(r[2]=='Force 136' for r in rows)/len(rows);wb=sum(base[(r[0],r[1])]['winner']=='Force 136' for r in rows)/len(rows)
    by={}
    for r in rows:by[r[0]]=by.get(r[0],0)+(r[2]=='Force 136')-(base[(r[0],r[1])]['winner']=='Force 136')
    rnd=random.Random(1);ks=list(by.values());bs=sorted(sum(rnd.choices(ks,k=len(ks)))/(6*len(ks)) for _ in range(4000))
    print('variant',round(w,4),'baseline',round(wb,4),'diff',round(w-wb,4),'CI',round(bs[100],4),round(bs[3900],4))
    for q in POLS:
        rs=[r for r in rows if r[1]==q];print(q,round(sum(r[2]=='Force 136' for r in rs)/len(rs),3),round(sum(base[(r[0],r[1])]['winner']=='Force 136' for r in rs)/len(rs),3))
