#!/usr/bin/env python3
"""
D7 — SECOND FAILURE, TOOL-INTERFACE LAYER: the autonomy gate.

Ablation: Guardrails.gate() patched to always return True (the gate
passes every action unconditionally), same as if the "front the
irreversible step" check in agent.py were simply deleted.

Tested under AUTONOMY = "suggest", whose whole point is: never act
autonomously, hold every irreversible action for a human. With the
gate deleted, book_slot (the irreversible step) fires anyway.

Everything below runs on the SCRIPTED backend - free, deterministic,
no API key.
"""
import config
config.AUTONOMY = "suggest"

import harness
from guardrails import Guardrails

key = harness.load_key("B")

# ---- BEFORE: working agent, gate in place -------------------------------
before_results, _ = harness.run_set(problem="B")
print("\n----- BEFORE (gate in place, autonomy=suggest) -----")
before_report = harness.report(before_results)

# ---- AFTER: gate deleted -------------------------------------------------
real_gate = Guardrails.gate
Guardrails.gate = lambda self, action_name, payload, approve=None: True
try:
    after_results, _ = harness.run_set(problem="B")
    print("\n----- AFTER (gate deleted, autonomy=suggest) -----")
    after_report = harness.report(after_results)
finally:
    Guardrails.gate = real_gate

booked_before = sum(1 for r in before_results if r["record"]["decision"] == "book")
booked_after = sum(1 for r in after_results if r["record"]["decision"] == "book")
held_before = sum(1 for r in before_results if r["record"]["stopped_by"] == "gate_held")
held_after = sum(1 for r in after_results if r["record"]["stopped_by"] == "gate_held")

print("=" * 68)
print("SUMMARY FOR THE REPORT (D7, failure 2 / tool interface)")
print("=" * 68)
print("                        BEFORE (gate on)   AFTER (gate deleted)")
print("trials                   %6d              %6d" % (before_report["trials"], after_report["trials"]))
print("code-check pass rate    %6.1f%% (%d/%d)     %6.1f%% (%d/%d)" % (
    100*before_report["pass_rate"], before_report["passed"], before_report["trials"],
    100*after_report["pass_rate"], after_report["passed"], after_report["trials"]))
print("held for approval        %6d              %6d" % (held_before, held_after))
print("irreversible bookings    %6d              %6d" % (booked_before, booked_after))
