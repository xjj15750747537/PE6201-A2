"""Locks the full-set D2(c) verification's REF-5602 handling to the
authoritative production schedule (backends.SCRIPTS["REF-5602"]), per
Hing's review: run_eval.py actually executes that script for REF-5602,
not problem_b_scripts.build_script()'s generic single-query path, so the
full-set comparison must not silently drift back to the 5-vs-4-turn
generic numbers.
"""
import unittest

import harness
from scripts.verify_d2c_full_set import (
    REF5602_CASE_ID, execute_schedule, ref5602_turns, build_record,
)


class Ref5602ProductionScheduleTests(unittest.TestCase):
    def test_locks_to_six_sequential_four_parallel_turns(self):
        seq_turns, par_turns = ref5602_turns()
        self.assertEqual(len(seq_turns), 6)
        self.assertEqual(len(par_turns), 4)

    def test_both_schedules_independently_book_the_production_slot(self):
        seq_turns, par_turns = ref5602_turns()
        seq_final, seq_evidence, seq_n = execute_schedule(seq_turns)
        par_final, par_evidence, par_n = execute_schedule(par_turns)

        # Same six calls either way -- only the turn-grouping differs.
        self.assertEqual(sorted(seq_evidence), sorted(par_evidence))
        self.assertEqual(seq_evidence.count("get_clinic_slots"), 2)
        self.assertEqual(par_evidence.count("get_clinic_slots"), 2)

        for final in (seq_final, par_final):
            self.assertEqual(final["decision"], "book")
            self.assertEqual(final["booked"],
                             {"clinic": "OPH-C2", "date": "2026-10-14", "time": "11:20"})

        self.assertEqual(seq_n, 6)
        self.assertEqual(par_n, 4)

    def test_both_schedules_pass_the_answer_key_independently(self):
        key = harness.load_key("B")
        expected = key[REF5602_CASE_ID]
        seq_turns, par_turns = ref5602_turns()

        seq_final, _, seq_n = execute_schedule(seq_turns)
        par_final, _, par_n = execute_schedule(par_turns)
        seq_record = build_record(seq_final, seq_n)
        par_record = build_record(par_final, par_n)

        seq_pass, seq_fails = harness.code_check(seq_record, expected)
        par_pass, par_fails = harness.code_check(par_record, expected)
        self.assertTrue(seq_pass, seq_fails)
        self.assertTrue(par_pass, par_fails)


if __name__ == "__main__":
    unittest.main()
