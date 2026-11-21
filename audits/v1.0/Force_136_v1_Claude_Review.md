# Force 136 v1.0: review of Claude's redesign

21 November 2026 | Japan player versus the British Force 136 bot

**Verdict: keep the redesign. Hold an unqualified release approval until the comparison tests and a few rule explanations are corrected. The package is suitable for structured tabletop playtesting.**

Claude has made a substantial improvement over the v0.2 draft. The nine-card deck, reliable marker placement, useful Ambushes, and practical Raid procedure address the weaknesses in the earlier simulation study. The work includes reproducible results, useful rejected experiments, an additional implementation, and a printable package. The recorded Agent result reproduces exactly. The issues below concern verification coverage, a mistaken rules explanation, one ambiguous reference-sheet instruction, and claims that go further than their supporting methods.

I found no demonstrated illegal action in the primary bot in the normal games exercised here. That is a bounded result, not certification of every game rule or capability combination. No production code or printed rules were changed during this review.

## 1. Version and sources

- Repository: https://github.com/ramyahoo88/the_british_way_solo
- Reviewed branch: `claude-force136`.
- Frozen commit: `615c870cf018a5122b3991b00dfbbd4224d04e42`.
- Baseline: `main` at `e54c718894eb44a8edb7c8b736c2c160edcfed60`; eight new commits reviewed.
- Product: `force136_v1/`, version 1.0, dated 21 November 2026. Nine Directive cards; five levels; standard standalone Japanese Occupation scenario. Japan is the human side; MPAJA remains an independent actor.
- Official rules: GMT's 2026 Japanese Occupation rulebook, 28 PDF pages, including section 1.4.1 on PDF page 4. The original card faces for J8, J22 and J27 were inspected visually. The previously collected player aids and rules were used for the relevant operations and scoring.
- Official rulebook: https://gmtwebsiteassets.s3.us-west-2.amazonaws.com/TheBritishWay_EnemyofMyEnemy/EomE_JapOcc_Rules.pdf
- Rulebook SHA-256: `ee65b70ce42cfe170d001c186fa16edcc5c1cb1fccfd7b1e4703184005fec370`.

The bot's printed variant rules determine its voluntary priorities; the publisher's rules determine legality. Restricting the bot to a subset of legal actions is a design choice. Calling an explicitly legal action an unresolved ruling is a documentation error. I did not conduct a new search for every subsequent publisher correction; this review is tied to the identified rules PDF and card faces.

## 2. What was tested directly

| Check | Direct result |
|---|---|
| Printed-rules module versus tuning module | 960 comparison cases across five levels; 0 reported mismatches. Each case executes both versions. |
| Printed-rules module versus secondary implementation | 960 comparison cases across five levels; 0 reported divergences using the shipped comparator. Its limits are demonstrated in F1 and F2. |
| Original Agent holdout replay | All 768 result rows reproduced exactly, including outcomes, tracks and action counts stored in those rows. |
| Recount of Claude's two stored holdouts | All 11,520 rows checked for duplicate game keys and results independently aggregated. |
| Fresh regular-opponent games | 1,152 Agent games on 192 new seeds; another 384 games cover the other four levels on 16 of those new seeds. |
| Fresh wide-search Japan | 32 Agent and 32 Mastermind games, 16 candidates and 4 reply samples per candidate. |
| Optional local-refresh experiment | 192 matched Agent games per policy variant, 384 executions total; no reliable gain. |
| Full shipped sample | Seed 20005, adaptive Japan: complete narrated output matches its stored JSON exactly. |
| Full game with independent scoring arithmetic | Seed 20007, counter Japan: all three Propaganda calculations and the final Japan victory at Resistance 17 checked. Phase boards came from the shared engine. |
| Focused regressions | J8 failed-roll selection, Japanese J27 lowest-Population choice, immediate New Village removal and a nearby surviving-cube case, Operation-before-SA timing, level bonus timing, deck exhaustion, visible-information decisions and preview immutability. |
| Printed materials | All five rules pages and both reference columns visually inspected; all nine card rectangles, goal orders, Limited preferences and backs checked. The combined ten-page package matches its component texts. |

