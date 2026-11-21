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
class LimShot(B):
    # Limited: PLACE > AMBUSH only at a good shot > TRAIN > AMBUSH (Police) > CONTACT
    def choose(self,free):
        if 'Op & SA' not in free and 'Limited' in free:
            for g in ['PLACE','SHOT','TRAIN','AMBUSH','CONTACT']:
                if g=='SHOT':
                    if any(self.ambush_target(s) in('Kempeitai','Troop') for s in self.f136_spaces()):return dict(op='AMBUSH',box='Limited',goal='AMBUSH')
                    continue
                p=self.goal(g,False)
                if p:return dict(p,box='Limited',goal=g)
        return B.choose(self,free)
class BigGatherFirst(B):
    def choose(self,free):
        if 'Op & SA' in free and self.available('force136'):
            p=self.goal('INTEL',True)
            if p:
                q=self.clone()
                if p['op']=='AMBUSH':q.strike()
                elif p['op']=='SABOTAGE':q.rail('C')
                else:q.contact()
                if len(q.clone().gather())>=3:return dict(p,box='Op & SA',goal='INTEL')
        return B.choose(self,free)
class SupplySafe2(B):
    def supply(self):
        # same as base but prefer Provinces with no Troops in or adjacent before 'most guerrillas'
        limit=min(3 if self.zipper>=12 else 2,self.available('cache'))
        selected=[];remote=False;b=self.board
        def threat(s):return bool(b[s]['troops'] or any(b[x]['troops'] for x in ADJ[s]))
        while len(selected)<limit:
            sites=[s for s in PROV if b[s]['camp'] and not b[s]['cache'] and s not in selected and (b[s]['force136'] or self.cap.get(8)=='U' and not remote)]
            if not sites:break
            s=min(sites,key=lambda s:(not b[s]['force136'],bool(b[s]['kempeitai']),threat(s),-gs(b[s]),-POP[s],F.mo(s)))
            selected.append(s)
            if not b[s]['force136']:remote=True
        n=0
        for s in selected:
            if self.cap.get(8)=='S' and self.die('Supply',s)<=2:continue
            b[s]['camp']=False;b[s]['cache']=True;n+=1
        if self.cap.get(27)=='S' and selected:
            el=[s for s in selected if b[s]['opposition']]
            if el:b[min(el,key=lambda s:(POP[s],F.mo(s)))]['opposition']=False
        self.cleanup();return n
class RaidKeep2(B):
    def donor_ok(self,s,n=1):
        v=self.board[s]
        if v['cache'] and gs(v)-n<2:return False
        return B.donor_ok(self,s,n)
class GuardFirst(B):
    def thin(self):
        b=self.board
        for s in self.f136_spaces():
            v=b[s]
            if v['cache'] and ug(v)<=1 and (v['troops'] or any(b[x]['troops'] for x in ADJ[s])):return True
        return False
    def choose(self,free):
        if self.thin():
            p=self.clone()
            if p.train():
                if 'Op & SA' in free:return dict(op='TRAIN',sa_list=('SUPPLY','RAID'),box='Op & SA',goal='TRAIN')
        return B.choose(self,free)
class KeepCacheUG(B):
    def protected(self,s):
        v=self.board[s];b=self.board
        return v['cache'] and ug(v)<=1 and (v['troops'] or any(b[x]['troops'] for x in ADJ[s]))
    def gather_targets(self,anchor,allow_adj=True):
        return [s for s in B.gather_targets(self,anchor,allow_adj) if not self.protected(s)]
    def ambush_target(self,s,color=None):
        if self.protected(s):return None
        return B.ambush_target(self,s,color)
def DeckVar(goals,lim):
    class DV(B):
        deck_cards=[F.card(i,'x',list(goals),lim) for i in range(1,10)]
    return DV
class DeckAllT(B):
    deck_cards=[dict(c,limited_first='TRAIN') for c in F.DECK]
class DeckAllA(B):
    deck_cards=[dict(c,limited_first='AMBUSH') for c in F.DECK]
