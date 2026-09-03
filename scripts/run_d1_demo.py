"""Run one deterministic, offline D1 ReAct trace."""

from __future__ import annotations

import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from src.backends import ScriptedBackend
from src.contracts import FinalOutcome, ModelTurn, ToolAction
from src.react_runner import ReActRunner


def demo_tool(action: ToolAction) -> dict[str, object]:
    if action.name != "get_referral":
        raise ValueError(f"Demo tool cannot execute {action.name!r}")
    return {
        "referral_id": action.arguments["referral_id"],
        "specialty": "OPH",
        "clinical_summary": "Sudden visual loss reported today.",
        "tests_attached": ["VF-01"],
    }


def main() -> None:
    backend = ScriptedBackend(
        [
            ModelTurn(
                actions=(ToolAction("get_referral", {"referral_id": "REF-DEMO"}),),
                input_tokens=120,
                output_tokens=25,
            ),
            ModelTurn(
                final=FinalOutcome(
                    decision="escalate",
                    reason="The scripted referral contains a red-flag symptom.",
                    evidence=["get_referral"],
                    autonomy="suggest",
                    gate="not reached: escalation path",
                ),
                input_tokens=180,
                output_tokens=35,
            ),
        ]
    )
    result = ReActRunner(backend, demo_tool).run("REF-DEMO")
    print(
        json.dumps(
            {
                "case_id": result.case_id,
                "decision": result.outcome.decision,
                "turns": result.turns,
                "tools_called": [event.action.name for event in result.trace],
                "input_tokens": result.input_tokens,
                "output_tokens": result.output_tokens,
                "estimated_cost_usd": result.estimated_cost_usd,
                "cap_fired": result.cap_fired,
            },
            indent=2,
        )
    )


if __name__ == "__main__":
    main()
