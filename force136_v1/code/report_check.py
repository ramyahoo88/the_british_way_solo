"""Check that the printed win-rate tables match the stored v1.0.1 results (GPT re-audit, finding R1).

Recomputes every cell from results/results_fresh_v101.csv.gz and compares it with:
- the simulation report's summary table (win %, mean final Resistance, MPAJA %; one decimal),
- the simulation report's per-policy table (whole percent; the search-player column is historical). Rounding is half up.,
- the level table in the rules and the force136_v1 README (whole percent),
- the summary table's 95% intervals: whole-seed bootstrap, 10,000 resamples, random.Random(33745) per level,
  2.5th and 97.5th percentiles, one decimal,
- the stress-policy table: wins / games per policy from results/results_exploits_v102.json.
Exit status 1 on any mismatch. Run from code/: python3 report_check.py
"""
import csv,gzip,os,re,sys
from decimal import Decimal,ROUND_HALF_UP
def fmt(x,d):return str(Decimal(repr(x)).quantize(Decimal('1') if d==0 else Decimal('0.1'),rounding=ROUND_HALF_UP))
HERE=os.path.dirname(os.path.abspath(__file__));PKG=os.path.dirname(HERE)
def find(name):
    p=os.path.join(HERE,'results',name)
    return p if os.path.exists(p) else os.path.join(HERE,name)
RES=find('results_fresh_v101.csv.gz')   # v1.0.2 reproduces every row (results/v102_fresh_identity.log)
rows=list(csv.DictReader(gzip.open(RES,'rt')))
LEVELS=('recruit','agent','veteran','legend','mastermind');POLS=('extraction','hunting','repair','adaptive','counter','mixed')
def cell(l,p=None):
    rs=[r for r in rows if r['level']==l and (p is None or r['policy']==p)]
    return (100*sum(r['winner']=='Force 136' for r in rs)/len(rs),sum(float(r['final_resistance']) for r in rs)/len(rs),
            100*sum(r['winner']=='MPAJA' for r in rs)/len(rs))
bad=[]
def check(where,got,want):
    if got!=want:bad.append(f'{where}: printed {got}, data {want}')
rep=open(os.path.join(PKG,'print','Force_136_v1_Sim_Report.md')).read()
for l in LEVELS:
    w,R,m=cell(l)
    line=re.search(r'^\| \**'+l.capitalize()+r'\** \|[^|]*\| \**([\d.]+)%\** \| [^|]* \| ([\d.]+) \| ([\d.]+)% \|$',rep,re.M)
    if not line:bad.append(f'report summary: no row for {l}');continue
    check(f'report summary {l} win',line.group(1),fmt(w,1));check(f'report summary {l} R',line.group(2),fmt(R,1))
    check(f'report summary {l} MPAJA',line.group(3),fmt(m,1))
import random,json
def interval(l):
    by={}
    for r in rows:
        if r['level']==l:by[r['seed']]=by.get(r['seed'],0)+(r['winner']=='Force 136')
    seeds=sorted(by);k=[by[x] for x in seeds];n=len(seeds);rnd=random.Random(33745);bs=[]
    for _ in range(10000):bs.append(100*sum(rnd.choices(k,k=n))/(6*n))
    bs.sort();return fmt(bs[249],1),fmt(bs[9749],1)
for l in LEVELS:
    line=re.search(r'^\| \**'+l.capitalize()+r'\** \|[^|]*\| [^|]* \| ([\d.]+)–([\d.]+)% \|',rep,re.M)
    if not line:bad.append(f'report interval: no row for {l}');continue
    check(f'report interval {l}',(line.group(1),line.group(2)),interval(l))
EX=json.load(open(find('results_exploits_v102.json')))
LABEL={'brute':'Eliminates, or makes a Limited Assault or Sweep','tempo':'takes the Limited box','econ':'Deploys or Constructs','eventhog':'takes the Event'}
for pol,label in LABEL.items():
    rs=[r for r in EX if r['pol']==pol];w=sum(r['winner']=='Force 136' for r in rs)
    line=re.search(r'^\| '+re.escape(label)+r' \| (\d+) / (\d+) \((\d+)%\) \|$',rep,re.M)
    if not line:bad.append(f'stress table: no row for {pol}');continue
    check(f'stress {pol}',(line.group(1),line.group(2),line.group(3)),(str(w),str(len(rs)),fmt(100*w/len(rs),0)))
m=re.search(r'seeds (\d+)–(\d+): (\d+) games per policy',rep)
seeds={r['seed'] for r in EX}
if not m:bad.append('stress caption missing')
else:check('stress caption',(int(m.group(1)),int(m.group(2)),int(m.group(3))),(min(seeds),max(seeds),len(EX)//len(LABEL)))
for p in POLS:
    line=re.search(r'^\| '+p+r' \| (\d+)% \| (\d+)% \| (\d+)% \| (\d+)% \| (\d+)% \|',rep,re.M)
    if not line:bad.append(f'report per-policy: no row for {p}');continue
    for k,l in enumerate(LEVELS):check(f'report per-policy {p}/{l}',line.group(k+1),fmt(cell(l,p)[0],0))
for name,path,labels in (('rules',os.path.join(PKG,'print','Force_136_v1_Rules.md'),{'recruit':'Recruit','agent':'Agent','veteran':'Veteran','legend':'Legend','mastermind':'Mastermind'}),
                         ('README',os.path.join(PKG,'README.md'),None)):
    text=open(path).read()
    for l in LEVELS:
        line=re.search(r'^\| '+l.capitalize()+r' \|[^\n]*\| (\d+)% \|$',text,re.M)
        if not line:bad.append(f'{name}: no level row for {l}');continue
        check(f'{name} level {l}',line.group(1),fmt(cell(l)[0],0))
print('\n'.join(bad) if bad else f'all printed win-rate cells match {os.path.basename(RES)}')
sys.exit(1 if bad else 0)
