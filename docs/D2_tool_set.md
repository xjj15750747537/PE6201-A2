# D2(a) Tool Set Rationale — Problem B

## Purpose

This document selects the smallest defensible tool set for the outpatient referral-coordination agent. The tool layer is an interface for the model, not a catalogue of every fixture file. A tool is retained only when a specific task fails without it, its boundary is distinguishable from its neighbours, and its prompt and safety cost is justified.

This is the D2(a) design baseline. D2(b) will provide typed six-field descriptors for every retained tool. D4 will run the removal experiments described below; no planned experiment is presented here as an observed result.

## Decision boundary

The system may reach one of three outcomes: book, request information, or escalate. A booking is only a local, gated booking-intent record. It must not contact a patient or make a real appointment.

The deterministic layer, rather than a separate agent tool, will perform fixture joins, date arithmetic, capacity filtering, and the policy checks used by the action gate. This prevents the agent from choosing between overlapping micro-tools for simple, testable operations.

## Working tool set

| Tool | Does a task actually fail without it? | Could the model confuse it with a neighbour? | Why it earns its place |
|---|---|---|---|
| `get_referral` | Yes. The agent cannot obtain the patient ID, specialty, attached tests, or clinical text needed to start a case. | No. It retrieves one referral; it neither assesses it nor searches appointments or capacity. | It is the required entry point, so it runs alone. |
| `check_referral_criteria` | Yes. The agent cannot establish hostile text, red flags, specialty fit, mandatory-test status, or urgency band without it. | No. It reports protocol facts; it does not make a routing decision or search availability. | It combines checks that are always required and whose order can stop the run, reducing overlapping micro-tools. |
| `lookup_patient` | Yes. The agent cannot establish whether a future same-specialty appointment already exists. | No. It reads patient/appointment facts; `get_clinic_slots` reads available capacity. | The duplicate rule cannot be inferred from the referral alone. |
| `as_of` | Yes. The legal urgency window must use the shared fixture clock rather than an assumed date. | No. It returns one fixed date and does not interpret the referral. | It prevents an apparently plausible booking against a wrong clock. |
| `get_clinic_slots` | Yes. A book outcome cannot show an available slot of the required specialty and urgency band inside the permitted window without it. | No. It searches capacity; it never reports a patient's existing appointment. | Its required `band` argument prevents an accidental wrong-band booking. |
| `book_slot` | Yes. Without one gated write-like operation, the system can only recommend a booking and cannot demonstrate the required act outcome. | No. It records a supported local booking only after evidence is gathered. | It is the only write-like action and must run alone behind the autonomy gate. |

## Tools deliberately not shipped

| Candidate tool | Why it was cut or absorbed | Evidence required before final submission |
|---|---|---|
| get_specialty_rules | Absorbed into `check_referral_criteria`. A separate specialty-rules lookup would expose policy fragments without performing the required deterministic checks. | A D4 removal comparison must show that the retained combined criteria check preserves required outcomes. |
| get_contact | Not exposed as an agent lookup. A booking intent may record an approved contact method through deterministic, local code without exposing contact details on request or escalation paths. | A D4 booking case must confirm that the required local record is complete without a separate model-visible contact tool. |
| classify_urgency | Not a tool. Trigger matching and window calculation are deterministic policy checks that can be tested outside the loop. | Unit tests must cover urgent, soon, routine, and no-slot boundary cases. |
| search_fixture_data | Rejected. It has no narrow task contract and overlaps every domain lookup. | Negative evaluation cases must show that the retained narrow tools make unsupported browsing unnecessary. |
| notify_patient | Rejected. The assignment requires a local action log, not real messaging or booking. | The action-gate tests must show that no external contact is possible. |

## Tool-reduction sequence

Before adding any new tool, the team will apply the required sequence:

1. Widen an existing tool's parameters instead of adding a sibling.
2. Return the additional necessary data from an existing call instead of adding another lookup.
3. Move deterministic work before or after the agent loop.
4. Add a tool only when the first three options make a required task fail.

The repository will record the case, removed or added tool, observed failure or retained outcome, turns, and prompt-token effect for each decision.

## D4 validation plan

Each retained tool must survive a removal test. Remove the tool or replace it with its nearest alternative, re-run the affected evaluation cases, and record the task that fails. The evaluation must also check that retained tools are not selected for a neighbour's task.

The final D2(a) table will replace each planned validation statement with its observed case identifier and result.
