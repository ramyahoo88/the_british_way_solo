# The British Way Solo

**Force 136** is an unofficial, card-driven paper opponent for the standard
standalone **Japanese Occupation** scenario in **The British Way: Enemy of My
Enemy**. The human plays Japan; Force 136 is the British opponent, and the MPAJA
remains the published independent actor.

The physical base game, expansion, Event cards and player aids are required.
The bot runs at the table without an application.

## Force 136 v1.0 (new design, branch `claude-force136`)

A new card-driven British bot built from scratch, with its own print-and-play package, rules-as-code and a simulation study: see [force136_v1/](force136_v1/README.md). Holdout simulations against six computer Japan policies: Recruit 36%, Agent 61%, Veteran 71%, Legend 79% Force 136 wins (v0.2: 0%). Not yet playtested at the table.

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
established. The latest simulation study recommends further priority changes;
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

[SHA-256 file manifest](FILE_MANIFEST_SHA256.json) identifies the uploaded
artifacts. The ZIP packages contain the source and their reproduction commands.

The underlying rules are GMT Games' [Japanese Occupation rulebook](https://gmtwebsiteassets.s3.us-west-2.amazonaws.com/TheBritishWay_EnemyofMyEnemy/EomE_JapOcc_Rules.pdf).
This is an independent fan variant, not a GMT publication. Publisher rulebooks,
Event artwork and maps are not included here.
