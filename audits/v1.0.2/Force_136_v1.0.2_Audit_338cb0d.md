# Force 136 v1.0.2: comprehensive audit of commit 338cb0d

21 November 2026 · Human Japan versus the British Force 136 bot · audit by Claude (Fable 5.2)

**Verdict.** The bot plays legally and its two implementations agree, including on positions the earlier tests never reached. The published win rates were about 3 points too high, because the computer Japan in the simulations made two weak choices. One rules reading favoured Britain (J25). All findings are fixed in v1.0.3; the level rates are now 39 / 61 / 71 / 79 / 89%.

**Who did this.** This audit was made in the same working session that produced v1.0 to v1.0.2, by a different Claude model (Fable 5.2; the earlier work used Opus 5.5). It is a fresh pass against the sources, not an outside review like GPT's three. Section 5 lists what it could not check.

## 1. Findings

| ID | Area | Finding | Fixed in v1.0.3 by |
|---|---|---|---|
| A1 | Simulation model | Japan removed Active guerrillas before Underground ones. | Japan removes Underground first. |
| A2 | Simulation model | Japanese Redeploy pulled every Kempeitai away from Force 136 markers. | One Kempeitai stays with each marker it already shares a space with. |
| A3 | Rules, in Britain's favour | After the Japanese side of J25, the bot chose where its marker returned. Rule 5.1 gives that choice to Japan. | Japan chooses; the bot rule is deleted. |
| A4 | Rules, completeness | The British sides of J12 and J15 had no printed procedure; the code used rankings the rules did not state. | Two printed lines; code matches them. |
| A5 | Text | "Pass in the leftmost free box" did not say that the Event box is closed on J6 and J9. | One sentence in rules and reference. |
| A6 | Reference sheet | The Move line omitted the Jungle Camp that Contact places. | Added. |
| A7 | Verification | The checker compared the two bots only on positions that the computer Japan reached, and nothing checked legality independently. | Two new tools: `fuzz_v1.py` and `legality_v1.py`. |

A1 and A2 together change every published win rate, so they matter most. A3 is a real rules error but touches one card. A4 to A6 never changed a simulated game.

## 2. What was checked

