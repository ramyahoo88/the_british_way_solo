"""v1.1's Event step (J4 and J25 as second player) against v1.0.4, on the stored fresh games.

Pairs results/results_fresh_v110.csv.gz with results/results_fresh_v103.csv.gz (v1.0.4 plays v1.0.3's games
exactly): the same seed, Japan policy and level. The games are identical until the first J4 or J25 turn where
the Event step fires. Intervals: whole-seed bootstrap, 10,000 resamples, random.Random(33745) per level.
report_check.py imports change() to check the printed table.

usage: python3 ev_package.py
"""
import csv,gzip,os,random
HERE=os.path.dirname(os.path.abspath(__file__))
LEVELS=('recruit','agent','veteran','legend','mastermind')
POLS=('extraction','hunting','repair','adaptive','counter','mixed')

def load(name):
    p=os.path.join(HERE,'results',name)
    return {(r['seed'],r['policy'],r['level']):r for r in csv.DictReader(gzip.open(p,'rt'))}

def change(new=None,old=None):
    """Per level: (change in win points, 2.5th and 97.5th percentiles, change in mean final Resistance,
    games that differ in winner)."""
    new=new or load('results_fresh_v110.csv.gz');old=old or load('results_fresh_v103.csv.gz')
    out={}
    for l in LEVELS:
        by={};dR=0;flips=0;n=0
        for (s,p,lv),r in new.items():
            if lv!=l:continue
            o=old[(s,p,l)];d=(r['winner']=='Force 136')-(o['winner']=='Force 136')
            by[s]=by.get(s,0)+d;dR+=int(r['final_resistance'])-int(o['final_resistance']);flips+=r['winner']!=o['winner'];n+=1
        seeds=sorted(by);k=[by[x] for x in seeds];rnd=random.Random(33745)
        bs=sorted(100*sum(rnd.choices(k,k=len(k)))/n for _ in range(10000))
        out[l]=(100*sum(k)/n,bs[249],bs[9749],dR/n,flips)
    return out

if __name__=='__main__':
    for l,(d,lo,hi,dR,f) in change().items():
        print(f'{l:10s} change {d:+.2f} points (95% {lo:+.2f} to {hi:+.2f})  final Resistance {dR:+.3f}  games with a different winner {f}')
