import json
from pathlib import Path
import unittest

from src.d4d6_support import CostInputs, break_even_success_rate, code_check, cost_summary, trial_count, validate_cases


class D4D6SupportTests(unittest.TestCase):
    def test_negative_case_gets_three_trials(self):
        self.assertEqual(trial_count({"is_negative": True}), 3)
        self.assertEqual(trial_count({"is_negative": False}), 1)

    def test_code_check_uses_expected_values_only(self):
        self.assertTrue(code_check({"decision": "escalate"}, {"decision": "escalate", "reason": "anything"}))
        self.assertFalse(code_check({"decision": "escalate"}, {"decision": "book"}))

    def test_cost_model_has_three_layers(self):
        result = cost_summary(CostInputs(1000, 100, 3, 3, 15, 0, 0.9, 10, 20, 100))
        self.assertGreater(result["layer_1_variable"], 0)
        self.assertAlmostEqual(result["layer_2_expected_fallback"], 1)
        self.assertEqual(result["layer_3_fixed_monthly"], 20)

    def test_break_even_is_calculated(self):
        self.assertAlmostEqual(break_even_success_rate(0.005, 0.657, 7.60), 0.9142105, places=6)

    def test_team_d4_set_has_55_real_labelled_cases(self):
        root = Path(__file__).resolve().parents[1]
        cases = json.loads((root / "templates" / "d4_cases_template.json").read_text(encoding="utf-8"))
        self.assertEqual(len(cases), 55)
        self.assertEqual(validate_cases(cases), [])
        self.assertGreaterEqual(sum(case["is_negative"] for case in cases), 10)
        self.assertTrue(all(not case["case_id"].startswith("TEAM-") for case in cases))
