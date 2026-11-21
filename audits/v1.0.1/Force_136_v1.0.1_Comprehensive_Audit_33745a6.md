# Force 136 v1.0.1
## Comprehensive audit of commit 33745a6

21 November 2026 • Human Japan versus the British bot • Codex review

**Five confirmed findings remain:** one bot implementation error, two printed-instruction problems, and two problems with the exploit-study evidence. None demonstrated a broad failure of the bot's priorities. The earlier scoring-checker, exit-status, J22/J27 coverage and Train-refresh fixes survived the checks below.

| ID | Severity / area | Confirmed result | Smallest correction |
|---|---|---|---|
| F1 | Medium / bot code | Redeploy leaves one of two stacked exposed markers behind | Iterate each original marker, not each occupied space |
| F2 | Medium / quick reference | J27 Supply omits the requirement that the target have Opposition | Restore that eligibility condition |
| F3 | Medium / simulation | Event-hog and Limited-tempo policies do not enforce the advertised strategies | Correct the two filters and rerun their table |
| F4 | Medium / reporting | Exploit table claims 256 games per policy; files contain 64 | Correct the denominator and assert group sizes |
| F5 | Low / instructions | “Never choose Event” conflicts with leftmost-free Pass | Distinguish executing an Event from passing in its box |

Severity reflects player or evidence impact, not frequency. F1 is a legal, targeted boundary case; it did not recur as a mismatch in the fresh natural games checked. F2 and F5 affect the materials a player follows. F3 and F4 affect confidence in the published stress tests, not the headline 30,000-game dataset.

## 1. Version, authority and scope

**Repository:** ramyahoo88/the_british_way_solo, branch `claude-force136`. Exact reviewed commit: `33745a6cad5d89f81b3118806b14eec291bec72a`. Its title is “Force 136 v1.0.1: merge main's review reports; fix GPT re-audit follow-ups”. All source locations below refer to this commit, under `force136_v1/` unless otherwise stated. No production files were modified for this audit.

This is the standard standalone Japanese Occupation 1942–1945 scenario of *The British Way: Enemy of My Enemy*. No Personas, prewar choices, linked campaign or other variants were added. MPAJA victory counts as both players losing. Difficulty changes are the printed bot variants: Recruit disables Raid; Agent is standard; Veteran starts Resistance at 4; Legend starts at 4 and receives +1 after each nonfinal Propaganda; Mastermind starts at 6 and receives +2. The ordinary northern railway interpretation is the baseline; the alternative is only a sensitivity experiment.

**Rule authority:** GMT's current Japanese Occupation rulebook, its setup/map diagram, Operations and Special Activities player aids, Propaganda aid, and all J1–J35 card faces. The living rulebook was downloaded again during this audit and matched the earlier copy: 28 pages, 2026 copyright; SHA-256 `ee65b70ce42cfe170d001c186fa16edcc5c1cb1fccfd7b1e4703184005fec370`. It has no separate numbered revision on the cover. Card/player-aid artwork was inspected in the Vassal 3.1.1 materials. The current publisher page and a targeted search did not reveal a separate Japanese Occupation errata sheet resolving the questions in section 7; that is a search result, not proof none exists.

The game's rules establish legality. The Force 136 v1.0.1 rules establish its narrower choices and tie-breaks. The engine and clean-room bot are evidence to test against those sources, not authorities from which to infer intended behavior. The core engine and bot files are unchanged from `fe57c0f`; this commit mainly corrects documentation and checking infrastructure.

