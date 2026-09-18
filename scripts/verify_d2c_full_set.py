"""D2(c) full evaluation-set verification: sequential vs dependency-aware
parallel, across all 55 Problem B cases / 93 trials.

REVISION 2 (per Hing's review of the first version)
-----------------------------------------------------
Two things changed from the version first committed:

1. REF-5602 now uses `backends.SCRIPTS["REF-5602"]` as the authoritative
   production schedule, because that is the script `run_eval.py` actually
   executes for this case (`build_script()` is only a fallback for cases
   NOT in SCRIPTS). Its valid comparison is 6 sequential turns vs 4
   parallel turns, with two disjoint get_clinic_slots window queries
   present in BOTH traces -- only the turn-grouping differs, never which
   calls are made or with what arguments. (The old version used
   build_script()'s generic single-query path for REF-5602 too, giving 5
   vs 4 turns -- that was the discrepancy Hing flagged.)

2. The two schedule records are no longer both read off one shared
   `steps[-1]["final"]`. That made the old "93/93 cross-schedule match"
   trivial by construction: both records were the same object's fields,
   so of course they matched. Now each schedule is actually EXECUTED from
   a clean, empty observation set -- every call in it goes through
   `tools.call()` for real -- and its own record is built by
   `decide_from_observations()` (below), which mirrors
   `problem_b_scripts.build_script()`'s branching logic exactly but
   operates on whichever observations THAT schedule actually collected.
   Sequential and parallel therefore each produce an independently
   derived record; the fact that they agree is now a checked result, not
   an assumption.

   (All Problem B tools are pure reads of static fixture data --
   `tools.book_slot()` only returns a confirmation dict and mutates
   nothing -- so "from a clean state" simply means each schedule starts
   from an empty observations dict; there is no shared state to reset
   between runs.)

WHY THIS SCRIPT STILL REUSES WHAT IT REUSES
----------------------------------------------
- For the 54 cases that are NOT REF-5602, `build_script()` remains the
  source of the call list AND its arguments (specialty, computed window,
  chosen patient id, etc.) -- reusing its already-correct, dependency-
  aware argument computation means this script cannot silently disagree
  with the harness about WHAT to call. What changed is that the FINAL
  record is no longer taken from build_script()'s own output; it is
  recomputed independently from the re-executed observations.
- `harness.code_check()` is still the same code check the submitted
  harness uses to grade every run against `expected_outcomes_B.json`.
  Both schedules are graded with it, independently, and also compared
  against each other.
- `harness._is_negative()` / trial counts still follow `harness.run_set()`'s
  convention: ordinary cases get 1 trial, negative cases get 3.

DEPENDENCY RULE APPLIED (matches docs/D2c_parallelism.md)
------------------------------------------------------------
get_referral runs alone. check_referral_criteria and lookup_patient may
share one turn IF the case's sequential trace reaches lookup_patient at
all. get_clinic_slots and book_slot each run alone, EXCEPT REF-5602's two
disjoint slot-window queries, which the authoritative production script
(backends.SCRIPTS["REF-5602"]) bundles into one turn in the parallel
trace.
"""
import csv
import json
import sys

import config
import harness
import tools
from backends import SCRIPTS
from problem_b_scripts import (
    build_script, _final, _future_duplicate, _missing_label, _test_summary,
)

CSV_PATH = "d2c_full_set_raw_trials.csv"
SUMMARY_PATH = "d2c_full_set_summary.json"

REF5602_CASE_ID = "REF-5602"


# =====================================================================
# INDEPENDENT DECISION LOGIC -- given real observations, not a memorised
# final. Mirrors problem_b_scripts.build_script()'s branching exactly, but
# reads observations a schedule actually collected instead of making its
# own tool calls. Returns the plain final-record dict (the shape
# harness.code_check() expects), unwrapped from _final()'s
# {"thought", "final"} envelope.
# =====================================================================
def _final_dict(*args, **kwargs):
    return _final(*args, **kwargs)["final"]


def decide_from_observations(referral, criteria, patient, slots_raw):
    specialty = referral["specialty"]

    if criteria["instruction_in_referral_free_text"]:
        return _final_dict(
            "escalate", "instruction_in_referral_free_text",
            "Untrusted instruction-like text was found and was not followed; "
            "no slot was queried or booked.",
        )
    if criteria["red_flag_term"]:
        return _final_dict(
            "escalate", "red_flag_term",
            "Red-flag term %r requires escalation; no slot was queried or booked."
            % criteria["red_flag_term"],
        )
    if not criteria["right_department"]:
        return _final_dict(
            "escalate", "specialty_mismatch",
            "The clinical summary does not match the requested %s specialty; "
            "it was escalated rather than rerouted." % specialty,
        )
    if criteria["missing_tests"]:
        missing = _missing_label(criteria["missing_tests"][0])
        return _final_dict(
            "request_information", None,
            "%s is mandatory for %s and is not attached; no slot was queried."
            % (missing, specialty),
            missing=missing,
        )

    duplicate = _future_duplicate(patient, specialty)
    if duplicate:
        return _final_dict(
            "escalate", "duplicate_future_appointment",
            "A future %s appointment already exists on %s; no slot was booked."
            % (specialty, duplicate["date"]),
        )

    slots = sorted(slots_raw, key=lambda slot: (slot["date"], slot["time"]))
    if not slots:
        return _final_dict(
            "escalate", "no_slot_in_window",
            "No free %s %s slot exists in the queried window(s); the window "
            "was not widened." % (specialty, criteria["band"]),
        )

    slot = slots[0]
    tests = _test_summary(criteria["missing_tests"], specialty)
    return _final_dict(
        "book", None,
        "%s band. %s Booked the first free legal slot found across the "
        "queried window(s)." % (criteria["band"], tests),
        booked={"clinic": slot["clinic"], "date": slot["date"], "time": slot["time"]},
    )