def SupplyGuard(minug):
    class SG(B):
        def supply(self):
            limit=min(3 if self.zipper>=12 else 2,self.available('cache'))
            selected=[];remote=False;b=self.board
            while len(selected)<limit:
                sites=[s for s in PROV if b[s]['camp'] and not b[s]['cache'] and s not in selected and ug(b[s])>=minug and (b[s]['force136'] or self.cap.get(8)=='U' and not remote)]
                if not sites:break
                s=min(sites,key=lambda s:(not b[s]['force136'],bool(b[s]['kempeitai']),-gs(b[s]),-POP[s],F.mo(s)))
                selected.append(s)
                if not b[s]['force136']:remote=True
            n=0
            for s in selected:
                if self.cap.get(8)=='S' and self.die('Supply',s)<=2:continue
                b[s]['camp']=False;b[s]['cache']=True;n+=1
            if self.cap.get(27)=='S' and selected:
                el=[s for s in selected if b[s]['opposition']]
                if el:b[min(el,key=lambda s:(POP[s],F.mo(s)))]['opposition']=False
            self.cleanup();return n
    return SG
class IntelNoSab(B):
    def goal(self,name,full):
        if name!='INTEL':return B.goal(self,name,full)
        if not full:return None
        for op in ('AMBUSH','CONTACT'):
            p=self.clone()
            if op=='AMBUSH':
                if not self.useful_ambush():continue
                p.strike()
            elif not p.contact():continue
            if len(p.clone().gather())>=2:return dict(op=op,sa='GATHER')
        return None
VARIANTS={'intel_nosab':IntelNoSab,'supply_ug1':SupplyGuard(1),'supply_ug2':SupplyGuard(2),'deck9_T':DeckAllT,'deck9_A':DeckAllA,'deck_AIT_A':DeckVar(['AMBUSH','INTEL','TRAIN'],'AMBUSH'),'deck_AIT_T':DeckVar(['AMBUSH','INTEL','TRAIN'],'TRAIN'),
 'deck_IAT_A':DeckVar(['INTEL','AMBUSH','TRAIN'],'AMBUSH'),'deck_ASIT_T':DeckVar(['AMBUSH','SUPPLY','INTEL','TRAIN'],'TRAIN'),
 'deck_TAI_T':DeckVar(['TRAIN','AMBUSH','INTEL'],'TRAIN'),'guardfirst':GuardFirst,'keepcacheug':KeepCacheUG,'supplysafe':SupplySafe2,'raidkeep2':RaidKeep2,'limshot':LimShot,'biggather':BigGatherFirst,'gather_notroops':GatherSafe('notroops'),'gather_keepug':GatherSafe('keepug'),'final_supply0':FinalSupply(0),'final_supply12':FinalSupply(12),'final_supply15':FinalSupply(15),'redeploy_idle':RedeployIdle,'redeploy_thin':RedeployUG,'shot_le2':Shot2(2),'shot_le4':Shot2(4),'kempjungle':KempJungle,'kemptroop':KempTroopFirst,'base':B,'gatherfirst':GatherFirst,'mobnoblue':MobNoBlue,'kempfirst':KempFirst,'shot2':Shot(2),'shot4':Shot(4),
          'place_mountain':PlaceTerrain('mountain'),'place_jungle':PlaceTerrain('jungle')}
def Refresh(order):
    """Train may take an Active guerrilla of the colour from the Train space itself (rule 1.4.1 example)."""
    class R(B):
        def place_one(self,s,c):
            v=self.board[s]
            if self.available(c):v[c+'_u']+=1;return True
            if order=='first' and v[c+'_a']:v[c+'_a']-=1;v[c+'_u']+=1;return True
            if B.place_one(self,s,c):return True
            if order=='last' and v[c+'_a']:v[c+'_a']-=1;v[c+'_u']+=1;return True
            return False
    return R
VARIANTS.update(refresh_first=Refresh('first'),refresh_last=Refresh('last'))
