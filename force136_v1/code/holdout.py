import json,time,sys
from multiprocessing import Pool
import lv
from harness import evaluate
HOLD=range(20000,20128)
if __name__=='__main__':
    out={}
    with Pool(2) as pool:
        for level in ['recruit','agent','veteran','legend']:
            t=time.time();r=lv.run(level,None,HOLD,pool);r['sec']=round(time.time()-t);out[level]=r;print(json.dumps(r),flush=True)
    for name,mod,cls,attrs in [('gpt_v0.2','expert','FastGame',{'variant':'baseline'}),('gpt_primary_guard','expert','FastGame',{'variant':'primary_guard'}),('expert','expert','ExpertGame',{'weights':None})]:
        t=time.time();o,_=evaluate(None,HOLD,mod=mod,cls=cls,attrs=attrs);out[name]=dict(per=o,win=o['ALL'][0],R=o['ALL'][1],mpaja=o['ALL'][2],sec=round(time.time()-t));print(name,json.dumps(out[name]),flush=True)
    json.dump(out,open('holdout_results.json','w'),indent=1)
