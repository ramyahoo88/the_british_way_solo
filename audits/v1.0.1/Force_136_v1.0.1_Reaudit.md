# Force 136 v1.0.1: review of Claude's fixes

21 November 2026 | Japan player versus the British Force 136 bot

**Verdict: retain v1.0.1 and its last-resort Train refresh. The previous release blocker is resolved. Pass for structured tabletop testing; make two small reporting and checker-command corrections before publishing the reviewed package.**

Claude's main claims hold. The old reproductions now pass, the strengthened comparison detects the planted scoring error, and the new Train policy improves results in an independent fresh experiment. I found no new defect in the bot's legal play or production scoring. Two follow-ups remain: the simulation report contains stale numbers, and the verifier reports errors without returning a failing process status. An additional Zipper oracle check would improve future regression coverage; it is explicitly optional here.

## 1. Frozen version and scope

- Repository: https://github.com/ramyahoo88/the_british_way_solo
- Branch: `claude-force136`.
- Reviewed commit: `fe57c0faea60bc913e1f7c859963059d92d9aa7e`.
- Comparison version: v1.0 at `615c870cf018a5122b3991b00dfbbd4224d04e42`.
- This is an incremental review of the fixes and new evidence, not a new independent implementation of every publisher Operation and Event.
- Rules precedence: GMT's 2026 Japanese Occupation rules and card faces determine legality; the printed Force 136 v1.0.1 rules determine the bot's voluntary priorities.

The official rulebook is the previously identified 28-page PDF, SHA-256 `ee65b70ce42cfe170d001c186fa16edcc5c1cb1fccfd7b1e4703184005fec370`. Section 1.4.1, PDF page 4, explicitly permits same-space re-placement during Train. J8, J22 and J27 were checked against the card faces during the previous review; the new changes were checked against those rulings. This review does not add a fresh census of publisher errata.

Official rulebook: https://gmtwebsiteassets.s3.us-west-2.amazonaws.com/TheBritishWay_EnemyofMyEnemy/EomE_JapOcc_Rules.pdf

## 2. Direct checks and previous findings

| Check | Observed result |
|---|---|
| New full-state verifier, `verify_v1.py 32` | 2,496 comparison cases, each executing both implementations; zero cross-check or scoring-oracle failures. JSON matches Claude's stored results exactly. |
| Mutation suite, `--mutants 16` | All 13 planted errors caught; 1,440 comparison cases. Results match Claude's stored JSON exactly. |
| Previous review fixtures | All eight pass, including exhausted pools, J22, J27, J8's limit, trace length and the final-scoring mutant. |
| Printed module versus tuning lab | 960 comparison cases across all five levels; zero mismatches. |
| Independent recount | 54,000 stored v1.0 rows and 30,000 v1.0.1 rows checked for duplicate keys and independently aggregated. |
| Untouched-seed Agent experiment | 1,536 matched cases per variant on seeds 120000-120255; 3,072 game executions. |
| Other levels | 96 matched cases per variant at each of the other four levels, another 768 executions; too small for precise strength estimates. |
| Wide-search replay | Agent and Mastermind, 128 games each on seeds 20000-20127, 16 candidates and four sampled replies. Results reproduce. |
| Nearby Train cases | Both implementations use a permitted remote donor before refreshing locally, retain the donor's majority, respect the Cache quota, and do not count an already Underground piece as a refresh. |
| Printed package | Six rules pages, two reference pages, nine cards and backs on two pages, one record sheet. The combined 11 pages match the individual PDFs' text. All nine card orders and Limited preferences agree with code. |
| Checksum manifest | All 136 listed files match; every other tracked file is covered. |

The printed rules and both reference columns were inspected visually. The reference now gives the J8 slot restriction and J22 reminder; J27's extra-space procedure is present in the full rules and reference. No physical playtest, handling-time measurement or printer trial was performed. The Chrome PDF build was not reproduced here.

| Previous finding | Closure |
|---|---|
| F1: checker ignored tracks, length and final winner | Fixed in the new comparison and scoring oracle. The old wrong-winner mutant is rejected. |
| F2: secondary J22/J27 omissions | Fixed; forced-capability comparisons and exact fixtures pass. The file accurately discloses that the original author added these parts later. |
| F3: same-space Train called uncertain | Corrected, and a legal last-resort refresh is now implemented. |
| F4: J8 reference could imply an extra slot | Corrected in both printed forms and tested. |
| F5: exaggerated benchmark descriptions | Search scope and sampled replies are now described accurately; the benchmark gap is no longer called a measured predictability cost. |
| F6: stale checksum manifest | Fixed. |
| Q1: J27's extra-space priority | Resolved explicitly: first qualifying non-F136 space in map order, not enough by itself to qualify a goal, and no Raid extension. The old Kedah/Pahang fixture now selects Kedah in both implementations. |