These are code executions and document inspections. There was no physical playtest, measured turn time, printer trial, or interaction with a shipped app. Undo, saves and browser recovery are outside this paper product's scope. The PDFs were inspected as shipped; I did not reproduce the Chrome-based PDF build in this environment.

## 3. What the simulation evidence supports

Claude's pooled figures are arithmetically correct. They are results against six fixed computer policies, not estimates of human win rates.

| Level | Claude's pooled British wins | Independent recount | Fresh check |
|---|---|---|---|
| Recruit | 36% | 840 / 2,304 = 36.5% | 36 / 96 = 37.5% |
| Agent | 61% | 1,409 / 2,304 = 61.2% | 618 / 1,152 = 53.6% |
| Veteran | 71% | 1,625 / 2,304 = 70.5% | 55 / 96 = 57.3% |
| Legend | 79% | 1,814 / 2,304 = 78.7% | 66 / 96 = 68.8% |
| Mastermind | 89% | 2,054 / 2,304 = 89.1% | 79 / 96 = 82.3% |

The non-Agent fresh cells contain only 16 seeds crossed with six policies. Their uncertainty is large: they establish the direction of the difficulty ladder in this sample, not revised precise ratings.

Agent's first fresh window, seeds 50000-50063, produced 196/384 wins (51.0%). A disjoint confirmation window, seeds 60000-60127, produced 422/768 (54.9%). Combined: 53.6%, with a seed-cluster bootstrap 95% interval of 49.1-58.2%. The difference from the original pooled result is -7.5 percentage points, with an independently resampled seed-cluster interval of -12.9 to -2.1 points. This is evidence of sensitivity across these seed windows. It does not identify a cause or establish deliberate selection, overfitting, or a universal 54% rate.

| Japan strategy | Fresh Agent British wins | Fresh games |
|---|---|---|
| extraction | 106 / 192 = 55.2% | 192 |
| hunting | 132 / 192 = 68.8% | 192 |
| repair | 111 / 192 = 57.8% | 192 |
| adaptive | 108 / 192 = 56.3% | 192 |
| counter | 70 / 192 = 36.5% | 192 |
| mixed | 91 / 192 = 47.4% | 192 |

The counter policy remains the most demanding ordinary opponent. Fresh wide-search Japan held Agent to 1/32 wins (3.1%) and Mastermind to 16/32 (50%). These small cells confirm vulnerability and the usefulness of a harder level; they do not precisely recalibrate Claude's 13% and 48% figures. Approximate Wilson intervals are 0.6-15.7% and 33.6-66.4%, respectively.

The old v0.2 comparisons stored in the branch use the same executor and first holdout: 0% for the paper draft, 2% for its earlier experimental variant, versus 59.9% for the new Agent. I replayed the new Agent cell, rather than every old reference cell. The size of the documented improvement and the fresh results support replacing v0.2 with this design. The expert benchmark's interpretation needs the qualification in F5.

## 4. Confirmed findings

### F1. High: the secondary comparison can approve a different winner

**Type:** verification defect. This is not a discovered scoring error in the primary bot.

**Impact:** the advertised independent agreement cannot establish agreement on Resistance, resources, Zipper, complete game length or final winner. A release check may stay green after a material rules regression.

**Expected behavior:** compare the relevant public state throughout play and require equal final outcomes. Require equal trace lengths before comparing entries.

**Exact reproduction:** run `compare_mutation.py` from the evidence package. It subclasses the secondary implementation and deliberately adds 1 Resistance immediately before final scoring. On seed 20007, counter Japan, Agent, the unchanged primary ends at Resistance 17 with Japan winning. The mutant ends at 18, with one Camp and two Force 136 markers, so Force 136 wins. Both have 18 recorded British turns. The shipped `first_div` returns `None`.

