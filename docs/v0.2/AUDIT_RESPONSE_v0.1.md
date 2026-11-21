# Force 136 v0.2 — response to the v0.1 audit

20 November 2026. Human Japan; paper Force 136 opponent; standard standalone
Japanese Occupation. This is an implementation release, not a fresh claim of
comprehensive rules coverage or measured competitive strength.

The baseline v0.1 package was preserved. Its input ZIP SHA-256 is
eebbc7d481cf1203d5a898f6177c918d04941a07abf633164c9ad56bc2008707.

## Confirmed findings

| Item | Implemented behavior | Direct evidence |
|---|---|---|
| F1, High | A certain British win takes priority on the publicly known last turn. Compare the normal route, Supply, usual Event and productive Contact, plus the other J4 side when relevant; choose the first guaranteed win. Plans with uncertain effects are excluded. | F1.json; test_F1_event_vs_supply_and_actual_selection: normal Supply selects Pahang→Kelantan and supplies Kelantan, Perak, Kedah. Final Resistance 20/Britain; J4 U is 18/MPAJA; J4 S is 17/Japan. Hold/Supply also wins. Resistance 16 is a no-guarantee control; 17–20 select Supply. A keen-card control still needs the safeguard. |
| F2, Medium | J26 requires positive actual track gain, and J4 uses capped gain for A/B. | F2.json; die 1 with cache +1 succeeds against one cube. At Resistance 20 the Event is skipped; normal Ambush displaces the Troop. At 18–19 J26 remains A with sufficient odds; two successful faces do not qualify. |
| F3, Medium | Forecast mandatory activations before committing to Op & SA. | F3.json; all three Sabotages activate the only underground guerrillas, so no Gather remains and Limited is selected. Add one underground guerrilla in Kelantan: Perak can anchor Gather and Op & SA is selected. The forecast does not mutate the starting board. |
| F4, Medium | One actor priority: red underground before blue for Sabotage, Ambush and Gather. Printed color requirements and incoming Raid actors override it. Forced losses retain their separate active-first rule. | F4.json; Ambush activates red and removes Police. The prescribed subsequent J6 attrition die 1 removes the active red, leaving blue underground. Required-blue and incoming-blue controls choose blue correctly. No future J6 information enters the bot's choice. |
| F5, Medium | Check every required field inside its own card cell in both PDFs. Check all 24 railway rank cells separately. Preserve sheet pixel comparisons and dimensions. | 18 cards, 324 field matches across both copies. All six mutations rejected, including deletion of card 09's GATHER > RAID while card 11 still carries it; both PDF copies are damaged identically, so pixel matching alone cannot catch it. |

Implementation locations are build_force136.py (paper rules and Event gates),
policy_rules.py (bounded decision references), regression_checks.py and
verify_printables.py. Exact source-line mappings are in evidence/fix_locations.json.

## Timing correction to the audit

The original F1 explanation wrongly inferred that final Propaganda must follow
merely because six regular Events appeared in the current campaign. Unplayed
Events below an earlier Propaganda carry into the next campaign. That count
alone is insufficient. The corrected F1 fixture states that only one card
remains in the physical Event deck, the third Propaganda has not appeared,
and Japan has finished acting. No inspection of the remaining card is needed.
The original numeric outcome is unchanged. A six-Event/two-cards-left negative
control explicitly prevents the safeguard from triggering too early.

This is a conservative paper safeguard: it covers only the printed candidate
plans whose complete outcomes are public and certain. It does not claim to
find every winning line, evaluate an unknown Intel value or solve every ending.

## Design choices and optional improvements

- Q1 resolved: an Event ages a normal-turn card once and never completes its
  primary, including matching Contact/Supply inside J25. Off-turn free effects
  do not age it. The two-turn discard limit remains.
- Q2 resolved: INTEL holds Contact when existing anchors permit useful Gather,
  even with an Available Force 136 marker. Otherwise normal Contact priorities apply.
- U1 implemented: eight railway rows and three rank columns, with unchanged
  preferences. Every printed rank is checked in its own row and column.
- U2 implemented: each card points to page 1's global checks; its footer names
  the Event-aging exception. Body font and poker-size dimensions are retained.
- U3 implemented conservatively: reconsider a listed D threat after declining
  B only when the normal route would Pass. U3.json has no available cache,
  no eligible Train placement/refresh, no Gather target, no useful Contact or
  attack, and protected donors. J14 B is declined and Event denial is selected.
  A productive Supply control is not replaced. Denial is disabled after Japan acts.
- U4 progressed as a test target: the sheet now records post-Reprisal guards
  and recovery plans. U4.json preserves the prior desk pilot's unguarded-cache
  snapshot and Intel reset seed 136021. A prescribed card-16 Train gives both
  caches two red guards using four of six Available red pieces. This is one
  legal recovery continuation, not proof that the bot will always recover.
  A separate connectivity check chooses a live starred exit over the dead
  Kuala Lumpur spur after the central railway is cut. Physical lookup timing,
  subsequent Japanese responses and complete strategy comparisons remain untested.

## Validation and release verdict

The release passes 52 retained development checks plus 35 focused regressions.
The print checker matches 61 rule sections, 32 Event entries, all 18 cards in
their own cells, all 24 railway ranks and separate/combined sheet pixels.
All six deliberate print mutations fail as intended. Rebuilding from a clean
source copy reproduces all three PDF hashes exactly. Actual rendered pages
were inspected, including the three card columns and the new table/safety page.

The checks exercise selected actions and decisions. They are not 87 complete
games, a general opponent engine, broad adversarial strategy testing, matched
seed balance measurements or a physical timing session. No win rate is stated.
The earlier six-Event desk reconstructions are not relabeled as new full games.

**Verdict: PASS v0.2 for paper playtesting. HOLD a competitive public-release
claim until complete three-campaign games against extraction, hunting, repair
and mixed Japanese plans, plus physical administration measurements, support it.**
