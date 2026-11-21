# Force 136 v0.2 - simulation findings

20 November 2026 | Human Japan | Standard standalone Japanese Occupation

**Verdict: hold a competitive public release.** The study found two concrete
paper-policy weaknesses and a broader Event-priority problem. Prioritizing
primary tasks improves results in this development model, but even the better
candidate wins too rarely against the tested active Japanese policies to support
a competitive claim. The paper v0.2 release was preserved.

## What was simulated

There were **2,176 study runs through the complete campaign sequence in a new
development executor**, plus 128 separate validation runs checking 384 scoring
points. These are computer-model results, not physical playtests or measured
real-player win rates. Every counted run reached final Propaganda or J9; no
unfinished run was counted as a loss. Initial exploratory passes, unit-test
games and an aborted technical run are excluded from those totals.

| Batch | Seeds | Policies and variants | Runs |
|---|---|---|---:|
| Discovery | 136300-136331 | Four Japanese policies; six bot policies | 768 |
| Fresh confirmation | 136900-136963 | Four policies; baseline, primary_first, primary_guard | 768 |
| Railway sensitivity | 137300-137331 | Four policies; baseline/candidate; two adjacency readings | 512 |
| Weak/repetitive controls | 137100-137131 | Two regular-turn controls; baseline/candidate | 128 |
| Separate score validation | 137500-137515 | Four policies; baseline/candidate | 128 additional |

Matched seeds share Event deals, Intel shuffle streams, bot-deck shuffle streams
and dice keyed to action/space/draw. The selectors do not inspect future cards
or concealed Intel. Four deterministic Japanese heuristics emphasize resource
extraction, hunting Force 136, repairing railways, or adaptive suppression.
They search legal one-step candidates, including Reprisal before Assault; they
are not calibrated human players or an optimal opponent.

The target is Force 136 v0.2, 20 November 2026, input ZIP SHA-256
639e7eb7418a5784889fa8cc1b1b17acd8797138d18fe285e9b41d5c1c2a7ce1.
The official reference is the 28-page GMT Japanese Occupation rulebook,
copyright 2026. The prior audit checked its original layouts and component
faces; no publisher-rule change or difficulty bonus was introduced here.

## Fresh-seed comparison

Each cell shows British wins / 64 and mean final Resistance. MPAJA wins are
losses for both players and are counted separately below.

| Japanese policy | Released v0.2 model | Primary first | Primary + recovery/guard |
|---|---|---|---|
| Extraction | 0/64; R 1.34 | 1/64; R 7.02 | 1/64; R 6.88 |
| Hunting | 0/64; R 1.30 | 1/64; R 5.81 | 2/64; R 6.12 |
| Repair | 0/64; R 1.61 | 2/64; R 5.94 | 5/64; R 6.70 |
| Adaptive | 0/64; R 1.41 | 2/64; R 4.97 | 1/64; R 4.97 |

Across the 256 fresh-seed policy cases, the winner counts were:

| Bot policy | Britain | MPAJA | Japan | Mean Resistance |
|---|---:|---:|---:|---:|
| Baseline | 0 | 0 | 256 | 1.41 |
| Primary first | 6 | 1 | 249 | 5.93 |
| Primary + recovery/guard | 9 | 2 | 245 | 6.17 |

Primary first improved final Resistance by **4.52**
[95% paired seed-cluster interval 3.48, 5.67].
The recovery/guard bundle improved it by **4.75**
[3.80, 5.78] over baseline.
Adding guards/recovery to primary first alone changed Resistance by only
0.23 [-0.44, 0.89];
that extra scoring benefit is not established.

The observed British-win improvements over baseline were 2.34 percentage points
[0.00, 6.25] for primary first and 3.52 [0.78, 7.81] for the bundle. The difference
between those candidates was 1.17 [-0.39, 3.13]. These intervals resample the 64
matched seed clusters, retaining their four policy cases together. They quantify
random-deal uncertainty within this model, not transcription error, human skill,
or real tabletop win rates. Zero observed baseline wins does not prove zero
chance of winning.

## S2 - confirmed behavior: a capability Event sacrifices two defendable caches

**Player impact.** Japan can remove two caches in one ordinary Assault while the
bot forgoes the Train already printed on its active card. This is a strategic
priority weakness, not an illegal execution of the current bot instructions.

**Rules and goal.** British Train at a cache can place two guerrillas (3.2.1).
Assault cannot remove a cache while any guerrilla remains underground (3.3.4).
A normal Reprisal displaces only one guerrilla per selected space (4.3.2).
The design goal is to defend useful infrastructure when a legal action prevents
its immediate loss. The current Event-before-task instruction causes the choice.

