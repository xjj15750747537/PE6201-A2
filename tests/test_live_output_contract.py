import json
import unittest
from unittest.mock import patch

import config
from agent import _tool_result_message, run_case
from backends import _parse_move
from prompt import build_system_prompt


class LiveOutputContractTests(unittest.TestCase):
    def test_accepts_json_wrapped_in_a_code_fence(self):
        move = _parse_move('```json\n{"final": {"decision": "book"}}\n```')
        self.assertEqual(move["final"]["decision"], "book")

    def test_rejects_a_json_object_followed_by_extra_prose(self):
        move = _parse_move('{"final": {"decision": "book"}} thanks')
        self.assertEqual(move["final"]["decision"], "escalate")
        self.assertEqual(move["final"]["parse_error"], "text followed the JSON object")

    def test_problem_b_prompt_names_canonical_scoring_values(self):
        prompt = build_system_prompt("B", version="v2")
        self.assertIn('trigger = "red_flag_term"', prompt)
        self.assertIn('"visual field test VF-01"', prompt)

    def test_output_contract_revision_is_present(self):
        import config
        self.assertEqual(config.LIVE_OUTPUT_CONTRACT_REVISION,
                         "json-contract-2026-09-16-tool-protocol")

    def test_tool_result_handoff_is_json_and_repeats_the_contract(self):
        message = _tool_result_message([
            {"tool": "get_referral", "args": {"referral_id": "REF-5602"},
             "observation": {"patient_id": "P-1"}},
        ])
        self.assertIn("TOOL_RESULTS_JSON", message)
        self.assertIn('"get_referral"', message)
        self.assertNotIn("'get_referral'", message)
        self.assertIn("exactly one JSON object", message)

    def test_live_loop_keeps_json_action_and_tool_protocol_on_turn_two(self):
        """Regression test for the failure that made live runs escalate at turn 1."""
        replies = [
            json.dumps({"calls": [["get_referral", {"referral_id": "REF-5602"}]]}),
            json.dumps({"final": {"decision": "book", "reason": "test final"}}),
        ]
        seen_messages = []

        def fake_live_call(messages):
            seen_messages.append(messages)
            return replies.pop(0), (10, 5)

        with patch.object(config, "BACKEND", "live"), \
             patch.object(config, "API_KEY", "test-key"), \
             patch("backends._live_call", side_effect=fake_live_call):
            record = run_case("REF-5602", problem="B", prompt_version="v1")

        self.assertEqual(record["decision"], "book")
        self.assertEqual(record["turns"], 1)
        self.assertEqual(record["evidence"], ["get_referral"])
        self.assertEqual(len(seen_messages), 2)
        self.assertEqual(
            json.loads(seen_messages[1][-2]["content"]),
            {"calls": [["get_referral", {"referral_id": "REF-5602"}]]},
        )
        self.assertIn("TOOL_RESULTS_JSON", seen_messages[1][-1]["content"])
        self.assertIn("exactly one JSON object", seen_messages[1][-1]["content"])


if __name__ == "__main__":
    unittest.main()
