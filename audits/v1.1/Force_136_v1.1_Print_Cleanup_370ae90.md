# Force 136 v1.1: print cleanup review

**21 November 2026. Reviewed commit:** `370ae906270464be64a304d95e6ee7a509c9fc1c`, `ramyahoo88/the_british_way_solo`, branch `claude-force136`.

**Result: pass for this cleanup, with one optional printing clarification.** The shipped booklet has five pages and the packet nine. No new bot or rules defect was found. This focused review checks the delivered documents and the changes since the previous v1.1 audit; it does not repeat the full game-engine audit or certify the remaining research-model assumptions.

## Directly verified

| Material | Observed result |
|---|---|
| Rules booklet | 5 numbered pages; sections 1-11; Sources is section 11; no Design notes section |
| Level table | Both columns and all five levels present; no win-rate column or footnote; Agent progression advice and Mastermind sentence retained |
| Removed language | Neither the Markdown nor shipped rules PDF contains simulation/computer language, a simulation-tested status line, the worked example's former simulation source line, or the five win-rate figures |
| Other rules text | All 116 source blocks, including table cells, present in the PDF after normalizing punctuation and whitespace; the worked moves and railway-corner note remain |
| Reference and cards | All 71 reference source blocks and all nine Directive cards checked; goal order and Limited order agree with card data; each footer includes the free Event-box condition |
| Packet | Exactly rules 1-5, reference 6-7, cards 8-9; each page matches its standalone component in both text and rendered pixels |
| Record sheet | Separate one-page PDF remains; its playtest-record page is absent from the packet |
| Release inputs | All 222 selected files match their pinned Git blob IDs; all 220 package entries match the SHA-256 manifest |

I visually inspected all five rules pages, both reference sides, and both card sides. The columns, level table, flowchart, footer reminders and section transitions are readable, with no clipping or missing text found. The packet pages are pixel-identical to these inspected standalone pages. This was a digital print review, not a physical printer or tabletop test.

Relevant source locations: `force136_v1/print/Force_136_v1_Rules.md:158` (levels), `:168` (retained advice), `:172` (worked example), `:191` (Sources), `:195` (railway reading); `force136_v1/print/build.py:230` (separate record sheet) and `:232` (packet components); `force136_v1/README.md:13` (packet description).

## Checks and scope

The engine, primary bot, clean-room bot and Directive data are byte-identical to the previously reviewed 127e34c inputs. The new Gather wording attributes J19's limit to its card tip while retaining the bot's first-space priority. The cleanup changes no level adjustment or gameplay procedure.

The native **19 fixtures pass**, including the new rule-source check at `code/review_fixtures.py:213`. **report_check.py passes**: the README and simulation report still match the stored v1.1 results. Its removed expectation concerns only the booklet's deleted win-rate column. The independent `print_verify.py` also checks the shipped PDF, so a clean Markdown file alone is insufficient to pass this review.

No new win-rate or strategy cohort was run; the native regression fixtures include fixed seeded games. Unchanged executable inputs make a repeat of the large simulation studies unnecessary for this document-only change. The previously documented J13 scope limitation, affected reference-search comparison and northern-adjacency model choice remain research qualifications; this cleanup does not resolve them by changing the engine.

A fresh PDF rebuild was attempted using the supplied build script and installed Chromium, substituting its executable name for Google Chrome. Chromium could not start because the environment denied its process socket. Therefore this review verifies the shipped outputs, source-to-PDF text, component assembly and manifest; it makes no claim of a successful clean rebuild or byte-identical regeneration. The failure log is included.

## P1 - Optional usability improvement: duplex printing

**Player impact.** Printing the entire nine-page packet as one ordinary duplex job would waste reference/card sheets or require reprinting. This is a printing trap, not a gameplay defect or release blocker; the separate PDFs already provide a working route.

**Expected behavior.** The printing instruction at `print/Force_136_v1_Rules.md:15` asks for a two-sided reference sheet. Its two sides should occupy the same sheet; card fronts and optional backs should likewise share a sheet.

**Exact reproduction.** Open the shipped nine-page packet. Choose all pages, ordinary two-sided printing and actual size, without booklet imposition or inserted blanks. With pages paired 1/2, 3/4, 5/6, 7/8 and 9/blank, the reference front (6) is on sheet 3 and its back (7) on sheet 4. Card fronts (8) and backs (9) occupy sheets 4 and 5. This assignment follows directly from the inspected page order; no physical print was performed.

**Source and smallest proposed fix.** `print/build.py:232-234` concatenates five rules pages immediately before the two reference and two card pages. Add this sentence to the printing note at `Rules.md:15` and, optionally, beside the download links at `README.md:13`:

> For two-sided printing, print the rules separately and use the separate reference-sheet and card PDFs as separate print jobs.

That preserves the nine-page packet and its optional card backs. Alternatively, print packet pages 1-5 separately, then 6-7 as one duplex job, then 8-9 as another. No blank page or gameplay change is required. The evidence records the exact page-to-sheet mapping.

## Release verdict

**Pass for the print cleanup at 370ae90.** The page counts and claimed removals are confirmed in the files players receive; required play instructions, card orders and level adjustments remain intact; the fixtures, stored-results check and independent PDF checks pass. P1 is an optional printing clarification. The existing paper-bot verdict stands, subject to the previously documented research limitations and lack of a physical tabletop session.