**Smallest useful public setup.** Seed 136300, adaptive Japan, draw 3, campaign 1,
current J22 after its icon, active bot card 15 TRAIN, fresh. Britain is first and
all boxes are free. Resistance 2, Resources 8, Zipper 0. Both threatened spaces
have a cache, Force 136, one Kempeitai, two Troops and one Police. Kedah has one
active blue guerrilla; Negri Sembilan has one active red. Four red and two blue
are Available. The full legal board, other forces and pools are in fixtures/S2.json.

**Exact reproduction.** Apply the paper's A-Event gate: take J22 U. This leaves
both lone guards Active. Japan selects Op & SA, Assaults Kedah and Negri
Sembilan, and uses each space's two Troops to remove its active guerrilla and
then its cache. The modeled Japanese plan also uses Eliminate afterward; no
die result is required for either cache loss. The opening deal is J25, J8, J22;
the preceding public actions are preserved in results/S2_full_trace.json.

**Expected alternative / observed counterfactual.** Limited Train adds two blue
underground in Kedah and two red underground in Negri Sembilan. Each then has
two underground and one active guard. Even a targeted Reprisal before Assault
leaves an underground guard at each cache, so both survive that immediate
operation/activity combination. The runnable witness explicitly targets both
caches with the counterfactual Reprisals. It does not claim safety forever or
against every future Event that directly removes a cache.

**Source and smallest proposed fix.** baseline/build_force136.py:102;
baseline/build_force136.py:121;
model/engine.py:958.
Before an ordinary Event, check a Force 136 cache under Troops with fewer than
two guerrillas. If Train can add guards, Train first; prefer Limited and avoid
immediately Raiding those defenders away. The experimental cache_guard policy
implements this bounded check. Nearby control: a cache with two underground
guerrillas needs no such emergency override, and an underground guard already
prevents an immediate ordinary Assault from removing the cache.

## S1 - confirmed behavior: Events override the existing network-recovery rule

**Player impact.** The bot can spend its turn on another Event while having no
Force 136 on the map, postponing the markers required for its normal network.
The Event may still have a useful effect; this finding does not call every such
turn completely wasted.

**Rules and goal.** Contact may place an Available Force 136 (3.2.2), and v0.2
already lists no-Force recovery as urgent. Its Event step precedes that urgent
step. Training, normal attacks and most intelligence activity depend on the
network, so recovery timing matters.

**Setup and steps.** Seed 136302, adaptive Japan, campaign 3, draw 14, J14 after
the icon; fresh card 04 SUPPLY. Resistance 0, Resources 0, Zipper 0. No Force 136
is on the map; all three are Available. Japan has taken Op & SA, leaving Limited
and Event. Three caches remain; there are no Camps, no Available caches, three
Available red and one blue. Follow the A-Event gate: J14 U is selected and ends
with zero Force 136. The ordinary urgent route can instead use Limited Contact
in Johore, producing one Force 136 and a Camp. Full board: fixtures/S1.json.
No hidden value or favorable roll is needed for that recovery.

**Expected versus observed.** A productive recovery action exists, but the Event
priority postpones it. This is a confirmed conflict between the stated urgent
objective and its priority, not a GMT violation or proof that the Event always
has lower long-term value.

**Source and smallest proposed fix.**
baseline/build_force136.py:102 and
baseline/build_force136.py:103.
Move the existing zero-Force recovery check ahead of unrelated Events, retaining
an accepted Event that itself restores Force 136, such as J16, J25 or J28 when
applicable. The recovery_first experiment eliminated measured no-recovery turns,
but by itself did not consistently improve scores. Keep that limitation attached
to the recommendation. Counter-control: do not replace a useful restoring Event
with a weaker single-marker Contact automatically.

## Conditional finding: the bot follows too many Events to sustain its card plan

In the fresh baseline sample, Events consumed 54.5% of normal
British turns. Only 25.3% used the normal primary-task route,
and the bot revealed an average 5.68 chits over the entire game.
The two-turn card lifetime continues to expire on Event turns, so a card can
leave play without performing the operation it was meant to drive. That aging
is intentional under the resolved Q1 rule; the simulation finding concerns
its interaction with an obligatory Event-first preference.

**Proposed experiment.** When the normal route reaches a useful printed primary,
try that task before an ordinary A/B Event. Preserve the known-final scoring
safeguard and the existing urgent-route treatment. This is primary_first in the
code. It reduced Event turns to 23.7%, increased normal primary-route
turns to 52.3%, and increased reveals to
9.56. It is the strongest simple scoring improvement tested,
but its low win count does not establish a competitively adequate design.

