# CONTRIBUTIONS

Team C-2 · Problem B — Outpatient Referral Coordination

This log combines Git-traceable evidence with factual work that Git cannot show (case design, evaluation runs, review, report work, and video production). Each member reviewed the wording of their own non-Git contribution.

---

## Shared evaluation-case allocation

The 55-case Problem B evaluation suite was a shared team deliverable. The team-created extension cases were apportioned across all six members at approximately 5–8 cases per person, covering booking, red-flag, hostile-instruction, and other negative scenarios. Each contributor checked the agreed scenario, trigger, expected outcome, and reason format; the final integrated fixture set and generator are traceable to `f729b4b`.

## CHANG HING LAM (G2604436H)

GitHub identity: `Hing Lam Chang` (also appears once as `Hing Lam CHANG`) — 23 commits, 3–20 September 2026 (confirmed match).

- Wrote D0 pre-build evidence and the Good-Run Criteria (`docs/good_run_criteria.md`), committed before any agent code existed (`f53afa7`, 3 Sep).
- Built the first instrumented scripted ReAct runner and integrated the lecturer scaffold for Problem B (`e9bf0b7`, `2a32f60`).
- Wrote the D2(a) tool-set rationale (`docs/D2_tool_set.md`, `812f1a7`) and the D2(c) dependency-aware parallel runner and write-up (`docs/D2c_parallelism.md`, `scripts/run_d2c_comparison.py`, `7c820e8`, `5d5d3bf`).
- Authored the final integrated 55-case D4 fixture set and generator (`f729b4b`) and coordinated the shared case-allocation workflow.
- Built the team’s novice-friendly Colab D5(b) live-evaluation pipeline: private-key handling, 93-trial policy, repository-import fixes, duplicate-fragment handling, output-contract hardening, and tool-result protocol tests.
- Restored `_validate_parallel_batch()` and the dependency-aware parallel runner after an interface change, keeping `book_slot` isolated as claimed by the D2(c) evidence (`a498767`).
- Ran the assigned GPT-4o-mini v1 measurement used in the same-model D2(b) v1/v2 comparison.
- Consolidated and verified the audited D5 evidence in `87dca8d`; rebuilt the aggregate from immutable fragments and checked GitHub, Drive, and Colab consistency.

## GAO ZIHAN (G2602301K)

GitHub identity: `JeffGao` — 11 commits, 5 & 18 September 2026 (confirmed match).

- Uploaded the working D2/D3 code layer: `agent.py`, `tools.py`, `backends.py`, `guardrails.py`, `harness.py`, `config.py`, `prompt.py`, and `run_eval.py` (`ebfad64`, `e844ef8`).
- Wrote the D2(b) interface handoff and D3 guardrail docs (`docs/D2b_interface_handoff.md`, `docs/D3_guardrails.md`, `5d1157b`) and added `tests/test_submission_runner.py` (`57d38a2`).
- Measured D2(b) return-shape evidence (`scripts/measure_d2b_return_shape.py`, `results/d2b_return_shape_measurement.json`).
- Contributed 5–8 allocated D4 evaluation cases, including booking, red-flag, and hostile-instruction scenarios; reviewed scenario, trigger, expected outcome, and reason formatting.
- Ran the assigned Mistral Small 3.2 v2 D5(b) battery: 55 referrals / 93 trials, 48/93 passes (51.6%), and US$0.045354 provider-reported cost. Source: `results/live_runs/zihan-mistral-small32-v2-01.json`; the JSON owner field is `Gao Zihan`.
- Reviewed QA/evidence labels, including the distinction between live v1/v2 descriptor comparison, scripted return-shape evidence, and provider-reported versus scripted figures.
- Recorded and inserted the Tool Layer plus D2(c) video clip, including the six-field descriptor explanation and REF-5602 six-turn-to-four-turn parallel-scheduling evidence.
- Provided factual D2/D4/D5 evidence inputs and accuracy review for the report.

## HU ZIYI NICOLE (G2604013B)

GitHub identity: `ziyinicolehu` — 3 commits, 18 September 2026 (confirmed match).

