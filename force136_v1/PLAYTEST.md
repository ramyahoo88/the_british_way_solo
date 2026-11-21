# Force 136 v1.1 — playtest guide

The simulations say the bot is competitive against computer Japan policies. Only real games can say whether it is fun, fast and hard to exploit for a person. This page lists what to record so a few games give useful answers.

## Before the first game

- Print the [print-and-play PDF](print/Force_136_v1_Print_and_Play.pdf) at 100%. Print the reference sheet two-sided if you can.
- Read rules sections 3–5 once. Play the worked opening in section 10 on the real board; it checks that you place, Gather, Train and Raid the way the simulation does.
- Play at **Agent** first.

## During each game, note

| What | Why |
|---|---|
| Each Force 136 turn: Directive card, goal used, box | Shows whether some cards or goals never matter |
| Any turn where you had to read a rule twice, or two readings seemed possible | Wording problems; give the section number |
| Time for five normal bot turns once you know the rules, and how many times you opened the full rules | The target is under a minute a turn; the 2.2 goal checks a turn is a simulation count, not a measured time |
| How long INTEL tests and Raid choices take | They are the longest lookups: INTEL previews up to three Operations, Raid compares destinations and sources |
| Turns where the bot played J4 or J25 (step 2), and whether you saw it coming | New in v1.1; about 1 turn in 40. Shows whether the Event step reads naturally and whether Japan plays around it |
| Turns where the bot Passed | Should be very rare (about 1 turn in 1,000) |
| After each Propaganda: where you left your Kempeitai, and what the bot did next | The simulation's Japan was corrected here in v1.0.3; real choices will show whether it is now realistic |
| Moments the bot did something a good British player never would | Candidate rule improvements |
| Anything you did specifically to exploit the bot, and whether it worked | Robustness |
| Final Resistance, Jungle Camps, Force 136 markers, winner | Comparison with the simulation |

## Things the simulation expects

- In a typical game Force 136 takes about 16 turns. About 30% are Limited Trains or Ambushes and about a quarter place a Force 136 marker. The most common full turns are Ambush + Raid, Ambush + Gather, Train + Supply and Contact + Gather.
- The bot is weakest against a Japan player who Assaults Active guerrillas, uses Reprisal to strip guerrillas from Caches, and keeps Kempeitai on Force 136 spaces. If you play that way and win easily at Agent, try Legend or Mastermind. Please report how you beat it: a computer Japan that previews the bot's reply whenever it acts first on a card wins most games at Agent.
- The MPAJA wins about 4–5% of games: Resistance 18–19 with too many Jungle Camps.
- If Japan ever plays the British side of a capability card, Force 136 uses it (rules section 7). These cases never come up in the simulations' normal games, so note any that you see.

## Reporting

A short list per game is enough: level, winner, final Resistance, the rule questions with section numbers, and any exploit you found. Rule questions that come up in more than one game will be fixed first.
