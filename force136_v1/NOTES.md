# Force 136 v1.0 — development log

Brief (user, 22:00 CST, 20 Nov 2026): do for The British Way solo what was done for the Kutná Hora Mincmistr. Act as the board game designer with full control over rules, mechanics and testing. Use the GPT draft only as input. Make the best card-driven bot possible in about 8 hours. Working targets carried over from Mincmistr: card-driven, low overhead, competitive, difficulty levels, no dice of its own, plays like a normal player, minimal cheating.

## Sources

- The user's Vassal module 3.1.1: Event card faces J1–J35, player aid cards 1–4, map. Card texts and icons were transcribed and checked against the engine.
- GMT's Japanese Occupation rulebook (public PDF), queried section by section: sequence of play, components, victory, setup, and specific rulings (no zero-effect Contact; Ambush in Kuala Lumpur; Train at a Cache; Supply Cache removal by Assault; Extract New Village bonus once; SA timing; Gather same-space reading).
- GPT's v0.2 package and simulation evidence. Its executor (`engine.py`) was adopted: the setup, all 32 Events, capabilities, icons, Propaganda and victory matched the card faces and aids.

## Timeline (CST)

- 22:05 Vassal cards and aids transcribed. The GPT engine read in full. GPT's v0.2 bot reproduced at about 0–4% wins.
- 22:30 One-step British search player ("expert"): 54% against GPT's four Japan policies, so the scenario is winnable for Britain in this model. Its traces show it takes Op & SA as first player, Gathers whenever 2+ chits are in reach, and places Force 136 on Limited turns.
- 22:40 Simple rule bot: 8%. With PLACE first on Limited turns: 34%. Ambush before Train: 42%.
- 22:50 Added `counter` and `mixed` Japan (adversarial to the search player's evaluation). Expert: 21% / 25% against them.
- 23:00 Score breakdown showed Japan extracting about 8 Resources per Extract. Targeted Sabotage did not help: Japan switches to military Operations.
- 23:10 Hybrid test: the full-turn choice was the gap. 120-order sweep: PLACE first dominates; then AMBUSH (or INTEL then AMBUSH).
- 23:20 Event sweep (paired seeds): Events never beat the bot's own Operations. Dropped.
- 23:30 Clean rules-as-code rewrite lost 15 points. Ablation traced it to Train (taking pieces from elsewhere on the map) and Raid. Both rebuilt with written priorities; same-space "refresh" rejected as not clearly legal.
- 23:40 Contact placement away from cubes (+3–4). Gather-2+ first (+1–2). Levels measured (no Raid; starting Resistance; Propaganda bonus; Ambush +1 and an early Zipper were too weak).
- 23:45 Directive deck: nine cards drawn from the strongest orders. South-first tie-breaks rejected (−4.7).
- 23:50 Printability simplifications costed. `force136_v1.py` written; `equiv.py` shows 0 mismatches against the lab in 768 games.
- 23:55 Holdout: Recruit 34.4%, Agent 58.3%, Veteran 66.9%, Legend 72.8%. Search player 56.5%; v0.2 0%.
- 00:00 Lookahead and exploit opponents; corner-adjacency sensitivity (no change); guard rules (no gain); Event retest on the final bot.
- 00:10 Rules, reference sheet, cards, sample game and report written and rendered.

## Decisions worth remembering

- The bot never takes Events. 27 of 28 Events taken as first player lowered results; none taken as second player gained more than 0.12 Resistance.
- PLACE is not printed on the cards as a choice: it is always first.
- Every card has the same four goals; only their order and the Limited preference differ.
- No zero-effect Operations: SUPPLY needs a Train that places a guerrilla, INTEL needs a real accompanying Operation, and Contact must place or move.
- Training when none of a colour is Available takes a guerrilla from another space without Force 136, keeping that space's Cache guard and majority (rule 1.4 exception).
