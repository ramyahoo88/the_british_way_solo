# Force 136 v1.0.1 — card-driven British bot for Japanese Occupation

A new solo opponent for *The British Way: Enemy of My Enemy*, Japanese Occupation scenario. You play Japan; Force 136 plays the British; the MPAJA stays the game's independent actor. It replaces the v0.2 draft on `main` rather than revising it.

**Five levels**, from Recruit (the bot never Raids) to Mastermind.

**How it plays:** draw one of nine Directive cards; never take the Event; with the Op & Special Activity box free, do the first goal that qualifies (PLACE, then the card's goals, then CONTACT); otherwise take a Limited Operation (PLACE, then the card's AMBUSH/TRAIN choice). About 16 bot turns a game and 2.3 goal checks a turn. No dice of its own, no peeking, no Events.

## Print and play

| File | Contents |
|---|---|
| [Print-and-play PDF](print/Force_136_v1_Print_and_Play.pdf) | Rules (6 pages), two-sided reference sheet, nine Directive cards (1 sheet), optional card backs, record sheet |
| [Rules PDF](print/Force_136_v1_Rules.pdf) · [Markdown](print/Force_136_v1_Rules.md) | Full rules with a worked opening |
| [Reference sheet](print/Force_136_v1_Reference.pdf) | Front: turn, goals, orders, levels, scoring. Back: procedures and between-turn choices |
| [Directive cards](print/Force_136_v1_Cards.pdf) | Nine poker-size cards; print at 100% and cut on the dashed lines. Page 2 holds the backs; all nine are identical, so duplex alignment does not matter |
| [Sample game](print/Force_136_v1_Sample_Game.pdf) · [Markdown](print/Force_136_v1_Sample_Game.md) | A full simulated game, turn by turn |
| [Record sheet](print/Force_136_v1_Record_Sheet.pdf) | One page to log a playtest, turn by turn |
| [Simulation report](print/Force_136_v1_Sim_Report.pdf) · [Markdown](print/Force_136_v1_Sim_Report.md) | Results, how the design was found, limits |

## Levels and results

v1.0.1, 6,000 simulated games per level on fresh seeds never used for tuning, against six computer Japan policies:

| Level | Change | Force 136 wins |
|---|---|---:|
| Recruit | never Raids | 41% |
| Agent | standard | 64% |
| Veteran | Resistance starts at 4 | 74% |
| Legend | starts at 4; +1 Resistance after each nonfinal Propaganda | 82% |
| Mastermind | starts at 6; +2 Resistance after each nonfinal Propaganda | 91% |

On the first holdout (seeds 20000–20127), Agent won 65%. On the same games, v0.2 won 0% and its best experimental variant 2%. A one-step search player won 57%; it compares a fixed menu of plans and scores each with a hand-written evaluation. Japan policies that preview the bot's reply before moving are much harder. The widest one holds Agent to about 15%, Legend to 26% and Mastermind to 51% (128 games each). Mastermind is for players who learn to exploit the bot. These are model results, not tabletop win rates. The bot has not yet been playtested at the table.

**v1.0.1** (21 November, after GPT's review of v1.0) adds one rule. When Train finds no guerrilla Available and no other space can give one, it re-places an Active guerrilla in the Train space, back Underground (rule 1.4.1). That gained 4.8 points at Agent in paired games. It also makes the British J27 procedure explicit, rewords J8 on the reference sheet and corrects the descriptions of the benchmark opponents. A stronger checker verifies all of this. v1.0 printed 36/61/71/79/89%, from a smaller holdout sample that ran about 1.5 points high. See [REVIEW_RESPONSE.md](REVIEW_RESPONSE.md). GPT's re-audit of v1.0.1 passed it for tabletop testing; its two follow-ups (stale per-policy numbers in the report, and checker exit codes) are fixed, as is its optional Zipper check.

## Code

`code/` runs on Python 3.11+ with the standard library.

- `force136_v1.py` — the printed rules as code (one function per rules section).
- `engine.py` — the game executor from GPT's v0.2 simulation study, adopted and audited against the Vassal card faces and player aids.
- `expert.py` — the Japan policies (four from v0.2, plus `counter` and `mixed`), the exploit policies and the one-step search player.
- `lookahead.py` — Japan policies that simulate the bot's reply.
- `cleanroom/` — an independent implementation written from the printed rules alone (its British J22/J27 handling and the v1.0.1 Train fallback were added afterwards, by me).
- `verify_v1.py` — the checker: compares both bots' full public state after every turn and Propaganda and their final results, recomputes every Propaganda score from the rulebook, and runs forced-capability games; `--mutants` shows it catches 15 planted errors. Both modes exit with status 1 on a failure (`check_exit_status.py` tests that). `review_fixtures.py` turns GPT's review reproductions into tests, and `report_check.py` checks every printed win rate against the stored results. (`cleancmp.py` is the older, narrower comparison.)
- `force136.py` — the tuning lab; `equiv.py` checks it plays move-for-move like `force136_v1.py`.
- `sample_game.py` + `sample_md.py` — regenerate the narrated sample game.
- `results/` — fresh-seed and holdout results, checker output, Event tests, order sweeps, the sample game.
- `lab/` — exploration scripts in the order they were used; run them from `code/` with `PYTHONPATH=. python3 lab/<script>.py`.

The commands that reproduce every reported number are at the end of the simulation report. `print/build.py` rebuilds the PDFs (Python-Markdown, pypdf and headless Google Chrome).

See [PLAYTEST.md](PLAYTEST.md) for what to record in the first tabletop games, [NOTES.md](NOTES.md) for the development log and [REVIEW_RESPONSE.md](REVIEW_RESPONSE.md) for the independent rules review, GPT's review of v1.0 and how each finding was resolved.

Unofficial fan variant, not a GMT publication. Publisher rulebooks, Event text, maps and artwork are not included.
