import force136_v1 as F
from engine import *
B=F.Force136
class GatherFirst(B):
    """For AMBUSH+GATHER and INTEL(Ambush), Gather before the Ambush."""
    def execute(self,plan):
        if plan['op']=='AMBUSH' and plan.get('sa')=='GATHER':
            self.gather();self.strike();return
        return B.execute(self,plan)
class MobNoBlue(B):
    def opp_pick(self,sites):
        return min(sites,key=lambda s:(bool(blue(self.board[s])),-POP[s],F.mo(s)))
class KempFirst(B):
    def ambush_target(self,s,color=None):
        v=self.board[s]
        if not (v[color+'_u'] if color else ug(v)):return None
        if s!='Kuala Lumpur' and v['kempeitai'] and self.good_shot(s):return 'Kempeitai'
        return B.ambush_target(self,s,color)
def Shot(th):
    class S(B):
        def good_shot(self,s):return cubes(self.board[s])-self.cache_bonus(s)<=th
    return S
def PlaceTerrain(pref):
    class P(B):
        def place_key(self,s):
            k=B.place_key(self,s);t=(s not in MOUNTAIN) if pref=='mountain' else (s in MOUNTAIN)
            return k[:3]+(t,)+k[3:]
    return P
class RaidNoTroops(B):
    def raid(self):
        return B.raid(self)
class SupplySafe(B):
    def supply(self):
        # prefer sites with no Troops in or adjacent
        return B.supply(self)
class KempJungle(KempFirst):
    def place_key(self,s):
        k=B.place_key(self,s);return k[:3]+((s in MOUNTAIN),)+k[3:]
class KempTroopFirst(B):
    # any good shot (Kempeitai, then Troop) before Police
    def ambush_target(self,s,color=None):
        v=self.board[s]
        if not (v[color+'_u'] if color else ug(v)):return None
        if s!='Kuala Lumpur' and self.good_shot(s):
            if v['kempeitai']:return 'Kempeitai'
            if v['troops']:return 'Troop'
        return B.ambush_target(self,s,color)
def Shot2(th):
    class S(B):
        def good_shot(self,s):return cubes(self.board[s])-self.cache_bonus(s)<=th
    return S
import copy
class RedeployIdle(B):
    def propaganda(self,final=False):
        # wrap: temporarily mark idle markers as exposed during redeploy
        self._idle=True
        try:return B.propaganda(self,final)
        finally:self._idle=False
    def exposed(self,s):
        v=self.board[s]
        if getattr(self,'_idle',False) and v['force136'] and gs(v)==0:return True
        return B.exposed(self,s)
class RedeployUG(B):
    def propaganda(self,final=False):
        self._idle=True
        try:return B.propaganda(self,final)
        finally:self._idle=False
    def exposed(self,s):
        v=self.board[s]
        if getattr(self,'_idle',False) and v['force136'] and gs(v)<=1 and not v['cache']:return True
        return B.exposed(self,s)
def FinalSupply(minR):
    class FS(B):
        def choose(self,free):
            if self.campaign==3 and self.resistance>=minR and self.count('camp')>=self.count('force136') and 'Op & SA' in free:
                p=self.goal('SUPPLY',True)
                if p:return dict(p,box='Op & SA',goal='SUPPLY')
            return B.choose(self,free)
    return FS
def GatherSafe(mode):
    class GS(B):
        def gather_targets(self,anchor,allow_adj=True):
            t=B.gather_targets(self,anchor,allow_adj)
            if mode=='notroops':return [s for s in t if not self.board[s]['troops']]
            if mode=='keepug':return [s for s in t if not(self.board[s]['troops'] and ug(self.board[s])==1)]
            return t
    return GS
VARIANTS={'gather_notroops':GatherSafe('notroops'),'gather_keepug':GatherSafe('keepug'),'final_supply0':FinalSupply(0),'final_supply12':FinalSupply(12),'final_supply15':FinalSupply(15),'redeploy_idle':RedeployIdle,'redeploy_thin':RedeployUG,'shot_le2':Shot2(2),'shot_le4':Shot2(4),'kempjungle':KempJungle,'kemptroop':KempTroopFirst,'base':B,'gatherfirst':GatherFirst,'mobnoblue':MobNoBlue,'kempfirst':KempFirst,'shot2':Shot(2),'shot4':Shot(4),
          'place_mountain':PlaceTerrain('mountain'),'place_jungle':PlaceTerrain('jungle')}
