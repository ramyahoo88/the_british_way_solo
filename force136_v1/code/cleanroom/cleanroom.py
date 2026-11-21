"""Clean-room Force 136 v1.0 bot, written from Force_136_v1_Rules.md (sections 3-7 and 9) only.

Conventions
- Every "would" test (section 3) runs on self.clone(): a preview copy whose dice are fixed
  (the engine returns 4, so an Ambush at a good shot and a J8 Supply roll both succeed:
  "assume no roll is needed") and whose concealed chits are never read.
- Nothing here reads a concealed chit value for a decision. The only line that touches
  self.secret is _reveal(), which is the physical act of turning a chit face up during Gather.
- Readings of ambiguous text are marked "READING:" in the comments.

Changes after GPT's review of commit 615c870 (made by the primary author, not the clean-room agent):
British J22 (Gather does not activate) and British J27 (one extra Ambush or Sabotage space, the first
in map order; never counted when testing whether a goal qualifies), from the revised section 7; and the
v1.0.1 Train fallback (re-place an Active guerrilla of the colour from the Train space itself, section 6.2).
v1.0.3: British J12 and J15 (new lines in section 7) were also added by the primary author, and the
Japanese Redeploy and J25 return moved into the shared engine (Japan's choices).
"""
from clean_base import CleanBase
from expert import FastGame
from engine import ORDER, PROV, POP, ADJ, MOBILIZE, KILL, BOXES, ix, gs, ug, red, blue, cubes, clamp

# Section 3: Railway list (all eight railways), in printed order.
RAILWAY_LIST = ('Perak-Pahang-Selangor', 'Negri Sembilan-Pahang', 'Perak-Kelantan', 'Thailand-Perak',
                'Thailand-Kelantan *', 'Negri Sembilan-Johore *', 'Pahang-Johore *', 'Thailand-Kedah *')
ECONOMIC_CENTERS = ('Northern EC', 'Southern EC')
OTHER = {'red': 'blue', 'blue': 'red'}

# Section 5: Special Activity lists, as (activity, minimum effect). "Gather if it would reveal
# 2 or more chits" is ('GATHER', 2); a bare entry only has to "do something" (effect >= 1).
SA_LISTS = {
    'PLACE':   [('GATHER', 2), ('SUPPLY', 1), ('RAID', 1), ('GATHER', 1)],
    'AMBUSH':  [('GATHER', 2), ('RAID', 1), ('GATHER', 1)],
    'TRAIN':   [('SUPPLY', 1), ('RAID', 1)],
    'CONTACT': [('SUPPLY', 1), ('GATHER', 1), ('RAID', 1)],
}
FIXED_SA = {'INTEL': 'GATHER', 'SUPPLY': 'SUPPLY'}   # goals whose Special Activity is part of the test


