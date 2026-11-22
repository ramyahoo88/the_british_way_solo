# Force 136 v1.1 — simulation report

21 November 2026 · Human Japan vs the Force 136 bot · standard standalone Japanese Occupation

## Summary

Force 136 is a card-driven British bot for the Japanese Occupation scenario. On 6,000 simulated games per level (seeds 0–999, never used for tuning), against six computer Japan policies, Force 136 wins:

| Level | Change | Force 136 wins | 95% interval | Mean final Resistance | MPAJA wins |
|---|---|---:|---:|---:|---:|
| Recruit | never Raids | 39.6% | 37.7–41.4% | 15.4 | 5.7% |
| **Agent** | standard | **63.0%** | 61.2–64.7% | 17.5 | 4.5% |
| Veteran | Resistance starts at 4 | 72.5% | 70.9–74.1% | 18.3 | 4.0% |
| Legend | starts at 4; +1 Resistance after each nonfinal Propaganda | 80.2% | 78.8–81.6% | 18.9 | 3.5% |
| Mastermind | starts at 6; +2 Resistance after each nonfinal Propaganda | 90.0% | 89.0–91.0% | 19.5 | 2.9% |

The rules print the rounded figures 40%, 63%, 72%, 80% and 90%. Intervals: whole-seed bootstrap, 10,000 resamples, `random.Random(33745)` for each level (`report_check.py` recomputes them).

These are computer-model results, not tabletop win rates. A strong human Japan player is expected to beat the computer policies more often. A computer Japan that previews the bot's reply, whenever it acts first on a card, holds Agent to about 16% and Mastermind to 60% (below). No physical playtest has been run.

**What changed in v1.1.** Force 136 now plays two Events. When Japan has already acted on the card and left the Event box free, it plays the British side of J4 (Chin Peng) or J25 (John Davis) if that side would do something (rules section 4, step 2). Every Event was retested against the corrected Japan (*Events*, below), and these two were the only ones that gained in both confirmation runs. On the same 6,000 games per level as v1.0.3 and v1.0.4, paired game for game, they add:

| Level | Change in wins (points) | 95% interval | Change in mean final Resistance |
|---|---:|---:|---:|
| Recruit | +0.8 | −0.1 to +1.7 | +0.14 |
| Agent | +1.7 | +0.9 to +2.5 | +0.14 |
| Veteran | +1.6 | +0.9 to +2.4 | +0.11 |
| Legend | +1.4 | +0.7 to +2.1 | +0.08 |
| Mastermind | +0.8 | +0.2 to +1.4 | +0.04 |

