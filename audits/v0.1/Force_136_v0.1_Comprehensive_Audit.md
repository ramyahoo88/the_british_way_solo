# Force 136 v0.1 - Comprehensive audit

20 November 2026 | Human Japan, paper Force 136 bot | Audit only; the baseline was not changed

**Finding count: 5 confirmed items - 1 High and 4 Medium.** They comprise two forced strategic blunders, two incomplete decision procedures, and one printable-verifier defect. There are also two internal design ambiguities and four optional usability/strategy recommendations.

## Exact target and rules

The reviewed release is the original 18-card Force 136 v0.1, dated 20 November 2026: the 16-page combined PDF, three card sheets, two reference pages, all 32 Event decision entries, editable rules and JSON, PDF builder, 52 reference checks and the printable checker. It is a standard standalone Japanese Occupation opponent; linked campaigns, Personas and Pre-War Options are excluded. No app exists, so UI previews, Undo, reload and application-save recovery are not applicable. JSON fixtures in this audit are runnable audit positions, not Vassal or web-app saves.

The current GMT-hosted 28-page Japanese Occupation rulebook was checked against the original retailer mirror. Its bytes differ but its extracted text is identical on all 28 pages. Both columns of the rules and player aids were checked in the original layouts. I also read all 35 Event/Propaganda card faces and all four Japanese Occupation player aids from the current public Vassal module v3.1.1; the module graphics are supporting component reproductions, while GMT rules govern. Aid 4 contains transition/options/Personas: its layout was checked and its out-of-scope procedures were not applied to this standalone bot.

GMT product resources and targeted searches were checked for corrections. No separate Japanese Occupation errata sheet was located. Vassal changelog corrections are module implementation fixes and were not treated as changes to the board-game rules.

Rules: https://gmtwebsiteassets.s3.us-west-2.amazonaws.com/TheBritishWay_EnemyofMyEnemy/EomE_JapOcc_Rules.pdf

Component-source module: https://vassalengine.org/library/projects/The_British_Way_Counterinsurgency_at_the_End_of_Empire

Archive identity:

- ZIP SHA-256: eebbc7d481cf1203d5a898f6177c918d04941a07abf633164c9ad56bc2008707
- Archived combined PDF SHA-256: 9cd803e6bd0aa611a0fa9a8c4604e8e23a0dbb21b612cb9076541fca321ebf2b
- Standalone PDF SHA-256: 003d51430359b27703108775e147b8c418c4fe25ec51acd28c27c15a866b611d

The standalone and archived PDFs have different container hashes but identical extracted text and matching rendered page pixels in the transport comparison. This is not a gameplay or printing finding. The evidence ZIP contains the exact frozen source under baseline/. All source-and-line references below are relative to that ZIP.

## Checks and normal-play evidence

| Check | Direct result | Limit |
|---|---|---|
| Original reference suite | 52/52 pass; original seed 136001 retained | Helpers do not execute a complete game |
| Original printable checker | Passes the intact release | F5 proves a missing-field blind spot |
| Independent card-cell scan | All 18 cards pass in their own rectangles, all three columns | Does not validate strategic quality |
| Clean rebuild | All three PDFs match shipped ZIP bytes exactly | Reproducible output is not a rules proof |
| Published example | Six Events, setup through first Propaganda/reset; Resistance 6 matches the book | Uses published human decisions, not the bot |
| Bot desk pilot | Six normal bot turns against stated Japanese hunting; first Propaganda Resistance 6 | One disclosed Contact interpretation; not a complete game |
| Focused reproductions | F1-F4 board/dice fixtures, F5 PDF mutation; 20 independent winner boundaries | Deterministic cases, not sampled win rates |

The published example reconstruction independently checks the two-column sequence: Reprisal before Sweep, Supply before Train, stock exhaustion and same-space refresh, protected caches during Assault, multiple-marker Limited Contact, Gather before Ambush, Intel concealment, automatic recruitment and net Resistance. Its first score is 3 + 4 Intel + 1 cache + 3 majorities - 2 Resources - 2 Neutral Population - 1 Police = 6. One damaged central railway survives Reset. These interleavings are legal even though the bot deliberately uses a simpler Operation-first policy.

