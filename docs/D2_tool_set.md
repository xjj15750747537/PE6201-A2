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
| get_referral_context | Yes. The agent cannot obtain the named referral, the associated specialty rules, or the clinical text needed to start a case. | No. It retrieves case facts and rules; it does not retrieve a patient's appointment history or offer a slot. | It is the entry point. Combining referral and specialty context removes an otherwise overlapping specialty-rules lookup. |
| get_existing_appointments | Yes. The agent cannot establish whether the patient already has a future appointment in the same specialty. | No. It answers what the patient already has; find_eligible_slots answers what can be offered now. | The duplicate-appointment rule cannot be safely inferred from the referral alone. |
| find_eligible_slots | Yes. A book outcome cannot show an available slot of the required specialty and urgency band inside the permitted window. | No. It searches available capacity; it never reports an existing patient appointment. | It provides the external fact needed to support the book branch and excludes full, wrong-band, or out-of-window slots. |
| stage_booking_intent | Yes. Without one gated write, the system can only recommend a booking and cannot demonstrate the required act outcome. | No. It records a supported local intent after the decision; it does not search or decide. | It is the only write. One gate protects the whole agent and prevents direct booking or patient contact. |

## Tools deliberately not shipped

| Candidate tool | Why it was cut or absorbed | Evidence required before final submission |
|---|---|---|
| get_specialty_rules | Absorbed into get_referral_context. After the referral identifies a specialty, a separate call would retrieve context required by the same decision. | A D4 removal comparison must show that the merged context preserves the required outcomes while using fewer tool definitions and turns. |
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
