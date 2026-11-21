# The British Way Solo

**Force 136** is an unofficial, card-driven paper opponent for the standard
standalone **Japanese Occupation** scenario in **The British Way: Enemy of My
Enemy**. The human plays Japan; Force 136 is the British opponent, and the MPAJA
remains the published independent actor.

The physical base game, expansion, Event cards and player aids are required.
The bot runs at the table without an application.

## Force 136 v1.0.3 (new design, branch `claude-force136`)

A new card-driven British bot built from scratch, with its own print-and-play package, rules-as-code and a simulation study: see [force136_v1/](force136_v1/README.md). Version 1.0.3, simulated against six computer Japan policies: Recruit 39%, Agent 61%, Veteran 71%, Legend 79%, Mastermind 89% Force 136 wins (v0.2: 0%). Not yet playtested at the table.

v1.0.3 follows a [full audit of v1.0.2](audits/v1.0.2/Force_136_v1.0.2_Audit_338cb0d.md) ([PDF](audits/v1.0.2/Force_136_v1.0.2_Audit_338cb0d.pdf)). The audit found the bot's play legal and consistent, but the computer Japan too kind in two places; correcting it lowered the win rates by about 3 points.

## Reviews of Claude's redesign

These reviews examine the versions on the
[`claude-force136` branch](https://github.com/ramyahoo88/the_british_way_solo/tree/claude-force136).
Each report is tied to the exact commit shown below.

| Reviewed version | PDF | Readable report | Reproduction evidence |
|---|---|---|---|
| [v1.0, `615c870`](https://github.com/ramyahoo88/the_british_way_solo/commit/615c870cf018a5122b3991b00dfbbd4224d04e42) | [Review PDF](audits/v1.0/Force_136_v1_Claude_Review.pdf) | [Markdown](audits/v1.0/Force_136_v1_Claude_Review.md) | [Evidence ZIP](audits/v1.0/Force_136_v1_Claude_Review_Evidence.zip) |
| [v1.0.1, `fe57c0f`](https://github.com/ramyahoo88/the_british_way_solo/commit/fe57c0faea60bc913e1f7c859963059d92d9aa7e) | [Re-audit PDF](audits/v1.0.1/Force_136_v1.0.1_Reaudit.pdf) | [Markdown](audits/v1.0.1/Force_136_v1.0.1_Reaudit.md) | [Evidence ZIP](audits/v1.0.1/Force_136_v1.0.1_Evidence.zip) |
| [v1.0.1, `33745a6`](https://github.com/ramyahoo88/the_british_way_solo/commit/33745a6cad5d89f81b3118806b14eec291bec72a) | [Comprehensive audit PDF](audits/v1.0.1/Force_136_v1.0.1_Comprehensive_Audit_33745a6.pdf) | [Markdown](audits/v1.0.1/Force_136_v1.0.1_Comprehensive_Audit_33745a6.md) | [Evidence ZIP](audits/v1.0.1/Force_136_v1.0.1_Audit_33745a6_Evidence.zip) |

The latest comprehensive audit examines commit `33745a6`, after the earlier
reporting and checker-command corrections. It identifies five remaining issues:
stacked-marker Redeploy, the printed J27 condition, two mislabeled exploit
policies, the exploit sample-size caption, and conflicting Pass wording. It
includes 4,736 fresh strategy games and recommends those corrections before
release. The earlier re-audit independently supports the last-resort Train
refresh. Each report includes reproductions, source references, checks,
simulation limits and a release verdict.

## v0.2 print package (GPT draft)

| File | Contents |
|---|---|
| [Complete guide and cards](downloads/v0.2/Force_136_Solo_v0.2.pdf) | 17-page combined print package |
| [Print-and-play source package](downloads/v0.2/Force_136_Print_and_Play_v0.2.zip) | Separate printables, editable source, checks and audit response |
| [Cards](downloads/v0.2/Force_136_Cards_v0.2.pdf) | Three sheets; 18 poker-size cards |
| [Reference sheets](downloads/v0.2/Force_136_Reference_v0.2.pdf) | Quick reference, railway ranks and record sheet |
| [Rules in Markdown](docs/v0.2/Force_136_Rules_v0.2.md) | Readable rules, Event policies and deck data |
| [Changes](docs/v0.2/CHANGELOG.md) | v0.2 changes |
| [Response to the v0.1 audit](docs/v0.2/AUDIT_RESPONSE_v0.1.md) | Finding-by-finding fixes and validation limits |

Print cards at actual size / 100%, single sided. Reprint both rules and cards
when moving from v0.1 to v0.2.

**Status:** a paper playtesting prototype. Competitive strength has not been
established. The v0.2 simulation study recommends further priority changes;
its experimental policies have not been installed into the v0.2 print package.

## Simulation study

| File | Contents |
|---|---|
| [Simulation report PDF](simulations/v0.2/Force_136_v0.2_Simulation_Report.pdf) | Findings, matched-seed comparisons and release verdict |
| [Simulation report in Markdown](simulations/v0.2/Force_136_v0.2_Simulation_Report.md) | Readable report text |
| [Simulation evidence and code](simulations/v0.2/Force_136_v0.2_Simulation_Evidence.zip) | Research executor, 2,176 study outcomes, validation, public positions and traces |

The study found two reproducible behavior weaknesses and a broader Event-priority
problem. The numerical results are conditional on a new development model and
its Japanese heuristics; they are not measured tabletop win rates.

## Earlier audit and release

| File | Contents |
|---|---|
| [v0.1 audit PDF](audits/v0.1/Force_136_v0.1_Comprehensive_Audit.pdf) | Comprehensive audit of the initial prototype |
| [v0.1 audit in Markdown](audits/v0.1/Force_136_v0.1_Comprehensive_Audit.md) | Readable audit text |
| [v0.1 audit evidence](audits/v0.1/Force_136_v0.1_Audit_Evidence.zip) | Frozen baseline, reproductions and check receipts |
| [v0.1 combined PDF](archive/v0.1/Force_136_Solo_v0.1.pdf) | Historical guide and cards |
| [v0.1 print-and-play package](archive/v0.1/Force_136_Print_and_Play_v0.1.zip) | Historical source and printables |

The v0.2 audit response corrects the earlier audit's final-Propaganda timing
explanation: six Events in a campaign alone do not prove Propaganda is next.
The historical documents are preserved as originally delivered.

## Verification and sources

[SHA-256 file manifest](FILE_MANIFEST_SHA256.json) lists every file on this
branch except the manifest itself; `force136_v1/code/make_manifest.py` regenerates it. The ZIP packages contain the source and their reproduction commands.

The underlying rules are GMT Games' [Japanese Occupation rulebook](https://gmtwebsiteassets.s3.us-west-2.amazonaws.com/TheBritishWay_EnemyofMyEnemy/EomE_JapOcc_Rules.pdf).
This is an independent fan variant, not a GMT publication. Publisher rulebooks,
Event artwork and maps are not included here.