The normal bot pilot uses the physical example Event order J14, J27, J2, J17, J8, J21, then J33, and an exact recorded bot-deck order. Japanese play strips the Perak Camp, removes its Force 136, concentrates Troops, and uses nonfinal Propaganda Reprisal to threaten cache defense. Four of six bot turns are Events; Supply and Intel are the two primary normal-operation turns. The pilot ends the first nonfinal Propaganda at Resistance 6, two Force 136, two caches and no Camps. It is not a win, and its result is not an A/B comparison with the published example because Japanese decisions differ.

Printed navigation was counted as locations used during this desk reconstruction, not as trained-player physical timing: the Supply and Intel turns each referenced six printed locations including their card sheet, while the Event turns referenced three to five. Recurring added bookkeeping is one active card, its upright/sideways state and two bot piles. The around-one-minute ordinary-turn design target has not been measured at a physical table. Full stage-by-stage boards and reference locations are in results/desk_traces.json.

No complete three-campaign bot game, physical playtest, general automated board executor, broad exploit search or matched-seed balance comparison was completed. No win-rate percentage is reported. The evidence establishes the specific failures below and validates the scoped walkthroughs; it does not establish competitive strength.

## Confirmed findings

### F1 - High: The Event-first priority can turn a certain British win into an MPAJA win

**Category:** Strategy / terminal decision

**Player impact:** A legal final-turn Supply wins for Force 136, but the compulsory A-Event gate takes J4 instead and hands the victory to the independent MPAJA. Japan and the bot both lose. This is a reproducible tactical blunder, not a measured overall win-rate result.

**Rule / expected behavior:** Published rules 1.13, 4.2.1, 6.1, 6.2, 6.7.3 and 7.0.1; physical J4. Bot goal: a competitive Force 136 opponent that distinguishes its own victory from an MPAJA victory.

**Source:** baseline/build_force136.py:64 (J4 gate), :100 (Event before urgent needs), :101 (camp-count rescue); shipped PDF pages 1 and 9.

**Smallest useful setup:** Campaign 3, sixth regular Event already revealed, J4 current; Japan has taken Limited, so Event and Op & SA are free. Resistance 19, Zipper 18, Resources 0. Force 136 and Camps are together in Kedah, Perak and Pahang. No caches on the map; five Available. Three red guerrillas Available. Opposition is in those same three Provinces: 6 Population opposed and 10 Neutral. Police occupy only Kuala Lumpur and Johore. The complete 15-Troop / 6-Police / 14-guerrilla inventory and all positions are in fixtures/F1.json. No Intel is revealed and no capability is active.

**Exact reproduction:**

1. Confirm that the next card is necessarily final Propaganda: all six regular Events in the last campaign have appeared. This uses public deck information.
2. Follow page 1: consult J4 before the urgent camp-count rule. Three Force 136/Camp spaces make the unshaded option an A Event.
3. Execute it: Resistance increases only from 19 to the cap of 20. At final Propaganda, three automatic red recruits create no guerrilla majorities. The 10 Neutral Population deduct 2. No other score modifier applies.
4. As a counterfactual, use Contact/Supply. The reproduced legal move is Pahang to Kelantan, creating a Camp, followed by three Supplies at Kelantan, Perak and Kedah. A Contact hold followed by three Supplies also wins. Neither line uses concealed Intel.

**Expected result:** Choose an available guaranteed British-winning line over an Event that is known to lose for Britain. Forecast the final Propaganda net and the independent winner, including the Resistance cap.

**Observed result:** J4 U: 20 - 2 = 18, with Camps = Force 136 = 3: MPAJA wins. J4 S is no rescue: 19 - 2 = 17, so Japan wins. Contact/Supply: 19 + 3 caches - 2 = 20, so Britain wins. In the moving-Contact version one Camp remains against three Force 136; in the hold version none remain.

