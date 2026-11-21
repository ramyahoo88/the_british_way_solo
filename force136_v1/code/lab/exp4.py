import sys,time
from harness import evaluate
B=dict(full=['PLACE','INTEL','SUPPLY','STRIKE','TRAIN','CONTACT'],limited=['PLACE','STRIKE','TRAIN','CONTACT'],intel_min=2,first_limited=False)
def V(**k):d=dict(B);d.update(k);return d
variants={
 'A':B,
 'raidfirst':V(strike_sa=['RAID','GATHER']),
 'rail_res4':V(limited=['PLACE','STRIKE','RAIL:res4','TRAIN','CONTACT']),
 'rail_full':V(full=['PLACE','INTEL','SUPPLY','STRIKE','RAIL','TRAIN','CONTACT']),
 'rail_full_res4':V(full=['PLACE','INTEL','SUPPLY','RAIL:res4','STRIKE','TRAIN','CONTACT'],limited=['PLACE','STRIKE','RAIL:res4','TRAIN','CONTACT']),

 'cut_full':V(cut_rail=True,full=['PLACE','INTEL','RAIL:cut','SUPPLY','STRIKE','TRAIN','CONTACT']),
 'cut_full2':V(cut_rail=True,full=['PLACE','INTEL','SUPPLY','RAIL:cut','STRIKE','TRAIN','CONTACT']),
 'cut_lim':V(cut_rail=True,limited=['PLACE','RAIL:cut','STRIKE','TRAIN','CONTACT']),
 'cut_both':V(cut_rail=True,full=['PLACE','INTEL','SUPPLY','RAIL:cut','STRIKE','TRAIN','CONTACT'],limited=['PLACE','RAIL:cut','STRIKE','TRAIN','CONTACT']),
 'cut_first':V(cut_rail=True,full=['PLACE','RAIL:cut','INTEL','SUPPLY','STRIKE','TRAIN','CONTACT'],limited=['PLACE','RAIL:cut','STRIKE','TRAIN','CONTACT']),
}
if __name__=='__main__':
    n=int(sys.argv[1]);start=int(sys.argv[2]);names=sys.argv[3].split(',') if len(sys.argv)>3 else list(variants)
    for name in names:
        t=time.time();out,_=evaluate(variants[name],range(start,start+n));print(name,out,round(time.time()-t),flush=True)