Two additional focused assertions show that recorded Resistance 18 versus 20 and an extra trace entry are also accepted.

**Observed cause and source:** `force136_v1/code/cleancmp.py:16-20` compares only plan box/Operation/SA, piece-board dictionaries and sabotage inside `zip(a,b)`. `:31` obtains both final results but does not compare them. The trace records Resistance at `:14` but the comparator ignores it. Goals and Directive IDs are also recorded but not compared.

**Smallest proposed fix:** reject unequal trace lengths; compare recorded Resistance, goal and Directive; add captures for resources, Zipper, capabilities and off-map/pool bookkeeping; compare final winner and final tracks. Keep the scoring mutant and a deleted-turn mutant as negative controls. Metrics with intentionally different names need not match.

### F2. Medium: the secondary implementation omits British J22 and J27 effects

**Type:** confirmed verification coverage defects. J27 also exposes an incomplete paper procedure; see Q1.

**Impact:** normal holdouts cannot reveal these omissions because neither side's policy creates British-side capabilities: Force 136 never chooses Events, while the Japan policies choose Japanese Event sides. A player can nevertheless choose a British capability, and printed section 7 explicitly supports that case.

**Expected behavior:** J22's British side preserves the Underground status of guerrillas used for Gather. J27's British side permits one additional non-F136 space for each Ambush and Sabotage Operation. The independent implementation should reproduce the adopted bot procedure for both.

**Reproduction A:** standard setup, seed 139002; set capability 22 to British (`U`); call Gather in each implementation. Both reveal the same six chits. The primary leaves eight guerrillas Underground; the secondary leaves two. It wrongly activates six.

**Reproduction B:** standard setup, seed 139003; move one Underground red guerrilla from Johore to Pahang and add one Available Police in Pahang. Set J27 British and call Ambush. The primary removes Pahang's Police and activates one guerrilla there. The secondary leaves that Police and the Underground guerrillas unchanged. Run `probe_findings.py` for both fixtures and full board output.

**Sources:** original J22 and J27 card faces; printed rules `Force_136_v1_Rules.md:104,141`; correct primary handling at `code/force136_v1.py:125-143,151-163`; secondary `code/cleanroom/cleanroom.py:288-294,330-337,359-361`. Its Ambush docstring explicitly says the extra space is ignored.

**Smallest proposed fix:** guard Gather activation with J22's British side; implement J27's extra Ambush and Sabotage selections from an explicit printed priority; add forced-capability tests for both sides of all six capabilities. Do not treat ordinary random games as coverage of states their policies cannot generate.

### F3. Medium: same-space Train refresh is described as an uncertain ruling

**Type:** confirmed incorrect rules explanation. Expanding the bot's action policy is optional.

**Impact:** the design notes incorrectly exclude a legal option on rules grounds. In an exhausted-pool position all nine Directives Pass although Train could restore Underground guerrillas and allow Supply. Players may misunderstand the base game.

**Expected rule:** official section 1.4.1, PDF page 4, explicitly illustrates taking guerrillas from the map during Train and returning them Underground in the same space or a different one. There is no unresolved ruling on that point.

**Smallest useful setup:** seed 139001; Resistance 6, Zipper 6, one unreleased Cache. Put all 15 Troops, six Police and three Kempeitai in Kuala Lumpur. Perak has F136, Camp, Cache and 10 Active red guerrillas. Kedah and Negri Sembilan each have F136, Camp and two Active blue guerrillas. All other spaces are empty; no red or blue guerrillas are Available. All action boxes are free.

**Steps and observed result:** apply each Directive to `choose(BOXES)`. Every one selects Pass. A local-refresh alternative instead chooses Train + Supply: it turns two Perak red and one blue in each other F136 space Underground, then converts the Kedah and Negri Sembilan Camps to Caches. Piece totals remain legal. `probe_findings.py` includes this assertion and the full board.