The verifier compares British-turn states and Propaganda/final states. It does not independently reimplement the shared Japanese Operations or Events. Its scalar scoring oracle is also narrower than a complete independent Propaganda-phase executor; see the optional extension below.

## 3. Strength and statistics

### The broader v1.0 baseline checks out

The compressed v1.0 data contains exactly 30,000 Agent games across five 1,000-seed blocks. Force 136 wins 17,835, or **59.45%**. My seed-cluster bootstrap interval is approximately 58.6-60.3%. The blocks range from 58.2% to 60.5%.

The earlier GPT windows are reproduced exactly inside those rows: 618/1,152, or 53.65%. Resampling 192 distinct seeds from the observed 5,000-seed population gave a result that low in 68 of 20,000 samples, or 0.34%. This supports Claude's explanation that those windows were unusually low in this model. It is a conditional empirical resampling result, not a probability about all possible future play.

My prior report correctly treated the 53.6% result as seed-window sensitivity and did not identify its cause. The larger data now supports a baseline near 59.5%. The 30,000-game baseline extends the earlier windows; the 1,152 overlapping games must not be counted as additional independent evidence.

### The last-resort refresh is supported

On Claude's 1,000 matched seeds, Agent goes from 3,580/6,000 wins (59.67%) without the refresh to 3,865/6,000 (64.42%) with it: **+4.75 percentage points**. My seed-cluster bootstrap interval is +3.8 to +5.7 points, consistent with the reported +3.8 to +5.8 after rounding and resampling variation. There are 541 newly won cases and 256 newly lost cases, so this is an aggregate improvement, not a benefit in every individual game.

The gain is positive against all six Japan policies in that sample. Other levels also improve in the stored matched data: Recruit +6.63 points, Veteran +3.93, Legend +3.55 and Mastermind +2.30.

For an independent confirmation I used untouched seeds 120000-120255 and the same six policies. The control is the same v1.0.1 code with only the local refresh disabled; its outcomes match 24 sampled v1.0 normal games exactly. British capability changes cannot confound this ordinary-policy comparison because those policies never create British-side capabilities.

| Agent variant | British wins | Mean final Resistance |
|---|---|---|
| Without refresh | 923 / 1,536 = 60.09% | 17.17 |
| Last-resort refresh | 988 / 1,536 = 64.32% | 17.51 |
| Paired change | +4.23 points; 95% interval +2.34 to +6.25 | +0.34 |

The direction is positive against every policy in this independent Agent sample as well. The small checks at other levels are inconclusive individually; they do not overturn the larger matched study.

This policy is different from the earlier refresh-first experiment. Using a remote donor first can preserve a useful local Active guerrilla while increasing the local force count. The new fallback restores an Underground actor only when that placement is unavailable. It adds one conditional step to Train and needs no extra component or bot die.

### Revised difficulty figures are arithmetically correct

| Level | Stored v1.0.1 British wins | Rate | Rounded printed rate |
|---|---|---|---|
| Recruit | 2,477 / 6,000 | 41.28% | 41% |
| Agent | 3,865 / 6,000 | 64.42% | 64% |
| Veteran | 4,440 / 6,000 | 74.00% | 74% |
| Legend | 4,896 / 6,000 | 81.60% | 82% |
| Mastermind | 5,475 / 6,000 | 91.25% | 91% |

The strongest tested Japan remains a serious challenge. Its replay gives Agent 19/128 wins (14.84%) and Mastermind 65/128 (50.78%). These are the claimed roughly 15% and 51%. They are results against a specific sampled-reply search policy, not proof of optimal Japanese play or a human win-rate prediction.

## 4. Remaining confirmed findings

### R1. Medium: the simulation report mixes v1.0 and v1.0.1 numbers

**Player impact:** readers get conflicting advice about difficulty and particular Japanese strategies. The headline rates in the rules are correct; this is a reporting error, not a discovered game-play error.

**Expected behavior:** every table labeled as v1.0.1 on seeds 0-999 should use the rows for that version. Historical v1.0 results should be labeled as such.

**Exact reproduction:** group `code/results/results_fresh_v101.csv.gz` by level and policy and divide Force 136 wins by the 1,000 rows in each cell. Compare the report's “Results by Japan policy” table. It retains older v1.0 values. For example, Agent versus extraction is printed as 66%, but the current result is 706/1,000 = 70.6%, which rounds to 71%.

