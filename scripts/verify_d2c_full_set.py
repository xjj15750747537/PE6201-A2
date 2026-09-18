"""D2(c) full evaluation-set verification: sequential vs dependency-aware
parallel, across all 55 Problem B cases / 93 trials.

WHY THIS SCRIPT EXISTS
-----------------------
`scripts/run_d2c_comparison.py` proves the dependency-aware parallel
schedule for exactly one case (REF-5602). `docs/D2c_parallelism.md` itself
says that is "a baseline implementation result, not the final
assignment-wide correctness claim" and that D4's evaluation set must be
rerun under both schedules before the report can say correctness is
unchanged. This script does that rerun.

WHAT IT REUSES, ON PURPOSE
---------------------------
- `problem_b_scripts.build_script()` is the actual, already-submitted
  sequential decision path used by the scripted D4/D5(a) battery for every
  Problem B case except REF-5602 (see backends.SCRIPTS). Its step list IS
  the sequential schedule: reusing it (instead of re-deriving decisions by
  hand) means this script cannot silently disagree with the harness about
  what the agent decides.
- `harness.code_check()` is the same code check the submitted harness uses
  to grade every run against `expected_outcomes_B.json`. Both schedules are
  graded with it, independently, and also compared against each other.
- `harness._is_negative()` / trial counts follow the same convention as
  `harness.run_set()`: ordinary cases get 1 trial, negative cases get 3
  (both schedules are scripted/deterministic, so repeated trials of the
  same case are identical by construction; they are still counted
  individually below because that is the trial-counting convention the
  rest of the report uses).

A CORRECTION THIS SCRIPT MAKES OVER AN EARLIER DRAFT
------------------------------------------------------
An earlier version of this comparison assumed check_referral_criteria,
lookup_patient and as_of are bundled into one parallel turn for EVERY
case. That is wrong. `build_script()` only calls lookup_patient for cases
that pass the criteria pre-checks (no untrusted instruction text, no red
flag, right department, no missing mandatory test). A case that escalates
or asks at the criteria step never reaches lookup_patient, so there is
nothing to bundle for it, and its parallel schedule is identical to its
sequential one. This script derives the parallel schedule from the real
steps `build_script()` returns, not from an assumption about which steps
exist.

A KNOWN OPEN QUESTION THIS SCRIPT DOES NOT SILENTLY RESOLVE
--------------------------------------------------------------
REF-5602 currently has THREE not-quite-matching schedules in this
repository: `scripts/run_d2c_comparison.py` (as_of as its own tool call,
one get_clinic_slots call), `backends.SCRIPTS["REF-5602"]` (the real
production script: no as_of tool call, TWO get_clinic_slots calls on split
windows), and the generic `build_script()` path this file uses (no as_of
tool call, ONE get_clinic_slots call, fully sequential unless bundled by
the rule below). This script always uses the `build_script()` path for
consistency across all 55 cases, so its REF-5602 numbers will not exactly
match `run_d2c_comparison.py`'s. Flagged for the team; not resolved here.

DEPENDENCY RULE APPLIED (matches docs/D2c_parallelism.md)
------------------------------------------------------------
get_referral runs alone. check_referral_criteria and lookup_patient may
share one turn IF the case's sequential trace reaches lookup_patient at
all. get_clinic_slots and book_slot each run alone.
"""
import csv
import json
import statistics
import sys

import config
import harness
from problem_b_scripts import build_script

CSV_PATH = "d2c_full_set_raw_trials.csv"
SUMMARY_PATH = "d2c_full_set_summary.json"


def sequential_schedule(steps):
    """Tool-turn count and call names in order, straight from build_script()."""
    calls = [step["calls"][0][0] for step in steps if "calls" in step]
    return calls


def parallel_schedule(calls):
    """Apply the documented dependency rule to a sequential call list.

    Only check_referral_criteria + lookup_patient (when lookup_patient is
    present at all) are bundled into one turn. Everything else keeps its
    own turn, in the same order.
    """
    if "lookup_patient" in calls and "check_referral_criteria" in calls:
        i_crit = calls.index("check_referral_criteria")
        i_pat = calls.index("lookup_patient")
        if i_pat == i_crit + 1:
            # Turns: everything up to and including get_referral, one
            # bundled turn for [criteria, patient], then whatever follows.
            before = calls[:i_crit]
            after = calls[i_pat + 1:]
            return before + [("check_referral_criteria", "lookup_patient")] + after
    # Nothing to bundle: parallel schedule equals sequential schedule.
    return list(calls)


def scripted_usage(tool_turns):
    """Mirrors backends.ScriptedBackend.token_estimate exactly.

    token_estimate(transcript) is called once per model move (every tool
    turn AND the concluding move), returning 1800 + 600*len(transcript) for
    input and a flat 120 for output. transcript grows by exactly 2 entries
    per move (one assistant entry, one user/tool-result entry), so the k-th
    move (0-indexed) sees len(transcript) == 2*k, i.e. input = 1800 +
    1200*k. Summed over tool_turns tool turns + 1 concluding move:
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
        steps = build_script(cid)
        if steps is None:
            print("  SKIP %s - build_script returned None" % cid, file=sys.stderr)
            continue
        final = steps[-1]["final"]
        seq_calls = sequential_schedule(steps)
        par_calls = parallel_schedule(seq_calls)

        seq_turns = len(seq_calls)
        par_turns = len(par_calls)
        seq_record = build_record(final, seq_turns)
        par_record = build_record(final, par_turns)

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
            "seq_turns": seq_turns, "par_turns": par_turns,
            "bundled": seq_turns != par_turns,
            "seq_pass": seq_pass, "par_pass": par_pass, "cross_match": cross_match,
        })

        for trial in range(1, n_trials + 1):
            for mode, turns, pass_, fails in (
                ("sequential", seq_turns, seq_pass, seq_fails),
                ("parallel", par_turns, par_pass, par_fails),
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
            "median_turns": statistics.median(turns_list) if turns_list else None,
            "worst_case_turns": max(turns_list) if turns_list else None,
            "total_input_tokens": sum(r["input_tokens"] for r in sub),
            "total_output_tokens": sum(r["output_tokens"] for r in sub),
            "total_cost_usd": round(sum(r["cost_usd"] for r in sub), 4),
        }

    cross_matches = sum(1 for c in case_summ for _ in range(c["n_trials"]) if c["cross_match"])
    total_trials_per_schedule = sum(c["n_trials"] for c in case_summ)
    bundled_cases = sum(1 for c in case_summ if c["bundled"])

    summary = {
        "cases": len(case_summ),
        "trials_per_schedule": total_trials_per_schedule,
        "bundled_cases": bundled_cases,
        "unbundled_cases": len(case_summ) - bundled_cases,
        "sequential": stats_for("sequential"),
        "parallel": stats_for("parallel"),
        "cross_schedule_match_trials": cross_matches,
        "cross_schedule_match_rate": cross_matches / total_trials_per_schedule,
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