**Sources:** `NOTES.md:20`; `print/Force_136_v1_Sim_Report.md:108`; primary `code/force136_v1.py:93-100`; printed Train restriction at `print/Force_136_v1_Rules.md:87`.

**Smallest proposed fix:** correct the report and notes to say the option is legal but deliberately excluded from this bot. Keep the exhausted-pool fixture. Consider a narrow recovery exception separately.

**Experiment, not a proposed release change:** a simple policy that refreshes locally before looking for a remote donor won 125/192 matched games versus 137/192 for unchanged Agent, seeds 51000-51031 and six policies. Difference -6.25 points, seed-cluster interval -13.0 to +0.5. It fixes the fixture but does not establish an overall improvement. Do not automatically adopt it, and do not describe the fixture as a permanent deadlock: Reset can restore Underground pieces.

### F4. Medium: J8's reference wording can imply an extra Supply slot

**Type:** ambiguous printed instruction, not a confirmed primary-code rules defect.

**Impact:** a player using the quick reference may convert three Camps when the normal two-Province limit applies.

**Expected behavior:** British J8 changes the eligibility of one selected Province; it does not increase the normal Supply limit. The full rules and primary code apply this correctly.

**Exact setup and reading:** at Zipper 6, have three Available Caches and three eligible Camp Provinces, two with F136 and one without. Follow the reference's two-space limit, then its line `British J8: +1 Province without F136.` That can be read as a third selection. The primary converts only two. The focused fixture is seed 139014 in `regression_checks.py`.

**Sources:** J8 card face; full printed section 6.6 at `Force_136_v1_Rules.md:108-110`; reference PDF page 2, right-hand Procedures column; generating source `print/build.py:137`; correct code `code/force136_v1.py:165-175`.

**Smallest proposed fix:** replace the short line with: `British J8: one selected Province may lack F136; no extra slot.` Add the British J22 reminder to Gather while revising that sheet. Regenerate the reference and combined PDFs.

### F5. Medium: benchmark descriptions overstate the search performed

**Type:** evidence interpretation and documentation; the benchmark remains useful.

**Impact:** readers may infer human-level strength, exhaustive legal search or an isolated eight-point predictability cost that these experiments do not establish.

**Expected description:** a one-step heuristic compares predefined engine action templates and their fixed targeting procedures. Lookahead Japan evaluates sampled Directive replies, rather than knowing the actual next hidden card. Differences between two different British policies do not alone isolate predictability as a causal factor.

**Reproduction and observed behavior:** `british_candidates` has four Train templates across the available boxes: one Limited Train and full Train with no SA, Supply or Raid. It does not enumerate legal target subsets or alternative piece allocations. Separately, with eight publicly discarded Directives and only Directive 9 left in the pile, the reply sampler still draws uniformly from all nine cards. For seed 139020, draw 1, its first four samples are 6, 6, 2, 6. `method_checks.py` records both witnesses.

**Sources:** `code/expert.py:106-135`; `code/lookahead.py:34-42`; overbroad wording in `README.md:33`, `print/Force_136_v1_Sim_Report.md:21-23,76-83`, and printed rules `:157,193`. The report's eight-point inference compares Agent and a different search policy, rather than a matched intervention changing only predictability.

**Smallest proposed fix:** describe the reference player as a one-step heuristic over predefined plans; replace “exact reply” with “sampled bot replies”; describe the eight points as an observed benchmark difference. For a future stronger experiment, sample only from publicly possible remaining Directives, use common samples across candidates, and retain per-seed wide-search results. Rerun that changed opponent on matched and fresh seeds before substituting its results.

### F6. Low: the root checksum manifest is stale

**Type:** packaging integrity.

**Impact:** a correct branch checkout fails verification of the root README, and the new v1 package has no entries in the existing root manifest.

