# Force 136 v1.0 — response to the pre-playtest rules review

An independent reviewer read only the printed rules, reference sheet and cards (no code) and reported 21 findings. Each finding was checked against what the simulation code (`code/force136_v1.py`) actually does. Where the text and the code disagreed, the text was changed to match the simulated behaviour, except for finding 16, which was a code error.

| # | Finding | Resolution |
|---|---|---|
| 1 | INTEL could qualify with no Operation possible; Ambush scope; "2 or more" total or per space | Text now matches the code: try Ambush (every useful space) › Sabotage › Contact, skip any that would do nothing, and use the first after which Gather reaches 2 in total; otherwise INTEL fails. "Gather 2+" is defined as a total (§3). |
| 2 | Raid could repeat a destination | The code never did. Text: "up to 2 different destinations". |
| 3 | "Never mix colours" had two readings | The code uses reading B. Text: one colour per destination, never into a space holding the other colour. |
| 4 | §6.3 "useful" required Force 136, which a Raid destination lacks | §6.3 now covers Raid destinations, counting the guerrilla sent. |
| 5 | "Majority" undefined | Defined in §3: more guerrillas than cubes, as the code uses it. |
| 6 | When the MPAJA icon is resolved | Once per card, at reveal, before either player acts (rules 2.3, 5.4), as the engine does. Moved out of the numbered turn on the reference sheet. |
| 7 | Sabotage order and re-check | Text: F136 spaces in map order, re-checked at each space, as the code does. |
| 8 | Japanese side of J19 not handled | The code already restricted it: only the first chosen space may use adjacent spaces. Now in §6.5 and on the reference sheet. |
| 9 | Forced-loss priority unclear between rules and reference; Camps | Text matches the code: Active › minority colour › blue; in J6 a Cache only if no guerrilla; markers are not forces. |
| 10 | SUPPLY next to TRAIN is redundant; cards look more different than they play | Confirmed. SUPPLY now appears only on Directive 9. Cards 1–8 list three goals, with identical play (equivalence check: 0 mismatches). The design note says what the cards really change. |
| 11 | Mobilize shortage rule placed only under nonfinal Propaganda | Moved under "Every Propaganda, including the final one". |
| 12 | Supply's limit ignored Cache availability | Text: "no more than the Caches Available"; Supply does nothing with no Cache Available. |
| 13 | "Pass, then Contact" was dead text; the card said "if useful" | §4.5: Pass with no Contact (CONTACT has already failed). Card footer: "Nothing qualifies: Pass." |
| 14 | Reference-sheet omissions | All eight added: the Zipper rule; the Train fallback; "can reach" in Move; the full INTEL test; the Legend wording; forced losses; J8 and J27; Events Japan plays. |
| 15 | Train source choice had two readings | Text matches the code: source with an Active guerrilla of that colour › most cubes › map order; take an Active one if it has one. |
| 16 | Japanese side of J27: which Opposition goes | **Code fix.** The bot wrongly removed it from the highest-Population space. It now removes it from the lowest-Population chosen space with Opposition. Results were rerun. |
| 17 | Worked example omitted the icon and Japan's moves | Added the Kill Traitors icon, Japan taking J22's Japanese side, and Japan's Sweep and Eliminate on card 2. |
| 18 | J8's Japanese side made "would" uncheckable | §3: rolls made afterwards don't count in "would" tests. |
| 19 | "Clear railway", "mixed space", Thailand | Defined in §3. The Railway list is all eight railways; Thailand is never a space. |
| 20 | Camp from the map: preference or requirement | Text: an ordered preference, as the code does. |
| 21 | Recruit note pointed to Special Activities "on the card" | Text: skip Raid wherever it appears in a section 5 list. |

The reviewer also confirmed that every Operation and Special Activity pairing is legal, that tie-breaks always end in map order, the Railway list or colour, and that every "would" test can be decided from public information (now including J8).

## Clean-room reimplementation

A second independent agent wrote the bot from the printed rules alone (`code/cleanroom/cleanroom.py`), without seeing any of the bot code. It reproduced the worked example in section 10 exactly. `code/cleancmp.py` then plays both versions on the same games and compares every Force 136 decision and the board after every Force 136 turn.

The first comparison (192 games) found 15 games that diverged. In every one, both versions chose the same goal, box, Operation and Special Activity; the differences were in board details. There were two causes, both in my code, not in the text:

- **New Village removal timing.** When an Ambush moved the last Japanese cube out of a space with a New Village, my code removed the Village only at the end of the card. The rules remove it at once (1.15), as the clean-room version did. Fixed.
- **Supply under the Japanese side of J8.** After a failed roll my code chose another Province and rolled again. The printed text, and the clean-room version, choose all the Provinces first (no more than the Caches Available) and then roll. The code was changed to match the text.

A larger comparison (768 games) then found 8 more games that diverged, all on the Special Activity after an Ambush. My code chose the Special Activity before rolling, assuming the roll succeeded. The clean-room version resolved the Ambush first and chose on the actual board, which is how the text reads at the table. The code now does the same, and section 5 says so explicitly.

After these fixes the two implementations agree on every decision and every board in 960 games across all five levels (`results/final_cleancmp.log`).

