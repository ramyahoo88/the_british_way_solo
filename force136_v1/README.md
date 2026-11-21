# Force 136 v1.0 — card-driven British bot for Japanese Occupation

A new solo opponent for *The British Way: Enemy of My Enemy*, Japanese Occupation scenario. You play Japan; Force 136 plays the British; the MPAJA stays the game's independent actor. It replaces the v0.2 draft on `main` rather than revising it.

**How it plays:** draw one of nine Directive cards; never take the Event; with the Op & Special Activity box free, do the first goal that qualifies (PLACE, then the card's four goals, then CONTACT); otherwise take a Limited Operation (PLACE, then the card's AMBUSH/TRAIN choice). About 16 bot turns a game and 2.3 goal checks a turn. No dice of its own, no peeking, no Events.

## Print and play

| File | Contents |
|---|---|
| [Print-and-play PDF](print/Force_136_v1_Print_and_Play.pdf) | Rules (5 pages), two-sided reference sheet, nine Directive cards (1 sheet) |
| [Rules PDF](print/Force_136_v1_Rules.pdf) · [Markdown](print/Force_136_v1_Rules.md) | Full rules with a worked opening |
| [Reference sheet](print/Force_136_v1_Reference.pdf) | Front: turn, goals, orders, levels, scoring. Back: procedures and between-turn choices |
| [Directive cards](print/Force_136_v1_Cards.pdf) | Nine poker-size cards; print at 100% and cut on the dashed lines |
| [Sample game](print/Force_136_v1_Sample_Game.pdf) · [Markdown](print/Force_136_v1_Sample_Game.md) | A full simulated game, turn by turn |
| [Simulation report](print/Force_136_v1_Sim_Report.pdf) · [Markdown](print/Force_136_v1_Sim_Report.md) | Results, how the design was found, limits |

## Levels and results

Holdout simulations: 768 games per level, six computer Japan policies, seeds never used for tuning.

| Level | Change | Force 136 wins |
|---|---|---:|
| Recruit | never Raids | 37% |
| Agent | standard | 59% |
| Veteran | Resistance starts at 4 | 69% |
| Legend | starts at 4; +1 Resistance after each nonfinal Propaganda | 77% |

For comparison on the same games: v0.2 won 0%, its best experimental variant 2%, and a one-step search player that tries every legal British action 56.5%. Against Japan policies that look ahead at the bot's reply, Agent wins 33–51% and Legend 53–68%. These are model results, not tabletop win rates. The bot has not yet been playtested at the table.

## Code

`code/` runs on Python 3.11+ with the standard library.

- `force136_v1.py` — the printed rules as code (one function per rules section).
- `engine.py` — the game executor from GPT's v0.2 simulation study, adopted and audited against the Vassal card faces and player aids.
- `expert.py` — the Japan policies (four from v0.2, plus `counter` and `mixed`), the exploit policies and the one-step search player.
- `lookahead.py` — Japan policies that simulate the bot's reply.
- `force136.py` — the tuning lab; `equiv.py` checks it plays move-for-move like `force136_v1.py`.
- `sample_game.py` + `sample_md.py` — regenerate the narrated sample game.
- `results/` — holdout results, Event tests, order sweeps, the sample game.
- `lab/` — exploration scripts in the order they were used; run them from `code/` with `PYTHONPATH=. python3 lab/<script>.py`.

The commands that reproduce every reported number are at the end of the simulation report. `print/build.py` rebuilds the PDFs (Python-Markdown, pypdf and headless Google Chrome).

See [NOTES.md](NOTES.md) for the development log and [REVIEW_RESPONSE.md](REVIEW_RESPONSE.md) for the independent rules review and how each finding was resolved.

Unofficial fan variant, not a GMT publication. Publisher rulebooks, Event text, maps and artwork are not included.
