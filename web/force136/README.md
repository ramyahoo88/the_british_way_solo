# Force 136 digital deck v1.0.0

[Open the companion](https://solo-table.pages.dev/games/force136/) · [Download the offline HTML](https://solo-table.pages.dev/downloads/force136)

Draw Force 136's nine Directive cards while playing Japan on your physical **The British Way: Enemy of My Enemy** board. The companion includes the Force 136 v1.1 rules from commit `370ae906270464be64a304d95e6ee7a509c9fc1c`.

## At the table

1. Set up the standard standalone Japanese Occupation scenario with the physical game and expansion. Choose a level in **Start game** and set the starting Resistance shown. Starting shuffles the deck; it does not draw a card.
2. Reveal your official Event cards on the table and resolve the MPAJA icon and any Mandatory Event before either player acts.
3. Whenever Force 136 acts, draw one Directive, including when it will take J4 or J25. Check its Event rule, then choose **Op & SA** or **Limited** to display the appropriate priorities. Tap a goal for its rule; the reference includes all seven procedures, map order, railway order and between-turn choices.
4. **Draw next Directive** discards the current card before drawing. **Finish turn / discard** is available if you want to discard immediately. Discards reshuffle only when an empty deck needs its next draw. Only revealed cards appear in history.

The app tracks the deck and optional notes. Keep the board position, official Event deck, pieces, dice, resources and tracks on the table. At final Propaganda, the optional winner check handles Resistance 18-19 with the strict Camp/marker comparison. MPAJA victory is a loss for both players.

## Convenience features

- Undo restores draws, discards, new games, imports and groups of note edits. Restoring a reshuffle and drawing again gives the same card.
- Autosave restores the current card, piles, notes and Undo after reload. A separately retained valid save is used when the primary save is damaged. Both damaged saves are reported without silently replacing them.
- Export/import moves a deck between browsers or devices. Imports are validated and reviewed before replacement; Undo can restore the game open before import. A fresh app also restores the imported Undo stack. Saves are limited to 4 MB, including the largest notes/history combination the app can export.
- Another tab changing the same deck locks stale draw controls until reload, preventing accidental overwrites.
- Searchable full rules, compact goal/procedure help, level reminders, and revealed-card history are available without printing. There are no win-rate or simulation claims in the playing interface.
- The downloadable HTML contains the app, card data, rules and flowchart in one file. Open it directly in a modern browser. Hosted and file copies may have separate browser storage; use export/import to transfer a game. The linked rules PDF is optional and needs a connection.

## Source and build

`source_data/` pins the published bot inputs. `provenance.json` gives their source commit and hashes. `src/core.js` implements the deck and save format; `src/ui.js` provides the controls. This app includes no game engine or automated board decisions.

```sh
python -m pip install -r requirements.txt
python build.py
python deployment/build_worker.py
node --test tests/core.test.cjs tests/worker.test.mjs
python tests/check_build.py
```

Build outputs in `dist/` are self-contained. Runtime has no package or network dependency. A seeded shuffle state is retained in saves so Undo replays a shuffle consistently; new games get their seed from browser cryptographic randomness.

`tests/browser-qa.js` exercises the built UI in an isolated browser session on a preview URL. It intentionally changes that session's storage; never run it in a player's existing browser session. Results are written to `#force136-qa-result`.

## Cloudflare maintenance

The existing public site is the **solo-table Pages project**. Its previously deployed assets remain in the complete retained manifest. The active function bundle serves the Force 136 paths and the updated catalog; other games continue to be served as their existing static assets. The connection could create Pages deployments but rejected direct asset-store uploads, so this supported function-upload route is used.

**Keep `deployment/pages-worker.mjs`, `routes.json` and `headers.txt` when making a future site deployment.** Uploading the old static manifest alone would remove these new routes. Prefer moving the self-contained outputs to normal Pages static assets when direct asset uploading is available. Do not replace the existing site with `dist/` by itself.

Before publishing another update, fetch the latest **production/canonical** deployment and its complete file manifest; preview deployments also change the latest-deployment field. Refresh the catalog against the current live page, preserve all other companion paths and download headers, build the bundle, test a preview, then deploy the same reviewed bundle to production. `deployment/previous_manifest.json` is this release's recorded baseline, not a permanently current manifest.

Rules and card faces remain Force 136 v1.1. The official physical game and its corrections take precedence. This is an independent fan companion; no publisher map or Event-card images are included.
