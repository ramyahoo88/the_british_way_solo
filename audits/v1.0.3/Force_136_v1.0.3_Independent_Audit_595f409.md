# Force 136 v1.0.3 — independent audit

21 November 2026 · Human Japan / British Force 136 · Codex review

Reviewed commit **595f409ccae43f795f7fbdc38878f07f7967682a** on `claude-force136`, in `ramyahoo88/the_british_way_solo`. Comparison version: v1.0.2, **338cb0d7bc87ce3c690a88c212aa6878bea8952d**. No production code, bot rules or shipped PDFs were changed by this audit.

The bot's play survived this review. I confirmed the new Japan procedures and independently resolved all 537 Raids in the published 240-game sample, including the cases left unconfirmed by the earlier search. I found one remaining printed contradiction, two weaknesses in the verification tools, and a minor description error. None demonstrates an illegal action by the shipped bot during normal play.

## 1. Rules, version and review scope

The authority is GMT's **Japanese Occupation 1942–1945** rulebook, copyright 2026, as linked under Living Rules on the [publisher's product page](https://www.gmtgames.com/p-1107-the-british-way-enemy-of-my-enemy.aspx). The [28-page rulebook](https://gmtwebsiteassets.s3.us-west-2.amazonaws.com/TheBritishWay_EnemyofMyEnemy/EomE_JapOcc_Rules.pdf) has no separate revision number on the copy reviewed. Its SHA-256 is recorded in `SOURCE_PIN.json`. I checked the current publisher listing and did not locate a separately listed Japanese Occupation errata document. That is a search result, not a claim that no unpublished clarification exists.

I reread the rules and the delivered bot booklet, both columns of the Japanese and British Operations / Special Activities aids, the Propaganda aid, and both sides of all 32 Event cards as reproduced in the British Way Vassal module 3.1.1. Original page layout was inspected for timing and priority; the bot's flowchart was also checked in the actual PDF. The setup and scoring expectations in the independent fixtures were transcribed from the publisher's rules, not obtained by asking the implementation what it should do.

Scope is the standard standalone scenario: no Personas, prewar choices, linked Malaya game, or campaign bonuses. The five bot levels are agreed fan-variant changes. This is a paper bot with a research simulator, not a shipped interactive app. Browser controls, Undo, reload and save recovery therefore do not apply. The supplied JSON fixtures are runnable simulator positions, not app-import saves.

The prior comprehensive audit at `33745a6` remains the baseline. This review rechecks its defects, the subsequent changes, the printed package, targeted rule boundaries and the new verification claims. It does not claim a second independent implementation of every Japanese Operation and Event.

## 2. Previous findings and Claude's changes

| Item | Result of this review |
|---|---|
| Stacked exposed markers at Redeploy | Fixed. Every marker in the original stack can move once. The one-marker and no-destination controls pass. |
| J27 reference omitted “with Opposition” | Fixed in the source and the delivered reference PDF. Neutral low-population spaces no longer appear to outrank eligible opposed spaces. |
| Event-hog and Limited-only stress filters | Fixed. The filters now enforce their stated contracts; the existing decision fixtures pass. |
| Stress-table sample size | Fixed. The current stored table contains 256 games per policy, 1,024 total, and the report recount passes. |
| Event-box Pass contradiction | **Partly fixed.** Rules prose, cards and reference agree; the embedded flowchart still contains the old prohibition. Finding P1 below. |
| Japan removes Active before Underground guerrillas | Changed as described. Japan now prefers Underground losses; British forced losses and Active-only Assault retain their separate behavior. |
| Kempeitai automatically leave Force 136 at Redeploy | Changed as described. One Kempeitai may stay with the marker; extra pieces move only to eligible destinations. Retaining a piece is permitted by rule 6.5.2. |
| J25 marker return | Corrected. Rule 5.1 assigns the Event's choices to its executor; Japan chooses the return Province. No Camp returns the marker to Available; final scoring performs no Reset return. |
| British J12 / J15 procedures | Present in the booklet, reference and both implementations. Priority, Terror, colour and empty-pool controls pass. |
| J6 / J9 closed Event box | Printed turn procedure and normal game loop are correct. The new legality check still contains a Pass exception; see V1. |
| Move reminder adds a Camp | Present on the delivered reference sheet. |

The independent boundary tests also cover exhausted Train pools, remote donors versus local refresh, strict Ambush and Eliminate thresholds, J8 failure without replacement selection, J27 removal after a failed Supply conversion, simultaneous Sweep conservation, Cache protection, all Zipper thresholds, final-scoring ties, bonus timing and J9's early ending. All **18 boundary groups** pass. The repository's **15 review fixtures** also pass.

## 3. Confirmed findings

### P1 — Low: the printed flowchart still forbids an Event-box Pass

**Player impact.** A player following the diagram gets a different box instruction from the prose immediately above it. This creates an unnecessary rules lookup and can cause the wrong cylinder placement. In the reproduced second-player Pass, either remaining box would leave Britain second eligible, so this case does not change the winner or demonstrate a scoring defect.

**Expected behavior / authority.** Bot rule 4.5 and GMT rule 2.4.3 permit a Pass in the leftmost free box, including Event. Mandatory J6 / J9 are the explicit exception under rule 5.4. The diagram should distinguish executing an Event from passing in its box.

**Small setup and reproduction.** Load the repository fixture `force136_v1/code/fixtures/audit_33745a6/F5_event_box_pass.json`, seed **3374504**, Agent. It has three Force 136 markers in Kedah, Perak and Negri Sembilan, one Underground red guerrilla in each, no Camp or Cache there, and all Intel revealed. Set current Event to J1, Directive to 1, and available boxes to Event / Op & SA; Japan occupies Limited. Run `choose(['Event','Op & SA'])`. Then inspect page 2 of either the Rules PDF or combined Print-and-Play PDF.

**Expected / observed.** The bot returns `PASS / Event`, as the prose requires. The diagram footer says **“Never the Event box.”** That exact stale sentence is embedded in both delivered PDFs, beside correct prose allowing the Pass. `paper_probes.py` confirms both the decision and the printed contradiction.

**Source.** `force136_v1/print/turn_flow.svg:41`; the SVG is embedded by `print/build.py:101`. Delivered locations: Rules PDF p.2 and Print-and-Play PDF p.2. The corrected prose is `print/Force_136_v1_Rules.md:45`.

**Smallest fix.** Replace the footer's first sentence with **“Never execute the Event.”** Rebuild the Rules and combined Print-and-Play PDFs, update the manifest, and add an assertion against the obsolete diagram text. No card reprint or bot behavior change is needed.

### V1 — Medium, verification only: the legality checker accepts illegal Supply results and a closed-box Pass

**Player impact.** The current bot passes the corresponding legal controls. The risk is false confidence: these tests would allow a future illegal change to pass the new independent-legality gate. The published zero-violation result should not be read as comprehensive coverage of capability-modified Supply or Mandatory Event box selection.

**Expected behavior / authority.** Japanese J8 prevents conversion on rolls 1–2. Japanese J27 requires removing Opposition from one selected Supply space if possible. GMT rule 5.4 closes the Event box on J6 / J9, including for Pass. Bot rules 6.6 and 4.5 state these requirements correctly.

**Exact reproductions.** Run `python checker_probes.py /path/to/repository`. Its Supply fixture starts with an otherwise empty map, 15 Troops / 6 Police / 3 Kempeitai in Kuala Lumpur, and one Force 136 marker, one Camp and one Underground red guerrilla in Perak. Resistance is 2, Zipper Delay, and three Caches are Available.

- **Seed 5954001, J8 Japanese side, die 1:** the test deliberately converts Perak's Camp after the failed roll. Expected checker result: reject. Observed: one Cache, no Camp, **zero violations**. Nearby control: unmodified bot leaves the Camp and places no Cache.
- **Seed 5954002, J27 Japanese side, Perak at Opposition:** the test performs Supply and deliberately restores Opposition afterward. Expected checker result: reject the skipped removal. Observed: Cache plus retained Opposition, **zero violations**. Nearby control: unmodified bot removes Opposition.
- **Seed 3374504, the P1 Pass fixture, current J6 or J9:** give the checker the Event / Op & SA box set used by the fuzzer. Expected: reject `PASS / Event`. Observed: both are accepted with **zero violations**. Nearby control: the normal game loop excludes Event, and the bot passes in Op & SA. This probe intentionally challenges the checker with an invalid box offer; it is not a reachable normal game-loop offer.

**Source.** `code/legality_v1.py:204` (`check_supply`) checks successful conversions but has no selected-space or Supply-die record. At line 216 it validates Opposition loss only if a loss occurred, so omission passes. Its die observer at line 342 records Ambush only. Line **365** explicitly exempts Pass from the Mandatory Event check. `code/fuzz_v1.py:34` supplies Event-containing box sets independently of the current Event; normal `code/engine.py:1150` filters correctly.

**Smallest fix.** Record the selected Supply spaces and actual Supply rolls; verify the selected-space limit, eligibility, J8 outcomes and mandatory J27 loss against that record. Do not infer selection solely from converted Camps, because failed J8 rolls are still selected spaces. Remove the `or p['op']=='PASS'` exception from line 365 and filter ordinary fuzz offers on J6 / J9; retain an explicit invalid-offer negative test. Add all three reproductions to the legality self-test. No production bot change is justified by these probes.

### V2 — Low, verification only: “full public state” is not what the fuzzer compares

**Player impact.** A divergence in a capability or off-board pool can alter later play while this fuzzer reports agreement. The broader policy-game verifier does compare more state, so this is a gap in the new fuzz claim, not evidence that all verification is ineffective.

**Expected behavior.** `fuzz_v1.py:13` promises that the full public state matches after every action. The comparison should include all state fields the harness copies into each bot and their terminal status.

**Exact reproduction.** Create two identical Force 136 games with seed **5954003**. Add only `b.cap[22]='S'` to the second. Both still satisfy the piece-count invariants. Call `fuzz_v1.public(a)==fuzz_v1.public(b)`. Expected: false. Observed: **true**. A nearby control changing Resources is correctly detected.

**Source.** `force136_v1/code/fuzz_v1.py:100` omits `cap`, `lost_k`, `away_troops`, `campaign`, `draw`, `event`, `first` and `regular_seen` from its public comparison, despite these being in `STATE` at line 31. Terminal flags are also absent. Its diagnostic function at line 105 covers an even smaller subset.

**Smallest fix.** Canonically compare the declared `STATE` fields plus terminal flags, using the same field set for diagnostics. Add the capability-only negative control. The audit's `fuzz_complete_state.py` demonstrates this overlay without changing the repository.

**Follow-up evidence.** With those fields added, **12,000 fresh positions, seeds 240000–251999, and 132,000 actions produced zero differences or exceptions**. Thus widening this check did not uncover a current bot divergence.

### D1 — Low: one printed sentence overstates the lookahead opponent

**Player impact.** Readers may believe the reported opponent previews a British reply on every Japanese turn. The simulation report describes the restriction correctly, but the rulebook still overstates it.

**Reproduction / expected / observed.** Read the level-table footnote on Rules PDF p.4 / `print/Force_136_v1_Rules.md:161`: it says the computer previews the bot's reply **“before every move.”** Inspect `code/lookahead.py:13`: when Britain has already acted, it immediately falls back to the one-step policy. Expected description: previews replies **when Japan acts first on a card**. This is a wording reproduction; no seed is needed.

**Smallest fix.** Replace “before every move” with “when Japan acts first on a card,” then regenerate the rulebook and combined PDF. Keep the accurately qualified simulation-report description.

## 4. What was tested directly

| Check | Direct result |
|---|---|
| Primary / second implementation, scoring oracle and forced capabilities | 2,496 comparison cases; 0 cross-check failures, 0 scoring-oracle failures |
| Deliberate corruption of bot / scoring / Zipper behavior | All 15 existing mutants caught; nonzero failure exits verified |
| Tuning module versus printed-rules module | 960 games, all five levels; 0 differences |
| Original differential fuzzer | 12,000 positions, seeds 700000–711999; 132,000 actions, 0 differences |
| Expanded-state differential fuzzer | Another 12,000 positions, seeds 240000–251999; 132,000 actions, 0 differences |
| Existing legality checks on random positions | 2,000 positions / 12,000 turns; 0 reported violations; six existing illegal-action mutants caught |
| Original game legality replay | 240 games, 0 reported violations; 11 Raids unconfirmed in this replay (7 in the stored author run) |
| Policy games with explicit Raid witnesses | Same 240 games / 3,810 turns; every other action check retained; 537 Raids / 965 individual moves independently validated |
| Fresh version comparison | 3,072 matched games per version, plus 128 current-version wide-search games; 6,272 executions total |
| Hidden-information / preview checks | 1,152 British comparisons and 1,152 pure-preview checks; 352 Japanese comparisons across 11 policies; 0 differences or preview mutations |
| Railway connectivity | All 256 Sabotage masks agree with a separately transcribed graph traversal |
| Event execution smoke test | 183 executions across setup and actual later positions; 0 invariant errors. This is not a proof of every Event's targeting choices. |
| Rules boundaries and past reproductions | 18 independent boundary groups and all 15 repository fixtures pass |
| Delivered print package | 9 fronts, 9 identical back texts, 11-page combined package, both reference columns, all 210 manifest entries checked |

**Closing the seven Raid uncertainties.** The original checker searches for any legal sequence that could produce the final board. Instead, `raid_witness.py` observes the real intermediate states and dice without making choices. A separate verifier checks movement from an adjacent Cache, one or two guerrillas, distinct destinations, the two/three-space limit, activation, Sabotage adjacency, Ambush results, piece destinations, Resistance and New Village cleanup. All 537 Raids pass, including 73 with three destinations. Instrumented games exactly match uninstrumented controls. A deliberately added Resistance point is rejected. These witnesses cover the same seeds 800000–800007, all five levels and all six standard policies; therefore they include the seven previously unresolved Raids.

The original final-state search also completed: 0 violations, but **11 unconfirmed Raids** in this replay rather than the author's 7. The search has a node budget and iterates sets, so its unresolved count is sensitive to search order; the game results themselves agree. The witness-based replay resolves all 537 directly and retains the other shipped action checks. V1 still qualifies the scope of those other checks.

**Normal play through scoring.** I replayed and inspected the delivered sample, seed **20005 / adaptive / Agent**. Its stored JSON matches the regenerated sample exactly. The first three British turns use Directives 8, 5 and 7: Contact + Gather; Limited Train; Ambush + Raid. The corrected Japan then reaches nonfinal scores **2→10** and **11→17**, followed by J9's third-campaign final score **18→20** on draw 16. An independent sum confirms every score. J9 resolves its icon and final phases without either player's turn or the nonfinal Reset. The full evidence trace includes dice and intervening phases omitted from the abbreviated player handout.

**Paper workload.** Across 192 fresh Agent games, 3,108 turns averaged **2.17 goal tests and 0.80 Special Activity tests per turn**, with 16.19 turns per game. The sample's first three turns require 1 / 2 / 3 goal tests and 1 / 0 / 2 Special Activity tests. These are procedure counts, not measured physical lookups or minutes: INTEL may test several Operations internally, while target ranking and Raid require board scans. One Directive draw/discard per turn and the normal game tracks remain the recurring bookkeeping. No physical tabletop session was performed.

**Print and build limits.** I rendered and inspected the delivered rules, both reference pages, cards, record sheet, sample and simulation report. Card priorities and Limited preferences were checked card by card against `cards.json` and the code, not pooled across a page. The combined PDF's text exactly matches its component PDFs. No out-of-page text blocks were detected. I did not regenerate the publisher-style PDFs from the HTML builder, so this is direct artifact inspection and hash verification, not a byte-identical rebuild claim. P1 shows why matching a manifest alone does not prove the text is correct.

## 5. Fresh simulations and purposeful opposition

The stored 30,000-game tables recount correctly to **38.8 / 61.3 / 70.9 / 78.8 / 89.2%** for v1.0.3, rounded in print to **39 / 61 / 71 / 79 / 89%**. I ran new matched v1.0.2 / v1.0.3 games on two unused seed blocks, **220000–220127** and **230000–230127**. Agent uses both full blocks; the other levels use the first 32 seeds of each block. Both versions share each seed and policy. No rule tuning or selection of a winning variant was done on these blocks.

| Level | Fresh games per version | v1.0.2 wins | v1.0.3 wins | Change |
|---|---:|---:|---:|---:|
| Recruit | 384 | 41.4% | 37.8% | −3.6 points |
| Agent | 1,536 | 63.9% | 62.9% | −1.0 points |
| Veteran | 384 | 70.6% | 71.6% | +1.0 points |
| Legend | 384 | 78.9% | 79.4% | +0.5 points |
| Mastermind | 384 | 90.9% | 90.1% | −0.8 points |

Agent's fresh rate is **966 / 1,536 = 62.9%**, with a whole-seed bootstrap 95% interval of **59.5–66.2%**. Its paired change is **−1.0 points, interval −3.0 to +0.9**. Both blocks have a lower Agent point estimate in v1.0.3 (−0.4 and −1.7 points), but this smaller fresh experiment does **not** establish a precise three-point reduction or a reduction at every level. The published current rates are consistent with these fresh estimates. The report's original same-seed three-point comparison is a result for its own stored sample, not a universal effect size.

| Japan policy / strategy | Fresh Agent wins | v1.0.3 rate | Matched change |
|---|---:|---:|---:|
| Extraction-focused | 184 / 256 | 71.9% | +2.3 points |
| Hunting-focused | 189 / 256 | 73.8% | −4.3 points |
| Repair-focused | 188 / 256 | 73.4% | −0.4 points |
| Adaptive | 173 / 256 | 67.6% | −1.2 points |
| Counter to the British evaluation | 95 / 256 | 37.1% | −1.6 points |
| Mixed adaptive / counter | 137 / 256 | 53.5% | −1.2 points |
| Wide reply lookahead, current version only | 7 / 64 | 10.9% | No old-version comparison |

The wide opponent uses 16 candidate plans and four sampled Directive cards. On the same 64 fresh seeds, Mastermind wins **33 / 64 = 51.6%**. This confirms the practical weakness against stronger Japanese play, while the samples are too small to equate 10.9% with a precise long-run win rate. The printed 15% Agent / 54% Mastermind figures remain plausible model results.

The repaired scripted stress policies and their stored counts were checked, but I did not rerun their entire 1,024-game table here. The fresh six-policy and lookahead results above are the new adversarial evidence. I found no repeatable farming loop or forced stall in those runs. Higher-level bonuses change difficulty; they do not remove the predictability that the stronger opponent exploits.

The confidence intervals in `fresh_summary.json` resample whole seeds 10,000 times with NumPy's generator seed 595409, keeping all policy outcomes from a seed together. Games within a seed are not treated as independent. Both versions share the same underlying engine family, so a shared rules error could still bias the comparison.

## 6. Ambiguous rulings and coverage gaps

These are unresolved questions or explicit limits, **not confirmed new gameplay defects**:

- **Northern railway corner adjacency.** The existing alternative reading remains a sensitivity case. The report's current 1.3-point comparison was not repeated in this review; the independent connectivity check validates rail-to-rail income connectivity, not every disputed space-to-rail corner.
- **J10 rounding, J13's British Limited Operations, and J2 / J23 Sabotage stacking.** The simulation report correctly preserves these interpretation questions. The no-Event bot does not voluntarily execute these British sides, but they matter to a renewed Event study or to broader engine certification. No new official ruling was found.
- **Event policy study.** “Never execute Events” remains an intentionally simple bot design. Its supporting selection study was run on v1.0, not on the corrected Japan model. This review did not repeat it. The old study should not be described as a fresh v1.0.3 optimization result.
- **Japan is a heuristic opponent.** It samples a fixed action menu, does not choose a deliberate Pass, and is not an optimal player. Correcting two weak choices does not establish the remaining choices as optimal or unbiased.
- **Shared implementation.** Japanese choices and much of the engine are common to the two British bots. The second bot's later capability fixes were made by the primary author. Differential agreement is useful evidence of consistency, not full independence.
- **Synthetic states.** The random generator enforces core piece-count invariants; that does not demonstrate historical reachability or every possible hidden-Intel allocation. The fresh complete-state fuzz run is described here as random positions, not as 12,000 proven reachable games.
- **Physical usability.** No human tabletop timing, misread rate, printer duplex test, or manual bookkeeping-error rate has been measured. App save/Undo/reload tests are inapplicable to this delivery.

## 7. Optional usability and research improvements

**U1 — Optional, print usability:** add page numbers to the six-page booklet and explicit duplex/cut instructions. Keep the rules section references as well. This would reduce handling friction; it is not a legality change.

**U2 — Optional, sample-game usability:** add the chosen Japanese Operation / Special Activity, capability changes, and compact post-Propaganda positions to the sample. Its present prose is accurate but abbreviated, so a reader cannot reconstruct every transition from those lines alone. The audit's full JSON trace demonstrates what is missing.

**U3 — Optional, verification maintenance:** retain actual Raid-step witnesses so legal games do not depend on a bounded reconstruction search. Extend mutation tests whenever a new capability rule is checked. Fail loudly on unexpected lookahead-preview exceptions instead of silently swallowing them in `lookahead.py:42`.

**U4 — Optional, further design research:** rerun only the most promising Event exceptions against corrected Japan, using development seeds followed by untouched confirmation seeds. Include a simple, explainable Japan policy focused on exposed Cache guards. Do not add more paper exceptions merely because a small in-sample gain appears. No proposed behavior change is established by this review.

## 8. Reproduction, priorities and release verdict

The evidence archive contains runnable probes, the full Raid witnesses, sample trace, raw fresh results, test logs, source pins and hashes. It excludes publisher artwork and rulebook copies. It expects the repository checked out at the exact commits above. Production simulations use the standard library; PDF checks need PyMuPDF and the fresh summary uses NumPy.

From the extracted evidence folder:

```text
python checker_probes.py /path/to/repository
python paper_probes.py /path/to/repository
python boundary_checks.py /path/to/repository
python raid_witness.py /path/to/repository
python fuzz_complete_state.py /path/to/repository
python fresh_games.py /path/to/v1.0.2 v102
python fresh_games.py /path/to/v1.0.3 v103
python analyze_fresh.py
```

The probe scripts assert the **observed current defects**, so an unchanged v1.0.3 checkout exits successfully when it reproduces them. After fixing a defect, convert its observation into the corresponding rejection / corrected-text assertion. The passing controls already distinguish the legal nearby cases. The README lists the additional package, information-access and repository-suite commands.

**Priority 1:** correct P1's stale flowchart sentence and regenerate the affected PDFs. Correct D1's short lookahead description in the same print pass. **Priority 2:** strengthen the legality checker with selected Supply spaces, Supply dice and the closed Event-box rule; add the negative controls. **Priority 3:** widen the fuzzer's state comparison and keep the successful fresh-state overlay as a regression check. Then run a physical game and record actual lookup counts and time.

**Release verdict: pass for playing the bot; a small print-and-verification patch is recommended before calling the package final.** No new gameplay or scoring defect was confirmed. The paper flowchart still contradicts the correct Pass rule, and the new legality claim has demonstrated blind spots. Once those are corrected, the current evidence supports release as a simulation-tested fan bot, with the printed limits on opponent strength and the absence of tabletop testing retained.
