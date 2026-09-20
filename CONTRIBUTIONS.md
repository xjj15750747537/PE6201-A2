# CONTRIBUTIONS

Team C-2 · Problem B — Outpatient Referral Coordination
This log names who did what. Commit history in this repository corroborates it (see the
commit hash / date range against each entry — verifiable with `git log --author="<name>"`).

---

## CHANG HING LAM (G2604436H)
GitHub identity: `Hing Lam Chang` (also appears once as `Hing Lam CHANG`) — 23 commits,
3–20 September 2026 (confirmed match)

- Wrote D0 pre-build evidence and the Good-Run Criteria (`docs/good_run_criteria.md`),
  committed before any agent code existed (`f53afa7`, 3 Sep), satisfying the brief's
  before-any-implementation timing requirement.
- Built the first instrumented scripted ReAct runner and integrated the lecturer scaffold
  for Problem B (`e9bf0b7`, `2a32f60`).
- Wrote the D2(a) tool-set rationale (`docs/D2_tool_set.md`, `812f1a7`) and the D2(c)
  dependency-aware parallel runner and write-up (`docs/D2c_parallelism.md`,
  `scripts/run_d2c_comparison.py`, `7c820e8`, `5d5d3bf`).
- Authored the 55-case Problem B D4 fixture set and generator (`f729b4b`).
- Built the team's Colab live-evaluation pipeline for D5(b) (multiple commits, 15–16 Sep):
  live trial policy, repository-import fixes, duplicate-fragment handling, output-contract
  hardening, tool-result protocol tests.
- 19 Sep (`a498767`): restored `_validate_parallel_batch()` and the dependency-aware
  parallel runner after the 18 Sep interface change below removed it — current code
  (`agent.py`) matches Section 2's "book_slot runs alone" claim again.
- 20 Sep (`87dca8d`): committed the audited D5(b) live-battery evidence — all six raw run
  files under `results/live_runs/`, plus `results/d5_model_summary.json` and
  `results/d5_runs.json`.

## GAO ZIHAN (G2602301K)
GitHub identity: `JeffGao` — 11 commits, 5 & 18 September 2026 (confirmed match)

- Uploaded the working D2/D3 code layer: `agent.py`, `tools.py`, `backends.py`,
  `guardrails.py`, `harness.py`, `config.py`, `prompt.py`, `run_eval.py`
  (`ebfad64`, `e844ef8`, 5 Sep).
- Wrote the D2(b) interface handoff and D3 guardrail docs (`docs/D2b_interface_handoff.md`,
  `docs/D3_guardrails.md`, `5d1157b`).
- Added `tests/test_submission_runner.py` (`57d38a2`).
- Measured the D2(b) return-shape evidence (`scripts/measure_d2b_return_shape.py`,
  `results/d2b_return_shape_measurement.json`, `eb4bfe7`, `87da4e1`, `c0cd283`).
- Ran the D5(b) live battery on Mistral Small 3.2 (`zihan-mistral-small32-v2-01`, per
  Table 3.1 / D5(b) source list) — raw run JSON committed at
  `results/live_runs/zihan-mistral-small32-v2-01.json` (`87dca8d`, 20 Sep; internal
  `owner: "Gao Zihan"` field matches this entry).
- 18 Sep: revised `agent.py`/`tools.py` (`a1b7f40`) — removed `_validate_parallel_batch()`
  and switched parallel tool calls to a sequential loop; added `get_clinic_slots_v1()`.
  This briefly created a wording mismatch with Section 2's "book_slot always runs alone"
  claim — **resolved 19 Sep** when Chang's `a498767` restored the guard (see above); no
  outstanding mismatch as of the current commit.

## HU ZIYI NICOLE (G2604013B)
GitHub identity: `ziyinicolehu` — 3 commits, 18 September 2026 (confirmed match)

- Built the D3(b) guardrail checklist: doc, results, and script
  (`docs/D3(b)_guardrail_checklist.md`, `results/d3(b)_guardrail_results.json`,
  `scripts/d3(b)_guardrail_checklist.py`).
- Ran the D5(b) live battery on GPT-4o-mini v2 (`nicole-gpt4omini-v1-protocolfix-01`,
  reported as a v2 result per its run metadata) — raw run JSON committed at
  `results/live_runs/nicole-gpt4omini-v1-protocolfix-01.json` (`87dca8d`, 20 Sep; internal
  `owner: "Ziyi Nicole Hu"` field matches this entry).

## LU YAO (G2603916H)
GitHub identity: `judylou0117-stack` — 1 commit, 16 September 2026 (confirmed match)

- Edited `run_main.ipynb` (Colab live-run notebook), 633 insertions / 342 deletions
  (`3d71907`).
- Ran the D5(b) live battery on Claude Haiku 4.5 (`yao-claude-haiku45-v2-02`) — raw run
  JSON committed at `results/live_runs/yao-claude-haiku45-v2-02.json` (`87dca8d`, 20 Sep;
  internal `owner: "LU YAO"` field matches this entry).

## XU JUNJUN (G2603439G)
GitHub identity: `xjj15750747537` — 1 commit, 31 August 2026 (repository owner / creator;
confirmed match)

- Created the repository (`4dba0b8`, initial `README.md`).
- Ran the D5(b) live battery on Gemini 3.8 Flash (`junjun-geminiflashlatest-v2-05`) — raw
  run JSON committed at `results/live_runs/junjun-geminiflashlatest-v2-05.json`
  (`87dca8d`, 20 Sep; internal `owner: "junjun"` field matches this entry).

## YOO SEUNGMIN (G2606541G)
GitHub identity: `usmin1004` — 17 commits, 18–19 September 2026 (confirmed match — this
account)

- Built the D2(c) full-set verification script, raw output, and summary doc
  (`scripts/verify_d2c_full_set.py`, `results/d2c_full_set_*`,
  `docs/D2C_FULL_SET_SUMMARY.md`); found and fixed the REF-5602 schedule discrepancy
  (three disagreeing implementations), locked the correct 6-sequential/4-parallel
  production schedule with a regression test
  (`e97c542`, `c6b6a11`, `16903ef`).
- Built the D2(b) v1/v2 tokens-per-call verification script, raw output, summary, and
  write-up, including the turns and positive/negative breakdown
  (`e618e5c`, `a3180e0`, `ce51826`, `58f25a7`).
- Built the D7 loop-failure and gate-failure ablation scripts (`3c49f7d`).
- Ran the D5(b) live battery on DeepSeek Chat v3.1 (`min-deepseek-chat-v3.1`) — raw run
  JSON committed at `results/live_runs/min-deepseek-chat-v3.1.json` (`87dca8d`, 20 Sep;
  internal `owner: "Seungmin Yoo"` field matches this entry).

---

## Note — D5(b) live-battery source files

As of `87dca8d` ("Add audited D5 live battery evidence", committed by Chang), all six raw
run files behind Table 3.1 are committed under `results/live_runs/`, together with the
consolidated `results/d5_model_summary.json` and `results/d5_runs.json`. Each raw file
carries an internal `owner` field naming the team member who ran it, matching this log —
see the notes against each name above.

One caveat worth noting for markers: because this commit was made by Chang consolidating
everyone's runs, `git blame`/`git log --author` on these specific files shows Chang as the
committer, not the person who generated the run. The per-file `owner` field and the dates
in each JSON are the actual evidence of who ran what; this log and those fields together
are the corroboration, not the commit author alone.
