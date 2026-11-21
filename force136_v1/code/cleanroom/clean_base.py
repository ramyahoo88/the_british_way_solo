"""Scaffolding for a clean-room Force 136 implementation.

Provides: level setup, the Directive deck shuffle (must stay as is so decks match),
the Legend bonus, and the Propaganda sequence with British decision hooks.
Everything else is in engine.py (game rules + Japanese policies) and expert.py (FastGame).
"""
from engine import *
from expert import FastGame
import random,json
from pathlib import Path
CARDS=json.loads((Path(__file__).parent/'cards.json').read_text())
LEVELS={'recruit':dict(raid=False,start_r=2,bonus=0),'agent':dict(raid=True,start_r=2,bonus=0),
        'veteran':dict(raid=True,start_r=4,bonus=0),'legend':dict(raid=True,start_r=4,bonus=1)}
class CleanBase(FastGame):
    def __init__(self,seed,corner=False,level='agent'):
        FastGame.__init__(self,seed,corner)
        self.level=level;self.L=LEVELS[level];self.resistance=self.L['start_r']
        self.dqueue=[];self.ddisc=[];self.dcycle=0;self.directive=None
    def draw_directive(self):
        """Draw the next Directive card into self.directive (a dict from cards.json). Do not change."""
        if not self.dqueue:
            cards=list(self.ddisc) if self.ddisc else list(CARDS)
            random.Random(stable(self.seed,'directive',self.dcycle)).shuffle(cards)
            self.dcycle+=1;self.dqueue=cards;self.ddisc=[]
        self.directive=self.dqueue.pop(0);self.ddisc.append(self.directive)
    def score_only(self,final=False):
        r=FastGame.score_only(self,final)
        if self.L['bonus'] and not final:self.resistance=clamp(self.resistance+self.L['bonus'])
        return r
    # ---- British hooks used during nonfinal Propaganda (implement in your subclass)
    def british_resources_phase(self):raise NotImplementedError
    def british_redeploy(self):raise NotImplementedError
    def j25_return_space(self,camp_provinces):raise NotImplementedError
    def propaganda(self,final=False):
        result=self.score_only(final);self.record('Final scoring' if final else 'Nonfinal scoring',result)
        if final:return result
        b=self.board
        self.british_resources_phase()
        self.construct()                  # Japanese Construct (engine policy)
        self.supply()                     # British Supply (your supply())
        self.reprisal()                   # Japanese Reprisal (engine policy)
        self.british_redeploy()
        sites=[s for s in ORDER if b[s]['troops']>gs(b[s])]   # Japanese Redeploy (engine policy)
        if sites:
            movable=0
            for s in ORDER:
                keep=min(b[s]['police'],1) if s not in sites and b[s]['force136'] and b[s]['kempeitai'] else 0
                movable+=b[s]['police']-keep;b[s]['police']=keep
            ranked=sorted(sites,key=lambda s:(bool(b[s]['police']),not bool(b[s]['force136']),ix(s)))
            for i in range(movable):b[ranked[i%len(ranked)]]['police']+=1
            total=self.count('kempeitai')
            for v in b.values():v['kempeitai']=0
            ranked=sorted(sites,key=lambda s:(not bool(b[s]['force136']),gs(b[s])-b[s]['police'],ix(s)))
            for i in range(total):b[ranked[i%len(ranked)]]['kempeitai']+=1
        for v in b.values():
            v['terror']=0
            for c in ['red','blue']:v[c+'_u']+=v[c+'_a'];v[c+'_a']=0
        self.reset_intel(self.campaign)
        b['Kuala Lumpur']['troops']+=self.away_troops;self.away_troops=0
        if self.away_f:
            camps=[s for s in PROV if b[s]['camp']]
            if camps:b[self.j25_return_space(camps)]['force136']+=self.away_f
            self.away_f=0
        self.campaign+=1;self.first='B';self.regular_seen=0;self.chosen={};self.record('Reset complete',{})
        return result