Intervals as above (Recruit's just includes zero); `ev_package.py` recomputes this table from the stored games. The games are identical until the first turn where the Event step fires, so most of them do not change; between 289 (Mastermind) and 639 (Recruit) of the 6,000 have a different winner. Against the lookahead Japan the change is about the same: 17 more wins in the 1,920 games of the 15 lookahead cells, +0.9 points (*Events*, below).

**What changed in v1.0.4 and v1.0.3.** v1.0.4 changed print and test tools only. v1.0.3 followed a full audit of v1.0.2 (`audits/v1.0.2/` in the repository), which found no illegal bot play and no difference between the two bot implementations on 12,000 random positions. Its main finding was in the model, not the bot: the computer Japan made two choices that a real Japan player would not, and both helped Britain.

- When Japan removed a guerrilla (Food Shortage icon, J11, J18), it took an Active one first. An Underground guerrilla is the better one to remove: only those can Ambush, Sabotage or Gather.
- At Japanese Redeploy it moved every Kempeitai to a space with more Troops than guerrillas, even one that was already sitting with a Force 136 marker. The move is optional (rule 6.5.2), and a Kempeitai next to a marker is where Japan wants it.

Japan now removes Underground guerrillas first and leaves one Kempeitai with each Force 136 marker it already shares a space with. A third fix follows rule 5.1: after the Japanese side of J25, Japan chooses the Province the marker returns to, not Britain. On the same 6,000 games per level, these lowered the win rates by 2 to 3 points: Recruit −2.5, Agent −3.2 (95% interval −4.2 to −2.2), Veteran −3.2, Legend −2.8, Mastermind −2.1. GPT's audit reran both versions on 256 other seeds and found a smaller change at Agent, −1.0 points (−3.0 to +0.9), so the size of that drop is less certain than the stored sample alone suggests.

On the first holdout (seeds 20000–20127, 768 games), where Agent wins 62.8% (482 games):

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
- **Protocol.** Rules were tuned only on development seeds (6000–7300 and 10000–10327); v1.1's Event study used seeds 410000–430999. Level results use seeds 0–999 (first used for v1.0.1, after tuning ended); the lookahead and reference runs use the holdout seeds 20000–20127 (128 seeds, so differences under about 10 points are noise). Games on the same seed share Event deals across policies, levels and versions.

## Results by Japan policy (seeds 0–999)

| Japan policy | Recruit | Agent | Veteran | Legend | Mastermind | Search player (holdout 1) |
|---|---:|---:|---:|---:|---:|---:|
| extraction | 34% | 70% | 80% | 86% | 94% | 71% |
| hunting | 60% | 74% | 83% | 89% | 95% | 59% |
| repair | 45% | 73% | 81% | 86% | 92% | 65% |
| adaptive | 41% | 67% | 77% | 85% | 93% | 64% |
| counter | 24% | 40% | 52% | 63% | 81% | 37% |
| mixed | 33% | 53% | 63% | 72% | 85% | 44% |

**Lookahead Japan** (128 holdout seeds per cell):

| Opponent | Recruit | Agent | Veteran | Legend | Mastermind |
|---|---:|---:|---:|---:|---:|
| look: adaptive values; bot reply previewed for its 8 best moves × 3 sampled cards | 39% | 58% | 70% | 81% | 97% |
| lookc: counter values, 8 moves × 3 sampled cards | 17% | 33% | 43% | 57% | 77% |
| lookc, wide: counter values, 16 moves × 4 sampled cards | 8% | 16% | 25% | 28% | 60% |

The wide search exploits the bot's predictability. It removes the early Caches with Assault + Reprisal right after the bot's Gathers and Ambushes have activated the guards, and it eliminates more Force 136 markers. Rules meant to protect thin Caches were tested against it on v1.0 and made the bot weaker against every opponent (Train first at a thin Cache; never activating a Cache's last Underground guerrilla; the same for Gather only). The levels carry the difference instead: Mastermind wins about 60% against it.

The same lookahead was run against the one-step search player, which has no fixed priorities:

| Opponent | Search player | Agent |
|---|---:|---:|
| lookc, 8 moves × 3 cards | 28% | 33% |
| lookc, 16 moves × 4 cards | 23% | 16% |

The search player loses almost as badly, so most of the wide search's edge looks like strong Japanese play. The 7-point gap against the wide search is an observed difference between two different British players on 128 games, not a measured cost of predictability.

**Scripted stress policies** (Agent, seeds 20000–20255: 256 games per policy, 1,024 in all). Each takes the best plan, by the adaptive values, that keeps its rule; only when no plan does may it play anything else.

| Japan always… | Force 136 wins |
|---|---:|
| Eliminates, or makes a Limited Assault or Sweep | 256 / 256 (100%) |
| takes the Limited box | 256 / 256 (100%) |
| Deploys or Constructs | 236 / 256 (92%) |
| takes the Event | 253 / 256 (99%) |

Committing to one kind of move is a poor way to beat the bot.

**Map reading.** With the wider northern railway-corner adjacency, Agent wins 61.2% instead of 62.8% (holdout 1). On 6,000 fresh paired games GPT measured a smaller change, −0.35 points; see *Interpretations and limits*.

**One more rule tested on the corrected Japan** (on v1.0.3). Because Kempeitai now stay with Force 136 markers after Redeploy, a variant moved every marker that shares a space with Kempeitai at Redeploy, not only exposed ones. It scored 60.5% against 60.0% on 768 development games: no gain, so the printed Redeploy rule stands.

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

v1.0 tested every Event on 288 games each and printed none. That test ran before the Train refresh and the Japan corrections, and a bot that never plays an Event can look wrong to players, so v1.1 tested them all again, on v1.0.4 against the corrected Japan (`ev_study_v104.py`).

For one Event card at a time, a variant bot takes the Event box when that card is revealed and the box is free, and plays the British side if it would do something. A second variant (*deny*) also takes it as first player when it would do nothing, only to keep the Japanese side from Japan. It still draws and discards its Directive card that turn. Each variant game is paired with the unchanged bot on the same seed and Japan policy; the two are identical until the card appears. Changes are in win points over the games where the choice arose, with whole-seed bootstrap intervals.

- **Screen:** all 30 Events that a player can choose (every card but the Mandatory J6 and J9), seeds 410000–410255, 1,536 games per Event and variant.
- **As first player** every Event lowered the win rate, by 1.5 points (J20 Lim Bo Seng, the closest to zero) to 26 points (J3, J17, J26 and J32). The *deny* variant did no better. An Event taken first leaves Japan the Op & SA box.
- **As second player,** where the Event replaces a Limited Operation, nine Events had a positive estimate. The seven most promising were rerun on 6,000 fresh games (seeds 420000–420999), and those still positive on a second 6,000 (seeds 430000–430999):

| Event, taken as second player | Block 1: games where taken, change (95% interval) | Block 2: games where taken, change (95% interval) |
|---|---:|---:|
| J4 Chin Peng | 1,153 · +4.3 (+1.5 to +7.2) | 1,185 · +4.1 (+1.2 to +6.9) |
| J25 John Davis | 1,296 · +3.0 (+0.2 to +6.0) | 1,453 · +2.1 (−1.0 to +5.2) |
| J26 Subhas Chandra Bose | 326 · +4.0 (−0.9 to +9.7) | 361 · +3.1 (−0.9 to +7.1) |
| J10 Rationing System | 675 · +2.5 (−0.7 to +5.8) | 729 · −0.4 (−4.4 to +3.2) |
| J1 Sook Ching | 271 · +1.9 (−4.6 to +8.1) | not rerun |
| J23 Allied Bombing | 1,378 · −0.4 (−2.9 to +2.2) | not rerun |
| J28 Operation Gustavus | 1,116 · −0.9 (−4.0 to +2.1) | not rerun |

J4 and J25 gained in both blocks. J26 gained in both, but neither interval excludes zero; it comes up in about 6% of games, and its British side needs a targeting rule and a roll, so it is left out. J10 did not hold up, and J1, J23 and J28 showed nothing clear.

The two adopted Events were then played together as printed, on the 6,000 games per level of the level table, which neither the screen nor the blocks used. That is the change table in the summary: +0.8 to +1.7 points at every level, and the printed rules play those 30,000 games exactly as the study's variant bot did. Both Events are cheap at the table: J4 counts the spaces with Force 136 and a Jungle Camp, and J25 is a CONTACT turn.

Against the lookahead Japan (128 holdout seeds per cell), v1.1 against v1.0.4:

| Opponent | Recruit | Agent | Veteran | Legend | Mastermind |
|---|---:|---:|---:|---:|---:|
| look, 8 moves × 3 cards | 39% (41%) | 58% (54%) | 70% (69%) | 81% (78%) | 97% (97%) |
| lookc, 8 moves × 3 cards | 17% (19%) | 33% (32%) | 43% (42%) | 57% (56%) | 77% (77%) |
| lookc, wide: 16 moves × 4 cards | 8% (9%) | 16% (15%) | 25% (24%) | 28% (30%) | 60% (54%) |

The cells move by −2 to +6 points, all within the noise of 128 games; in all, v1.1 wins 17 more of the 1,920 games (+0.9 points), about the same as against the one-step policies. The lookahead Japan previews the bot's real procedures, Event step included, so it can play around J4 and J25.

## Verification

- **Rules as code.** `force136_v1.py` follows the printed rules section by section. The tuning lab (`force136.py`) and the printed-rules module play move for move the same in 960 games across all five levels (`equiv.py`: 0 mismatches).
- **Clean-room implementation.** A second agent implemented the bot from the printed rules alone, without seeing any bot code (`cleanroom/`). Later rule changes (British J22, J27, J12 and J15; the Train refresh; v1.1's Event step) were added to it by the primary author, and the file says so. Japan's choices, including the Japanese Redeploy and the J25 return, sit in the shared engine.
- **Checker on policy games** (`verify_v1.py`):

    1. *Cross-check.* Both bots play the same seed. After every Force 136 turn the Directive card, goal, box, Operation, Special Activity and board must match, along with every track and the pieces off the map and in pools. The same holds after every Propaganda reset and for the final result.
    2. *Scoring oracle.* Every Propaganda score in both bots is recomputed from the rulebook alone (6.1–6.2.5, 6.7.2, 7.0.1, 1.13) plus the level bonus: Resistance, winner, Zipper box, Cache track and Caches on the map. This catches errors in the engine code both bots share.
    3. *Forced capabilities.* 96 games with each side of each capability in play from the start, and 192 each with all six British or all six Japanese sides.

    For v1.1, 2,496 games (960 normal ones across the five levels, plus 1,536 forced-capability games) gave 0 cross-check failures and 0 oracle failures. They include 1,218 Event turns (434 J4, 784 J25).
- **Mutation tests.** `verify_v1.py --mutants` plants 17 deliberate errors in the bots and the engine's scoring and Zipper code, two of them in the Event step (omitted; also taken as first player); all 17 are caught. Both modes exit with status 1 on a failure (`check_exit_status.py`).
- **Random positions** (`fuzz_v1.py`). The checker above only sees positions that the computer Japan policies reach; that is how v1.0.1's stacked-marker Redeploy error went unseen. The fuzzer builds random legal positions directly: any mix of pieces, markers, tracks and capability sides, including stacked markers and empty pools; in 30% of them the card is J4 or J25, and when two boxes are left Japan has taken the third, so the Event step fires. From each it makes both bots take a Force 136 turn (three Directive cards, two sets of free boxes), run a nonfinal Propaganda, resolve both British icons, and receive a Japanese Extract and Construct (for British J15 and J12). Afterwards every state field must match: board, Sabotage, capabilities, tracks, pools, pieces off the map, deck and eligibility fields, and the end-of-game flags. Two runs of 12,000 positions (264,000 actions in all, 5,503 of them Event turns: 1,448 J4 and 4,055 J25) show 0 differences. Run against v1.0.1's bot, the fuzzer finds the Redeploy error in 57 of 1,500 positions.
- **Legality** (`legality_v1.py`). A check, written from GMT's player aid and rulebook rather than from the bot's procedures, of whether a British player could legally have made each change to the board: every Operation, Special Activity, icon and British Resources step. Ambush and Supply rolls are checked against the logged dice, Supply against the spaces actually selected, and each Raid step by step from the positions observed after every destination. A British Event may only be J4 or J25 in the Event box: J4 must add exactly 1 Resistance per space with Force 136 and a Jungle Camp and change nothing else, and J25's Contact and Special Activity are checked like any others. It checked 960 policy games (15,690 bot turns, 374 of them Event turns) and 12,000 random positions (72,000 bot turns, 2,801 of them Event turns), about 194,000 Operations, Special Activities, icons and Resources steps in all, and found 0 violations; all 12,034 Raids were confirmed. GPT's audit of v1.0.3 validated all 537 Raids of its 240-game sample with its own step checker. The self-test plants ten illegal actions, one of them a J4 counted per marker instead of per space, and all are flagged.
- **Fixtures.** `review_fixtures.py` holds 19 fixed tests: 12 reproductions from GPT's first three reviews, using GPT's saved positions (`fixtures/audit_33745a6/`); 3 for the v1.0.2 audit's findings (Japan's guerrilla choice, the Kempeitai that stays and the J25 return, British J12 and J15); 1 that the flowchart and footnote corrected in v1.0.4 stay corrected; and 3 for v1.1's Event step (J4 taken only as second player and only when it scores, never on other cards; J25 the same in both bots; the printed texts). All pass.
- **Printed numbers.** `report_check.py` recomputes every win-rate cell and interval in this report's summary, v1.1-change and per-policy tables, the stress table's counts, the lookahead tables, the rules' level table and the README from the stored results, and fails on any mismatch.
- **Limits.** The two bots share the engine, including Japan's choices, and the clean-room bot's later rules were added by the primary author, so their agreement shows consistency, not full independence. The random positions satisfy the piece limits but are not shown to be reachable in play. The engine is GPT's research executor. Only its Propaganda scoring and Zipper placement are checked independently; its Operations and Events were compared with the player aids and card faces by reading, not by a second implementation. The Japan policies are heuristics: v1.0.3 corrected two weak choices, and others may remain, so the win rates could still be somewhat high against sound play.

## Bot behaviour (Agent, seeds 0–999)

A game gives Force 136 about 16 turns. A turn needs 2.2 goal checks on average, plus 0.8 Special Activity checks (counted over 600 games of v1.0.3; v1.1's Event check adds a step only on J4 and J25 after Japan has acted). These are counts of procedure steps, not measured time.

| Goal used | Share of turns |
|---|---:|
| TRAIN | 34% |
| AMBUSH | 32% |
| PLACE | 24% |
| INTEL | 6% |
| Event (J4, J25) | 2.6% |
| SUPPLY (Directive 9) | 1.1% |
| Pass | 0.1% |
| CONTACT | under 0.1% |

| Most common actions | Share of turns |
|---|---:|
| Limited Train | 23.8% |
| Ambush + Raid | 14.5% |
| Ambush + Gather | 13.8% |
| Limited Contact (placing a marker) | 13.7% |
| Train + Supply | 8.6% |
| Contact + Gather | 7.9% |
| Event (J4 or J25) | 2.6% |

## Interpretations and limits

- **Readings settled by the rulebook:**

    - When none of the colour is Available, Train takes a guerrilla from another space, or re-places one from the Train space itself back Underground (1.4.1; the example of play does both). Force 136 uses the second only as a last resort.
    - Gather reveals the chit in each activated guerrilla's own space (4.2.2 and its example).
    - A Special Activity may come before, during or after its Operation (4.1); Force 136 always chooses it after the Operation and its rolls.
    - Japan makes the choices in the Events it executes (5.1), including where the J25 marker returns.
    - J4's British side adds 1 Resistance per space with a Force 136 marker and a Jungle Camp; J25's is a Contact, then any Special Activity (card texts). The bot chooses J25's Special Activity as for the CONTACT goal.
    - Card tips: J2 and J23 may place Sabotage on a railway that already has it (the engine allows this), and J19's Japanese side lets Gather use adjacent guerrillas for only one selected space (Force 136 uses the first).

- **Bot choices within the rules:** a Contact must place or move a marker, and Ambush in Kuala Lumpur only removes Police.

- **Engine readings that remain open or known to be narrow:**

    - J10's rounding: the card says to reduce Japan's Resources by half, rounding down. The engine rounds the amount removed (7 becomes 4), not what is left (which would give 3).
    - J13's British side: the engine runs each of its two Limited Operations in one space, but rule 2.4.4 lets British Limited Operations use every eligible space. GPT's follow-up review (`audits/v1.1/`) corrected it and reran J13 on 6,000 games: still negative as first player (−11.3 points where taken) and as second (−3.0, interval −6.7 to +0.4), so it stays out. Force 136 never plays J13; the one-step search player can, and with the correction it wins 438 of the 768 holdout games (57.0%) instead of 434 (56.5%). The results here use the uncorrected engine.
    - The northern railway corner: the model counts only the Province on each Thailand border. Both reviews favour the wider reading of rule 1.3.6, which also counts the Provinces meeting the end of that border. On 6,000 fresh paired Agent games it changed the win rate by −0.35 points (95% interval −0.75 to +0.05; GPT's follow-up). All published rates assume the narrower reading.
    - Japan never Passes.

    No official ruling was found for J10's rounding or the railway corner.

- **Untested:** no physical playtest has been run, and turn time has not been measured. The win rates are conditional on this executor and these opponents.

## Version history

Win rates on seeds 0–999 (6,000 games per level), for Recruit / Agent / Veteran / Legend / Mastermind:

| Version | Change | Win rates |
|---|---|---|
| v1.0 | first release (printed 36 / 61 / 71 / 79 / 89 from a smaller holdout sample that ran about 1.5 points high) | 34.7 / 59.7 / 70.1 / 78.1 / 89.0 |
| v1.0.1 | Train re-places an Active guerrilla in its own space as the last source: +4.8 at Agent (GPT's independent check: +4.2) | 41.3 / 64.4 / 74.0 / 81.6 / 91.3 |
| v1.0.2 | stacked exposed markers all Redeploy; text fixes; strict stress policies | unchanged, game for game |
| v1.0.3 | Japan model corrected (Underground guerrillas removed first; Kempeitai stay with Force 136; J25 return is Japan's choice) | 38.8 / 61.3 / 70.9 / 78.8 / 89.2 |
| v1.0.4 | print fixes (flowchart footer, lookahead footnote, page numbers); stronger test tools | unchanged, game for game |
| v1.1 | J4 and J25 played as second player when they would do something (rules 4, step 2): +0.8 to +1.7 | 39.6 / 63.0 / 72.5 / 80.2 / 90.0 |

The reviews behind each step are in `REVIEW_RESPONSE.md` and the repository's `audits/` folder.

## Reproduce

From the `code/` folder, with Python 3.11+ and only the standard library:

```text
python3 equiv.py 32 recruit,agent,veteran,legend,mastermind   # printed rules == tuning lab
python3 fresh_v101.py 0 1000 fresh_v110                # level results, seeds 0-999 (6,000 games per level)
python3 ev_package.py                                  # v1.1 against v1.0.3/v1.0.4 on those games
python3 ev_study_v104.py screen 256 410000             # Event screen, every Event, both variants
python3 ev_study_v104.py confirm 10:second,4:second,23:second,26:second,1:second,25:second,28:second 1000 420000
python3 ev_study_v104.py confirm 4:second,25:second,10:second,26:second 1000 430000
python3 verify_v1.py 32                                # checker: cross-check, scoring oracle, forced capabilities
python3 verify_v1.py --mutants 16                      # the checker must catch 17 planted errors
python3 fuzz_v1.py 12000 700000                        # both bots on 12,000 random positions (also run from seed 240000)
python3 legality_v1.py games 32                        # legality of every action in 960 games
python3 legality_v1.py fuzz 12000                      # legality from 12,000 random positions
python3 legality_v1.py selftest                        # ten planted illegal actions
python3 review_fixtures.py                             # fixed tests
python3 check_exit_status.py                           # the checker fails loudly
python3 report_check.py                                # printed tables == stored results
python3 holdout_v1.py 20000 128 holdout1_v110 agent    # first holdout
python3 look_run.py 20000 128 recruit,agent,veteran,legend,mastermind look
python3 look_run.py 20000 128 recruit,agent,veteran,legend,mastermind lookc
python3 look_deep.py 20000 128 recruit,agent,veteran,legend,mastermind lookc 16 4
python3 look_expert.py 20000 128 8 3                   # the same lookahead against the one-step search player
python3 look_expert.py 20000 128 16 4
python3 refs.py                                        # v0.2 bot, its best variant, the search player
POLS=brute,tempo,econ,eventhog python3 holdout_v1.py 20000 256 exploits_v110 agent
python3 corner_run.py
python3 sample_game.py 20005 adaptive
```

The search player and the references do not use the bot's rules, so their v1.0.3 runs stand (`v103_lookexpert.log`, `refs_v103.json`). Earlier versions' result files stay in `results/` (see its README). The v1.0.2 audit's sensitivity scripts are in `audits/v1.0.2/evidence/`.

The printed rules are `force136_v1.py`. The engine is `engine.py` (GPT's executor) with `expert.py` (Japan policies and the search player). `force136.py` is the tuning lab.
