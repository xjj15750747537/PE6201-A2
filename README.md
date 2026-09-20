# PE6201 A2 - Team C-2

This is our Problem B (Outpatient Referral Coordination) submission for PE6201 Emerging AI Technologies. The committed default is a deterministic scripted backend, so a marker can reproduce the submitted evaluation without a network connection, an API key, or third-party packages.

## Reproduce the scripted evaluation

```bash
git clone https://github.com/xjj15750747537/PE6201-A2.git
cd PE6201-A2
python3 scripts/check_my_data.py
python3 run_eval.py
```

The data check should report that the fixtures hang together. The evaluation should report 93 of 93 scripted trials passed. This is the D5(a) reproducibility run; it is not a live-model quality claim.

## Default configuration and integrity

- `BACKEND = "scripted"` is the committed default.
- The scripted path requires no API key, network, or package installation.
- Do not put API keys in Git, notebooks, or configuration files.
- D5(b) live-model runs are retained as evidence under `results/live_runs/`; provider-reported live figures are kept distinct from deterministic scripted token and cost estimates.

## Repository guide

- `SUBMISSION_README.md` explains the marker path and integrity rules.
- `data_B/` and `expected_outcomes_B.json` contain the 55 labelled cases and answer key.
- `tools.py`, `agent.py`, and `guardrails.py` contain the tool layer, ReAct loop, and safety controls.
- `harness.py` and `run_eval.py` provide the D4/D5(a) evaluation entry point.
- `results/` contains D2, D3, D5, D6, and D7 evidence.
- `CONTRIBUTIONS.md` records team contributions and evidence attribution.

For the guided Google Colab workflow, open `run_main.ipynb`. It is a collaboration aid; the command above is the official submitted reproduction path.
