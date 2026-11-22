# Force 136 Digital Deck v1.0.0 - comprehensive app audit

21 November 2026, America/Chicago. Review by Astra.

**Verdict: pass for continued use, with three low-severity interface fixes recommended.** No card-order, deck-conservation, shuffle-boundary, save-validation, recovery-data, or winner-calculation defect was found in the tested release. This verdict covers the digital deck companion and its delivered reference materials. It does not certify new bot-strength claims or a complete rules engine; this app has neither a board engine nor automated board decisions.

## Exact release and authority

| Item | Reviewed version |
|---|---|
| Repository | `ramyahoo88/the_british_way_solo` |
| Main at review | `b8a5fdb4c6ddd3205f5adcb96349d7377b64a2d4` |
| App source release | `201d3399453038c869a211b8b0c5f974c5fa85f5`, app v1.0.0 |
| Paper inputs | Force 136 v1.1, `370ae906270464be64a304d95e6ee7a509c9fc1c` on `claude-force136` |
| Production | https://solo-table.pages.dev/games/force136/ |
| Cloudflare production deployment | `43b844c7-5902-46fe-be98-10dfebdad625`, successful; source commit 201d339 |
| Shipped HTML SHA-256 | `53918fa5acd805b971bdcdab64ed749f1536c26b76e3eb9ef9fe557ebda21fc3` |
| Served rules PDF SHA-256 | `de13a6ff38cbdea686d6fc0981d7b1906c500b272f67c7bae8567a6928a28e01` |

The official physical game and official corrections take precedence. For bot decisions, the pinned v1.1 booklet and nine printed Directives are the agreed variant. The app should reproduce those priorities and preserve the deck while the player resolves the physical board.

I checked GMT's current product page and its linked Japanese Occupation living rulebook, including the original Propaganda aid layout. The product page lists living rules; I found no separate expansion errata link there. Relevant official sections are 2.3-2.4, 5.4, 6.2.6 and 7.0.1. This is not a claim that no clarification exists elsewhere. Sources and links are listed below.

## Confirmed findings

### F1 - Low: winner text remains after its inputs cease to apply

**Player impact.** The optional scoring helper can display a definitive winner beside changed counts or an unchecked final-Propaganda box. A player may read the old result as a current assessment. The underlying winner function is correct; the problem is stale presentation.

**Expected behavior.** A displayed result must either describe the current confirmed inputs or be clearly labeled as a previous calculation. Unchecking final Propaganda should remove the current winner announcement. Bot rule 8 and official rules 6.2.6/7.0.1 establish the timing and winning conditions.

**Smallest setup and exact reproduction.** No deck seed or board save is needed. Open Reference. Set Resistance to 20, Camps to 0 and Force 136 markers to 0. Check "This is the final Propaganda" and click Check winner. Then change Resistance to 0 and uncheck final Propaganda. Do not click Check winner again.

**Observed result.** "Force 136 wins. Japan loses." remains visible beside Resistance 0 and an unchecked final box. `evidence/browser-evidence.json` records the live production input, checkbox and result readback. With the final box checked and a fresh submission, the correct Japan result is produced at Resistance 0; the adjacent calculation case passes.

**Source and cause.** `web/force136/src/ui.js:83` writes the result only on submit. No input/change handler invalidates it. Game replacement at `ui.js:14` also leaves this auxiliary form/result intact. Inputs and output are defined at `src/template.html:22`.

**Smallest proposed fix.** Clear `score-result` whenever any score input or the final checkbox changes. Clear the result and final confirmation when a new game or imported game replaces the session, and when Undo changes the session identity. Alternatively, retain a clearly labeled snapshot of the checked values. The clear-on-change approach is smaller.

**Runnable boundary assertion.** After the reproduction, in the page's developer console: `console.assert(document.getElementById('score-result').textContent === '', 'F1: stale winner');`. This intentionally reports a failure on v1.0.0. Repeating Check winner on unchanged valid inputs must still show the correct result after a fix.

### F2 - Low: resolved storage warnings keep describing a current failure

**Player impact.** A recovered, successfully saved deck can simultaneously say "Saved on this device" and "Autosave is unavailable." After explicitly replacing damaged saves, the banner still instructs the player to import or start again and says the damaged save was left in place. The tested data is stored correctly, but the conflicting messages undermine confidence and can provoke unnecessary recovery work.

**Expected behavior.** A persistent warning should reflect the current storage state. A successful write should clear or replace an earlier storage failure notice. A cross-tab conflict must remain until the stale tab reloads; it must not be cleared merely because another unrelated operation succeeds.

**Reproduction A.** Generate the supplied disposable browser fixtures. Open `app.html?case=damaged`. It initializes the primary and backup to malformed JSON before loading the unchanged release UI. Start a new Agent game, then click the fixture's Inspect storage state button.

**Observed A.** The stored primary is valid JSON, level Agent, draw 0; the app reports "Saved on this device." The banner still says the saved deck could not be opened and the damaged save was left in place.

