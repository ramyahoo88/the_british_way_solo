import sys,os
sys.path.insert(0,os.path.dirname(os.path.dirname(os.path.abspath(__file__))));sys.path.insert(0,os.path.dirname(os.path.abspath(__file__)))
from multiprocessing import Pool
POLS=tuple(os.environ.get('POLS','extraction,hunting,repair,adaptive,counter,mixed').split(','))
def one(args):
    seed,pol,name=args
    import variants
    g=variants.VARIANTS[name](seed);g.policy=pol;r=g.run()
    return (pol,r['winner']=='Force 136',r['final_resistance'])
if __name__=='__main__':
    start=int(sys.argv[1]);n=int(sys.argv[2])
    with Pool(2) as pool:
        for name in sys.argv[3].split(','):
            out=pool.map(one,[(s,p,name) for s in range(start,start+n) for p in POLS],chunksize=8)
            per={p:round(sum(o[1] for o in out if o[0]==p)/sum(1 for o in out if o[0]==p),2) for p in POLS}
            print(f"{name:16s}",round(sum(o[1] for o in out)/len(out),3),round(sum(o[2] for o in out)/len(out),2),per,flush=True)
