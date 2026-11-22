# Force 136 Digital Deck v1.0.1

This release addresses the three interface findings in the v1.0.0 app audit
and includes its three suggested convenience improvements.

| Finding | Result |
|---|---|
| F1: stale winner | Editing scoring inputs clears the previous result. Imports and new games reset the final-Propaganda confirmation and result; Undo across games does the same. |
| F2: stale save warning | A successful save clears a resolved recovery or storage warning. An active cross-tab conflict remains locked and visible. |
| F3: mobile procedure scroll | Each newly selected goal or procedure opens at the beginning and focuses its heading. |
| Q1: physical piece counts | The scoring form and core validation cap Camps at four and Force 136 markers at three. |
| Q2: final Resistance timing | The reference explains when to enter Resistance and which final-Propaganda phases must already be complete. |
| Q3: procedure glossary | An expandable Terms section repeats the printed definitions of Majority, Good shot and Exposed. |

Validation: all 17 core/hosting tests pass; the app rebuilds byte for byte.
`browser-regressions.json` records 65 successful checks of the built UI.
`manual-checks.json` records the recovery notices and the 390px procedure
transition. The phone transition was checked again before publication:
Raid opens at scroll position 0, with its heading below the dialog's top edge.
The Cloudflare preview's three inline script hashes match the tested build.
`stress-results.json` retains the independent 72,000-draw deck checks.

Existing v1.0.0 deck saves and Undo remain compatible. Force 136 rules remain
v1.1; the nine Directive faces and the rules PDF are unchanged.
