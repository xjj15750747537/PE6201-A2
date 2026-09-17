"""Regression checks for the authoritative D2(c) controlled comparison."""

import unittest

from scripts.run_d2c_comparison import run_schedule


class CurrentD2cComparisonTests(unittest.TestCase):
    def test_current_tools_have_same_booking_outcome_with_two_fewer_turns(self):
        sequential = run_schedule(parallel=False)
        parallel = run_schedule(parallel=True)

        expected_tools = [
            "get_referral", "check_referral_criteria", "lookup_patient",
            "as_of", "get_clinic_slots", "book_slot",
        ]
        self.assertEqual(sequential["tool_names"], expected_tools)
        self.assertEqual(parallel["tool_names"], expected_tools)
        self.assertEqual(sequential["decision"], "book")
        self.assertEqual(parallel["decision"], "book")
        self.assertEqual(sequential["tool_turns"], 6)
        self.assertEqual(parallel["tool_turns"], 4)
        self.assertEqual(parallel["usage_kind"],
                         "scripted_estimate_not_live_measurement")


if __name__ == "__main__":
    unittest.main()
