# Force 136 v1.0 — card-driven British bot for Japanese Occupation

A new solo opponent for *The British Way: Enemy of My Enemy*, Japanese Occupation scenario. You play Japan; Force 136 plays the British; the MPAJA stays the game's independent actor. It replaces the v0.2 draft on `main` rather than revising it.

**How it plays:** draw one of nine Directive cards; never take the Event; with the Op & Special Activity box free, do the first goal that qualifies (PLACE, then the card's four goals, then CONTACT); otherwise take a Limited Operation (PLACE, then the card's AMBUSH/TRAIN choice). About 16 bot turns a game and 2.3 checks a turn. No dice of its own, no peeking, no Events.

## Print and play

| File | Contents |
|---|---|
| [Print-and-play PDF](print/Force_136_v1_Print_and_Play.pdf) | Rules (4 pages), reference sheet (1 page), nine Directive cards (1 sheet) |
| [Rules PDF](print/Force_136_v1_Rules.pdf) · [Markdown](print/Force_136_v1_Rules.md) | Full rules with a worked opening |
| [Reference sheet](print/Force_136_v1_Reference.pdf) | Turn, goals, procedures, orders, levels |
| [Directive cards](print/Force_136_v1_Cards.pdf) | Nine poker-size cards; print at 100% and cut on the dashed lines |
| [Sample game](print/Force_136_v1_Sample_Game.pdf) · [Markdown](print/Force_136_v1_Sample_Game.md) | A full simulated game, turn by turn |
| [Simulation report](print/Force_136_v1_Sim_Report.pdf) · [Markdown](print/Force_136_v1_Sim_Report.md) | Results, how the design was found, limits |

## Levels and results

Holdout simulations: 768 games per level, six computer Japan policies, seeds never used for tuning.

| Level | Change | Force 136 wins |
|---|---|---:|
| Recruit | never Raids | 34% |
| Agent | standard | 58% |
| Veteran | Resistance starts at 4 | 67% |
| Legend | starts at 4; +1 Resistance after each nonfinal Propaganda | 73% |

For comparison on the same games: v0.2 won 0%, its best experimental variant 2%, and a one-step search player that tries every legal British action 56.5%. Against a Japan policy that looks ahead at the bot's reply, Agent wins 24–52% and Legend 46–69%. These are model results, not tabletop win rates. The bot has not yet been playtested at the table.

## Code

`code/` runs on Python 3.11+ with the standard library.

- `force136_v1.py` — the printed rules as code (one function per rules section).
- `engine.py` — the game executor from GPT's v0.2 simulation study, adopted and audited against the Vassal card faces and player aids.
- `expert.py` — the Japan policies (four from v0.2, plus `counter` and `mixed`), the exploit policies and the one-step search player.
- `lookahead.py` — Japan policies that simulate the bot's reply.
- `force136.py` — the tuning lab; `equiv.py` checks it plays move-for-move like `force136_v1.py`.
- `results/` — holdout results, Event tests, order sweeps, the sample game.
- `lab/` — exploration scripts in the order they were used; run them from `code/` with `PYTHONPATH=. python3 lab/<script>.py`.

The commands that reproduce every reported number are at the end of the simulation report. `print/build.py` rebuilds the PDFs (Python-Markdown, pypdf and headless Google Chrome).

See [NOTES.md](NOTES.md) for the development log.

Unofficial fan variant, not a GMT publication. Publisher rulebooks, Event text, maps and artwork are not included.