Source: baseline/build_force136.py:105,
model/engine.py:805 and model/engine.py:958.
This is an experimental policy finding supported by matched outcomes, not a
third confirmed rules defect. Do not solve it merely by increasing bot resources
or adding extra actions; neither was tested here.

## Which changes are supported

The discovery pass used the same 32 seeds for every candidate and every policy.
These runs selected candidates; fresh confirmation supplies the main comparison.

| Discovery policy | British wins | Mean final Resistance |
|---|---:|---:|
| baseline | 0/128 | 2.01 |
| recovery_first | 0/128 | 2.02 |
| cache_guard | 0/128 | 2.33 |
| late_intel | 1/128 | 2.85 |
| primary_first | 3/128 | 5.89 |
| combined | 0/128 | 3.52 |

The recovery/guard/late-Intel bundle was not the best performer. I would not
adopt every added priority simply because each sounds useful. First try the
primary/Event reorder. Retain the local cache defense repair and network-recovery
clarification, while checking their cost in full tabletop games.

The primary + recovery/guard candidate reduced unguarded-cache turn exposures
from 5.06 to
3.70 per modeled game;
the matched difference was -1.36
[-2.09, -0.59].
This metric counts an unguarded cache at the end of a bot turn, including one
seen on several turns. It is not a count of distinct caches or proven losses.
Actual cache losses to Assault also fell from 2.12
to 1.78 per game in the model.

## Strategy and interpretation checks

The bot beat the control taking no normal Japanese action in 32/32 cases under
both policies. Those controls still made the normal Japanese free choices during
nonfinal Propaganda. Against the repetitive regular-turn Deploy/Extract control,
baseline Britain won 20/32; Japan won 9 and MPAJA 3. The candidate won 30/32,
with one Japanese and one MPAJA win. This is evidence against treating extraction
spam itself as a proven dominant exploit. The active heuristic policies were
much stronger than that repetitive control.

The matched railway sensitivity used two readings of northern corner contacts,
with the same 32 fresh seeds per reading. Baseline mean Resistance was 1.30 under
border-sharing adjacency and 1.27 with added corners; the candidate's was 6.19
and 6.72. The priority improvement remained in both readings. This bounds one
map assumption; it does not settle an official ruling or validate every target.

## Validation, gaps and reproduction

The new model passes 35 focused checks: setup and stock, deck construction,
Event-effect stocks, capabilities, the earlier audit boards, actor colors,
Raid donor reservation, final-phase stopping and limited-information checks.
Its scorer reproduces Resistance 6 from the published example's pre-Propaganda
board. This is a scoring-snapshot test, not an independent implementation of
every action in that example. Independent post-recruitment arithmetic matched
all 384 scoring points in 128 additional model runs.

The model includes all normal operations, Special Activities, 32 Event effects,
MPAJA icons, six capabilities, Zipper, all three campaigns and J9. Nevertheless,
it is a new transcription. Several paper target choices require bounded
interpretations, Japanese strategy is one-step heuristic play, and the model
has not had an independent line-by-line audit. Its rare win percentages must not
be advertised as physical-game balance. No physical administration, fun or
human adaptation was measured. MODEL_SCOPE.md gives the exact assumptions.

Reproduce from the evidence package:

```text
python3 model/validate_engine.py
python3 model/behavior_witnesses.py
python3 model/replay.py --seed 136300 --policy adaptive --variant baseline --output trace.json
python3 model/run_study.py --start 136900 --n 64 --name confirmation --variants baseline,primary_first,primary_guard
python3 model/analyze.py
```

README.md contains every batch command. The package includes complete public
S1/S2 positions, two end-to-end traces, all 2,176 outcome rows, paired statistics,
source identities and the frozen v0.2 rules. These JSON positions are research
fixtures, not importable Vassal saves. The official rulebook and artwork are
linked and hashed rather than redistributed.

Rules: https://gmtwebsiteassets.s3.us-west-2.amazonaws.com/TheBritishWay_EnemyofMyEnemy/EomE_JapOcc_Rules.pdf

**Next priorities and release verdict.** Prepare a paper v0.3 candidate with the
primary/Event priority change, the narrow cache-defense check and recovery
clarification. Keep these changes separate from untested bonuses or a larger
bot deck. Independently audit the model, then play complete tabletop games
against extraction, hunting, repair and mixed plans, recording guard losses and
lookup time. **Hold the competitive-release claim: the confirmed local decisions
need correction, and the tested improvements still produce few British wins
against the active policies in this development model.**
