"""GPT review fixtures (review of commit 615c870), rewritten as tests of the revised code.

Each fixture reproduces a setup from GPT's evidence package (probe_findings.py, regression_checks.py)
and asserts the behaviour v1.0 (revised) must now have. Run from this folder: python3 review_fixtures.py
"""
import sys,os,copy
HERE=os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0,HERE)
for d in (os.path.join(HERE,'cleanroom'),os.path.join(os.path.dirname(HERE),'cleanroom')):
    if os.path.exists(os.path.join(d,'cleanroom.py')):sys.path.append(d);break
import force136_v1 as F,cleanroom as C,verify_v1 as T
from engine import new_board,BOXES
ok=[]
def passed(name):ok.append(name);print('PASS',name)

# F2 / R2: British J22 — Gather reveals but does not activate (both implementations).
a=F.Force136(139002);b=C.CleanForce136(139002)
for h in (a,b):h.cap[22]='U'
ra=a.gather();rb=b.gather()
und=lambda g:sum(v['red_u']+v['blue_u'] for v in g.board.values())
assert ra==rb and len(ra)==6 and und(a)==8 and und(b)==8 and a.board==b.board
passed('J22 British: Gather reveals 6, all 8 guerrillas stay Underground, boards equal')

# F2 / R3: British J27 — Ambush adds the first non-F136 space where it is useful.
a=F.Force136(139003);b=C.CleanForce136(139003)
for h in (a,b):
    h.board['Pahang']['red_u']+=1;h.board['Pahang']['police']=1;h.board['Johore']['red_u']-=1
    h.cap[27]='U';h.invariants()
a.strike();b.strike()
assert a.board['Pahang']['police']==0 and a.board==b.board
passed('J27 British: Ambush adds Pahang, removes its Police, boards equal')

# Q1: British J27 — Sabotage adds the first non-F136 space in map order (Kedah at standard setup).
a=F.Force136(139004);b=C.CleanForce136(139004)
for h in (a,b):h.cap[27]='U'
ha=a.rail();hb=b.sabotage_op()
assert ha==hb and a.board==b.board and a.sabotage==b.sabotage
kedah=[r for r in ha if r.startswith('Thailand-Kedah')]
assert kedah,ha
passed(f'J27 British: Sabotage extra space is Kedah (map order); railways {ha}')

# Q1: the extra space never makes a goal qualify.
g=F.Force136(139005);g.board=new_board()
g.board['Perak'].update(force136=1,camp=True)                       # F136 space: no guerrilla, nothing useful
g.board['Pahang'].update(red_u=1,police=1)                          # non-F136 space where Ambush would be useful
g.cap[27]='U';g.directive=F.DECK[0]
assert not g.useful_ambush() and g.goal('AMBUSH',True) is None
c=C.CleanForce136(139005);c.board=copy.deepcopy(g.board);c.cap[27]='U'
assert c._qualifies('AMBUSH','Op & SA') is None
passed('J27 British: extra space alone does not qualify AMBUSH (both implementations)')

# F4: British J8 changes eligibility, not the limit.
g=F.Force136(139014);g.board=new_board();g.track_cache=1;g.zipper=6;g.cap[8]='U'
for s in ['Kedah','Perak','Kelantan']:g.board[s].update(camp=True,red_u=1)
for s in ['Kedah','Perak']:g.board[s]['force136']=1
assert g.supply()==2 and not g.board['Kelantan']['cache']
passed('J8 British: two F136 Provinces fill the limit; the Province without F136 is not added')

# F3 / R1: exhausted pools. Refresh is legal (rule 1.4.1); v1.0.1 uses it when no other source exists.
g=F.Force136(139001);g.board=new_board()
g.board['Kuala Lumpur'].update(troops=15,police=6,kempeitai=3)
g.board['Perak'].update(red_a=10,force136=1,camp=True,cache=True)
g.board['Kedah'].update(blue_a=2,force136=1,camp=True)
g.board['Negri Sembilan'].update(blue_a=2,force136=1,camp=True)
g.resistance=6;g.zipper=6;g.track_cache=1;g.invariants()
choices=[]
for card in F.DECK:
    g.directive=card;choices.append(g.choose(BOXES))
assert all(c['op']=='TRAIN' for c in choices),choices
g.directive=F.DECK[3];plan=g.choose(BOXES);g.execute(plan);g.invariants()
assert plan['op']=='TRAIN' and plan.get('sa')=='SUPPLY' and sum(v['cache'] for v in g.board.values())==3
passed('Exhausted pools (v1.0.1): every Directive Trains by re-placing Active guerrillas; Directive 4 then Supplies 2 Caches')

# F1 / R4: the new comparator rejects a Resistance difference and a missing turn.
A=T.Box();B=T.Box()
A.items=[('turn',1,'x',18)];B.items=[('turn',1,'x',20)]
assert T.compare(A,B)
B.items=A.items+A.items
assert T.compare(A,B)
passed('Comparator: rejects a Resistance difference and an extra trace entry')

# F1: GPT's negative control (secondary adds 1 Resistance before final scoring). GPT's witness game was
# seed 20007/counter/Agent under v1.0; v1.0.1 changes that game, so check a range: every game whose
# final Resistance the mutant changes must be flagged, and unchanged pairs must agree.
class FinalPlusOne(C.CleanForce136):
    def score_only(self,final=False):
        if final:self.resistance=min(20,self.resistance+1)
        return C.CleanForce136.score_only(self,final)
changed=caught=0
for seed in range(20000,20016):
    assert not any(T.check(seed,'counter','agent').get(k) for k in ('cross','oracle'))
    a,ra=T.play(F.Force136,seed,'counter','agent');b,rb=T.play(FinalPlusOne,seed,'counter','agent')
    o=T.check(seed,'counter','agent',None,Q=FinalPlusOne)
    if ra!=rb:
        changed+=1;assert o['cross'] and o['oracle'];caught+=1
assert changed>0
passed(f'GPT +1 final-scoring mutant: {caught} of {changed} changed games caught by both checks; 16 unchanged pairs agree')
print(len(ok),'fixtures passed')
