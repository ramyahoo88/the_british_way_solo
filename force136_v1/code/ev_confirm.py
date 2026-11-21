import sys,json
from multiprocessing import Pool
from ev_test_v1 import one,POLS
if __name__=='__main__':
    start=int(sys.argv[1]);n=int(sys.argv[2]);specs=[(int(x.split(':')[0]),x.split(':')[1]) for x in sys.argv[3].split(',')]
    seeds=range(start,start+n)
    with Pool(2) as pool:
        base=pool.map(one,[(s,p,0,'') for s in seeds for p in POLS],chunksize=8)
        bmap={(a,b):(w,r) for a,b,w,r in base}
        print('base',round(sum(x[2] for x in base)/len(base),4),round(sum(x[3] for x in base)/len(base),3),flush=True)
        for j,mode in specs:
            out=pool.map(one,[(s,p,j,mode) for s in seeds for p in POLS],chunksize=8)
            d=[o[2]-bmap[(o[0],o[1])][0] for o in out];dr=[o[3]-bmap[(o[0],o[1])][1] for o in out]
            import statistics
            print(j,mode,'dWin',round(sum(d)/len(d),4),'+-',round(statistics.pstdev(d)/len(d)**.5,4),'dR',round(sum(dr)/len(dr),3),'+-',round(statistics.pstdev(dr)/len(dr)**.5,3),flush=True)