**Smallest proposed fix:** On a publicly certain final scoring turn, rank otherwise legal candidate actions by their actual post-Propaganda winner before applying Event preference. A guaranteed Force 136 win must outrank an MPAJA win or Japanese win. Reuse the existing camp-count check; do not add a recurring player track.

**Runnable evidence:** reproduce_audit.py: final_trap(); fixtures/F1.json; results/audit_results.json. Assertions require Event = MPAJA, shaded Event = Japan, both Supply variants = Force 136. Nearby Resistance 16 is a negative control: neither unshaded Event nor Supply wins.

### F2 - Medium: J26 is an A Event even when its only reward is lost at the Resistance cap

**Category:** Strategy / no-effect Event

**Player impact:** The bot exposes an underground guerrilla while gaining no Resistance and moving no Japanese unit. The ordinary Ambush available on its own card instead removes the local Troop threat with certainty.

**Rule / expected behavior:** Published rules 1.13, 2.4.5 and 3.2.4; physical J26 replaces Troop movement with its Resistance reward. The bot itself defines useful actions on PDF page 2.

**Source:** baseline/build_force136.py:86 (J26 chance-only gate), :100 (A Event first), :106 (usefulness), :132 (normal STRIKE); shipped PDF pages 1, 2, 5 and 11.

**Smallest useful setup:** Campaign 2, Resistance 20, current J26, active bot card 13. Japan has already taken Limited. Negri Sembilan has one Troop, one underground red guerrilla, one Force 136 and one cache; no Police, Kempeitai or Camp. The cache gives +1 against one cube. All other pieces are accounted for in fixtures/F2.json. The Kill Traitors icon has no eligible target.

**Exact reproduction:**

1. Read J26: all six die faces succeed, so the printed gate rates it A.
2. Take Event and roll 1: modified 2 beats the one cube. Activate the guerrilla. Apply the Event reward in place of displacement.
3. For a nearby counterfactual, take ordinary STRIKE using Op & SA without a Special Activity. The same die displaces the Troop to Kuala Lumpur.
4. On a following ordinary J3, with no eligible Mobilize icon effect, Japan is first after its prior Limited. It can Assault the exposed guerrilla in the Event branch. It cannot Assault Negri Sembilan in the ordinary-Ambush branch because no Troop remains there.

**Expected result:** At the cap, do not rate a reward-only Event as a positive A Event unless an explicit denial benefit justifies spending the turn. Here Japan has already acted, so there is no such benefit.

**Observed result:** Event branch: Resistance stays 20, the Troop stays, and the guerrilla becomes Active. Ordinary Ambush: Resistance also stays 20, but the Troop leaves. The next Japanese Assault can remove the exposed guerrilla only in the Event branch.

**Smallest proposed fix:** Add an actual-gain condition to the J26 gate: require min(20, Resistance + 2) > Resistance. If Event denial is desired, express it separately rather than treating a capped reward as useful. Apply the same cap-aware review to J4.

**Runnable evidence:** reproduce_audit.py: cap_trap(); fixtures/F2.json. Success faces are 1-6; actual Event gain is 0. Nearby control at Resistance 18 produces a real gain of 2.

### F3 - Medium: Ordinary Operation planning does not pin down post-operation Special Activity usefulness

**Category:** Decision procedure / interpretation-dependent tempo loss

**Player impact:** A current-board reading chooses Op & SA for a Gather that Sabotage itself makes impossible. Britain makes the same Sabotage attacks it could make under Limited, but yields first eligibility without a Special Activity. A reader who forecasts the activation may avoid the mistake; the two readings are not distinguished in the printed procedure.

**Rule / expected behavior:** Published rules 2.4.4, 2.4.5, 3.2.3 and 4.2.2; British player-aid columns. Limited British Sabotage may use multiple Force 136 spaces. Ordinary Gather still needs underground guerrillas.

**Source:** baseline/build_force136.py:107 (box choice), :108 (Operation before Special Activity), :129 (recheck after Operation); baseline/reference_checks.py:49 and :52. Shipped PDF pages 2 and 4.

