#!/usr/bin/env python3
"""
D7 — run the action-de-duplication ablation across the WHOLE eval set
(the same failure shape as demo_loop_failure.py, generalised to every
case), to get the aggregate numbers the report checklist asks for:
median turns, worst case turns, # runs hitting the step cap, and pass
rate, BEFORE and AFTER removing the guard.

BEFORE = every case's normal script, guard in place (the working agent).
AFTER  = every case's script with one step repeated (a model that
         forgot it already asked), guard REMOVED so the repeat is not
         caught.
"""
import copy

import backends
import harness
from guardrails import Guardrails
from problem_b_scripts import build_script

PROBLEM = "B"
cases = harness.load_cases(PROBLEM)

# Resolve and cache the normal (unmodified) script for every case.
normal_scripts = {}
for cid in cases:
    steps = backends.SCRIPTS.get(cid)
    if steps is None:
        steps = build_script(cid)
    normal_scripts[cid] = steps


def looping_script(cid):
    steps = copy.deepcopy(normal_scripts[cid])
    repeat = copy.deepcopy(steps[1])
    repeat["thought"] = "Let me check the criteria again to be sure."
    return steps[:2] + [repeat, repeat] + steps[2:]


# ---- BEFORE: working agent, guard in place, normal scripts -------------
for cid in cases:
    backends.SCRIPTS[cid] = normal_scripts[cid]
before_results, _ = harness.run_set(problem=PROBLEM)
print("\n\n----- BEFORE (guard on, normal scripts) -----")
before_report = harness.report(before_results)

# ---- AFTER: repeated step injected + de-duplication guard removed -----
for cid in cases:
    backends.SCRIPTS[cid] = looping_script(cid)
real_check = Guardrails.check_duplicate
Guardrails.check_duplicate = lambda self, tool, args: None
try:
    after_results, _ = harness.run_set(problem=PROBLEM)
    print("\n\n----- AFTER (repeat injected, guard removed) -----")
    after_report = harness.report(after_results)
finally:
    Guardrails.check_duplicate = real_check
    for cid in cases:
        backends.SCRIPTS[cid] = normal_scripts[cid]

print("=" * 68)
print("SUMMARY FOR THE REPORT (D7, failure 1 / loop)")
print("=" * 68)
worst_before = max(r["record"]["turns"] for r in before_results)
worst_after = max(r["record"]["turns"] for r in after_results)
cap_before = sum(1 for r in before_results if r["record"]["stopped_by"] == "step_cap")
cap_after = sum(1 for r in after_results if r["record"]["stopped_by"] == "step_cap")
print("                 BEFORE (guard on)   AFTER (guard removed)")
print("trials            %6d               %6d" % (before_report["trials"], after_report["trials"]))
print("pass rate        %6.1f%% (%d/%d)      %6.1f%% (%d/%d)" % (
    100 * before_report["pass_rate"], before_report["passed"], before_report["trials"],
    100 * after_report["pass_rate"], after_report["passed"], after_report["trials"]))
print("median turns     %6s              %6s" % (before_report["median_turns"], after_report["median_turns"]))
print("worst case turns %6s              %6s" % (worst_before, worst_after))
print("hit step cap     %6d               %6d" % (cap_before, cap_after))
print("total cost USD   %9.4f           %9.4f" % (before_report["cost_usd"], after_report["cost_usd"]))
