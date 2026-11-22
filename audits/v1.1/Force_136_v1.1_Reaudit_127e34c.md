# Force 136 v1.1: independent re-audit

**21 November 2026. Release verdict: pass as a simulation-tested paper fan bot.** No confirmed gameplay, scoring, Event-step, or new printed-rules defect was found. No required fix follows from this review. The fresh experiments support keeping J4 and J25. Two optional printing/test refinements are listed below.

Reviewed repository: `ramyahoo88/the_british_way_solo`, branch `claude-force136`, merge **127e34cdabae591901124c66fdbeba2e80ee2102**, containing v1.1 commit **47e5a2d5d46905ad674de9e70e72d761ca4d2e0f**. Compared with the reviewed v1.0.4 at `5efd44f`.

## Basis and scope

The player plays Japan; Force 136 runs Britain in the standard standalone Japanese Occupation scenario. The MPAJA remains independent. The bot uses the nine Directive cards, five stated levels and its printed priorities. This review does not introduce Personas, pre-war options or campaign links.

The official reference is GMT's current online **Japanese Occupation Rules of Play**, `EomE_JapOcc_Rules.pdf` (28 pages, ©2026), opened on 21 November, plus the original J4 and J25 faces from the supplied Vassal module **3.1.1**. GMT's product/Living Rules index was checked for the current reference; no separate errata entry was listed there. The original card layouts were inspected directly. J4 awards Resistance by qualifying **space**, rather than by marker. J25 permits British Contact followed by one Special Activity. The rules' Event framework, Resistance cap and free-box requirement remain binding; an Event does not create another ordinary Operation.

Bot authority is **Force_136_v1_Rules.md**, v1.1, especially section 4 step 2 and the Contact/Special Activity procedures. That step requires Japan to have acted, the Event box to remain free, the card to be J4 or J25, and the British side to have an effect. It is evaluated after drawing the Directive. The Directive is consumed on Event turns too. Recruit continues to skip Raid.

All **222** current release/source files in the checked scope matched the pinned Git blob identities. `engine.py`, `expert.py` and `lookahead.py` are unchanged from v1.0.4. This review concentrates on the new Event policy and its evidence, with regression, legality, scoring and printed-material checks. It is not a claim of exhaustive independent certification of every base-game action.