**Smallest useful setup:** Bot card 09; Britain first. All three boxes are free; current J31 has no useful Event because Resources = 0. Kedah, Perak and Negri Sembilan each have one Force 136 and exactly one underground red guerrilla. No other guerrilla and no cache is on the map. All relevant Intel is concealed and three distinct legal railway attacks exist. J31 Mobilize has already placed Opposition in Perak.

**Exact reproduction:**

1. Evaluate the current board: GATHER, first in the card's Special Activity order, has legal concealed Intel opportunities.
2. The current-board call to the shipped helper selects Op & SA. Perform all three Sabotage attacks, activating all three guerrillas.
3. Recheck Gather as page 4 instructs: no underground guerrilla remains. Raid is also unavailable. Omit the Special Activity.
4. Repeat the same three attacks under Limited: Britain retains first eligibility. As a nearby positive control, add one underground guerrilla in Kelantan; it can survive the attacks and Gather via Perak, making Op & SA useful.

**Expected result:** Specify whether usefulness is evaluated before or after the selected Operation. A deterministic paper bot should not require the player to infer a forecast rule that is explicitly stated only for primary Special Activity tasks.

**Observed result:** The reproducible current-board branch chooses Op & SA and performs no Special Activity. The forecast branch chooses Limited and gets identical Sabotage with better next eligibility. Both readings fit portions of the present prose.

**Smallest proposed fix:** Replace the box test with: choose Op & SA only if a compatible useful Special Activity remains possible after the planned Operation and its compulsory activations. Otherwise prefer Limited. This preserves the existing Operation-first timing.

**Runnable evidence:** reproduce_audit.py: initiative_trap(); fixtures/F3.json. This is a confirmed specification gap and bad allowed branch, not an assertion that every reader or a non-existent app always chooses it.

### F4 - Medium: Ambush and Gather lack the guerrilla-color tie-break supplied for Sabotage

**Category:** Decision procedure / unresolved actor choice

**Player impact:** Two players following the paper bot can produce different board states from the same position. The difference changes which color is exposed, lost or remains recruitable; it is not merely cosmetic.

**Rule / expected behavior:** Published rules 3.1, 3.2.4, 4.2.2 and 5.4; physical J6. The executing faction chooses the friendly piece used, so a solo procedure needs to supply that choice.

**Source:** baseline/build_force136.py:132 (STRIKE), :125 (Gather), :127 (red-before-blue exists only for RAIL); shipped PDF pages 4 and 5. The forced-loss preference at :112 does not select an actor for an action.

**Smallest useful setup:** Negri Sembilan: one Troop, one Police, one underground red and one underground blue guerrilla, Force 136, Camp and cache. No Kempeitai. Bot card 13; Japan has already taken Op & SA, so the bot uses Limited Ambush. Current J17 Seize has no eligible target because the cache already shares a space with a Camp. All other pieces are in fixtures/F4.json.

**Exact reproduction:**

1. Follow STRIKE: remove the Police. An underground guerrilla must be activated, but STRIKE supplies no red/blue choice.
2. Branch A activates red; branch B activates blue. Space tie-breaks cannot distinguish two pieces in the same space.
3. For a prescribed referee continuation, reveal J6 next. Food Shortage has no target: the only red guerrilla is cache-protected. Roll 1 for Negri Sembilan. Under the bot's loss priority, remove the Active guerrilla before the underground one. Japan also resolves its own loss; that does not change the British color comparison.

**Expected result:** One deterministic actor choice, expressed in the paper rules, without borrowing a priority explicitly limited to a different action.

**Observed result:** Both Ambush branches are legal, but after the same attrition one leaves blue and the other leaves red. Gather has the same missing actor tie when both underground colors occupy one eligible Intel space. A single-color position is the nearby unambiguous control.

**Smallest proposed fix:** Add a global activation rule, for example: when either color is equally legal, activate an underground red guerrilla before blue, unless the effect specifically requires one color or a moved Raid participant. Apply it explicitly to Ambush and Gather.