**Reproduction:** compute SHA-256 of the pinned branch's `README.md` and compare `FILE_MANIFEST_SHA256.json:2`. Expected by the manifest: `6bb8b4924f7ac5f85a12e4ad8f83c61676cc18383b48e03048d965e800ff5f69`. Observed: `c1c005ca493df3c0c153ff0c2c5c62b6730798017c7294ee272164143a185f3b`. `probe_findings.py` asserts the mismatch.

**Smallest proposed fix:** regenerate the manifest after final edits, or scope it explicitly to the historical release and provide a current v1 manifest. Do not include the manifest's own hash recursively.

## 5. Ambiguous procedures and optional improvements

**Q1: J27's extra Operation space needs an explicit target and timing rule.** Sections 6.3 and 6.4 describe F136 spaces, while section 7 grants British capability benefits using matching procedures and then map order. At standard setup with British J27, seed 139004, inherited primary Sabotage chooses Pahang as the remote space using the old regional railway priority; a straightforward application of the printed map-order fallback chooses Kedah. The primary's actual sabotages are Perak-Pahang-Selangor, Negri Sembilan-Pahang and Pahang-Johore. This is a legal base-game use of J27, but the intended bot priority is insufficiently specified. State when the extra space is selected, how it is ranked, and whether it can qualify a goal by itself. Then align both implementations and the reference. The board witness is in `regression_checks.json`. This is a procedure question, not a claimed illegal move.

**Optional usability:** change “the card's four goals” in `README.md:7` and “same four goals” in `NOTES.md:49` to “the card's goals.” Cards 1-8 correctly have three variable goals; card 9 has four. Keep the direct explanation that PLACE is always first and CONTACT the fallback.

**Optional tabletop measurement:** retain the current playtest record and add turn duration plus the number of times the full rules were opened. The reported 2.3 goal checks is a model count, not measured handling time. INTEL's three separate previews and Raid's destination/source comparisons deserve particular observation. No timing benefit has yet been established.

## 6. Reproduction and evidence

The evidence ZIP contains this report's Markdown, assertion scripts, full board witnesses, source hashes, original-Agent replay rows, fresh results, matched refresh results, and independent statistics. It excludes the publisher's PDF and card artwork. The frozen repository supplies the reviewed implementation and printed PDFs.

Arrange the extracted `review_claude_v1` folder beside a checkout named `claude_force136_review`, pinned to the commit above. Scripts locate that sibling directory; they do not patch its source.

```text
cd review_claude_v1
python3 probe_findings.py
python3 compare_mutation.py
python3 regression_checks.py
python3 method_checks.py
python3 scoring_checks.py
python3 analyze_results.py
python3 check_printables.py
```

The first six checks need only Python's standard library. The final printable check requires PyMuPDF. `regression_checks.py` uses the already supplied reproduced sample JSON; the evidence README gives the command to regenerate it and the exact commands for each larger run. Statistical intervals resample whole seeds, preserving the six policies' pairing within a seed. The two fresh Agent windows are disjoint; repeated Agent games from the initial five-level sweep are not counted twice.

## 7. Release decision and priorities

1. Strengthen the comparator and demonstrate that it rejects wrong-score, wrong-winner and missing-turn mutants.
2. Add forced British capability fixtures; fix the secondary J22/J27 behavior and settle the printed J27 procedure.
3. Correct the Train explanation, J8 reference text and benchmark claims; regenerate the affected PDFs and checksum manifest.
4. Keep the current nine-card design and five-level ladder for tabletop testing. Do not adopt the simple refresh policy or another defensive rule solely because it repairs one position.

**Release verdict: conditional hold for an unqualified public-release approval; proceed with structured tabletop playtesting after the short corrections.** The improvement over v0.2 is substantial and supported by executable evidence. Normal comparisons reproduce, the printed cards agree with code, and the targeted past fixes tested here hold. The remaining blockers are false confidence from an incomplete independent checker and avoidable printed-rule uncertainty. Human difficulty, handling time, all capability combinations, a fresh errata census, and independent validation of the full shared executor remain coverage gaps.
