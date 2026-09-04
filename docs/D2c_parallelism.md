# D2(c): dependency-aware multi-tool turns

## Scope

D2(c) extends the hand-written ReAct runner so one model turn can contain multiple Action calls. The runner executes every action, appends every observation, and in parallel mode uses a bounded thread pool while preserving declared action order in the trace.

The policy in src/dependency_policy.py prevents speculative batching:

| State relationship | Execution rule |
|---|---|
| get_referral_context establishes patient, specialty, and urgency state. | Run alone. |
| get_existing_appointments and find_eligible_slots read independent fixture views after context. | May share one parallel turn. |
| stage_booking_intent is a gated write-like local action. | Run alone after deterministic checks. |

## Controlled comparison

scripts/run_d2c_comparison.py compares a deterministic booked-case script in two schedules. Both use the same four tools, fixture observations, final decision, and staged (not real) booking behavior.

| Schedule | Tool turns | Input tokens | Output tokens | Estimated cost |
|---|---:|---:|---:|---:|
| Sequential | 4 | 7,200 | 170 | USD 0.02415 |
| Dependency-aware parallel | 3 | 6,000 | 140 | USD 0.02010 |

The parallel schedule combines only the independent duplicate check and slot search. It removes one decision point and reduces the scripted token and cost totals in this controlled trace. It does not claim parallelism is always cheaper: unnecessary branches can increase tool work, context size, and review risk.

## Correctness claim and D4 boundary

For the controlled case, the script asserts the same final decision (book) and the same four-tool coverage. This is a baseline implementation result, not the final assignment-wide correctness claim. D4 must rerun the same evaluation set under both schedules, report pass rates, and explain any discrepancy before the final submission states that correctness is unchanged.

Run:

    python3 scripts/run_d2c_comparison.py
    python3 -m unittest discover -s tests -v
