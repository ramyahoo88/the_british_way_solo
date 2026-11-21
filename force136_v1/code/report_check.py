"""Check that the printed win-rate tables match the stored v1.0.1 results (GPT re-audit, finding R1).

Recomputes every cell from results/results_fresh_v103.csv.gz and compares it with:
- the simulation report's summary table (win %, mean final Resistance, MPAJA %; one decimal),
- the simulation report's per-policy table (whole percent; the search-player column is historical). Rounding is half up.,
- the level table in the rules and the force136_v1 README (whole percent),
- the summary table's 95% intervals: whole-seed bootstrap, 10,000 resamples, random.Random(33745) per level,
  2.5th and 97.5th percentiles, one decimal,
- the stress-policy table: wins / games per policy from results/results_exploits_v103.json,
- the lookahead, search-player, reference and map-reading figures from the stored v103 logs.
Exit status 1 on any mismatch. Run from code/: python3 report_check.py
"""
import csv,gzip,os,re,sys
from decimal import Decimal,ROUND_HALF_UP
def fmt(x,d):return str(Decimal(repr(x)).quantize(Decimal('1') if d==0 else Decimal('0.1'),rounding=ROUND_HALF_UP))
HERE=os.path.dirname(os.path.abspath(__file__));PKG=os.path.dirname(HERE)
def find(name):
    p=os.path.join(HERE,'results',name)
    return p if os.path.exists(p) else os.path.join(HERE,name)
RES=find('results_fresh_v103.csv.gz')
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
EX=json.load(open(find('results_exploits_v103.json')))
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
# ---- 128-seed tables: lookahead Japan, search player, references, map reading (from the stored logs)
def logrows(name):
    out={}
    for line in open(find(name)):
        m=re.match(r'^(look|lookc)( K=16 S=4)? (\w+) (\d+) win ([\d.]+)',line)
        if m:n=int(m.group(4));out[m.group(3)]=round(float(m.group(5))*n)/n      # the log rounds to 3 decimals: recover the count
    return out
for label,name in (('look: adaptive values','v103_look.log'),('lookc: counter values, 8 moves','v103_lookc.log'),('lookc, wide','v103_lookdeep.log')):
    rowdata=logrows(name)
    line=re.search(r'^\| '+re.escape(label)+r'[^|]*\| (\d+)% \| (\d+)% \| (\d+)% \| (\d+)% \| (\d+)% \|$',rep,re.M)
    if not line:bad.append(f'lookahead table: no row for {label}');continue
    for k,l in enumerate(LEVELS):check(f'lookahead {label}/{l}',line.group(k+1),fmt(100*rowdata[l],0))
ex={}
for line in open(find('v103_lookexpert.log')):
    m=re.match(r'^expert vs lookc (\d+) (\d+) (\d+) ([\d.]+)',line)
    if m:n=int(m.group(3));ex[(m.group(1),m.group(2))]=round(float(m.group(4))*n)/n
for (k,sm),label,agentlog in ((('8','3'),'lookc, 8 moves × 3 cards','v103_lookc.log'),(('16','4'),'lookc, 16 moves × 4 cards','v103_lookdeep.log')):
    line=re.search(r'^\| '+re.escape(label)+r' \| (\d+)% \| (\d+)% \|$',rep,re.M)
    if not line:bad.append(f'search-player table: no row for {label}');continue
    check(f'search player vs {label}',(line.group(1),line.group(2)),(fmt(100*ex[(k,sm)],0),fmt(100*logrows(agentlog)['agent'],0)))
H=json.load(open(find('results_holdout1_v103.json')));hw=sum(r['winner']=='Force 136' for r in H)
m=re.search(r"where Agent wins ([\d.]+)% \((\d+) games\)",rep)
if not m:bad.append('holdout sentence missing')
else:check('holdout 1 Agent',(m.group(1),m.group(2)),(fmt(100*hw/len(H),1),str(hw)))
REF=json.load(open(find('refs_v103.json')))
for key,pat in (('gpt_v0.2',r"v0\.2 paper bot, run in the same executor, won ([\d.]+)% \(mean Resistance ([\d.]+)\)"),
                ('gpt_primary_guard',r'"primary \+ recovery/guard"\) won ([\d.]+)% \(mean Resistance ([\d.]+)\)'),
                ('expert',r"A one-step search player won ([\d.]+)% \(mean Resistance ([\d.]+)\)")):
    m=re.search(pat,rep)
    if not m:bad.append(f'reference sentence missing: {key}');continue
    check(f'reference {key}',(m.group(1),m.group(2)),(fmt(100*REF[key]['win'],1),fmt(REF[key]['R'],1)))
for p in POLS:
    line=re.search(r'^\| '+p+r' \|(?: \d+% \|){5} (\d+)% \|$',rep,re.M)
    if not line:bad.append(f'search-player column: no row for {p}');continue
    check(f'search-player column {p}',line.group(1),fmt(100*REF['expert']['per'][p][0],0))
corner=[round(float(l.split()[2])*768)/768 for l in open(find('v103_corner.log')) if l.startswith('corner')]
m=re.search(r'Agent wins ([\d.]+)% instead of ([\d.]+)% \(holdout 1\)',rep)
if not m:bad.append('map-reading sentence missing')
else:check('map reading',(m.group(1),m.group(2)),(fmt(100*corner[1],1),fmt(100*corner[0],1)))
print('\n'.join(bad) if bad else 'all printed results match the stored v1.0.3 results')
sys.exit(1 if bad else 0)