| Check | Result |
|---|---|
| Printed rules, reference sheet and cards against `force136_v1.py`, line by line | Agreed, except A3 to A6. |
| GMT's British and Japanese player aids (read from the Vassal module images) against the bot's Operations, Special Activities, Limited Operations, Pass and icons | Every pairing and limit the bot uses is legal. British Limited Train, Sabotage and Ambush may use any number of Force 136 spaces. |
| Rulebook sections 1.3–1.4, 1.6–1.15, 2.3–2.4, 3.1–3.2, 4.1–4.2, 5.1–5.5, 6.1–6.7, 7.0, read through a text fetch of GMT's PDF. The tool paraphrases, so exact wording was taken from the player aids where it mattered. | Used for the legality rules and for A3. |
| All 32 Event faces, both sides, against `engine.execute_event` | Effects match. One choice was on the wrong side (A3). |
| Map: Initiative Track order, Zipper track and its Cache boxes, railways and adjacency | Match the engine. The northern railway corner stays an open reading. |
| Sample game (seed 20005), first campaign replayed by hand through the first Propaganda | Every bot choice follows the printed rules; the scoring (+3 Intel, +3 Caches, +4 majorities, −1 Neutral, −1 Police) recomputes. |
| Both bot implementations on random positions (`fuzz_v1.py`) | v1.0.2: 12,000 positions, 108,000 actions, 0 differences. v1.0.3: 12,000 positions, 132,000 actions, 0 differences. |
| Does the fuzzer find a known error? | Run against v1.0.1's bot it finds the stacked-marker Redeploy error in 57 of 1,500 positions. |
| Legality of every bot action (`legality_v1.py`) | v1.0.3: 240 policy games (3,810 bot turns) and 2,000 random positions (12,000 bot turns); about 35,000 Operations, Special Activities and icons checked; 0 violations. 7 of 537 Raids in the games were too large for the search (three destinations at Zipper 20) and stay unconfirmed; none was shown illegal. Six planted illegal actions are all flagged. |
| Existing suite on v1.0.3 | `verify_v1.py 32`: 2,496 games, 0 cross-check and 0 oracle failures. All 15 mutants caught. `equiv.py`: 960 games, 0 mismatches. 15 fixtures pass (GPT's 12 and 3 new ones for A1 to A4). Exit-status and printed-number checks pass. |
| Sensitivity of the win rate to Japan's choices | A1 and A2 below. |
| One bot rule retested on the corrected Japan | Redeploying every marker that shares a space with Kempeitai: 60.5% against 60.0% on 768 development games. No gain; rule unchanged. |

## 3. Findings in detail

### A1. Japan removed Active guerrillas first

**Where.** `engine.lose_guerrilla` with `british=False`: the Food Shortage icon (6 cards) and the Japanese sides of J11 and J18.

**Problem.** Japan chooses which MPAJA guerrilla Food Shortage removes. The engine removed an Active one whenever it could. Only Underground guerrillas can Ambush, Sabotage or Gather, and Active ones are already exposed to Assault, so a Japan player removes the Underground one. The engine's own Reprisal already preferred to move Underground guerrillas.

**Effect.** On seeds 0–299 (1,800 Agent games paired with v1.0.2's stored results), removing Underground first lowers Force 136 from 64.1% to 62.5%: −1.6 points (95% interval −2.8 to −0.5). Script: `evidence/jp_loss.py`.

**Fix.** `lose_guerrilla` now ranks Underground first for Japan's choices.

### A2. Japanese Redeploy pulled Kempeitai off Force 136 markers

**Where.** The Japanese Redeploy step of Propaganda (the same code sat in `engine.py`, `force136_v1.py`, `force136.py` and `cleanroom/clean_base.py`).

**Problem.** Rule 6.5.2 says Japan *may* move Kempeitai and Police to spaces with more Troops than guerrillas. The engine picked up every Kempeitai and put it down in such a space. A Kempeitai already sharing a space with a Force 136 marker was moved away whenever that space had too few Troops, which is the usual case where the bot has trained guerrillas. That removes the Eliminate threat at the start of each campaign, when Britain moves first. The same code kept one Police at such spaces "for intelligence", which only makes sense if the Kempeitai stays.

**Effect.** On seeds 0–299, leaving one Kempeitai with each marker lowers Force 136 from 64.1% to 61.1%: −3.1 points (−4.9 to −1.3). With A1 as well: 60.1%, −4.1 (−6.1 to −2.1). Scripts: `evidence/jp_redeploy.py`, `evidence/jp_both.py`.

**Fix.** A shared `engine.japan_redeploy()`: Police are spread as before; one Kempeitai stays with each Force 136 marker it already accompanies; the rest move as before.

**Results after A1, A2 and A3** (seeds 0–999, 6,000 games per level, paired with v1.0.2):

| Level | v1.0.2 | v1.0.3 | Change (95% interval) |
|---|---:|---:|---:|
| Recruit | 41.3% | 38.8% | −2.5 (−3.7 to −1.4) |
| Agent | 64.4% | 61.3% | −3.2 (−4.2 to −2.2) |
| Veteran | 74.0% | 70.9% | −3.2 (−4.1 to −2.2) |
| Legend | 81.6% | 78.8% | −2.8 (−3.7 to −1.9) |
| Mastermind | 91.3% | 89.2% | −2.1 (−2.8 to −1.4) |

The full 1,000 seeds give a smaller drop than the first 300 did; both intervals overlap. The lookahead, stress, reference and map-reading tables were all rerun and are in the simulation report.

### A3. The J25 marker's return is Japan's choice

**Rule.** J25's Japanese side: remove a Force 136 marker to the card, and return it to any Province with a Jungle Camp in the next Reset Phase. Rule 5.1 says the Faction executing an Event makes its choices unless the text names the other Faction. The text names nobody, and Japan executes it.

**Problem.** Rules section 7 told the bot where to return the marker ("preferring no Kempeitai; then no Force 136; then most guerrillas"), and the code did so. That is the same kind of error as the J20 choice corrected in v1.0: a Japanese choice made in Britain's favour.

**Fix.** The bot rule is deleted. Section 7 now says Japan makes the choices in the Events it executes, naming the marker removed by J20, J25 or J28 and the J25 return. In the simulations Japan returns it to a Camp Province with Kempeitai, then one that already has Force 136, then fewest guerrillas, most Troops, map order (`engine.j25_return`).

### A4. British J12 and J15 had no printed procedure

Section 7 said that with a British capability side in play the bot "takes every optional benefit, choosing by the matching procedure above, else in map order". For J12 (Opposition next to a railway that Construct repairs) and J15 (a guerrilla in each New Village space when Japan Extracts) no procedure matches exactly, and the engine used its own rankings: for J12 a rule that also looked at Terror and New Villages, for J15 a colour choice and a way of taking guerrillas from the map. A player could not have reproduced either from the page.

These sides arise only if Japan plays the British side of its own capability card, which no policy does and few players would. They are now printed, and both implementations follow the print:

- J12: one adjacent Province or Kuala Lumpur without Opposition: highest Population; then no Terror; then map order.
- J15: one guerrilla in each New Village Province, in map order: the colour the space has more of (red on a tie or if empty), if one is Available.

The fuzzer now also sends a Japanese Extract and Construct to both bots so that these lines are compared. Planting a wrong colour in J15 or a wrong order in J12 makes it report differences (50 and 52 in 600 positions).

### A5. Pass and Mandatory Events

Step 5 says to Pass in the leftmost free box, "even if that is the Event box". On J6 and J9 neither player may use the Event box (rule 5.4). The code already left it out. The rules and reference now say so.

### A6. Reference sheet: Camp on a Move

The reference's Place line ends "Add a Camp if none"; the Move line did not, although Contact places a Camp where a moved marker arrives too (rules 6.1). Added.

### A7. The checks could not see rare positions or illegal play

`verify_v1.py` plays both bots through whole games. It is thorough about what it compares, but it only meets positions the six policies produce. GPT's stacked-marker Redeploy error survived 2,496 such games for that reason and was found by a hand-built position. Separately, no test asked whether an action was legal under the publisher's rules; agreement between two bots written from the same booklet cannot show that.

**`fuzz_v1.py`** builds random legal positions: any mix of pieces, markers, tracks and capability sides, including stacked markers, empty pools and British capability sides. From each position both bots take a Force 136 turn (three Directive cards, two sets of free boxes), run a nonfinal Propaganda, resolve a Mobilize and a Kill Traitors icon, and receive a Japanese Extract and Construct. The full public state must match afterwards.

**`legality_v1.py`** looks only at the board before and after each Operation, Special Activity, icon or British Propaganda step and decides whether a British player could legally have done that, from rules written out of the player aid. It checks, for example, that Train places at most one guerrilla (two at a Cache), MPAJA only with a Camp or Cache, and takes pieces from the map only when none is Available; that each Ambush activates one Underground guerrilla and moves a piece only on a logged roll that beats the cubes; that Gather's reveals fit two (or three) Force 136 spaces and their neighbours; and that a Raid's result can be reached by legal Raid steps. Its self-test plants six illegal actions and all are flagged.

Neither tool found a fault in the v1.0.2 bot. They close the gap for later changes.

## 4. What held up

- **Legality.** Every Operation and Special Activity pairing the bot uses is allowed (Supply with Train or Contact; Gather with Contact, Sabotage or Ambush; Raid with any). Its Contact, Train, Sabotage, Ambush, Supply, Gather and Raid stay inside the player aid's limits in every position tested.
- **Rules as code.** Apart from A3 and A4, each printed sentence has matching code and the reverse. The worked opening in rules section 10 matches the sample game.
- **Scoring and victory.** The sample game's first Propaganda recomputes by hand; the existing oracle recomputes all of them.
- **Hidden information.** The bot's tests count concealed chits without reading them; previews fix the dice. (GPT's audit also changed hidden values in 1,152 positions without changing a choice.)
- **Earlier fixes.** The stacked Redeploy, J27, Event-box Pass, Train refresh, J8 limit and British J22/J27 fixtures all still pass.
- **Design.** The one bot rule most exposed to the corrected Japan (Redeploy) was retested and stands.

## 5. Limits

- The auditor shares a lineage and a session with the author. An outside reader may catch what both miss.
- The engine's Japanese Operations and Events were compared with the player aids and card faces by reading. There is still no second implementation of them; only Propaganda scoring and the Zipper have an independent oracle.
- The Japan policies are one-step heuristics. A1 and A2 were found by asking where the engine made a choice for Japan that a player would not make. I looked at the other fixed choices (which space Food Shortage and Seize Supplies hit, how Deploy places Kempeitai, how Police spread at Redeploy) and found nothing as clear, but I did not test them. The win rates may still be somewhat high against sound play, and the lookahead results (Agent about 15%) show how far a stronger Japan can push them down.
- The British-Event study (the reason the bot never takes Events) and the design-search figures were run on v1.0 against the uncorrected Japan and were not repeated.
- Open rules readings are unchanged: the northern railway corner, J10's rounding and J13's British side.
- Nothing here measures play at a table: no physical game, no timing.

## 6. Reproduce

The tools are in `force136_v1/code/` on the `claude-force136` branch at the v1.0.3 commit:

```text
python3 fuzz_v1.py 12000 700000        # both bots on random positions
python3 legality_v1.py games 8         # legality of every action in 240 policy games
python3 legality_v1.py fuzz 2000       # legality from random positions
python3 legality_v1.py selftest        # six planted illegal actions
python3 verify_v1.py 32                # the existing checker; --mutants 16 for its 15 planted errors
python3 review_fixtures.py
python3 report_check.py
```

The sensitivity runs for A1 and A2 are in `evidence/` beside this report. They must run on the v1.0.2 engine (commit 338cb0d), because v1.0.3 already contains the fixes:

```text
F136_CODE=<checkout at 338cb0d>/force136_v1/code python3 jp_loss.py 300
F136_CODE=<checkout at 338cb0d>/force136_v1/code python3 jp_redeploy.py 300
F136_CODE=<checkout at 338cb0d>/force136_v1/code python3 jp_both.py 300 agent
```

`evidence/fuzz_catches_v101.py` reruns the fuzzer against v1.0.1's bot. `evidence/count_checks.py` counts goal checks per turn.

Sources: GMT Games, *The British Way: Enemy of My Enemy*, Japanese Occupation rulebook ([PDF](https://gmtwebsiteassets.s3.us-west-2.amazonaws.com/TheBritishWay_EnemyofMyEnemy/EomE_JapOcc_Rules.pdf)); player aids, map and Event card faces as shown in the Vassal module, version 3.1.1. No publisher text or artwork is included here.
