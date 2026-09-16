import json
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from scripts import run_live_battery


def fragment(run_name: str, passed: bool = True) -> dict:
    return {
        "run_name": run_name,
        "owner": "Test",
        "model": "openai/gpt-4o-mini",
        "family": "OpenAI",
        "price_tier": "cheap",
        "prompt_version": "v1",
        "input_price_per_million": 0.15,
        "output_price_per_million": 0.60,
        "results": [{
            "case_id": "REF-TEST",
            "trial": 1,
            "passed": passed,
            "fails": [],
            "record": {
                "backend": "live",
                "token_usage_kind": "provider_reported",
                "tokens_in": 1,
                "tokens_out": 1,
                "turns": 1,
                "cost_usd": 0.0,
                "stopped_by": None,
            },
        }],
    }


class LiveRunAggregationTests(unittest.TestCase):
    def test_skips_only_byte_identical_duplicate_fragments(self):
        with tempfile.TemporaryDirectory() as temporary_directory:
            results = Path(temporary_directory)
            live_runs = results / "live_runs"
            live_runs.mkdir()
            content = json.dumps(fragment("same-run"), indent=2)
            (live_runs / "first.json").write_text(content, encoding="utf-8")
            (live_runs / "second.json").write_text(content, encoding="utf-8")

            with patch.object(run_live_battery, "RESULTS", results), \
                 patch.object(run_live_battery, "LIVE_RUNS", live_runs):
                self.assertEqual(run_live_battery.rebuild_d5_runs(), 1)

    def test_rejects_same_name_with_different_evidence(self):
        with tempfile.TemporaryDirectory() as temporary_directory:
            results = Path(temporary_directory)
            live_runs = results / "live_runs"
            live_runs.mkdir()
            (live_runs / "first.json").write_text(
                json.dumps(fragment("same-run")), encoding="utf-8")
            (live_runs / "second.json").write_text(
                json.dumps(fragment("same-run", passed=False)), encoding="utf-8")

            with patch.object(run_live_battery, "RESULTS", results), \
                 patch.object(run_live_battery, "LIVE_RUNS", live_runs):
                with self.assertRaisesRegex(ValueError, "Conflicting measured run_name"):
                    run_live_battery.rebuild_d5_runs()

    def test_honours_documented_fragment_exclusion(self):
        with tempfile.TemporaryDirectory() as temporary_directory:
            results = Path(temporary_directory)
            live_runs = results / "live_runs"
            live_runs.mkdir()
            (live_runs / "obsolete.json").write_text(
                json.dumps(fragment("same-run")), encoding="utf-8")
            (live_runs / "valid.json").write_text(
                json.dumps(fragment("same-run", passed=False)), encoding="utf-8")
            exclusions = results / "d5_fragment_exclusions.json"
            exclusions.write_text(json.dumps({"excluded_fragments": {
                "obsolete.json": "Owner-confirmed superseded duplicate."}}),
                encoding="utf-8")

            with patch.object(run_live_battery, "RESULTS", results), \
                 patch.object(run_live_battery, "LIVE_RUNS", live_runs), \
                 patch.object(run_live_battery, "EXCLUSIONS", exclusions):
                self.assertEqual(run_live_battery.rebuild_d5_runs(), 1)


if __name__ == "__main__":
    unittest.main()
