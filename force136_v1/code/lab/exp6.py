import sys,time
from harness import evaluate
n=int(sys.argv[1]);start=int(sys.argv[2])
t=time.time();out,res=evaluate(None,range(start,start+n),mod='force136',cls='F136Game');print('F136Game',out,round(time.time()-t),flush=True)
