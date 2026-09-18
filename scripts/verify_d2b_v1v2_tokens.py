"""D2(b) verification: mean input/output tokens per tool call, v1 vs v2,
on the live gpt-4o-mini battery.

WHY THIS SCRIPT EXISTS
-----------------------
A D2(b)/D6 table quoting mean tokens-per-call for the v1 and v2 descriptor
contracts (gpt-4o-mini) was circulating as a finished Word table with no
committed script, raw output, or summary behind it -- the same gap D2(c)
had before Hing asked for a reproducible artefact. This script closes that
gap the same way: it recomputes the table directly from the two measured
live-battery run files that were actually used, rather than restating the
numbers by hand.

WHAT IT REUSES, ON PURPOSE
---------------------------
- results/d2b_v1v2_source/hing-gpt4omini-v1-protocolfix-01.json: Hing Lam
  Chang's measured gpt-4o-mini live battery run. Its own `prompt_version`
  field is "v1".
- results/d2b_v1v2_source/nicole-gpt4omini-v1-protocolfix-01.json: Ziyi
  Nicole Hu's measured gpt-4o-mini live battery run. NOTE: this file's
  NAME says "v1-protocolfix-01" but its own `prompt_version` field inside
  the JSON is "v2" -- it is the v2 run, just named after the protocol-fix
  batch rather than the prompt version. This script trusts the field
  inside the file (the same field run_live_battery.py and
  report_d2b_comparison.py group by), not the filename. Flagged below so
  nobody "fixes" this by swapping files based on the name alone.

Both are real `results/live_runs/`-shaped fragments (see
tests/test_live_run_aggregation.py for the shape): one dict per run, with
a `results` list of per-trial records. Each record's `evidence` list is
the ordered list of tool calls the live model actually made in that
trial; its length is the "number of tool calls in that trial" the
original table's caption describes. tokens_in / tokens_out on each record
are the provider-reported totals for that whole trial (token_usage_kind:
"provider_reported" -- not estimated).

WHAT "PER CALL" MEANS HERE, AND WHAT IT DOES NOT MEAN
--------------------------------------------------------
mean tokens per call = (sum of tokens_in over all 93 trials) / (sum of
tool calls over all 93 trials), and likewise for tokens_out. This is a
call-weighted MEAN across the whole run, matching the original table's
caption ("Per-call = total tokens for the trial / number of tool calls in
that trial") and matching scripts/report_d2b_comparison.py's existing
per-trial-mean convention in spirit, but at call granularity rather than
trial granularity (report_d2b_comparison.py's mean_input_tokens is PER
TRIAL, not per call -- the two are not interchangeable; do not confuse
this script's numbers with that script's output).

>>> THIS IS NOT PROVIDER-MEASURED PER-INDIVIDUAL-TOOL-CALL ATTRIBUTION. <<<
The live runner (agent.py / backends.LiveBackend) records ONE usage figure
per model response/trial from the provider -- it does not, and the
provider API does not, break usage down per individual tool call inside
a bundled or multi-call trial. So when a trial has 3 tool calls, we do
NOT know whether call 1 cost more tokens than call 2 or 3; we only know
the trial's total. "Mean tokens per call" here is that trial total spread
evenly across the trial's call count, aggregated over all 93 trials -- a
clearly-labelled derived statistic, not a measured per-call figure. Do
not present it, or quote it, as "we measured what each tool call costs";
present it as "on average, each tool call in this run corresponded to
about this many tokens of the trial it belonged to."
"""
import csv
import json
import os

SOURCE_DIR = os.path.join(os.path.dirname(__file__), "..", "results", "d2b_v1v2_source")
CSV_PATH = os.path.join(os.path.dirname(__file__), "..", "results", "d2b_v1v2_raw_trials.csv")
SUMMARY_PATH = os.path.join(os.path.dirname(__file__), "..", "results", "d2b_v1v2_summary.json")

RUNS = [
    ("hing-gpt4omini-v1-protocolfix-01.json", "v1"),
    ("nicole-gpt4omini-v1-protocolfix-01.json", "v2"),
]


def load_run(filename):
    path = os.path.join(SOURCE_DIR, filename)
    with open(path) as fh:
        return json.load(fh)


