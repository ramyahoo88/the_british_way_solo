# Force 136 v1.0.3 — simulation report

21 November 2026 · Human Japan vs the Force 136 bot · standard standalone Japanese Occupation

## Summary

Force 136 is a card-driven British bot for the Japanese Occupation scenario. On 6,000 simulated games per level (seeds 0–999, never used for tuning), against six computer Japan policies, v1.0.3 wins:

| Level | Change | Force 136 wins | 95% interval | Mean final Resistance | MPAJA wins |
|---|---|---:|---:|---:|---:|
| Recruit | never Raids | 38.8% | 36.9–40.5% | 15.3 | 5.9% |
| **Agent** | standard | **61.3%** | 59.5–63.0% | 17.3 | 4.7% |
| Veteran | Resistance starts at 4 | 70.9% | 69.2–72.5% | 18.2 | 4.2% |
| Legend | starts at 4; +1 Resistance after each nonfinal Propaganda | 78.8% | 77.3–80.3% | 18.8 | 3.7% |
| Mastermind | starts at 6; +2 Resistance after each nonfinal Propaganda | 89.2% | 88.1–90.2% | 19.5 | 3.0% |

The rules print the rounded figures 39%, 61%, 71%, 79% and 89%. Intervals: whole-seed bootstrap, 10,000 resamples, `random.Random(33745)` for each level (`report_check.py` recomputes them).

These are computer-model results, not tabletop win rates. A strong human Japan player is expected to beat the computer policies more often. A computer Japan that previews the bot's reply before moving holds Agent to about 15% and Mastermind to 54% (below). No physical playtest has been run.

**What changed in v1.0.3.** A full audit of v1.0.2 (`audits/v1.0.2/` in the repository) found no illegal bot play and no difference between the two bot implementations on 12,000 random positions. Its main finding was in the model, not the bot: the computer Japan made two choices that a real Japan player would not, and both helped Britain.

- When Japan removed a guerrilla (Food Shortage icon, J11, J18), it took an Active one first. An Underground guerrilla is the better one to remove: only those can Ambush, Sabotage or Gather.
- At Japanese Redeploy it moved every Kempeitai to a space with more Troops than guerrillas, even one that was already sitting with a Force 136 marker. The move is optional (rule 6.5.2), and a Kempeitai next to a marker is where Japan wants it.

Japan now removes Underground guerrillas first and leaves one Kempeitai with each Force 136 marker it already shares a space with. A third fix follows rule 5.1: after the Japanese side of J25, Japan chooses the Province the marker returns to, not Britain. On the same 6,000 games per level, these lower the win rates by 2 to 3 points: Recruit −2.5, Agent −3.2 (95% interval −4.2 to −2.2), Veteran −3.2, Legend −2.8, Mastermind −2.1. v1.0.2 printed 41%, 64%, 74%, 82% and 91%. The bot's own procedures did not change, apart from that J25 choice and two new lines for British capability sides that never arise in these games.

On the first holdout (seeds 20000–20127, 768 games), where v1.0.3's Agent wins 61.3% (471 games):