Sources: [pinned repository](https://github.com/ramyahoo88/the_british_way_solo/tree/33745a6cad5d89f81b3118806b14eec291bec72a), [GMT living rulebook](https://gmtwebsiteassets.s3.us-west-2.amazonaws.com/TheBritishWay_EnemyofMyEnemy/EomE_JapOcc_Rules.pdf). The evidence ZIP identifies inputs and contains audit scripts and results, but does not redistribute GMT's rulebook or artwork.

### Materials and layout actually checked

| Material | Direct inspection and comparison |
|---|---|
| Bot Rules, 6 pages | All text, both printed columns, turn flow, goal table, procedure and between-turn rules; checked against the executable choices and relevant official rules |
| Reference, 2 pages | Both columns; all four goal-table columns; level table, map/rail orders, procedures, capability reminders and timing |
| Directive cards, 2 pages | All nine fronts, names, full-turn goal orders and Limited preferences; all nine backs; compared PDF extraction, cards.json and executable DECK |
| Record sheet, 1 page | All printed columns and 22 turn rows; enough rows for the 21-card maximum deck |
| Combined print-and-play | 11 pages; text matches the four components page for page; rendered text bounds remain within pages |
| Simulation report, 8 pages | All tables/columns and prose read. Recounted current headline data, policy tables via report checker, exploit denominators and uncertainty; historical tuning studies were inspected, not all rerun |
| Sample game, 2 pages | All printed entries compared with the regenerated seed 20005 example; expanded trace checks icons, phases and early ending |
| Official material | Read rules and event notes; visually checked original map/setup, railway/Zipper diagram, player-aid columns, all 32 Event faces and three Propaganda cards |

All 145 entries in the repository checksum manifest matched their bytes and the tracked-file set. Correct hashes establish package consistency, not rules correctness. This was screen-based inspection of printable PDFs and execution of the shipped command-line code. I did not cut, shuffle or time physical components. No interactive app is shipped here, so app Undo, browser reload and user-facing save recovery are not applicable. The supplied diagnostic JSON positions were loaded and exercised directly.

## 2. Confirmed findings and reproductions

### F1. Redeploy skips additional exposed markers in one space

**Impact / severity:** Medium. A legal stacked Force 136 position can leave an exposed marker behind despite eligible Camp destinations. This diverges from the printed bot, can expose the marker to elimination, and can distort simulations that reach the position.

**Expected:** Official rules 1.4.2 explicitly permit multiple Force 136 markers in one space; 6.5.1 permits their Redeploy to Camps. Bot section 7 requires moving each exposed marker, in map order, once. This is a bot-procedure error, not an illegal choice under the more permissive human rule.

**Source:** `code/force136_v1.py:347–351`; printed requirement `print/Force_136_v1_Rules.md:136`. The clean-room implementation at `code/cleanroom/cleanroom.py:499–512` already handles multiplicities correctly.

**Smallest useful position:** Seed 3374501, Agent, Resistance 2, Resources 0, Zipper 0, two track Caches. Clear the board, then put 14 Troops, 6 Police and 1 Kempeitai in Kuala Lumpur; 1 Troop, 1 Kempeitai and 2 Force 136 in Perak; 1 Kempeitai and 1 Force 136 in Johore. Put one Camp in each of Kedah, Kelantan and Trengganu. No guerrillas, map Caches, Opposition or other markers. The JSON fixture includes the remaining state and conserved inventories.

**Steps:** Load `evidence/F1_stacked_redeploy.json`; call `propaganda()` as a nonfinal round. Before British Redeploy, the earlier phases do not consume these Camps or move Force 136. Resolve the printed procedure independently: Perak's two markers go to Kedah and Kelantan; Johore's goes to Trengganu.

**Expected positions:** Kedah 1, Kelantan 1, Trengganu 1. **Observed:** Kedah 1, Perak 1, Kelantan 1. The production loop visits Perak only once, subtracting only one marker. The fixture also verifies that the leftover Perak marker remains exposed after Japanese Redeploy. The clean-room bot produces the expected positions. Single-marker and no-legal-destination controls agree between implementations.

**Smallest fix:** Snapshot exposed origins and their marker counts, then attempt one legal move per original marker, recomputing destinations after each move. Preserve the once-per-marker restriction; do not accidentally move arrivals again. Reuse the clean-room loop or its equivalent. Add this stacked fixture beside the single-marker and no-destination controls.

**Evidence:** `focused_checks.py`, checks `F1_stacked_redeploy`, `F1_single_marker_control`, `F1_no_destination_control`. Among 111 fresh baseline games that had stacked markers at a bot turn end, an extra full comparison found zero cross-check or scoring failures. Stacking alone is insufficient: exposure and spare Camp destinations must coincide. No natural-game win-rate effect is established by this audit.

### F2. J27's quick reference selects a Neutral Province

**Impact / severity:** Medium. A player following only the reference can target a lower-population Neutral Province and fail to remove Opposition elsewhere, preserving Opposition and potentially Resistance incorrectly. The full bot rules and code already give the correct result.

**Expected:** J27's shaded effect and official event tip require removing Opposition from one selected Supply space if possible; Britain chooses which. Bot section 6.6 narrows the choice to the selected Province with Opposition having lowest Population, then map order.

**Source:** `print/build.py:137`; Reference PDF page 2, right-hand Supply paragraph; combined print-and-play page 8. Compare correct `print/Force_136_v1_Rules.md:112` and `code/force136_v1.py:192–194`. The reference drops “with Opposition”.

**Position / steps:** Seed 3374502, Agent, shaded J27, Zipper 0, at least two Caches Available. Trengganu has Force 136, Camp and one Underground red guerrilla, but is Neutral (Population 1). Negri Sembilan has the same pieces and Opposition (Population 2). No other Supply candidates. Load `evidence/F2_J27_reference.json` and execute Supply; both Provinces are selected and converted.

**Expected:** Remove Opposition in Negri Sembilan. **Observed:** The code does so. Applying the literal printed lowest-Population target instead selects Neutral Trengganu, where there is no Opposition to remove. This is a verified text/code divergence; it is not a claim that an observed human chose to ignore the official card.

**Smallest fix:** Change the reminder to “remove Opposition from the selected Province **with Opposition** that has lowest Population, then map order.” Rebuild Reference and combined PDFs and regenerate the manifest. The both-opposed control removes Trengganu's Opposition; the neither-opposed control removes none. Both pass.

**Evidence:** `focused_checks.py`, `F2_J27_reference` and its two controls; importable `evidence/F2_J27_reference.json`.

### F3. Two exploit policies do not do what their labels promise

**Impact / severity:** Medium. The published experiment cannot support claims about always taking Events or always taking Limited. These are defects in the test opponents and their description; they are not additional Force 136 play errors.

**Expected:** “Grabs the Event whenever possible” must choose Event when available. “Takes the Limited box” must choose Limited when available. Otherwise, documented fallback behavior may apply.

**Source:** `code/expert.py:15–18`, applied at lines 22 and 34–37; report `print/Force_136_v1_Sim_Report.md:92–101`, PDF page 3.

**Reproduction A:** At seed 170000 with policy `eventhog`, use normal Agent setup, draw J10, resolve the icon and British first turn. Japan has Limited and Event free. `evidence/F3_eventhog_before_japan.json` stores this position. Set the restored game's policy to `eventhog` and call `japan_turn(['Limited','Event'])`.

**Expected:** Event. **Observed:** Limited Sweep, strength 2, Special Activity timing “after”. The filter accepts an Event plan OR any non-Event-box plan, which is every generated candidate. It imposes no Event priority at all.

**Reproduction B:** Seed 170001, policy `tempo`, same opening procedure, J27. Japan again has Limited and Event free. `evidence/F3_tempo_before_japan.json` stores the position. **Expected:** Limited. **Observed:** Event. The filter explicitly accepts Event alongside Limited and chooses whichever scores best.

**Smallest fix:** Set the Event-hog filter to `lambda p: p['op']=='EVENT'` and the tempo filter to `lambda p: p['box']=='Limited'`. The existing `filtered_pool or candidates` fallback handles an unavailable requested box. Alternatively, rename the policies and table to describe the actual mixed behavior. The brute/economy labels should also disclose that their filters permit Events. Rerun the intended strict policies before retaining the “always” labels.

**Evidence / practical consequence:** `focused_checks.py` reproduces both openings. In 256 fresh Event-hog games, the shipped policy took only 1,007 of 3,906 available Events. A diagnostic version took all 3,906. Force 136 wins rose from 180/256 to 255/256, a paired +29.3 percentage points (95% seed-bootstrap interval +23.8 to +34.8); the effect repeated on the second seed block. The shipped tempo policy took 1,823 Events in 256 games. Strict Limited still yielded 256 Force 136 wins out of 256. Thus the corrected stress strategies did not uncover a successful Japanese exploit, even though the original labels were false. These tests concern **Japan's** Event policy, not whether the British bot should take Events.

### F4. Exploit sample sizes are overstated fourfold

**Impact / severity:** Medium for reporting. The table implies four times as much evidence per strategy as the result files contain. Its win percentages are consistent with the smaller actual samples, but precision and robustness are overstated.

**Source / expected:** `print/Force_136_v1_Sim_Report.md:92` says “256 games each”; PDF page 3 repeats it. The denominator must match the per-policy rows in `code/results/results_exploits_v101.json` (line 1). The previous `results_exploits.json` has the same sample structure.

**Exact reproduction:** Load the current JSON and count `pol`. It contains 256 total rows, comprising 64 each for brute, tempo, econ and eventhog, seeds 20000–20063. The stored runner command is equivalent to `POLS=brute,tempo,econ,eventhog python3 holdout_v1.py 20000 64 exploits_v101 agent` from the code directory.

| Policy | Actual Force 136 wins | Actual games | Printed percentage |
|---|---|---|---|
| brute | 60 | 64 | 94% |
| tempo | 63 | 64 | 98% |
| econ | 45 | 64 | 70% |
| eventhog | 45 | 64 | 70% |

**Smallest fix:** Change the caption to “64 games per policy; 256 total”, then regenerate report PDF and manifest. Add a group-size assertion to `report_check.py`. If F3 is corrected first, rerun and print the new counts instead of preserving these mislabeled policy results.

**Evidence:** `focused_checks.py` checks `F4_exploit_sample_size`; `recount_tables.py` independently recounts both primary results and the current exploit table. `evidence/recount_tables.json` records the counts and seed range. No board position is required for this data/report mismatch.

### F5. Passing in the Event box contradicts “never choose Event”

**Impact / severity:** Low. The written directions conflict at a legal boundary, requiring a player to decide which instruction overrides the other. The implemented Pass is legal under the official game.

**Expected:** Official rule 2.4.3 permits selecting a box and passing instead of executing its action. Bot section 4 step 2 forbids choosing the Event box, while step 5 requires passing in the leftmost free box. These cannot both be obeyed if Event is leftmost and every goal fails.

**Source:** `print/Force_136_v1_Rules.md:40,45`; `print/build.py:113,116`, Reference page 1. The executor follows the leftmost rule at `code/force136_v1.py:301`.

**Position / steps:** Seed 3374504, Agent. Put all 15 Troops, 6 Police and 3 Kempeitai in Kuala Lumpur. Put one Force 136 and one Underground red guerrilla in each of Kedah, Perak and Negri Sembilan; no Camps or map Caches. All nine Intel chits are face up; no capabilities. Japan has occupied Limited. Set Directive 1 and offer `['Event','Op & SA']`. The three Force 136 markers are deployed, but PLACE, AMBUSH, INTEL, TRAIN and CONTACT all fail.

**Observed:** `choose()` returns `{'op':'PASS','box':'Event','goal':'PASS'}`. This satisfies step 5 and the official rule, but contradicts step 2. The same issue appears on the reference.

**Smallest fix:** Say “Force 136 never **executes an Event**. It may Pass in the Event box when that is the leftmost free box.” Keep the legal executor behavior. This is wording cleanup, not a reason to change priorities.

**Evidence:** `focused_checks.py`, `F5_pass_instruction_conflict`; `evidence/F5_event_box_pass.json`.

## 3. Normal play and boundary testing

The delivered sample was rerun from setup with seed **20005**, Agent, Japan policy **adaptive**. Its regenerated sample JSON exactly matches the repository example. I additionally recorded every state, die result, icon and intervening phase; `sample_full_trace.json.gz` includes details omitted from the brief handout.

| Draw / card | Scoring | Resistance before | Positive / negative | Resistance after |
|---|---|---|---|---|
| 6 / J33 | Nonfinal | 2 | +10 / −2 | 10 |
| 13 / J34 | Nonfinal | 11 | +9 / −3 | 17 |
| 16 / J9 | Final early ending | 17 | +9 / −3 | 20 |

Positive totals were independently recalculated from revealed Intel, Caches and guerrilla majorities. Negative totals used Resources, Neutral Population and Police presence. For the three rows respectively, positive components were 3+3+4, 1+4+4 and 3+2+4. Negative components were 0+1+1, 1+1+1 and 1+1+1. Final Resistance clamps at 20. J9's MPAJA icon resolves before final scoring; there is no player turn or nonfinal Resources/Support/Redeploy/Reset after that ending. Force 136 wins. The game includes 13 Directive draws and one deck recycle.

**Setup checks** independently asserted piece pools, starts, concealed-Intel distribution and 100 Event-deck deals: 21 unique cards, three seven-card campaigns, each Propaganda among its campaign's last three cards.

The focused suite now contains **22 named checks/observations**, including the five findings and their controls. It exercises exhausted guerrilla supplies, remote donor priority, same-space Train refresh, preservation of Cache guards and majorities, already-Underground controls; Ambush's strict die threshold and automatic Police removal; J8 failure without reselecting Supply targets; shaded J27 with a failed Supply roll; simultaneous Sweep movement and terrain; Construct's strict superiority requirement; Assault Cache protection; Eliminate's Camp ordering, die threshold and J22 exception; J6's single die per Jungle Province and forces-only losses; all Zipper boxes and two Cache returns from the map; Resistance 17/18/19/20 outcomes and ties; nonfinal-only difficulty bonuses after Zipper; early J9 versus its first/second-campaign appearances; J15 Neutral treatment and J12 Terror override; and New Village cleanup distinguishing forces from markers.

The suite intentionally asserts the **observed defects** as reproducible observations. A successful run means the report's observations reproduced; it does not mean those defects satisfy the rules. Once production is fixed, change those specific assertions to the expected outcomes.

### Existing regressions and independent checks

| Check run on this commit | Result and limit |
|---|---|
| `verify_v1.py 32` | 2,496 paired games; 0 full-state cross-check failures and 0 independent Propaganda-oracle failures; includes both sides of every capability and combined sides |
| `verify_v1.py --mutants 16` | All 15 planted errors caught over 1,632 paired cases, including wrong scoring and Zipper mutations |
| `equiv.py` (32 seeds, all five levels) | 960 comparisons, 0 mismatches between tuning implementation and printed-rules implementation |
| `review_fixtures.py` | All 8 earlier review fixtures passed |
| `report_check.py` | Current primary printed numeric fields agree with underlying results; F4 shows denominator coverage must be extended |
| `check_exit_status.py` | Clean run exits 0; injected scoring failure and deliberately uncatchable mutant checks exit 1 |
| Independent railway traversal | All 256 combinations of sabotaged/clear railways agree with a separately transcribed baseline graph |
| Force 136 information/preview checks | 1,152 comparisons across 32 visible positions, all nine Directives and four box sets: concealed Intel and future deck changes do not change the choice; all 1,152 choice previews leave the source state untouched |
| Japan information checks | 352 comparisons: 32 visible positions × 11 policies including wide lookahead; changing secret Intel and future Event/Directive order does not change the chosen plan |
| Event execution sweep | 183 executions across setup and two actual later states; no exceptions or invariant failures. This is an execution/conservation smoke test, not independent certification of every Event target or outcome |

The clean-room bot shares the engine for many Operations and Event effects. Agreement between implementations therefore does not establish engine correctness by itself. The extra hand-derived fixtures and scoring/railway calculations broaden coverage but do not replace a second complete game engine.

The previous review's stale headline/strategy-table figures and nonzero-exit-status defects are corrected here. The J8 slot reminder, British J22 Gather behavior, British J27 extra-space handling and Train last-resort refresh also pass. The core playing code is unchanged from the previous review, so I retained its matched refresh evidence rather than presenting it as a new experiment. I did not rerun every historical development sweep.

## 4. Fresh strategy simulations

**4,736 new game executions** used two declared blocks: 170000–170127 and 180000–180127. The second block confirms diagnostic effects without tuning between blocks. Agent baseline uses ten policies × 256 seeds = 2,560 games; strict Event and strict Limited add 256 each; alternative map adjacency adds 1,536; wide lookahead adds 128, split equally between Agent and Mastermind. These counts exclude the existing regression suite, sample traces and 111 stacked-game comparisons.

Matched variants use the same seeds and Event deals. Dice and Intel are action-keyed, so identical relevant actions share draws while divergent paths are not forced to use a misleading identical sequence. Aggregate and paired intervals resample whole seeds (4,000 bootstrap repetitions, RNG seed 33745), retaining policy correlation. Individual policy intervals below use Wilson 95% intervals. These intervals describe sampling variation within this model, not rules uncertainty or human play.

### Regular Japan policies: fresh Agent results

| Japan policy | Force 136 wins / 256 | Japan wins | MPAJA wins | Force 136 rate / 95% interval |
|---|---|---|---|---|
| extraction | 184 | 65 | 7 | 71.9% / 66.1–77.0% |
| hunting | 181 | 65 | 10 | 70.7% / 64.9–75.9% |
| repair | 192 | 62 | 2 | 75.0% / 69.4–79.9% |
| adaptive | 176 | 70 | 10 | 68.8% / 62.8–74.1% |
| counter | 95 | 154 | 7 | 37.1% / 31.4–43.2% |
| mixed | 127 | 117 | 12 | 49.6% / 43.5–55.7% |

Pooled Force 136 result: **955/1,536 = 62.2%**, seed-cluster 95% interval **58.4–65.8%**. This is consistent with the shipped 64.4% estimate. Policy dependence is much larger than the headline difference: counter Japan remains a strong challenge. Pooling equally across these six artificial opponents is a reporting choice, not an estimated distribution of human opponents.

### Purposeful stress strategies

| Japan strategy | Force 136 wins | Japan / MPAJA wins | Interpretation |
|---|---|---|---|
| Shipped brute | 248/256, 96.9% | 8 / 0 | Direct force pressure as implemented is very weak against Agent |
| Shipped tempo | 256/256, 100% | 0 / 0 | Includes Events; not the claimed strict Limited policy |
| Shipped economy | 173/256, 67.6% | 70 / 13 | Constrained economy menu with Events allowed |
| Shipped eventhog | 180/256, 70.3% | 64 / 12 | Filter admits every generated candidate |
| Strict Event whenever offered | 255/256, 99.6% | 1 / 0 | Corrected intended Event stress test; not a successful exploit |
| Strict Limited whenever available | 256/256, 100% | 0 / 0 | Corrected intended tempo test; no successful exploit observed |
| Wide lookahead, Agent | 8/64, 12.5% | 56 / 0 | Strong counter opponent; Wilson interval 6.5–22.8% |
| Wide lookahead, Mastermind | 35/64, 54.7% | 28 / 1 | Difficulty support matters; interval 42.6–66.3% |

Observed 256/256 wins do not imply universal success; the Wilson interval is about 98.5–100%. The wide tests use seeds 170000–170031 and 180000–180031, 16 candidate plans and four sampled Directive replies. They are compatible with the earlier 15% Agent / 51% Mastermind results given the small sample.

**Matched checks:** For strict Event, the first block changes Force 136 wins from 90 to 128 of 128 (+29.7 points); the fresh confirmation block changes 90 to 127 (+28.9 points). Combined: +29.3 points, interval +23.8 to +34.8. Strict Limited changes no observed win outcomes: 128/128 in both versions in each block; identical outcomes here do not prove identical behavior or equal strength generally. Alternative railway-corner adjacency yields 948/1,536 versus 955/1,536, a paired −0.46 points, interval −1.24 to +0.33. That small sensitivity is not a rules ruling.

**No new repeatable benefit-farming or wasted-turn exploit was established.** The regular games contain 55 no-public-state-change bot turns among 24,786 turns (0.22%), all logged Passes. This does not prove no exploit exists: state coverage is finite and Japan's candidate generator does not enumerate every legal move or every choice of spaces. Wide lookahead samples from all nine Directive cards instead of conditioning on remaining cards and only previews a British reply when Japan acts first. Both restrictions are now accurately disclosed in the shipped report.

### Recount of the published headline data

The stored fresh dataset contains exactly 30,000 unique seed/level/policy rows: 6,000 per level, 1,000 seeds with six policies each. Wins, mean final Resistance and MPAJA columns recompute as follows.

| Level | Force 136 wins / 6,000 | Rate | Mean Resistance | MPAJA wins |
|---|---|---|---|---|
| Recruit | 2,477 | 41.283% | 15.538 | 331 (5.517%) |
| Agent | 3,865 | 64.417% | 17.583 | 246 (4.100%) |
| Veteran | 4,440 | 74.000% | 18.366 | 227 (3.783%) |
| Legend | 4,896 | 81.600% | 18.920 | 191 (3.183%) |
| Mastermind | 5,475 | 91.250% | 19.559 | 139 (2.317%) |

The printed whole-percent difficulty values are consistent with those counts. The primary results are substantially better supported than the mislabeled exploit table. My separate 10,000-resample whole-seed bootstrap gives Recruit 39.42–43.12%, while the report prints 40–43%; the other level intervals approximately reproduce. Since its exact bootstrap RNG/rounding recipe is not recorded, I flag the Recruit lower endpoint as a reproducibility question, not a demonstrated win-count error. Publish unrounded interval values, resampling code and RNG seed.

## 5. Work required at the table

Across the 1,536 regular-policy Agent games, instrumentation counted 54,484 outer goal checks over 24,786 bot turns: **2.20 goal checks per turn**. There were 12,170 Special Activity lists and 20,152 Special Activity checks: **0.81 checks per bot turn**, or 1.66 per consulted list. These are procedure-entry counts, not all board comparisons or rule lookups within them. They exclude internal trial branches and cannot be converted into human minutes.

The recurring physical tasks are a Directive draw and discard; reading its full or Limited order; checking qualifying goals against the visible board; following the corresponding procedure and any Special Activity; moving pieces/markers and updating Resistance/Resources; and resolving Event icons, capability reminders and Propaganda between turns. INTEL can require mentally testing Ambush, Sabotage and Contact plus subsequent Gather reach. Raid requires scanning destination/source pairs, guerrilla colour, Cache guards and majority preservation. These remain the heaviest choices despite short cards.

The expanded sample makes 13 Directive draws and one reshuffle. A player may ordinarily consult the goal row plus one or two procedure paragraphs each turn, but I did not measure real human page changes. The source of unnecessary extra lookup is clearer: F2 forces a J27 rulebook/card check, and F5 forces an exception decision. Those should be removed before adding more tactical rules.

## 6. Optional usability and evidence improvements

These are suggestions, not new confirmed gameplay defects.

- Restore “Underground first” in the reference's Majority Raid reminder (`print/build.py:138`); the full rule at `Force_136_v1_Rules.md:120` already states it. This reduces a routine lookup.
- Expand the example's between-turn entries and label its final scoring as J9 at draw 16. The abbreviated sample omits much of the icon/phase bookkeeping, so it is less useful as a first-game walkthrough than the full trace.
- Separate design commentary from the essential playing rules to shorten the six-page rulebook. Check readability with a physical print before shrinking type. I have not measured physical legibility or play time.
- Correct the results index's “13 planted errors” at `code/results/README.md:10` to 15, matching the actual mutant catalog. This stale label understates current test coverage but does not affect play.
- Generate report captions, denominators and uncertainty from one machine-readable summary. Extend the current report checker to include sample counts and named-policy behavioral contracts, not just percentages.
- Retain the legal Train refresh fallback and current priorities while addressing these small corrections. A new priority/guard rule needs a fresh matched experiment and independent confirmation; none is justified by this audit alone.

## 7. Ambiguous rulings and important coverage gaps

**A1 — Northern railway-corner adjacency.** Official rules 1.3.6–1.3.7 and the original map determine which spaces touch Railway markers. The northern corner interpretation remains unresolved by an official clarification located in this audit. `code/engine.py:121–127` supports the alternative under `corner=True`. Keep the chosen convention explicit. The paired −0.46-point sensitivity result above is evidence about this model's outcomes, not authority for either reading.

**A2 — J10 rounding.** `code/engine.py:465` subtracts half the Resources rounded down, so 7 becomes 4. Rounding the remaining half instead would give 3. The card's phrasing supports the implemented rounded-loss reading, but a definitive published clarification was not located. Retain it as a declared interpretation and use odd-resource fixtures if an official ruling changes it.

**A3 — J13 British Event scope.** The face permits two Limited Ambush/Sabotage Operations using any MPAJA guerrillas, while official rule 2.4.4 ordinarily allows British Limited Operations in multiple Force 136 spaces. `code/engine.py:466–481` performs only two single-space actions in total. Does J13 grant two potentially multi-space Operations, or two single-space exceptions? The event tip says nothing. This audit does not resolve that interpretation. It matters to the older British-Event experiments; the production bot never selects British Events, and the standard Japan policies choose shaded effects, so it does not directly explain the fresh baseline bot results. Obtain a ruling and add an explicit multi-space fixture before treating the old Event study as conclusive.

**Simulation coverage:** Operations, Event targeting and Japanese decisions are not backed by a complete independent engine. Boundary tests and hidden-information perturbations reduce risk but cannot certify every legal action. Mandatory events, capacity shortages, major timing boundaries and all capability sides received direct coverage; every combination of simultaneous capabilities and arbitrary board state did not.

**Design evidence:** The British Event-versus-operation study was performed on v1.0 and has not been repeated for v1.0.1. This audit's strict Japanese Event experiment answers a different question. Historical parameter searches and all five levels' broad win rates were not freshly simulated again here; all levels' stored counts were recounted, while new simulations concentrated on Agent and the strongest Japan/Mastermind comparison.

**Player experience:** No physical blind playtest or timed rules-learning test was conducted. No human strategy distribution or optimal opponent has been established. The 62.2% pooled Agent result is not a predicted human win rate. The low rate against wide search warrants retaining a strong-player difficulty recommendation, not a claim that the bot has been solved.

## 8. Fix order, acceptance checks and release verdict

1. **Fix F1 and F2 first.** Add stacked-marker, single-marker and no-destination Redeploy tests; restore J27 eligibility and regenerate affected PDFs. The rules, code and reference must agree on the supplied positions.
2. **Fix F3 and F4 together.** Make the policy names executable contracts, rerun the exploit table with declared per-policy counts, and include denominator checks in report generation.
3. **Clarify F5**, then regenerate all affected files and the checksum manifest. Keep the official legal Pass behavior.
4. Rerun focused cases, existing equivalence/scoring/capability suites, mutant detection, exit-status checks and print-package consistency. If a bot fix changes natural simulation outcomes, rerun affected result tables rather than retaining stale figures.
5. Before making a stronger validation claim, resolve or explicitly document A1–A3, repeat the British Event study on the current bot, and conduct a blind physical playtest using only the delivered materials.

**Release verdict: suitable for structured playtesting, but hold a fully validated release until F1–F5 are corrected.** The evidence is substantial: 2,496 clean paired verification games, 15/15 detected mutants, 960 equivalence comparisons, 22 targeted checks/observations, fresh hidden-information checks for both sides, and 4,736 new strategy games. It supports the overall v1.0.1 design and the recent fixes. It does not erase the reproduced stacked Redeploy discrepancy, printed J27/Pass problems, mislabeled exploit policies or overstated sample size, nor the shared-engine and physical-playtest gaps.
