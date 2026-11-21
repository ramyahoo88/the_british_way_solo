import sys,time,json,collections
from multiprocessing import Pool
POLS=('extraction','hunting','repair','adaptive','counter','mixed')
def _one(args):
    modname,clsname,P,seed,pol,attrs=args
    import importlib;m=importlib.import_module(modname);base=getattr(m,clsname)
    cls=type('V',(base,),{'P':P}) if P is not None else base
    g=cls(seed);g.policy=pol
    for k,v in (attrs or {}).items():setattr(g,k,v)
    r=g.run();r.pop('metrics',None);r.pop('event_order',None);return r
def evaluate(P,seeds,pols=POLS,mod='rulebot',cls='RuleGame',attrs=None,procs=2):
    jobs=[(mod,cls,P,s,p,attrs) for s in seeds for p in pols]
    with Pool(procs) as pool:res=pool.map(_one,jobs,chunksize=4)
    out={}
    for p in pols:
        rs=[r for r in res if r['policy']==p]
        out[p]=(round(sum(r['winner']=='Force 136' for r in rs)/len(rs),3),round(sum(r['final_resistance'] for r in rs)/len(rs),1))
    n=len(res);out['ALL']=(round(sum(r['winner']=='Force 136' for r in res)/n,3),round(sum(r['final_resistance'] for r in res)/n,2),round(sum(r['winner']=='MPAJA' for r in res)/n,3))
    return out,res