The agent's list of readings it had to choose led to these clarifications in the text:

- "would" tests assume later rolls succeed;
- a British Limited Train or Ambush still uses every F136 space;
- each INTEL Operation is tested on its own;
- the game's Ambush success rule and +1 Resistance;
- the British side of J22 in Gather;
- "Zipper 12 or more";
- the J8 roll;
- a 2-guerrilla Majority comes from one source, and a sent guerrilla activates when it acts;
- Opposition goes to Provinces or Kuala Lumpur;
- British capability sides that Japan might play.

It also found one Japanese choice that the engine made in Britain's favour. Under the Japanese side of J20, the engine removed the least useful Force 136 marker. Japan executes the card, so the choice is Japan's: the engine now removes the marker that threatens the most Intel, then the one with most guerrillas. All results were rerun with this fix.

## GPT's review of v1.0 (commit 615c870) and v1.0.1

GPT reviewed v1.0 at commit 615c870 (`Force_136_v1_Claude_Review.pdf` and its evidence ZIP). It recommended keeping the design, fixing the verification and some printed explanations, and then going ahead with tabletop playtesting. I reran GPT's evidence scripts and fixtures against my code. Every finding reproduced. `code/review_fixtures.py` turns GPT's reproductions into tests of the revised code.

| # | GPT's finding | Resolution |
|---|---|---|
| F1 (high) | The clean-room comparison could approve a different winner: it compared plans, boards and Sabotage after each Force 136 turn, but not Resistance, other tracks, trace length or the final result. | Confirmed. The new checker, `code/verify_v1.py`, compares the full public state after every Force 136 turn and every Propaganda reset, plus the final result. That covers the Directive card, goal, every track, pieces off the map and capabilities, and unequal trace lengths fail. It also recomputes every Propaganda score from the rulebook, in both implementations, so it also catches errors in the engine code the two bots share. It catches all 13 deliberate errors in `verify_v1.py --mutants`, including GPT's own (+1 Resistance before final scoring). `cleancmp.py` now also rejects unequal lengths and checks Resistance and final results. |
| F2 | The clean-room bot missed the British sides of J22 (Gather does not activate) and J27 (one extra Ambush or Sabotage space). Normal games never exercise them, because Japan always plays its own side. | Confirmed and fixed in `cleanroom.py`. These changes were made by me, not by the clean-room agent, and the file says so. The checker now runs forced-capability games: each side of all six capabilities in play from the start, plus all-British and all-Japanese. Coverage counts show the British effects actually fired. |
| F3 | Same-space Train "refresh" is explicitly legal (rule 1.4.1's example); the report called it unclear. | Confirmed: my error. Retesting it led to a design change (below). |
| F4 | The reference sheet's "British J8: +1 Province without F136" can read as an extra Supply slot. | Reworded on the reference sheet and in section 6.6: the Province without F136 may fill an open slot; it does not add one. A fixture checks the limit. The British J22 reminder is now on the reference sheet's Gather line. |
| F5 | The search player and the lookahead Japan were described too strongly ("every legal action", "exact reply"); the 8-point gap was presented as the cost of predictability. | Reworded everywhere. The search player compares a fixed menu of plans, with the engine's procedures choosing spaces. The lookahead Japan previews the bot's real procedures with Directive cards drawn at random from all nine. The 8 points are an observed difference between two players, not a measured cause. |
| F6 | The root checksum manifest was stale. | Regenerated for every file on the branch, except the manifest itself. |
| Q1 | J27's extra space needed an explicit rule. | Section 7 now says: when Force 136 carries out an Ambush or Sabotage Operation, it adds the first space without Force 136, in map order, where that Operation would do something. The extra space never makes a goal qualify, and Raid never adds it. The printed-rules code had picked the Sabotage space by the engine's regional railway order; it now uses map order (GPT's seed 139004: Kedah). |
| Optional | "the card's four goals" was wrong; record turn time and rules look-ups. | Fixed: cards 1–8 have three goals and card 9 has four. The record sheet and `PLAYTEST.md` now ask for start and end times and a tally of rules look-ups. |

**Fresh-seed win rates.** GPT ran Agent on 192 new seeds (50000–50063, 60000–60127) and got 53.6%, against my published 61%. I reproduced those 1,152 games exactly. I then ran Agent on five blocks of 1,000 fresh seeds (30,000 games), which gave 58.2–60.5% per block and 59.5% overall. GPT's two windows were unusually low: only about 3 in 1,000 random 192-seed sets do as badly. My holdout's 61% was about 1.5 points high, which happens about one time in eight. The rules now print figures from 6,000 games per level on fresh seeds 0–999.

**Design change in v1.0.1: Train refresh as a last resort.** GPT tested refreshing before other sources and found no gain (−6, not significant); I found −0.9. Refreshing only when no other space can supply the guerrilla is different. It gained +6.5 and +7.1 on two development seed sets and +4.8 points (95% interval +3.8 to +5.8) in 6,000 paired games on fresh seeds, better against every Japan policy. It is one added sentence in section 6.2, so v1.0.1 adopts it. GPT's exhausted-pool position, where every Directive used to Pass, now Trains and Supplies. All results below were rerun on v1.0.1.
