"""Compare D2(c) schedules using the submitted Problem B tool interface.

This is deliberately a scripted, fixture-backed controlled experiment.  It
does not call a model and its token/cost fields are estimates under the same
instrumentation convention as the scripted runner.  Provider-reported D5(b)
numbers remain the only measured live-model cost evidence.
"""

from __future__ import annotations

import json
import sys
from concurrent.futures import ThreadPoolExecutor
from datetime import date, timedelta
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

import config
import tools


CASE_ID = "REF-5602"


def _execute(stages, parallel):
    """Run declared tool stages and retain the real fixture observations."""
    trace = []
    for stage in stages:
        if parallel and len(stage) > 1:
            with ThreadPoolExecutor(max_workers=len(stage)) as executor:
                results = list(executor.map(
                    lambda item: tools.call("B", item[0], item[1]), stage))
        else:
            results = [tools.call("B", name, args) for name, args in stage]
        trace.extend((name, args, result)
                     for (name, args), result in zip(stage, results))
    return trace, len(stages)


def _scripted_usage(tool_turns):
    """Mirror backends.ScriptedBackend.token_estimate for tool turns + final."""
    model_moves = tool_turns + 1
    input_tokens = sum(1800 + 1200 * index for index in range(model_moves))
    output_tokens = 120 * model_moves
    cost = (input_tokens / 1_000_000 * config.PRICE_IN
            + output_tokens / 1_000_000 * config.PRICE_OUT)
    return input_tokens, output_tokens, round(cost, 6)


def run_schedule(parallel):
    """Run REF-5602 through the current six-call Problem B schedule."""
    referral = tools.get_referral(CASE_ID)
    if referral is None:
        raise RuntimeError("REF-5602 fixture is missing")
    specialty = referral["specialty"]
    patient_id = referral["patient_id"]

    first = [("get_referral", {"referral_id": CASE_ID})]
    independent = [
        ("check_referral_criteria", {"specialty": specialty,
                                      "referral_id": CASE_ID}),
        ("lookup_patient", {"patient_id": patient_id}),
        ("as_of", {}),
    ]

    # In sequential mode, each call is its own tool turn.  In parallel mode,
    # the three reads share exactly one turn because they require only the
    # referral identifiers and do not write or query capacity.
    stages = [first]
    stages += [independent] if parallel else [[call] for call in independent]
    trace, turns_so_far = _execute(stages, parallel)
    observations = {name: result for name, _args, result in trace}
    criteria = observations["check_referral_criteria"]
    patient = observations["lookup_patient"]
    today = date.fromisoformat(observations["as_of"])

    if (criteria["instruction_in_referral_free_text"] or criteria["red_flag_term"]
            or not criteria["right_department"] or criteria["missing_tests"]):
        raise AssertionError("REF-5602 must pass the pre-slot criteria")
    duplicate = any(
        appointment["specialty"] == specialty and appointment["date"] >= today.isoformat()
        for appointment in patient["patient"].get("existing_appointments", [])
    )
    if duplicate:
        raise AssertionError("REF-5602 must have no future duplicate appointment")

    window = {
        "from": today.isoformat(),
        "to": (today + timedelta(weeks=criteria["window_weeks"])).isoformat(),
    }
    slot_call = [("get_clinic_slots", {
        "specialty": specialty, "band": criteria["band"], **window,
    })]
    slot_trace, slot_turns = _execute([slot_call], parallel)
    slots = sorted(slot_trace[0][2], key=lambda row: (row["date"], row["time"]))
    if not slots:
        raise AssertionError("REF-5602 must have a legal slot")
    slot = slots[0]

    book_call = [("book_slot", {
        "clinic": slot["clinic"], "date": slot["date"], "time": slot["time"],
        "referral_id": CASE_ID,
    })]
    book_trace, book_turns = _execute([book_call], parallel)
    booking = book_trace[0][2]
    if not booking.get("booked"):
        raise AssertionError("The local booking action did not confirm")

    trace += slot_trace + book_trace
    tool_turns = turns_so_far + slot_turns + book_turns
    input_tokens, output_tokens, cost = _scripted_usage(tool_turns)
    return {
        "case_id": CASE_ID,
        "tool_turns": tool_turns,
        "tool_names": [name for name, _args, _result in trace],
        "decision": "book",
        "booked": {key: booking[key] for key in ("clinic", "date", "time")},
        "input_tokens_estimated": input_tokens,
        "output_tokens_estimated": output_tokens,
        "estimated_cost_usd": cost,
        "usage_kind": "scripted_estimate_not_live_measurement",
    }


def main() -> None:
    sequential, parallel = run_schedule(False), run_schedule(True)
    comparison = {
        "case_id": CASE_ID,
        "sequential": sequential,
        "parallel": parallel,
        "same_final_decision": sequential["decision"] == parallel["decision"],
        "same_tool_coverage": sequential["tool_names"] == parallel["tool_names"],
        "scope_note": (
            "Controlled scripted baseline using the submitted tools.py interface. "
            "D4 must compare the full evaluation set before claiming that "
            "parallel scheduling leaves assignment-wide correctness unchanged."
        ),
    }
    assert comparison["same_final_decision"] and comparison["same_tool_coverage"]
    print(json.dumps(comparison, indent=2))


if __name__ == "__main__":
    main()