**Reproduction B.** Open `app.html?case=quota`. This starts from the included Legend save, seed 2200001, draw 12, current Directive 4, then deliberately rejects storage writes. Draw once: the deck advances in memory and the failure warning appears. Click the fixture's Restore storage writes button, draw again, then Inspect storage state.

**Observed B.** The primary now contains the valid draw-14 deck and the save status reports success; the old "Autosave is unavailable" banner remains. `browser-evidence.json` retains both before/after observations. The nearby genuinely failing-write case correctly shows the warning, and a damaged-primary/valid-backup case correctly restores and continues the deck.

**Source and cause.** `web/force136/src/ui.js:9` sets the single notice. Lines 10-12 create startup notices; `ui.js:13` adds a write-failure notice but never clears it on success. `src/core.js:105` successfully writes the state in the reproduced recovery case.

**Smallest proposed fix.** Track the notice's reason. On a successful write or explicit successful replacement, clear/update storage-error and damaged-save notices. Preserve the cross-tab conflict notice while `locked` is true. No save-format or deck change is required.

**Reproducibility.** `prepare_browser_fixtures.py`, `fixtures/seed-2200001.json` and the README provide the setup. The fixture changes only its own test origin and storage-fault precondition; the released UI and core scripts are unmodified. This fault injection was exercised in the real browser, not reported as a naturally occurring production outage.

### F3 - Low: switching a mobile procedure retains the previous scroll position

**Player impact.** Opening the next procedure from a long reference can omit its heading and opening restrictions from the visible area. In the reproduced Raid case the start of its destination limit was above the modal viewport. The instructions exist, but the player must notice and scroll back.

**Expected behavior.** Choosing a new goal/procedure should open that content at its beginning. Bot procedure 6.7 places Raid's limits before its ranked choices, so that order needs to remain apparent when entering the procedure.