| Japan policy | Report's Agent cell | Correct v1.0.1 Agent result | Matched refresh gain |
|---|---|---|---|
| extraction | 66% | 70.6% | +5.0 points |
| hunting | 72% | 76.9% | +4.5 points |
| repair | 70% | 76.7% | +6.6 points |
| adaptive | 64% | 68.7% | +5.1 points |
| counter | 38% | 40.2% | +1.8 points |
| mixed | 48% | 53.4% | +5.5 points |

The same problem affects the other bot columns in that table. The report's summary paragraph also still says wide-search Agent 13% and Legend 31%, while its current detailed table and README correctly give about 15% and 26%.

**Sources:** `force136_v1/print/Force_136_v1_Sim_Report.md:32,54-63`; shipped report PDF pages 1-2. The correct current data is also in `code/results/fresh_v101_summary.json`.

**Smallest proposed fix:** replace the five bot columns with the current summary values and correct the wide-search summary paragraph; retain the search-player column with its existing historical label. Regenerate the simulation report PDF and checksum manifest. A data-driven table generator or an assertion against the CSV would prevent this drift. `recount.py` produces every expected cell in `evidence/recount.json`.

### R2. Medium: verification failures still produce a successful command status

**Player impact:** future automated release checks can go green even when the verifier detects a material scoring regression. This does not invalidate the zero-failure results reproduced above; it affects how the checker is used.

**Expected behavior:** normal verification should exit nonzero when cross-check or oracle failures occur. Mutation mode should exit nonzero if any required mutant is missed.

**Exact reproduction:** run `python3 exit_status_probe.py` from the evidence package. It starts a subprocess, temporarily doubles Cache scoring in the shared engine in memory, then runs the unmodified verifier command with one seed per normal block. It reports oracle failures in 27 of 30 normal comparison cases, yet the subprocess returns **exit code 0**. No production source file is edited. The captured stdout and JSON are included.

**Observed cause and source:** `force136_v1/code/verify_v1.py:235-260` prints counts and “SOME MISSED” where applicable, but neither branch raises an assertion or selects a failing exit code. Positive seed-count validation would also help avoid empty forced-capability blocks in very small runs.

**Smallest proposed fix:** finish normal mode with a failing exit status if either total is nonzero; finish mutation mode with a failing status unless all required entries are caught. Retain the injected-error subprocess as a test of the command's status, alongside a clean-run status check.

## 5. Optional verification extension and limits

**Optional: independently check Zipper placement as well as scalar scoring.** The oracle explicitly implements Resistance and winner calculations through rules 6.1.1-6.2.4, 7.0.1 and 1.13. It does not independently check rule 6.2.5's Zipper placement or the resulting Cache releases/returns. Cross-comparison of those fields cannot expose an identical error in the shared engine.

A focused negative control freezes Zipper at Delay whenever the shared engine is asked to place it during Propaganda. In seed 20000/counter/Agent, the altered game reaches Resistance 15 after draw 7 while Zipper remains 0 instead of 12. At draw 14, Resistance is 20 and Zipper is still 0 instead of 20. Both cross-check and oracle report zero failures. `zipper_oracle_probe.py` reproduces this. The actual shipped engine uses the correct threshold formula; this is a coverage extension, not a newly discovered production defect.

The smallest extension is to derive expected Zipper from scored Resistance before the optional level bonus, then check Cache-track/pool changes under rule 6.7.2. Until then, describe the oracle as independently checking Resistance and victory arithmetic rather than every effect of the Propaganda phase.

Other remaining limits are accurately disclosed by Claude: Operations, Events and Japanese targeting share the research executor; capability/Event combinations are not exhaustive; Event-policy experiments were run on v1.0, not repeated after the refresh. No physical game or handling-time measurement has been performed. There is no evidence here that the added fallback requires a new Event policy or a different deck mix.

## 6. Reproduction and release recommendation

The evidence ZIP contains the review's Markdown, complete fresh matched-game rows, independent recounts, old-window reference rows, regression witnesses and captured validation output. It does not redistribute publisher rules or card artwork. The reviewed code, original compressed studies and printed PDFs remain available at the frozen GitHub commit.

Extract `review_claude_v101` beside a checkout named `claude_force136_v101_review`, pinned to the commit in section 1. The evidence README gives all commands. Standard Python 3.11+ is sufficient except for `check_package.py`, which needs PyMuPDF.

**Priorities:** correct R1's report text and tables; give the verifier reliable failure exit codes for R2; optionally extend the scoring oracle to Zipper. Keep the last-resort refresh and the current Directive deck. The independent confirmation supports the change without adding a new rules subsystem.

**Release verdict:** the previous high-severity blocker is closed. v1.0.1 passes this incremental review for structured tabletop testing. A short reporting/checker patch should precede publication of the reviewed package. No further bot redesign is warranted by these results; human difficulty and tabletop usability remain to be established.
