# Force 136 v1.0.4 — independent re-audit

21 November 2026 · Human Japan versus the British Force 136 bot · Review of `5efd44f`

**Verdict: pass for release. All four findings from the v1.0.3 audit are resolved. No new material defect was confirmed.** The revised verification tools reject the previously missed illegal cases, the shipped PDFs contain the corrections, and the expanded example regenerates exactly. The bot's rules and game engine are unchanged.

This is a regression audit of Claude's response, supported by fresh random positions and a repeat of the published legality sample. It builds on the comprehensive review of `595f409`; it does not present that earlier work as newly performed. No production files were changed during this review.

## 1. Version, authority and scope

Reviewed repository: [ramyahoo88/the_british_way_solo](https://github.com/ramyahoo88/the_british_way_solo), branch `claude-force136`, full commit **5efd44f34a64625f4b627c832d038a2d85566780**. Baseline: **595f409ccae43f795f7fbdc38878f07f7967682a**. The version under review is the nine-card Force 136 v1.0.4 paper bot, standard standalone Japanese Occupation, with no Personas, Pre-War Options or campaign links.

The rules authority remains GMT's [Japanese Occupation rulebook](https://gmtwebsiteassets.s3.us-west-2.amazonaws.com/TheBritishWay_EnemyofMyEnemy/EomE_JapOcc_Rules.pdf), 2026 printing, 28 pages, with no separate revision identifier. Its SHA-256 is recorded in `SOURCE_PIN.json`. The previous comprehensive review checked both columns of the Japanese and British Operations/Special Activities aids, the Propaganda aid, setup, and all 32 Event faces in Vassal module 3.1.1 against that rulebook. Those sources and interpretations are unchanged. No separate official errata or clarification was located in that same-day source review; this follow-up makes no claim of a later publisher ruling.

For the changed areas, expected behavior was taken from GMT rules 2.4.3, 4.2.1, 4.2.3 and 5.4, the Japanese sides of J8/J27, and bot rules 4.5, 6.6 and 6.7. The legal/illegal fixtures below were specified independently of the revised checker. I inspected the delivered flowchart at full-page resolution, both reference pages and all their columns, the nine Directive fronts and backs, all six rules pages, the three-page sample and eight-page simulation report. Text bounds and the combined PDF were checked programmatically as well.

Seven core files match the baseline byte for byte: `engine.py`, `expert.py`, `force136_v1.py`, `force136.py`, both clean-room Python files, and `cards.json`. Their hashes are in `evidence/release_checks.json`. The only change to opponent execution is removal of a swallowed exception in `lookahead.py`; ordinary successful choices remain the same, as the paired test below confirms.

## 2. Closure of the four findings

All file/line references in this section refer to commit `5efd44f`; paths beginning `code/` or `print/` are relative to `force136_v1/`. These are resolved findings, not four remaining defects.

### P1 — flowchart contradiction: resolved

**Player impact and expectation.** The old footer could lead a player to reject a legal Event-box Pass. Passing does not execute an Event (GMT 2.4.3). Bot rule 4.5 uses the leftmost free box; GMT 5.4 closes the Event box on J6 and J9.

**Exact reproduction.** Load `code/fixtures/audit_33745a6/F5_event_box_pass.json`, seed 3374504, Agent. It has Force 136 and an Underground red guerrilla in Kedah, Perak and Negri Sembilan, no qualifying productive goal, and revealed Intel. Set current Event to J1, use Directive 1, and offer Event plus Op & SA. The expected and observed choice is **PASS / Event**. Repeat with J6 or J9: an intentionally invalid offer is rejected by the checker; the correctly filtered offer produces **PASS / Op & SA** with no violation.

**Printed result and smallest fix.** `print/turn_flow.svg:41` now says “Never execute the Event.” That exact correction appears on page 2 of both the rules PDF and the combined print-and-play, beside the correct Pass prose. The old sentence is absent. The minimal text replacement has been applied; no further fix is needed. Evidence: `regression_checks.py`, `release_checks.py`, and their JSON receipts.

### V1 — legality-checker blind spots: resolved

**Impact and expectation.** These were weaknesses in the claimed verification, not demonstrated illegal play by the shipped bot. The checker must reject a conversion after a failed Japanese-J8 Supply roll, omission of Japanese-J27 Opposition removal, and any Event-box use on J6/J9.

**Smallest Supply setup.** Start Agent seed 5954001, replace the board with an empty board, put all 15 Troops, six Police and three Kempeitai in Kuala Lumpur, and put one Force 136 marker, one Underground red guerrilla and a Jungle Camp in Perak. Keep the constructor's off-map fields, and turn on Japanese J8. The executable fixture preserves piece invariants and fixes the real Supply die to 1 while retaining the checker's roll observer.

- With the real bot, the Camp remains and no Cache appears. With a test mutation that converts that Camp after the failed roll, the checker now reports **“J8: Perak rolled 1 but was converted.”** Legal controls for dice 1, 2, 3 and 6 pass; conversion starts at 3.
- For seed 5954002, put Perak at Opposition and enable Japanese J27. A test mutation restores Opposition after Supply. The checker now rejects it. The real bot removes Opposition, including when J8 is also in play and its die is 1, so no Cache conversion succeeds. Removing Opposition depends on selection, not success. Opposition in unselected Kedah is correctly left alone.
- The Event-box setup above is rejected on **both J6 and J9**, while its ordinary-card control is accepted.

**Source and smallest fix.** `code/legality_v1.py:204` checks Supply using observed rolls/selected spaces; line 233 requires the J27 loss when possible; line 371 records Supply dice; line 396 removes the Pass exception on Mandatory cards. `code/fuzz_v1.py:119` filters ordinary offers. These implement the requested minimal fixes. All nine shipped planted-error tests pass, and the independent combined-capability and neighboring-case probes pass. No further production change is indicated.

### V2 — incomplete random-position comparison: resolved within its stated scope

**Impact and expectation.** Previously, two bots could disagree on capabilities or off-map pieces and still compare equal. The test should compare every field populated by its random-position harness, plus the terminal flags, and report those differences.

**Reproduction and result.** At seed 5954003, create two identical positions, then change only J22's side in one. The new comparator detects the difference. `regression_checks.py` repeats this isolated mutation for **all 20 declared fields**, including lost Kempeitai, away Troops, capability state, eligibility, campaign/draw fields and winner/end flags. Every mutation is detected and described; identical controls agree.

**Source and smallest fix.** `code/fuzz_v1.py:106` defines the comparison list; lines 108 and 115 use that same list for equality and diagnostics. The prior omitted fields have been added. Two independent fresh blocks, seeds **360000–371999** and **380000–391999**, yield **24,000 positions and 264,000 action comparisons, with zero differences or exceptions**.

“Every field” here means those 20 declared game-state fields. It is not equality of the entire Python object, private future deck/RNG state, or diagnostic counters. Random positions satisfy piece-count invariants; reachability through normal play is not proved. Those limits do not reopen the original finding.

### D1 — lookahead description: resolved

**Player impact and expectation.** The old description overstated how often the Japanese policy considers a British reply. `code/lookahead.py:13` uses its base heuristic when Britain has already acted. Reply previews occur when Japan acts first on a card.

**Reproduction and result.** `print/Force_136_v1_Rules.md:163`, the delivered rules PDF, README, playtest guide and simulation report now describe that condition correctly. An independent test replaces the British preview with a deliberate exception: Japan-first execution raises it, while Japan-second execution completes without invoking another British turn. The policy is restored after failure and the real board/state remains unchanged.

**Smallest fix.** The wording replacement has been applied. Removing the broad exception handler at `code/lookahead.py:41` also implements the optional fail-loud recommendation. No further fix is needed.

## 3. What was run directly

The table counts distinct kinds of work separately. A nested Ambush may be checked inside a Raid, and a turn contains several effects; these numbers must not be added as though they were unique games.

| Check | Scope | Observed result |
|---|---|---|
| Full-game differential/scoring check | 624 paired cases; normal games and every capability side | 0 state/result mismatches; 0 independent scoring-oracle failures |
| Scoring/bot mutation suite | All 15 deliberately wrong implementations | All caught |
| Failure exit status | Clean run, injected scoring error, deliberately missed mutant | Exit codes 0 / 1 / 1 |
| Shipped review fixtures | 16 fixed tests | All pass |
| Independent regressions | 25 groups, including 20 individual field mutations | All pass |
| Earlier rule boundaries | 18 groups, rerun against v1.0.4 | All pass |
| Fresh differential fuzz | 24,000 positions; 264,000 actions | 0 differences or exceptions |
| Published legality games | 960 games, all five levels and six Japan policies | 0 violations; 2,240 Raids confirmed |
| Published legality fuzz | 12,000 positions; 72,000 bot turns | 0 violations; 9,967 Raids confirmed |
| Legality negative controls | Nine shipped planted errors, plus independent probes | All expected rejections occur |
| Wide lookahead comparison | 256 old/new matched pairs; 512 executions | Complete results identical; 0 exceptions |
| Sample/hidden-information checks | Full sample, 1,152 hidden-information comparisons and 1,152 preview-purity checks | All pass |
| Map/Event smoke checks | 256 railway masks; 183 Event executions | All pass within the limited scope below |
| Delivered print package | Nine fronts/backs, 11 combined pages, all 224 manifest entries | Content and hashes match; no text outside page bounds |

The 960-game legality run uses seeds **800000–800031**, each at all five levels against extraction, hunting, repair, adaptive, counter and mixed. The 12,000-position legality run uses seeds **900000–911999**. Both result JSON files match Claude's stored v1.0.4 results exactly, including every counter. Together they contain **12,207 confirmed Raids and zero undecided Raids**. The effect counters total **193,877** when Operations, Special Activities, icons and Resources steps are counted; aggregate TURN counters are excluded from that total.

The Raid change records intermediate positions in `code/legality_v1.py:373` and checks each destination in `check_raid` at line 289. Independent small witnesses accept two destinations at Zipper 18 and three at Zipper 20. They reject a third destination at 18, a repeated destination, an extra Resistance point, a source without a Cache and a nonadjacent destination. This tests both rejection and the neighboring legal case. The earlier audit's independent 537-Raid witness proof also remains applicable to the unchanged production bot; it is not counted again as newly executed here.

The 18 boundary groups cover standard setup and 100 deck deals, exhausted Train supplies and same-space refresh, Ambush thresholds and Cache bonuses, failed J8 Supply with J27 removal, simultaneous Sweep conservation, Construct/Assault/Eliminate boundaries, the shared J6 roll, all Zipper thresholds, final-scoring ties and bonus timing, J9's immediate ending, New Village cleanup, revised Japanese removal/Redeploy choices, J25 return, and British J12/J15 behavior.

## 4. Shipped materials and representative play

The print-and-play remains **11 pages**: six rules pages, two reference pages, two card pages and one record sheet. Rules pages now display page numbers 1–6. The printing note at `print/Force_136_v1_Rules.md:15` specifies actual size, cutting and the optional backs. The separate sample is three pages; the simulation report is eight. The combined PDF's page text exactly matches its component PDFs. All nine front priorities and Limited preferences match `cards.json` and the executable deck; all nine back texts match one another.

For sample seed **20005**, Agent versus adaptive Japan, I regenerated `sample_game.py` output and then `sample_md.py` output. The JSON matches the shipped JSON, and the Markdown is byte-identical to the shipped Markdown. The PDF contains the added icon names, Japanese Operation/Special Activity labels, J22 capability entry, Resource changes and post-Reset positions. The new recording code is at `code/sample_game.py:37`, line 45 and line 55.

The independent trace records actual dice, icons, Japanese choices, British choices and every scoring board. Recomputing all six scoring terms gives:

| Draw | Phase | Positive / negative terms | Resistance |
|---|---|---|---|
| 6 | First nonfinal Propaganda | +10 / −2 | 2 → 10 |
| 13 | Second nonfinal Propaganda | +9 / −3 | 11 → 17 |
| 16 | J9 final Propaganda | +9 / −3 | 18 → 20, capped |

On draw 16, the J9 icon resolves before the Mandatory Event sends the game to final Propaganda; neither player takes a normal turn. Force 136 wins at Resistance 20. `evidence/sample_full_trace.json.gz` preserves the full trace and dice.

The hidden-information test changes concealed Intel, future deck order and seed while preserving visible position and the current Directive: choices remain unchanged in all 1,152 comparisons. The same 1,152 decision previews leave their real input state unchanged. The Event sweep checks execution and conservation on three positions; it does **not** independently certify every Event's target choice. The railway test independently recomputes all 256 blocked-marker masks; it does not settle disputed corner adjacency.

No physical tabletop session or printer test was performed. No web app is shipped in this branch, so browser controls, Save, Undo and reload are not applicable. I inspected the shipped PDFs rather than claiming a byte-identical browser PDF rebuild. The existing measure of roughly 2.2 goal checks and 0.8 Special Activity tests per bot turn remains relevant to the unchanged procedures; it is a simulation count, not a measured human turn time.

## 5. Strength claims and purposeful opposition

Keeping the headline **39 / 61 / 71 / 79 / 89%** is justified as a carry-forward of the existing simulated results, not a new balance measurement. The seven unchanged core files establish why normal-policy outcomes carry forward, and `report_check.py` confirms the printed tables against the stored v1.0.3 data. The full 30,000-game headline study was not redundantly rerun in this follow-up.

The changed exception handling was checked separately on the strongest existing Japanese policy: `lookc`, 16 candidate plans and four sampled Directive cards, seeds **20000–20127**, Agent and Mastermind. Both commits were run in separate interpreters, and all fields of every returned game result matched.

| Level | Force 136 wins, either version | Mean final Resistance |
|---|---|---|
| Agent | 19 / 128 = 14.84% | 10.828 |
| Mastermind | 69 / 128 = 53.91% | 16.547 |

No preview exception occurred. These reproduce Claude's reported wide-search outcomes. This is a matched regression on the published holdout, **not a fresh strength sample**. The prior comprehensive audit supplied the fresh strategic evidence: 6,272 executions across six normal policies and wide lookahead. It found Agent at 62.9% in 1,536 normal-policy games, and 7/64 at Agent versus 33/64 at Mastermind against wide lookahead. Those results still concern the unchanged bot and engine.

The updated report now accurately states that the Japanese correction cost about 1.0 percentage point in the prior independent fresh sample, versus 3.2 in Claude's stored sample. The current level rates fit both; the exact size of the correction should not be treated as settled. The strong Japanese policy remains a repeatable challenge to Agent. No new waste-turn exploit, illegal information use or demonstrated behavior improvement was found in this follow-up, and no speculative priority change is recommended from these regression results.

## 6. Remaining questions, optional work and verdict

**Unresolved interpretations, carried forward:** northern railway corner adjacency; J10 rounding; the scope of J13's British Limited Operations; and J2/J23 Sabotage stacking. This review found no new ruling and does not relabel those questions as defects. The bot never voluntarily executes Events, which limits their direct exposure, but a player can still execute a British Event side.

**Coverage limits:** the two bots share an engine, so agreement is not independent proof of every Japanese Operation or Event. The legality checker is finite testing, not a proof for all possible positions. Random positions are not certified reachable. The Japanese policies are fixed heuristics with a finite plan menu, not optimal human play. The Event-policy experiment was run on the older bot/Japan model and has not been repeated. Physical handling and turn time remain untested.

**Optional next work:** run tabletop sessions that record lookup counts, ambiguous decisions and turn time; retain the independent negative controls with future checker changes; repeat the Event study on the current model before making a new claim that taking Events cannot help. These are follow-up research and usability tasks, not release blockers or confirmed improvements to bot strength. The previously requested page numbers, printing note, fuller sample and fail-loud previews are implemented and verified.

## Reproduction files

The accompanying evidence ZIP contains the pinned source identifiers, scripts, inputs, logs, full sample trace and checksums. It does not include publisher artwork or the publisher's rulebook. Use the repository at the pinned commit; commands and optional PDF-library requirements are in its `README.md`. Primary scripts are `regression_checks.py`, `run_suite.py`, `boundary_checks.py`, `extended_checks.py`, `lookahead_compare.py`, `check_package.py` and `release_checks.py`.


**Fix priority: none required by this review. Release verdict: pass v1.0.4 as a simulation-tested paper fan bot.** All four previous findings are closed, the legality totals reproduce exactly with no undecided Raids, 24,000 fresh positions show no bot disagreement, the strongest opponent's paired results are unchanged, and the delivered PDFs agree with the corrected instructions. Keep the current distinction between simulated win rates and tabletop performance.
