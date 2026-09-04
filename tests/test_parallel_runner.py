import unittest

from src.backends import ScriptedBackend
from src.contracts import FinalOutcome, ModelTurn, ToolAction
from src.dependency_policy import DependencyPolicy
from src.react_runner import ReActRunner, RunnerConfig


class ParallelRunnerTests(unittest.TestCase):
    def test_parallel_batch_keeps_declared_trace_order(self):
        actions = (ToolAction("get_existing_appointments", {"patient_id": "P-1180"}), ToolAction("find_eligible_slots", {"specialty": "OPH", "urgency_band": "soon"}))
        final = FinalOutcome(decision="request_information", reason="Demo complete.", evidence=(), autonomy="review_required", gate="demo")
        runner = ReActRunner(ScriptedBackend((ModelTurn(actions=actions, final=final, input_tokens=10, output_tokens=5),)), lambda action: {"observed": action.name}, RunnerConfig(execution_mode="parallel"), DependencyPolicy().validate_batch)
        result = runner.run("parallel-test", {"task": "test"})
        self.assertEqual(result.turns, 1)
        self.assertEqual([event.action.name for event in result.trace], ["get_existing_appointments", "find_eligible_slots"])
        self.assertEqual([event.observation["observed"] for event in result.trace], ["get_existing_appointments", "find_eligible_slots"])