**Runnable evidence:** reproduce_audit.py: actor_gap(); fixtures/F4.json. Both branches and the correctly ordered MPAJA icon/mandatory effect are recorded in results/audit_results.json.

### F5 - Medium: The print checker accepts a card with its Special Activity order deleted

**Category:** Verification / printable integrity

**Player impact:** The current shipped card is intact. The defect is in the release guard: a future card can lose required instructions while the checker still claims all 18 cards match.

**Rule / expected behavior:** Expected release behavior: each field on each individual bot card must match its own source row. Text on a different card cannot satisfy the check.

**Source:** baseline/verify_printables.py:40 (page-wide text), :46 (membership check). Witness: card 09, combined PDF page 15, top-right cell; separate card PDF page 2.

**Smallest useful setup:** Make an isolated copy of the unmodified shipped ZIP contents. Leave bot_data.json unchanged. Card 09 and card 11 share the text GATHER > RAID on the same sheet.

**Exact reproduction:**

1. In the copy only, remove the GATHER > RAID field from card 09 in both the combined and separate PDFs.
2. Run the unmodified shipped verify_printables.py. The two mutated PDFs still match each other, and card 11 still supplies the missing phrase to the page-wide search.
3. Independently read only card 09's rectangle: x 396-576, y 167-419 PDF points. Its required field is missing.

**Expected result:** The original checker must fail the mutant while continuing to pass the intact release.

**Observed result:** The shipped checker exits 0 and reports cards_matched = 18. The independent card-09 clip check fails. The untouched baseline passes an independent per-card check for every field across all three columns.

**Smallest proposed fix:** Find the six card rectangles on each sheet and validate every card's ID, title, primary text, preparation order, Special Activity order, region and Event flag inside its own rectangle. Keep the separate-versus-combined pixel comparison as an additional check.

**Runnable evidence:** reproduce_audit.py: mutation_test(); results/mutant_verifier_stdout.txt and results/strict_card_cells.json. The mutant is created under mutated_card09; no delivered v0.1 file is changed.

## Ambiguous rulings / design choices

These are internal bot design decisions, not claims that GMT rules are wrong.

### Q1 - Event completion and card aging (internal bot design)

A fresh SUPPLY card takes J25 U and completes Contact/Supply inside the Event. Page 1 says discard when the primary task was attempted, but also retain a card when an Event used the turn instead. The helper treats EVENT as different from SUPPLY. Source: baseline/build_force136.py:103 and :85; baseline/reference_checks.py:71 and :219. Decide which branch governs. Smallest wording consistent with the existing helper: an Event ages the active card once and never completes its printed primary task, even if it includes a matching free action. This is a design decision, not an unresolved GMT ruling.

### Q2 - Contact hold versus expansion (internal bot design)

INTEL says Contact may hold when current positions already allow a useful Gather; generic Contact prefers placing an Available marker and then moving. With two productive on-map markers and a third Available, one reader holds and another expands. Source: baseline/build_force136.py:115 and :125, PDF pages 3-4. Smallest proposed resolution: INTEL holds if current anchors already yield useful Gather; otherwise use normal placement/movement priorities. The six-Event hunting desk trace states and uses the hold interpretation. Neither interpretation is a publisher-rule violation.

## Optional usability and strategy improvements

### U1 - Put regional priorities in one comparison table

Replace the three long rail-name chains with eight rows and N/C/S rank columns. Include the live-route preference once above it. This changes no target priority and reduces repeated visual searching. All eight rails and four starred exits were checked against the map.

### U2 - Add global reminders on the bot cards

A short line saying check Event and urgent needs first, plus the relevant procedure page, would reduce dependence on remembering page 1. Keep the existing upright/sideways two-turn state; do not add a recurring track.

### U3 - Treat declined B Events and D denial as a focused experiment

J14 can qualify only as B on a B-NO card; its current otherwise-D condition is then not reconsidered, leaving Japan the permanent-cache-removal option. Re-evaluate D after the B-card filter if defense is intended. This is an optional strategy change, not a proven always-better fix: denying an Event spends a turn and can forgo a stronger Operation. Compare the actual board trade-off before making D universal.

