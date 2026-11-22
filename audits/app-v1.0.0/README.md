# Force 136 Digital Deck v1.0.0 audit

Reviewed app: main `b8a5fdb4c6ddd3205f5adcb96349d7377b64a2d4`; rules v1.1 from `370ae906270464be64a304d95e6ee7a509c9fc1c`.

**Pass for continued use, with three low-severity interface fixes.** See REPORT.md and the PDF. Production was not changed.

## Repeat the automated checks

From this directory in a repository checkout:

```sh
node stress.cjs ../../web/force136
python content_inventory.py ../../web/force136
node --test ../../web/force136/tests/core.test.cjs ../../web/force136/tests/worker.test.mjs
```

The inventory script requires PyMuPDF. The app's own build requires Python-Markdown as pinned by its requirements.txt. `stress.cjs` has no third-party dependency. Fresh seeds: 2200001-2201000. Each of the 1,000 sessions draws 72 cards; all five levels are covered equally. A failing assertion exits nonzero.

## Browser reproductions

F1 can be reproduced directly on the live app: Reference, Resistance 20, Camps 0, markers 0, confirm final, Check winner; change Resistance to 0 and uncheck final. The old winner remains. See REPORT.md for the boundary assertion and source line.

F3 can be reproduced on a narrow viewport: draw a card, PLACE, Contact, scroll to its procedure links, Raid. The new heading opens above the visible modal. The supplied mobile frame reproduced it at a 390px outer width / 375px content width.

For deterministic storage-fault testing:

```sh
python prepare_browser_fixtures.py ../../web/force136
python -m http.server 8000 --directory browser-fixtures/dist
```

Open http://localhost:8000/ in a disposable test origin. The index links to both-damaged, quota-failure, valid-backup, and mobile fixtures. Never host these fault fixtures at a player's production origin: they deliberately replace that test origin's Force 136 save keys. The source app is not modified. In Work Mode this audit used the supported local preview service instead of the example server command above.

- Both damaged: start a new game, then Inspect storage state. The valid stored game and successful status coexist with the stale damaged-save banner.
- Quota: draw once while writes fail, Restore storage writes, draw again, Inspect storage state. The valid draw-14 save coexists with the stale failure banner.
- Backup: the supplied Legend seed 2200001 save at draw 12 restores as Directive 4 and can advance normally.

The JavaScript boundary assertions in REPORT.md intentionally fail on v1.0.0 after their specified actions. They are focused readbacks, not an unexecuted claim of a portable full-browser runner. The actual 50 browser checks were performed through the browser's native controls and are listed in evidence/browser-evidence.json.

## Files

- `fixtures/seed-2200001.json`: importable deterministic Legend deck, draw 12, Directive 4, with Undo history.
- `fixtures/live-export.json`: the actual browser export from the production audit; ten draws and a literal-text note.
- `fixtures/damaged-duplicate-card.json`: deliberately invalid import for rejection testing.
- `evidence/`: exact results, content inventory, remote tree/release provenance, and the F3 screenshot.
- `stress.cjs`, `content_inventory.py`, `prepare_browser_fixtures.py`: executable reproduction tools.
- `build_report.py`: PDF generation from REPORT.md; requires ReportLab, Pillow and DejaVu fonts.
- `SHA256SUMS.txt`: checksum list of the packaged audit inputs and outputs (excluding itself and the ZIP).

The generated browser-fixtures directory is disposable and omitted from the evidence ZIP. No publisher images, authentication data, browser profile data or user game saves are included. The only saves are the audit's synthetic/test sessions.
