# D0 — Why an Agent for Outpatient Referral Coordination

## Scope

Problem B has three fixed outcomes: book a slot, request named missing information, or escalate to a triage nurse. The team automates this routing rule; it does not redesign clinical policy. The system will be one ReAct agent over local fixtures. A booking is only a local decision log, but it remains the irreversible business action and must be gated immediately before the write.

## Ladder justification

| Rung | Why it is insufficient or appropriate |
|---|---|
| Single call | Cannot access referral, specialty, patient, or slot records. |
| Prompt chain | Uses a fixed path even when a red flag or missing test should stop the run early. |
| Routing | Selects an initial lane but not the evidence-gathering sequence within it. |
| Parallelisation | Groups independent calls but cannot decide whether later calls are needed. |
| Orchestrator-workers | Adds coordination cost and failure surface without a necessary capability. |
| Evaluator-optimiser | Improves prose but cannot prove a red flag, duplicate, test, or legal slot exists. |
| Agent | Selects tools at runtime, receives record-backed observations, stops early, and acts only after the booking gate passes. |

The agent is justified because the next tool depends on prior observations. A red-flag referral escalates without slot search; a referral missing a mandatory test requests the named test and stops; a routine referral may need specialty, patient, urgency, and slot evidence before it reaches the gated action.

## Architecture test

| Question | Answer |
|---|---|
| Who selects retrieval? | The model selects the next tool at runtime from the referral and observations. |
| Can it loop? | Yes; additional record or slot queries may be needed after earlier evidence. |
| Can it change the world? | Yes in business meaning: book_slot writes a simulated appointment decision. |

The governance cliff is the first booking write, not retrieval.

## Ground truth at machine speed

| System of record | What it verifies |
|---|---|
| referrals.json | Referral facts, free text, attached tests |
| specialties.json | Mandatory tests, red flags, treatment scope |
| patients.json | Future same-specialty appointments |
| urgency_bands.json | Permitted booking window |
| clinic_slots.json | Capacity inside a clinic, band, date, and time |
| action log | Duplicate booking actions |

## Reliability plan

D4 will measure whole-run pass rate P and D7 median turns T. We will report implied per-step reliability: s = P^(1/T). This is a diagnostic, not a constant. Failure clustering after one tool indicates a step-quality problem; unnecessary repeated observations indicate a step-count problem.

## Pre-build boundary

The accompanying profiler is read-only. It checks data connectivity only; it does not route cases, generate labels, call a model, or write bookings. Agent implementation starts only after these D0 artefacts are committed.