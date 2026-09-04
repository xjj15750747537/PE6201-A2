import unittest

from src.contracts import ToolAction
from src.dependency_policy import DependencyPolicy, DependencyViolation


class DependencyPolicyTests(unittest.TestCase):
    def setUp(self):
        self.policy = DependencyPolicy()

    def test_allows_independent_read_pair(self):
        self.policy.validate_batch((ToolAction("get_existing_appointments", {"patient_id": "P-1180"}), ToolAction("find_eligible_slots", {"specialty": "OPH", "urgency_band": "soon"})))

    def test_rejects_context_in_parallel_batch(self):
        with self.assertRaises(DependencyViolation):
            self.policy.validate_batch((ToolAction("get_referral_context", {"referral_id": "REF-5602"}), ToolAction("get_existing_appointments", {"patient_id": "P-1180"})))

    def test_rejects_gated_staging_in_parallel_batch(self):
        with self.assertRaises(DependencyViolation):
            self.policy.validate_batch((ToolAction("find_eligible_slots", {"specialty": "OPH", "urgency_band": "soon"}), ToolAction("stage_booking_intent", {})))
