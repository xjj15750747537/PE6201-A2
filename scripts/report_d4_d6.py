"""Score D4 observations, summarise D5 runs, and calculate D6 costs.

This script intentionally refuses placeholder values.  It is safe for a
non-technical owner to run: D3/D5 supply measured JSON files; this script
only checks and reports those measurements.
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from src.d4d6_support import CostInputs, code_check, cost_summary, pass_rate, sensitivity, trial_count

ROOT = Path(__file__).resolve().parents[1]
RESULTS = ROOT / "results"


def load_json(path: Path) -> object:
    if not path.exists():
        raise FileNotFoundError(f"Missing {path}. Run the preceding notebook step first.")
    return json.loads(path.read_text(encoding="utf-8"))


def save_json(name: str, value: object) -> Path:
    RESULTS.mkdir(exist_ok=True)
    path = RESULTS / name
    path.write_text(json.dumps(value, indent=2), encoding="utf-8")
    return path


def d4() -> None:
    labels = {row["case_id"]: row for row in load_json(ROOT / "expected_outcomes_B.json")}
    observed = load_json(RESULTS / "d3_observations.json")
    if not isinstance(observed, list):
        raise ValueError("results/d3_observations.json must be a JSON list.")
    scored = []
    counts: dict[str, int] = {}
    for row in observed:
        if not isinstance(row, dict):
            raise ValueError("Every D3 observation must be a JSON object.")
        case_id = str(row.get("case_id", ""))
        if case_id not in labels:
            raise ValueError(f"Unknown case_id: {case_id!r}")
        counts[case_id] = counts.get(case_id, 0) + 1
        expected = {key: labels[case_id][key] for key in ("expected_decision", "booked", "trigger", "missing") if key in labels[case_id]}
        expected["decision"] = expected.pop("expected_decision")
        actual = row.get("observed")
        if not isinstance(actual, dict):
            raise ValueError(f"{case_id} needs an observed JSON object.")
        scored.append({"case_id": case_id, "passed": code_check(expected, actual), "expected": expected, "observed": actual})
    expected_trials = {case_id: trial_count({"is_negative": label["expected_decision"] != "book"}) for case_id, label in labels.items()}
    missing = [case_id for case_id, number in expected_trials.items() if counts.get(case_id, 0) != number]
    summary = pass_rate(scored)
    summary.update({"labelled_cases": len(labels), "complete_trial_plan": not missing, "trial_plan_issues": missing})
    save_json("d4_scored_results.json", {"summary": summary, "rows": scored})
    print(json.dumps(summary, indent=2))
    if missing:
        raise ValueError("D4 trial plan incomplete: ordinary cases need one trial and negative cases need three.")


def d5() -> None:
    runs = load_json(RESULTS / "d5_runs.json")
    if not isinstance(runs, list) or not runs:
        raise ValueError("results/d5_runs.json must be a non-empty JSON list.")
    required = {"model", "family", "price_tier", "case_id", "input_tokens", "output_tokens", "turns", "passed"}
    for row in runs:
        missing = required - set(row)
        if missing:
            raise ValueError(f"D5 run is missing: {', '.join(sorted(missing))}")
    grouped: dict[str, list[dict[str, object]]] = {}
    for row in runs:
        grouped.setdefault(str(row["model"]), []).append(row)
    summary = []
    for model, rows in grouped.items():
        summary.append({
            "model": model,
            "family": rows[0]["family"],
            "price_tier": rows[0]["price_tier"],
            "runs": len(rows),
            "pass_rate": sum(bool(row["passed"]) for row in rows) / len(rows),
            "mean_input_tokens": sum(float(row["input_tokens"]) for row in rows) / len(rows),
            "mean_output_tokens": sum(float(row["output_tokens"]) for row in rows) / len(rows),
            "mean_turns": sum(float(row["turns"]) for row in rows) / len(rows),
        })
    save_json("d5_model_summary.json", summary)
    print(json.dumps(summary, indent=2))


def d6() -> None:
    values = load_json(ROOT / "templates" / "d6_inputs_template.json")
    if not isinstance(values, dict):
        raise ValueError("D6 inputs must be a JSON object.")
    blocked = [key for key, value in values.items() if isinstance(value, str)]
    if blocked:
        raise ValueError("Replace measured D6 values before calculation: " + ", ".join(blocked))
    report = {"baseline": cost_summary(CostInputs(**values)), "sensitivity": sensitivity(CostInputs(**values))}
    save_json("d6_cost_report.json", report)
    print(json.dumps(report, indent=2))


parser = argparse.ArgumentParser()
parser.add_argument("section", choices=("d4", "d5", "d6"))
args = parser.parse_args()
{"d4": d4, "d5": d5, "d6": d6}[args.section]()
