# Results

Final runs (printed rules `force136_v1.py`, final engine):

| File | What |
|---|---|
| final_equiv.log | tuning lab vs printed rules, 960 games (five levels): 0 mismatches |
| final_cleancmp.log | clean-room implementation vs printed rules, 960 games: 0 divergences |
| final_holdout.log, results_holdout.json, holdout_summary.json | holdout 1 (seeds 20000–20127, 768 games/level); holdout_summary.json has intervals and behaviour for holdout 1 and both holdouts pooled |
| final_confirm.log, results_confirm.json | holdout 2 (seeds 20128–20383, 1,536 games/level) |
| final_look.log, final_lookc.log, final_lookdeep.log | lookahead Japan policies (8×3 and the wide 16×4 search) |
| final_exploits.log, results_exploits.json | scripted exploit policies |
| final_corner.log | alternative railway-corner adjacency |
| final_refs.log, refs_final.json | v0.2 bot, v0.2 best variant, one-step search player |
| final_events.log, final_events_summary.log, ev_test_v1.json | per-Event paired tests |
| ev_confirm.log | 1,152-game follow-ups for the best Event candidates |
| sample_20005_adaptive.json | the sample game |

Development-era logs: `sweep_full.log` (120 full-turn orders, early rule bot), `sweep2.log` (24 orders × 2 Limited preferences), `ev_test.log` (first Event sweep, early rule bot).