### U4 - Target the next usability test at cache defense and live-rail tracing

The hunting pilot ends its first Propaganda with two caches under Japanese Troops and no guerrillas after the Japanese free Reprisal. That exposes a useful playtest target, not a demonstrated dominant strategy. Test whether guard commitments survive the known nonfinal Propaganda response. Separately time the live-route lookup on real pieces; do not turn it into a second network-management game.

## Strategy challenges and information limits

| Challenge | Reproduced result | What it does not establish |
|---|---|---|
| Neutral-Population defense at the end | F1: an A Event gives MPAJA the win; legal Supply guarantees Britain the win | Frequency in natural games |
| Hunting exposed resistance | F2 and the six-Event pilot: a capped Event exposes a guerrilla; Camp stripping and removal reduce the network | A dominant hunting strategy |
| Initiative and extraction opportunities | F3: ordinary Sabotage can needlessly hand Japan first eligibility | A perpetual denial loop or quantified score margin |
| Mixed-group attrition | F4: identical dice can leave different colored survivors under the incomplete actor rule | Which color priority is strongest in every position |

The final-turn fixture uses a publicly certain last Propaganda, not knowledge of an unseen card. Concealed Intel values are absent from bot selection. In the desk traces the referee uses the published example Intel assignment, while the bot targets only concealed/revealed status and legal public geometry. The F4 next-card continuation is a prescribed referee test, not information the bot uses. Stock accounting includes all 15 Troops, six Police or their Available balance, ten red and four blue guerrillas, all three Kempeitai, all three Force 136, four Camps, and five caches including any on Zipper.

Correct boundaries rechecked include strict camp-count ties at Resistance 18-19, no normal early victory, J9 final scoring before either normal turn, Mandatory Event box closure even when its effect is empty, marker-versus-force distinction, compatible Special Activities, ordinary Sabotage versus Event stacking, cache protection by underground guerrillas, nonfinal Supply after scoring, and persistent Sabotage on Reset. Not all of these have a full general executor; the report distinguishes the original checks, independent score assertions and desk reconstructions.

## Reproducing the audit

Extract the evidence ZIP. With Python and PyMuPDF, run:

```text
python3 reproduce_audit.py
python3 desk_traces.py
python3 baseline/reference_checks.py
python3 baseline/verify_printables.py
```

Without PyMuPDF, the four board cases and independent score checks can run with python3 reproduce_audit.py --skip-pdf-mutation. The PDF mutation requires PyMuPDF. Rebuilding the original PDFs additionally requires ReportLab and DejaVu Sans. The frozen baseline is preserved; the mutation script creates a disposable mutated_card09 copy. Do not print the deliberate mutant as a game component.

Evidence includes full F1-F4 JSON positions, the independent score oracle, the mutant detector, original and independent check receipts, clean-rebuild hashes, strict card-cell results, source/component hashes and both desk reconstructions. Official rulebook pages, player-aid art and Event art are linked and hashed rather than redistributed.

## Fix order and release verdict

1. Correct the final-scoring Event choice in F1 and capped J26 reward in F2.
2. Make post-Operation Special Activity usefulness and colored-actor selection explicit (F3-F4); settle Q1-Q2 at the same time.
3. Validate every card field inside its own rectangle (F5), with the deletion mutant as a regression test.
4. Run complete three-campaign games using extraction, hunting, adaptive repair and mixed strategies. Add adversarial repeated play only after the rules and paper decisions are settled. Measure physical administration before adding more bot machinery.

**Release verdict: HOLD v0.1 for a competitive public release.** The package is reproducible and the shipped print content is intact: 52 checks pass, all 18 cards match independently, and all three PDFs rebuild exactly. However, F1 proves a forced choice that throws away a guaranteed British win, F2 proves a no-reward action that exposes a guerrilla, F3-F4 leave material decisions to interpretation, and F5 weakens the print gate. Keep v0.1 as a development prototype until those items are corrected and complete-game validation supports a stronger claim.
