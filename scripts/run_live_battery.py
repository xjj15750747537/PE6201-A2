"""Run one measured D5(b) model battery without editing config.py.

Each owner uses a private Colab Secret named OPENROUTER_API_KEY, enters only
the public model metadata in the notebook, and receives one immutable result
fragment under results/live_runs/.  All fragments are then combined into the
submission-ready results/d5_runs.json file.  A full battery follows the
assignment trial policy: booking cases run once and negative cases run three
times.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import re
import sys
from datetime import datetime, timezone
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
RESULTS = ROOT / "results"
LIVE_RUNS = RESULTS / "live_runs"

# When launched as ``python3 scripts/run_live_battery.py``, Python places the
# scripts directory—not the repository root—on sys.path.  Add the root so the
# canonical config.py and harness.py imports below resolve in Colab as well.
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))


def safe_name(value: str) -> str:
    value = re.sub(r"[^A-Za-z0-9_.-]+", "-", value.strip())
    if not value or value in {".", ".."}:
        raise ValueError("run name must contain letters or numbers")
    return value


def d5_rows(fragment: dict) -> list[dict]:
    rows = []
    for item in fragment["results"]:
        record = item["record"]
        if record.get("backend") != "live" or record.get("token_usage_kind") != "provider_reported":
            raise ValueError("Only provider-reported live results may be included in D5.")
        rows.append({
            "run_name": fragment["run_name"],
            "owner": fragment["owner"],
            "model": fragment["model"],
            "family": fragment["family"],
            "price_tier": fragment["price_tier"],
            "prompt_version": fragment["prompt_version"],
            "prompt_contract_revision": fragment.get(
                "prompt_contract_revision", "legacy-unversioned"),
            "input_price_per_million": fragment["input_price_per_million"],
            "output_price_per_million": fragment["output_price_per_million"],
            "case_id": item["case_id"],
            "trial": item["trial"],
            "input_tokens": record["tokens_in"],
            "output_tokens": record["tokens_out"],
            "turns": record["turns"],
            "passed": item["passed"],
            "fails": item["fails"],
            "cost_usd": record["cost_usd"],
            "stopped_by": record["stopped_by"],
        })
    return rows


def rebuild_d5_runs() -> int:
    rows = []
    seen_run_names: dict[str, tuple[str, Path]] = {}
    for path in sorted(LIVE_RUNS.glob("*.json")):
        raw_fragment = path.read_bytes()
        fragment = json.loads(raw_fragment.decode("utf-8"))
        run_name = str(fragment.get("run_name", ""))
        if not run_name:
            raise ValueError(f"{path.name} has no run_name.")
        digest = hashlib.sha256(raw_fragment).hexdigest()
        if run_name in seen_run_names:
            earlier_digest, earlier_path = seen_run_names[run_name]
            if digest == earlier_digest:
                print(
                    f"Skipping byte-identical duplicate evidence {path.name}; "
                    f"already included {earlier_path.name}."
                )
                continue
            raise ValueError(
                f"Conflicting measured run_name {run_name!r} in {earlier_path.name} "
                f"and {path.name}. Keep immutable evidence, but do not merge an "
                "ambiguous aggregate.")
        seen_run_names[run_name] = (digest, path)
        rows.extend(d5_rows(fragment))
    (RESULTS / "d5_runs.json").write_text(json.dumps(rows, indent=2), encoding="utf-8")
    return len(rows)


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--run-name", required=True, help="Unique public label, e.g. alice-gpt4omini-v2")
    parser.add_argument("--owner", required=True, help="Public owner label; never put a key here")
    parser.add_argument("--model", required=True)
    parser.add_argument("--family", required=True)
    parser.add_argument("--price-tier", required=True, choices=("cheap", "mid", "frontier"))
    parser.add_argument("--prompt-version", required=True, choices=("v1", "v2"))
    parser.add_argument("--input-price-per-million", required=True, type=float)
    parser.add_argument("--output-price-per-million", required=True, type=float)
    parser.add_argument("--case-limit", type=int, default=0, help="0 means all 55 cases; use only for a preflight.")
    args = parser.parse_args()

    if not os.environ.get("OPENROUTER_API_KEY"):
        raise SystemExit("OPENROUTER_API_KEY is missing. Add it in Colab Secrets; never paste it into code.")
    if args.input_price_per_million < 0 or args.output_price_per_million < 0:
        raise SystemExit("Verified token prices must be non-negative.")

    run_name = safe_name(args.run_name)
    LIVE_RUNS.mkdir(parents=True, exist_ok=True)
    output = LIVE_RUNS / f"{run_name}.json"
    if output.exists():
        raise SystemExit(f"{output} already exists. Choose a new run name; do not overwrite measured evidence.")

    # Import after environment validation, then set this process only.  The
    # committed config remains scripted so a marker can reproduce D5(a).
    import config
    config.BACKEND = "live"
    config.MODEL = args.model
    config.PROMPT_VERSION = args.prompt_version
    config.PRICE_IN = args.input_price_per_million
    config.PRICE_OUT = args.output_price_per_million

    from harness import load_cases, load_key, report, run_set

    cases = load_cases()
    if args.case_limit:
        if args.case_limit < 1:
            raise SystemExit("--case-limit must be positive or 0.")
        cases = cases[:args.case_limit]
    answer_key = load_key()
    total_trials = sum(
        1 if answer_key[case_id]["expected_decision"] == "book" else 3
        for case_id in cases
    )
    print(
        f"LIVE D5(b): {len(cases)} cases / {total_trials} trials "
        f"(one booking, three negative), model={args.model}, "
        f"descriptors={args.prompt_version}"
    )
    results, judgement_queue = run_set(cases, prompt_version=args.prompt_version)
    summary = report(results)
    fragment = {
        "run_name": run_name,
        "owner": args.owner,
        "model": args.model,
        "family": args.family,
        "price_tier": args.price_tier,
        "prompt_version": args.prompt_version,
        "prompt_contract_revision": config.LIVE_OUTPUT_CONTRACT_REVISION,
        "input_price_per_million": args.input_price_per_million,
        "output_price_per_million": args.output_price_per_million,
        "created_utc": datetime.now(timezone.utc).isoformat(),
        "summary": summary,
        "results": results,
        "judgement_queue": judgement_queue,
    }
    output.write_text(json.dumps(fragment, indent=2), encoding="utf-8")
    total = rebuild_d5_runs()
    print(f"Saved {output.relative_to(ROOT)} and rebuilt results/d5_runs.json ({total} measured rows).")


if __name__ == "__main__":
    main()
