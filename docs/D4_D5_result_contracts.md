# D4 and D5 result-file contracts

The non-technical `run_main.ipynb` calls the report script only after these files exist. The D3/D5 code owner writes them; owners of D4-D6 never edit Python.

## `results/d3_observations.json`

Write one JSON object per trial. Normal cases appear once; negative cases appear three times. `observed` is the final structured output from the D3 runner.

```json
[
  {
    "case_id": "REF-5602",
    "observed": {
      "decision": "book",
      "booked": {"clinic": "OPH-C2", "date": "2026-10-14", "time": "11:20"}
    }
  }
]
```

For `request_information`, include `decision` and `missing`. For `escalate`, include `decision` and `trigger`. The report script compares only labelled fields and never invents or judges a reason string.

## `results/d5_runs.json`

Write one JSON object for each actual model/case run. All keys are required.

```json
[
  {
    "model": "provider/model-name",
    "family": "provider-family",
    "price_tier": "cheap",
    "case_id": "REF-5602",
    "input_tokens": 123,
    "output_tokens": 45,
    "turns": 4,
    "passed": true
  }
]
```

The D5 live runner must obtain its credential from Colab Secrets or the owner's environment. Never write an API key into this repository, a notebook, or either result file.
