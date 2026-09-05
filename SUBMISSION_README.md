# PE6201 A2 — Problem B submission runner

This repository contains our Problem B (outpatient referral coordination)
implementation.  It begins from the lecturer-provided A2 scaffold and keeps
the required default execution path reproducible.

## Marker / D5(a) command

```bash
python3 run_eval.py
```

The committed default is `BACKEND = "scripted"`; it needs no API key, network,
or third-party package.  The command writes `results.json`.  It deliberately
runs only cases which have a scripted move sequence in `backends.py`.  Add a
case to `SCRIPTS` before including it in the reproducible scripted result set.

## Layout

- `data_B/` and `expected_outcomes_B.json`: 55 cases and their answer key.
- `tools.py`: Problem B tools, interface descriptors, and the action gate.
- `agent.py`: instrumented ReAct loop.
- `guardrails.py`: step cap, token ceiling, de-duplication, and booking gate.
- `harness.py`: D4 code check and judgement queue.
- `run_eval.py`: reproducible entry point.
- `scripts/check_my_data.py`: fixture and answer-key consistency check.
- `run_main.ipynb`: the Google Colab guide for teammates.

## Important integrity rules

Do not put an API key in `config.py`, a notebook, or Git.  Live evaluation is
only for D5(b), after the team has agreed the model and documented its real
token usage.  Do not present scripted token estimates as measured live usage.

Run the data check after changing cases:

```bash
python3 scripts/check_my_data.py
```
