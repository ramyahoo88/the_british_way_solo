# Force 136 v1.1 — card-driven British bot for Japanese Occupation

A new solo opponent for *The British Way: Enemy of My Enemy*, Japanese Occupation scenario. You play Japan; Force 136 plays the British; the MPAJA stays the game's independent actor. It replaces the v0.2 draft on `main` rather than revising it.

**Five levels**, from Recruit (the bot never Raids) to Mastermind.

**How it plays:** draw one of nine Directive cards; if Japan has already acted on J4 or J25 and left the Event box free, play that Event's British side when it would do something; otherwise, with the Op & Special Activity box free, do the first goal that qualifies (PLACE, then the card's goals, then CONTACT), or else take a Limited Operation (PLACE, then the card's AMBUSH/TRAIN choice). About 16 bot turns a game and 2.2 goal checks a turn. No dice of its own, no peeking, and only two Events.

## Print and play

| File | Contents |
|---|---|
| [Print-and-play PDF](print/Force_136_v1_Print_and_Play.pdf) | Rules (6 numbered pages), two-sided reference sheet, nine Directive cards (1 sheet), optional card backs, record sheet |
| [Rules PDF](print/Force_136_v1_Rules.pdf) · [Markdown](print/Force_136_v1_Rules.md) | Full rules with a worked opening |
| [Reference sheet](print/Force_136_v1_Reference.pdf) | Front: turn, goals, orders, levels, scoring. Back: procedures and between-turn choices |
| [Directive cards](print/Force_136_v1_Cards.pdf) | Nine poker-size cards; print at 100% and cut on the dashed lines. Page 2 holds the backs; all nine are identical, so duplex alignment does not matter |
| [Sample game](print/Force_136_v1_Sample_Game.pdf) · [Markdown](print/Force_136_v1_Sample_Game.md) | A full simulated game, turn by turn |
| [Record sheet](print/Force_136_v1_Record_Sheet.pdf) | One page to log a playtest, turn by turn |
| [Simulation report](print/Force_136_v1_Sim_Report.pdf) · [Markdown](print/Force_136_v1_Sim_Report.md) | Results, how the design was found, limits |

## Levels and results

v1.1, 6,000 simulated games per level on seeds never used for tuning, against six computer Japan policies:

| Level | Change | Force 136 wins |
|---|---|---:|
| Recruit | never Raids | 40% |
| Agent | standard | 63% |
| Veteran | Resistance starts at 4 | 72% |
| Legend | starts at 4; +1 Resistance after each nonfinal Propaganda | 80% |
| Mastermind | starts at 6; +2 Resistance after each nonfinal Propaganda | 90% |

On the first holdout (seeds 20000–20127), Agent won 63%. On the same games, v0.2 won 0% and its best experimental variant 1%. A one-step search player won 57%; it compares a fixed menu of plans and scores each with a hand-written evaluation. Japan policies that preview the bot's reply, whenever Japan acts first on a card, are much harder. The widest one holds Agent to about 16%, Legend to 28% and Mastermind to 60% (128 games each). Mastermind is for players who learn to exploit the bot. These are model results, not tabletop win rates. The bot has not yet been playtested at the table.

**v1.1** (21 November) adds two Events. A bot that never plays an Event can look wrong to players, so every Event was retested against the corrected Japan: 30 Events on 1,536 paired games each, then 6,000 and 6,000 more for the promising ones. Every Event taken as first player lowered the win rate. As second player, only J4 (Chin Peng) and J25 (John Davis) gained in both confirmation runs. Force 136 now plays their British side when Japan has already acted on the card and the Event box is free, if it would do something (rules section 4, step 2). On the same 6,000 games per level this adds 0.8 to 1.7 points at every level (Agent +1.7, 95% interval +0.9 to +2.5), and against the lookahead Japan it is about the same (+0.9 points over 1,920 games).

**v1.0.4** (21 November) fixes the four findings of GPT's audit of v1.0.3 (commit 595f409), which found no gameplay or scoring defect. The turn flowchart now says "Never execute the Event" (a Pass may sit in the Event box). The level footnote says the lookahead Japan previews the bot's reply when it acts first on a card, not before every move. The legality check now uses the Supply spaces and rolls and checks Raids step by step, and the random-position test compares every state field. The booklet has page numbers and the sample game lists Japan's moves and the icons. The bot and all results are unchanged.

**v1.0.3** (21 November) follows a full audit of v1.0.2 ([report](../audits/v1.0.2/Force_136_v1.0.2_Audit_338cb0d.md)). The bot's play was legal and both implementations agreed on 12,000 random positions. The main finding was in the simulation: the computer Japan removed Active guerrillas before Underground ones, and at Redeploy it pulled its Kempeitai away from Force 136 markers. Both helped Britain. With Japan corrected, the win rates are about 3 points lower than v1.0.2 printed (41 / 64 / 74 / 82 / 91%). Rules changes are small: after J25, Japan chooses where the marker returns (rule 5.1); the British sides of J12 and J15 get printed procedures; a Pass cannot use the Event box on J6 or J9.

**v1.0.2** fixed five problems from GPT's audit of commit 33745a6: stacked exposed markers now all Redeploy; the reference's J27 line; "never executes an Event"; and the stress-test policies and their table.

**v1.0.1** added one rule after GPT's review of v1.0: when Train finds no guerrilla Available and no other space can give one, it re-places an Active guerrilla in the Train space, back Underground (rule 1.4.1). That gained 4.8 points at Agent in paired games.

See [REVIEW_RESPONSE.md](REVIEW_RESPONSE.md) for every review finding and its fix.

## Code

`code/` runs on Python 3.11+ with the standard library.

- `force136_v1.py` — the printed rules as code (one function per rules section).
- `engine.py` — the game executor from GPT's v0.2 simulation study, adopted and audited against the Vassal card faces and player aids.
- `expert.py` — the Japan policies (four from v0.2, plus `counter` and `mixed`), the exploit policies and the one-step search player.
- `lookahead.py` — Japan policies that simulate the bot's reply.
- `cleanroom/` — an independent implementation written from the printed rules alone (later rule changes were added to it by the primary author; the file lists them).
- `verify_v1.py` — the checker on whole games: compares both bots' full public state after every turn and Propaganda and their final results, recomputes every Propaganda score from the rulebook, and runs forced-capability games; `--mutants` shows it catches 17 planted errors.
- `fuzz_v1.py` — both bots on random legal positions (stacked markers, empty pools, British capability sides), where whole games rarely go.
- `legality_v1.py` — an independent check, written from GMT's player aid, that every bot action is one a British player could legally make.
- `review_fixtures.py` — 19 fixed tests from the five reviews and the v1.1 Event step; `report_check.py` checks every printed win rate, interval and stress-table count against the stored results; `check_exit_status.py` checks that the checker fails loudly.
- `force136.py` — the tuning lab; `equiv.py` checks it plays move-for-move like `force136_v1.py`.
- `ev_study_v104.py` — the v1.1 Event study (every Event, first and second player, paired games); `ev_package.py` — v1.1 against v1.0.4 on the stored level games.
- `sample_game.py` + `sample_md.py` — regenerate the narrated sample game.
- `results/` — fresh-seed and holdout results, checker output, Event tests, order sweeps, the sample game.
- `lab/` — exploration scripts in the order they were used; run them from `code/` with `PYTHONPATH=. python3 lab/<script>.py`.

The commands that reproduce every reported number are at the end of the simulation report. `print/build.py` rebuilds the PDFs (Python-Markdown, pypdf and headless Google Chrome).

See [PLAYTEST.md](PLAYTEST.md) for what to record in the first tabletop games, [NOTES.md](NOTES.md) for the development log and [REVIEW_RESPONSE.md](REVIEW_RESPONSE.md) for the independent rules review, GPT's review of v1.0 and how each finding was resolved.

Unofficial fan variant, not a GMT publication. Publisher rulebooks, Event text, maps and artwork are not included.
