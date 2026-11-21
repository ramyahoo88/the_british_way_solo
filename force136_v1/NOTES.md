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
- 23:30 Clean rules-as-code rewrite lost 15 points. Ablation traced it to Train (taking pieces from elsewhere on the map) and Raid. Both rebuilt with written priorities; same-space "refresh" left out. (Correction after GPT's review: rule 1.4.1 explicitly allows it; leaving it out is a design choice, not a rules question.)
- 23:40 Contact placement away from cubes (+3–4). Gather-2+ first (+1–2). Levels measured (no Raid; starting Resistance; Propaganda bonus; Ambush +1 and an early Zipper were too weak).
- 23:45 Directive deck: nine cards drawn from the strongest orders. South-first tie-breaks rejected (−4.7).
- 23:50 Printability simplifications costed. `force136_v1.py` written; `equiv.py` shows 0 mismatches against the lab in 768 games.
- 23:55 Holdout: Recruit 34.4%, Agent 58.3%, Veteran 66.9%, Legend 72.8%. Search player 56.5%; v0.2 0%.
- 00:00 Lookahead and exploit opponents; corner-adjacency sensitivity (no change); guard rules (no gain); Event retest on the final bot.
- 00:10 Rules, reference sheet, cards, sample game and report written and rendered. First push.
- 00:15 Independent rules review (text only) started. More experiments on the frozen bot:
    - Ambush rolling at a good shot before removing Police: +4.6 / +4.8 on two seed sets. Adopted.
    - Gather-before-Ambush, Mobilize avoiding blue, placement terrain, Redeploy of idle markers, last-campaign Supply, Gather avoiding Troops: no gain.
- 00:30 Review returned 21 findings. One code error (Japanese J27 choice). Twenty text fixes, each matched to the code. Cards 1–8 lose a redundant SUPPLY goal, with identical play (0 mismatches). The reference sheet becomes two-sided.
- 00:45 Final holdout: Recruit 36.7%, Agent 59.0%, Veteran 68.5%, Legend 77.0%. Lookahead-counter Japan: Agent 33%, Legend 53%.
- 00:50 Clean-room reimplementation from the printed rules started by a separate agent, to test whether the text alone determines the moves.
- 01:00 The clean-room bot reproduced the worked example and diverged from mine in 15 of 192 games, always on board details, never on choices. Two code fixes followed: New Village removal is now immediate, and J8 Supply chooses its Provinces before rolling, as the text says. The engine's Japanese J20 choice, which favoured Britain, was also fixed. The text gained the clean-room agent's clarifications.
- 01:05 Full rerun: equivalence, holdout, lookahead, exploits, corner reading, clean-room comparison (768 games), Event tests.
- 01:15 The 768-game clean-room comparison found 8 more divergences. All came from choosing the Special Activity before the Ambush roll rather than after it. The code now resolves the Operation first, as the text reads; section 5 says so. Rerun everything again. Card backs added.
- 01:35 Final results: 0 clean-room divergences in 768 games; lab = printed rules in 768 games. Holdout: Recruit 37.6%, Agent 59.9%, Veteran 67.7%, Legend 77.2%. Search player 56.9%; v0.2 0%.
- 01:50 Event retest on the final bot, then 1,152-game follow-ups for the best candidates (J23, J10, J24): none worth a point of wins. "No Events" stays.
- 02:00 Second holdout (1,536 games per level): 35.9 / 61.8 / 71.9 / 79.5%. The printed level table uses both holdouts pooled.
- 02:10 Flowchart, record sheet. More rule tests against the strongest opponents (Supply away from Troops; Raid keeping 2 guards): no gain.
- 02:15 A wider lookahead Japan (16 candidates × 4 sampled bot replies) beats Agent 87% of the time. It strips Cache guards right after the bot activates them. Defensive rules made the bot weaker everywhere. A fifth level, Mastermind (start 6, +2 per nonfinal Propaganda), was added for players who learn the bot: 89% against the regular policies, 48% against the wide search.
- 02:40 Final rerun for five levels: equivalence and clean-room checks (960 games each, 0 differences), both holdouts, all lookahead opponents.
- 02:45 The wide search against the one-step search player: 21% British wins (8-move version: 29%). Most of its strength is strong Japanese play rather than exploitation of the bot. All-TRAIN and all-AMBUSH Limited decks: within noise; the printed mix stays.
- 02:55 Last checks: guarded-only Supply (worse everywhere), INTEL without Sabotage (−2 to −3). Design frozen.

### 21 November, morning: GPT's review and v1.0.1

- 07:25 GPT's review of commit 615c870 arrived. Every finding reproduced. Its 1,152 fresh Agent games (53.6%) reproduce exactly.
- 07:40 Five 1,000-seed blocks of v1.0 Agent (30,000 games): 59.5%, 58.2–60.5% per block. GPT's windows were unusually low; the holdout's 61% was about 1.5 points high.
- 07:45 New checker `verify_v1.py`: full public state after every turn and reset, final results, a scoring oracle from the rulebook, and forced-capability games. Clean-room bot given British J22 and J27. J27's extra space now follows a written rule (first in map order; never qualifies a goal; not with Raid). All 12 planted errors caught.
- 08:05 Train refresh retested now that it is known to be legal. Refresh first: −0.9. Refresh as the last source: +6.5 and +7.1 on two development sets, +4.8 (3.8–5.8) on 6,000 fresh paired games. Adopted as v1.0.1.
- 08:30 v1.0.1 reruns: equivalence (0 mismatches), checker (2,496 games, 0 failures), 13 mutants caught, fresh levels 41 / 64 / 74 / 82 / 91%, lookahead and exploit opponents.
- 09:35 GPT's re-audit of v1.0.1: passed for tabletop testing. Fixed its two follow-ups: the report's per-policy table (still v1.0 numbers) and checker exit codes. Added its optional Zipper check to the oracle. New `report_check.py` ties every printed win rate to the stored results.
- 10:40 GPT's audit of commit 33745a6: five findings, all reproduced. v1.0.2 fixes them. Redeploy now moves every marker in a stack of exposed markers. The rerun of all 30,000 fresh games is identical, row for row. Also fixed: J27 "with Opposition" on the reference; "never executes an Event" (a Pass may use the Event box); strict stress-policy filters, rerun at 256 games per policy. GPT's saved positions are now fixtures.

### 21 November, midday: full audit of v1.0.2 and v1.0.3

- 11:15 Full audit of commit 338cb0d by Claude (Fable 5.2). Read the rules against the code, the player aids, the map and all 32 Event faces again.
- 11:30 New `fuzz_v1.py`: both bots on 12,000 random positions, 0 differences (it finds v1.0.1's Redeploy error in 57 of 1,500). New `legality_v1.py`: no illegal action.
- 11:40 Two weak Japanese choices in the engine: Active guerrillas removed first, and every Kempeitai pulled off Force 136 markers at Redeploy. On 300 seeds: −1.6 and −3.1 points, −4.1 together. Corrected in the engine.
- 11:45 J25's Japanese side: the return Province is Japan's choice (rule 5.1). Bot rule deleted. British J12 and J15 given printed procedures. Pass note for J6/J9.
- 11:50 Redeploying every marker next to Kempeitai, tested on the corrected Japan: 60.5 vs 60.0%. Not adopted.
- 12:20 v1.0.3 reruns: levels 38.8 / 61.3 / 70.9 / 78.8 / 89.2% (−2 to −3 points on the same seeds), lookahead, stress, references, checker, fuzz and legality.
- 14:00 GPT's audit of v1.0.3 (commit 595f409): no gameplay or scoring defect; four print and verification points. v1.0.4 fixes them: flowchart footer, lookahead footnote, legality check (Supply spaces and rolls, closed Event box, Raids checked step by step from observed positions), fuzzer compares every state field. Page numbers and a fuller sample game added. Bot and results unchanged.

### 21 November, afternoon: the Event question and v1.1

- 14:20 Question from the user: will players think less of a bot that never plays an Event? Probably, so the v1.0 Event test (288 games per Event, before the Train refresh and the Japan corrections) was redone on v1.0.4 with a larger design: `ev_study_v104.py`.
- 14:45 Screen, 1,536 paired games per Event and variant (seeds 410000–410255). As first player every Event lowers the win rate (−1.5 to −26 points where the choice arises), including pure denial. As second player nine Events have positive estimates.
- 15:05 First confirmation block, 6,000 games (seeds 420000–420999), seven Events as second player: J4 +4.3 and J25 +3.0 clear zero; J26 +4.0 and J10 +2.5 do not; J1, J23, J28 flat.
- 15:20 Second block (seeds 430000–430999): J4 +4.1, J25 +2.1, J26 +3.1, J10 −0.4. J4 and J25 adopted; J26 left out (rare, not clear, needs a targeting rule and a roll).
- 15:40 Package on seeds 0–999, all levels: +0.8 / +1.7 / +1.6 / +1.4 / +0.8. Against the lookahead Japan not worse.
- 16:00 v1.1: step 4.2 in the rules, reference, cards and flowchart; both bots, the lab, the checker, the fuzzer and the legality check updated; three new fixtures and two new mutants. The printed bot plays all 30,000 level games exactly as the study's variant did.

## Decisions worth remembering

- Japan's choices are Japan's: which guerrilla Food Shortage removes, where Kempeitai sit after Redeploy, and every choice in an Event Japan executes (J20, J25, J28). The simulation's Japan should make them the way a player would.
- The bot plays only J4 and J25, and only as second player (v1.1). Every Event taken as first player lowered results, and only these two gained as second player in two fresh 6,000-game blocks. (v1.0 had no Events; its smaller test ran before the Train refresh and the Japan corrections.)
- PLACE is not printed on the cards as a choice: it is always first.
- Cards 1–8 carry the same three goals (AMBUSH, INTEL, TRAIN); card 9 adds SUPPLY. Only the order and the Limited preference differ.
- No zero-effect Operations: SUPPLY needs a Train that places a guerrilla, INTEL needs a real accompanying Operation, and Contact must place or move.
- Training when none of a colour is Available takes a guerrilla from another space without Force 136, keeping that space's Cache guard and majority (rule 1.4.1). If no space can give one, it re-places an Active guerrilla in the Train space itself (v1.0.1).
