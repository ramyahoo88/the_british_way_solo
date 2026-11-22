# Force 136 v1.1: rulebook follow-up

**21 November 2026.** Reviewed `ramyahoo88/the_british_way_solo` at **127e34cdabae591901124c66fdbeba2e80ee2102**. This addendum corrects and narrows the unresolved-readings discussion in the preceding v1.1 audit and simulation report. It does not publish a new bot version.

**Outcome:** J13's trial policy unnecessarily restricts British Limited Operations. The J2/J23 and J19 card tips settle the cited questions, and the current code already follows them. I favor the wider northern adjacency reading, while labeling that conclusion as an interpretation of the map/border wording rather than an explicit northern-corner ruling. The tested changes give no reason to add J13 to the bot's Event list.

## Basis

I rechecked the current GMT **Japanese Occupation Rules of Play** (28 pages, ©2026): rule **2.4.4**, rules **1.3.6-1.3.7**, the **4.3.1 Extract example**, and the J2, J13, J19 and J23 card notes. The original layouts of rules pages 3 and 9 were inspected. Sources: [rules PDF](https://gmtwebsiteassets.s3.us-west-2.amazonaws.com/TheBritishWay_EnemyofMyEnemy/EomE_JapOcc_Rules.pdf) and [GMT product/Living Rules index](https://www.gmtgames.com/p-1107-the-british-way-enemy-of-my-enemy.aspx).

J13 changes which guerrillas can participate; it does not turn a British Limited Operation into a Japanese one-space Operation. J2/J23 explicitly permit adding Sabotage to already sabotaged Railways. J19's shaded tip preserves use of the selected spaces themselves and restricts adjacent-space use to one selected anchor. The bot's choice of its first anchor for that permission is a priority, not an official requirement.

## F1 — Confirmed trial-policy restriction: J13

**Impact.** The original experiment undervalues a wider legal J13 policy. Its two single-space actions are legal choices, so this is not evidence of illegal play. The problem is hard-coding those choices as the trial's available scope and treating that as a complete test of the Event. The released bot's own Event list remains J4/J25.

**Expected behavior.** Each J13 Limited Operation can use multiple eligible MPAJA spaces, while selecting one Operation type and adding no Special Activity. Activation and other ordinary eligibility requirements still apply. Choosing every eligible space is the corrected trial policy; it is not a mandatory official instruction.

**Smallest useful reproduction.** Use seed **1122001**. Empty the board; put all 15 Troops, six Police and three Kempeitai in Kuala Lumpur. Put two Underground MPAJA guerrillas in each of Kedah, Kelantan and Johore. Start at Resistance 2, with all Railways clear and no Force 136 markers on the map. Apply J13's British side, using the research selector's Sabotage-first priority.

- **Observed at 127e34c:** two one-space Sabotage calls, both in Kelantan; two Sabotage placements in total.
- **Corrected trial:** the first Operation uses Kelantan, Johore and Kedah; the second uses Kelantan and Johore; five placements in total.
- **Ambush boundary:** instead put two Troops in each of those three Provinces, nine Troops in Kuala Lumpur, and Sabotage on all eight Railways. Fix Ambush dice at 6. The original policy makes two attempts in Kedah and raises Resistance from 2 to 4. The corrected policy makes two Operations of three attempts each and raises it from 2 to 8. Neither performs a Special Activity.
- **Nearby controls:** with only Kelantan eligible, both policies make the same two Sabotage placements. With only blue guerrillas in the three spaces, neither uses them for J13.

**Source and smallest fix.** `force136_v1/code/engine.py:468-484`, particularly the single-space lists passed at `:480-481`. `J13_multispace.patch` adds a dedicated unshaded-J13 branch that resolves all selected eligible spaces for each of its two Operations. It preserves the existing Sabotage-before-Ambush selector, J11's separate behavior, the Japanese J13 side, and the no-Special-Activity limit. The patch applies cleanly to the pinned source; its resulting engine matches the fixture-tested file byte for byte.

**Unresolved paper procedure, not a finding of illegal play.** The simulated Japan policies execute shaded Events (`engine.py:1044`), and the released British bot chooses only J4/J25 (`force136_v1.py:284`). That explains why this branch is absent from the reported Force 136 level games. A human Japan can select either side, including British J13. If this resolution is to be fully automatic at the table, its choice between Sabotage and Ambush should have a written priority. The proposed patch's priority is a research choice, not an implied GMT ruling. Section 7 currently directs British choices to matching procedures without explicitly naming that choice.

## What the corrected J13 experiment says

The matched cohort is **1,000 seeds, 900000-900999**, crossed with extraction, hunting, repair, adaptive, counter and mixed Japan: **6,000 seed-policy pairs**. As in the original Event study, the baseline is **v1.0.4 with no bot Event step**, against corrected Japan. It is not a test of adding J13 on top of v1.1's J4/J25 combination.

The corrected run's 6,000 baseline winners and final Resistance values exactly match the retained unmodified-engine controls. The old J13 policy was rerun on the same cohort. Event effects below are conditional on the games where it was taken:

| J13 policy/position | Games taken | Old → corrected win-point change against baseline |
|---|---:|---|
| Useful British side, first | 1,417 | −15.10 → **−11.29**, corrected 95% **−14.53 to −8.10** |
| Useful British side, second | 895 | −3.46 → **−3.02**, corrected 95% **−6.68 to +0.44** |
| Deny Japan even when ineffective, first | 1,536 | Corrected **−11.07**, 95% **−14.27 to −7.94** |

Allowing the broader scope improves the trial, particularly when first, but does not produce evidence for adding J13. The second-player point estimate remains negative and its interval crosses zero. These results concern the tested target/type priorities; they do not prove every possible contextual use of J13 is bad.

**Effect on prior claims.** The old J13 row should be labeled a restricted-policy result and superseded by the corrected trial. The new test restores evidence for a negative first-player J13 estimate on this cohort. It does not retroactively make the old implementation complete. Other Event trials and released J4/J25 play do not enter this unshaded-J13 branch. The 30,000 stored level games were not all replayed in this follow-up; the unchanged baseline and unreachable-path argument are the narrower evidence for no J13 effect on them.

## F2 — The shared correction affects the reference search player

The no-effect claim must not be extended to every comparison in the report. The one-step reference search player considers British Event sides, including J13: `code/expert.py:109-131` and `refs.py`. It can therefore change even though Force 136's J4/J25 policy does not.

**Matched reproduction:** the original reference cohort, seeds **20000-20127**, six Japan policies, `ExpertGame` with `weights=None`, 768 games per version. The original engine gives **434 British wins (56.51%)**; the isolated J13 patch gives **438 (57.03%)**. Six game winners and twelve final Resistance values differ. Both still round to the printed 57% headline. The original result matches the active `refs_v103.json`/`v103_refs.log`, rather than the superseded `refs_final.json`.

**Smallest case:** seed **20038**, policy **repair**, reference `ExpertGame`, `weights=None`: the original engine ends at **Japan / Resistance 17**; the patched engine ends at **Force 136 / Resistance 20**. `single_reference_case.py` reproduces it directly. Fixed hash-seed controls 0 and 1 give the same original and corrected results.

**Impact and smallest fix:** this does not change the released Force 136 level results, but the raw reference comparison needs updating with the corrected engine. Recheck `refs.py` and the search-player/lookahead comparisons that can preview or execute J13. The latter were not rerun here. Do not describe the engine patch as leaving every v1.1 research result unchanged merely because the headline percentage rounds the same way.

## D1 — Confirmed documentation correction: settled card tips

My previous unresolved-reading language was too broad and should be corrected.

- **J2/J23:** the current simulation report still lists stacking under remaining uncertainties at `print/Force_136_v1_Sim_Report.md:244`. The official tips are on rules pages **17 and 22**. The code already permits stacking at `code/engine.py:434-443` and `:540` onward. A fixture starts every Railway with one Sabotage; J2 adds one to three distinct eligible Railways (11 markers total), and J23 adds one to two (10 total). No engine change is needed for this point.
- **J19:** the current report actually places this under the readings used, at `:234`, rather than its remaining-uncertainties sublist. The tip on rules page **21** supplies the missing authority. `engine.py:223-225` retains an anchor's own space when adjacent use is disabled, and `force136_v1.py:163` onward applies the one-anchor restriction. In the fixture, Perak and Johore are the selected anchors; Perak, Kelantan and Johore reveal, while adjacent Negri Sembilan does not. Both original and patched engines agree.

**Player impact:** no changed action or numerical result from closing these readings; the benefit is accurate provenance and fewer unnecessary ruling questions. **Smallest fix:** remove J2/J23 from the open list; cite the two card tips and J19's tip; distinguish the official one-anchor limit from the bot's first-anchor choice. Replace the blanket “no official clarification” sentence accordingly. The separate J10 rounding and Japan-policy assumptions are not resolved by these tips.

## R1 — Preferred interpretation: wider northern adjacency

Rule 1.3.6 treats a Railway as covering its whole border; 1.3.7 describes its adjacency to spaces touching that border. Read with the map endpoints, I favor including the adjoining corner Provinces:

| Railway | Current narrow model | Wider model already available as `corner=True` |
|---|---|---|
| Thailand-Kedah star | Kedah | Kedah, Perak |
| Thailand-Perak | Perak | Kedah, Perak, Kelantan |
| Thailand-Kelantan star | Kelantan | Kelantan, Perak |

**Important distinction:** the Extract example directly establishes Railway-to-Railway connection at the northern junction. The engine's `EDGES` graph already has that connection under both settings. Therefore that example alone does not prove the separate Province-to-Railway adjacency question. The wider reading is supported by the whole-border wording and map geometry; it is not an explicit named-corner ruling. I retain that interpretation label rather than calling an inferred answer an official clarification.

**Exact boundary reproduction.** Use the same empty-board fixture seed **1122001**, place a Force 136 marker and one Underground red guerrilla in Perak, and put Sabotage on every Railway except the Thailand-Kedah star. `rail_choice('Perak')` is `None` in the current narrow model and the starred Railway in the wider model. The changed memberships are in `code/engine.py:121-126`; both variants have fixtures.

**Measured impact, held separately from J13.** For current v1.1 with its existing J4/J25 policy, 6,000 matched Agent games on seeds 900000-900999 give **3,811/6,000 (63.52%) narrow** against **3,790/6,000 (63.17%) wider**: **−0.35 points**, whole-seed 95% interval **−0.75 to +0.05**. This is a small effect in this cohort and does not choose the rule for us. The report's existing 768-game sensitivity sample had a larger −1.6-point difference.

**Recommendation:** use the wider reading as the declared basis for future primary model runs, or obtain a specific ruling before treating either interpretation as certified. A change to the default should update its model description and rerun the published level/lookahead tables. These 6,000 Agent games do not certify all five levels. No default or released win-rate table was changed by this review.

## Evidence and release verdict

The evidence includes original/corrected native fixtures, the portable engine patch, the old and corrected J13 records, the 6,000 paired northern-adjacency records, exact seeds/policies and independent analysis. The 19 fixed bot regressions and the prior review's 36 Event-boundary executions still pass against the isolated engine correction. No production file was edited in the reviewed branch, and no publisher artwork is redistributed.

**Verdict:** the v1.1 J4/J25 Event rule remains supported. Keep J13 out on the evidence here. Correct the J13 research implementation, refresh its affected reference/search data, and close the settled-tip questions. Treat the published percentages as results of their declared narrow model until the railway interpretation is resolved and incorporated. This is an addendum to the paper-bot pass, not a claim that the engine or every future rule interpretation is fully certified.