Official sources: [GMT product and Living Rules index](https://www.gmtgames.com/p-1107-the-british-way-enemy-of-my-enemy.aspx); [Japanese Occupation Rules of Play](https://gmtwebsiteassets.s3.us-west-2.amazonaws.com/TheBritishWay_EnemyofMyEnemy/EomE_JapOcc_Rules.pdf). Source versions, paths and exact Git identities are retained in the evidence.

## Fresh evidence: the change helps

The review used an additional **1,000 seeds, 900000-900999**, crossed with the same six purposeful Japan policies: **6,000 matched games per complete variant**. Baseline disables only the new Event step (`V104`); the corrected Japan, Train refresh, difficulty and other bot choices stay the same. The supplied actual engine ran the games. The independent analysis checks unique identities, complete matching and whole-seed clustering.

| Fresh Agent comparison | Force 136 wins | Win rate |
|---|---:|---:|
| v1.0.4, no Event step | 3,679 / 6,000 | 61.3% |
| v1.1, J4 and J25 together | 3,811 / 6,000 | 63.5% |
| Paired change | +132 wins | **+2.2 points; 95% +1.4 to +3.0** |

The interval uses 10,000 whole-seed resamples, retaining all six policy games together. The new code executed 2,554 Event turns in these 6,000 games, about 0.43 per game. The change keeps the existing Directive cycle and uses existing Contact/Special Activity procedures.

| Japan policy, 1,000 fresh games each | v1.0.4 wins | v1.1 wins | Change in percentage points |
|---|---:|---:|---:|
| extraction | 681 | 705 | +2.4 |
| hunting | 721 | 726 | +0.5 |
| repair | 739 | 749 | +1.0 |
| adaptive | 659 | 673 | +1.4 |
| counter | 364 | 408 | +4.4 |
| mixed | 515 | 550 | +3.5 |

Every policy's aggregate point estimate improved. This does not establish a statistically certain gain within every policy, nor that either individual Event helps against every policy.

The individual-card experiment also repeated on the same fresh cohort, before evaluating the combined package. Cards absent from a game's deck cannot affect it. The following gains are **conditional on actually taking the Event**, not whole-campaign percentage gains:

| Event as second player | Fresh games where taken | Conditional paired gain, 95% interval |
|---|---:|---:|
| J4 Chin Peng | 1,196 | **+6.4 points, +3.4 to +9.2** |
| J25 John Davis | 1,368 | **+3.4 points, +0.7 to +6.2** |

These support the two additions without changing the printed rule. Only six J4 cases and one J25 case in this fresh experiment replaced an Op & Special Activity rather than a Limited Operation; those tiny subsets had zero net winner change. They do not establish the quality of that rarer branch.

## Published numbers and study interpretation

The two stored 30,000-row level datasets have complete, unique matched seed-policy-level grids. Recomputed wins and paired differences agree with the published values:

| Level | v1.0.4 wins / 6,000 | v1.1 wins / 6,000 | Paired change |
|---|---:|---:|---:|
| Recruit | 2,325 | 2,374 | +0.82 points |
| Agent | 3,676 | 3,777 | +1.68 points |
| Veteran | 4,251 | 4,349 | +1.63 points |
| Legend | 4,728 | 4,811 | +1.38 points |
| Mastermind | 5,351 | 5,401 | +0.83 points |

The printed **40 / 63 / 72 / 80 / 90%** is consistent with the unrounded totals. Veteran is 72.483%, so its whole-percent label is 72 even though a one-decimal presentation gives 72.5. Independent seed-block intervals give the same conclusions, including Recruit's interval crossing zero. Small differences in bootstrap percentiles reflect numeric versus textual seed ordering, not different games.

Both stored Event-confirmation blocks were checked from their paired records. J4's positive interval repeats in both. J25 has positive point estimates in both, but its second interval crosses zero, as the report discloses. The additional fresh block above strengthens that evidence.

The screen covers the **British sides** of all 30 nonmandatory Event cards. Its first-player point estimates are all negative; this supports the tested policy of declining them. It is not proof that every possible contextual first-player Event choice, or a Japanese-side Event used by Britain, is inferior. The report's method identifies this scope.

The quoted **+0.9 points over 1,920 lookahead games** pools 15 cells: three lookahead configurations across five levels, with 128 games each. It is not 1,920 Agent games against the single strongest configuration. I checked the published results through the report checker, but did not rerun those expensive lookahead cells here. Their fixed candidate menus and sampled Directive replies remain model limitations.

## Rules, boundaries and regressions tested directly

The Event paths are in `force136_v1/code/force136_v1.py:284` through the Event execution/turn code; the separate implementation is in `code/cleanroom/cleanroom.py:108`. The printed instruction is `print/Force_136_v1_Rules.md:42`.

- **18 focused Event positions, both implementations: 36 executions.** J4 counts two qualifying spaces even with three markers; caps at 20; declines at 20, when first, with no matching Camp, or with Event occupied. J25 qualifies through Contact alone, Supply alone, Gather alone or Raid alone; declines when all are ineffective; and declines when first or when Event is occupied. Recruit rejects the Raid-only case. The rarer case after Japan chooses Limited is also checked.
- **J25 sequencing and interrupted results.** Supply is chosen from the post-Contact board. With Japanese J8/J27 in play, a fixed real roll of 1 keeps the Camp, makes no Cache and still removes Opposition; roll 3 converts. The same intended Event/Special Activity is selected in both cases. These are isolated fixtures, not counted campaign games.
- **Five preview/hidden-information checks.** Event qualification leaves the live state unchanged. Swapping concealed Intel values, future Event order and the queued Directive does not change whether the Event qualifies. Real Gather reveals may legitimately differ afterward.
- **624 complete comparison games** across levels and forced capability sides: zero state/result disagreement and zero independent Propaganda-oracle failures.
- **12,000 additional random positions**, starting at differential-fuzzer seed **1060000**: 132,000 compared actions, zero differences. These contain 721 J4 and 1,963 J25 Event turns. Random constructed positions are not certified reachable campaigns.
- **Legality checks:** 960 games and 12,000 constructed positions, zero reported violations. The checker observed **3,175 Event turns** in total (910 J4 and 2,265 J25) and no unresolved Raid category.
- **19 fixed regression fixtures** pass; **17 comparison/scoring mutations** are caught at the published 16-seed setting; **10 legality negative controls** are caught. Exit-status checks correctly fail on deliberately broken scoring or an uncaught mutant.
- **Deterministic victory boundary.** A new focused review fixture retains Resistance at 18 or 19 with two Camps and two markers: MPAJA wins. With one Camp and two markers, Force 136 wins. It distinguishes the planted equal-Camp error without depending on random campaign exposure.

The reduced eight-seed mutation probe initially missed the equal-Camp victory error. The full 16-seed run catches all 17, including that one; the new explicit boundary fixture catches it directly. That reduced-coverage observation is not an illegal action or a failure of the published full check. Both raw runs are retained rather than hiding the exploratory failure.

## Delivered materials and representative play

I inspected the actual delivered PDFs, the flowchart, all nine Directive faces and the reference tables. The rules, reference and flowchart contain the Event-box-free condition and current J4/J25 procedures. Card goal orders and Limited choices match the source data; the new Event reminder appears on every Directive. No clipping or text beyond page bounds was found. The 11-page combined packet matches its component pages.

Delivered lengths: six rules pages, two reference pages, two card pages including backs, one record sheet, three sample-game pages, and ten simulation-report pages. Every rules page is numbered. These were inspected as shipped, not reprinted through Chrome here; Chrome was unavailable in the execution environment, so no byte-identical PDF rebuild is claimed.

The sample **seed 20005 / adaptive / Agent** was rerun. Its full trace and regenerated Markdown match the submitted sample byte for byte. At draw 11, J25 follows Japan's Op & SA: the British Contact places a marker in Selangor, then Supply converts Camps into Caches. The Directive is still drawn and consumed. Propaganda score changes are +8 at draw 6, +8 at draw 13, and +5 capped at 20 after the draw-16 J9 early ending. Force 136 wins at 20. Independent scoring is also checked throughout the 624 comparison games.

## Optional refinements, not release blockers

### U1 — Put the free-box guard on the Directive reminder

**Player impact:** when Japan uses J25's Event box, a player reading the card footer alone must consult the referenced rule to see that Britain cannot take the same box. The complete rules, reference, flowchart and code already handle this correctly.

**Reproduction:** use `event_boundaries.py`, case “J25 after Japan took Event is declined.” With Japan in Event, the British side could still have an effect, but Event is not free and the actual bot takes a legal remaining box. Compare that with any of the nine printed footer reminders: they start “Japan acted first on J4 or J25” and do not repeat the free-box guard.

**Source:** `force136_v1/print/build.py:174`, all nine faces on page 1 of `Force_136_v1_Cards.pdf`; expected instruction at `print/Force_136_v1_Rules.md:42` and `code/force136_v1.py:296`.

**Smallest proposed improvement:** add “and the Event box is free” to that shared footer sentence, then regenerate the Cards and Print-and-Play PDFs and manifest. This is reminder completeness, not a demonstrated rules conflict or bot bug.

### U2 — Retain a fixed equal-Camp mutation witness

**Player impact:** none in the tested release; this protects future verification work. A short random campaign window need not reach the exact victory boundary it is intended to test.

**Exact reproduction:** `python verify_v1.py --mutants 8` misses “18-19 tie counted for Britain” on seeds 23000-23007, both specified levels and all six policies. The full `--mutants 16` setting catches it. `victory_tie_fixture.py` in this evidence isolates the tie and the nearby unequal-Camp control at both Resistance 18 and 19.

**Source:** `force136_v1/code/verify_v1.py:194` (mutant) and `:276` (sampled jobs); official victory boundary and the existing independent scoring oracle.

**Smallest proposed improvement:** include the deterministic fixture as a checker self-test or fixed regression. Keep the broad full-game mutation run as well. No game-rule change is suggested.

## Reproduction, limits and release decision

The evidence ZIP contains runnable review scripts, exact runtime/card inputs, recorded checks, paired raw results and the independent analysis. `README.md` gives paths and commands; `source_verification.json` identifies the 222 checked Git blobs. Fresh game records include seed, Japan policy, variant, winners and final Resistance. Publisher artwork and the publisher's rulebook are not redistributed in the bundle.

Important limits remain: both bot implementations share the engine and some data. Their agreement does not independently certify all Japanese Operations or every Event. Only Propaganda scoring has the separate full oracle. Random positions and legality searches are finite tests. Six fixed Japan policies are not optimal human play; the lookahead cells are bounded searches, and were not rerun in this review. No physical tabletop handling, fun or turn-time test was conducted. The prior railway-corner and other recorded ruling questions remain assumptions; this update introduces no new ruling.

**Fix priority: no mandatory correction.** U1 is a small improvement for the next print refresh; U2 strengthens the verification suite. The original and additional confirmation blocks, fresh +2.2-point combined gain, complete matched datasets, legal Event boundaries, consistent implementations and matching delivered materials support **releasing v1.1**. Keep its current description as a simulation-tested paper fan bot with human playtesting still to come.