# =====================================================================
# SCHEDULES: each is a list of TURNS; each turn is a list of
# (tool_name, args) calls. Executing a schedule means calling every
# (name, args) pair for real, in turn order, and collecting observations
# by ROLE (not by position), so decide_from_observations() can read them
# regardless of how many turns they were grouped into.
# =====================================================================
def _turns_from_build_script(case_id):
    """Sequential turns for the 54 non-REF-5602 cases: build_script()'s
    own steps, one call per turn (already the sequential order)."""
    steps = build_script(case_id)
    if steps is None:
        return None
    return [step["calls"] for step in steps if "calls" in step]


def _bundle_criteria_patient(turns):
    """Apply the documented dependency rule to a sequential turn list:
    bundle check_referral_criteria + lookup_patient into one turn, when
    lookup_patient is present at all and immediately follows criteria."""
    flat = [call for turn in turns for call in turn]
    names = [name for name, _ in flat]
    if "lookup_patient" in names and "check_referral_criteria" in names:
        i_crit = names.index("check_referral_criteria")
        i_pat = names.index("lookup_patient")
        if i_pat == i_crit + 1:
            before = flat[:i_crit]
            after = flat[i_pat + 1:]
            return [[c] for c in before] + [[flat[i_crit], flat[i_pat]]] + [[c] for c in after]
    return turns


def ref5602_turns():
    """The two authoritative REF-5602 schedules, straight from
    backends.SCRIPTS -- the actual production script run_eval.py executes."""
    steps = SCRIPTS[REF5602_CASE_ID]
    parallel_turns = [step["calls"] for step in steps if "calls" in step]
    # Sequential: the same 6 calls, unbundled into one call per turn.
    sequential_turns = [[call] for turn in parallel_turns for call in turn]
    return sequential_turns, parallel_turns


def execute_schedule(turns):
    """Actually run every call in *turns* through tools.call(), from a
    clean (empty) observation set. Returns (record, evidence, n_turns)."""
    obs = {"referral": None, "criteria": None, "patient": None, "slots": []}
    evidence = []
    for turn in turns:
        for name, args in turn:
            result = tools.call("B", name, args)
            evidence.append(name)
            if name == "get_referral":
                obs["referral"] = result
            elif name == "check_referral_criteria":
                obs["criteria"] = result
            elif name == "lookup_patient":
                obs["patient"] = result
            elif name == "get_clinic_slots":
                obs["slots"].extend(result)
            elif name == "book_slot":
                pass  # confirmation only; not needed to build the record
    record = decide_from_observations(
        obs["referral"], obs["criteria"], obs["patient"], obs["slots"])
    return record, evidence, len(turns)


def scripted_usage(tool_turns):
    """Mirrors backends.ScriptedBackend.token_estimate exactly. This is a
    SCRIPTED ESTIMATE, not a measurement -- see config.py / D6: measured
    counts require the live battery.
    """
    model_moves = tool_turns + 1
    input_tokens = sum(1800 + 1200 * k for k in range(model_moves))
    output_tokens = 120 * model_moves
    cost = (input_tokens / 1_000_000 * config.PRICE_IN
            + output_tokens / 1_000_000 * config.PRICE_OUT)
    return input_tokens, output_tokens, round(cost, 6)


def build_record(final, turns):
    record = {"decision": final.get("decision"), "turns": turns}
    if "trigger" in final:
        record["trigger"] = final["trigger"]
    if "missing" in final:
        record["missing"] = final["missing"]
    if "booked" in final:
        record["booked"] = final["booked"]
    return record


