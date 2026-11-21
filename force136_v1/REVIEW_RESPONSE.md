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

After these fixes the two implementations agree on every decision and every board in 768 games across all four levels (`results/final_cleancmp.log`).

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
