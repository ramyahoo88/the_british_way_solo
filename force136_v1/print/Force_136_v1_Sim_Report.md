# Force 136 v1.0.1 — simulation report

21 November 2026, revised the same day after GPT's review (v1.0.1) · Human Japan vs the Force 136 bot · standard standalone Japanese Occupation

## Summary

Force 136 is a new card-driven British bot. It replaces the v0.2 draft rather than revising it. On 6,000 simulated games per level on fresh seeds (0–999, never used for tuning or for any earlier check), against six computer Japan policies, v1.0.1 wins:

| Level | Change | Force 136 wins | 95% interval | Mean final Resistance | MPAJA wins |
|---|---|---:|---:|---:|---:|
| Recruit | never Raids | 41.3% | 40–43% | 15.5 | 5.5% |
| **Agent** | standard | **64.4%** | 63–66% | 17.6 | 4.1% |
| Veteran | Resistance starts at 4 | 74.0% | 72–76% | 18.4 | 3.8% |
| Legend | starts at 4; +1 Resistance after each nonfinal Propaganda | 81.6% | 80–83% | 18.9 | 3.2% |
| Mastermind | starts at 6; +2 Resistance after each nonfinal Propaganda | 91.3% | 90–92% | 19.6 | 2.3% |

The rules print the rounded figures 41%, 64%, 74%, 82% and 91%.

**What changed in v1.0.1.** GPT reviewed v1.0 (see `REVIEW_RESPONSE.md`). Two things moved the numbers:

- *A better Train.* When no guerrilla of the colour is Available and no other space can give one, Train now re-places an Active guerrilla in the Train space itself, back Underground. Rule 1.4.1 allows it; v1.0 had wrongly treated it as unclear. In paired games on the same seeds it adds 4.8 points at Agent (95% interval +3.8 to +5.8), against every Japan policy. GPT's re-audit confirmed it independently on untouched seeds 120000–120255: +4.2 points (+2.3 to +6.3) in 1,536 paired games.
- *A larger fresh sample.* v1.0 printed 36%, 61%, 71%, 79% and 89%, pooled from 2,304 games per level on the holdout seeds 20000–20383. GPT ran v1.0's Agent on 192 other seeds (50000–50063 and 60000–60127) and got 53.6%. I reproduced those 1,152 games exactly, so the code is not the cause. I then ran v1.0's Agent on five blocks of 1,000 fresh seeds: 58.2–60.5% per block, 59.5% (58.7–60.2%) over all 30,000 games. GPT's windows were unusually low: only about 3 in 1,000 random sets of 192 seeds do that badly. The holdout's 61% was about 1.5 points high, which happens about one time in eight. On seeds 0–999, v1.0 won 34.7%, 59.7%, 70.1%, 78.1% and 89.0%.

On the first holdout (seeds 20000–20127, 768 games), where v1.0's Agent won 59.9% and v1.0.1's wins 64.7%:

