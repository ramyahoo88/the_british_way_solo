# Force 136 v1.0 — simulation report

21 November 2026 · Human Japan vs the Force 136 bot · standard standalone Japanese Occupation

## Summary

Force 136 v1.0 is a new card-driven British bot. It replaces the v0.2 draft rather than revising it. On 768 simulated games per level that were never used for tuning, against six computer Japan policies, it wins:

| Level | Change | Force 136 wins | 95% interval | Mean final Resistance | MPAJA wins |
|---|---|---:|---:|---:|---:|
| Recruit | never Raids | 37.6% | 32–43% | 14.8 | 4.9% |
| **Agent** | standard | **59.9%** | 55–65% | 17.0 | 3.1% |
| Veteran | Resistance starts at 4 | 67.7% | 63–73% | 17.9 | 4.6% |
| Legend | starts at 4; +1 Resistance after each nonfinal Propaganda | 77.2% | 73–81% | 18.6 | 3.0% |
| Mastermind | starts at 6; +2 Resistance after each nonfinal Propaganda | 87.6% | 85–90% | 19.4 | 3.5% |

On the same games:

- GPT's v0.2 paper bot, run in the same executor, won 0.0% (mean Resistance 1.3).
- v0.2's best experimental variant ("primary + recovery/guard") won 2.0% (mean Resistance 5.4).
- A one-step search player that tries every legal British action and scores it with a hand-written evaluation won 56.9% (mean Resistance 16.8).

The printed Agent bot plays at least as well as that search player.

A second holdout on 256 more seeds (1,536 games per level, seeds 20128–20383) confirms the levels: Recruit 35.9%, Agent 61.8%, Veteran 71.9%, Legend 79.5%, Mastermind 89.9%. Pooled over both holdouts (2,304 games per level), the rates are 36%, 61%, 71%, 79% and 89%. Those are the figures printed in the rules.

These are computer-model results, not tabletop win rates. A strong human Japan player is expected to beat the computer policies more often. Japan policies that simulate the bot's exact reply before moving do much better (below): the widest search holds Agent to 13% and Legend to 31%. The Mastermind level exists for players who learn to exploit the bot that way.

## The model

- **Engine.** GPT's research executor (research-0.2, from the v0.2 simulation evidence), adopted with its paper-bot code removed from the British side. It covers the full scenario and was audited for this study:

    - Turns and setup: setup, the 21-card deck with Propaganda in each pile's bottom three, both factions' Operations and Special Activities, eligibility.
    - Cards and markers: all 32 Events, the six capabilities, MPAJA icons, the Zipper track with its cache releases.
    - Propaganda and pools: full Propaganda, victory, piece pools.

    I checked the setup, icon sets, Event effects, Operations and Propaganda against the card faces and player aids in the Vassal module (3.1.1) and against the GMT rulebook. I found no discrepancy that changes play.

- **Japan.** Six one-step policies. Four are GPT's: extraction, hunting, repair and adaptive. Two are new:

    - *counter* minimizes the British evaluation used by the search player, so it attacks what that evaluation values.
    - *mixed* averages counter and adaptive.

    Two lookahead variants (look, lookc) simulate the bot's actual reply, with a sampled Directive card, before choosing. Four scripted exploit policies try to abuse a predictable bot.

- **Information.** Policies see only public information. Concealed Intel values stay hidden from both sides' decisions. Dice and Intel draws are keyed to the seed, so matched games share Event deals.
- **Protocol.** Rules were tuned only on development seeds (6000–7300 and 10000–10327). Every number in the summary uses the untouched holdout seeds 20000–20127, crossed with the six policies (768 games per row). The intervals resample whole seeds.

## Results by Japan policy (holdout)

| Japan policy | Recruit | Agent | Veteran | Legend | Mastermind | Search player |
|---|---:|---:|---:|---:|---:|---:|
| extraction | 32% | 63% | 72% | 84% | 95% | 66% |
| hunting | 59% | 73% | 78% | 82% | 91% | 63% |
| repair | 38% | 68% | 77% | 84% | 91% | 67% |
| adaptive | 43% | 63% | 70% | 80% | 89% | 64% |
| counter | 20% | 38% | 48% | 59% | 74% | 36% |
| mixed | 34% | 54% | 63% | 74% | 85% | 46% |

**Lookahead Japan** (128 holdout seeds per cell):

| Opponent | Recruit | Agent | Veteran | Legend | Mastermind |
|---|---:|---:|---:|---:|---:|
| look: adaptive values; bot reply simulated for its 8 best moves | 38% | 52% | 61% | 71% | 89% |
| lookc: counter values, 8 moves × 3 sampled cards | 16% | 34% | 45% | 54% | 77% |
| lookc, wide: counter values, 16 moves × 4 sampled cards | 7% | 13% | 19% | 31% | 48% |

The wide search exploits the bot's predictability. It removes the early Caches (0.7 on the map at the first Propaganda instead of 1.6) with Assault + Reprisal right after the bot's Gathers and Ambushes have activated the guards, and it eliminates more Force 136 markers. Rules meant to protect thin Caches were tested against it and made the bot weaker against every opponent:

