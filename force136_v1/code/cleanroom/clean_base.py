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
        'veteran':dict(raid=True,start_r=4,bonus=0),'legend':dict(raid=True,start_r=4,bonus=1),
        'mastermind':dict(raid=True,start_r=6,bonus=2)}
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
    def j25_return_space(self,camp_provinces):raise NotImplementedError   # no longer called (v1.0.3: Japan chooses)
    def propaganda(self,final=False):
        result=self.score_only(final);self.record('Final scoring' if final else 'Nonfinal scoring',result)
        if final:return result
        b=self.board
        self.british_resources_phase()
        self.construct()                  # Japanese Construct (engine policy)
        self.supply()                     # British Supply (your supply())
        self.reprisal()                   # Japanese Reprisal (engine policy)
        self.british_redeploy()
        self.japan_redeploy()             # Japanese Redeploy (engine policy)
        for v in b.values():
            v['terror']=0
            for c in ['red','blue']:v[c+'_u']+=v[c+'_a'];v[c+'_a']=0
        self.reset_intel(self.campaign)
        b['Kuala Lumpur']['troops']+=self.away_troops;self.away_troops=0
        self.j25_return()                 # J25 marker returns: Japan's choice (rule 5.1; engine policy, v1.0.3)
        self.campaign+=1;self.first='B';self.regular_seen=0;self.chosen={};self.record('Reset complete',{})
        return result