- GPT's v0.2 paper bot, run in the same executor, won 0.0% (mean Resistance 1.3).
- v0.2's best experimental variant ("primary + recovery/guard") won 2.0% (mean Resistance 5.4).
- A one-step search player won 56.9% (mean Resistance 16.8). It compares a fixed menu of plans (each free box with each Operation and Special Activity, the engine's targeting procedures choosing the spaces) and scores each with a hand-written evaluation. It does not search every legal action or every choice of spaces.

The printed Agent bot plays better than that search player against these opponents.

These are computer-model results, not tabletop win rates. A strong human Japan player is expected to beat the computer policies more often. Japan policies that preview the bot's reply (its real procedures, with randomly sampled Directive cards) before moving do much better (below): the widest search holds v1.0.1's Agent to about 15%, Legend to 26% and Mastermind to 51% (128 holdout seeds each). GPT's re-audit replayed the Agent and Mastermind runs and got the same results. The Mastermind level exists for players who learn to exploit the bot that way.

## The model

- **Engine.** GPT's research executor (research-0.2, from the v0.2 simulation evidence), adopted with its paper-bot code removed from the British side. It covers the full scenario and was audited for this study:

    - Turns and setup: setup, the 21-card deck with Propaganda in each pile's bottom three, both factions' Operations and Special Activities, eligibility.
    - Cards and markers: all 32 Events, the six capabilities, MPAJA icons, the Zipper track with its cache releases.
    - Propaganda and pools: full Propaganda, victory, piece pools.

    I checked the setup, icon sets, Event effects, Operations and Propaganda against the card faces and player aids in the Vassal module (3.1.1) and against the GMT rulebook. I found no discrepancy that changes play.

- **Japan.** Six one-step policies. Four are GPT's: extraction, hunting, repair and adaptive. Two are new:

    - *counter* minimizes the British evaluation used by the search player, so it attacks what that evaluation values.
    - *mixed* averages counter and adaptive.

    Two lookahead variants (look, lookc) act only when Japan moves first on a card. They rate a fixed menu of Japanese moves, take the best 8 (or 16), run the real bot procedures as Force 136's reply to each with 3 (or 4) Directive cards drawn at random from all nine, and choose the best average. They know the bot's rules but not its next card, and they do not narrow the draw to the cards still in the Directive pile. Four scripted exploit policies try to abuse a predictable bot.

- **Information.** Policies see only public information. Concealed Intel values stay hidden from both sides' decisions. Dice and Intel draws are keyed to the seed, so matched games share Event deals.
- **Protocol.** Rules were tuned only on development seeds (6000–7300 and 10000–10327). The first results used the untouched holdout seeds 20000–20383. After GPT's review, every level was rerun on fresh seeds 0–999 (6,000 games per level), and Agent on four more 1,000-seed blocks. Games on the same seed share Event deals across policies and levels. The intervals resample whole seeds.

## Results by Japan policy (v1.0.1, fresh seeds 0–999)

| Japan policy | Recruit | Agent | Veteran | Legend | Mastermind | Search player (v1.0 holdout 1) |
|---|---:|---:|---:|---:|---:|---:|
| extraction | 33% | 71% | 80% | 88% | 95% | 66% |
| hunting | 63% | 77% | 85% | 90% | 96% | 63% |
| repair | 49% | 77% | 83% | 88% | 95% | 67% |
| adaptive | 44% | 69% | 79% | 87% | 94% | 64% |
| counter | 23% | 40% | 50% | 62% | 80% | 36% |
| mixed | 35% | 53% | 66% | 75% | 87% | 46% |

**Lookahead Japan** (v1.0.1; 128 holdout seeds per cell, v1.0 in brackets):

| Opponent | Recruit | Agent | Veteran | Legend | Mastermind |
|---|---:|---:|---:|---:|---:|
| look: adaptive values; bot reply previewed for its 8 best moves × 3 sampled cards | 45% (38) | 57% (52) | 65% (61) | 72% (71) | 93% (89) |
| lookc: counter values, 8 moves × 3 sampled cards | 22% (16) | 36% (34) | 43% (45) | 55% (54) | 70% (77) |
| lookc, wide: counter values, 16 moves × 4 sampled cards | 9% (7) | 15% (13) | 22% (19) | 26% (31) | 51% (48) |

With 128 seeds per cell, differences under about 10 points are within noise. GPT reran the wide search against v1.0 on 32 other seeds: Agent won 1 game and Mastermind 16.

The wide search exploits the bot's predictability. It removes the early Caches (0.7 on the map at the first Propaganda instead of 1.6, measured on v1.0) with Assault + Reprisal right after the bot's Gathers and Ambushes have activated the guards, and it eliminates more Force 136 markers. Rules meant to protect thin Caches were tested against it on v1.0 and made the bot weaker against every opponent:

- Train first at a thin Cache: 14% (no change);
- never activating a Cache's last Underground guerrilla: 6%;
- the same rule for Gather only: 8%.

The levels carry the difference instead: Mastermind (Resistance 6, +2 per nonfinal Propaganda) wins about half the time against it.

How much of this is exploiting the bot? The same lookahead was run against the one-step search player, which has no fixed priorities, again previewing its reply:

| Opponent | Search player | Agent v1.0 | Agent v1.0.1 |
|---|---:|---:|---:|
| 8 moves | 29% | 34% | 36% |
| 16 moves | 21% | 13% | 15% |

The search player loses almost as badly, so most of the wide search's edge looks like strong Japanese play. The remaining 6–8-point gap is an observed difference between two different British players, not a measured cost of predictability. A deck with TRAIN first on every Limited turn, or AMBUSH first on every card, stayed within noise of the printed mix against both this opponent and the regular policies (v1.0).

**Exploit attempts** (Agent v1.0.1, 256 games each; v1.0 in brackets):

| Japan always… | Force 136 wins |
|---|---:|
| Eliminates, or makes Limited Assaults and Sweeps | 94% (94) |
| takes the Limited box to keep the initiative | 98% (98) |
| plays economically (Deploy, Extract, Construct) | 70% (69) |
| grabs the Event whenever possible | 70% (72) |

None of these beats the regular policies.

**Map reading.** With GPT's alternative northern railway-corner adjacency, v1.0.1's Agent wins 64.1% instead of 64.7% (holdout 1).

## How the design was found

Each step was measured on development seeds with matched games (all six policies unless noted). Figures in this section are from v1.0 development, except where v1.0.1 is named.

1. **Start from GPT's procedures.** A plain priority bot built on v0.2's targeting rules won 8% against GPT's four policies.
2. **Place Force 136 first.** Contacting to place an Available marker before anything else on Limited turns: 34%. Ambush before Train on Limited turns: 42%.
3. **Find where the gap was.** Handing only the full-turn (Op & SA) choices to the search player closed most of the gap to it (44.8% vs 36.5%). So the full-turn order mattered most.
4. **Sweep the full-turn order.** All 120 orders were tested. PLACE first dominates. After it, decks led by AMBUSH, or by INTEL then AMBUSH, win 54–56%. Decks led by INTEL without AMBUSH next win 30–39%, and decks led by SUPPLY or TRAIN win 8–28%.
5. **Fix the procedures that mattered.**

    - Taking a guerrilla from elsewhere on the map when none is Available (rule 1.4.1) was worth +7 points.
    - Rule 1.4.1's example also lets Train take an Active guerrilla from the Train space itself and place it back Underground (a "refresh"). v1.0 wrongly called that unclear and left it out. After GPT's review it was tested again on the final bot. Refreshing before other sources: −0.9 (GPT's own matched test: −6). Refreshing only when no other source exists: +6.5 and +7.1 on two development seed sets, then +4.8 (95% interval +3.8 to +5.8) in 6,000 paired games on fresh seeds 0–999, better against every policy. GPT's independent check on seeds 120000–120255 gave +4.2 (+2.3 to +6.3). v1.0.1 adopts it as Train's last source.
    - A fuller Raid procedure (Sabotage › Ambush › Majority, 1–2 pieces) was worth about 11 points over the first simple version.
    - Placing Force 136 away from cubes: +3 to +4 on two seed sets.
    - "Gather if it would reveal 2 or more" as the first Special Activity: +1–2.
    - Ambush rolling at a good shot (Kempeitai, else a Troop) before removing Police: +4.6 and +4.8 on two seed sets.
    - Raid ahead of Gather after an Ambush halves the win rate (27% vs 52%).

6. **Simplify for the table.** Each simplification was costed:

    - a fixed railway list instead of a "live route" test: −0.8;
    - one-sentence Train colours: −0.8;
    - Supply only after a Train that places something, so no Operation does nothing: −1.7.

    The bot never uses a Contact that neither places nor moves a marker.

7. **Make it card-driven.** Each Directive card carries one of the strongest goal orders and a Limited preference. The nine-card mix scored 55.9% against 56.9% for the single best order (development). South-first tie-breaks would have cost 4.7 points, so every card uses map order.

**No gain, so not adopted:**

- Sabotage aimed at cutting Extract income: −1 to −26, depending on where it sat in the order.
- A late-campaign Intel priority: +0.6, within noise.
- Forcing Supply in the last campaign: −1 to +0.6.
- Guarding thin Caches first: +0.9 on Limited turns, −8 or worse on full turns.
- Requiring Police or two targets for Ambush: −7.
- Gathering only where no Troops are: −29. Keeping the last Underground guerrilla next to Troops: −9.
- Intel-reach Contact placement: −11.
- Mountain-first placement: −8. Jungle-first: +0.8.
- Moving idle markers at Redeploy: 0.
- Avoiding blue spaces at Mobilize: −1.5.
- Taking Limited when Japan took the Event: about 0 (+1.1 and −0.8 on two seed sets).
- Supply only in Provinces with 1+ (or 2+) Underground guerrillas: −5 (−26), and also worse against the wide-search Japan.
- INTEL without its Sabotage option, to shorten the lookup: −2 to −3 on two seed sets.
- Limited Ambush only at good shots: +1.3, within noise.

### Events

Each Event was tested on the final bot with paired games (48 seeds × 6 policies = 288 games per Event and mode), taking the British side whenever a sensible condition held:

- **Taken as first player,** replacing an Operation with a Special Activity: 24 of 28 Events lowered final Resistance, by up to 0.9. The other four gained at most 0.2: J24 +0.19, J10 +0.08, J31 +0.07, J21 +0.02.
- **Taken as second player,** replacing a Limited Operation: the best gains were J23 (+0.24 Resistance), J24 (+0.13) and J10 (+0.07).

A follow-up on 1,152 fresh games per case (seeds 32000–32191) tested the most promising of these:

| Case | Change in wins | Change in final Resistance |
|---|---:|---:|
| J23 as second player | +0.6 points (±0.7) | +0.11 (±0.05) |
| J10 as second player | +0.8 points (±0.4) | +0.07 (±0.03) |
| J24 as second player | −0.8 points | −0.09 |
| J24 as first player | −2.6 points | −0.26 |

None is worth a printed exception and an extra lookup.

So Force 136 never takes Events. That also removes the bot's longest lookup. (These Event tests ran on v1.0, before the Train refresh, and were not rerun.)

## Verification

- **Rules as code.** `force136_v1.py` follows the printed rules section by section. The tuning lab (`force136.py`) and the printed-rules module play move for move the same in 960 games across all five levels (`equiv.py`: 0 mismatches, rerun for v1.0.1). This includes the nine cards as printed, where cards 1–8 omit a SUPPLY goal that would only repeat TRAIN.
- **Independent rules review.** A reviewer who saw only the printed rules, reference sheet and cards reported 21 findings. Twenty were text problems: ambiguities, omissions and reference-sheet gaps. They were fixed by making the text say what the simulation does. One was a real code error: the British choice under the Japanese side of J27 removed Opposition from the highest-Population space instead of the lowest. It was fixed and all results rerun. See `REVIEW_RESPONSE.md`.
- **Clean-room implementation.** A second agent implemented the bot from the printed rules alone, without seeing any bot code. It reproduced the worked example exactly. Comparing the two found three places where my code did not do what the text says, all fixed: New Village removal was delayed; J8 Supply re-chose a Province after a failed roll; and the Special Activity was chosen before the Ambush roll instead of after it. It also found an engine choice made in Britain's favour (Japanese side of J20), now Japan's.
- **GPT's review of v1.0.** The v1.0 comparison (`cleancmp.py`) checked decisions, boards and Sabotage after each Force 136 turn. GPT showed that it ignored Resistance, the other tracks, trace length and the final result, so a deliberate scoring error that changed the winner passed. GPT also showed that normal games never put a British capability side in play, so the clean-room bot's missing British J22 and J27 effects went unseen. Both are fixed.
- **The checker now** (`verify_v1.py`) has three parts:

    1. *Cross-check.* Both bots play the same seed. After every Force 136 turn the Directive card, goal, box, Operation, Special Activity and board must match, along with every track and the pieces off the map and in pools. The same holds after every Propaganda reset and for the final result. Unequal trace lengths fail.
    2. *Scoring oracle.* Every Propaganda score in both bots is recomputed from the rulebook alone (6.1–6.2.5, 6.7.2, 7.0.1, 1.13) plus the level bonus. That covers Resistance, the winner, the Zipper box, the Cache track and which Caches stay on the map. This catches errors in the engine code both bots share, which a cross-check cannot see. (The Zipper part was added after GPT's re-audit of v1.0.1.)
    3. *Forced capabilities.* 96 games with each side of each capability (J8, J12, J15, J19, J22, J27) in play from the start, and 192 each with all six British sides or all six Japanese sides. Counters show the British effects fired: for example, 333 Gathers under British J22 and 246 extra Ambush spaces under British J27.

    For v1.0.1, 2,496 games (960 normal ones across the five levels, plus 1,536 forced-capability games) gave 0 cross-check failures and 0 oracle failures.
- **Mutation tests.** `verify_v1.py --mutants` plants 15 deliberate errors, and the checker must flag each one. They are: the level bonus at final scoring; an Agent bonus; 18–19 ties given to Britain; the Train refresh left out; British J22 ignored; British J27 ignored for Ambush or for Sabotage, or ranked by railway order; GPT's +1 Resistance before final scoring in the clean-room bot; a skipped clean-room turn; three engine scoring errors (Neutral Population counted per 4, no Police penalty, Caches counted double); and two engine Zipper errors (frozen at Propaganda, one box low). All 15 are caught. Only the oracle sees the five engine errors.
- **Exit status.** `verify_v1.py` exits with status 1 if any game fails, and `--mutants` exits with status 1 if any mutant is missed, so an automated check cannot pass on a failure. `check_exit_status.py` tests this with an injected engine error and an uncatchable mutant (GPT's re-audit found the earlier version always exited 0).
- **Printed numbers.** `report_check.py` recomputes every win-rate cell in this report's summary and per-policy tables, the rules' level table and the README from the stored results, and fails on any mismatch. (GPT's re-audit found the per-policy table still showing v1.0 values.)
- **Review fixtures.** `review_fixtures.py` turns GPT's reproductions into tests: British J22 and J27 in both bots, the J27 extra space never qualifying a goal, the J8 limit, the exhausted-pool position (all nine Directives now Train), and the comparator rejecting score and length differences.
- **Limits.** The engine is GPT's research executor. Only its Propaganda scoring and Zipper placement are checked independently. Its Operations, Events and Japan policies are not reimplemented. The British capability coverage comes from forced setups; combinations of capabilities with particular Events are not exhaustively covered.

## Bot behaviour (Agent, fresh seeds 0–999)

A game gives Force 136 about 16 turns. Most turns need one to three goal checks (2.3 on average, measured on v1.0).

| Goal used | Share of turns |
|---|---:|
| TRAIN | 36% |
| AMBUSH | 34% |
| PLACE | 23% |
| INTEL | 6% |
| SUPPLY (Directive 9) | 1.1% |
| Pass | 0.1% (v1.0: 1.7%) |
| CONTACT | under 0.1% (v1.0: 1.1%) |

| Most common actions | Share of turns |
|---|---:|
| Limited Train | 26% |
| Ambush + Raid | 16% |
| Ambush + Gather | 14% |
| Limited Contact (placing a marker) | 14% |
| Train + Supply | 9% |
| Contact + Gather | 8% |

The Train refresh replaced most Passes and fallback Contacts: once the pools run dry, Train can still turn guerrillas Underground.

## Interpretations and limits

- **Rules readings used by the bot:**

    - When none of the colour is Available, Train takes a guerrilla from another space, and as a last resort re-places an Active one in the Train space itself (1.4.1; its example names both).
    - Gather reveals the chit in the activated guerrilla's own space.
    - A Contact must place or move a marker.
    - Ambush in Kuala Lumpur can only remove Police.
    - Under the Japanese side of J19, only the first Gather space may use adjacent spaces.
    - The Special Activity is chosen after the Operation, and its rolls, are resolved.

- **Engine readings that remain uncertain:**

    - J10's rounding.
    - Japanese choices inside Events are made by engine heuristics. One (J20) favoured Britain and was corrected.
    - Sabotage placed on an already sabotaged railway by J2 or J23.
    - The Japanese Redeploy policy.
    - Japan never Passes.

    None involves a bot decision.

- **Untested:** no physical playtest has been run, and turn time has not been measured. The Japan policies are heuristics, not people. The win rates are conditional on this executor and these opponents.

## Reproduce

From the `code/` folder, with Python 3.11+ and only the standard library:

```text
python3 equiv.py 32 recruit,agent,veteran,legend,mastermind   # printed rules == tuning lab (960 games, 0 mismatches)
python3 fresh_v101.py 0 1000 fresh_v101                # v1.0.1 level results, fresh seeds 0-999 (6,000 games per level)
python3 verify_v1.py 32                                # checker: cross-check, scoring oracle, forced capabilities
python3 verify_v1.py --mutants 16                      # the checker must catch 15 planted errors
python3 review_fixtures.py                             # GPT's reproductions as tests
python3 check_exit_status.py                           # the checker fails loudly
python3 report_check.py                                # printed tables == stored results
python3 holdout_v1.py 20000 128 holdout1_v101 agent    # first holdout
python3 look_run.py 20000 128 recruit,agent,veteran,legend,mastermind look
python3 look_run.py 20000 128 recruit,agent,veteran,legend,mastermind lookc
python3 look_deep.py 20000 128 recruit,agent,veteran,legend,mastermind lookc 16 4
python3 look_expert.py 20000 128 16 1                # the same search against the one-step search player
POLS=brute,tempo,econ,eventhog python3 holdout_v1.py 20000 64 exploits_v101 agent
python3 corner_run.py
python3 sample_game.py 20005 adaptive
```

v1.0-only runs (results kept in `results/`): `fresh_agent.py` and `fresh_levels.py` (v1.0 on fresh seeds, including GPT's windows), `holdout_v1.py 20128 256 confirm`, `ev_test_v1.py 48 31000`, `ev_confirm.py 32000 192 23:second,24:second,10:second,24:always`. To rerun them, restore v1.0's `force136_v1.py` from commit 615c870. The refresh comparison pairs `results/results_fresh_v101.csv.gz` with v1.0's rows for the same seeds in `results/results_fresh_v1.0.csv.gz`; the development-seed tests are `lab/variants.py` (`refresh_last`, `refresh_first`) on v1.0.

The printed rules are `force136_v1.py`. The engine is `engine.py` (GPT's executor) with `expert.py` (Japan policies and the search player). `force136.py` is the tuning lab.
