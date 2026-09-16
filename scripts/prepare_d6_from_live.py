"""Fill the numerical D6 input file from measured D5(b) rows.

The only values a non-technical owner supplies are public business assumptions
(tool fees, fallback labour cost, fixed cost, monthly volume).  Token counts,
turns, success rate, and model prices are copied from the recorded live run.
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path

import config


ROOT = Path(__file__).resolve().parents[1]
RUNS = ROOT / "results" / "d5_runs.json"
OUT = ROOT / "templates" / "d6_inputs_template.json"


def average(rows: list[dict], key: str) -> float:
    return sum(float(row[key]) for row in rows) / len(rows)


def one_price(rows: list[dict], key: str) -> float:
    values = {float(row[key]) for row in rows}
    if len(values) != 1:
        raise ValueError(f"Selected rows disagree on {key}; use one verified price.")
    return values.pop()


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--model", required=True)
    parser.add_argument("--prompt-version", default="v2", choices=("v1", "v2"))
    parser.add_argument("--retrieval-and-tool-fees", required=True, type=float)
    parser.add_argument("--failure-cost", required=True, type=float)
    parser.add_argument("--fixed-monthly-cost", required=True, type=float)
    parser.add_argument("--monthly-volume", required=True, type=int)
    args = parser.parse_args()
    if not RUNS.exists():
        raise SystemExit("Missing results/d5_runs.json. Run a measured D5(b) battery first.")
    rows = [row for row in json.loads(RUNS.read_text(encoding="utf-8"))
            if (row["model"] == args.model
                and row.get("prompt_version") == args.prompt_version
                and row.get("prompt_contract_revision") == config.LIVE_OUTPUT_CONTRACT_REVISION)]
    if not rows:
        raise SystemExit("No measured rows match this model, prompt version, and current live-output contract. Run the repaired battery before D6.")
    if min(args.retrieval_and_tool_fees, args.failure_cost, args.fixed_monthly_cost) < 0 or args.monthly_volume < 1:
        raise SystemExit("D6 public cost inputs must be non-negative and monthly volume must be at least one.")
    values = {
        "input_tokens": average(rows, "input_tokens"),
        "output_tokens": average(rows, "output_tokens"),
        "turns": average(rows, "turns"),
        "input_price_per_million": one_price(rows, "input_price_per_million"),
        "output_price_per_million": one_price(rows, "output_price_per_million"),
        "retrieval_and_tool_fees": args.retrieval_and_tool_fees,
        "success_rate": sum(bool(row["passed"]) for row in rows) / len(rows),
        "failure_cost": args.failure_cost,
        "fixed_monthly_cost": args.fixed_monthly_cost,
        "monthly_volume": args.monthly_volume,
    }
    OUT.write_text(json.dumps(values, indent=2), encoding="utf-8")
    print(json.dumps(values, indent=2))
    print(f"Saved {OUT.relative_to(ROOT)} from {len(rows)} measured live rows.")


if __name__ == "__main__":
    main()