- Built the D3 guardrail checklist: documentation, results, and script (`docs/D3(b)_guardrail_checklist.md`, `results/d3(b)_guardrail_results.json`, `scripts/d3(b)_guardrail_checklist.py`).
- Contributed 5–8 allocated D4 evaluation cases and ran the assigned GPT-4o-mini v2 D5(b) battery. Source: `results/live_runs/nicole-gpt4omini-v1-protocolfix-01.json`; its run metadata identifies the v2 prompt result and owner `Ziyi Nicole Hu`.
- Generated the report structure and contributed to Section 1 D0(a), Section 2 tool list/explanation, and Section 3 D4/D5 reporting.
- Generated the video template; helped assemble and export the final video; made and narrated guardrails, v1/v2, and D7 slides; and narrated the live negative-case demonstration.

## LU YAO (G2603916H)

GitHub identity: `judylou0117-stack` — 1 commit, 16 September 2026 (confirmed match).

- Edited `run_main.ipynb` (633 insertions / 342 deletions, `3d71907`).
- Contributed 5–8 allocated D4 evaluation cases; completed D0 Test 1 and ground-truth testing of expected outcomes.
- Ran the assigned Claude Haiku 4.5 D5(b) battery. Source: `results/live_runs/yao-claude-haiku45-v2-02.json`; JSON owner: `LU YAO`.
- Completed the D6 three-layer cost-to-serve analysis for Claude Haiku 4.5 and Mistral Small 3.2: per-task model cost, expected human fallback cost, monthly cost, ±10 percentage-point sensitivity, cheap-model break-even success rate, and model comparison.
- Prepared the live-model battery presentation explanation and the D6 findings; presented the complete aggregate table rather than selected favourable results.
- Ran the D7 test, reviewed its observed result, and updated relevant documentation.

## XU JUNJUN (G2603439G)

GitHub identity: `xjj15750747537` — repository creator (`4dba0b8`, initial `README.md`).

- Contributed 5–8 allocated D4 evaluation cases, including normal and negative cases with code and judgement checks.
- Ran the assigned Gemini Flash v2 D5(b) live-model battery and collected pass-rate, turns, token usage, and provider-reported cost evidence used in D6. Source: `results/live_runs/junjun-geminiflashlatest-v2-05.json`; JSON owner: `junjun`.
- Contributed D0(b) Test 2 by calculating implied per-step reliability from measured pass rate and median turns.
- Contributed D4/D5(b) evaluation reporting and D6 cost-to-serve analysis: token/turn/success-rate measurements, cost-lever comparisons, sensitivity, break-even analysis, and proposed cost-control limits.
- Prepared and narrated the Cost to Serve video section, covering observation size, parallel execution, token usage, reliability, proposed usage limits, and the cost conclusion.

## YOO SEUNGMIN (G2606541G)

GitHub identity: `usmin1004` — 17 commits, 18–19 September 2026 (confirmed match).

- Built the D2(c) full-set verification script, raw output, and summary (`scripts/verify_d2c_full_set.py`, `results/d2c_full_set_*`, `docs/D2C_FULL_SET_SUMMARY.md`); resolved the REF-5602 schedule discrepancy and locked the 6-sequential/4-parallel production schedule with a regression test.
- Built the D2(b) v1/v2 tokens-per-call verification, including turns and positive/negative breakdown; built the D7 loop-failure and gate-failure ablation scripts.
- Contributed 5–8 allocated D4 evaluation cases and ran the assigned DeepSeek Chat v3.1 D5(b) battery. Source: `results/live_runs/min-deepseek-chat-v3.1.json`; JSON owner: `Seungmin Yoo`.
- Contributed report Sections 1 D0(c), 2 (v1/v2 descriptor rewrite and sequential/parallel comparison), 5 (two failures), and 6 (what we would not deploy).
- Led the final report pass with Nicole: table numbering, captions, Word table of contents, footer, and trimming to meet the 2,000-word cap.
- Narrated the D4 video segment.

## Note — D5(b) source attribution

The repository preserves 14 immutable D5 raw JSON fragments because reruns, protocol-fix runs, and a superseded duplicate remain available for audit. File count is therefore not an even measure of contribution.

For the six designated primary live-model runs used in Table 3.1, responsibility is distributed as one assigned primary run per member. The JSON `owner` field identifies the actual operator. Commit `87dca8d` was a consolidation commit by Chang, so its commit author is not used as evidence that Chang ran every model; per-file owner metadata and run dates provide that attribution.
