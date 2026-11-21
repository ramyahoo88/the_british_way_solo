# Force 136 v1.0 — simulation report

21 November 2026 · Human Japan vs the Force 136 bot · standard standalone Japanese Occupation

## Summary

Force 136 v1.0 is a new card-driven British bot. It replaces the v0.2 draft rather than revising it. On 768 simulated games per level that were never used for tuning, against six computer Japan policies, it wins:

| Level | Change | Force 136 wins | 95% interval | Mean final Resistance | MPAJA wins |
|---|---|---:|---:|---:|---:|
| Recruit | never Raids | 34.4% | 29–40% | 14.4 | 4.0% |
| **Agent** | standard | **58.3%** | 53–64% | 16.8 | 3.8% |
| Veteran | Resistance starts at 4 | 66.9% | 62–72% | 17.6 | 3.9% |
| Legend | starts at 4; +1 Resistance after each nonfinal Propaganda | 72.8% | 68–77% | 18.3 | 4.0% |

On the same games:

- GPT's v0.2 paper bot, run in the same executor, won 0.0% (mean Resistance 1.2).
- v0.2's best experimental variant ("primary + recovery/guard") won 2.0% (mean Resistance 5.3).
- A one-step search player that tries every legal British action and scores it with a hand-written evaluation won 56.5% (mean Resistance 16.6).

The printed Agent bot plays at least as well as that search player.

These are computer-model results, not tabletop win rates. A strong human Japan player is expected to beat the computer policies more often. The hardest computer opponent, which looks one move ahead at the bot's reply, holds Agent to 24% and Legend to 46% (below).

## The model

- **Engine.** GPT's research executor (research-0.2, from the v0.2 simulation evidence), adopted with its paper-bot code removed from the British side. It covers the full scenario and was audited for this study:
    - Turns and setup: setup, the 21-card deck with Propaganda in each pile's bottom three, both factions' Operations and Special Activities, eligibility.
    - Cards and markers: all 32 Events, the six capabilities, MPAJA icons, the Zipper track with its cache releases.
    - Propaganda and pools: full Propaganda, victory, piece pools.

    I checked the setup, icon sets, Event effects, Operations and Propaganda against the card faces and player aids in the Vassal module (3.1.1) and against the GMT rulebook. I found no discrepancy that changes play.

- **Japan.** Six one-step policies. Four are GPT's: extraction, hunting, repair and adaptive. Two are new:
    - *counter* minimizes the British evaluation used by the search player, so it attacks what that evaluation values.
    - *mixed* averages counter and adaptive.

    Two lookahead variants (look, lookc) simulate the bot's actual reply before choosing. Four scripted exploit policies try to abuse a predictable bot.

- **Information.** Policies see only public information. Concealed Intel values stay hidden from both sides' decisions. Dice and Intel draws are keyed to the seed, so matched games share Event deals.
- **Protocol.** Rules were tuned only on development seeds (6000–7300 and 10000–10127). Every number in the summary uses the untouched holdout seeds 20000–20127, crossed with the six policies (768 games per row). The intervals resample whole seeds.

## Results by Japan policy (holdout)

| Japan policy | Recruit | Agent | Veteran | Legend | Search player |
|---|---:|---:|---:|---:|---:|
| extraction | 28% | 65% | 73% | 78% | 68% |
| hunting | 56% | 69% | 74% | 77% | 64% |
| repair | 33% | 66% | 77% | 81% | 66% |
| adaptive | 40% | 64% | 73% | 81% | 63% |
| counter | 17% | 31% | 44% | 50% | 35% |
| mixed | 33% | 56% | 61% | 69% | 43% |

**Lookahead Japan** (128 holdout seeds each):

| Opponent | Recruit | Agent | Veteran | Legend |
|---|---:|---:|---:|---:|
| look: adaptive values plus the bot's simulated reply | 28% | 52% | 63% | 69% |
| lookc: counter values plus the bot's simulated reply | — | 24% | — | 46% |

**Exploit attempts** (Agent, 256 games):

| Japan always… | Force 136 wins |
|---|---:|
| Eliminates, or makes Limited Assaults and Sweeps | 92% |
| takes the Limited box to keep the initiative | 98% |
| plays economically (Deploy, Extract, Construct) | 69% |
| grabs the Event whenever possible | 66% |

None of these beats the regular policies.

**Map reading.** With GPT's alternative northern railway-corner adjacency, Agent wins 57.7% instead of 58.3%.

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
- Forcing Supply in the last campaign: −1.
- Guarding thin Caches first: +0.9 on Limited turns, −8 or worse on full turns.
- Requiring Police or two targets for Ambush: −7.
- Intel-reach Contact placement: −11.
- Taking Limited when Japan took the Event: about 0 (+1.1 and −0.8 on two seed sets).

### Events

Each Event was tested on the final bot with paired games (48 seeds × 6 policies = 288 games per Event and mode), taking the British side whenever a sensible condition held:

- **Taken as first player,** replacing an Operation with a Special Activity: 27 of 28 Events lowered final Resistance, by up to 1.2. The exception, J31, gained 0.06.
- **Taken as second player,** replacing a Limited Operation: no Event gained more than 0.12 Resistance per game.

So Force 136 never takes Events. That also removes the bot's longest lookup.

## Bot behaviour (Agent, holdout)

A game gives Force 136 about 16 turns. Most turns need one to three goal checks (2.3 on average).

| Goal used | Share of turns |
|---|---:|
| AMBUSH | 34% |
| TRAIN | 30% |
| PLACE | 23% |
| SUPPLY | 6% |
| INTEL | 5% |
| Pass | 1.5% |
| CONTACT | 1% |

| Most common actions | Share of turns |
|---|---:|
| Limited Train | 25% |
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
- **Engine readings that remain uncertain:**
    - J10's rounding.
    - Sabotage placed on an already sabotaged railway by J2 or J23.
    - The Japanese Redeploy policy.
    - Japan never Passes.

    None involves a bot decision.

- **Untested:** no physical playtest has been run, and turn time has not been measured. The Japan policies are heuristics, not people. The win rates are conditional on this executor and these opponents.

## Reproduce

From the `code/` folder, with Python 3.11+ and only the standard library:

```text
python3 equiv.py 32 recruit,agent,veteran,legend      # printed rules == tuning lab (768 games, 0 mismatches)
python3 holdout_v1.py 20000 128 holdout                # level results
python3 look_run.py 20000 128 recruit,agent,veteran,legend look
python3 look_run.py 20000 128 agent,legend lookc
POLS=brute,tempo,econ,eventhog python3 holdout_v1.py 20000 64 exploits agent
python3 corner_run.py
python3 ev_test_v1.py 48 31000
python3 sample_game.py 20005 adaptive
```

The printed rules are `force136_v1.py`. The engine is `engine.py` (GPT's executor) with `expert.py` (Japan policies and the search player). `force136.py` is the tuning lab.
