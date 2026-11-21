# Results

## v1.0.3 (after the full audit of v1.0.2; Japan model corrected)

| File | What |
|---|---|
| v103_fresh.log, results_fresh_v103.csv.gz, fresh_v103_summary.json | all five levels on seeds 0–999 (6,000 games per level); `report_check.py` reads the CSV |
| v103_equiv.log | tuning lab vs printed rules, 960 games |
| v103_verify.log, v103_verify_results.json, v103_mutants.log, v103_mutants.json, v103_exit_status.log, v103_fixtures.log | checker, 15 mutants, exit status, 15 fixtures |
| v103_fuzz.log, v103_fuzz_results.json | `fuzz_v1.py 12000 700000`: both bots on random positions |
| v103_legality_games.log, v103_legality_fuzz.log, v103_legality_selftest.log (+ .json) | `legality_v1.py`: policy games, random positions, planted illegal actions |
| v103_holdout1.log, results_holdout1_v103.json | Agent on the first holdout (seeds 20000–20127) |
| v103_look.log, v103_lookc.log, v103_lookdeep.log, v103_lookexpert.log | lookahead Japan against the bot (five levels) and against the search player |
| v103_refs.log, refs_v103.json | v0.2 bot, its best variant and the search player on the first holdout |
| v103_exploits.log, results_exploits_v103.json | strict stress policies, 256 games per policy |
| v103_corner.log | alternative railway-corner adjacency |
| sample_20005_adaptive.json | the sample game (regenerated for v1.0.3) |

Everything below was produced with the earlier Japan model (before v1.0.3's corrections).

## v1.0.2 (after GPT's audit of commit 33745a6)

| File | What |
|---|---|
| v102_fresh_identity.log | all 30,000 fresh games rerun on v1.0.2: identical, row for row, to `results_fresh_v101.csv.gz` (which `report_check.py` reads) |
| v102_holdout1.log, v102_lookdeep.log, v102_equiv.log | first holdout, wide-search Japan (Agent, Mastermind) and equivalence, rerun on v1.0.2 |
| v102_exploits.log, results_exploits_v102.json | strict stress policies, 256 games per policy (seeds 20000–20255) |
| v102_verify.log, v102_verify_results.json, v102_mutants.log, v102_mutants.json, v102_exit_status.log, v102_fixtures.log | checker, mutants, exit status and the 12 review fixtures on v1.0.2 |

## v1.0.1 (after GPT's review)

| File | What |
|---|---|
| v101_fresh.log, results_fresh_v101.csv.gz, fresh_v101_summary.json | all five levels on fresh seeds 0–999 (6,000 games per level), with goal and action shares |
| v101_equiv.log | tuning lab vs printed rules, 960 games: 0 mismatches |
| v101_verify.log, v101_verify_results.json | `verify_v1.py 32`: 2,496 games (normal and forced-capability), 0 cross-check and 0 oracle failures, coverage counts |
| v101_mutants.log, v101_mutants.json | `verify_v1.py --mutants 16`: all 15 planted errors caught |
| v101_fixtures.log | `review_fixtures.py`: GPT's reproductions as tests, 8 passed |
| results_holdout1_v101.json | Agent on the first holdout (seeds 20000–20127) |
| v101_look.log, v101_lookc.log, v101_lookdeep.log | lookahead Japan, all five levels, 128 holdout seeds |
| v101_exploits.log, results_exploits_v101.json | scripted exploit policies |
| v101_corner.log | alternative railway-corner adjacency |
| sample_20005_adaptive.json | the sample game (regenerated for v1.0.1) |

v1.0 checks made in response to the review:

| File | What |
|---|---|
| results_v1.0_gpt_window_50000.json, results_v1.0_gpt_window_60000.json | GPT's fresh windows rerun: identical to GPT's rows (51.0% and 54.9%) |
| v1.0_fresh_agent.log, results_fresh_v1.0.csv.gz | v1.0 on fresh seeds: Agent on five 1,000-seed blocks (0, 30000, 50000, 60000, 90000) and the other levels on seeds 0–999 |
| v1.0_refresh_variants.log | Train refresh variants on development seeds (refresh last: +6.5 and +7.1; refresh first: −0.9) |

The 6,000 paired games for the refresh decision are the Agent rows for seeds 0–999 in `results_fresh_v101.csv.gz` and `results_fresh_v1.0.csv.gz`.

## v1.0

Final runs (printed rules `force136_v1.py` at v1.0, final engine):

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

Development-era logs: `sweep_full.log` (120 full-turn orders, early rule bot), `sweep2.log` (24 orders × 2 Limited preferences), `ev_test.log` (first Event sweep, early rule bot).