**Smallest setup and exact reproduction.** Use a 390px-wide by 844px-high browser frame (375px content width with this desktop browser's scrollbar). Start any game and draw a Directive. Open PLACE, then Contact. Scroll to the procedure buttons at the end and choose Raid. The included `mobile.html` fixture frames the exact unmodified release HTML.

**Observed result.** The Raid modal retained `scrollTop=145`; its top edge was at y=16 while the Raid heading was at y=-67.8125. The opening text and close control were above the visible area. `evidence/F3-mobile-detail.jpg` records the result. Initial opening of the shorter PLACE reference starts normally; the failure requires navigation after the longer content has scrolled.

**Source and cause.** `web/force136/src/ui.js:25` replaces the existing modal body. `ui.js:26` calls `openDialog`, which does nothing when the dialog is already open (`ui.js:15`). Neither resets the scroll position.

**Smallest proposed fix.** After replacing the content and opening the modal, set the dialog's `scrollTop` to zero. Moving focus to the new heading is a useful accompanying accessibility improvement.

**Runnable boundary assertion.** With the affected frame selected in developer tools, evaluate `console.assert(document.querySelector('#detail-content h2').getBoundingClientRect().top >= document.getElementById('detail-dialog').getBoundingClientRect().top, 'F3: procedure heading is above the viewport');`. It fails in the recorded v1.0.0 position.

## Evidence that passed

| Area | Direct result |
|---|---|
| GitHub inputs | All 33 app files matched the reviewed main tree's Git blob IDs. The four paper inputs also matched their blobs on 370ae90. |
| Rebuild | HTML, downloadable HTML, PDF copy and Pages function bundle rebuilt byte for byte. |
| Public downloads | The actual browser-downloaded HTML and served rules PDF matched the hashes above. PDF: 5 pages. |
| Repository tests | All 15 existing core/Worker tests passed in this audit. |
| Fresh deck stress | 1,000 sessions, seeds 2200001-2201000, five levels; 72,000 draws over eight cycles per session. Zero invariant failures. |
| Save and Undo stress | 6,000 JSON round-trips, 10,000 exact Undo/replay comparisons, 24,000 explicit finishes; zero failures. |
| Invalid saves | 26 malformed/incompatible mutations rejected; no state replacement. The live UI also rejected a duplicate-card import and kept its current deck. |
| Winner helper | 420 combinations covering Resistance 0-20, Camps 0-4 and markers 0-3 matched the independently stated winner table. Seven boundary positions also checked through the browser controls. |
| Browser checks | 50 recorded positive checks passed across live production and isolated fixtures. The three confirmed defects above are recorded separately, not counted as passes. |
| Delivered content | Nine Directive faces; all 18 full/Limited priority lists; 11 rule sections; both level-table columns and all five levels; six goals and seven procedures. |
| Catalog and hosting | Live catalog shows all 11 companions. Production retains the previous 31 static path/hash entries; app routes are narrowly scoped. No deployment was made during this audit. |

The independent stress script checks conservation, exactly-once cards within each cycle, draw-count relationships, expected next cards before a reshuffle, explicit/implicit discard behavior, and exact replay from the prior state. Its counts describe deck sessions, not complete simulated board games. The first-card counts are retained as diagnostics, not presented as a statistical proof of perfect randomness.

I followed the real controls from setup through drawing, a complete nine-card cycle, reshuffle, Undo, notes, export, import review/application, undoing an import, new-game level changes, reload and cross-tab conflict/reload. A separate 32-draw workflow reached cycle 4 and recorded 32 revealed cards in History, followed by final-winner inputs. Board actions and Resistance scoring remained the player's responsibility. No physical tabletop game was played.

The second-player useful-J4/J25 condition, no-SA Limited reminder, Recruit Raid exclusion, mandatory-card Pass restriction, later-level bonus timing, source ordering and map/railway lists agree with the pinned paper instructions. I visually checked the printed nine-card sheet and Propaganda aid, and inspected the on-screen card/modal layout at desktop and narrow widths. Existing special-case procedure text (including J8, J19, J22 and J27) remains in the searchable rules and procedure panels.

## Optional usability improvements, not confirmed gameplay defects

- **Q1 - Validate physical piece counts.** The score fields and `core.js:114` permit counts up to 99. The standard game has four Jungle Camps and three Force 136 markers. Capping those inputs at the physical supplies would catch typing errors. This is an input guard, not a change to the winning formula.
- **Q2 - Clarify when to enter final Resistance.** At `src/template.html:22`, add a short reminder to finish the MPAJA and Resistance phases before using the winner check, and stop before the later nonfinal phases. This would make the helper easier for a first-time player using the physical aid.
- **Q3 - Short glossary beside procedures.** A small Terms link inside the modal would reduce trips to Rules for "good shot," "exposed" and "majority." Keep the complete printed procedures authoritative; do not add board automation for this improvement.

The practical administration observed is one draw action per British turn, plus a mode change when needed. A first-time PLACE lookup used three additional interactions: open PLACE, open Contact, close the reference. Moving directly to Gather costs one more selection. The app handles shuffling, discards and save bookkeeping; board assessment, dice, icons, phases and piece movement stay at the table. These are observed interaction counts, not a timed human-playtest study.

## Ambiguities and coverage limits

The northern railway-corner reading remains an explicitly allowed paper interpretation in rule 11. This app contains no adjacency graph, so it does not silently choose one reading. Use the physical map and the agreed interpretation. No new rules ambiguity was found in the app's implemented deck/scoring functions.

There was no new Japan-policy comparison or win-rate simulation: the companion cannot choose Operations, apply Events, inspect concealed Intel, or score a complete board. Tests of strategic exploits would exercise the separate research engine, not this release. Earlier qualifications about that engine's J13 trial and railway model are not resolved by this app audit. Undo and export are deliberate player tools, not an anti-cheating boundary; their existence is not counted as a bot exploit.

The cloud browser rejected local `file:` navigation by policy. I downloaded and hashed the standalone file and verified that it embeds its runtime data/scripts/styles, but did not directly launch it as an offline local file. No workaround was attempted. Real Android/iOS file-opening behavior, Safari/Firefox, screen-reader use, physical printing and a human tabletop session remain untested. The phone check used a narrow frame in desktop Chrome, not a physical phone. Browser Print rules was inspected in source; its system print dialog was not exercised. No new HTTP sweep of every other game was performed; catalog preservation rests on the native deployment manifest, unchanged routing and the live catalog inspection.

## Fix order and release verdict

Prioritize F1's stale winner and F3's procedure scroll reset, then F2's notice lifecycle. Q1 and Q2 are small optional improvements suitable for the same polish release; Q3 can wait for tabletop feedback. None requires changing bot rules, Directive composition, saves, or published difficulty results.

**Release verdict: PASS for continued use of app v1.0.0, with three low-severity defects recommended for a v1.0.1 interface patch.** The rebuilt/downloaded release matches its sources, all core and new stress checks passed, all nine cards and both priority modes match print, and the browser workflow retained deck state correctly. The verdict is bounded by the explicit offline/device/tabletop gaps above. This audit changes no production application or bot rule.

## Sources and reproduction

- GMT product and living-rule links: https://www.gmtgames.com/p-1107-the-british-way-enemy-of-my-enemy.aspx
- GMT Japanese Occupation rules: https://gmtwebsiteassets.s3.us-west-2.amazonaws.com/TheBritishWay_EnemyofMyEnemy/EomE_JapOcc_Rules.pdf
- Pinned fan rules/cards: https://github.com/ramyahoo88/the_british_way_solo/tree/370ae906270464be64a304d95e6ee7a509c9fc1c/force136_v1/print
- Reviewed app: https://github.com/ramyahoo88/the_british_way_solo/tree/b8a5fdb4c6ddd3205f5adcb96349d7377b64a2d4/web/force136
- Original-layout checks used the retained Japanese Occupation Propaganda aid from the Vassal 3.1.1 material and the shipped fan card PDF. Publisher artwork is not redistributed in this audit package.

The accompanying README gives exact commands, fixtures and assertions. `evidence/browser-evidence.json` records each browser check and the three reproductions; `evidence/stress-results.json` records the fresh deterministic run. The report PDF and evidence ZIP are convenience copies of this audit directory.
