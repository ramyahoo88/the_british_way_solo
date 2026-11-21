import sys,time
from harness import evaluate
from exp4 import variants
P=variants['A']
for hy in sys.argv[3].split(','):
    t=time.time();out,_=evaluate(P,range(int(sys.argv[2]),int(sys.argv[2])+int(sys.argv[1])),cls='HybridGame',attrs={'HY':hy});print(hy,out,round(time.time()-t),flush=True)