def main():
    rows = []
    per_version = {}

    for filename, expected_version in RUNS:
        data = load_run(filename)
        actual_version = data["prompt_version"]
        if actual_version != expected_version:
            raise SystemExit(
                "STOP: %s claims prompt_version=%r inside the file, but "
                "this script expected %r. The v1/v2 label must come from "
                "the field inside the file, not the filename -- re-check "
                "before trusting any table built from this run."
                % (filename, actual_version, expected_version)
            )

        total_calls = 0
        total_in = 0
        total_out = 0
        for r in data["results"]:
            rec = r["record"]
            n_calls = len(rec.get("evidence", []))
            tokens_in = rec.get("tokens_in", 0)
            tokens_out = rec.get("tokens_out", 0)
            total_calls += n_calls
            total_in += tokens_in
            total_out += tokens_out
            rows.append({
                "prompt_version": actual_version,
                "run_name": data["run_name"],
                "owner": data["owner"],
                "case_id": r["case_id"],
                "trial": r["trial"],
                "passed": r["passed"],
                "tool_calls": n_calls,
                "tokens_in": tokens_in,
                "tokens_out": tokens_out,
                "token_usage_kind": rec.get("token_usage_kind"),
            })

        per_version[actual_version] = {
            "source_file": filename,
            "run_name": data["run_name"],
            "owner": data["owner"],
            "model": data["model"],
            "prompt_contract_revision": data["prompt_contract_revision"],
            "created_utc": data["created_utc"],
            "trials": len(data["results"]),
            "pass_rate": data["summary"]["pass_rate"],
            "total_tool_calls": total_calls,
            "total_tokens_in": total_in,
            "total_tokens_out": total_out,
            "mean_input_tokens_per_call": round(total_in / total_calls, 1),
            "mean_output_tokens_per_call": round(total_out / total_calls, 1),
        }

    with open(CSV_PATH, "w", newline="") as fh:
        w = csv.DictWriter(fh, fieldnames=list(rows[0].keys()))
        w.writeheader()
        w.writerows(rows)

    v1, v2 = per_version["v1"], per_version["v2"]

    # Comparability check: same model, same 93-trial set, same output
    # contract revision -- the three conditions the team agreed a v1/v2
    # comparison must satisfy before it can be committed.
    mismatches = []
    if v1["model"] != v2["model"]:
        mismatches.append("model differs: %r vs %r" % (v1["model"], v2["model"]))
    if v1["trials"] != v2["trials"]:
        mismatches.append("trial count differs: %d vs %d" % (v1["trials"], v2["trials"]))
    if v1["prompt_contract_revision"] != v2["prompt_contract_revision"]:
        mismatches.append("prompt_contract_revision differs: %r vs %r"
                          % (v1["prompt_contract_revision"], v2["prompt_contract_revision"]))
    if mismatches:
        raise SystemExit("STOP: v1/v2 runs are not comparable:\n  - "
                         + "\n  - ".join(mismatches))

    summary = {
        "note": (
            "Both runs are real measured live-battery fragments "
            "(token_usage_kind=provider_reported), not scripted/estimated. "
            "nicole-gpt4omini-v1-protocolfix-01.json is named after the "
            "protocol-fix batch, not the prompt version -- its own "
            "prompt_version field is 'v2', confirmed by this script "
            "refusing to run if that field does not match."
        ),
        "comparability_check": (
            "PASSED: same model (%s), same trial count (%d each), same "
            "prompt_contract_revision (%s)."
            % (v1["model"], v1["trials"], v1["prompt_contract_revision"])
        ),
        "caveat": (
            "'mean_*_tokens_per_call' is a DERIVED MEAN (trial total tokens "
            "divided by that trial's tool-call count, summed over all 93 "
            "trials), not provider-measured per-individual-tool-call "
            "attribution -- the provider only reports one usage figure per "
            "model response/trial, never broken out per tool call within "
            "it. Report this as a labelled average, not as measured "
            "per-call cost."
        ),
        "v1": v1,
        "v2": v2,
        "change": {
            "mean_input_tokens_per_call_pct": round(
                (v2["mean_input_tokens_per_call"] - v1["mean_input_tokens_per_call"])
                / v1["mean_input_tokens_per_call"] * 100, 1),
            "mean_output_tokens_per_call_pct": round(
                (v2["mean_output_tokens_per_call"] - v1["mean_output_tokens_per_call"])
                / v1["mean_output_tokens_per_call"] * 100, 1),
        },
    }
    with open(SUMMARY_PATH, "w") as fh:
        json.dump(summary, fh, indent=2)

    print(json.dumps(summary, indent=2))


if __name__ == "__main__":
    main()
