"""Compare sequential and dependency-aware parallel tool-turn schedules."""

from __future__ import annotations

import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from src.backends import ScriptedBackend
from src.contracts import FinalOutcome, ModelTurn, ToolAction
from src.dependency_policy import DependencyPolicy
from src.react_runner import ReActRunner, RunnerConfig


def fixture_executor(action: ToolAction) -> dict[str, object]:
    observations = {
        "get_referral_context": {"referral": {"referral_id": "REF-5602", "patient_id": "P-1180", "specialty": "OPH"}, "specialty": {"code": "OPH"}, "as_of": "2026-09-04", "urgency_bands": ["urgent", "soon", "routine"]},
        "get_existing_appointments": {"patient_id": "P-1180", "existing_appointments": []},
        "find_eligible_slots": {"specialty": "OPH", "urgency_band": "soon", "slots": [{"clinic": "Eye Clinic A", "specialty": "OPH", "band": "soon", "date": "2026-09-10", "time": "09:00", "capacity_remaining": 1}]},
        "stage_booking_intent": {"status": "staged", "booking_intent_id": "INTENT-5602", "gate": "passed", "contact_method": "sms"},
    }
    return observations[action.name]


def outcome() -> FinalOutcome:
    return FinalOutcome(decision="book", reason="The deterministic fixture gates passed and a local intent was staged.", evidence=("REF-5602", "INTENT-5602"), autonomy="local_demo_only", gate="passed")


def run_schedule(parallel: bool):
    context = ToolAction("get_referral_context", {"referral_id": "REF-5602"})
    appointments = ToolAction("get_existing_appointments", {"patient_id": "P-1180"})
    slots = ToolAction("find_eligible_slots", {"specialty": "OPH", "urgency_band": "soon"})
    stage = ToolAction("stage_booking_intent", {"referral_id": "REF-5602", "patient_id": "P-1180", "specialty": "OPH", "slot": {"clinic": "Eye Clinic A", "date": "2026-09-10", "time": "09:00"}, "evidence": ["criteria_passed", "no_duplicate", "capacity_positive"]})
    if parallel:
        turns = (ModelTurn(actions=(context,), final=None, input_tokens=1200, output_tokens=30), ModelTurn(actions=(appointments, slots), final=None, input_tokens=2000, output_tokens=50), ModelTurn(actions=(stage,), final=outcome(), input_tokens=2800, output_tokens=60))
    else:
        turns = (ModelTurn(actions=(context,), final=None, input_tokens=1200, output_tokens=30), ModelTurn(actions=(appointments,), final=None, input_tokens=1600, output_tokens=40), ModelTurn(actions=(slots,), final=None, input_tokens=2000, output_tokens=45), ModelTurn(actions=(stage,), final=outcome(), input_tokens=2400, output_tokens=55))
    runner = ReActRunner(ScriptedBackend(turns), fixture_executor, RunnerConfig(execution_mode="parallel" if parallel else "sequential"), DependencyPolicy().validate_batch)
    return runner.run("D2C-DEMO-REF-5602", {"task": "stage only after gates pass"})


def compact(result):
    return {"turns": result.turns, "input_tokens": result.input_tokens, "output_tokens": result.output_tokens, "estimated_cost_usd": round(result.estimated_cost_usd, 5), "decision": result.outcome.decision, "tool_names": [event.action.name for event in result.trace]}


def main() -> None:
    sequential, parallel = run_schedule(False), run_schedule(True)
    comparison = {"case_id": sequential.case_id, "sequential": compact(sequential), "parallel": compact(parallel), "same_final_decision": sequential.outcome.decision == parallel.outcome.decision, "same_tool_coverage": {event.action.name for event in sequential.trace} == {event.action.name for event in parallel.trace}, "scope_note": "Controlled baseline only; D4 must compare the full evaluation set."}
    assert comparison["same_final_decision"] and comparison["same_tool_coverage"]
    print(json.dumps(comparison, indent=2))


if __name__ == "__main__":
    main()