- GPT's v0.2 paper bot, run in the same executor, won 0.0% (mean Resistance 1.2).
- v0.2's best experimental variant ("primary + recovery/guard") won 0.9% (mean Resistance 5.1).
- A one-step search player won 56.5% (mean Resistance 16.7). It compares a fixed menu of plans (each free box with each Operation and Special Activity, the engine's targeting procedures choosing the spaces) and scores each with a hand-written evaluation. It does not search every legal action or every choice of spaces.

## The model

- **Engine.** GPT's research executor (research-0.2, from the v0.2 simulation evidence), with its paper-bot code removed from the British side. It covers the full scenario: setup, the 21-card deck with Propaganda in each pile's bottom three, both factions' Operations and Special Activities, eligibility, all 32 Events, the six capabilities, MPAJA icons, the Zipper track, Propaganda and victory. For the v1.0.2 audit the British and Japanese player aids, the map and all 32 Event faces in the Vassal module (3.1.1) were read again and compared with the code, both sides of every card.
- **Japan.** Six one-step policies. Four are GPT's: extraction, hunting, repair and adaptive. Two are new:

    - *counter* minimizes the British evaluation used by the search player, so it attacks what that evaluation values.
    - *mixed* averages counter and adaptive.

    Each rates a fixed menu of moves one step ahead. They are heuristics, not strong players, and the v1.0.3 corrections show their choices can hide weaknesses. Two lookahead variants (look, lookc) act only when Japan moves first on a card. They rate the same menu, take the best 8 (or 16), run the real bot procedures as Force 136's reply to each with 3 (or 4) Directive cards drawn at random from all nine, and choose the best average. They know the bot's rules but not its next card. Four scripted stress policies commit to one kind of move.

- **Information.** Policies see only public information. Concealed Intel values stay hidden from both sides' decisions. Dice and Intel draws are keyed to the seed, so matched games share Event deals.
- **Protocol.** Rules were tuned only on development seeds (6000–7300 and 10000–10327). Level results use seeds 0–999 (first used for v1.0.1, after tuning ended); the lookahead and reference runs use the holdout seeds 20000–20127 (128 seeds, so differences under about 10 points are noise). Games on the same seed share Event deals across policies, levels and versions.

## Results by Japan policy (v1.0.3, seeds 0–999)

| Japan policy | Recruit | Agent | Veteran | Legend | Mastermind | Search player (holdout 1) |
|---|---:|---:|---:|---:|---:|---:|
| extraction | 32% | 69% | 78% | 85% | 93% | 71% |
| hunting | 60% | 74% | 83% | 88% | 95% | 59% |
| repair | 45% | 73% | 79% | 86% | 93% | 65% |
| adaptive | 40% | 65% | 76% | 83% | 92% | 64% |
| counter | 23% | 38% | 48% | 61% | 79% | 37% |
| mixed | 34% | 50% | 61% | 71% | 84% | 44% |

**Lookahead Japan** (v1.0.3; 128 holdout seeds per cell):

| Opponent | Recruit | Agent | Veteran | Legend | Mastermind |
|---|---:|---:|---:|---:|---:|
| look: adaptive values; bot reply previewed for its 8 best moves × 3 sampled cards | 41% | 54% | 69% | 78% | 97% |
| lookc: counter values, 8 moves × 3 sampled cards | 19% | 32% | 42% | 56% | 77% |
| lookc, wide: counter values, 16 moves × 4 sampled cards | 9% | 15% | 24% | 30% | 54% |

The wide search exploits the bot's predictability. It removes the early Caches with Assault + Reprisal right after the bot's Gathers and Ambushes have activated the guards, and it eliminates more Force 136 markers. Rules meant to protect thin Caches were tested against it on v1.0 and made the bot weaker against every opponent (Train first at a thin Cache; never activating a Cache's last Underground guerrilla; the same for Gather only). The levels carry the difference instead: Mastermind wins about half the time against it.

The same lookahead was run against the one-step search player, which has no fixed priorities:

| Opponent | Search player | Agent |
|---|---:|---:|
| lookc, 8 moves × 3 cards | 28% | 32% |
| lookc, 16 moves × 4 cards | 23% | 15% |

The search player loses almost as badly, so most of the wide search's edge looks like strong Japanese play. The 8-point gap against the wide search is an observed difference between two different British players on 128 games, not a measured cost of predictability.

**Scripted stress policies** (Agent v1.0.3, seeds 20000–20255: 256 games per policy, 1,024 in all). Each takes the best plan, by the adaptive values, that keeps its rule; only when no plan does may it play anything else.

| Japan always… | Force 136 wins |
|---|---:|
| Eliminates, or makes a Limited Assault or Sweep | 256 / 256 (100%) |
| takes the Limited box | 256 / 256 (100%) |
| Deploys or Constructs | 237 / 256 (93%) |
| takes the Event | 253 / 256 (99%) |

Committing to one kind of move is a poor way to beat the bot.

**Map reading.** With GPT's alternative northern railway-corner adjacency, Agent wins 60.0% instead of 61.3% (holdout 1).

**One more rule tested on the corrected Japan.** Because Kempeitai now stay with Force 136 markers after Redeploy, a variant moved every marker that shares a space with Kempeitai at Redeploy, not only exposed ones. It scored 60.5% against 60.0% on 768 development games: no gain, so the printed Redeploy rule stands.

## How the design was found

Each step was measured on development seeds with matched games (all six policies unless noted). The figures in this section come from v1.0 and v1.0.1 development, against the Japan model as it was before v1.0.3's two corrections; they were not rerun. They show which choices mattered, not current win rates.

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

So Force 136 never takes Events. That also removes the bot's longest lookup. (These Event tests ran on v1.0, before the Train refresh and the Japan corrections, and were not rerun.)

## Verification

- **Rules as code.** `force136_v1.py` follows the printed rules section by section. The tuning lab (`force136.py`) and the printed-rules module play move for move the same in 960 games across all five levels (`equiv.py`: 0 mismatches).
- **Clean-room implementation.** A second agent implemented the bot from the printed rules alone, without seeing any bot code (`cleanroom/`). Later rule changes (British J22, J27, J12 and J15; the Train refresh) were added to it by the primary author, and the file says so. Japan's choices, including the Japanese Redeploy and the J25 return, sit in the shared engine.
- **Checker on policy games** (`verify_v1.py`):

    1. *Cross-check.* Both bots play the same seed. After every Force 136 turn the Directive card, goal, box, Operation, Special Activity and board must match, along with every track and the pieces off the map and in pools. The same holds after every Propaganda reset and for the final result.
    2. *Scoring oracle.* Every Propaganda score in both bots is recomputed from the rulebook alone (6.1–6.2.5, 6.7.2, 7.0.1, 1.13) plus the level bonus: Resistance, winner, Zipper box, Cache track and Caches on the map. This catches errors in the engine code both bots share.
    3. *Forced capabilities.* 96 games with each side of each capability in play from the start, and 192 each with all six British or all six Japanese sides.

    For v1.0.3, 2,496 games (960 normal ones across the five levels, plus 1,536 forced-capability games) gave 0 cross-check failures and 0 oracle failures.
- **Mutation tests.** `verify_v1.py --mutants` plants 15 deliberate errors in the bots and the engine's scoring and Zipper code; all 15 are caught. Both modes exit with status 1 on a failure (`check_exit_status.py`).
- **Random positions** (`fuzz_v1.py`, new in v1.0.3). The checker above only sees positions that the computer Japan policies reach; that is how v1.0.1's stacked-marker Redeploy error went unseen. The fuzzer builds random legal positions directly: any mix of pieces, markers, tracks and capability sides, including stacked markers and empty pools. From each it makes both bots take a Force 136 turn (three Directive cards, two sets of free boxes), run a nonfinal Propaganda, resolve both British icons, and receive a Japanese Extract and Construct (for British J15 and J12). For v1.0.3: 12,000 positions and 132,000 actions, with 0 differences. Run against v1.0.1's bot, the same fuzzer finds the Redeploy error in 57 of 1,500 positions.
- **Legality** (`legality_v1.py`, new in v1.0.3). An independent check, written from GMT's player aid and rulebook rather than from the bot's procedures, of whether a British player could legally have made each change to the board: every Operation, Special Activity, icon and British Resources step, with Ambush rolls checked against the logged die. For v1.0.3 it checked 240 policy games (3,810 bot turns) and 2,000 random positions (12,000 bot turns), about 35,000 Operations, Special Activities and icons in all, and found 0 violations. Seven three-destination Raids in the games were too large for its search and stay unconfirmed. It flags all six planted illegal actions in its self-test.
- **Fixtures.** `review_fixtures.py` holds 15 fixed-position tests: 12 reproductions from GPT's three reviews, using GPT's saved positions (`fixtures/audit_33745a6/`), and 3 for the v1.0.2 audit's findings (Japan's guerrilla choice, the Kempeitai that stays and the J25 return, British J12 and J15). All pass.
- **Printed numbers.** `report_check.py` recomputes every win-rate cell and interval in this report's summary and per-policy tables, the stress table's counts, the rules' level table and the README from the stored results, and fails on any mismatch.
- **Limits.** The engine is GPT's research executor. Only its Propaganda scoring and Zipper placement are checked independently; its Operations and Events were compared with the player aids and card faces by reading, not by a second implementation. The Japan policies are heuristics: v1.0.3 corrected two weak choices, and others may remain, so the win rates could still be somewhat high against sound play.

## Bot behaviour (Agent, seeds 0–999)

A game gives Force 136 about 16 turns. A turn needs 2.2 goal checks on average, plus 0.8 Special Activity checks (counted over 600 games). These are counts of procedure steps, not measured time.

| Goal used | Share of turns |
|---|---:|
| TRAIN | 35% |
| AMBUSH | 34% |
| PLACE | 24% |
| INTEL | 6% |
| SUPPLY (Directive 9) | 1.1% |
| Pass | 0.1% |
| CONTACT | under 0.1% |

| Most common actions | Share of turns |
|---|---:|
| Limited Train | 26% |
| Ambush + Raid | 15% |
| Limited Contact (placing a marker) | 14% |
| Ambush + Gather | 14% |
| Train + Supply | 9% |
| Contact + Gather | 8% |

## Interpretations and limits

- **Rules readings used by the bot:**

    - When none of the colour is Available, Train takes a guerrilla from another space, and as a last resort re-places an Active one in the Train space itself (1.4.1; its example names both).
    - Gather reveals the chit in the activated guerrilla's own space.
    - A Contact must place or move a marker.
    - Ambush in Kuala Lumpur can only remove Police.
    - Under the Japanese side of J19, only the first Gather space may use adjacent spaces.
    - The Special Activity is chosen after the Operation, and its rolls, are resolved.
    - Japan makes the choices in the Events it executes (5.1), including where the J25 marker returns.

- **Engine readings that remain uncertain:**

    - J10's rounding: half the Resources lost, rounded down (7 becomes 4).
    - J13's British side: the engine runs two single-space Limited Operations; the card might allow two multi-space ones. It affects only the British-Event study (run on v1.0).
    - The northern railway corner: which spaces touch the Thailand railways (above: 1.3 points on 768 games).
    - Sabotage placed on an already sabotaged railway by J2 or J23.
    - Japan never Passes.

    No official clarification for these was found.

- **Untested:** no physical playtest has been run, and turn time has not been measured. The win rates are conditional on this executor and these opponents.

## Version history

Win rates on seeds 0–999 (6,000 games per level), for Recruit / Agent / Veteran / Legend / Mastermind:

| Version | Change | Win rates |
|---|---|---|
| v1.0 | first release (printed 36 / 61 / 71 / 79 / 89 from a smaller holdout sample that ran about 1.5 points high) | 34.7 / 59.7 / 70.1 / 78.1 / 89.0 |
| v1.0.1 | Train re-places an Active guerrilla in its own space as the last source: +4.8 at Agent (GPT's independent check: +4.2) | 41.3 / 64.4 / 74.0 / 81.6 / 91.3 |
| v1.0.2 | stacked exposed markers all Redeploy; text fixes; strict stress policies | unchanged, game for game |
| v1.0.3 | Japan model corrected (Underground guerrillas removed first; Kempeitai stay with Force 136; J25 return is Japan's choice) | 38.8 / 61.3 / 70.9 / 78.8 / 89.2 |

The reviews behind each step are in `REVIEW_RESPONSE.md` and the repository's `audits/` folder.

## Reproduce

From the `code/` folder, with Python 3.11+ and only the standard library:

```text
python3 equiv.py 32 recruit,agent,veteran,legend,mastermind   # printed rules == tuning lab
python3 fresh_v101.py 0 1000 fresh_v103                # level results, seeds 0-999 (6,000 games per level)
python3 verify_v1.py 32                                # checker: cross-check, scoring oracle, forced capabilities
python3 verify_v1.py --mutants 16                      # the checker must catch 15 planted errors
python3 fuzz_v1.py 12000 700000                        # both bots on 12,000 random positions
python3 legality_v1.py games 8                         # legality of every action in 240 games
python3 legality_v1.py fuzz 2000                       # legality from 2,000 random positions
python3 legality_v1.py selftest                        # six planted illegal actions
python3 review_fixtures.py                             # GPT's reproductions as tests
python3 check_exit_status.py                           # the checker fails loudly
python3 report_check.py                                # printed tables == stored results
python3 holdout_v1.py 20000 128 holdout1_v103 agent    # first holdout
python3 look_run.py 20000 128 recruit,agent,veteran,legend,mastermind look
python3 look_run.py 20000 128 recruit,agent,veteran,legend,mastermind lookc
python3 look_deep.py 20000 128 recruit,agent,veteran,legend,mastermind lookc 16 4
python3 look_expert.py 20000 128 8 3                   # the same lookahead against the one-step search player
python3 look_expert.py 20000 128 16 4
python3 refs.py                                        # v0.2 bot, its best variant, the search player
POLS=brute,tempo,econ,eventhog python3 holdout_v1.py 20000 256 exploits_v103 agent
python3 corner_run.py
python3 sample_game.py 20005 adaptive
```

Earlier versions' result files stay in `results/` (see its README). The v1.0.2 audit's sensitivity scripts are in `audits/v1.0.2/evidence/`.

The printed rules are `force136_v1.py`. The engine is `engine.py` (GPT's executor) with `expert.py` (Japan policies and the search player). `force136.py` is the tuning lab.
