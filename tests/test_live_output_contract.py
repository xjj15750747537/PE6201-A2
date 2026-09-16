import unittest

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
        self.assertEqual(config.LIVE_OUTPUT_CONTRACT_REVISION, "json-contract-2026-09-16")


if __name__ == "__main__":
    unittest.main()
