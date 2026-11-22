# The British Way Solo

**Force 136** is an unofficial, card-driven paper opponent for the standard
standalone **Japanese Occupation** scenario in **The British Way: Enemy of My
Enemy**. The human plays Japan; Force 136 is the British opponent, and the MPAJA
remains the published independent actor.

The physical base game, expansion, Event cards and player aids are required.
The bot runs at the table without an application.


## Digital Directive deck

[Open Force 136 on Solo Table](https://solo-table.pages.dev/games/force136/) or
[download the offline app](https://solo-table.pages.dev/downloads/force136).
The optional companion draws the nine Directives, provides the v1.1 rules and
reference, and keeps deck saves, Undo and notes. Play Japan on your physical
board using your official Event cards, pieces and player aids.

[App source, build instructions and validation](web/force136/README.md)

## Reviews of Claude's redesign

These reviews examine the versions on the
[`claude-force136` branch](https://github.com/ramyahoo88/the_british_way_solo/tree/claude-force136).
Each report is tied to the exact commit shown below.

| Reviewed version | PDF | Readable report | Reproduction evidence |
|---|---|---|---|
| [v1.0, `615c870`](https://github.com/ramyahoo88/the_british_way_solo/commit/615c870cf018a5122b3991b00dfbbd4224d04e42) | [Review PDF](audits/v1.0/Force_136_v1_Claude_Review.pdf) | [Markdown](audits/v1.0/Force_136_v1_Claude_Review.md) | [Evidence ZIP](audits/v1.0/Force_136_v1_Claude_Review_Evidence.zip) |
| [v1.0.1, `fe57c0f`](https://github.com/ramyahoo88/the_british_way_solo/commit/fe57c0faea60bc913e1f7c859963059d92d9aa7e) | [Re-audit PDF](audits/v1.0.1/Force_136_v1.0.1_Reaudit.pdf) | [Markdown](audits/v1.0.1/Force_136_v1.0.1_Reaudit.md) | [Evidence ZIP](audits/v1.0.1/Force_136_v1.0.1_Evidence.zip) |
| [v1.0.1, `33745a6`](https://github.com/ramyahoo88/the_british_way_solo/commit/33745a6cad5d89f81b3118806b14eec291bec72a) | [Comprehensive audit PDF](audits/v1.0.1/Force_136_v1.0.1_Comprehensive_Audit_33745a6.pdf) | [Markdown](audits/v1.0.1/Force_136_v1.0.1_Comprehensive_Audit_33745a6.md) | [Evidence ZIP](audits/v1.0.1/Force_136_v1.0.1_Audit_33745a6_Evidence.zip) |
| [v1.0.3, `595f409`](https://github.com/ramyahoo88/the_british_way_solo/commit/595f409ccae43f795f7fbdc38878f07f7967682a) | [Independent audit PDF](audits/v1.0.3/Force_136_v1.0.3_Independent_Audit_595f409.pdf) | [Markdown](audits/v1.0.3/Force_136_v1.0.3_Independent_Audit_595f409.md) | [Evidence ZIP](audits/v1.0.3/Force_136_v1.0.3_Audit_595f409_Evidence.zip) |
| [v1.0.4, `5efd44f`](https://github.com/ramyahoo88/the_british_way_solo/commit/5efd44f34a64625f4b627c832d038a2d85566780) | [Re-audit PDF](audits/v1.0.4/Force_136_v1.0.4_Reaudit_5efd44f.pdf) | [Markdown](audits/v1.0.4/Force_136_v1.0.4_Reaudit_5efd44f.md) | [Evidence ZIP](audits/v1.0.4/Force_136_v1.0.4_Audit_5efd44f_Evidence.zip) |

The latest review examines v1.0.4 at `5efd44f`. All four findings from the
v1.0.3 audit are resolved; no new material defect was confirmed. The evidence
includes 24,000 fresh positions with 264,000 action comparisons, the reproduced
960-game and 12,000-position legality runs (12,207 confirmed Raids; none
undecided), and 256 old/new wide-lookahead pairs with identical complete results.
The corrected 11-page print package and expanded sample were verified.
Verdict: pass v1.0.4 for release as a simulation-tested paper fan bot. Physical
playtesting remains outstanding. The reviewed release files are on
`claude-force136`; this audit update does not merge that branch.
The older reports remain available above with their exact source commits.

## Current print package: v0.2

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

[SHA-256 file manifest](FILE_MANIFEST_SHA256.json) identifies the uploaded
artifacts. The ZIP packages contain the source and their reproduction commands.

The underlying rules are GMT Games' [Japanese Occupation rulebook](https://gmtwebsiteassets.s3.us-west-2.amazonaws.com/TheBritishWay_EnemyofMyEnemy/EomE_JapOcc_Rules.pdf).
This is an independent fan variant, not a GMT publication. Publisher rulebooks,
Event artwork and maps are not included here.
