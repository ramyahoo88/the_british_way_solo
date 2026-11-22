"""Fixed-position tests from the reviews of commits 615c870, 33745a6, 338cb0d and 595f409, and for v1.1's Event step.

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

# ---------------------------------------------------------------- GPT audit of commit 33745a6
# Positions from GPT's evidence package (fixtures/audit_33745a6/*.json), loaded with its restore() recipe.
import json
from copy import deepcopy
from pathlib import Path
FX=Path(HERE)/'fixtures'/'audit_33745a6'
def restore(name,cls=F.Force136):
    d=json.loads((FX/(name+'.json')).read_text());g=cls(d['seed'],level=d['level'])
    for k,v in d.items():setattr(g,k,({int(a):b for a,b in v.items()} if k=='cap' else set(v) if k=='removed_intel' else v))
    g.invariants();return g
pos=lambda x:{s:v['force136'] for s,v in x.board.items() if v['force136']}

# F1: a stack of exposed markers redeploys every marker, one at a time.
g=restore('F1_stacked_redeploy');c=restore('F1_stacked_redeploy',C.CleanForce136)
g.propaganda();c.propaganda();g.invariants()
assert pos(g)=={'Kedah':1,'Kelantan':1,'Trengganu':1}==pos(c) and g.board==c.board
g=restore('F1_stacked_redeploy');g.board['Perak']['force136']=1;g.board['Johore']['force136']=0
c=restore('F1_stacked_redeploy',C.CleanForce136);c.board=deepcopy(g.board)
g.propaganda();c.propaganda();assert g.board==c.board
g=restore('F1_stacked_redeploy');c=restore('F1_stacked_redeploy',C.CleanForce136)
for x in (g,c):
    for v in x.board.values():v['camp']=False
    x.propaganda()
assert g.board==c.board and pos(g)=={'Perak':2,'Johore':1}
passed('F1 Redeploy: stacked exposed markers all move (Kedah, Kelantan, Trengganu); single-marker and no-destination controls agree')

# F2: Japanese J27 removes Opposition from the chosen Province WITH Opposition; reference says so.
g=restore('F2_J27_reference');assert g.supply()==2 and not g.board['Negri Sembilan']['opposition']
for opposed,want in ((['Trengganu','Negri Sembilan'],'Trengganu'),([],None)):
    g=restore('F2_J27_reference');sel=['Trengganu','Negri Sembilan']
    for s_ in sel:g.board[s_]['opposition']=s_ in opposed
    before={s_:g.board[s_]['opposition'] for s_ in sel};g.supply()
    assert [s_ for s_ in sel if before[s_] and not g.board[s_]['opposition']]==([want] if want else [])
PR=Path(HERE).parent/'print'
src=(PR/'build.py').read_text()
assert 'Japanese J27: remove Opposition from the chosen Province <em>with Opposition</em>' in src
passed('F2 J27: Negri Sembilan loses Opposition (not Neutral Trengganu); both/none controls; reference text has "with Opposition"')

# F3: the stress policies keep their contracts.
g=restore('F3_eventhog_before_japan');g.policy='eventhog';g.japan_turn(['Limited','Event'])
assert g.chosen['J']=='Event'
g=restore('F3_tempo_before_japan');g.policy='tempo';g.japan_turn(['Limited','Event'])
assert g.chosen['J']=='Limited'
viol={};offered={}
for pol,box in (('eventhog','Event'),('tempo','Limited')):
    viol[pol]=offered[pol]=0
    for seed in range(20000,20004):
        class Watch(F.Force136):
            def japan_turn(self,free):
                ok=box in free and not (box=='Event' and self.event in (6,9))
                F.Force136.japan_turn(self,free)
                if ok:
                    offered[pol]+=1
                    if self.chosen['J']!=box:viol[pol]+=1
        w=Watch(seed);w.policy=pol;w.run()
assert all(offered[p]>0 and viol[p]==0 for p in viol),(offered,viol)
passed(f'F3 stress policies: fixtures choose Event and Limited; over 8 games {offered} offers, 0 violations')

# F5: a Pass may use the Event box (legal, rule 2.4.3) and the printed text says so.
g=restore('F5_event_box_pass');g.directive=F.DECK[0]
plan=g.choose(['Event','Op & SA']);assert plan['op']=='PASS' and plan['box']=='Event'
rules=(PR/'Force_136_v1_Rules.md').read_text()
assert 'even if that is the Event box' in rules and 'never chooses the Event box' not in rules
assert 'Otherwise never execute an Event' in src
passed('F5 Pass: Event-box Pass is legal and the rules, reference and cards no longer forbid it')

# ---------------------------------------------------------------- full audit of v1.0.2 (commit 338cb0d)
# A1: Japan removes an Underground guerrilla first (Food Shortage icon).
for cls in (F.Force136,C.CleanForce136):
    g=cls(3380001);g.board=new_board();b=g.board
    b['Kuala Lumpur'].update(troops=15,police=3,kempeitai=3)
    b['Pahang'].update(red_u=1,red_a=1)
    g.invariants();g.icon(5)                                   # J5 carries Food Shortage
    assert (b['Pahang']['red_u'],b['Pahang']['red_a'])==(0,1),cls
passed('A1 Food Shortage: Japan removes the Underground guerrilla, not the Active one (both bots)')

# A2: at Japanese Redeploy a Kempeitai already with a Force 136 marker stays; the others move.
# A3: the J25 marker returns where Japan chooses: the Camp Province with Kempeitai.
for cls in (F.Force136,C.CleanForce136):
    g=cls(3380002);g.board=new_board();b=g.board
    b['Kuala Lumpur'].update(troops=9,police=1)
    b['Perak'].update(force136=1,camp=True,red_u=3,troops=1,kempeitai=1)      # Troops <= guerrillas: not a destination
    b['Trengganu'].update(troops=5,kempeitai=1)                               # an ordinary Kempeitai
    b['Johore'].update(camp=True,kempeitai=1)                                 # Camp Province with Kempeitai, no Troops
    b['Kedah'].update(camp=True,blue_u=1)
    g.away_f=1;g.lost_cache=3                                                 # no Cache Available: Supply leaves Perak's Camp
    g.invariants();g.propaganda(False);g.invariants()
    assert b['Perak']['kempeitai']==1,(cls,'the Kempeitai left the Force 136 marker')
    assert b['Johore']['kempeitai']==0 and g.count('kempeitai')==3,cls
    assert b['Perak']['force136']==2 and g.away_f==0,(cls,{s:v['force136'] for s,v in b.items() if v['force136']})
passed('A2/A3 Reset: the Kempeitai stays with Force 136 in Perak; the J25 marker returns beside it (Japan\'s choice)')

# A4: British J12 and J15 follow the printed lines in both bots.
for cls in (F.Force136,C.CleanForce136):
    g=cls(3380003);g.board=new_board();b=g.board
    b['Kuala Lumpur'].update(troops=15,police=3,kempeitai=3)
    b['Pahang'].update(new_village=True,blue_u=1,red_u=1,police=0);b['Kuala Lumpur']['troops']-=1;b['Pahang']['troops']=1
    b['Selangor'].update(new_village=True);b['Kuala Lumpur']['troops']-=1;b['Selangor']['troops']=1
    g.cap[15]='U';g.invariants();g.extract()
    assert b['Pahang']['red_u']==2 and b['Selangor']['red_u']==1 and b['Selangor']['blue_u']==0,cls
    g=cls(3380004);g.board=new_board();b=g.board
    b['Kuala Lumpur'].update(troops=15,police=3,kempeitai=3);b['Perak']['terror']=1;b['Negri Sembilan']['terror']=1
    g.sabotage['Perak-Kelantan']=1;g.sabotage['Negri Sembilan-Johore *']=1;g.cap[12]='U';g.invariants()
    g.repair('Perak-Kelantan',True);g.repair('Negri Sembilan-Johore *',True)
    assert b['Perak']['opposition'] and not b['Kelantan']['opposition'],cls            # highest Population first, even with Terror
    assert b['Johore']['opposition'] and not b['Negri Sembilan']['opposition'],cls     # equal Population: the one without Terror
passed('A4 British J15: red on a tie and in an empty New Village; British J12: highest Population, then no Terror')

# ---------------------------------------------------------------- GPT audit of commit 595f409
# P1: the flowchart must not forbid an Event-box Pass; D1: the level footnote must not say "before every move".
svg=(PR/'turn_flow.svg').read_text()
assert 'Never the Event box' not in svg and 'Otherwise never execute the Event.' in svg
readme=' '.join((Path(HERE).parent/'README.md').read_text().split())
assert 'before every move' not in rules and 'whenever Japan acts first on a card' in readme
assert 'simulat' not in rules.lower() and 'computer' not in rules.lower()          # v1.1 cleanup: the booklet is rules only
passed('P1/D1 print: flowchart says "Otherwise never execute the Event."; lookahead wording correct; rules booklet free of simulation text')
# ---------------------------------------------------------------- v1.1: step 4.2, J4 and J25 as second to act
def ev_setup(cls,seed,j,japan):
    g=cls(seed);g.board=new_board();b=g.board
    b['Kuala Lumpur'].update(troops=15,police=3,kempeitai=3)
    b['Perak'].update(force136=1,camp=True,red_u=2,cache=True)
    b['Kedah'].update(force136=1,camp=True,blue_u=1)
    b['Johore'].update(red_u=1)
    g.event=j;g.chosen={'J':japan} if japan else {};g.resistance=5;g.invariants();return g
for cls in (F.Force136,C.CleanForce136):
    g=ev_setup(cls,1100001,4,'Op & SA');g.bot_turn(['Limited','Event'])
    assert g.last_plan['op']=='EVENT' and g.last_plan['box']=='Event' and g.resistance==7,(cls,g.last_plan,g.resistance)
    g=ev_setup(cls,1100002,4,None);g.bot_turn(['Limited','Event','Op & SA'])         # Force 136 first: no Event
    assert g.last_plan['op']!='EVENT' and g.last_plan['box']=='Op & SA',(cls,g.last_plan)
    g=ev_setup(cls,1100003,4,'Op & SA');g.board['Perak']['camp']=False;g.board['Kedah']['camp']=False
    g.bot_turn(['Limited','Event']);assert g.last_plan['op']!='EVENT',(cls,'J4 with no Force 136 Camp taken')
    g=ev_setup(cls,1100004,7,'Op & SA');g.bot_turn(['Limited','Event'])              # an unlisted Event: never
    assert g.last_plan['op']!='EVENT',cls
passed('4.2 J4: taken only as second to act and only if it scores (+1 per F136 Camp space); never as first player or on other cards')
boards=[]
for cls in (F.Force136,C.CleanForce136):
    g=ev_setup(cls,1100005,25,'Op & SA');g.bot_turn(['Limited','Event'])
    assert g.last_plan['op']=='EVENT' and g.last_plan['box']=='Event',(cls,g.last_plan)
    assert g.count('force136')==3,(cls,'J25 Contact did not place the Available marker')
    boards.append((g.board,g.sabotage,g.resistance))
assert boards[0]==boards[1]
passed('4.2 J25: Contact places the Available marker, then the CONTACT Special Activity; both bots end on the same board')
rules=(PR/'Force_136_v1_Rules.md').read_text()
assert '**J4 Chin Peng**' in rules and '**J25 John Davis**' in rules and 'never executes an Event' not in rules
assert 'J4 or J25' in svg and 'J4 / J25' in src
passed('4.2 print: rules, flowchart and reference/cards name J4 and J25')
print(len(ok),'fixtures passed')
