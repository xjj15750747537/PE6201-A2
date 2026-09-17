# D2(c): dependency-aware multi-tool turns

## Scope

D2(c) extends the submitted hand-written runner (`run_eval.py -> agent.py -> tools.py`) so one model turn can contain multiple Action calls. The runner executes an approved batch in a bounded thread pool while preserving declared action order in the trace. This document and `scripts/run_d2c_comparison.py` use the same Problem B tool names as `tools.py`; the retired `src/` workbook prototype is not submission evidence.

The policy in src/dependency_policy.py prevents speculative batching:

| State relationship | Execution rule |
|---|---|
| `get_referral` establishes patient and specialty identifiers. | Run alone. |
| `check_referral_criteria`, `lookup_patient`, and `as_of` are independent reads once the referral identifiers are known. | May share one parallel turn. |
| `get_clinic_slots` depends on criteria and the legal window, and must not run after an escalation, missing-test, or duplicate outcome. | Run alone. |
| `book_slot` is the gated write-like local action. | Run alone after all deterministic checks. |

## Controlled comparison

`scripts/run_d2c_comparison.py` compares the deterministic booked case `REF-5602` in two schedules. Both call the same six current tools against the real fixture data, produce the same local booking result, and make no real appointment.

| Schedule | Tool turns | Input tokens | Output tokens | Estimated cost |
|---|---:|---:|---:|---:|
| Sequential | 6 | 37,800 (scripted estimate) | 840 (scripted estimate) | USD 0.004116 (scripted estimate) |
| Dependency-aware parallel | 4 | 21,000 (scripted estimate) | 600 (scripted estimate) | USD 0.002340 (scripted estimate) |

The parallel schedule combines only the independent criteria, duplicate, and clock reads. It removes two decision points in this controlled trace. Its token and cost fields are scripted estimates, not live-model measurements. It does not claim parallelism is always cheaper: unnecessary branches can increase tool work, context size, and review risk.

## Correctness claim and D4 boundary

For the controlled case, the script asserts the same final decision (`book`) and the same six-call coverage. This is a baseline implementation result, not the final assignment-wide correctness claim. D4 must rerun the same evaluation set under both schedules, report pass rates, and explain any discrepancy before the final submission states that correctness is unchanged.

Run:

    python3 scripts/run_d2c_comparison.py
    python3 -m unittest discover -s tests -v