- Train first at a thin Cache: 14% (no change);
- never activating a Cache's last Underground guerrilla: 6%;
- the same rule for Gather only: 8%.

The levels carry the difference instead: Mastermind (Resistance 6, +2 per nonfinal Propaganda) wins 48% against it.

**Exploit attempts** (Agent, 256 games):

| Japan always… | Force 136 wins |
|---|---:|
| Eliminates, or makes Limited Assaults and Sweeps | 94% |
| takes the Limited box to keep the initiative | 98% |
| plays economically (Deploy, Extract, Construct) | 69% |
| grabs the Event whenever possible | 72% |

None of these beats the regular policies.

**Map reading.** With GPT's alternative northern railway-corner adjacency, Agent wins 59.2% instead of 59.9%.

## How the design was found

Each step was measured on development seeds with matched games (all six policies unless noted).

1. **Start from GPT's procedures.** A plain priority bot built on v0.2's targeting rules won 8% against GPT's four policies.
2. **Place Force 136 first.** Contacting to place an Available marker before anything else on Limited turns: 34%. Ambush before Train on Limited turns: 42%.
3. **Find where the gap was.** Handing only the full-turn (Op & SA) choices to the search player closed most of the gap to it (44.8% vs 36.5%). So the full-turn order mattered most.
4. **Sweep the full-turn order.** All 120 orders were tested. PLACE first dominates. After it, decks led by AMBUSH, or by INTEL then AMBUSH, win 54–56%. Decks led by INTEL without AMBUSH next win 30–39%, and decks led by SUPPLY or TRAIN win 8–28%.
5. **Fix the procedures that mattered.**

    - Taking a guerrilla from elsewhere on the map when none is Available (rule 1.4) was worth +7 points. Refreshing an Active guerrilla in its own space would add 5 more, but it is not clearly legal, so the bot does not do it.
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

So Force 136 never takes Events. That also removes the bot's longest lookup.

## Verification

- **Rules as code.** `force136_v1.py` follows the printed rules section by section. The tuning lab (`force136.py`) and the printed-rules module play move for move the same in 960 games across all five levels (`equiv.py`: 0 mismatches). This includes the nine cards as printed, where cards 1–8 omit a SUPPLY goal that would only repeat TRAIN.
- **Independent rules review.** A reviewer who saw only the printed rules, reference sheet and cards reported 21 findings. Twenty were text problems: ambiguities, omissions and reference-sheet gaps. They were fixed by making the text say what the simulation does. One was a real code error: the British choice under the Japanese side of J27 removed Opposition from the highest-Population space instead of the lowest. It was fixed and all results rerun. See `REVIEW_RESPONSE.md`.
- **Clean-room check.** A second agent implemented the bot from the printed rules alone, without seeing any bot code. It reproduced the worked example exactly. `cleancmp.py` plays both versions on the same games and compares every Force 136 decision and the board after every Force 136 turn. Early runs found three places where my code did not do what the text says, all fixed:
    - New Village removal was delayed;
    - J8 Supply re-chose a Province after a failed roll;
    - the Special Activity was chosen before the Ambush roll instead of after it.

    It also found an engine choice made in Britain's favour (Japanese side of J20), now Japan's. After the fixes the two versions agree on every decision and every board in 960 games across the five levels.

## Bot behaviour (Agent, holdout)

A game gives Force 136 about 16 turns. Most turns need one to three goal checks (2.3 on average).

| Goal used | Share of turns |
|---|---:|
| TRAIN | 35% |
| AMBUSH | 33% |
| PLACE | 24% |
| INTEL | 5% |
| Pass | 1.7% |
| CONTACT | 1.1% |
| SUPPLY (Directive 9) | 0.8% |

| Most common actions | Share of turns |
|---|---:|
| Limited Train | 24% |
| Ambush + Raid | 15% |
| Limited Contact (placing a marker) | 14% |
| Ambush + Gather | 13% |
| Train + Supply | 9% |
| Contact + Gather | 8% |

## Interpretations and limits

- **Rules readings used by the bot:**

    - Train may take a guerrilla from another space when none is Available (1.4 exception).
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
python3 holdout_v1.py 20000 128 holdout                # level results (all five levels)
python3 look_run.py 20000 128 recruit,agent,veteran,legend,mastermind look
python3 look_run.py 20000 128 recruit,agent,veteran,legend,mastermind lookc
python3 look_deep.py 20000 128 recruit,agent,veteran,legend,mastermind lookc 16 4
POLS=brute,tempo,econ,eventhog python3 holdout_v1.py 20000 64 exploits agent
python3 corner_run.py
python3 ev_test_v1.py 48 31000
python3 ev_confirm.py 32000 192 23:second,24:second,10:second,24:always
python3 holdout_v1.py 20128 256 confirm
python3 cleancmp.py 32 recruit,agent,veteran,legend,mastermind   # clean-room comparison (960 games)
python3 sample_game.py 20005 adaptive
```

The printed rules are `force136_v1.py`. The engine is `engine.py` (GPT's executor) with `expert.py` (Japan policies and the search player). `force136.py` is the tuning lab.
