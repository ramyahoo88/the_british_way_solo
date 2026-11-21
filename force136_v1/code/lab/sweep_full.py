import itertools,json,sys,time
from harness import evaluate
from exp4 import variants
base=dict(variants['A'])
goals=['PLACE','INTEL','SUPPLY','STRIKE','TRAIN']
out=[]
for perm in itertools.permutations(goals):
    P=dict(base);P['full']=list(perm)+['CONTACT']
    r,_=evaluate(P,range(7100,7132))
    out.append((r['ALL'],perm));print(r['ALL'],perm,flush=True)
out.sort(reverse=True)
json.dump(out,open('sweep_full.json','w'))