class CleanForce136(CleanBase):
    def __init__(self, seed, corner=False, level='agent'):
        CleanBase.__init__(self, seed, corner, level)
        self.last_plan = None

    # ------------------------------------------------------------------ section 3 terms
    def _exposed(self, s):
        """Exposed: a F136 marker in a space with Kempeitai and no Jungle Camp; with the
        Japanese side of J22 every F136 marker with Kempeitai is exposed."""
        v = self.board[s]
        return bool(v['force136'] and v['kempeitai'] and (not v['camp'] or self.cap.get(22) == 'S'))

    def _good_shot(self, s):
        """Good shot: cubes minus Supply Caches in and adjacent to the space is 3 or less."""
        return cubes(self.board[s]) - self.cache_bonus(s) <= 3

    def _keeps(self, s, n):
        """Donor test (6.2, 6.7): after losing n guerrillas the space keeps a guerrilla at its
        Cache and keeps its majority (if it had one)."""
        v = self.board[s]
        left = gs(v) - n
        if left < 0 or (v['cache'] and left < 1):
            return False
        return not (gs(v) > cubes(v) and left <= cubes(v))

    def _reveal(self, s):
        """Physically turn a chit face up. The value is never used by any British decision."""
        self.board[s]['intel'] = 1 if self.preview else self.secret[s]
        if self.preview:
            self.uncertain = True

    # ------------------------------------------------------------------ section 4 turn
    def bot_turn(self, free):
        self.draw_directive()                                   # 4.1 draw (base class handles discard)
        card = self.directive
        if 'Op & SA' in free:                                   # 4.3
            box = 'Op & SA'
            goals = ['PLACE'] + list(card['goals']) + ['CONTACT']
        else:                                                   # 4.4
            assert 'Limited' in free, free
            box = 'Limited'
            first = card['limited_first']
            goals = ['PLACE', first, 'TRAIN' if first == 'AMBUSH' else 'AMBUSH', 'CONTACT']
        for goal in goals:
            op = self._qualifies(goal, box)
            if not op:
                continue
            self.chosen['B'] = box
            self._do_op(self, op)
            sa = None
            if box == 'Op & SA':                                # 4.4: a Limited Operation never adds an SA
                sa = FIXED_SA.get(goal) or self._choose_sa(goal)
                if sa:
                    self.special(sa)
            self._finish(dict(goal=goal, box=box, op=op, sa=sa, directive=card['id']))
            return
        # 4.5: nothing qualifies -> Pass in the leftmost free box, with no Contact.
        box = min(free, key=BOXES.index)
        self.chosen['B'] = box
        self._finish(dict(goal='PASS', box=box, op='PASS', sa=None, directive=card['id']))

    def _finish(self, plan):
        self.last_plan = plan
        self.inc('bot_turns'); self.inc('goal_' + plan['goal']); self.inc('op_' + plan['op'])
        if plan['sa']:
            self.inc('sa_' + plan['sa'])
        self.cleanup()
        self.record('British turn', plan)

    @staticmethod
    def _do_op(g, op, extra=True):
        """Carry out an Operation on game g (the real game or a preview) and return its effect.
        Tests pass extra=False: the British J27 extra space never makes a goal qualify (section 9)."""
        if op == 'CONTACT':
            return g.contact()
        if op == 'TRAIN':
            return g.train()
        if op == 'AMBUSH':
            return g.strike(extra=extra)
        if op == 'SABOTAGE':
            return g.sabotage_op(extra=extra)
        raise ValueError(op)

    # ------------------------------------------------------------------ section 5 goals
    def _qualifies(self, goal, box):
        """Return the Operation to carry out if the goal qualifies, else None."""
        if goal == 'PLACE':                                     # a marker is Available
            return 'CONTACT' if self.available('force136') > 0 else None
        if goal == 'AMBUSH':                                    # useful in at least one F136 space
            return 'AMBUSH' if self.clone().strike(extra=False) else None
        if goal == 'INTEL':
            return self._intel_op() if box == 'Op & SA' else None
        if goal == 'SUPPLY':                                    # Train places 1+, then Supply converts a Camp
            if box != 'Op & SA':
                return None
            p = self.clone()
            return 'TRAIN' if p.train() and p.supply() else None
        if goal == 'TRAIN':
            return 'TRAIN' if self.clone().train() else None
        if goal == 'CONTACT':                                   # would place or move a marker
            return 'CONTACT' if self.clone().contact() else None
        raise ValueError(goal)

    def _intel_op(self):
        """INTEL: try Ambush, Sabotage, Contact in order, skipping any that would do nothing;
        qualify with the first after which Gather would reveal 2 or more chits."""
        for op in ('AMBUSH', 'SABOTAGE', 'CONTACT'):
            p = self.clone()
            if not self._do_op(p, op, extra=False):
                continue
            if len(p.gather()) >= 2:
                return op
        return None

    def _choose_sa(self, goal):
        """Section 5: take the first Special Activity in the goal's list that would do something.
        Section 9: at Recruit, skip Raid and go on to the next choice."""
        for sa, need in SA_LISTS[goal]:
            if sa == 'RAID' and not self.L['raid']:
                continue
            result = self.clone().special(sa)
            effect = len(result) if isinstance(result, (list, tuple)) else int(result or 0)
            if effect >= need:
                return sa
        return None

    # ------------------------------------------------------------------ 6.1 Contact
    def _place_rank(self, s):
        """6.1 placement preferences: no Kempeitai; no Supply Cache (only while a Cache is
        Available); no cubes; most guerrillas; highest Population; map order."""
        v = self.board[s]
        cache_matters = self.available('cache') > 0
        return (bool(v['kempeitai']), bool(v['cache']) if cache_matters else False,
                cubes(v) > 0, -gs(v), -POP[s], ix(s))

    def contact(self, task=None, hold=False):
        """6.1. `task` is accepted for engine compatibility and ignored; hold=True does nothing."""
        if hold:
            return []
        b = self.board
        moves = []
        if self.available('force136') > 0:                      # Place
            dests = [s for s in PROV if not b[s]['force136']]
            if dests:
                dst = min(dests, key=self._place_rank)
                b[dst]['force136'] += 1
                moves.append(('Available', dst))
        else:                                                   # Move (only when none is Available)
            for src in ORDER:
                if not self._exposed(src):
                    continue
                dests = [d for d in ADJ[src] if d in PROV and not b[d]['force136'] and not b[d]['kempeitai']]
                if not dests:
                    continue
                dst = min(dests, key=self._place_rank)
                # Escort: one blue (Underground first) if the destination has no red and
                # another guerrilla stays behind.
                if blue(b[src]) and not red(b[dst]) and gs(b[src]) >= 2:
                    field = 'blue_u' if b[src]['blue_u'] else 'blue_a'
                    b[src][field] -= 1
                    b[dst][field] += 1
                b[src]['force136'] -= 1
                b[dst]['force136'] += 1
                moves.append((src, dst))
                break
        if moves and moves[-1][1] in PROV:                      # Camp where the marker arrives
            self.add_camp(moves[-1][1])                         # engine: Camp from the map
        self.cleanup()
        return moves

    # ------------------------------------------------------------------ 6.2 Train
    def _train_colour(self, s):
        """Colour to train in s, or None if the space needs red and has no Camp or Cache."""
        v = self.board[s]
        r, bl = red(v), blue(v)
        if r or bl:
            colour = 'red' if r >= bl else 'blue'               # more of; red on a tie
        else:                                                   # empty space
            colour = 'red' if (v['camp'] or v['cache']) and self.available('red') > 0 else 'blue'
        if colour == 'red' and not (v['camp'] or v['cache']):
            return None
        return colour

    def _train_donor(self, s, colour, reserve_cache_donors=False):
        """6.2 source when no guerrilla of the colour is Available: another space without F136
        that keeps a guerrilla at its Cache and keeps its majority. Order: has an Active one of
        that colour; most cubes; map order."""
        b = self.board
        cands = [x for x in ORDER if x != s and not b[x]['force136']
                 and b[x][colour + '_u'] + b[x][colour + '_a'] > 0 and self._keeps(x, 1)
                 and not (reserve_cache_donors and b[x]['cache'])]
        if not cands:
            return None
        return min(cands, key=lambda x: (not b[x][colour + '_a'], -cubes(b[x]), ix(x)))

    def train(self, locations=None, reserve_cache_donors=False):
        """6.2: every F136 space except Economic Centers, map order; 1 guerrilla, 2 at a Cache.
        `reserve_cache_donors` is an engine-compatibility switch, not part of the printed rules."""
        b = self.board
        if locations is None:
            sites = [s for s in ORDER if b[s]['force136'] and s not in ECONOMIC_CENTERS]
        else:
            sites = sorted(locations, key=ix)
        placed = 0
        for s in sites:
            v = b[s]
            for _ in range(2 if v['cache'] else 1):
                colour = self._train_colour(s)
                if colour is None:                              # needs red, no Camp/Cache: skip space
                    break
                if self.available(colour) > 0:
                    v[colour + '_u'] += 1
                else:
                    src = self._train_donor(s, colour, reserve_cache_donors)
                    if src is not None:
                        field = colour + ('_a' if b[src][colour + '_a'] else '_u')
                        b[src][field] -= 1
                        v[colour + '_u'] += 1                   # READING: arrives Underground (placed)
                    elif v[colour + '_a']:                      # v1.0.1: re-place an Active one from here
                        v[colour + '_a'] -= 1
                        v[colour + '_u'] += 1
                    else:                                       # no source: stop training this space
                        break
                placed += 1
        self.cleanup()
        return placed

    # ------------------------------------------------------------------ 6.3 Ambush
    def _ambush_target(self, s):
        """What an Ambush in s would do, ignoring the Underground-guerrilla requirement."""
        v = self.board[s]
        if s != 'Kuala Lumpur' and self._good_shot(s):         # in Kuala Lumpur only Police removal
            if v['kempeitai']:
                return 'Kempeitai'
            if v['troops']:
                return 'Troop'
        if v['police']:
            return 'Police'
        return None

    def strike_option(self, s, force_color=None, bose=False):
        """6.3: None, or (target, success faces). Needs an Underground guerrilla (of force_color)."""
        if bose:                                                # J26 (British side) is not in the v1 rules
            return FastGame.strike_option(self, s, force_color, bose)
        v = self.board[s]
        if not (v[force_color + '_u'] if force_color else ug(v)):
            return None
        target = self._ambush_target(s)
        if target is None:
            return None
        if target == 'Police':
            return ('Police', 6)
        faces = sum(d + self.cache_bonus(s) > cubes(v) for d in range(1, 7))
        return (target, faces)

    def strike_rank(self, s, color=None, bose=False):
        """6.3: work through the spaces in map order."""
        if bose:
            return FastGame.strike_rank(self, s, color, bose)
        return (ix(s),)

    def strike(self, locations=None, color=None, bose=False, extra=True):
        """6.3 Ambush in every F136 space where it is useful (or in `locations`), map order.
        British side of J27 (an optional benefit, section 9): with `extra`, one space without
        Force 136 where Ambush is useful is added: the first in map order."""
        if bose:
            return FastGame.strike(self, locations, color, bose, False)
        b = self.board
        sites = [s for s in ORDER if b[s]['force136']] if locations is None else sorted(locations, key=ix)
        if locations is None and extra and self.cap.get(27) == 'U':
            more = [s for s in ORDER if not b[s]['force136'] and self.strike_option(s, color)]
            if more:
                sites = sorted(sites + more[:1], key=ix)
        hits = []
        for s in sites:
            opt = self.strike_option(s, color)
            if not opt:
                continue
            self.activate(s, color)                             # red before blue
            target = opt[0]
            hits.append((s, target))
            if target == 'Police':
                b[s]['police'] -= 1                             # no roll
            elif self.die('Ambush', s) + self.cache_bonus(s) > cubes(b[s]):
                field = 'kempeitai' if target == 'Kempeitai' else 'troops'
                b[s][field] -= 1
                b['Kuala Lumpur'][field] += 1
                self.resistance = clamp(self.resistance + 1)    # sections 10/11: +1 Resistance
        self.inc('ambush_attempts', len(hits))
        self.cleanup()
        return hits

    # ------------------------------------------------------------------ 6.4 Sabotage
    def rail_choice(self, s, region='C', stack=False, eligible=None):
        """First clear railway on the Railway list adjacent to s (region is ignored: v1 has one list)."""
        if stack:
            return FastGame.rail_choice(self, s, region, stack, eligible)
        for r in RAILWAY_LIST:
            if s in self.rail_adj(r) and not self.sabotage[r] and (eligible is None or r in eligible):
                return r
        return None

    def _sabotage_at(self, s, color=None):
        r = self.rail_choice(s)
        self.activate(s, color)
        self.sabotage[r] += 1
        return r

    def sabotage_op(self, extra=True):
        """6.4: F136 spaces in map order; each with an Underground guerrilla and an adjacent clear
        railway activates one (red first) and sabotages the first such railway on the list."""
        b = self.board
        sites = [s for s in ORDER if b[s]['force136']]
        if extra and self.cap.get(27) == 'U':                   # British J27: one more space, map order
            more = [s for s in ORDER if not b[s]['force136'] and ug(b[s]) and self.rail_choice(s)]
            if more:
                sites = sorted(sites + more[:1], key=ix)
        hit = []
        for s in sites:
            if ug(b[s]) and self.rail_choice(s):
                hit.append(self._sabotage_at(s))
        self.inc('sabotages', len(hit))
        return hit

    # ------------------------------------------------------------------ 6.5 Gather
    def gather(self):
        """6.5: up to 2 F136 spaces (3 with British J19), each the one that would reveal most chits
        (ties map order); Japanese J19 lets only the first chosen space use adjacent spaces."""
        b = self.board
        limit = 3 if self.cap.get(19) == 'U' else 2
        chosen, revealed = [], []
        for n in range(limit):
            allow_adj = not (self.cap.get(19) == 'S' and n > 0)
            best = None
            for s in ORDER:
                if not b[s]['force136'] or s in chosen:
                    continue
                t = self.gather_targets(s, allow_adj)
                if best is None or len(t) > len(best[1]):
                    best = (s, t)
            if best is None or not best[1]:                     # READING: stop when none would reveal
                break
            chosen.append(best[0])
            for t in best[1]:
                if self.cap.get(22) != 'U':                     # British J22: Gather does not activate
                    self.activate(t)                            # red before blue
                self._reveal(t)
                revealed.append(t)
        self.inc('gather_reveals', len(revealed))
        return revealed

    # ------------------------------------------------------------------ 6.6 Supply
    def supply(self):
        """6.6: convert Camps in F136 Provinces with a Camp and no Cache. Limit 2, or 3 at Zipper 12
        (READING: Zipper 12 or higher), and no more than the Caches Available."""
        b = self.board
        limit = min(3 if self.zipper >= 12 else 2, self.available('cache'))
        if limit <= 0:
            return 0
        def pref(s):
            return (bool(b[s]['kempeitai']), -gs(b[s]), -POP[s], ix(s))
        pool = [s for s in PROV if b[s]['force136'] and b[s]['camp'] and not b[s]['cache']]
        chosen = sorted(pool, key=pref)[:limit]
        if self.cap.get(8) == 'U' and len(chosen) < limit:     # British J8: one more, after all F136 Provinces
            remote = [s for s in PROV if not b[s]['force136'] and b[s]['camp'] and not b[s]['cache']]
            if remote:
                chosen.append(min(remote, key=pref))
        n = 0
        for s in chosen:
            if self.cap.get(8) == 'S' and self.die('Supply', s) <= 2:   # Japanese J8 roll (engine's 1-2 fails)
                continue
            b[s]['camp'] = False
            b[s]['cache'] = True
            n += 1
        if self.cap.get(27) == 'S':                             # Japanese J27
            opp = [s for s in chosen if b[s]['opposition']]
            if opp:
                b[min(opp, key=lambda s: (POP[s], ix(s)))]['opposition'] = False
        self.inc('caches_built', n)
        return n

    # ------------------------------------------------------------------ 6.7 Raid
    def raid(self):
        """6.7: up to 2 destinations (3 at Zipper 20), one at a time. Sabotage beats Ambush beats
        Majority; ties: destination map order, source with most guerrillas, source map order,
        red before blue."""
        b = self.board
        dests = []
        for _ in range(3 if self.zipper == 20 else 2):
            options = []
            for dst in ORDER:
                if dst in dests:
                    continue
                w = b[dst]
                for src in ORDER:
                    if src not in ADJ[dst] or not b[src]['cache']:
                        continue
                    v = b[src]
                    for colour in ('red', 'blue'):
                        if w[OTHER[colour] + '_u'] + w[OTHER[colour] + '_a']:
                            continue                            # never into a space with the other colour
                        tie = (ix(dst), -gs(v), ix(src), colour != 'red')
                        if v[colour + '_u'] and self._keeps(src, 1):
                            if self.rail_choice(dst):
                                options.append(((0,) + tie, src, dst, colour, 1, 'SABOTAGE'))
                            if self._ambush_target(dst):
                                options.append(((1,) + tie, src, dst, colour, 1, 'AMBUSH'))
                        need = cubes(w) - gs(w) + 1             # fewest that give a majority
                        if gs(w) <= cubes(w) and need <= 2 and v[colour + '_u'] + v[colour + '_a'] >= need \
                                and self._keeps(src, need):
                            options.append(((2,) + tie, src, dst, colour, need, 'MAJORITY'))
            if not options:
                break
            _, src, dst, colour, n, kind = min(options)
            for _ in range(n):                                  # Underground first
                field = colour + ('_u' if b[src][colour + '_u'] else '_a')
                b[src][field] -= 1
                b[dst][field] += 1
            dests.append(dst)
            if kind == 'SABOTAGE':
                self._sabotage_at(dst, colour)
            elif kind == 'AMBUSH':
                self.strike([dst], colour)
            self.cleanup()
        self.inc('raid_destinations', len(dests))
        return dests

    # ------------------------------------------------------------------ section 7 between turns
    def icon(self, j):
        """7 MPAJA icons: Mobilize Population and Kill Traitors are British choices; Japan resolves
        Seize Supplies and Food Shortage (engine)."""
        b = self.board
        if j in MOBILIZE:
            sites = [s for s in PROV if b[s]['camp'] and not b[s]['terror'] and not b[s]['opposition']]
            if sites:
                b[min(sites, key=lambda s: (-POP[s], ix(s)))]['opposition'] = True
            self.cleanup()
        elif j in KILL:
            sites = [s for s in ORDER if red(b[s]) and b[s]['police']]
            if sites:
                s = min(sites, key=lambda s: (b[s]['police'] != 1, not b[s]['force136'], ix(s)))
                b[s]['police'] -= 1
            self.cleanup()
        else:
            FastGame.icon(self, j)

    def placement_rank(self, s):
        """7 Every Propaganda: at Mobilize, if red runs short, place it in map order."""
        return (ix(s),)

    def british_resources_phase(self):
        """7 Nonfinal Propaganda, Resources: for each sabotaged railway in Railway-list order, set one
        adjacent space without Terror or Opposition to Opposition: highest Population, map order.
        READING: only spaces with Population can hold Opposition (Economic Centers excluded)."""
        b = self.board
        for r in RAILWAY_LIST:
            if not self.sabotage[r]:
                continue
            sites = [s for s in self.rail_adj(r) if POP[s] and not b[s]['terror'] and not b[s]['opposition']]
            if sites:
                b[min(sites, key=lambda s: (-POP[s], ix(s)))]['opposition'] = True

    def british_redeploy(self):
        """7 Nonfinal Propaganda, Redeploy: each exposed marker, map order, to a Camp Province without
        F136 or Kempeitai: most guerrillas, then map order. A marker moves at most once."""
        b = self.board
        movers = [(s, b[s]['force136']) for s in ORDER if self._exposed(s)]   # fixed before any move
        for src, n in movers:
            for _ in range(n):
                dests = [s for s in PROV if b[s]['camp'] and not b[s]['force136'] and not b[s]['kempeitai']]
                if not dests:
                    return
                dst = min(dests, key=lambda s: (-gs(b[s]), ix(s)))
                b[src]['force136'] -= 1
                b[dst]['force136'] += 1

    # ------------------------------------------------------------------ 7 British capability sides
    # Added by the primary author for v1.0.3 from the new lines in rules section 7 (not clean-room work).
    def british_j12(self, r):
        """J12 (British side): when Construct removes Sabotage from railway r, set one adjacent Province
        or Kuala Lumpur without Opposition to Opposition: highest Population; no Terror; map order."""
        b = self.board
        best = None
        for s in ORDER:
            if s not in self.rail_adj(r) or not POP[s] or b[s]['opposition']:
                continue
            key = (-POP[s], 1 if b[s]['terror'] else 0, ix(s))
            if best is None or key < best[0]:
                best = (key, s)
        if best:
            b[best[1]]['opposition'] = True

    def british_j15(self):
        """J15 (British side): when Japan Extracts, each New Village Province in map order gets one
        guerrilla of the colour it has more of (red on a tie or if empty), if one is Available."""
        b = self.board
        for s in ORDER:
            if not b[s]['new_village']:
                continue
            colour = 'red' if red(b[s]) >= blue(b[s]) else 'blue'
            if self.available(colour) > 0:
                b[s][colour + '_u'] += 1

    def j25_return_space(self, camp_provinces):
        """v1.0 to v1.0.2 rules section 7: a marker returning from J25 goes to a Camp Province: no Kempeitai;
        no F136; most guerrillas; map order. No longer called: under rule 5.1 the choice is Japan's (v1.0.3)."""
        b = self.board
        return min(camp_provinces, key=lambda s: (bool(b[s]['kempeitai']), bool(b[s]['force136']), -gs(b[s]), ix(s)))
