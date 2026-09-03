from __future__ import annotations

import unittest

from src.backends import ScriptedBackend
from src.contracts import FinalOutcome, ModelTurn, ToolAction
from src.react_runner import ReActRunner, RunnerConfig


class ReActRunnerTests(unittest.TestCase):
    def test_scripted_run_records_action_and_final_outcome(self) -> None:
        backend = ScriptedBackend(
            [
                ModelTurn(actions=(ToolAction("lookup", {"id": "REF-1"}),)),
                ModelTurn(
                    final=FinalOutcome(
                        decision="escalate",
                        reason="A scripted negative case.",
                        evidence=["lookup"],
                    )
                ),
            ]
        )
        result = ReActRunner(
            backend,
            lambda action: {"id": action.arguments["id"], "red_flag": True},
        ).run("REF-1")

        self.assertEqual(result.outcome.decision, "escalate")
        self.assertEqual(result.turns, 2)
        self.assertEqual([event.action.name for event in result.trace], ["lookup"])
        self.assertFalse(result.cap_fired)

    def test_step_cap_produces_loud_escalation(self) -> None:
        backend = ScriptedBackend(
            [ModelTurn(actions=(ToolAction("lookup", {"id": "REF-2"}),))]
        )
        result = ReActRunner(
            backend,
            lambda action: {"id": action.arguments["id"]},
            RunnerConfig(step_cap=1),
        ).run("REF-2")

        self.assertTrue(result.cap_fired)
        self.assertEqual(result.outcome.decision, "escalate")
        self.assertIn("Step cap", result.outcome.reason)


if __name__ == "__main__":
    unittest.main()
