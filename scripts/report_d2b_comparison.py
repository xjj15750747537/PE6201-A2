"""Summarise measured v1-versus-v2 D2(b) runs for the same model."""

from __future__ import annotations

import json
from collections import defaultdict
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
RUNS = ROOT / "results" / "d5_runs.json"
OUT = ROOT / "results" / "d2b_prompt_comparison.json"


def metrics(rows: list[dict]) -> dict:
    return {
        "trials": len(rows),
        "pass_rate": sum(bool(row["passed"]) for row in rows) / len(rows),
        "mean_turns": sum(float(row["turns"]) for row in rows) / len(rows),
        "mean_input_tokens": sum(float(row["input_tokens"]) for row in rows) / len(rows),
        "mean_output_tokens": sum(float(row["output_tokens"]) for row in rows) / len(rows),
    }


def main() -> None:
    if not RUNS.exists():
        raise SystemExit("Missing results/d5_runs.json. Run both measured v1 and v2 batteries first.")
    rows = json.loads(RUNS.read_text(encoding="utf-8"))
    # Compare only versions that share one output/parsing contract. Older
    # immutable fragments remain evidence but must not be silently mixed in.
    grouped: dict[tuple[str, str], dict[str, list[dict]]] = defaultdict(lambda: defaultdict(list))
    for row in rows:
        key = (str(row["model"]), str(row.get("prompt_contract_revision", "legacy-unversioned")))
        grouped[key][str(row.get("prompt_version", ""))].append(row)
    comparisons = []
    for (model, revision), versions in sorted(grouped.items()):
        if not versions.get("v1") or not versions.get("v2"):
            continue
        v1, v2 = metrics(versions["v1"]), metrics(versions["v2"])
        comparisons.append({
            "model": model,
            "prompt_contract_revision": revision,
            "v1": v1,
            "v2": v2,
            "v2_minus_v1": {key: v2[key] - v1[key] for key in v1},
        })
    if not comparisons:
        raise SystemExit("No model has both measured v1 and v2 runs yet.")
    OUT.write_text(json.dumps(comparisons, indent=2), encoding="utf-8")
    print(json.dumps(comparisons, indent=2))
    print(f"Saved {OUT.relative_to(ROOT)}")


if __name__ == "__main__":
    main()