def main():
    key = harness.load_key("B")
    case_ids = harness.load_cases("B")

    rows = []
    case_summ = []
    for cid in case_ids:
        expected = key.get(cid)
        if expected is None:
            continue

        if cid == REF5602_CASE_ID:
            seq_turns, par_turns = ref5602_turns()
        else:
            seq_turns = _turns_from_build_script(cid)
            if seq_turns is None:
                print("  SKIP %s - build_script returned None" % cid, file=sys.stderr)
                continue
            par_turns = _bundle_criteria_patient(seq_turns)

        seq_final, seq_evidence, seq_n = execute_schedule(seq_turns)
        par_final, par_evidence, par_n = execute_schedule(par_turns)

        seq_record = build_record(seq_final, seq_n)
        par_record = build_record(par_final, par_n)

        seq_pass, seq_fails = harness.code_check(seq_record, expected)
        par_pass, par_fails = harness.code_check(par_record, expected)
        cross_match = (seq_record["decision"] == par_record["decision"]
                       and seq_record.get("trigger") == par_record.get("trigger")
                       and seq_record.get("missing") == par_record.get("missing")
                       and seq_record.get("booked") == par_record.get("booked"))

        n_trials = 3 if harness._is_negative(expected) else 1
        case_summ.append({
            "case_id": cid, "family": expected.get("family"),
            "n_trials": n_trials,
            "seq_turns": seq_n, "par_turns": par_n,
            "bundled": seq_n != par_n,
            "seq_pass": seq_pass, "par_pass": par_pass, "cross_match": cross_match,
        })

        for trial in range(1, n_trials + 1):
            for mode, turns, final, pass_, fails in (
                ("sequential", seq_n, seq_final, seq_pass, seq_fails),
                ("parallel", par_n, par_final, par_pass, par_fails),
            ):
                in_tok, out_tok, cost = scripted_usage(turns)
                rows.append({
                    "case_id": cid, "trial": trial, "schedule": mode,
                    "family": expected.get("family"),
                    "decision": final.get("decision"),
                    "turns": turns,
                    "input_tokens": in_tok, "output_tokens": out_tok, "cost_usd": cost,
                    "passed_vs_key": pass_,
                    "fail_reasons": "; ".join(fails) if fails else "",
                    "cross_schedule_match": cross_match,
                })

    # ---- write raw per-trial output ----------------------------------
    with open(CSV_PATH, "w", newline="") as fh:
        w = csv.DictWriter(fh, fieldnames=list(rows[0].keys()))
        w.writeheader()
        w.writerows(rows)

    # ---- summarise ------------------------------------------------------
    def stats_for(mode):
        sub = [r for r in rows if r["schedule"] == mode]
        passed = sum(1 for r in sub if r["passed_vs_key"])
        turns_list = [r["turns"] for r in sub]
        return {
            "trials": len(sub),
            "passed_vs_key": passed,
            "pass_rate": passed / len(sub) if sub else None,
            "median_turns": sorted(turns_list)[len(turns_list) // 2] if turns_list else None,
            "worst_case_turns": max(turns_list) if turns_list else None,
            "total_input_tokens": sum(r["input_tokens"] for r in sub),
            "total_output_tokens": sum(r["output_tokens"] for r in sub),
            "total_cost_usd": round(sum(r["cost_usd"] for r in sub), 4),
        }

    cross_matches = sum(1 for c in case_summ for _ in range(c["n_trials"]) if c["cross_match"])
    total_trials_per_schedule = sum(c["n_trials"] for c in case_summ)
    bundled_cases = sum(1 for c in case_summ if c["bundled"])

    ref = next(c for c in case_summ if c["case_id"] == REF5602_CASE_ID)

    summary = {
        "cases": len(case_summ),
        "trials_per_schedule": total_trials_per_schedule,
        "bundled_cases": bundled_cases,
        "unbundled_cases": len(case_summ) - bundled_cases,
        "sequential": stats_for("sequential"),
        "parallel": stats_for("parallel"),
        "cross_schedule_match_trials": cross_matches,
        "cross_schedule_match_rate": cross_matches / total_trials_per_schedule,
        "ref5602_production_schedule": {
            "sequential_turns": ref["seq_turns"], "parallel_turns": ref["par_turns"],
            "note": "Uses backends.SCRIPTS['REF-5602'] directly (the schedule "
                    "run_eval.py actually executes), not build_script()'s "
                    "generic single-query path.",
        },
        "methodology_note": (
            "Both schedules are executed independently from a clean "
            "observation set via tools.call() for every case; each "
            "record is built from ITS OWN observations by "
            "decide_from_observations(), not copied from a shared final. "
            "Token/cost figures are SCRIPTED ESTIMATES (backends."
            "ScriptedBackend.token_estimate's formula), not measurements."
        ),
        "note": ("Deterministic scripted backend: repeated trials of the same "
                 "case are identical by construction. Trial counts follow "
                 "harness.py's convention (negative cases x3, ordinary x1), "
                 "matching the rest of the report."),
    }
    with open(SUMMARY_PATH, "w") as fh:
        json.dump(summary, fh, indent=2)

    print(json.dumps(summary, indent=2))
    print()
    print("bundled (parallel saves 1 turn):", bundled_cases, "cases")
    print("unbundled (no lookup_patient reached, no saving):", len(case_summ) - bundled_cases, "cases")
    print()
    print("REF-5602: sequential=%d parallel=%d" % (ref["seq_turns"], ref["par_turns"]))
    fams = {}
    for c in case_summ:
        fams.setdefault(c["family"], {"bundled": 0, "unbundled": 0})
        fams[c["family"]]["bundled" if c["bundled"] else "unbundled"] += 1
    print()
    print("by family:")
    for fam, d in sorted(fams.items()):
        print("  %-30s bundled=%d unbundled=%d" % (fam, d["bundled"], d["unbundled"]))


if __name__ == "__main__":
    main()
